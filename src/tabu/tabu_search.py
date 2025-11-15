from ..model.op import OP 
from ..model.solution import Solution
from ..model.result_exporter import ResultExporter
from ..model.execution_context import ExecutionContext
from .evaluator import Evaluator
from .move.move import Move
from .move.insertion_move import InsertionMove
from .move.relocate_move import RelocateMove
from .move.two_opt_move import TwoOptMove
from .move.replace_move import ReplaceMove
from .tabu_list import TabuList

import random
import time

class TabuSearch:
    def __init__(self, op: OP, context: ExecutionContext, exporter: ResultExporter, ls_first_improve: bool, enable_diversification: bool, enable_intensification: bool, max_time_sec: int, target: int, export_fig_lvl: int, rng: int=0):
        self.op = op
        self.evaluator = Evaluator(op)
        self.max_time_sec = max_time_sec
        self.target = target
        self.enable_diversification = enable_diversification
        self.enable_intensification = enable_intensification
        self.rng = rng
        self.sol = None
        self.best_sol = None
        self.context = context

        self.ls_first_improve = ls_first_improve

        self.exporter = exporter

        tabu_tenure = max(3, int(op.n * 0.3))
        self.tabu_list = TabuList(tabu_tenure)

        self.export_fig_lvl = export_fig_lvl
        self.export_fig_count = 0

        random.seed(rng)

    class LocalSearchState:
        def __init__(self, evaluator: Evaluator, sol: Solution, best_sol: Solution):
            # best moves & deltas
            self.best_delta_dist = float("+inf")
            self.best_dist_move: Move | None = None
            self.best_delta_score = float("-inf")
            self.best_score_move: Move | None = None
            self.best_delta_ratio = float("-inf")
            self.best_ratio_move: Move | None = None

            # current & best solution metrics
            self.score_cur_sol = evaluator.total_score(sol)
            self.dist_cur_sol = evaluator.total_dist(sol)
            self.score_best_sol = evaluator.total_score(best_sol)
            self.dist_best_sol = evaluator.total_dist(best_sol)

    def solve(self):
        self.start = time.time()

        self.sol = self.constructive_heuristic()
        self.best_sol = Solution.copy(self.sol)

        itr = 0
        last_solution_change_itr = 0
        
        while self._time_elapsed() < self.max_time_sec and not self.best_sol.are_all_vertices_in_path() and self.evaluator.total_score(self.best_sol) < self.target:
            self.local_search(itr, last_solution_change_itr)

            if self._update_best_sol():
                last_solution_change_itr = itr     
                self._save_improve_data("[local_search] best sol improved", "improve_global", self.best_sol)           

            if self._trigger_diversification_criteria(itr, last_solution_change_itr):
                last_solution_change_itr = itr
                self._diversify()
                self._export_figure(self.sol, "diversify")

            itr += 1

    def constructive_heuristic(self) -> Solution:
        self.sol = Solution.create_trivial_path(self.op.n)

        while True:
            best_delta_ratio = float('-inf')
            best_candidate: Move = None

            for candidate in self.evaluator.insertion_candidates(self.sol):
                if candidate.delta_ratio() > best_delta_ratio:
                    best_delta_ratio = candidate.delta_ratio()
                    best_candidate = candidate

            if best_candidate is not None:
                best_candidate.apply_move(self.sol)
                self._save_improve_data("[constructive_heuristic] best sol improved", "constructive_heuristic", self.sol)
            else:
                break

        self.context.log(f"[constructive_heuristic] finished construction phase, {self.sol}", save=True)
        self._export_figure(self.sol, "constructive_heuristic_sol", lvl=0)

        return self.sol
    
    def _export_figure(self, sol: Solution, name: str, lvl: int=1):
        if lvl <= self.export_fig_lvl:
            self.exporter.export_solution_figure(sol, f"{self.export_fig_count}_{name}")
            self.export_fig_count += 1

    def local_search(self, itr: int, last_solution_change_itr: int):
        self._update_tabus(itr)

        state = self.LocalSearchState(self.evaluator, self.sol, self.best_sol)
        if self._search_insertion(state):
            self._export_figure(self.sol, "insertion")
            return
        
        if self._search_replace(state):
            self._export_figure(self.sol, "replace")
            return
    
        if state.best_delta_score > 0.0 and not self._is_move_forbidden(state.best_score_move, state, use_metric_score=True):
            self.context.log(f"[local_search] applying best score move: {state.best_score_move}")
            state.best_score_move.apply_move(self.sol)
            self._export_figure(self.sol, "best_score_move")
            return

        if state.best_delta_ratio > 0.0 and not self._is_move_forbidden(state.best_ratio_move, state, use_metric_score=True):
            self.context.log(f"[local_search] applying best ratio move: {state.best_ratio_move}")
            state.best_ratio_move.apply_move(self.sol)
            self._export_figure(self.sol, "best_ratio_move")
            return
        
        if self._search_relocate(state):
            self._export_figure(self.sol, "relocate")
            return
        
        if self._search_twoOpt(state):
            self._export_figure(self.sol, "2-opt")
            return
        
        if state.best_delta_dist < 0.0 and not self._is_move_forbidden(state.best_dist_move, state, use_metric_score=False):
            self.context.log(f"[local_search] applying best_dist_move move: {state.best_dist_move}")
            state.best_dist_move.apply_move(self.sol)
            self._export_figure(self.sol, "best_dist_move")
            return
        
        if self._trigger_intensification_criteria(itr, last_solution_change_itr) and self._intensification_search():
            self.context.log(f"[local_search] intensification successfully improved sol")
            self._export_figure(self.sol, "3-opt")
            return
        
        self.context.log(f"[local_search] local optimum: {self.sol}")
        self._apply_non_improving_move(
            state.best_dist_move,
            state.best_score_move,
            state.best_ratio_move,
            itr
        )

    def _apply_non_improving_move(self, move1: Move, move2: Move, move3: Move, itr: int):
        valid_moves = [
            m for m in [move1, move2, move3]
            if m is not None and not self.tabu_list.is_tabu(m)
        ]
        if len(valid_moves) == 0:
            self.context.log("[local_search] no valid candidates for non-improving move")
            return
    
        move = random.choice(valid_moves)

        self.context.log(f"[local_search] applying non-improving move {move}")
        move.apply_move(self.sol)
        self._export_figure(self.sol, f"non_improving_{type(move).__name__}")

        self.tabu_list.add(move, itr)

    def _search_insertion(self, state: LocalSearchState) -> bool:
        for move in self.evaluator.insertion_candidates(self.sol):
            delta_ratio = move.delta_ratio()

            if self._is_move_forbidden(move, state, use_metric_score=True):
                continue

            if self.ls_first_improve and delta_ratio > 0:
                self.context.log(f"[local_search] applying insertion move (first-improve): {move}")
                move.apply_move(self.sol)
                return True
            
            if delta_ratio > state.best_delta_ratio:
                state.best_delta_ratio = delta_ratio
                state.best_ratio_move = move
        
        return False
    
    def _search_replace(self, state: LocalSearchState) -> bool:
        for move in self.evaluator.replace_candidates(self.sol):
            delta_score = move.delta_score()
            delta_dist = move.delta_distance()
            delta_ratio = move.delta_ratio()

            #case 1: the replace move does not increase the score
            # occurs when the two swapped vertices have the same score
            # then, only the delta distance is verified
            if delta_score == 0.0:
                if self._is_move_forbidden(move, state, use_metric_score=False):
                    continue

                if self.ls_first_improve and delta_dist < 0.0:
                    self.context.log(f"[local_search] applying replace move (first-improve): {move}")
                    move.apply_move(self.sol)
                    return True

                if delta_dist < state.best_delta_dist:
                    state.best_delta_dist = delta_dist
                    state.best_dist_move = move

            #case 2: when both the score and the distance are improved 
            elif delta_dist < 0.0:
                if self._is_move_forbidden(move, state, use_metric_score=True):
                    continue

                if self.ls_first_improve:
                    self.context.log(f"[local_search] applying replace move (first-improve): {move}")
                    move.apply_move(self.sol)
                    return True
                
                if delta_score > state.best_delta_score:
                    state.best_delta_score = delta_score
                    state.best_score_move = move

            #Case 3: when the score is improved, but the distance does not improve
            else: # delta_score > 0.0, delta_dist >= 0.0
                if self._is_move_forbidden(move, state, use_metric_score=True):
                    continue
                                    
                if self.ls_first_improve and delta_ratio > 0.0:
                    self.context.log(f"[local_search] applying replace move (first-improve): {move}")
                    move.apply_move(self.sol)
                    return True
                
                if delta_ratio > state.best_delta_ratio:
                    state.best_delta_ratio = delta_ratio
                    state.best_ratio_move = move
        
        return False
    
    def _trigger_diversification_criteria(self, cur_itr: int, last_solution_change_itr: int):
        if not self.enable_diversification:
            return False
        
        threshold = 50
        return cur_itr - last_solution_change_itr > threshold

    def _diversify(self):
        self.context.log(f"[local_search] diversifying the best sol: {self.best_sol}")

        new_solution = Solution.copy(self.best_sol)
        self.sol = self.evaluator.diversify_vertices(new_solution)

        self.context.log(f"[local_search] sol after diversification: {self.sol}")

        self.tabu_list.clear()

    def _trigger_intensification_criteria(self, cur_itr: int, last_solution_change_itr: int):
        if not self.enable_intensification or cur_itr < 5:
            return False
        
        if cur_itr - last_solution_change_itr == 1:
            return True
                
        if cur_itr % self.op.n in (0, 1):
            return True
        
        return False
    
    def _search_intensified_replace(self, state: LocalSearchState) -> bool:
        for move in self.evaluator.intensified_replace_candidates(self.sol):
            delta_score = move.delta_score()
            delta_dist = move.delta_distance()
            delta_ratio = move.delta_ratio()

            #case 1: the replace move does not increase the score
            # occurs when the two swapped vertices have the same score
            # then, only the delta distance is verified
            if delta_score == 0.0:
                if self.ls_first_improve and delta_dist < 0.0:
                    self.context.log(f"[local_search] intensification: applying replace move (first-improve): {move}")
                    move.apply_move(self.sol)
                    return True

                if delta_dist < state.best_delta_dist:
                    state.best_delta_dist = delta_dist
                    state.best_dist_move = move

            #case 2: when both the score and the distance are improved 
            elif delta_dist < 0.0:
                if self.ls_first_improve:
                    self.context.log(f"[local_search] intensification: applying replace move (first-improve): {move}")
                    move.apply_move(self.sol)
                    return True
                
                if delta_score > state.best_delta_score:
                    state.best_delta_score = delta_score
                    state.best_score_move = move

            #Case 3: when the score is improved, but the distance does not improve
            else: # delta_score > 0.0, delta_dist >= 0.0  
                if self.ls_first_improve and delta_ratio > 0.0:
                    self.context.log(f"[local_search] intensification: applying replace move (first-improve): {move}")
                    move.apply_move(self.sol)
                    return True
                
                if delta_ratio > state.best_delta_ratio:
                    state.best_delta_ratio = delta_ratio
                    state.best_ratio_move = move
        
        return False
    
    def _search_threeOpt(self, state: LocalSearchState) -> bool:
        for move in self.evaluator.threeOpt_candidates(self.sol):
            delta_dist = move.delta_distance()

            if self.ls_first_improve and delta_dist < 0.0:
                self.context.log(f"[local_search] intensification: applying 3-opt move (first-improve): {move}")
                move.apply_move(self.sol)
                return True

            if delta_dist < state.best_delta_dist:
                state.best_delta_dist = delta_dist
                state.best_dist_move = move

        return False
    
    def _search_relocate(self, state: LocalSearchState) -> bool:
        for move in self.evaluator.relocate_candidates(self.sol):
            delta_dist = move.delta_distance()

            if self._is_move_forbidden(move, state, use_metric_score=False):
                continue

            if self.ls_first_improve and delta_dist < 0.0:
                self.context.log(f"[local_search] applying relocate move (first-improve): {move}")
                move.apply_move(self.sol)
                return True

            if delta_dist < state.best_delta_dist:
                state.best_delta_dist = delta_dist
                state.best_dist_move = move
        
        return False
    
    def _search_twoOpt(self, state: LocalSearchState) -> bool:
        for move in self.evaluator.twoOpt_candidates(self.sol):
            delta_dist = move.delta_distance()

            if self._is_move_forbidden(move, state, use_metric_score=False):
                continue

            if self.ls_first_improve and delta_dist < 0.0:
                self.context.log(f"[local_search] applying 2-opt move (first-improve): {move}")
                move.apply_move(self.sol)
                return True

            if delta_dist < state.best_delta_dist:
                state.best_delta_dist = delta_dist
                state.best_dist_move = move

        return False
    
    def _intensification_search(self) -> bool:
        state = self.LocalSearchState(self.evaluator, self.sol, self.best_sol)

        self.context.log(f"[local_search] intensification...")

        if self._search_intensified_replace(state):
            self._export_figure(self.sol, "intensified_replace")
            return True
        
        if state.best_delta_score > 0.0:
            self.context.log(f"[local_search] intensification: applying best score move: {state.best_score_move}")
            state.best_score_move.apply_move(self.sol)
            self._export_figure(self.sol, "intensification_best_score_move")
            return True

        if state.best_delta_ratio > 0.0:
            self.context.log(f"[local_search] intensification: applying best ratio move: {state.best_ratio_move}")
            state.best_ratio_move.apply_move(self.sol)
            self._export_figure(self.sol, "intensification_best_ratio_move")
            return True
        
        if self._search_threeOpt(state):
            self._export_figure(self.sol, "3-opt")
            return True
        
        if state.best_delta_dist < 0.0:
            self.context.log(f"[local_search] intensification: best_dist move: {state.best_dist_move}")
            state.best_dist_move.apply_move(self.sol)
            self._export_figure(self.sol, "intensification_best_dist_move")
            return True
        
        self.context.log(f"[local_search] intensification did not improve sol")
        return False

    def _is_move_forbidden(self, move: Move, state: LocalSearchState, use_metric_score: bool) -> bool:
        """
        Returns True if the move is tabu and should be skipped,
        based on the chosen metric ('score', 'dist').
        """
        if not self.tabu_list.is_tabu(move):
            return False

        if use_metric_score:
            #aspiration criteria
            is_forbidden = state.score_cur_sol + move.delta_score() <= state.score_best_sol
            if is_forbidden:
                self.context.log(f"[local_search] move forbidden due to score metric, {move}")
            return is_forbidden
        
        #aspiration criteria
        is_forbidden = state.dist_cur_sol + move.delta_distance() >= state.dist_best_sol
        if is_forbidden:
            self.context.log(f"[local_search] move forbidden due to dist metric, {move}")

        return is_forbidden

    def _update_tabus(self, itr: int):
        self.tabu_list.update(itr)
        
    def _update_best_sol(self) -> bool:
        score_sol = self.evaluator.total_score(self.sol)
        score_best_sol = self.evaluator.total_score(self.best_sol)
        
        if score_sol > score_best_sol:
            self.best_sol = Solution.copy(self.sol)
            return True
        elif score_sol == score_best_sol:
            dist_sol = self.evaluator.total_dist(self.sol)
            dist_best_sol = self.evaluator.total_dist(self.best_sol)
            if dist_sol < dist_best_sol:
                self.best_sol = Solution.copy(self.sol)
                return True
        return False
    
    def _time_elapsed(self):
        return time.time() - self.start
    
    def _save_improve_data(self, log_prefix: str, fig_name: str, sol: Solution):
        score = self.evaluator.total_score(sol)
        dist = self.evaluator.total_dist(sol)

        self.context.log(f"{log_prefix}: score={score}, dist={dist}, {sol}", save=True)
        self.context.add_improve(sol, self._time_elapsed())
        self._export_figure(sol, fig_name, lvl=0)
        