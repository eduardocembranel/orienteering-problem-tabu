from ..model.op import OP
from ..model.solution import Solution
from .move.insertion_move import InsertionMove
from .move.relocate_move import RelocateMove
from .move.two_opt_move import TwoOptMove
from .move.three_opt_move import ThreeOptMove
from .move.replace_move import ReplaceMove
from .move.move import Move

from typing import Generator

import random

class Evaluator:
    def __init__(self, op: OP):
        self.op = op

    def insertion_candidates(self, sol: Solution) -> Generator[Move]:
        cur_dist = self.total_dist(sol)

        for cand in sol.get_remaining_vertices():
            for prev in sol.get_vertices():
                if prev == sol.n - 1: #disconsider the last vertex
                    continue
                delta_dist = self._evaluate_insertion_delta_dist(sol, cand, prev)
                if cur_dist + delta_dist <= self.op.t_max:
                    delta_score = self._evaluate_insertion_delta_score(cand)
                    delta_improve = self._calculate_delta_improve(delta_score, delta_dist)
                    yield InsertionMove(cand, prev, delta_score, delta_dist, delta_improve)
    
    def relocate_candidates(self, sol: Solution) -> Generator[Move]:
        cur_dist = self.total_dist(sol)

        for cand in sol.get_vertices():
            if cand == 0 or cand == sol.n - 1: #disconsider the first and end vertices
                continue
            for rel_pos in sol.get_vertices():
                if rel_pos == cand or sol.next[rel_pos] == cand or rel_pos == sol.n - 1:
                    continue
                delta_dist = self._evaluate_realocate_delta_dist(sol, cand, rel_pos)
                if cur_dist + delta_dist <= self.op.t_max:
                    yield RelocateMove(cand, rel_pos, delta_dist)
    
    def twoOpt_candidates(self, sol: Solution) -> Generator[Move]:
        cur_dist = self.total_dist(sol)
        vertices = sol.get_vertices()

        for i in range(len(vertices)):
            v1 = vertices[i]
            for j in range(i + 2, len(vertices) - 1):
                v2 = vertices[j]
                delta_dist = self._evaluate_twoOpt_delta_dist(sol, v1, v2)
                if cur_dist + delta_dist <= self.op.t_max:
                    yield TwoOptMove(v1, v2, delta_dist)
    
    def threeOpt_candidates(self, sol: Solution) -> Generator[Move]:
        cur_dist = self.total_dist(sol)
        vertices = sol.get_vertices()

        for i in range(len(vertices)):
            v1 = vertices[i]
            for j in range(i + 2, len(vertices)):
                v2 = vertices[j]
                for k in range(j + 2, len(vertices) - 1):
                    v3 = vertices[k]
                    
                    delta_dist = self._evaluate_threeOpt_delta_dist(sol, v1, v2, v3)
                    if cur_dist + delta_dist <= self.op.t_max:
                        yield ThreeOptMove(v1, v2, v3, segment_swap=False, delta_dist=delta_dist)
                    
                    delta_dist_case_2 = self._evaluate_threeOpt_with_segment_swap_delta_dist(sol, v1, v2, v3)
                    if cur_dist + delta_dist_case_2 <= self.op.t_max:
                        yield ThreeOptMove(v1, v2, v3, segment_swap=True, delta_dist=delta_dist_case_2)
        
    def replace_candidates(self, sol: Solution) -> Generator[Move]:
        cur_dist = self.total_dist(sol)
        vertices = sol.get_vertices()
        remaining_vertices = sol.get_remaining_vertices()

        for i in range(1, len(vertices) - 1):
            out_cand = vertices[i]
            for in_cand in remaining_vertices:
                delta_score = self._evaluate_replace_delta_score(in_cand, out_cand)
                if delta_score >= 0.0:
                    delta_dist = self._evaluate_replace_delta_dist(sol, in_cand, out_cand)
                    if cur_dist + delta_dist <= self.op.t_max:
                        delta_improve = self._calculate_delta_improve(delta_score, delta_dist)
                        insert_pos = sol.prev[out_cand]
                        yield ReplaceMove(in_cand, insert_pos, out_cand, delta_score, delta_dist, delta_improve)


    def intensified_replace_candidates(self, sol: Solution):
        cur_dist = self.total_dist(sol)
        vertices = sol.get_vertices()
        remaining_vertices = sol.get_remaining_vertices()

        for i in range(1, len(vertices) - 1):
            out_cand = vertices[i]
            for in_cand in remaining_vertices:
                delta_score = self._evaluate_replace_delta_score(in_cand, out_cand)
                if delta_score >= 0.0:
                    for insert_pos in vertices:
                        # cannot insert after the end vertex, neither after the out_cand because
                        # out_cand will no long be in the path
                        if insert_pos == sol.n - 1 or insert_pos == out_cand:
                            continue

                        delta_dist = self._evaluate_intensified_replace_delta_dist(sol, in_cand, out_cand, insert_pos)
                        if cur_dist + delta_dist <= self.op.t_max:
                            delta_improve = self._calculate_delta_improve(delta_score, delta_dist)
                            yield ReplaceMove(in_cand, insert_pos, out_cand, delta_score, delta_dist, delta_improve)

    def diversify_vertices(self, sol: Solution) -> Solution:
        vertices = sol.get_vertices()
        remaining_vertices = sol.get_remaining_vertices()

        if (len(vertices) <= 3 or len(remaining_vertices) == 0):
            return sol
                
        k_max = len(vertices)
        removal_counts = list(range(2, k_max - 1))

        in_v = random.choice(remaining_vertices)

        for k in removal_counts:
            new_sol = Solution.copy(sol)
            
            #remove k vertices
            out_v = random.sample(vertices[1:-1], k)

            for v in out_v:
                new_sol.remove_vertex(v)

            vertices_after_removal = new_sol.get_vertices()

            possible_insert_pos = vertices_after_removal[:-1]
            random.shuffle(possible_insert_pos)

            for insert_pos in possible_insert_pos:
                tmp_sol = Solution.copy(new_sol)

                tmp_sol.add_vertex_after(in_v, insert_pos)

                if self.is_feasible(tmp_sol):
                    return tmp_sol
        
        return sol

    def _evaluate_replace_delta_dist(self, sol: Solution, in_cand: int, out_cand: int) -> float:
        prev_out = sol.prev[out_cand]
        next_out = sol.next[out_cand]

        dist_removed_1 = self.op.A[prev_out][out_cand]
        dist_removed_2 = self.op.A[out_cand][next_out]

        dist_added_1 = self.op.A[prev_out][in_cand]
        dist_added_2 = self.op.A[in_cand][next_out]

        return dist_added_1 + dist_added_2 - dist_removed_1 - dist_removed_2

    def _evaluate_intensified_replace_delta_dist(self, sol: Solution, in_cand: int, out_cand: int, insert_pos: int) -> float:
        # for the out vertex
        prev_out = sol.prev[out_cand]
        next_out = sol.next[out_cand]
        
        dist_removed_1 = self.op.A[prev_out][out_cand]
        dist_removed_2 = self.op.A[out_cand][next_out]
        dist_added_1 = self.op.A[prev_out][next_out]

        #for the in vertex
        next_insert = sol.next[insert_pos]

        dist_removed_3 = self.op.A[insert_pos][next_insert]
        dist_added_2 = self.op.A[insert_pos][in_cand]
        dist_added_3 = self.op.A[in_cand][next_insert]
       
        return dist_added_1 + dist_added_2 + dist_added_3 - dist_removed_1 - dist_removed_2 - dist_removed_3

    def _evaluate_insertion_delta_dist(self, sol: Solution, cand: int, insert_pos: int) -> float:
        next = sol.next[insert_pos]

        dist_removed = self.op.A[insert_pos][next]
        dist_added_1 = self.op.A[insert_pos][cand]
        dist_added_2 = self.op.A[cand][next]
        
        return dist_added_1 + dist_added_2 - dist_removed
    
    def _evaluate_insertion_delta_score(self, cand: int) -> int:
        return self.op.V[cand].score
    
    def _evaluate_replace_delta_score(self, cand_in: int, cand_out: int) -> int:
        return self.op.V[cand_in].score - self.op.V[cand_out].score

    def _calculate_delta_improve(self, delta_score: int, delta_dist: float) -> float:
        if delta_dist == 0.0:
            big_const = 10000.0 #non-infinite big constant
            return delta_score * big_const
        return (delta_score)/(delta_dist)
        #return (-delta_dist)
        #return delta_score
        #return delta_score + 1.5*(-delta_dist)
                
    def _evaluate_realocate_delta_dist(self, sol: Solution, cand: int, rel_pos: int) -> float:
        prev_of_cand = sol.prev[cand]
        next_of_cand = sol.next[cand]
        next_of_rel_pos = sol.next[rel_pos]

        dist_added_1 = self.op.A[prev_of_cand][next_of_cand]
        dist_added_2 = self.op.A[rel_pos][cand]
        dist_added_3 = self.op.A[cand][next_of_rel_pos]

        dist_removed_1 = self.op.A[prev_of_cand][cand]
        dist_removed_2 = self.op.A[cand][next_of_cand]
        dist_removed_3 = self.op.A[rel_pos][next_of_rel_pos]

        return dist_added_1 + dist_added_2 + dist_added_3 - dist_removed_1 - dist_removed_2 - dist_removed_3
        
    def _evaluate_twoOpt_delta_dist(self, sol: Solution, v1: int, v2: int) -> float:
        next_v1 = sol.next[v1]
        next_v2 = sol.next[v2]

        dist_removed_1 = self.op.A[v1][next_v1]
        dist_removed_2 = self.op.A[v2][next_v2]

        dist_added_1 = self.op.A[v1][v2]
        dist_added_2 = self.op.A[next_v1][next_v2]

        return dist_added_1 + dist_added_2 - dist_removed_1 - dist_removed_2

    def _evaluate_threeOpt_delta_dist(self, sol: Solution, v1: int, v2: int, v3: int) -> float:
        """
        S_1 S_2(reverted) S_3(reverted) S_4
        """
        next_v1 = sol.next[v1]
        next_v2 = sol.next[v2]
        next_v3 = sol.next[v3]

        dist_removed_1 = self.op.A[v1][next_v1]
        dist_removed_2 = self.op.A[v2][next_v2]
        dist_removed_3 = self.op.A[v3][next_v3]

        dist_added_1 = self.op.A[v1][v2]
        dist_added_2 = self.op.A[next_v1][v3]
        dist_added_3 = self.op.A[next_v2][next_v3]

        return dist_added_1 + dist_added_2 + dist_added_3 - dist_removed_1 - dist_removed_2 - dist_removed_3

    def _evaluate_threeOpt_with_segment_swap_delta_dist(self, sol: Solution, v1: int, v2: int, v3: int) -> float:
        """
        S_1 S_3(reverted) S_2(reverted) S_4
        """
        next_v1 = sol.next[v1]
        next_v3 = sol.next[v3]

        dist_removed_1 = self.op.A[v1][next_v1]
        dist_removed_2 = self.op.A[v3][next_v3]

        dist_added_1 = self.op.A[v1][v3]
        dist_added_2 = self.op.A[next_v1][next_v3]

        return dist_added_1 + dist_added_2 - dist_removed_1 - dist_removed_2

    def total_dist(self, sol: Solution) -> float:
        total_dist = 0.0
        for u, v in enumerate(sol.next):
            if v is not None:
                total_dist += self.op.A[u][v]
        return total_dist

    def total_score(self, sol: Solution) -> float:
        total_score = 0
        for v in sol.get_vertices():
            total_score += self.op.V[v].score
        return total_score
    
    def is_feasible(self, sol: Solution) -> bool:
        return self.total_dist(sol) <= self.op.t_max