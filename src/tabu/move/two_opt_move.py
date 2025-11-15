from ...model.solution import Solution

class TwoOptMove:
    def __init__(self, v1: int, v2: int, delta_dist: float):
        self.v1 = v1
        self.v2 = v2
        self.delta_dist = delta_dist
    
    def apply_move(self, sol: Solution) -> Solution:
        sol.twoOpt(self.v1, self.v2)
        return sol
    
    def delta_ratio(self) -> float:
        return None
    
    def delta_score(self) -> float:
        return None

    def delta_distance(self) -> float:
        return self.delta_dist
    
    def tabu_add_key(self) -> list[str]:
        return [
            str(self.v1), str(self.v2)
        ]
    
    def tabu_check_key(self) -> list[str]:
        return [
            str(self.v1), str(self.v2)
        ]

    def __str__(self):
        return (
            f"TwoOptMove(v1={self.v1}, "
            f"v2={self.v2}, "
            f"delta_dist={self.delta_dist:.2f})"
        )
