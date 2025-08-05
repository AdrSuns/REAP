# Supplementary Material for REAP: A Neural-Symbolic Cognitive Architecture Based on Reasoning through Event-Abstraction and Prompting

This archive contains the full source code and raw experimental data used in the paper. It is provided to facilitate reproduction and further verification of our results.

## Contents

- `source/` – Source code for training and evaluation
- `data/` – Raw evaluation logs and step-wise scores

## Environment

- Dependencies listed in .yaml files in  the procject directory

## Usage

To reproduce the experiments:

1. Create virtual environments and install dependencies

2. How to run LLM & Reap:
    (1) Server:
        enter "source/LLM&Reap/Server" and run "python aca_api.py"
    (2) Local:
        enter "source/LLM&Reap/Local" and run "python main.py"

3. How to run RL experiment:
    enter "source/RL/t5-scienceworld" and run "python t5_test.py"
    
## Notes

- All key results and summary tables are reported in the main paper.
- This archive includes full experiment traces.
- File names and task IDs follow ScienceWorld's official definitions.

For more details, please refer to the main paper.
