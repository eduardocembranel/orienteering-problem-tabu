from .op import OP
from .solution import Solution
from ..tabu.evaluator import Evaluator

import gurobipy as gp
from typing import Any, Tuple
from pathlib import Path

import csv

class ExecutionContext:
    def __init__(self, op: OP, config_name: str, out_relative_path: str, verbose: bool=True):
        self.op = op
        self.config_name = config_name
        self.out_relative_path = out_relative_path
        self.verbose = verbose
        self.evaluator = Evaluator(op)

        self.improves = []
        self.improves_score = []

        self.best_sol = None
        self.best_score = None
        self.best_dist = None
        self.best_time = None
        self.UB = None
        self.gap = None
        self.is_optimal = None

        self._remove_old_logs()

    def log(self, msg: str, save=False):
        if self.verbose:
            print(msg)

        if save:
            with open(f"{self.out_relative_path}/logs.txt", "a") as file:
                file.write(f"{msg}\n")

    def add_improve(self, sol: Solution, time_sec: float):
        score = self.evaluator.total_score(sol)
        dist = self.evaluator.total_dist(sol)

        if self.best_sol == None or score > self.best_score:
            self.improves_score.append([self.op.instance, self.config_name, score, f"{dist:.2f}", f"{time_sec:.2f}"])

        self.best_sol = Solution.copy(sol)
        self.best_time = time_sec
        self.best_score = score
        self.best_dist = dist

        self.improves.append([self.op.instance, self.config_name, score, f"{dist:.2f}", f"{time_sec:.2f}"])

    def export_improves_csv(self):
        with open(f"{self.out_relative_path}/improves.csv", "w", encoding='utf-8') as file:
            writer = csv.writer(file)

            output = [["instance", "config", "score", "dist", "time"]] + self.improves
            writer.writerows(output)
    
    def export_improve_scores_csv(self):
        with open(f"{self.out_relative_path}/improve_scores.csv", "w", encoding='utf-8') as file:
            writer = csv.writer(file)

            output = [["instance", "config", "score", "dist", "time"]] + self.improves_score
            writer.writerows(output)

    def export_best_sol_csv(self):
        score = "" if self.best_score is None else self.best_score
        dist = "" if self.best_dist is None else f"{self.best_dist:.2f}"
        time = "" if self.best_time is None else f"{self.best_time:.2f}"
        ub = "" if self.UB is None else f"{self.UB:.2f}"
        gap = "" if self.gap is None else f"{self.gap:.2f}"

        with open(f"{self.out_relative_path}/best.csv", "w", encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows([
                ["instance", "config", "score", "dist", "UB", "gap", "time"],
                [self.op.instance, self.config_name, score, dist, ub, gap, time]
            ])

    def add_gurobi_data(self, model: gp.Model, x: gp.tupledict[Tuple[Any, ...], gp.Var]):
        self.best_sol = Solution.from_gurobi(self.op.n, x)
        self.UB = model.ObjBound
        self.gap = model.MIPGap * 100
        self.best_score = model.ObjVal
        self.best_dist = self.evaluator.total_dist(self.best_sol)
        self.best_time = model.Runtime
        self.is_optimal = model.Status == gp.GRB.OPTIMAL

    def _remove_old_logs(self):
        file = Path(f"{self.out_relative_path}/logs.txt")
        if file.exists():
            file.unlink()
