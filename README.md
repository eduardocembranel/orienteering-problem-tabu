# Tabu Search for the Orienteering Problem

This project implements an Tabu Search implementation to solve the **Orieteering Problem** (OP). Also an exact algorithm using Integer Linear Programming (ILP) is provided

## Requirements

- Python 3 (3.13 recommended)
- Unix based operational system (optional)

## 1. Clone the repository
```
git clone https://github.com/eduardocembranel/orienteering-problem-tabu.git
cd orienteering-problem-tabu
```

## 2. Activate a virtual environment (venv)
```
python3 -m venv venv
source venv/bin/activate
```

## 3. Install the packages (gurobi)
```
pip install -r requirements.txt
```

## 4. Run the algorithms

for the tabu search
```
python -m src.run_tabu_search [options]
```

for the ilp solver
```
python -m src.run_ilp [options]
```
>To see all available options run the above command with the `--help` flag

## Run experiments

To run all the experiments for the tabu search variations
```bash
./run_experiments_tabu_search.sh
```

To run all the experiments for the ilp solver
```bash
./run_experiments_ilp.sh
```
>The results will be available in the directories `./results/<instance>/<config>`
