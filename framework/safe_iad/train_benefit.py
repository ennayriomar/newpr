"""Source-only grouped model fitting; target validation is reported, not tuned."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
from threadpoolctl import threadpool_limits

from .benefit_model import BenefitModel, fit_benefit_models
from .counterfactual import FEATURE_NAMES
from .experiment_io import complete_stage, read_jsonl, verify_stage, write_json, write_jsonl, input_fingerprints, implementation_hashes


def evaluate_candidate_rows(rows, model, role):
    if any(row['experiment_role'] != role for row in rows):
        raise ValueError('Mixed evaluation roles')
    vectors = [row['features'] for row in rows]
    predicted = model.predict(vectors, feature_names=FEATURE_NAMES, provenance=rows[0])
    observed = np.asarray([row['observed_benefit'] for row in rows])
    grouped = {}
    for row, prediction in zip(rows, predicted):
        key = (row['dataset'],row['category'],row['seed'],row['shots'],row['query_id'])
        grouped.setdefault(key, []).append((row,float(prediction)))
    reports = []
    iq = FEATURE_NAMES.index('candidate_query_global_distance')
    isupport = FEATURE_NAMES.index('candidate_support_global_distance')
    for (dataset,category,seed,shots,query), candidates in grouped.items():
        truth = np.asarray([row['observed_benefit'] for row,_ in candidates])
        estimate = np.asarray([value for _,value in candidates])
        salt = int.from_bytes(hashlib.sha256(f'{seed}:{query}'.encode()).digest()[:8], 'little')
        indices = {'learned':int(estimate.argmax()),
                   'random':int(np.random.default_rng(salt).integers(len(candidates))),
                   'nearest_global':int(np.argmin([row['features'][iq] for row,_ in candidates])),
                   'diversity':int(np.argmax([row['features'][isupport] for row,_ in candidates])),
                   'oracle':int(truth.argmax())}
        ranking = float(spearmanr(estimate,truth).statistic) if np.ptp(estimate)>0 and np.ptp(truth)>0 else None
        reports.append({'dataset':dataset,'category':category,'seed':seed,'shots':shots,'query_id':query,
                        'query_source_id':candidates[0][0]['query_source_id'],
                        'query_kind':candidates[0][0]['query_kind'],'candidate_count':len(candidates),
                        'rank_spearman':ranking,
                        'selected_observed_benefit':{policy:float(truth[index]) for policy,index in indices.items()},
                        'learned_prediction':float(estimate[indices['learned']]),
                        'learned_regret_to_forced_oracle':float(truth.max()-truth[indices['learned']])})
    valid_ranks=[row['rank_spearman'] for row in reports if row['rank_spearman'] is not None]
    return {'rows':len(rows),'query_support_candidate_groups':len(reports),
            'rmse':float(np.sqrt(np.mean((predicted-observed)**2))),
            'mean_candidate_rank_spearman':float(np.mean(valid_ranks)) if valid_ranks else None,
            'mean_selected_observed_benefit':{policy:float(np.mean([row['selected_observed_benefit'][policy] for row in reports]))
                                              for policy in ['learned','random','nearest_global','diversity','oracle']},
            'model_selected_using_this_validation':False,
            'scope':'normal-training and explicitly synthetic queries in disjoint validation categories; no native test masks'}, reports


def train(config):
    if not verify_stage(Path(config['output'])/'targets',require_inputs=True):
        raise ValueError('Complete verified source targets before fitting benefit models')
    output = Path(config['output'])/'models'
    output.mkdir(parents=True,exist_ok=True)
    if verify_stage(output,require_inputs=True):
        report=json.loads((output/'training_report.json').read_text())
        return BenefitModel.load(output/(report['primary_model']+'.json')),report
    source = read_jsonl(Path(config['output'])/'targets/training.jsonl')
    validation = read_jsonl(Path(config['output'])/'targets/validation.jsonl')
    with threadpool_limits(limits=1):
        models,report = fit_benefit_models(source,config['category_roles'],seed=config['model_seed'])
    report['training_target_path']=str(Path(config['output'])/'targets/training.jsonl')
    report['validation_data_used_for_primary_selection']=False
    write_json(output/'training_report.json',report)
    reports={}
    for name,model in models.items():
        model.save(output/(name+'.json'))
        restored=BenefitModel.load(output/(name+'.json'))
        vectors=[row['features'] for row in source]
        if not np.array_equal(model.predict(vectors),restored.predict(vectors)):
            raise ValueError('Model JSON reload does not reproduce predictions')
        reports[name],groups=evaluate_candidate_rows(validation,model,'validation_source_normal_or_synthetic')
        write_jsonl(output/(name+'_validation_groups.jsonl'),groups)
    write_json(output/'heldout_validation.json',reports)
    complete_stage(output,['training_report.json','heldout_validation.json','ridge.json','mlp.json',
                           'ridge_validation_groups.jsonl','mlp_validation_groups.jsonl'],
                   {'input_sha256':input_fingerprints([Path(config['output'])/'targets/training.jsonl',
                                                       Path(config['output'])/'targets/validation.jsonl',
                                                       Path(config['output'])/'targets/completion.json']),
                    'input_verification_version':1,
                    'implementation_sha256':implementation_hashes(['benefit_model.py','train_benefit.py','experiment_io.py'])})
    print(json.dumps({'primary_model':report['primary_model'],'source_rows':len(source),
                      'heldout_validation':reports}),flush=True)
    return models[report['primary_model']],report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True)
    args=parser.parse_args()
    train(json.loads(args.config.read_text()))


if __name__=='__main__':
    main()
