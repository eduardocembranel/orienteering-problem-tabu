from typing import Any, Tuple
import gurobipy as gp

class Solution:
    def __init__(self, n: int):
        self.n = n
        self.prev: list[int | None] = [None] * n #list for the previous vertex
        self.next: list[int | None] = [None] * n #list for the next vertex

    @classmethod
    def create_trivial_path(cls, n: int) -> "Solution":
        """
        create the initial path v_1 -> v_n
        """
        sol = cls(n)
        sol.next[0] = n - 1
        sol.prev[n - 1] = 0
        return sol

    @classmethod
    def copy(cls, other_sol: "Solution") -> "Solution":
        new_sol = cls(other_sol.n)
        new_sol.next = other_sol.next[:]
        new_sol.prev = other_sol.prev[:]
        return new_sol
    
    @classmethod
    def from_gurobi(cls, n: int, x: gp.tupledict[Tuple[Any, ...], gp.Var]) -> "Solution":
        sol = cls(n)
        for i in range(n):
            for j in range(n):
                if x[i,j].X == 1.0:
                    sol.next[i] = j
                    sol.prev[j] = i
        return sol
    
    @classmethod
    def from_arcs(cls, n: int, arcs: list[tuple[int,int]]) -> "Solution":
        sol = cls(n)
        print("here, ", sol.next)
        for i, j in arcs:
            sol.next[i] = j
            sol.prev[j] = i
        for i in range(len(sol.next)):
            if sol.next[i] == 0:
                sol.next[i] = None
        for i in range(len(sol.prev)):
            if sol.prev[i] == 0:
                sol.prev[i] = None
        return sol
    
    def get_vertices(self) -> list[int]:
        res = []
        cur = 0

        while cur is not None:
            res.append(cur)
            cur = self.next[cur]
        
        return res
    
    def get_remaining_vertices(self) -> list[int]:
        total_vertices = set(range(len(self.next)))
        sol_vertices = set(self.get_vertices())
        return list(total_vertices - sol_vertices)
    
    def are_all_vertices_in_path(self) -> bool:
        return len(self.get_vertices()) == self.n
    
    def add_vertex_after(self, x: int, v1: int):
        """
        Add vertex x after the vertices v1
        """
        v2 = self.next[v1]

        self.next[v1] = x
        self.prev[x] = v1

        self.prev[v2] = x
        self.next[x] = v2

    def remove_vertex(self, v: int):
        prev = self.prev[v]
        next = self.next[v]

        self.next[prev] = next
        self.prev[next] = prev

        self.prev[v] = None
        self.next[v] = None

    def add_and_remove_vertex(self, in_v: int, insert_pos: int, out_v: int):
        self.remove_vertex(out_v)
        self.add_vertex_after(in_v, insert_pos)

    def relocate_vertex(self, x: int, rel_pos: int):
        prev_of_x = self.prev[x]
        next_of_x = self.next[x]
        next_of_rel_pos = self.next[rel_pos]

        self.next[prev_of_x] = next_of_x
        self.prev[next_of_x] = prev_of_x

        self.next[rel_pos] = x
        self.prev[next_of_rel_pos] = x

        self.next[x] = next_of_rel_pos
        self.prev[x] = rel_pos

    def twoOpt(self, v1: int, v2: int):
        """
        Apply a 2-opt move in place.
        It removes edges (v1, next[v1]) and (v2, next[v2]),
        then reconnects by reversing the segment between next[v1] and v2.

        Assumes that v1 and v2 are non adjacents and that v2 is not the last vertex
        """
        self._reverse_internal_segment(self.next[v1], v2)

    def threeOpt(self, v1: int, v2: int, v3: int):
        next_v2 = self.next[v2]
        self._reverse_internal_segment(self.next[v1], v2)
        self._reverse_internal_segment(next_v2, v3)

    def threeOpt_with_segment_swap(self, v1: int, v2: int, v3: int):
        next_v1 = self.next[v1]
        next_v2 = self.next[v2]

        self.threeOpt(v1, v2, v3)

        self._swap_adjacent_segments(
            v2, next_v1, v3, next_v2
        )

    def _reverse_internal_segment(self, start: int, end: int):
        """
        Reverse the internal segment of the path between 'start' and 'end' (inclusive).
        Assumes that 'start' is not the first vertex and 'end' is not the last vertex.
        """
        assert self.prev[start] is not None, "start cannot be the first vertex"
        assert self.next[end] is not None, "end cannot be the last vertex"

        before_start = self.prev[start]
        after_end = self.next[end]

        prev = after_end
        cur = start

        # inverte enquanto não passou do 'end'
        while cur != after_end:
            nxt = self.next[cur]
            self.next[cur] = prev
            self.prev[prev] = cur
            prev = cur
            cur = nxt

        # conserta as bordas
        self.next[before_start] = end
        self.prev[end] = before_start

        self.next[start] = after_end
        self.prev[after_end] = start

    def _swap_adjacent_segments(self, v1: int, v2: int, v3: int, v4: int):
        """
        Swap the position of two adjacent segments S1 S2:
        S1 = [v1 ... v2], S2 = [v3 ... v4] 
        """
        prev_v1 = self.prev[v1]
        next_v4 = self.next[v4]

        if prev_v1 is not None:
            self.next[prev_v1] = v3
        self.prev[v3] = prev_v1

        # Conectar o fim de S2 ao início de S1
        self.next[v4] = v1
        self.prev[v1] = v4

        # Conectar o fim de S1 ao sucessor original de S2
        self.next[v2] = next_v4
        if next_v4 is not None:
            self.prev[next_v4] = v2


    def get_vertices_reverse(self) -> list[int]:
        """
        Percorre o grafo de trás para frente a partir do vértice 'start' e retorna a lista de vértices.
        """
        start = self.n - 1
        res = []
        cur = start

        # Percorrer até chegar a um vértice sem antecessor (None)
        while cur is not None:
            res.append(cur)
            cur = self.prev[cur]  # Ir para o vértice anterior
        
        # A lista estará em ordem inversa, então podemos retornar invertendo
        return res[::-1]  # Inverter para a ordem original

    def __str__(self) -> str:
        next_repr = ', '.join([str(x) if x is not None else 'None' for x in self.next])
        return f"Solution(n={self.n}, next=[{next_repr}])"