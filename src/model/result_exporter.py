from .op import OP
from ..tabu.evaluator import Evaluator

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import os
from pathlib import Path

class ResultExporter:
    def __init__(self, op: OP, out_relative_path: str, figure_export_option: int, plot_score: bool=True):
        self.op = op
        self.out_relative_path = out_relative_path
        self.figure_export_option = figure_export_option
        self.plot_score = plot_score
        self.evaluator = Evaluator(op)

        self._remove_old_figures()

    def _remove_old_figures(self):
        folder = Path(f"{self.out_relative_path}/figures")
        folder.mkdir(parents=True, exist_ok=True)
        for file in folder.glob("*.png"):
            file.unlink()  # deleta o arquivo

    def export_solution_figure(self, sol, file_name: str):
        if self.figure_export_option == 0 or sol is None:
            return

        # Coordenadas dos pontos
        points = [(v.x, v.y) for v in self.op.V]

        # Conexões da solução
        arcs = []
        for i in range(len(sol.next)):
            if sol.next[i] is not None:
                arcs.append((i, sol.next[i]))

        x, y = zip(*points)
        scores = [v.score for v in self.op.V]

        # Cria a figura e eixo
        fig, ax = plt.subplots(figsize=(8, 8))

        # Plota os pontos
        ax.scatter(x, y, color='black', edgecolors='black', zorder=5)

        # Plota as setas
        for p1, p2 in arcs:
            x1, y1 = points[p1]
            x2, y2 = points[p2]
            arrow = mpatches.FancyArrowPatch(
                (x1, y1), (x2, y2),
                mutation_scale=15,
                color='red',
                arrowstyle='->',
                linewidth=1.5,
                zorder=4
            )
            ax.add_patch(arrow)

        # Rótulo dos scores
        if self.plot_score:
            for i, (xi, yi) in enumerate(zip(x, y)):
                ax.text(xi, yi + 0.2, f'{scores[i]}', ha='center', fontsize=12, color='black', fontweight='bold')
        
        # Aspect ratio igual e sem eixos
        ax.set_aspect('equal', adjustable='datalim')
        ax.axis('off')

        # Lucro e distância
        lucro = self.evaluator.total_score(sol)
        distancia = self.evaluator.total_dist(sol)
        ax.text(
            0, 1,
            f"Lucro: {lucro}\nDistância: {distancia:.2f}",
            transform=ax.transAxes,
            fontsize=11,
            color='black',
            fontweight='bold',
            verticalalignment='top',
            horizontalalignment='left',
            bbox=dict(facecolor='white', alpha=0.2, edgecolor='none', pad=0)
        )

        # Ajusta layout e salva/mostra
        plt.tight_layout()
        if self.figure_export_option == 1:
            plt.show()
        else: # == 2
            filepath = f'{self.out_relative_path}/figures/{file_name}.png'
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            plt.savefig(filepath, bbox_inches='tight', pad_inches=0)

        plt.close('all')
