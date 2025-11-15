import math

class Vertex:
    def __init__(self, score: int, x: float, y: float):
        self.score = score
        self.x = x
        self.y = y

class OP:
    def __init__(self, n: int, V: list[Vertex], A: list[list[float]], t_max: float, instance: str):
        self.n = n 
        self.V = V
        self.A = A
        self.t_max = t_max
        self.instance = instance

    @classmethod
    def from_file(cls, instance: str):
        filepath = f'instances/{instance}.txt'

        with open(filepath, 'r') as file:
            lines = file.readlines()

        t_max, _ = map(int, lines[0].split())
        V = [
            Vertex(int(score), float(x), float(y)) for x, y, score in (line.split() for line in lines[1:])
        ]

        # swap the second vertex with the last vertex
        # then, the inicial and end vertex will be v[0] and v[n-1] respectivelly
        V[1], V[len(V) - 1] = V[len(V) - 1], V[1]

        A = [
            [OP._euclidean_dist(V[i], V[j]) for j in range(len(V))] for i in range(len(V))
        ]
        
        return OP(len(V), V, A, t_max, instance)
    
    @staticmethod
    def _euclidean_dist(v1: Vertex, v2: Vertex) -> float:
        """
        Calculate the euclidean distance between two vertices (v1 e v2).
        """
        return math.sqrt((v1.x - v2.x)**2 + (v1.y - v2.y)**2)
