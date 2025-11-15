from ...model.solution import Solution
from .move import Move

class InsertionMove(Move):
    def __init__(self, cand: int, insert_pos: int, _delta_score: int, delta_dist: float, _delta_ratio: float):
        self.cand = cand
        self.insert_pos = insert_pos
        self._delta_score = _delta_score
        self.delta_dist = delta_dist 
        self._delta_ratio = _delta_ratio
    
    def apply_move(self, sol: Solution) -> Solution:
        sol.add_vertex_after(self.cand, self.insert_pos)
        return sol
    
    def delta_ratio(self) -> float:
        return self._delta_ratio
    
    def delta_score(self) -> float:
        return self._delta_score

    def delta_distance(self) -> float:
        return self.delta_dist
    
    def tabu_add_key(self) -> list[str]:
        return [
            str(self.cand)
        ]
    
    def tabu_check_key(self) -> list[str]:
        return [
            str(self.cand)
        ]

    def __str__(self):
            return (f"InsertionMove(cand={self.cand}, "
                    f"insert_pos={self.insert_pos}, "
                    f"delta_score={self._delta_score}, "
                    f"delta_dist={self.delta_dist:.2f}, "
                    f"delta_ratio={self._delta_ratio:.2f})")
