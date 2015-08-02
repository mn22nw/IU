import kivy

from kivy.properties import ObjectProperty
from kivy.graphics.transformation import Matrix
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
        #print('touched Y\'ALL', touch.y, '<---y')

        '''
        if not self.collide_point(*touch.pos):
            return False
        else:
            touch.ud['shooter_touch'] = True
            return True
        '''   
    def on_touch_up(self, touch):
        print('touched Y\'ALL X', touch.x, '<---x')
        
        self.changeAngle(touch)
        #shooot a bubble muhahah
        if not touch.is_mouse_scrolling:
            self.parent.parent.fireBubble()
        
        
    '''
    ####################################
    ##
    ##   On Touch Move
    ##
    ####################################
    '''
    def on_touch_move(self, touch):
        self.changeAngle(touch)
          

    def changeAngle(self, touch):
        #print('DB HAS BEEN MOVED LOL', touch.y, '<---y', self.top)
        ud = touch.ud
        #self.shooterTowerAngle = 60.0

        
        #calculates the angle i radians from x, and y values   
        angle = atan2(touch.y - self.center_y, touch.x - self.center_x );
        
        
        #radians to degrees
        angle = angle * (180/pi);    
        #print('ANGLE', angle)
        
        #Limit a value between a minvalue and maxvalue, for how far the tower can rotate
        angle = boundary(angle, 0, 360)     #boundary(value, minvalue, maxvalue)  Limit a value between a minvalue and maxvalue.
        
        if angle < 149 and angle > 29:
            
            self.shooterTowerAngle = angle  - 90
            self.shootDirectionAngle = angle
            #print(angle, 'miiip DEgrees????')
            #self.shooter_tower_angle = angle


       #jetSprite.rotation =90 + angle;
    '''
        def radians_to_degrees(radians):
            return (radians / math.pi) * 180.0
        
        def degrees_to_radians(degrees):
            return degrees * (math.pi / 180.0)
    '''