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
import time

'''
    ####################################
    ##
    ##   Bubble Class
    ##
    ####################################
'''

class Bubble(Image):
        
    def __init__(self, **kwargs):
        super(Bubble, self).__init__(**kwargs)
        #properties
        self.bubbleColor= StringProperty()
        self.angle = NumericProperty(0) # in radians!
        self.colorList = ['blue', 'green', 'red', 'purple', 'yellow']
        self.animation = None       
        self.bubbleSizeX =  0.08333333333333 #setting procentual values for bubblesize, to be able to make the game responsive
        self.bubbleSizeY = 0.045
        self.posTaken = False
        self.distanceToClostestGridBubble = 0
        self.collidedWithWall = False
        self.colorMatchesList = []
        self.allColorMatchesList = []

    def fire(self):
        #angle is in radians
        self.startAnimation(self.angle)
        # start to track the position changes
        self.bind(pos=self.callbackPos)
        self.bind(pos=self.callbackPosWallCollision)
     
    def calculateOrigin(self):
        self.x +=  math.cos(degrees_to_radians(self.boss.turretAngle)) * (Tank.side-20)
        self.posy +=  math.sin(degrees_to_radians(-self.boss.turretAngle)) * (Tank.side-20)    
    
    def calculateDestination(self, angle):
        #set a destination
        destination = 600
        #set angle and distance from the correct position (x, y).
        destinationX = destination* math.cos(angle) + self.center_x 
        destinationY = destination* math.sin(angle) + self.center_y
        return (destinationX, destinationY)       


    def startAnimation(self, angle):
        destination = self.calculateDestination(angle)
        app = App.get_running_app()  # maybe change this??!
        speed = boundary(app.config.getint('GamePlay', 'BubbleSpeed'), 1, 10)
        self.animation = self.createAnimation(speed, destination)      
        # start the animation
        self.animation.start(self)

    def animationComplete(self):
        self.unbind(pos=self.callbackPosWallCollision)      
        
        self.parent.parent.vc.fitBubbleToGrid()
        Clock.schedule_once(self.parent.parent.vc.removeOrKeepBubbles,1)
        #self.parent.parent.vc.removeOrKeepBubbles()  
    
    def createAnimation(self, speed, destination):
        time = Vector(self.center).distance(destination) / (speed * +70.0)
        return Animation(x=destination[0],y=destination[1], duration=time, transition='linear')
    
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

    def findColorMatches(self):  
        print('triesTOfindCOlorMatch : ****', self.getColor(), '*****',self.pos)
        colorMatches = []
        if not len(self.parent.parent.bubbleList) == 0:
            hitAreaRight = self.center_x + self.width * 0.5
            hitAreaLeft = self.center_x - self.width * 0.5
            hitAreaTop = self.center_y + self.width * 0.85
            hitAreaBottom = self.center_y - self.width * 0.85
            for b in self.parent.parent.bubbleList:
                #Top right bubble
                if b.collide_point(hitAreaRight , hitAreaTop):
                    print('TOP RIGHT BUBBLE COLLIDE', b.getColor())
                    if b.getColor() == self.getColor():
                        colorMatches.append(b)
                #Bottom right bubble
                if b.collide_point(hitAreaRight, hitAreaBottom):
                    print('BOTTOM RIGHT BUBBLE COLLIDE', b.getColor())
                    if b.getColor() == self.getColor():
                        colorMatches.append(b)
                #Top left bubble
                if b.collide_point(hitAreaLeft , hitAreaTop):
                    print('TOP LEFT BUBBLE COLLIDE', b.getColor())
                    if b.getColor() == self.getColor():
                        colorMatches.append(b)
                        
                #Bottom left bubble
                if b.collide_point(hitAreaLeft , hitAreaBottom):
                    print('BOTTOM LEFT BUBBLE COLLIDE', b.getColor())
                    if b.getColor() == self.getColor():
                        colorMatches.append(b)

                #Right bubble
                if b.collide_point(self.center_x + self.width , self.center_y):
                    print('RIGHT BUBBLE COLLIDE', b.getColor())
                    if b.getColor() == self.getColor():
                        colorMatches.append(b)

                #Left bubble
                if b.collide_point(self.center_x - self.width , self.center_y):
                    print('LEFT BUBBLE COLLIDE', b.getColor())
                    if b.getColor() == self.getColor():
                        colorMatches.append(b)
            print('DID IT FIND ANY??', len(colorMatches)) 
            #if it has more than one color of the same color next to it - remove them from the bubbleList
            if len(colorMatches) > 0:
                for bubble in colorMatches:
                    self.parent.parent.bubbleList.remove(bubble)              
            return colorMatches

        
    def findClosestColorMatches(self):
        #checks how many colormatches that are closest to the bubble (maximum 6)
        listOfMatches = self.findColorMatches()        
        print('Length FoR listOfMatches', len(listOfMatches) ) 
        return listOfMatches
        
    def findAllRelatedColorMatches(self, firstColorMatchesList):
        allRelatedColorMatchesList = []
        print('THE LENGHT OF firstColorMatchesList', len(firstColorMatchesList))

        if not len(firstColorMatchesList) == 0:
            for bubble in firstColorMatchesList:
                allRelatedColorMatchesList.append(bubble)
            while len(firstColorMatchesList) > 0: 
                print('\nINSIDE WHILE LOOP- THE LENGHT OF firstColorMatchesList')
                print(len(firstColorMatchesList))
                if len(firstColorMatchesList) == 0:   
                    break
                
                for bubble in  firstColorMatchesList:
                    #allRelatedColorMatchesList.append(bubble)  
                    firstColorMatchesList.remove(bubble)
                    #the bubble needs to be removed from the bubbleList so the removeColorMatches function doesn't find the same bubble over and over again (endless loop will occur)
                    
                    #fint the closest colormatches (it does not count with itself)
                    bList = bubble.findClosestColorMatches()
                    
                    if bList > 0:                       
                        #allRelatedColorMatchesList.append(bubble) 
                        for b in bList:
                            print('\nbList', len(bList))
                            #if bubble in self.parent.parent.bubbleList:
                                #self.parent.parent.bubbleList.remove(bubble)
                            firstColorMatchesList.append(b)
                            print('\nIt adds to the allreladed')
                            #instead of deleting the bubble now, I save it for later in a list so that the controller can access it and delete all the bubbles and add points to them before they get deleted
                            allRelatedColorMatchesList.append(b)
                    
                
                #break
            print(len(allRelatedColorMatchesList))
        return allRelatedColorMatchesList

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
       
    
    #returns a string with the color name  
    def setRandomColor(self):
        c = random.randint(0,(len(self.colorList) - 1))
        self.bubbleColor = self.colorList[c]
        return self.bubbleColor

        #for c in range(0,len(colorList)):
    def getColor(self):
        #print(self.bubbleColor, 'CCssCCCOL')
        return self.bubbleColor

    def changeToPointsPicture(self):
        self.source = 'graphics/points.png'

    def animatePointsPicture(self):
        Clock.schedule_once(self.removeBubble, 0.2)
    '''
    def animateBubble(self, instance):
        X = self.width
        Y = self.height
        threatAnimation = Animation( size=(X *1.5, X*1.5), opacity = 0, duration=0.2)
        threatAnimation.start(self)
        self.parent.remove_widget(self)
      
    '''
    def removeBubble(self, instance):
        self.parent.parent.bubbleLayout.remove_widget(self)

    
