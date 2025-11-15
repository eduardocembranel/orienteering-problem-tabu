from .tabu.tabu_search import TabuSearch
from .model.op import OP
from .model.result_exporter import ResultExporter
from .model.execution_context import ExecutionContext

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance", required=True, help="Instance name (located in the ./instances directory)")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--first_improve", action="store_true", help="Enable first-improve strategy in local-search (default = best-improve)")
    parser.add_argument("--intensification", action="store_true", help="Enable intensification (default = disabled)")
    parser.add_argument("--diversification", action="store_true", help="Enable diversification (default = disabled)")
    parser.add_argument("--max_time", type=int, default=60, help="Maximum runtime (seconds)")
    parser.add_argument("--target", type=int, default=99999999, help="Score target")
    parser.add_argument("--figure_export_option", type=int, default=0, help="0: don't display/save. 1: display figures in runtime. 2: save figures in filesystem")
    parser.add_argument("--export_figure_level", type=int, default=0, help="0: export only improve solutions. 1: display all solutions during the tabu search")
    parser.add_argument("--plot_score", action="store_true", help="Whether the vertices' scores should be plotted in the exported figures (default = true)")
    parser.add_argument("--config_name", required=True, help="Name to be used to save in the result files")
    parser.add_argument("--rng", type=int, default=0, help="Seed number for random generator")

    args = parser.parse_args()

    instance = str(args.instance)
    out = str(args.out)
    first_improve = bool(args.first_improve)
    enable_intensification = bool(args.intensification)
    enable_diversification = bool(args.diversification)
    max_time = int(args.max_time)
    target = int(args.target)
    figure_export_option = int(args.figure_export_option)
    export_figure_level = int(args.export_figure_level)
    plot_score = bool(args.plot_score)
    config_name = str(args.config_name)
    rng = int(args.rng)

    print(f"Running tabu search with options:")
    print(f"Instance: {instance}")
    print(f"Output dir: {out}")
    print(f"First improve: {first_improve}")
    print(f"Intensification: {enable_intensification}")
    print(f"Diversification: {enable_diversification}")
    print(f"Tempo máximo: {max_time}")
    print(f"Target: {target}")
    print(f"Figure export option: {figure_export_option}")
    print(f"Export figure level: {export_figure_level}")
    print(f"Plot score: {plot_score}")
    print(f"Config name: {config_name}")
    print(f"Seed RNG: {rng}")

    op = OP.from_file(instance)
    context = ExecutionContext(op, config_name, out)
    exporter = ResultExporter(op, out, figure_export_option, plot_score)

    ts = TabuSearch(op, context, exporter, ls_first_improve=first_improve, enable_diversification=enable_diversification, enable_intensification=enable_intensification, max_time_sec=max_time, target=target, export_fig_lvl=export_figure_level, rng=rng)

    ts.solve()

    context.export_improves_csv()
    context.export_improve_scores_csv()
    context.export_best_sol_csv()
