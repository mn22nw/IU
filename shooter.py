import kivy

from kivy.properties import ObjectProperty
from kivy.graphics.transformation import Matrix
from kivy.uix.widget import Widget

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
class Shooter(Widget):
    shooter_tower_scatter = ObjectProperty(None)
    shooter_tower_angle = ObjectProperty(None)

    '''
    ####################################
    ##
    ##   On Touch Down
    ##
    ####################################
    '''
    def on_touch_down(self, touch):

        '''
        if not self.collide_point(*touch.pos):
            return False
        else:
            touch.ud['shooter_touch'] = True
            return True
        '''   
        
    
    '''
    ####################################
    ##
    ##   On Touch Move
    ##
    ####################################
    '''
    def on_touch_move(self, touch):

        print('DB HAS BEEN MOVED LOL', touch.y, '<---y', self.top)
        ud = touch.ud
        #if not 'shooter_touch' in ud:
           # return False
        a = atan2(20,5)
        angle = atan2(touch.y - self.shooter_tower_scatter.center_y, touch.x - self.shooter_tower_scatter.center_x );
        angle = angle * (180/pi);
            # if the current touch is already in the 'rotate' mode, rotate the tower.
            #dx = touch.x - self.x
            #dy = touch.y - self.y
        angle = boundary(angle, 10, 180)     #boundary(value, minvalue, maxvalue)  Limit a value between a minvalue and maxvalue.
        if angle < 149 and angle > 29:

            print(angle, 'ANGLEEE')
            angle_change = self.shooter_tower_scatter.rotation - angle
            #rotation_matrix = Matrix().rotate(-radians(angle_change), 0, 0, 1)
            #self.shooter_tower_scatter.apply_transform(rotation_matrix, post_multiply=True, anchor=(105, 15))
            self.shooter_tower_scatter.rotation = -90 + angle

            self.shooter_tower_angle = angle
            '''
            if angle < 90:
                if not self.shooter_tower_scatter.x > self.x :
                    print ('scatter', self.shooter_tower_scatter.x , 'self', self.x)
                    self.shooter_tower_scatter.x = self.shooter_tower_scatter.x - 1
            if angle > 90:
                if not self.shooter_tower_scatter.x < self.x :
                    print ('scatter', self.shooter_tower_scatter.x , 'self', self.x)
                    self.shooter_tower_scatter.x = self.shooter_tower_scatter.x + 1
            '''
       #jetSprite.rotation =90 + angle;
            

