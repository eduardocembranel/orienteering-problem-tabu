from .move.move import Move

class TabuList:
    def __init__(self, tabu_tenure):
        self.tabu_tenure = tabu_tenure
        self.tabu_dict = {}
    
    def add(self, move: Move, curr_itr):
        items = move.tabu_add_key()
        for item in items:
            self.tabu_dict[item] = curr_itr + self.tabu_tenure
    
    def is_tabu(self, move: Move):
        items = move.tabu_check_key()
        for item in items:
            if item in self.tabu_dict:
                return True
        return False
    
    def update(self, curr_itr):
        expired = [item for item, expiry in self.tabu_dict.items() if curr_itr > expiry]
        for item in expired:
            del self.tabu_dict[item]

    def clear(self):
        self.tabu_dict = {}
    
    def __str__(self):
        return f"TabuList items: {self.tabu_dict}"
