# ICS HTTP Cache Simulator Roadmap

[简体中文](roadmap.zh-CN.md)

All team deadlines use Shanghai time. The Brightspace deadline is Friday, December 4, 2026 at 17:59. Aim to have the final ZIP and video link ready by December 3 at 21:00.

## Implementation plan

The simulator is a Python 3.10+ command-line program. The starter uses the standard library. `cache_sim/models.py` defines the records, `cache_sim/io.py` adapts CSV files, `cache_sim/simulator.py` processes requests and calculates metrics, `cache_sim/policies.py` contains replacement rules, and `cache_sim/__main__.py` defines the CLI. `tests/` contains the test suite, and `examples/` contains the synthetic CSV fixtures. The CLI exports global and per-client metrics as JSON so the experiment runner can collect them consistently.

The simulation core owns capacity accounting, hit/miss modeling, counters for cached entries, and per-client attribution. Replacement policies select an eviction victim from the current entries. An optional event callback can capture ordered hits, misses, and evictions for reference validation. The CSV reader consumes rows in chronological file order. The synthetic fixtures use an explicitly documented CSV schema. Confirm the course headers and units when the reference files arrive.

For reference validation, start with an empty 102,400-byte cache, use a 5 ms hit latency and each resource's stated origin latency on misses, and bypass storage for oversized objects. For every evaluation run use a fresh cache and the same inputs and configuration across policies. Report request and byte hit ratios, mean latency, and origin bytes globally and per client. Store raw measurements and the commands and inputs needed to reproduce them.

## Owners and work items

| Owner | Due | Deliverable | Acceptance check |
| --- | --- | --- | --- |
| Oscar | Nov 20 | Inventory the course inputs and hand-calculate a small validation trace | Provide both CSVs and reference outputs through the team workspace, document headers and units, and write expected events and metrics for a small synthetic trace. |
| Alyx | Nov 23 | Finish FIFO, LRU, and LFU | Unit tests distinguish hit effects and LFU tie-breaking, cover multiple evictions, and verify oversized bypass and exact capacity. |
| Daniel | Nov 23 | Integrate official CSV input and request event export | Load the supplied files, provide a CLI command for exporting ordered hit/miss/eviction events, and test running from a fresh clone. |
| Ryan | Nov 23 | Specify the custom policy and experiment protocol | State the objective, eviction/admission rules, deterministic tie-break, hypotheses, and workload/capacity selections before reviewing final results. |
| Alyx | Nov 25 | Verify the three baselines against course outputs | Compare all published measures and event details available, document mismatch resolutions, and preserve a repeatable validation command. |
| Oscar | Nov 25 | Prepare three repeatable workload traces | Produce repetitive, sequential, and mixed workloads from Ryan's design, with pattern definitions, client IDs, and a seed if generated. |
| Daniel | Nov 27 | Automate the policy/workload/capacity matrix | Run the configurations with empty caches and export stable machine-readable global and client rows. Document one reproduction command. |
| Ryan | Nov 27 | Implement and test the custom policy | Register it in the CLI, test the chosen scoring and tie rules, and show an expected effect with a focused synthetic trace. |
| Ryan | Nov 29 | Run experiments and prepare results, figures, and report analysis | Save raw data. Explain changes across workloads and capacities, trade-offs between metrics, and outcomes for individual clients. |
| Alyx | Dec 1 | Audit experiment correctness and contribute technical report sections | Spot-check independent metrics and policy behavior, and write the simulator, data structures, and reference-validation sections. |
| Oscar | Dec 2 | Write HOWTO, test a clean copy, and coordinate the recorded demo | Another teammate reproduces a run from HOWTO. Coordinate a 12-minute script with one three-minute segment per member and a reproducible CLI demo. |
| Daniel | Dec 3 | Integrate the 3–4 page report and verify the submission package | Test the extracted ZIP, verify inputs, outputs, instructions and report are included, and check the YouTube link before Brightspace submission. |

## Checkpoints

- **Nov 23 at 21:00** — Standard policies, official input path, and custom strategy proposal ready. Daniel reviews the integration, and Alyx reviews assumptions with Ryan.
- **Nov 29 at 21:00** — Baselines validated, custom policy tested, experiment matrix run, and preliminary figures ready. Ryan reviews the workload traces with Oscar, and Alyx spot-checks results.
- **Dec 3 at 21:00** — Report and ZIP reviewed, all four contributions recorded, and link tested. Daniel and Oscar check the exact submission files together.

Start workload preparation and custom-policy design while the baselines are under development. Use the complete reference run and confirmed official metrics before drawing final conclusions. Each teammate reviews the issues they depend on and explains their own contribution in the presentation.
