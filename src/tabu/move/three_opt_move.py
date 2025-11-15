from ...model.solution import Solution

class ThreeOptMove:
    def __init__(self, v1: int, v2: int, v3: int, segment_swap: bool, delta_dist: float):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.segment_swap = segment_swap
        self.delta_dist = delta_dist
    
    def apply_move(self, sol: Solution) -> Solution:
        if not self.segment_swap:
            sol.threeOpt(self.v1, self.v2, self.v3)
        else:
            sol.threeOpt_with_segment_swap(self.v1, self.v2, self.v3)

        return sol
    
    def delta_ratio(self) -> float:
        return None

    def delta_score(self) -> float:
        return None
    
    def delta_distance(self) -> float:
        return self.delta_dist
    
    def tabu_add_key(self) -> list[str]:
        return [
            str(self.v1), str(self.v2), str(self.v3)
        ]
    
    def tabu_check_key(self) -> list[str]:
        return [
            str(self.v1), str(self.v2), str(self.v3)
        ]

    def __str__(self):
        return (
            f"ThreeOptMove(v1={self.v1}, "
            f"v2={self.v2}, "
            f"v3={self.v3}, "
            f"segment_swap={self.segment_swap}, "
            f"delta_dist={self.delta_dist:.2f})"
        )
