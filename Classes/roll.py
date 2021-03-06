from itertools import chain
from dataclasses import dataclass

class DiceRoll:
    def __init__(self,num_of_dice,values) :
       self.num_of_dice = num_of_dice
       self.values = values
       self.val_string = " ,".join(str(e) for e in list(chain.from_iterable(values)))
       self.original_values = self.list_copy(values)

    def update_val_string(self):
        self.val_string = " ,".join(str(e) for e in list(chain.from_iterable(self.values)))

    def list_copy(self,l):
        return l[:]
@dataclass
class Roll:
    number : int = 1
    sides :int = 6
    mod : int = 0
    neg : bool = False