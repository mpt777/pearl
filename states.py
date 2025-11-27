from enum import Enum

import cv2

RESET_COLOR = (255,255,255)

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

    def enter(self):
        pass
        # Turn Motor On 

    def process(self, f):
        if not self.sorter.colors_match(f.color, RESET_COLOR):
            self.sorter.change_state(SortState.SAMPLING)

    def get_color(self):
        return [32, 3, 252]


class SortStateINIT(ISortState):

    def process(self, f):

        if self.sorter.key in [13, 10]:   # ENTER key
            self.sorter.reference_color = f.color
            print("Stored reference color:", self.sorter.reference_color)
            self.sorter.change_state(SortState.IDLE)

    def get_color(self):
        return [218,112,214]


class SortStateDUMP(ISortState):

    def exit(self):
        self.sorter.matched = 0

    def process(self, f):
        pass

    def get_color(self):
        return [218,112,214]
    
    
class SortStateSAMPLING(ISortState):

    def enter(self):
        pass
        # Turn Motor OFF 

    def process(self, f):
        if self.sorter.colors_match(f.color, RESET_COLOR):
            self.sorter.change_state(SortState.IDLE)

        if self.sorter.colors_match(f.color, self.sorter.reference_color):
            print("MATCH  →", f.color)
            self.sorter.matched = 1
        else:
            print("NO MATCH →", f.color)
            self.sorter.matched = -1

    def get_color(self):
        if self.sorter.matched == 1:
            return [3, 252, 94]
        if self.sorter.matched == -1:
            return [252, 65, 3]
        return (255, 255, 255)
        