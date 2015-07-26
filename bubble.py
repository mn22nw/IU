import kivy
kivy.require('1.9.0')

from kivy.properties import NumericProperty, StringProperty
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.graphics import Color, Point
from kivy.app import App

from kivy.utils import boundary
import math
from kivy.vector import Vector
import random

class Bubble(Image):
    radius = NumericProperty() 
    bubbleColor= StringProperty()
    angle = NumericProperty(0) # in radians!
    animation = None
    colorList = ['blue', 'green', 'red', 'purple', 'yellow']
    exploding = False
        
    '''
    ####################################
    ##
    ##   Bubble Behavioral
    ##
    ####################################
    '''
    
    def __init__(self, **kwargs):
        super(Bubble, self).__init__(**kwargs)
        #set radius to half the size of the bullet minus 2 pixels
        self.radius = self.width *0.5 - 2

    def fire(self):
        #angle in radiants
        destination = self.calculateDestination(self.angle)

        app = App.get_running_app()  # maybe change this??!
        speed = boundary(app.config.getint('GamePlay', 'BubbleSpeed'), 1, 10)
        self.animation = self.create_animation(speed, destination)
        
        # start the animation
        self.animation.start(self)
       
        #when animation is completed/stopped run this function
        self.animation.bind(on_complete=self.animationComplete)
        
        # start to track the position changes
        self.bind(pos=self.callbackPos)
        
        


    def calculateOrigin(self):
        self.x +=  math.cos(degrees_to_radians(self.boss.turretAngle)) * (Tank.side-20)
        self.posy +=  math.sin(degrees_to_radians(-self.boss.turretAngle)) * (Tank.side-20)
    
    def create_animation(self, speed, destination):
        # create the animation
        # t = s/v -> v from 1 to 10 / unit-less
        # NOTE: THE DIFFERENCE BETWEEN TWO RENDERED ANIMATION STEPS
        # MUST *NOT* EXCESS THE RADIUS OF THE BULLET! OTHERWISE I
        # HAVE PROBLEMS DETECTING A COLLISION WITH A DEFLECTOR!!
        time = Vector(self.center).distance(destination) / (speed * +70.0)
        # the splitting of the position animation in (x,y) is a work-around for the kivy issue #2667 for version < 1.9.0
        return Animation(x=destination[0],y=destination[1], duration=time, transition='linear')
        
    def calculateDestination(self, angle):

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

        #set a destination
        destination = 600

        #set angle and distance from the correct position (x, y).
        destinationX = destination* math.cos(self.angle) + self.center_x 
        destinationY = destination* math.sin(self.angle) + self.center_y

        return (destinationX, destinationY)

    def animationComplete(self, animation, widget):
        print('COMPLETEOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOD')
        self.correctPlacementBubble()

        #this doesn't workediworki
        #self.checkWidgetOverlap()
        #add the new bubble to the list of bubbles
        self.parent.bubbleList.append(self)

    def correctPlacementBubble(self):
        if not len(self.parent.bubbleList) == 0:
            for bubble in self.parent.bubbleList:
                if bubble.collide_widget(self):
                    print(bubble.getColor())
                '''
                if bubble.collide_widget(self):
                    X = bubble.center_x
                    Y = bubble.center_y
                    self.center = X - self.radius * 0.5, Y - self.radius * 2
                '''

   
    def checkBubbleDistance(self,bubble):
        #calculate the distance between the centre of both bubbles
        a = Vector(self.center)
        b = Vector(bubble.center)
        distance = int(Vector(a).distance(b))

        diameter = int(self.radius + bubble.radius)

        print('CENTER', distance, 'radi: ', diameter)

        #if for some reason the distance is 0 return false
        if distance == 0:
            return False

        if distance < diameter: 
            return True        

        #if there is 2 of sam e color POP THEM and remove them from bubble_list

    def checkBubbleCollision(self, bubble): 
        print('A BUBBLE HAS COLLIDED width a bubble at', bubble.x, bubble.y, 'and it has the color of', str(bubble.getColor()))            
        if self.checkBubbleDistance(bubble):
            #stop animation on collide
            self.animation.stop(self)
            self.unbind(pos=self.callbackPos)
    
    def checkCollision(self, bubble):
        if self.checkBubbleCollision(bubble):
            return True
        if self.checkThreatCollision(bubble):
            return True


    def checkThreatCollision(self, bubble): 
        pass
        #self.threatExplode()
              

    def checkWidgetOverlap(self):
        vaku = 0
        if not len(self.parent.bubbleList) == 0:
            for bubble in self.parent.bubbleList:
                for i in range(int(self.width * 0.5)):
                    if int(bubble.x) + i == int(self.x):
                        print('JOMENSeeATTE :' , bubble.getColor(), 'x', bubble.x, 'selfX', self.x)            
        print( 'VAKUUUU', len(self.parent.bubbleList))
 
    def callbackPos(self, instance, pos):
        # check here if the bubble collides with another bubble
        if not len(self.parent.bubbleList) == 0:
            for bubble in self.parent.bubbleList:
                if bubble.collide_widget(self):
                    #check if it collides with a threat or bubble
                    self.checkCollision(bubble)
                    return
        
        
        # then check if there's a collision with threatBox:
        if not len(self.parent.threat_list) == 0:
            for threat in self.parent.threat_list:
                if self.collide_widget(threat):
                    self.on_collision_with_threat()
                    return

    def bubbleExplode(self):
        if self.exploding == True:
            return
        self.exploding = True
        
        self.unbind(pos=self.callback_pos)
        self.animation.unbind(on_complete=self.on_collision_with_edge)
        self.animation.stop(self)
        
        #self.parent.bubble_exploding()

    #TODO - flytta till threat!!!?!
    def threatExplode(self):
        if self.exploding == True:
            return
        self.exploding = True
        
        self.unbind(pos=self.callback_pos)
        self.animation.unbind(on_complete=self.on_collision_with_edge)
        self.animation.stop(self)
        
        self.parent.threat_exploding()
        
    def on_collision_with_edge(self, animation, widget):
        self.bubbleExplode()

        
    def degreesToRadians(self,degrees):
            return degrees * (math.pi / 180.0)
    
    #returns a string with the color name  
    def setRandomColor(self):
        c = random.randint(0,(len(self.colorList) - 1))
        self.bubbleColor = self.colorList[c]
        return self.bubbleColor

        #for c in range(0,len(colorList)):
    def getColor(self):
        #print(self.bubbleColor, 'CCssCCCOL')
        return self.bubbleColor


