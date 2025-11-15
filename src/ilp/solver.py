import gurobipy as gp
from gurobipy import GRB

from ..model.op import OP
from ..model.execution_context import ExecutionContext
from ..model.result_exporter import ResultExporter
from ..model.solution import Solution

class ILPSolver:
    def __init__(self, op: OP, context: ExecutionContext, exporter: ResultExporter, max_time_sec: int):
        self.op = op
        self.context = context
        self.exporter = exporter
        self.max_time_sec = max_time_sec

        self.export_fig_count = 0

    def solve(self) -> ExecutionContext:
        model = gp.Model("op")
        model.setParam("TimeLimit", self.max_time_sec)
        
        x = model.addVars(
            [(i, j) for i in range(self.op.n) for j in range(self.op.n)],
            vtype=GRB.BINARY,
            name="x"
        )

        u = model.addVars(range(self.op.n), vtype=GRB.INTEGER, name="u")

        model.setObjective(
            gp.quicksum(self.op.V[i].score * x[i, j] for i in range(1, self.op.n-1) for j in range(1, self.op.n)),
            GRB.MAXIMIZE
        )

        model.addConstr(
            gp.quicksum(x[i, i] for i in range(self.op.n)) == 0
        )

        model.addConstr(
            gp.quicksum(x[0, i] for i in range(1, self.op.n)) == 1
        )

        model.addConstr(
            gp.quicksum(x[i, self.op.n-1] for i in range(self.op.n-1)) == 1
        )

        for k in range(1, self.op.n-1):
            arcs_in = gp.quicksum(x[i, k] for i in range(self.op.n-1))
            arcs_out = gp.quicksum(x[k, i] for i in range(1, self.op.n))
            model.addConstr(arcs_in <= 1)
            model.addConstr(arcs_out <= 1)
            model.addConstr(arcs_in == arcs_out)

        model.addConstr(
            gp.quicksum(self.op.A[i][j] * x[i, j] for i in range(self.op.n-1) for j in range(1, self.op.n) if i != j) <= self.op.t_max
        )

        for i in range(1, self.op.n-1):
            model.addConstr(u[i] >= 2)
            model.addConstr(u[i] <= self.op.n - 1)

        for i in range(1, self.op.n-1):
            for j in range(1, self.op.n-1):
                model.addConstr(u[i] - u[j] + 1 <= (self.op.n - 2) * (1 - x[i, j]))

        model._x = x

        def save_new_best_sol(model: gp.Model, where):
            if where == GRB.Callback.MIPSOL:
                runtime = model.cbGet(GRB.Callback.RUNTIME)
                x_vals = model.cbGetSolution(model._x)

                selected_arcs = [(i, j) for (i, j), val in x_vals.items() if val > 0.5]

                sol = Solution.from_arcs(self.op.n, selected_arcs)
                self.context.add_improve(sol, float(runtime))
                self.export_figure(sol, "improve_global")

        model.optimize(save_new_best_sol)

        self.context.add_gurobi_data(model, x)

    def export_figure(self, sol: Solution, fig_name: str):
        self.exporter.export_solution_figure(sol, f"{self.export_fig_count}_{fig_name}")
        self.export_fig_count += 1