from ...model.solution import Solution

class RelocateMove:
    def __init__(self, cand: int, rel_pos: int, delta_dist: float):
        self.cand = cand
        self.rel_pos = rel_pos
        self.delta_dist = delta_dist
    
    def apply_move(self, sol: Solution) -> Solution:
        sol.relocate_vertex(self.cand, self.rel_pos)
        return sol
    
    def delta_ratio(self) -> float:
        return None

    def delta_score(self) -> float:
        return None
    
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
        return (f"RelocateMove(cand={self.cand}, "
                f"rel_pos={self.rel_pos}, "
                f"delta_dist={self.delta_dist:.2f})")