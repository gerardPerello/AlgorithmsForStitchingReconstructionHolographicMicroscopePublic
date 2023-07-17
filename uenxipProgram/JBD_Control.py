import pygame
import os
from display_general import display_general

ROWS = 1080
COLUMNS = 1920

class JbdDisplay(display_general):
    def __init__(self, Width=1920, Height=1280, screenNo=3):
        if pygame.get_sdl_version()[0] == 2:
            print("ok")
        self.width = Width
        self.height = Height
        self.max_intensity = 255
        self.intensity_value = 255

        pygame.init()


        # Launch the auxiliary window
        if(screenNo == 2):
            self.screenRes = 1920
        elif(screenNo ==3):
            self.screenRes = 3840
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (self.screenRes,0)
        SCREENRECT = pygame.Rect(0,0,self.width,self.height)
        winstyle = 0 #pygame.RESIZABLE  # |FULLSCREEN
        bestdepth = pygame.display.mode_ok(SCREENRECT.size,winstyle,32)
        self.screen = pygame.display.set_mode(SCREENRECT.size,
                                               winstyle, bestdepth)
        
        self.clear_display()
        print('JBD Display has been initialized.')
        #pygame.mouse.set_visible(0)

    def turn_on_led(self, row, col):
        """ Turn on the selected LED. """
        self.screen.set_at((col, row), (self.intensity_value,
                                        self.intensity_value,
                                        self.intensity_value))
        pygame.display.flip()

    def set_sequence(self, datalist):
        """ Turn on several LEDs charge on datalist. """
        for led in datalist:
            row, col = led
            self.screen.set_at((col, row), (self.intensity_value,
                                            self.intensity_value,
                                            self.intensity_value))
        pygame.display.flip()


    def turn_off_led(self, row, col):
        """ Turn off the selected LED. """
        self.screen.set_at((col, row), (0,
                                        0,
                                        0))
        pygame.display.flip()

    def clear_display(self):
        """ Turn off the entire display. """
        self.screen = pygame.display.set_mode((self.width,
                                               self.height),
                                               pygame.NOFRAME)
        pygame.display.flip()

