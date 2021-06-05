from itertools import chain

class DiceRoll:
    def __init__(self,num_of_dice,values) :
       self.num_of_dice = num_of_dice
       self.values = values
       self.val_string = " ,".join(str(e) for e in list(chain.from_iterable(values)))
       self.original_values = values

    def update_val_string(self):
        self.val_string = " ,".join(str(e) for e in list(chain.from_iterable(self.values))) 