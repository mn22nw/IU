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
    posTaken = False
    availableBubblePositions = []
    distanceToClostestGridBubble = 0
    collidedWithWall = False
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

    def animationComplete(self):
        self.unbind(pos=self.callbackPosWallCollision)
        self.fitBubbleToGrid()

        #check if it targeted the same colors and if so, remove the bubble itself. 
        if self.findColorMatches():
            layout = self.parent.parent.ids.bubbleLayout
            layout.remove_widget(self)
        else: 
            #add bubble to the list of bubbles 
            self.parent.parent.bubbleList.append(self)

        

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

    def onWallCollision(self, anglechange):
        self.animation.stop(self)
        print('self.angle', self.angle, self.angle + math.radians(90))
        self.startAnimation(self.angle - math.radians(anglechange))
        #needs to send ranians
        self.unbind(pos=self.callbackPosWallCollision)
        #threatAnimation = Animation( pos=(600, 500), opacity = 0.5, duration=0.2)
        #threatAnimation.start(self)
        #change the angle with 90degrees

    def checkBubbleCollision(self, bubble):              
        if self.checkBubbleDistance(bubble):
            #stop animation on collide
            self.animation.stop(self)
            self.animationComplete()
            self.unbind(pos=self.callbackPos)
            #print('A BUBBLE HAS COLLIDED width a bubble at', bubble.x, bubble.y, 'and it has the color of', str(bubble.getColor()))      


    def checkThreatCollision(self, threat): 
        #find threats in parent threat list
        print('threeaaat COLLIIIIIISSISOSIon')
        self.animation.stop(self)
        self.animationComplete()
        self.unbind(pos=self.callbackPos)
        threat.displayQuestionScreen()
        #Clock.schedule_once(self.animateBubble, 1.1)
        #  Clock.schedule_once(self.removeBubble, 2)


    

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

    def calculateAvailableBubblePositions(self):
        self.availableBubblePositions = []
        if not len(self.parent.parent.bubbleGridList) == 0:
            for gridBubble in self.parent.parent.bubbleGridList[::-1]: #start from the last added bubble
                if not gridBubble.posTaken:
                    self.availableBubblePositions.append(gridBubble)

    #TODO-move this outside of bubbleclass!!!
    def fitBubbleToGrid(self):
        bubblesToCompareList = []
        distancesToCompareList = []
        self.calculateAvailableBubblePositions()
        for b in self.availableBubblePositions:
            #get the distance of the closest gridBubbles to the bubble
            distance = self.getGridBubbleDistance(b)
            b.distanceToClostestGridBubble = distance
            
            #if the distance is close enough we have a potential position for the bubble, so add this gridBubble to a list
            if b.distanceToClostestGridBubble > 0: 
                bubblesToCompareList.append(b)
                distancesToCompareList.append(b.distanceToClostestGridBubble)

        #just need to see which of the nearby gridBubbles that are the closest one, and set the bubble position to that 
        if not len(distancesToCompareList) == 0:
            smallestDistance = min(distancesToCompareList)       
            for b in bubblesToCompareList:

                if b.distanceToClostestGridBubble == smallestDistance:
                    self.pos_hint = b.pos_hint              

                    #set the bubble as taken! 
                    if b in self.parent.parent.bubbleGridList[::-1]:
                        print('iT*S INSEDE THE GRID YOOO')
                        b.posTaken = True

    #TODO - this should be move outside of bubble class
    def findColorMatch(self, bubble):
        print('triesTOfindCOlorMatch')
        colorMatches = []
        if not len(self.parent.parent.bubbleList) == 0:
            hitAreaRight = bubble.center_x + bubble.width * 0.5
            hitAreaLeft = bubble.center_x - bubble.width * 0.5
            hitAreaTop = bubble.center_y + bubble.width
            hitAreaBottom = bubble.center_y - bubble.width
            for b in self.parent.parent.bubbleList:

                if b.collide_point(hitAreaRight , hitAreaTop):
                    if b.getColor() == self.getColor():
                        colorMatches.append(b)

                if b.collide_point(hitAreaRight , hitAreaBottom):
                    if b.getColor() == self.getColor():
                        colorMatches.append(b)

                if b.collide_point(hitAreaLeft , hitAreaTop):
                    if b.getColor() == self.getColor():
                        colorMatches.append(b)
                        

                if b.collide_point(hitAreaLeft , hitAreaBottom):
                    if b.getColor() == self.getColor():
                        colorMatches.append(b)
                           
            return colorMatches
    #TODO - this should be move outside of bubble class
    def findColorMatches(self):
        bubblesWithSameColor = 0
        colorMatchesList = self.findColorMatch(self)
        moreMatchesList = []
    
        for bubble in colorMatchesList:
            moreMatchesList = self.findColorMatch(bubble)
            #bubblesWithSameColor += len(colorMatchesList)

        totalList = colorMatchesList + moreMatchesList
        #if there is 3 or more of the same color pop them and remove the recently fired bubble
        if len(totalList) + 1 >= 3:
            for b in totalList:
                layout = self.parent.parent.ids.bubbleLayout
                b.posTaken = False
                #add bubble to gridList 
                self.parent.parent.bubbleGridList.append(b)
                layout.remove_widget(b)
            return True
            print('Pop them!') 
            #then look if the last popped bubble has a bubble of same color near it? 

        return False
        #print('COLORMATCHESAFTER', len(colorMatches), colorMatches)
    
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
                if self.collide_widget(threat):
                    #check if it collides with a threat
                    self.checkThreatCollision(threat)
                    #self.removeBubble()
                    return

        # check here if the bubble collides with another bubble
        if not len(self.parent.parent.bubbleList) == 0:
            for bubble in self.parent.parent.bubbleList:
                if bubble.collide_widget(self):
                    #check if it collides with a bubble
                    self.checkBubbleCollision(bubble)
                    return
    
    def __eq__(self, other):
        return self.pos == other.pos       
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
