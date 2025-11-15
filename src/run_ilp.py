from .ilp.solver import ILPSolver
from .model.op import OP
from .model.result_exporter import ResultExporter
from .model.execution_context import ExecutionContext

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance", required=True, help="Instance name (located in the ./instances directory)")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--max_time", type=int, default=60, help="Maximum runtime (seconds)")
    parser.add_argument("--figure_export_option", type=int, default=0, help="0: don't display/save. 1: display figures in runtime. 2: save figures in filesystem")
    parser.add_argument("--plot_score", action="store_true", help="Whether the vertices' scores should be plotted in the exported figures (default = true)")
    parser.add_argument("--config_name", required=True, help="Name to be used to save in the result files")

    args = parser.parse_args()

    instance = str(args.instance)
    out = str(args.out)
    max_time = int(args.max_time)
    config_name = str(args.config_name)
    figure_export_option = str(args.figure_export_option)
    plot_score = bool(args.plot_score)
    
    print(f"Running ILP solver with options:")
    print(f"Instance: {instance}")
    print(f"Output dir: {out}")
    print(f"Tempo máximo: {max_time}")
    print(f"Figure export option: {figure_export_option}")
    print(f"Plot score: {plot_score}")
    print(f"Config name: {config_name}")

    op = OP.from_file(instance)
    context = ExecutionContext(op, config_name, out)
    exporter = ResultExporter(op, out_relative_path=out, figure_export_option=figure_export_option, plot_score=plot_score)

    solver = ILPSolver(op=op, context=context, exporter=exporter, max_time_sec=max_time)

    solver.solve()
    
    context.export_best_sol_csv()
    context.export_improves_csv()
