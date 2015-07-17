import kivy
kivy.require('1.9.0')

from kivy.properties import NumericProperty, StringProperty
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.graphics import Color, Point
from kivy.app import App

from kivy.utils import boundary
from kivy.uix.popup import Popup
from math import tan
from math import sin
from math import pi
from math import radians
from kivy.vector import Vector
import random

class Threat(Image):
    threatColor= StringProperty()
    angle = NumericProperty(0) # in radians!
    animation = None
    colorList = ['blue', 'green', 'red', 'purple', 'yellow']
    exploding = False
        
    '''
    ####################################
    ##
    ##   Threat Behavioral
    ##
    ####################################
    '''
    
    def __init__(self, **kwargs):
        super(Bubble, self).__init__(**kwargs)
        
    def display_question_screen(self):
        # display the question screen on a Popup
        image = Image(source='graphics/help_screen.png')
        
        help_screen = Popup(title='Help Screen',
                            attach_to=self,
                            size_hint=(0.98, 0.98),
                            content=image)
        image.bind(on_touch_down=help_screen.dismiss)
        help_screen.open()
    
    def create_animation(self, speed, destination):
        # create the animation
        # t = s/v -> v from 1 to 10 / unit-less
        # NOTE: THE DIFFERENCE BETWEEN TWO RENDERED ANIMATION STEPS
        # MUST *NOT* EXCESS THE RADIUS OF THE BULLET! OTHERWISE I
        # HAVE PROBLEMS DETECTING A COLLISION WITH A DEFLECTOR!!
        time = Vector(self.center).distance(destination) / (speed * +70.0)
        # the splitting of the position animation in (x,y) is a work-around for the kivy issue #2667 for version < 1.9.0
        return Animation(x=destination[0],y=destination[1], duration=time, transition='linear')
        
    def calc_destination(self, angle):

        '''
        CHANGE ALL THIS!!!!!!
        '''
        # calculate the path until the bullet hits the edge of the screen
        win = self.get_parent_window()
        # the following "magic numbers" are based on the dimensions of the
        # cutting of the image 'overlay.png'
        left = 150.0 * win.width / 1920.0
        right = win.width - 236.0 * win.width / 1920.0
        top = win.height - 50.0 * win.height / 1920.0
        bottom = 96.0 * win.height / 1920.0
        
        bullet_x_to_right = right - self.center_x
        bullet_x_to_left = left - self.center_x
        bullet_y_to_top = top - self.center_y
        bullet_y_to_bottom = bottom - self.center_y
        
        destination_x = 0
        destination_y = 0
        
            
        # this is a little bit ugly, but I couldn't find a nicer way in the hurry
        if 0 <= self.angle < pi/2:
            # 1st quadrant
            if self.angle == 0:
                destination_x = bullet_x_to_right
                destination_y = 0
            else:
                destination_x = boundary(bullet_y_to_top / tan(self.angle), bullet_x_to_left, bullet_x_to_right)
                destination_y = boundary(tan(self.angle) * bullet_x_to_right, bullet_y_to_bottom, bullet_y_to_top)
                
        elif pi/2 <= self.angle < pi:
            # 2nd quadrant
            if self.angle == pi/2:
                destination_x = 0
                destination_y = bullet_y_to_top
            else:
                destination_x = boundary(bullet_y_to_top / tan(self.angle), bullet_x_to_left, bullet_x_to_right)
                destination_y = boundary(tan(self.angle) * bullet_x_to_left, bullet_y_to_bottom, bullet_y_to_top)
                
        elif pi <= self.angle < 3*pi/2:
            # 3rd quadrant
            if self.angle == pi:
                destination_x = bullet_x_to_left
                destination_y = 0
            else:
                destination_x = boundary(bullet_y_to_bottom / tan(self.angle), bullet_x_to_left, bullet_x_to_right)
                destination_y = boundary(tan(self.angle) * bullet_x_to_left, bullet_y_to_bottom, bullet_y_to_top) 
                       
        elif self.angle >= 3*pi/2:
            # 4th quadrant
            if self.angle == 3*pi/2:
                destination_x = 0
                destination_y = bullet_y_to_bottom
            else:
                destination_x = boundary(bullet_y_to_bottom / tan(self.angle), bullet_x_to_left, bullet_x_to_right)
                destination_y = boundary(tan(self.angle) * bullet_x_to_right, bullet_y_to_bottom, bullet_y_to_top)
            
        
        # because all of the calculations above were relative, add the bullet position to it.
        destination_x += self.center_x
        destination_y += self.center_y
        
        return (destination_x, destination_y)
        
    def check_threat_collision(self, deflector):
        '''
        CHANGE ALL THIS!!!!!!
        '''
        # first thing to do is: we need a vector describing the bullet. Length isn't important.
        bullet_position = Vector(self.center)
        bullet_direction = Vector(1, 0).rotate(self.angle * 360 / (2*pi))
        deflector_point1 = Vector(deflector.to_parent(deflector.point1.center[0], deflector.point1.center[1]))
        deflector_point2 = Vector(deflector.to_parent(deflector.point2.center[0], deflector.point2.center[1]))
        
        # then we need a vector describing the deflector line.
        deflector_vector = Vector(deflector_point2 - deflector_point1)
        
        # now we do a line intersection with the deflector line:
        intersection = Vector.line_intersection(bullet_position, bullet_position + bullet_direction, deflector_point1, deflector_point2)
        
        # now we want to proof if the bullet comes from the 'right' side.
        # Because it's possible that the bullet is colliding with the deflectors bounding box but
        # would miss / has already missed the deflector line.
        # We do that by checking if the expected intersection point is BEHIND the bullet position.
        # ('behind' means the bullets direction vector points AWAY from the vector 
        # [bullet -> intersection]. That also means the angle between these two vectors is not 0
        # -> due to some math-engine-internal inaccuracies, i have to check if the angle is greater than one:
        if abs(bullet_direction.angle(intersection - bullet_position)) > 1:
            # if the bullet missed the line already - NO COLLISION
            return False
        
        # now we finally check if the bullet is close enough to other bubbles:
        distance = abs(sin(radians(bullet_direction.angle(deflector_vector)) % (pi/2))) * Vector(intersection - bullet_position).length()
        if distance < (self.width / 2):
            # there is a collision!
            # kill the animation!
            self.animation.unbind(on_complete=self.on_collision_with_edge)
            self.animation.stop(self)
            # call the collision handler
            self.on_collision_with_deflector(deflector, deflector_vector)
            
        
    
    def callback_pos(self, instance, pos):
        # check here if the bullet collides with another bubble
        # (edge collision detection is irrelevant - the edge is where the bullet animation ends
        # and therefor a callback is raised then)
        
        # first check if there's a collision with other bubbles:
        if not len(self.parent.bubble_list) == 0:
            for bubble in self.parent.bubble_list:
                if bubble.collide_widget(self):
                    self.check_bubble_collision(bubble)
                    return
        
        
        # then check if there's a collision with threatBox:
        if not len(self.parent.threat_list) == 0:
            for threat in self.parent.threat_list:
                if self.collide_widget(threat):
                    self.on_collision_with_threat()
                    return


    #TODO - flytta till threat!!!?!
    def threat_explode(self):
        if self.exploding == True:
            return
        self.exploding = True
        
        self.unbind(pos=self.callback_pos)
        self.animation.unbind(on_complete=self.on_collision_with_edge)
        self.animation.stop(self)
        
        self.parent.threat_exploding()
        
    def on_collision_with_edge(self, animation, widget):
        self.bubble_explode()
    
    def on_collision_with_threat(self):
        self.threat_explode()
    
    def on_collision_with_bubble(self, bubble, deflector_vector):
        #self.parent.app.sound['poppop'].play()
        Pass
        #check if there is surrounding colors of same

        #if there is 2 of sam e color POP THEM and remove them from bullet_list
    
    #returns a string with the color name  
    def setRandomColor(self):
        c = random.randint(0,(len(self.colorList) - 1))
        self.bubbleColor = self.colorList[c]
        return self.bubbleColor

        #for c in range(0,len(colorList)):
    def getColor(self):
        print(self.bubbleColor, 'CCssCCCOL')
        return self.bubbleColor


