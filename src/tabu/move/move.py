from abc import ABC, abstractmethod
from ...model.solution import Solution

class Move(ABC):
    """
    Abstract base class representing a move applied to a solution.
    """

    @abstractmethod
    def apply_move(self, sol: Solution) -> Solution:
        """
        Apply the move to a solution and return the resulting new solution.
        
        Parameters
        ----------
        sol : Solution
            The current solution to which the move will be applied.
        
        Returns
        -------
        Solution
            A new solution after applying the move.
        """
        pass

    @abstractmethod
    def delta_ratio(self) -> float:
        """
        Returns the variation (delta) in the solution's quality if this move is applied.

        The improvement is a scalar value that quantifies how much the move 
        increases or decreases the overall objective function being optimized 
        (e.g., profit-distance ratio, or another composite measure).

        A positive value indicates that the move improves the current solution, 
        while a negative value indicates a worsening.
        
        Returns:
            float: The change in the solution’s improvement metric.
        """
        pass

    @abstractmethod
    def delta_score(self) -> float:
        """

        """
        pass
    
    @abstractmethod
    def delta_distance(self) -> float:
        """
        Returns the variation (delta) in total distance caused by this move.

        This value represents how much the total path length (or travel cost) 
        will increase or decrease if the move is applied.

        A positive value indicates an increase in distance, 
        while a negative value indicates a reduction.

        Returns:
            float: The change in total distance.
        """
        pass

    @abstractmethod
    def tabu_add_key(self) -> list[str]:
        """
        Returns the key (or signature) that should be added to the tabu list
        after this move is applied.

        Typically represents the reverse or forbidden move that prevents
        cycling back to a previous solution state.
        """
        pass

    @abstractmethod
    def tabu_check_key(self) -> list[str]:
        """
        Returns the key used to check if this move is currently tabu.
        """
        pass

    @abstractmethod
    def __str__(self) -> str:
        """
        Return a string representation of the move.
        """
        pass
