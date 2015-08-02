# -*- coding: utf-8 -*-
import kivy
kivy.require('1.9.0')

from kivy.app import App
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.graphics import Color, Point
from kivy.clock import Clock

from kivy.utils import boundary
import math
from kivy.vector import Vector
import random

class Bubble(Image):
    bubbleColor= StringProperty()
    angle = NumericProperty(0) # in radians!
    animation = None
    colorList = ['blue', 'green', 'red', 'purple', 'yellow']
    exploding = False
    #setting procentual values for bubblesize, to be able to make the game responsive
    bubbleSizeX =  0.08333333333333 
    bubbleSizeY = 0.045
    '''
    ####################################
    ##
    ##   Bubble Behavioral
    ##
    ####################################
    '''
    
    def __init__(self, **kwargs):
        super(Bubble, self).__init__(**kwargs)

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

        time = Vector(self.center).distance(destination) / (speed * +70.0)
        # the splitting of the position animation in (x,y) is a work-around for the kivy issue #2667 for version < 1.9.0
        return Animation(x=destination[0],y=destination[1], duration=time, transition='linear')
        
    def calculateDestination(self, angle):
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
        '''
        #set a destination
        destination = 600

        #set angle and distance from the correct position (x, y).
        destinationX = destination* math.cos(self.angle) + self.center_x 
        destinationY = destination* math.sin(self.angle) + self.center_y

        return (destinationX, destinationY)

    def animationComplete(self, animation, widget):
        print('COMPLETEOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOD')

        #self.correctPlacementBubble()

        #this doesn't workediworki
        self.checkWidgetOverlap()
        self.parent.parent.bubbleList.append(self)
        #add the new bubble to the list of bubbles
        

    #TODO - calulate correctPlacement before calculating related colors
    '''    
    def correctPlacementBubble(self):
        if not len(self.parent.bubbleList) == 0:
            for bubble in self.parent.bubbleList:
                i = 0
                
                #if they collided
                if self.checkBubbleDistance(bubble):
                    i += 1
                    print('TRUUUUUUUUUUEDISTANCEE')
                    print('A BUBBLE HAS COLLIDED width a bubble at', bubble.x, bubble.y, 'and it has the color of', str(bubble.getColor()))   
                    print(bubble.getColor())


                if i == 1:
                    a = Animation( center_x=(bubble.x ), duration=0.2)
                    a.start(self)  
                
                
                #Check if a point (x, y) is inside the widget’s axis aligned bounding
                if bubble.collide_point(self.center_x , self.top):
                    i += 1
                    print('TRUUUUUUUUUUE')
                    print(bubble.getColor())
                    #new position
                    print(self.x)
                  
                if i == 1:
                    a = Animation( center_x=(bubble.x ), duration=0.2)
                    a.start(self)  

                #sätt nya placemen till bubbelcolorns x center +....storlek? 

                
                if bubble.collide_widget(self):


                    print(bubble.getColor())
                    X = bubble.center_x
                    Y = bubble.center_y
                    self.center = X - self.radius * 0.5, Y - self.radius * 2
                
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

        diameter = int(bubble.width)

        print('CENTER', distance, 'radi: ', diameter)

        #if for some reason the distance is 0 return false
        if distance == 0:
            return False

        if distance < diameter: 
            return True        


    def checkBubbleCollision(self, bubble):              
        if self.checkBubbleDistance(bubble):
            #stop animation on collide
            self.animation.stop(self)
            self.unbind(pos=self.callbackPos)
            #print('A BUBBLE HAS COLLIDED width a bubble at', bubble.x, bubble.y, 'and it has the color of', str(bubble.getColor()))      


    def checkThreatCollision(self, threat): 
        #find threats in parent threat list
        print('threeaaat COLLIIIIIISSISOSIon')
        self.animation.stop(self)
        self.unbind(pos=self.callbackPos)
        threat.displayQuestionScreen()
        #Clock.schedule_once(self.animateBubble, 1.1)
        #  Clock.schedule_once(self.removeBubble, 2)


    def findColorMatch(self, bubble):
        colorMatches = []
        if not len(self.parent.parent.bubbleList) == 0:
            hitAreaRight = bubble.center_x + bubble.width * 0.5
            hitAreaLeft = bubble.center_x - bubble.width * 0.5
            hitAreaTop = bubble.center_y + bubble.width
            hitAreaBottom = bubble.center_y - bubble.width
            for b in self.parent.parent.bubbleList:

                if b.collide_point(hitAreaRight , hitAreaTop):
                    print('TRUUUUUUUUUUEAREA 1')
                    #print(b.getColor(), 'nunnle', self.getColor())
                    if b.getColor() == self.getColor():
                        print('SAME COLOR YOLO')
                        colorMatches.append(b)

                if b.collide_point(hitAreaRight , hitAreaBottom):
                    print('TRUUUUUUUUUUEAREA 2')
                   #print(b.getColor(), 'nunnle', self.getColor())
                    if b.getColor() == self.getColor():
                        print('SAME COLOR YOLO')
                        colorMatches.append(b)

                if b.collide_point(hitAreaLeft , hitAreaTop):
                    print('TRUUUUUUUUUUE 3')
                    if b.getColor() == self.getColor():
                        print('SAME COLOR YOLO')
                        colorMatches.append(b)
                    print(b.getColor(), 'nunnle', self.getColor())

                if b.collide_point(hitAreaLeft , hitAreaBottom):
                    print('TRUUUUUUUUUUE 4')
                    if b.getColor() == self.getColor():
                        print('SAME COLOR YOLO')
                        colorMatches.append(b)
                    print(b.getColor(), 'nunnle', self.getColor())
 
                

                '''
                for i in range(int(self.width * 0.5)):
                    if int(bubble.x) + i == int(self.x):
                        print('JOMENSeeATTE :' , bubble.getColor(), 'x', bubble.x, 'selfX', self.x) 
                '''           
            return colorMatches

    #TODO - this should be move outside of bubble class
    def checkWidgetOverlap(self):
        bubblesWithSameColor = 0
        colorMatches = self.findColorMatch(self)
        print('COLORMATCHES', len(colorMatches), colorMatches)

        if len(colorMatches) > 0:
            bubblesWithSameColor += len(colorMatches) +1
        
        for bubble in colorMatches:
            moreMatches = self.findColorMatch(bubble)
            bubblesWithSameColor += len(moreMatches)

        print('BUBBLES WITH SAMECOLOR', bubblesWithSameColor)
        print('COLORMATCHESAFTER', len(colorMatches), colorMatches)
    
    #now check every bubble for the matched color and calculate the sum of the same colors
 
    def callbackPos(self, instance, pos):
        # check if there's a collision with a threat
        if not len(self.parent.parent.threatListCopy) == 0:
            for threat in self.parent.parent.threatListCopy:
                if self.collide_widget(threat):
                    self.checkThreatCollision(threat)
                    #self.removeBubble()
                    return

        # check here if the bubble collides with another bubble
        if not len(self.parent.parent.bubbleList) == 0:
            for bubble in self.parent.parent.bubbleList:
                if bubble.collide_widget(self):
                    #check if it collides with a threat or bubble
                    self.checkBubbleCollision(bubble)
                    #remove bubbles of the same color
                    return
             
    '''            
    def bubbleExplode(self):
        if self.exploding == True:
            return
        self.exploding = True
        
        self.unbind(pos=self.callback_pos)
        self.animation.unbind(on_complete=self.on_collision_with_edge)
        self.animation.stop(self)
        
        #self.parent.bubble_exploding()
    '''
    
    #returns a string with the color name  
    def setRandomColor(self):
        c = random.randint(0,(len(self.colorList) - 1))
        self.bubbleColor = self.colorList[c]
        return self.bubbleColor

        #for c in range(0,len(colorList)):
    def getColor(self):
        #print(self.bubbleColor, 'CCssCCCOL')
        return self.bubbleColor

    def animateBubble(self, instance):
        X = self.width
        Y = self.height
        threatAnimation = Animation( size=(X *1.5, X*1.5), opacity = 0, duration=0.2)
        threatAnimation.start(self)
        self.parent.remove_widget(self)
        
    def removeBubble(self, instance):
        self.parent.remove_widget(self)
