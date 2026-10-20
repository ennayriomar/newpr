"""One locked AD2-source / full-image bottle-and-VisA controlled experiment.

No target images enter source selection or calibration. Source and target
stages are separate commands; target inference requires a sealed protocol.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import gc
import hashlib
import json
from pathlib import Path
import random
import time

import numpy as np
from PIL import Image
import torch

from controlled_common import (LABELS, LAMBDAS, METRICS, canonical_hash, cluster_bootstrap,
    full_prediction, full_truth, measured_metrics, normal_cutoff, paired_bootstrap,
    save_sealed, select_figures, validate_roles)
from utils import file_sha256, read_json, use_local_framework, write_json

use_local_framework()
from safe_iad.safal_cli import inventory
from safe_iad.vision_hybrid_features import RegisterEncoder, SLOTS, preprocess, support_inputs, transform
from safe_iad.vision_hybrid_model import HybridParameters, VisionHybrid


def event(run, **value):
    value = {"utc": datetime.now(timezone.utc).isoformat(), **value}
    line = json.dumps(value, allow_nan=False)
    with (run/"progress.jsonl").open("a") as handle:handle.write(line+"\n")
    print(line, flush=True)


def code_hashes():
    root = Path(__file__).parent
    names = ["controlled_experiment.py", "controlled_common.py", "audit_outputs.py", "utils.py"]
    names += ["framework/safe_iad/"+name for name in ("vision_hybrid_model.py", "vision_hybrid_features.py", "safal_features.py", "research_metrics.py", "verify_dataset.py")]
    return {name: file_sha256(root/name) for name in names}


def record(dataset, root, sample):
    return {"image_id": dataset+":"+sample.image, "dataset": dataset,
            "path": str(root/sample.image), "native_id": sample.image,
            "mask": str(root/sample.mask) if sample.mask else None,
            "category": sample.category, "split": sample.split, "label": sample.label}


def choose_support(rows, seed, shots=1):
    ids = sorted(r["image_id"] for r in rows if r["split"] == "train" and r["label"] == "normal")
    selected = random.Random(seed).sample(ids, max(shots, 1))
    # The maximum-shot draw is fixed first; smaller budgets are prefixes. This
    # experiment has k=1, so nesting does not add target training images.
    return selected[:shots]


def prepare(run):
    config = read_json(run/"experiment_config.json")
    if (run/"source_plan.json").exists():raise ValueError("Source plan already exists")
    inventories = {}
    for dataset, key in (("mvtec_ad2", "source_root"), ("mvtec_ad", "bottle_root"), ("visa", "visa_root")):
        root, samples = inventory({"roots": {dataset: config[key]}}, dataset)
        inventories[dataset] = [record(dataset, root, s) for s in samples.values()]
    source = inventories["mvtec_ad2"]
    categories = sorted({r["category"] for r in source})
    episodes, calibration, selection = [], [], []
    for i, category in enumerate(categories):
        rows = [r for r in source if r["category"] == category]
        support = choose_support(rows, config["source_seed"])
        available = sorted(r["image_id"] for r in rows if r["split"] == "train" and r["label"] == "normal" and r["image_id"] not in support)
        chosen_cal = random.Random(config["split_seed"]+i).sample(available, config["calibration_normals_per_ad2_category"])
        queries = []
        for label, key in (("normal", "source_query_normals_per_category"), ("anomaly", "source_query_anomalies_per_category")):
            available = sorted(r["image_id"] for r in rows if r["split"] == "test_public" and r["label"] == label)
            queries += random.Random(config["split_seed"]+100+i).sample(available, config[key])
        episodes.append({"dataset": "mvtec_ad2", "category": category, "seed": config["source_seed"],
                         "support_ids": support, "calibration_ids": chosen_cal, "query_ids": sorted(queries)})
        calibration += chosen_cal;selection += queries
    targets = []
    bottle = [r for r in inventories["mvtec_ad"] if r["category"] == "bottle"]
    targets.append({"dataset": "mvtec_ad", "category": "bottle", "seed": 17,
                    "support_ids": choose_support(bottle, 17),
                    "query_ids": sorted(r["image_id"] for r in bottle if r["split"] == "test"),
                    "scope": "development check; never selects settings"})
    for category in sorted({r["category"] for r in inventories["visa"]}):
        rows = [r for r in inventories["visa"] if r["category"] == category]
        for seed in config["target_seeds"]:
            targets.append({"dataset": "visa", "category": category, "seed": seed,
                            "support_ids": choose_support(rows, seed),
                            "query_ids": sorted(r["image_id"] for r in rows if r["split"] == "test"),
                            "scope": "actual target; all native test IDs"})
    lookup = {r["image_id"]:r for rows in inventories.values() for r in rows}
    all_support = sorted({k for episode in episodes+targets for k in episode["support_ids"]})
    evaluation = sorted({k for episode in targets for k in episode["query_ids"]})
    roles = {name:[lookup[k] for k in values] for name, values in
             (("support", all_support), ("calibration", calibration), ("source_query", selection), ("evaluation", evaluation))}
    leakage = validate_roles(roles)
    plan = {"config_sha256": file_sha256(run/"experiment_config.json"), "config": config,
            "source_episodes": episodes, "target_episodes": targets,
            "records": {k:lookup[k] for k in sorted(set(all_support+calibration+selection+evaluation))},
            "roles": roles, "leakage_check": leakage, "code_sha256": code_hashes(),
            "target_data_access_before_freeze": "Native split/ID metadata only; no image pixels, masks or scores"}
    save_sealed(run/"source_plan.json", plan)
    write_json(run/"leakage_check.json", leakage)
    event(run, stage="prepared", **leakage)


def validate_plan(run):
    plan = read_json(run/"source_plan.json")
    if file_sha256(run/"source_plan.json") != (run/"source_plan.json.sha256").read_text().split()[0]:raise ValueError("Source plan changed")
    if file_sha256(run/"experiment_config.json") != plan["config_sha256"]:raise ValueError("Config changed")
    if code_hashes() != plan["code_sha256"]:raise ValueError("Implementation changed after source plan")
    validate_roles(plan["roles"])
    return plan


def encoder(config):
    return RegisterEncoder(config["source_dir"], config["checkpoint"], device="cpu", threads=config["threads"],
                           resize=448, crop=448, layers=config["layers"])


def bank_for(episode, plan, enc, destination):
    features, slots = [], {slot:[] for slot in SLOTS}
    support_hashes = {}
    for identifier in episode["support_ids"]:
        row = plan["records"][identifier];before = file_sha256(row["path"])
        values, indices = enc.support(row["path"])
        offset = len(features);features.extend(values)
        for slot in SLOTS:slots[slot].extend(offset+i for i in indices[slot])
        if file_sha256(row["path"]) != before:raise ValueError("Support input changed")
        support_hashes[identifier] = before
    model = VisionHybrid(features, slots, episode["support_ids"], clusters=(1,), variances=(.95,), threads=plan["config"]["threads"])
    destination.mkdir(parents=True, exist_ok=False)
    np.savez_compressed(destination/"support_features.npz", **{f"view_{i:03d}":x.numpy() for i,x in enumerate(features)})
    write_json(destination/"support.json", {"episode": episode, "input_sha256": support_hashes,
        "encoder": enc.metadata(), "model": model.metadata(), "same_support_for_all_methods": True,
        "extra_target_normal_images": 0, "support_features_sha256": file_sha256(destination/"support_features.npz")})
    return model


def query(row, enc):
    before = file_sha256(row["path"])
    features = enc.query(row["path"])
    if file_sha256(row["path"]) != before:raise ValueError("Query changed during inference")
    return features, before


def repeat_check(row, enc, models, strengths, expected):
    again, _ = query(row, enc)
    actual = []
    for model in models:
        raw = model.raw(again)
        actual.append([full_prediction(raw, strength, model.grid)[1] for strength in strengths])
    if actual != expected:raise ValueError("Same-seed repeated real inference produced different scores")
    return {"image_id": row["image_id"], "identical_scores": True, "scores": actual,
            "same_frozen_bank_and_seed": True, "encoder_inference_repeated": True}


def source(run):
    plan = validate_plan(run);cfg=plan["config"]
    if (run/"protocol.json").exists():raise ValueError("Source selection already frozen")
    enc=encoder(cfg);event(run, stage="real_weights_verified", encoder=enc.metadata())
    all_images={str(v):[] for v in LAMBDAS};all_pixels={str(v):[] for v in LAMBDAS}
    candidates={str(v):[] for v in LAMBDAS};sanities=[]
    for episode in plan["source_episodes"]:
        category=episode["category"];out=run/"source"/category
        model=bank_for(episode, plan, enc, out/"bank")
        event(run, stage="source_bank", category=category, support_ids=episode["support_ids"])
        for role in ("calibration", "query"):
            folder=out/role;folder.mkdir()
            for i, identifier in enumerate(episode[role+"_ids"]):
                row=plan["records"][identifier]
                features, image_hash=query(row, enc);raw=model.raw(features)
                arrays={};scores={}
                for strength in LAMBDAS:
                    score_map, score=full_prediction(raw, strength, model.grid)
                    arrays["lambda_"+str(strength)]=score_map;scores[str(strength)]=score
                    if role=="calibration":
                        all_images[str(strength)].append(score);all_pixels[str(strength)].append(score_map.ravel())
                    else:
                        candidates[str(strength)].append({"category":category,"image_id":identifier,"label":int(row["label"]!="normal"),"score":score})
                control,_=full_prediction(raw,0,model.grid)
                if not np.array_equal(control,arrays["lambda_0.0"]):raise ValueError("Zero strength differs from baseline")
                np.savez_compressed(folder/f"map-{i:04d}.npz", **arrays)
                with (out/(role+".jsonl")).open("a") as handle:
                    handle.write(json.dumps({"image_id":identifier,"image_sha256":image_hash,"scores":scores,"role":role},allow_nan=False)+"\n")
                if role=="query" and i==0 and not sanities:
                    sanities.append(repeat_check(row,enc,[model],LAMBDAS,[[scores[str(v)] for v in LAMBDAS]]))
                event(run, stage="source_"+role, category=category, completed=i+1,total=len(episode[role+"_ids"]))
        del model;gc.collect()
    calibration={}
    for strength in LAMBDAS:
        key=str(strength)
        calibration[key]={"image":normal_cutoff(all_images[key],cfg["image_fpr"]),
                          "pixel":normal_cutoff(np.concatenate(all_pixels[key]),cfg["pixel_fpr"])}
    selection=[]
    from sklearn.metrics import roc_auc_score
    for strength in LAMBDAS:
        key=str(strength);category_metrics=[]
        for category in sorted({r["category"] for r in candidates[key]}):
            rows=[r for r in candidates[key] if r["category"]==category]
            truth=np.array([r["label"] for r in rows]);scores=np.array([r["score"] for r in rows]);pred=scores>calibration[key]["image"]["cutoff"]
            category_metrics.append({"category":category,"balanced_accuracy":float((pred[truth==1].mean()+1-pred[truth==0].mean())/2),"image_auroc":float(roc_auc_score(truth,scores))})
        selection.append({"lambda":strength,"mean_balanced_accuracy":float(np.mean([r["balanced_accuracy"] for r in category_metrics])),
                          "mean_image_auroc":float(np.mean([r["image_auroc"] for r in category_metrics])),"categories":category_metrics})
    chosen=max(selection,key=lambda r:(r["mean_balanced_accuracy"],r["mean_image_auroc"],-r["lambda"]))["lambda"]
    write_json(run/"source_selection.json",{"candidates":selection,"selected_lambda":chosen,"calibration":calibration,"selection_images":"AD2 public-test queries only","cutoff_images":"AD2 train normals only"})
    write_json(run/"source_reproducibility.json",sanities)
    write_json(run/"calibration_ids.json",plan["roles"]["calibration"])
    protocol={"frozen_at_utc":datetime.now(timezone.utc).isoformat(),"frozen_lambda":chosen,
        "config_sha256":plan["config_sha256"],"config":cfg,"source_plan_sha256":file_sha256(run/"source_plan.json"),
        "source_selection_sha256":file_sha256(run/"source_selection.json"),"code_sha256":code_hashes(),
        "calibration":calibration,"calibration_ids_sha256":file_sha256(run/"calibration_ids.json"),
        "target_episodes":plan["target_episodes"],"encoder":enc.metadata(),"leakage_check":plan["leakage_check"],
        "evaluation_images_seen_before_freeze":False,"source_normal_calibration_images":len(plan["roles"]["calibration"]),
        "method_labels":LABELS,"figure_rule":cfg["figure_rule"],"deviations":cfg["deviations"],
        "pixel_auroc_intervals":"Query-image bootstrap on fixed4096-score-rank ROC grid; exact reported point is also saved; approximation disclosed separately"}
    save_sealed(run/"protocol.json",protocol)
    event(run,stage="lambda_frozen",selected_lambda=chosen,protocol_sha256=file_sha256(run/"protocol.json"))


def evaluate(run):
    plan=validate_plan(run);protocol=read_json(run/"protocol.json");cfg=plan["config"]
    if file_sha256(run/"protocol.json")!=(run/"protocol.json.sha256").read_text().split()[0]:raise ValueError("Protocol changed")
    if protocol["code_sha256"]!=code_hashes():raise ValueError("Code changed after freeze")
    strength=protocol["frozen_lambda"];selected=protocol["calibration"][str(strength)]
    cuts={"baseline":protocol["calibration"]["0.0"],"hybrid":selected,"lambda_zero":protocol["calibration"]["0.0"]}
    enc=encoder(cfg);sanities=[]
    grouped={}
    for episode in plan["target_episodes"]:grouped.setdefault((episode["dataset"],episode["category"]),[]).append(episode)
    for (dataset,category),episodes in grouped.items():
        root=run/"results"/dataset/category;root.mkdir(parents=True,exist_ok=False)
        models=[bank_for(e,plan,enc,root/f"seed-{e['seed']}"/"bank") for e in episodes]
        truths=[];maps=[{"baseline":[],"hybrid":[]} for e in episodes];rows=[[] for e in episodes]
        for index,identifier in enumerate(episodes[0]["query_ids"]):
            row=plan["records"][identifier]
            features,image_hash=query(row,enc)
            # Target labels/masks enter only AFTER extracting both raw branches.
            raw_branches=[model.raw(features) for model in models]
            truth=full_truth(row["path"],row["mask"]);truths.append(truth)
            mask_hash=file_sha256(row["mask"]) if row["mask"] else None
            expected=[]
            for j,(episode,model,raw) in enumerate(zip(episodes,models,raw_branches)):
                base,bscore=full_prediction(raw,0,model.grid);hybrid,hscore=full_prediction(raw,strength,model.grid)
                zero,zscore=full_prediction(raw,0,model.grid)
                if not np.array_equal(base,zero) or bscore!=zscore:raise ValueError("Lambda0 control is not exact baseline")
                if base.shape!=truth.shape or hybrid.shape!=truth.shape:raise ValueError("Map and full-frame GT shape mismatch")
                delta=hybrid.astype(float)-base.astype(float)
                pred=hybrid>cuts["hybrid"]["pixel"]["cutoff"];union=(pred|truth).sum()
                item={"dataset":dataset,"category":category,"seed":episode["seed"],"shots":1,"image_id":identifier,"native_id":row["native_id"],
                    "image_sha256":image_hash,"mask_sha256":mask_hash,"label":int(row["label"]!="normal"),
                    "scores":{"baseline":bscore,"hybrid":hscore,"lambda_zero":zscore},"method_labels":LABELS,
                    "decisions":{m:s>cuts[m]["image"]["cutoff"] for m,s in (("baseline",bscore),("hybrid",hscore),("lambda_zero",zscore))},
                    "truth_pixels":int(truth.sum()),"hybrid_pixel_iou":float((pred&truth).sum()/union) if union else None,
                    "max_abs_branch_difference":float(abs(delta).max()),"mean_abs_branch_difference":float(abs(delta).mean()),
                    "lambda_zero_exact":True,"map_shape":list(base.shape),"gt_shape":list(truth.shape),"scored_field_fraction":1.,
                    "protocol_sha256":file_sha256(run/"protocol.json"),"support_ids":episode["support_ids"]}
                dest=root/f"seed-{episode['seed']}"/"maps";dest.mkdir(exist_ok=True)
                np.savez_compressed(dest/f"map-{index:04d}.npz",baseline=base,hybrid=hybrid,truth=truth.astype(np.uint8))
                item["raw_map"]=str((dest/f"map-{index:04d}.npz").relative_to(run))
                item["raw_map_sha256"]=file_sha256(dest/f"map-{index:04d}.npz")
                rows[j].append(item);maps[j]["baseline"].append(base);maps[j]["hybrid"].append(hybrid)
                with (run/"results/per_image.jsonl").open("a") as handle:handle.write(json.dumps(item,allow_nan=False)+"\n")
                expected.append([bscore,hscore,zscore])
            if index==0:sanities.append(repeat_check(row,enc,models,[0,strength,0],expected))
            event(run,stage="target_query",dataset=dataset,category=category,completed=index+1,total=len(episodes[0]["query_ids"]),support_draws=len(episodes))
        for j,episode in enumerate(episodes):
            folder=root/f"seed-{episode['seed']}"
            measured={}
            for method in ("baseline","hybrid"):
                measured[method]=measured_metrics(truths,maps[j][method],[r["label"] for r in rows[j]],[r["scores"][method] for r in rows[j]],cuts[method])
                measured[method]["method_label"]=LABELS[method]
            measured["lambda_zero"]={**measured["baseline"],"method_label":LABELS["lambda_zero"],"exact_control":True}
            write_json(folder/"metrics.json",measured)
            boot=paired_bootstrap(truths,maps[j],rows[j],cuts,cfg["bootstrap_replicates"],cfg["bootstrap_seed"])
            np.savez_compressed(folder/"bootstrap.npz",**boot)
            write_json(folder/"image_ids.json",[r["image_id"] for r in rows[j]])
            write_json(folder/"figure_selection.json",select_figures(rows[j],cuts["hybrid"]["image"]["cutoff"]))
            event(run,stage="target_metrics",dataset=dataset,category=category,seed=episode["seed"],metrics=measured)
        write_json(run/"results/reproducibility.json",sanities)
        del models,maps,truths,rows;gc.collect()
    event(run,stage="all_target_inference_complete")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage",choices=["prepare","source","evaluate"])
    parser.add_argument("--run",type=Path,required=True)
    args=parser.parse_args()
    {"prepare":prepare,"source":source,"evaluate":evaluate}[args.stage](args.run.resolve(strict=True))


if __name__=="__main__":main()
