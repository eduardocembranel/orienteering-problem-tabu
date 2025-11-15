from ...model.solution import Solution
from .move import Move

class ReplaceMove(Move):
    def __init__(self, in_cand: int, insert_pos: int, out_cand: int, _delta_score: int, delta_dist: float, _delta_ratio: float):
        self.in_cand = in_cand
        self.insert_pos = insert_pos
        self.out_cand = out_cand
        self._delta_score = _delta_score
        self.delta_dist = delta_dist
        self._delta_ratio = _delta_ratio 
    
    def apply_move(self, sol: Solution) -> Solution:
        sol.add_and_remove_vertex(self.in_cand, self.insert_pos, self.out_cand)
        return sol
    
    def delta_ratio(self) -> float:
        return self._delta_ratio

    def delta_score(self) -> float:
        return self._delta_score

    def delta_distance(self) -> float:
        return self.delta_dist
    
    def tabu_add_key(self) -> list[str]:
        return [
            str(self.out_cand), str(self.in_cand)
        ]
    
    def tabu_check_key(self) -> list[str]:
        return [
            str(self.out_cand), str(self.in_cand)
        ]

    def __str__(self):
            return (f"ReplaceMove(in_cand={self.in_cand}, "
                    f"insert_pos={self.insert_pos}, "
                    f"out_cand={self.out_cand}, "
                    f"delta_score={self._delta_score:.2f}, "
                    f"delta_dist={self.delta_dist:.2f}, "
                    f"delta_ratio={self._delta_ratio:.2f})")
