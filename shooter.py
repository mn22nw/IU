import kivy

from kivy.uix.image import Image
from kivy.properties import NumericProperty

from kivy.utils import boundary
from math import radians
from math import atan2
from math import pi

'''
####################################
##
##   Shooter Class
##
####################################
'''
class Shooter(Image):
    shooterTowerAngle = NumericProperty(0)
    shootDirectionAngle = NumericProperty(0)
    '''
    ####################################
    ##
    ##   On Touch Down
    ##
    ####################################
    '''
    def on_touch_down(self, touch):
        pass

    '''
    ####################################
    ##
    ##   On Touch Up
    ##
    ####################################
    '''
    def on_touch_up(self, touch):
        self.changeAngle(touch)
        #prevent from shooting bubbles when scrolling mouse wheel
        if not touch.is_mouse_scrolling:
            self.parent.parent.vc.fireBubble()
              
    '''
    ####################################
    ##
    ##   On Touch Move
    ##
    ####################################
    '''
    def on_touch_move(self, touch):
        self.changeAngle(touch)
          
    '''
    ####################################
    ##
    ##   CHANGE ANGLE
    ##
    ####################################
    '''
    def changeAngle(self, touch):
        maxAngle = 155
        minAngle = 25

        #calculates the angle i radians from x, and y values   
        angle = atan2(touch.y - self.center_y, touch.x - self.center_x );      
        
        #radians to degrees
        angle = angle * (180/pi);    
        #print('ANGLE', angle)

        #if user clicks below the shooter, move it to the lowest right/left position
        if angle < 180 and angle > -180: 
            print('less')
            self.shooterTowerAngle = maxAngle  - 90
            self.shootDirectionAngle = maxAngle   

        if angle < minAngle and angle >= - 90:
            print('more')
            self.shooterTowerAngle = minAngle  - 90
            self.shootDirectionAngle = minAngle

        #Limit a value between a minvalue and maxvalue, for how far the shooter can rotate
        angle = boundary(angle, 0, 360)     #boundary(value, minvalue, maxvalue)  Limit a value between a minvalue and maxvalue.
        
        if angle < maxAngle and angle > minAngle:
           
            self.shooterTowerAngle = angle  - 90
            self.shootDirectionAngle = angle
        
