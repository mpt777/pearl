import cv2
from enum import Enum
import numpy as np

from states import *
from ws import WS

BOX_SIZE = 20
TOLERANCE = 30




class Pearl:
    def __init__(self, rgb, tolerance):
        self.rgb = rgb          # [R, G, B]
        self.tolerance = tolerance


class PearlFrame:
    def __init__(self, frame, box_color=(255, 255, 255)):
        self.frame = frame
        self.bounds = []
        self.color = []
        self.box_color = box_color

    def build_bounds(self):
        h, w, _ = self.frame.shape

        # Define a small sampling box in the center
        box_size = BOX_SIZE
        cx, cy = w // 2, h // 2

        x1 = cx - box_size
        x2 = cx + box_size
        y1 = cy - box_size
        y2 = cy + box_size

        self.bounds = [x1, x2, y1, y2]

    def draw_square(self):
        x1, x2, y1, y2 = self.bounds
        # Draw box on screen
        b = self.box_color
        cv2.rectangle(self.frame, (x1, y1), (x2, y2), (b[2], b[1], b[0]), 2)
        cv2.imshow("Webcam", self.frame)

    def sample_rgb(self):
        x1, x2, y1, y2 = self.bounds
        roi = self.frame[y1:y2, x1:x2]

        # Average BGR values
        avg_bgr = roi.mean(axis=0).mean(axis=0)
        b, g, r = avg_bgr
        self.color = [int(r), int(g), int(b)]
        # print("Sampled RGB:", self.color)

    def process(self):
        self.build_bounds()
        self.sample_rgb()
        # self.draw_square()
        


class PearlSorter:

    def __init__(self):
        self.cap = None
        self.state = None

        # Pre-instantiate states to preserve per-state data
        self.state_instances = {
            SortState.INIT: SortStateINIT(self),
            SortState.IDLE: SortStateIDLE(self),
            SortState.SAMPLING: SortStateSAMPLING(self),
            SortState.DUMPING: SortStateDUMP(self)
        }


        self.change_state(SortState.INIT)
        self.reference_color = []
        self.box_color = (255, 255, 255)
        self.tolerance = TOLERANCE
        self.key = None
        self.matched = 0



    def constructor(self):
        self.ws = WS()
        self.cap = cv2.VideoCapture(1)

        if not self.cap.isOpened():
            print("Could not open webcam")
            exit()

    def colors_match(self, c1, c2):
        """ Check if two RGB colors are within a tolerance """
        c1 = np.array(c1)
        c2 = np.array(c2)
        diff = np.abs(c1 - c2)
        return np.all(diff <= self.tolerance)

    def process(self):
        while True:
            self.key = None

            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            state = self.state_instances[self.state]
            self.key = cv2.waitKey(1) & 0xFF
            
            frame = PearlFrame(frame, box_color=self.box_color)
            frame.process()

            state.process(frame)

            self.box_color = state.get_color()
            frame.box_color = self.box_color
            frame.draw_square()

            
            # Press 'q' to quit
            if self.key == ord('q'):
                break
            
            if self.key == ord('r'):
                self.change_state(SortState.INIT)
                print("RESET COLOR------------------------------------------")

        self.cap.release()
        cv2.destroyAllWindows()

    def change_state(self, new_state):
        if new_state == self.state:
            return
      
        if self.state:
            # Exit current state
            self.state_instances[self.state].exit()

        # Enter new state
        self.state = new_state
        self.state_instances[self.state].enter()



######################################################################

def main():
    print("Welcome to the Pearl Sorter!")
    sorter = PearlSorter()
    sorter.constructor()
    sorter.process()
    print("Program finished.")

if __name__ == "__main__":
    main()
