import numpy as np

class Slide():

    def __init__(self, controllerStateGenerator):
        """Create a new Slide instance with a given state generator"""
        self.controllerStateGenerator = controllerStateGenerator
        self.position = np.zeros(3)
        self.calibrating = False
        self.start_position = np.zeros(3)
        self.stop_position = np.zeros(3)

    def update(self):
        """Update the slide position using the state generator"""
        state = next(self.controllerStateGenerator)
        
        #position
        if 'position' in state:
            self.position = state['position']

        #handle calibration button
        #TODO add haptics?
        if 'calibrate' in state:
            calibration_button = state['calibrate']
            if calibration_button and not self.calibrating:
                #start calibration
                self.calibrating = True
                self.start_position = self.position
            elif not calibration_button and self.calibrating:
                #end calibration
                self.calibrating = False
                self.stop_position = self.position
                print('calibration: ', self.start_position, self.stop_position)

    def getSlideValue(self):
        """Return the position of the slide as a value between 0 and 1"""
        #translate so start_position is at the origin
        stop_position = self.stop_position - self.start_position
        off_slide_position = self.position - self.start_position

        #normalize
        slide_length = np.linalg.norm(stop_position)
        stop_position /= slide_length #unit length
        off_slide_position /= slide_length #length <= 1

        return np.dot(off_slide_position, stop_position)
    
    def getPositionAndOffset(self):
        """Return the position of the slide (1-7) and the offset"""

        value = self.getSlideValue()
        raise NotImplementedError("not implemented")
        


if __name__ == '__main__':
    from etrombone.inputs.vr.controller import getControllerState
    from time import sleep
    generator = getControllerState()
    slide = Slide(generator)
    while True:
        slide.update()
        sleep(0.1)
        print(slide.getSlideValue())