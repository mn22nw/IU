# -*- coding: utf-8 -*-
import kivy
kivy.require('1.9.0')

from kivy.app import App
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.graphics import Color, Point
from kivy.clock import Clock
from functools import partial

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
    posTaken = False
    distanceToClostestGridBubble = 0
    collidedWithWall = False
    colorMatchesList = []
    pointList = []

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
        #angle is in radians
        self.startAnimation(self.angle)
        #when animation is completed/stopped run this function
        #self.animation.bind(on_complete=self.animationComplete)
        
        # start to track the position changes
        self.bind(pos=self.callbackPos)
        self.bind(pos=self.callbackPosWallCollision)
            

    def startAnimation(self, angle):
        destination = self.calculateDestination(angle)
        app = App.get_running_app()  # maybe change this??!
        speed = boundary(app.config.getint('GamePlay', 'BubbleSpeed'), 1, 10)
        self.animation = self.createAnimation(speed, destination)
        
        # start the animation
        self.animation.start(self)

    def animationComplete(self):
        self.unbind(pos=self.callbackPosWallCollision)
    

        
    def calculateOrigin(self):
        self.x +=  math.cos(degrees_to_radians(self.boss.turretAngle)) * (Tank.side-20)
        self.posy +=  math.sin(degrees_to_radians(-self.boss.turretAngle)) * (Tank.side-20)
    
    def createAnimation(self, speed, destination):
        time = Vector(self.center).distance(destination) / (speed * +70.0)
        return Animation(x=destination[0],y=destination[1], duration=time, transition='linear')
        
    def calculateDestination(self, angle):
        #set a destination
        destination = 600

        #set angle and distance from the correct position (x, y).
        destinationX = destination* math.cos(angle) + self.center_x 
        destinationY = destination* math.sin(angle) + self.center_y

        return (destinationX, destinationY)


    def onWallCollision(self, anglechange):
        self.animation.stop(self)
        print('self.angle', self.angle, self.angle + math.radians(90))
        self.startAnimation(self.angle - math.radians(anglechange))
        #needs to send ranians
        self.unbind(pos=self.callbackPosWallCollision)
        #threatAnimation = Animation( pos=(600, 500), opacity = 0.5, duration=0.2)
        #threatAnimation.start(self)
        #change the angle with 90degrees

    

    def getGridBubbleDistance(self,bubble):
        #calculate the distance between the centre of both bubbles
        a = Vector(self.center)
        b = Vector(bubble.center)
        distance = int(Vector(a).distance(b))
        diameter = int(bubble.width*1.4)
        
        #print('DISTANCE', distance)
        if distance < diameter: 
            return distance
        return 0  


    #TODO - this should be move outside of bubble class - and refactor it to remove DRY
    def findColorMatch(self, bubble):
        print('triesTOfindCOlorMatch')
        colorMatches = []
        if not len(self.parent.parent.bubbleList) == 0:
            hitAreaRight = bubble.center_x + bubble.width * 0.5
            hitAreaLeft = bubble.center_x - bubble.width * 0.5
            hitAreaTop = bubble.center_y + bubble.width * 0.85
            hitAreaBottom = bubble.center_y - bubble.width * 0.85
            for b in self.parent.parent.bubbleList:

                #Top right bubble
                if b.collide_point(hitAreaRight , hitAreaTop):
                    if b.getColor() == bubble.getColor():
                        colorMatches.append(b)

                #Bottom right bubble
                if b.collide_point(hitAreaRight , hitAreaBottom):
                    if b.getColor() == bubble.getColor():
                        colorMatches.append(b)
                #Top left bubble
                if b.collide_point(hitAreaLeft , hitAreaTop):
                    if b.getColor() == bubble.getColor():
                        colorMatches.append(b)
                        
                #Bottom left bubble
                if b.collide_point(hitAreaLeft , hitAreaBottom):
                    if b.getColor() == bubble.getColor():
                        colorMatches.append(b)

                #Right bubble
                if b.collide_point(bubble.center_x + bubble.width , bubble.center_y):
                    if b.getColor() == bubble.getColor():
                        colorMatches.append(b)

                #Left bubble
                if b.collide_point(bubble.center_x - bubble.width , bubble.center_y):
                    if b.getColor() == bubble.getColor():
                        colorMatches.append(b)
                           
            return colorMatches

    

    def removeBubble(self, bubble): 

        layout = self.parent.parent.ids.bubbleLayout
        #Clock.schedule_once(self.animateBubble, 1.1)
        b = Bubble()
        b.source = 'graphics/points.png'
        b.pos_hint = bubble.pos_hint
        layout.add_widget(b) 
        self.pointList.append(bubble)
        layout.remove_widget(bubble)
        self.parent.parent.bubbleList.remove(bubble)

    #this function first removes the colormatch, the returns the related new colormatches for the removed colormatch bubble
    def removeBubbleAndFindClosestColorMatch(self, bubble):
        bubble.posTaken = False
        #add bubble to gridList 
        self.parent.parent.bubbleGridList.append(bubble)
        self.removeBubble(bubble)
        #find closest bubbleMatch      
        colorMatchesList = self.findColorMatch(bubble)

        return colorMatchesList
        

    #TODO - this should be move outside of bubble class
    def findColorMatches(self):
        bubblesWithSameColor = 0
        self.colorMatchesList = self.findColorMatch(self)
        moreMatchesList = []
        totalColorMatchesList = []
        
        for bubble in  self.colorMatchesList:
            print(bubble.getColor())
            moreMatchesList = self.findColorMatch(bubble)
            #bubblesWithSameColor += len(colorMatchesList)

        print('moreMatchesList',  len(moreMatchesList))
        totalColorMatchesList =  self.colorMatchesList + moreMatchesList
        totalColorMatchesList.append(self)
        
        return totalColorMatchesList
        
    def removeColorMatches(self):
        #if there is three or more of the same color pop them and remove them 
            while True: 
                for bubble in self.colorMatchesList:
                    self.colorMatchesList.remove(bubble)
                    #start with removing the first colorMatch the shooting bubble had. 
                    #then remove every bubble that's related to that one
                    while True:
                        if bubble in self.parent.parent.bubbleList:
                            bList= self.removeBubbleAndFindClosestColorMatch(bubble)
                            if len(bList) == 0:
                                break
                            
                            if len(bList) > 1:
                                bubble = bList[0]
                                bList.remove(bubble)
                                for b in bList:
                                    self.colorMatchesList.append(b)
                            else:
                                bubble = bList[0]  
                        else:
                            break
                if len(self.colorMatchesList) == 0:
                    break
    
    def checkThreatCollision(self, threat): 
        if self.collide_widget(threat):
            self.animation.stop(self)
            self.animationComplete()
            self.unbind(pos=self.callbackPos)
            threat.displayQuestionScreen()  
            return True
        return False  

    def checkBubbleDistance(self,bubble):
        #calculate the distance between the centre of both bubbles
        a = Vector(self.center)
        b = Vector(bubble.center)
        distance = int(Vector(a).distance(b))
        diameter = int(bubble.width *.9) 

        #if for some reason the distance is 0 return false
        if distance == 0:
            return False

        if distance < diameter: 
            return True  

    def checkBubbleCollision(self, bubble): 
        if bubble.collide_widget(self):             
            if self.checkBubbleDistance(bubble):
                self.animation.stop(self)
                self.animationComplete()
                self.unbind(pos=self.callbackPos)
                return True
        return False
            #print('A BUBBLE HAS COLLIDED width a bubble at', bubble.x, bubble.y, 'and it has the color of', str(bubble.getColor()))      

    
    #now check every bubble for the matched color and calculate the sum of the same colors
    def callbackPosWallCollision(self, instance, pos):
        #check if collision with wall
        leftWall = self.parent.parent.ids.leftWall
        rightWall = self.parent.parent.ids.rightWall
        #only do this once....hmmm
        if self.collide_widget(leftWall):
            self.onWallCollision(90)

        if self.collide_widget(rightWall):
            self.onWallCollision(-90)


    def callbackPos(self, instance, pos):

        # check if there's a collision with a threat
        if not len(self.parent.parent.threatListCopy) == 0:
            for threat in self.parent.parent.threatListCopy:
                if self.checkThreatCollision(threat):
                    return

        # check here if the bubble collides with another bubble
        if not len(self.parent.parent.bubbleList) == 0:
            for bubble in self.parent.parent.bubbleList:
                if self.checkBubbleCollision(bubble):
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
    '''    
    def removeBubble(self, instance):
        self.parent.remove_widget(self)
    '''
