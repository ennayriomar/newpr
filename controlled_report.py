"""Summarize only completed controlled runs; no selection or threshold changes."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil

import numpy as np
from PIL import Image

from controlled_common import LABELS, METRICS, cluster_bootstrap, pro_from_weights, select_figures
from utils import file_sha256, read_json, write_json


def interval(values):
    return np.quantile(values,[.025,.975]).tolist()


def render(rows,run,plan,path,bounds,delta_max,cuts):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import Normalize

    fig,axes=plt.subplots(len(rows),5,figsize=(17,3.4*len(rows)),squeeze=False)
    for i,row in enumerate(rows):
        native=plan["records"][row["image_id"]]
        if file_sha256(native["path"])!=row["image_sha256"]:raise ValueError("Figure input changed")
        with Image.open(native["path"]) as image:rgb=np.asarray(image.convert("RGB").resize((448,448),Image.Resampling.BILINEAR))
        with np.load(run/row["raw_map"],allow_pickle=False) as z:
            base,hybrid,truth=z["baseline"],z["hybrid"],z["truth"]
        if base.shape!=truth.shape or hybrid.shape!=truth.shape:raise ValueError("Figure score/GT geometry mismatch")
        axes[i,0].imshow(rgb);axes[i,1].imshow(truth,cmap="gray",vmin=0,vmax=1)
        for j,array in ((2,base),(3,hybrid)):
            axes[i,j].imshow(rgb);axes[i,j].imshow(array,cmap="jet",vmin=bounds[0],vmax=bounds[1],alpha=.5)
        axes[i,4].imshow(hybrid-base,cmap="magma",vmin=0,vmax=delta_max if delta_max else 1.)
        for j,title in enumerate(("Full image","Full-field GT","Search: internal baseline","Hybrid: adapted implementation","Hybrid - baseline")):
            axes[i,j].set_title(title,fontsize=9);axes[i,j].set_xticks([]);axes[i,j].set_yticks([])
        axes[i,0].set_ylabel(" / ".join(row["selection_reasons"]),fontsize=8)
        axes[i,0].set_xlabel(row["native_id"],fontsize=7)
        for j,method in ((2,"baseline"),(3,"hybrid")):
            predicted="defective" if row["decisions"][method] else "normal"
            axes[i,j].set_xlabel(f"{row['scores'][method]:.4f} > {cuts[method]['image']['cutoff']:.4f}: {predicted}",fontsize=8)
        if not delta_max:axes[i,4].set_xlabel("All differences exactly zero",fontsize=8)
    fig.subplots_adjust(left=.08,right=.98,top=.94,bottom=.12,hspace=.4,wspace=.1)
    bar=fig.add_axes([.2,.045,.29,.012])
    fig.colorbar(plt.cm.ScalarMappable(norm=Normalize(*bounds),cmap="jet"),cax=bar,orientation="horizontal").set_label("Shared raw score: both methods and all evaluated images")
    if delta_max:
        bar=fig.add_axes([.63,.045,.25,.012])
        fig.colorbar(plt.cm.ScalarMappable(norm=Normalize(0,delta_max),cmap="magma"),cax=bar,orientation="horizontal").set_label("Raw additive difference")
    fig.suptitle("Rule-selected cases | full image resized to448x448 | per-method source-only cutoffs",fontsize=12)
    fig.savefig(path,dpi=120);plt.close(fig)


def report(run):
    protocol=read_json(run/"protocol.json");cfg=protocol["config"];plan=read_json(run/"source_plan.json")
    if file_sha256(run/"protocol.json")!=(run/"protocol.json.sha256").read_text().split()[0]:raise ValueError("Protocol changed")
    rows=[json.loads(line) for line in (run/"results/per_image.jsonl").read_text().splitlines()]
    expected=sum(len(e["query_ids"]) for e in protocol["target_episodes"])
    if len(rows)!=expected or len({(r["dataset"],r["category"],r["seed"],r["image_id"]) for r in rows})!=expected:
        raise ValueError("Incomplete/duplicate controlled evaluation ledger")
    expected_cases={(e["dataset"],e["category"],e["seed"],q) for e in protocol["target_episodes"] for q in e["query_ids"]}
    if {(r["dataset"],r["category"],r["seed"],r["image_id"]) for r in rows}!=expected_cases:raise ValueError("Wrong native query cohort")
    draw_rows=[];boot_by_category={};metrics_by_category={};pixel_grid_errors=[]
    for episode in protocol["target_episodes"]:
        dataset,category,seed=(episode[k] for k in ("dataset","category","seed"))
        folder=run/"results"/dataset/category/f"seed-{seed}"
        values=read_json(folder/"metrics.json")
        for method,value in values.items():
            draw_rows.append({"dataset":dataset,"category":category,"seed":seed,"method":method,
                              "method_label":LABELS[method],**{k:value[k] for k in METRICS},
                              "image_fp":value["image_fp"],"image_fn":value["image_fn"],
                              "normal_images":value["normal_images"],"anomalous_images":value["anomalous_images"]})
        key=(dataset,category)
        metrics_by_category.setdefault(key,[]).append(values)
        with np.load(folder/"bootstrap.npz",allow_pickle=False) as arrays:
            boot_by_category.setdefault(key,[]).append({metric:arrays["paired_"+metric].copy() for metric in METRICS})
            for method in ("baseline","hybrid"):
                stats={name:arrays[method+"_pro_"+name] for name in ("fp","region_sum","normal_count","region_count","thresholds")}
                if not np.isclose(pro_from_weights(stats,np.ones(len(stats["normal_count"])))[0],values[method]["au_pro"],atol=1e-12,rtol=0):
                    raise ValueError("Saved PRO sufficient statistics do not replay reported point")
                pixel_grid_errors.append({"dataset":dataset,"category":category,"seed":seed,"method":method,
                    "exact_pixel_auroc":values[method]["pixel_auroc"],
                    "bootstrap_grid_pixel_auroc":float(arrays[method+"_pixel_auroc_grid_point"]),
                    "absolute_grid_error":abs(float(arrays[method+"_pixel_auroc_grid_point"])-values[method]["pixel_auroc"])})
    category_rows=[];category_differences=[];category_boot={}
    for (dataset,category),draws in metrics_by_category.items():
        for method in LABELS:
            category_rows.append({"dataset":dataset,"category":category,"method":method,"method_label":LABELS[method],
                                  "draws":len(draws),**{metric:float(np.mean([d[method][metric] for d in draws])) for metric in METRICS}})
        differences={metric:float(np.mean([d["hybrid"][metric]-d["baseline"][metric] for d in draws])) for metric in METRICS}
        averages={metric:np.mean([b[metric] for b in boot_by_category[(dataset,category)]],axis=0) for metric in METRICS}
        category_boot[(dataset,category)]=averages
        np.savez_compressed(run/"results"/dataset/category/"paired_bootstrap_across_fixed_draws.npz",**averages)
        category_differences.append({"dataset":dataset,"category":category,"draws":len(draws),
                                     "paired_differences":{m:{"point":differences[m],"interval":interval(averages[m])} for m in METRICS}})
    csv_headers=["dataset","category","method","method_label","draws",*METRICS]
    with (run/"results/per_category.csv").open("w",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=csv_headers,lineterminator="\n");writer.writeheader();writer.writerows(category_rows)
    with (run/"results/per_draw.csv").open("w",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=list(draw_rows[0]),lineterminator="\n");writer.writeheader();writer.writerows(draw_rows)
    write_json(run/"results/per_category_paired_intervals.json",category_differences)
    overall={};cluster_arrays={}
    for metric in METRICS:
        category_values={category:[d["hybrid"][metric]-d["baseline"][metric] for d in draws]
                         for (dataset,category),draws in metrics_by_category.items() if dataset=="visa"}
        samples,indices=cluster_bootstrap(category_values,cfg["bootstrap_replicates"],cfg["bootstrap_seed"])
        point=float(np.mean([np.mean(v) for v in category_values.values()]))
        overall[metric]={"paired_mean_difference":point,"category_cluster_interval":interval(samples)}
        cluster_arrays[metric]=samples
        cluster_arrays["category_indices"]=indices
    cluster_arrays["category_order"]=np.array(sorted(category_values))
    np.savez_compressed(run/"results/category_cluster_bootstrap.npz",**cluster_arrays)
    macro={method:{metric:float(np.mean([r[metric] for r in category_rows if r["dataset"]=="visa" and r["method"]==method]))
                   for metric in METRICS} for method in LABELS}
    pooled={}
    for method in LABELS:
        method_rows=[r for r in draw_rows if r["dataset"]=="visa" and r["method"]==method]
        fp,fn,normal,anomaly=(sum(r[k] for r in method_rows) for k in ("image_fp","image_fn","normal_images","anomalous_images"))
        pooled[method]={"normal_query_draw_cases":normal,"anomaly_query_draw_cases":anomaly,
                        "false_alarms":fp,"misses":fn,"image_fpr":fp/normal,"recall":1-fn/anomaly,
                        "accuracy":1-(fp+fn)/(normal+anomaly),"query_draw_cases_are_correlated":True}
    variation={}
    for method in LABELS:
        per_seed={str(seed):{metric:float(np.mean([r[metric] for r in draw_rows if r["dataset"]=="visa" and r["method"]==method and r["seed"]==seed]))
                             for metric in METRICS} for seed in cfg["target_seeds"]}
        variation[method]={"per_seed_macro":per_seed,
                           "std_across_three_draws_ddof1":{metric:float(np.std([values[metric] for values in per_seed.values()],ddof=1)) for metric in METRICS}}
    lo,hi=overall["image_auroc"]["category_cluster_interval"]
    benefit=(lo>0 and overall["image_auroc"]["paired_mean_difference"]>0
             and overall["balanced_accuracy"]["category_cluster_interval"][0]>0)
    conclusion="demonstrated benefit in this controlled known-dataset comparison" if benefit else "no demonstrated benefit"
    # One literal raw range across both methods and ALL figures, without labels.
    minimum,maximum,delta_max=np.inf,-np.inf,0.
    for row in rows:
        if row["map_shape"]!=[448,448] or row["gt_shape"]!=[448,448] or not row["lambda_zero_exact"]:raise ValueError("Sanity ledger failed")
        if file_sha256(run/row["raw_map"])!=row["raw_map_sha256"]:raise ValueError("Raw map changed")
        with np.load(run/row["raw_map"],allow_pickle=False) as z:
            minimum=min(minimum,float(z["baseline"].min()),float(z["hybrid"].min()))
            maximum=max(maximum,float(z["baseline"].max()),float(z["hybrid"].max()))
            delta_max=max(delta_max,float(np.abs(z["hybrid"].astype(float)-z["baseline"].astype(float)).max()))
    bounds=[minimum,maximum]
    write_json(run/"results/display_bounds.json",{"shared_raw_bounds":bounds,"shared_delta_range":[0.,delta_max],"scope":"All evaluated bottle and VisA images, both methods, all draws; display only"})
    selected_cut=protocol["calibration"][str(protocol["frozen_lambda"])]
    cuts={"baseline":protocol["calibration"]["0.0"],"hybrid":selected_cut}
    figure_records=[]
    for episode in protocol["target_episodes"]:
        group=[r for r in rows if (r["dataset"],r["category"],r["seed"])==(episode["dataset"],episode["category"],episode["seed"])]
        chosen=select_figures(group,cuts["hybrid"]["image"]["cutoff"])
        selected=[]
        folder=run/"results"/episode["dataset"]/episode["category"]/f"seed-{episode['seed']}"/"figures"
        folder.mkdir(exist_ok=False)
        for row in group:
            reasons=[reason for reason,identifier in chosen.items() if identifier==row["image_id"]]
            if not reasons:continue
            item={**row,"selection_reasons":reasons}
            stem=hashlib.sha256(row["image_id"].encode()).hexdigest()[:12]
            raw_name=stem+"_raw.npz";os.link(run/row["raw_map"],folder/raw_name)
            write_json(folder/(stem+"_metadata.json"),{**item,"raw_map":raw_name,"shared_raw_bounds":bounds,"delta_range":[0.,delta_max],"cutoffs":cuts})
            selected.append(item)
        render(selected,run,plan,folder/"cases.png",bounds,delta_max,cuts)
        figure_records.append({"dataset":episode["dataset"],"category":episode["category"],"seed":episode["seed"],"selection":chosen,"figure":str((folder/"cases.png").relative_to(run/"results"))})
    write_json(run/"results/figure_index.json",figure_records)
    summary={"conclusion":conclusion,"stop_without_further_search":not benefit,"frozen_lambda":protocol["frozen_lambda"],
             "visa_categories":12,"support_draws":3,"shots":1,"unique_visa_test_images":len({r["image_id"] for r in rows if r["dataset"]=="visa"}),
             "visa_query_draw_cases":sum(r["dataset"]=="visa" for r in rows),"macro_metrics":macro,"pooled_operating_metrics":pooled,
             "paired_overall":overall,"support_seed_variation":variation,"method_labels":LABELS,
             "baseline_hybrid_identical_cases":sum(r["max_abs_branch_difference"]==0 for r in rows),
             "empty_full_field_masks_on_native_anomalies":[{k:r[k] for k in ("image_id","seed")} for r in rows if r["label"] and not r["truth_pixels"]],
             "report_code_sha256":file_sha256(__file__),"protocol_sha256":file_sha256(run/"protocol.json"),
             "pixel_auroc_bootstrap_grid_point_checks":pixel_grid_errors,
             "largest_absolute_pixel_auroc_grid_point_error":max(r["absolute_grid_error"] for r in pixel_grid_errors),
             "uncertainty":"Paired query-image stratified bootstrap conditional on fixed support banks; common image weights across support draws within category; category-cluster bootstrap averages draws before resampling12 categories. Pixel AUROC bootstrap uses4096-score-rank grid; its point metric is exact. AU-PRO uses128-score-rank grid, FPR0.3. Neither resamples pixels independently.",
             "interpretation":"Known datasets with prior research exposure; no fresh-data, official reproduction or state-of-the-art claim"}
    write_json(run/"results/summary.json",summary)
    for name in ("protocol.json","protocol.json.sha256","calibration_ids.json","source_selection.json","leakage_check.json","experiment_config.json","source_reproducibility.json","unit_tests.log","analysis_plan.json","analysis_plan.json.sha256"):
        shutil.copyfile(run/name,run/"results"/name)
    lines=["# Controlled full-image source-calibrated experiment", "", f"**{conclusion}.** Frozen lambda: {protocol['frozen_lambda']}.", "",
           "VisA: all12 native categories, all2162 native test images, one-shot supports at seeds17/29/43; the three methods use exactly the same support images and no additional target normals. Bottle is development evidence only and did not select any setting.", "",
           "| Method | Image AUROC | Pixel AUROC | AU-PRO | Image FPR (macro) | Recall | Pixel IoU | Pixel F1 |", "|---|---|---|---|---|---|---|---|"]
    for method in LABELS:
        values=macro[method]
        lines.append(f"| {method} ({LABELS[method]}) | "+" | ".join(f"{values[m]:.4f}" for m in ("image_auroc","pixel_auroc","au_pro","image_fpr","recall","pixel_iou","pixel_f1"))+" |")
    lines += ["", f"Realised pooled VisA hybrid false-alarm rate: **{pooled['hybrid']['image_fpr']:.4f}** ({pooled['hybrid']['false_alarms']}/{pooled['hybrid']['normal_query_draw_cases']} correlated normal query/draw cases). The5% source calibration target is not a target-domain guarantee.", "",
              "## Paired overall differences", "", "| Metric | Hybrid minus baseline | 95% category-cluster interval |", "|---|---|---|"]
    for metric,value in overall.items():
        a,b=value["category_cluster_interval"]
        lines.append(f"| {metric} | {value['paired_mean_difference']:+.5f} | [{a:+.5f}, {b:+.5f}] |")
    lines += ["", "Per-category paired intervals, seed variation, bootstrap multiplicities and sampled curves are saved. Gains with intervals containing zero are not demonstrated improvements. No new settings were tried after target inference.", "",
              summary["uncertainty"], "", "## Protocol and deviations", "",
              "Cutoffs were fit separately for every lambda from160 AD2 train-normal images, disjoint by ID/resolved path from all supports, source selection queries and evaluation images. Strict `score > cutoff` handles calibration ties conservatively. Lambda used80 source-only AD2 public-test queries; the selection rule, candidate set and all settings were recorded before source inference, then the chosen lambda and configuration hash were sealed before target inference.", "",
              "Image and full-image GT are resized to448x448, and maps have the same448x448 shape. The complete field is scored; native-resolution pixel metrics are not claimed. Any anomalies erased by GT downsampling are listed in summary.json and retain their native image labels.", ""]
    lines += ["- "+d for d in protocol["deviations"]]
    lines += ["", "## Figures", "", "Fixed rule, one shared raw-score range across methods and all figures. Each figure has raw maps and native-ID metadata beside it. Selected cases are diagnostic examples, not random representatives. Missing false positives or misses are explicitly recorded.", ""]
    for figure in figure_records:
        lines.append(f"- [{figure['dataset']} / {figure['category']} / seed{figure['seed']}]({figure['figure']})")
    lines += ["", "## Attribution", "", "MVTec AD / AD2: MVTec Software GmbH, Bergmann et al. (CVPR2019), Heckler-Kram et al. (arXiv2503.21622,2025); derived MVTec figures/maps retain CC BY-NC-SA4.0. VisA: Zou et al., SPot-the-Difference (ECCV2022); derived VisA figures/maps retain CC BY4.0. Meta DINOv2 source/weights retain their original licensing. This is an internal baseline and adapted implementation, not an official paper reproduction.", "",
              "| Item | Status |", "|---|---|", "| Experiment code and leakage checks | unit-tested |", "| Official frozen DINOv2 weights | real-weights verified |", "| AD2 source selection and calibration | real-dataset verified |", "| Bottle development check | benchmark evaluated |", "| All12 VisA categories and three support draws | benchmark evaluated |"]
    (run/"results/README_results.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"conclusion":conclusion,"lambda":protocol["frozen_lambda"],"VisA":macro,"pooled":pooled,"paired":overall},indent=2),flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--run",type=Path,required=True)
    report(parser.parse_args().run)
