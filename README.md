# Tabu Search

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

## 4. Run the tabu search algorithm

```
python -m src.run_tabu_search [options]
```

## Run experiments

To run all the experiments for the tabu search variations
```bash
./run_experiments_tabu_search.sh
```

To run all the experiments for the ilp solver
```bash
./run_experiments_ilp.sh
```

To run `intensification` heuristic with an spectific target with 50 independent executions for the instance `exact_n200`, in order to have empirical data for later analasys
```
# With an "easy" target
./run_easy_target.sh

# With an "medium" target
./run_easy_target.sh

# With an "hard" target
./run_easy_target.sh
```

## Run for a single instance

```
java -cp out Main <instance_name> <method>
```

####  Run example for the instance *exact_n25* with method *std*
```
java -cp out Main exact_n25 std
```

#### Available instances are those present in the `./instances` and the <instance_name> is the name of the file (without the extension)

#### Available methods are:
* std
* std+t2
* std+best
* std+div
* std+int

## See the results

The result output will be available in the file `./results/<method>/<instance_name>.txt`
