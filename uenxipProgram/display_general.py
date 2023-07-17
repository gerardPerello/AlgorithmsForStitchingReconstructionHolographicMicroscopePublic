class display_general():

    def turn_on_led(self, row, col):
        pass

    def set_sequence(self, datalist):
        pass

    def turn_off_led(self, row, col):
        pass

    def clear_display(self):
        pass

    def turn_on(self):
        pass

    def turn_off(self):
        pass

    def restart(self):
        pass

    def set_BIAS(self, value):
        pass

    def set_led_intensity(self, value):
        """ Change the intensity of the LED. """
        if value > self.max_intensity:
            value = self.max_intensity
        elif value < 0:
            value = 0
        self.intensity_value = value

    def saveOptions(self, luminanceValue, BIASvalue=None):
        self.set_led_intensity(luminanceValue)

        if BIASvalue:
            self.set_BIAS(BIASvalue)

    
