from enum import Enum

import cv2


class SortState(Enum):
    INIT = 1      # Waiting for color lock-in
    IDLE = 2   # Using locked reference color
    SAMPLING = 3
    DUMPING = 4


class ISortState:
    def __init__(self, sorter):
        self.sorter = sorter

    def enter(self):
        pass

    def exit(self):
        pass

    def process(self, f):
        pass

    def get_color(self):
        return [218,112,214]
    
class SortStateIDLE(ISortState):

    def process(self, f):
        pass

    def get_color(self):
        return [32, 3, 252]


class SortStateINIT(ISortState):

    def process(self, f):

      if self.sorter.key in [13, 10]:   # ENTER key
            self.sorter.reference_color = f.color
            print("Stored reference color:", self.sorter.reference_color)
            self.sorter.change_state(SortState.SAMPLING)

    def get_color(self):
        return [218,112,214]


class SortStateDUMP(ISortState):

    def process(self, f):
        pass

    def get_color(self):
        return [218,112,214]
    
    
class SortStateSAMPLING(ISortState):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.matched = False

    def process(self, f):

        if self.sorter.colors_match(f.color, self.sorter.reference_color):
            print("MATCH  →", f.color)
            self.matched = True
        else:
            print("NO MATCH →", f.color)
            self.matched = False

    def get_color(self):
        if self.matched:
            return [3, 252, 94]
        return [252, 65, 3]
        