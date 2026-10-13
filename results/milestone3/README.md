# Milestone 3: learned reference benefit feasibility pilot

Read [the research report](research_report.md), [the method specification](method_specification.md), and [component status](status_table.csv).

The real pretrained-weight pilot completed 576 prediction records across six paired policies, eight unique native validation queries, and twelve normal stress queries. The gate stopped advancement: four detected-to-missed inspection events affected two unique VisA defect images across repeated draw/shot configurations. The learned policy's small benefit difference from nearest selection has a bootstrap interval containing zero. The matched support-omission experiment did not establish the proposed false-alarm mechanism. Full benchmark and private AD 2 evaluations remain unrun.

[Gate](evaluation/gate.json) · [artifact validation](validation.json) · [two-query fresh-cache check](real_weight_reproduction.json) · [97 test results](all_tests.log)

These files include every M3 text/JSON record, fitted source-only models, measured figures, and logs. Raw datasets, generated training images, pretrained weights, feature caches, and native NPZ arrays are separate and absent from this code/report package. Absolute-path completion ledgers provide recorded provenance; copied ledgers do not establish fresh-environment resume readiness. The [earlier complete results archive](https://github.com/ennayriomar/newpr/tree/main/results_archive) is preserved.
