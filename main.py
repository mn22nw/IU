# -*- coding: utf-8 -*-
#Inlämningsuppgift, Maria Nygren
#Plattform: Windows 8.1
#Python version 3.4.3
#kivy 1.9.0 (http://kivy.org/#home) - http://www.lfd.uci.edu/~gohlke/pythonlibs/#kivy

from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.uix.popup import Popup
from kivy.factory import Factory
from kivy.storage.jsonstore import JsonStore
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.core.audio import SoundLoader
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.clock import Clock

from math import sin
from math import cos
from math import radians
import random

from shooter import Shooter
from bubble import Bubble
from threat import Threat

#sätter storleken för huvudfönstret:
Window.size = 560, 836


#Custom styles for Label
class TableLabel(Label):  
    title = Label.text


'''
####################################
##
##   VIEW
##
####################################
'''
class MyView(Widget):
    #def __init__(self,vc):
    def __init__(self, vc=None, **kwargs):
        super(MyView, self).__init__(**kwargs)
    
        '''
        def __init__(self, *args, **kwargs):
            #self.first_arg = kwargs.pop('parent')
            parent = self.first_arg = kwargs.pop('parent')
            super(MyView, self).__init__(*args, **kwargs)
        '''
        
        #properties of the view 
        self.vc = vc
        self.lives = 5
        self.points = NumericProperty()
        self.bubble = None
        self.upcomingBubble = None
        self.bubbleList = []
        self.bubbleGridList = []
        self.threatList = []
        self.threatListCopy = []
        self.angle = NumericProperty()
        self.rowspaceY = 0
        self.bubbleSpaceX = 0
    
    #loading the view (called in the controller)
    def loadView(self):

        self.bubble = Bubble()

        #create all the bubbles and threats for the startup
        self.createObsticles()
        
        #create the grid for the bubbles to fit in
        self.createBubbleGrid()

        #add the first upcoming bubble to the view
        self.addUpcomingBubbletoView()


    def changeUpcomingBubbleColor(self):
        self.upcomingBubble.setRandomColor()
        self.upcomingBubble.source = 'graphics/bubbles/' + self.upcomingBubble.getColor() + '.png'


    def addUpcomingBubbletoView(self):
        self.upcomingBubble = self.createBubble(0,0)
        self.upcomingBubble.pos_hint={'x': 0.55, 'center_y': .5}
        #add the upcomingBubble to the preview-window
        self.nextBubbleLayout.add_widget(self.upcomingBubble)

    def createShootingBubble(self):
        self.bubble = Bubble(pos=(500,500)) 
        #set the shooting bubble to the same color as the upcoming previewd bubble
        self.bubble.bubbleColor = self.upcomingBubble.getColor()
        self.bubble.source = 'graphics/bubbles/' + self.bubble.getColor() + '.png'

        return self.bubble
    

    #setters and getters for the properties   TODO - put all the setters and getters here
    def setLabelText(self,label, text):
        #self.labelText.set(newText)
        label.text = str(text) 
    #def getLabelText(self):
    #    return self.labelText.get()
     
    def updatePoints(self, instance, value):
        pass
        #self.updateLabel(self.ids.pointsLbl, value)

     
    def setBubbleStartPosition(self, bubble):
        bubble.center = self.shooter.center
    '''
    def bubble_exploding(self):
        #self.app.sound['pop'].play()
        
        self.lives -= 1
        self.update_label(self.ids.livesLbl, self.lives)
        print(self.lives , 'LIIIIVES')
        #if self.lives == 0:
            #self.reset_level()
    '''

    def display_help_screen(self):
        # display the help screen on a Popup
        image = Image(source='graphics/help_screen.png')
        
        help_screen = Popup(title='Help Screen',
                            attach_to=self,
                            size_hint=(0.98, 0.98),
                            content=image)
        image.bind(on_touch_down=help_screen.dismiss)
        help_screen.open()

    

    def createBubble(self, x, y):
        b = Bubble(pos_hint={'x': x, 'center_y': y}) 
        b.setRandomColor()
        b.source = 'graphics/bubbles/' + b.getColor() + '.png'
        return b

    def createBubbleRow(self, spaces, bubblesLeft, bubblesRight, x, y):       
        bubbleSizeX =  0.08333333333333 
        
        #create bubbles to the left
        for i in range(bubblesLeft):
            b = self.createBubble(x, y)
            self.bubbleLayout.add_widget(b)
            self.bubbleList.append(b)
            x += bubbleSizeX
        
        #add empty space for the threat
        x += (bubbleSizeX * spaces)
        
        #create bubbles to right
        for i in range(bubblesRight):
            b = self.createBubble(x, y)
            self.bubbleLayout.add_widget(b)
            self.bubbleList.append(b)
            x += bubbleSizeX
    
    def createBubbleGridRow(self, numberOfBubbles):  
        if (numberOfBubbles % 2 == 1): #odd
            self.bubbleSpaceX = 0.041666666666665    
        else:
            self.bubbleSpaceX = 0
        
        #create bubbles to the left
        for i in range(numberOfBubbles):
            b = self.createBubble(self.bubbleSpaceX, self.rowspaceY)
            self.bubbleGridLayout.add_widget(b)
            self.bubbleGridList.append(b)
            self.bubbleSpaceX += self.bubble.bubbleSizeX
        
        self.rowspaceY +=self.bubble.bubbleSizeY
           
    def createThreat(self, x, y):
        #get a random threat from the list
        threatIndex = random.randint(0, len(self.threatList)-1)
        
        threat = self.threatList.pop(threatIndex)
        
        
        threat.pos_hint={'x': x, 'center_y': y}
        #b.setRandomColor()
        #t.setQuestion()
        self.bubbleLayout.add_widget(threat)

    def createObsticles(self):    

        #each block contains one threat and 3 rows of bubbles
        numberOfBlocks = 4  
        #setting procentual values for bubblesize, to be able to make the game responsive
        bubbleSizeX =  0.08333333333333 
        bubbleSizeY = 0.045
        x = 0
        y = bubbleSizeY * 10
        threatPosY = y + bubbleSizeY *1.3
        rowCount = 0
        numberOfBubbles = 12        
        xOdd = 0.041666666666665

        #the range is number of rows
        for r in range(numberOfBlocks):
            numberOfBubbles = 12
            #number of spaces that's needed for the threat to fit within the bubbles
            spaces = 3
            #set startnumber for threat
            startNumber = random.randint(1,9)

            #bubbles and posistion for first row of threat
            bubblesLeft = startNumber -1
            bubblesRight = numberOfBubbles - startNumber - spaces + 1

            #this will create 3 rows of bubbles with a threat inside at a random position
            for i in range(3): #remember! first time in range i will be equal to 0            
                #create a threat only on first row of block
                if i == 0:
                    threatPosX = (startNumber - 1) * bubbleSizeX
                     #if threat starts at an uneven row, add half a bubble of extra space on it's left
                    if (rowCount % 2 == 1): 
                        threatPosX += xOdd

                    #create a threat
                    self.createThreat(threatPosX, threatPosY)

                    #increase the y-value for the threat position
                    threatPosY += bubbleSizeY * 3
                if (rowCount % 2 == 0): #even 
                    if i == 1:  #if row is even for every fourth row then add one bubble to left, and remove one right
                        bubblesLeft += 1
                        bubblesRight -= 1
                    if i == 2: 
                        bubblesRight -= 1
                    self.createBubbleRow(spaces, bubblesLeft, bubblesRight, x, y)
                    numberOfBubbles -= 1
                else: #odd
                    if i == 2:  #if row is uneven for every third row then take one bubble off left
                        bubblesLeft -= 1                     
                    self.createBubbleRow(spaces, bubblesLeft, bubblesRight -1, xOdd, y)
                    numberOfBubbles += 1
                spaces -= 1
                #bubbles and posistion for second row of threat
                if i == 1:
                    bubblesLeft +=1
                    
                bubblesRight += 1 
                y+=bubbleSizeY
                rowCount +=1 
     
    def createBubbleGrid(self):    
            #each block contains one threat and 3 rows of bubbles
            numberOfBlocks = 6  
            numberOfBubbles = 12
            #the range is number of rows
            for i in range(numberOfBlocks):

                #set if the block should start with a row of 11 or 12 bubbles
                if (numberOfBlocks % 2 == 0): #even 
                    #STARTONEVEN 
                    self.createBubbleGridRow(numberOfBubbles)
                    self.createBubbleGridRow(numberOfBubbles-1)
                    self.createBubbleGridRow(numberOfBubbles)
                else: #odd
                    #STARTONODD
                    self.createBubbleGridRow(numberOfBubbles-1)
                    self.createBubbleGridRow(numberOfBubbles)
                    self.createBubbleGridRow(numberOfBubbles-1)        

                numberOfBlocks -= 1     
            #reverse the bubblegridList and set all the bubblepositions on the 'first' eight rows to taken (since they will be taken by the default bubbles)
            
            numberUnTakenPositions = 115
            for gridBubble in self.bubbleGridList[numberUnTakenPositions:]:
                gridBubble.posTaken = True
                gridBubble.opacity= .8
            
                #set all the bubbles that are where a threat is places to available positions
                for threat in self.threatListCopy:
                    if threat.collide_point(gridBubble.center_x , gridBubble.center_y):
                        gridBubble.posTaken = False
                        gridBubble.opacity= 0

            
          
    
    

Factory.register("Shooter", Shooter)


'''
####################################
##
##   VIEWCONTROLLER
##
####################################
'''

class MyViewController(Widget):
    
    def __init__(self, **kwargs):
        super(MyViewController, self).__init__(**kwargs)
        
        #properties of the controller 
        self.level = 1
        self.availableBubblePositions = []
        self.pointList = []

        #instantiation of view
        self.view = MyView(vc=self)
        
        #get all the Questions for the game
        self.getAllQuestions() 
        
        #load the view (this needs to be called after getting the questions)
        self.view.loadView()
        
    

#Game functions
    def fireBubble(self):

        print('FIREEEE')
        '''
        #hej = App.get_running_app()
        #hej.sound['bullet_start'].play()
        ###
        '''
        # create a bubble, calculate the start position and fire it.
        #TODO- maybe return the bubble instead
        self.bubble = self.view.createShootingBubble()

        #change the color of the upcoming bubble
        self.view.changeUpcomingBubbleColor()

        self.view.angle= radians(float(self.view.shooter.shootDirectionAngle))

        #set the bubble angle to the same as tower angle (in radiant)
        self.bubble.angle =  self.view.angle
        
        self.view.setBubbleStartPosition(self.bubble)

        #add the bullet to the correct layout
        self.view.bubbleLayout.add_widget(self.bubble)

        self.bubble.fire()

    
    def removePoints(self,instance):
        for point in self.pointList:
            print('remove point')
            self.view.bubbleLayout.remove_widget(point)

    
    #get all the questions from a json file 
    def getAllQuestions(self):

        import json
        #I took help from http://xmodulo.com/how-to-parse-json-string-in-python.html
        try:
            #get the json-file were the questions are stored
            with open('questions.json', "r") as f:
                data = json.loads(f.read())

            #get all CSRF questions
            self.addQuestionsToThreats('CSRF', data)
            
            #get all SQL-Injection questions
            self.addQuestionsToThreats('SQL-Injection', data)
            
            #need a copy of the threatList to be able to check for collision later (the original threatList is manipulated later)
            self.view.threatListCopy = list(self.view.threatList)
        except (ValueError, KeyError, TypeError):
            print "JSON format error"

    def addQuestionsToThreats(self, subject, data):
        for item in data['level' + str(self.level)][subject]:
                threat = Threat()
                threat.title = subject
                threat.question = item['question']
                threat.answers = item['answers']
                threat.correctAnswer = str(item['correctAnswer'])
                threat.imageSrc = 'graphics/threats/threat.png' #+ b.getColor() + '.png'
                print(threat.question)
                self.view.threatList.append(threat)

    def removeOrKeepBubbles(self):
        #check if it targeted the same color/s and if so, remove the bubble itself.
        matches = self.bubble.findColorMatches()
        if len(matches) >= 3:
            self.bubble.removeColorMatches()
            #set the bubblespace in grid to available
            self.posTaken = False
            #add bubble to gridList 
            self.view.bubbleGridList.append(self)               

            for bubble in matches:
                b = Bubble()
                b.source = 'graphics/points.png'
                b.pos_hint = bubble.pos_hint
                self.view.bubbleLayout.add_widget(b) 
                self.pointList.append(b)
            
            #delete the recently fired bubble
            self.view.bubbleLayout.remove_widget(self.bubble) 
            Clock.schedule_once(self.removePoints, 0.2)
        else: 
            #add bubble to the list of bubbles 
            self.view.bubbleList.append(self.bubble)

    def calculateAvailableBubblePositions(self):
        self.availableBubblePositions = []
        if not len(self.view.bubbleGridList) == 0:
            for gridBubble in self.view.bubbleGridList[::-1]: #start from the last added bubble
                if not gridBubble.posTaken:
                    self.availableBubblePositions.append(gridBubble)

    
    def fitBubbleToGrid(self):
        print('FIIINTTTIING?!?!?!?')
        bubblesToCompareList = []
        distancesToCompareList = []
        self.calculateAvailableBubblePositions()
        for b in self.availableBubblePositions:
            #get the distance of the closest gridBubbles to the bubble
            distance = self.bubble.getGridBubbleDistance(b)
            b.distanceToClostestGridBubble = distance
            
            #if the distance is close enough we have a potential position for the bubble, add this gridBubble to a list
            if b.distanceToClostestGridBubble > 0: 

                bubblesToCompareList.append(b)
                distancesToCompareList.append(b.distanceToClostestGridBubble)

        #just need to see which of the nearby gridBubbles that are the closest one, and set the bubble position to that 
        if not len(distancesToCompareList) == 0:
            smallestDistance = min(distancesToCompareList)       
            for b in bubblesToCompareList:

                if b.distanceToClostestGridBubble == smallestDistance:

                    print(b.pos_hint , 'b.pos_hint ')
                    self.bubble.pos_hint = b.pos_hint              

                    #set the bubble as taken! 
                    if b in self.view.bubbleGridList[::-1]:
                        print('iT*S INSEDE THE GRID YOOO')
                        b.posTaken = True


'''
#Handlers -- target action

    #when quit is pressed 
    def close(self):
        App.get_running_app().stop()
        raise SystemExit(0)

    #when display help screen is pressed
    def welcome_screen(self):
        self.root.display_help_screen()  
    def addPressed(self):
'''

# huvudklassen för applikationen, detta är med andra ord den kod som körs när applikationen byggs och blir huvudcontainern där alla widgetar placeras. 


#Huvudklassen som bygger applicationen och returnerar MainWidget
class DbShooter(App):
	
    def build(self):

        self.sound = {}
        self.title = 'DB Shooter'      
	    
        from kivy.base import EventLoop
        EventLoop.ensure_window()
        self.window = EventLoop.window

        '''
        # create the root widget and give it a reference of the application instance (so it can access the application settings)
        self.DbShooterWidget = DbShooterWidget(app=self)
        self.root = self.DbShooterWidget
        '''

        self.MyViewController = MyViewController(app=self)

        self.root = self.MyViewController.view
        #self.root.bind(points=self.root.updatePoints)
        

        # load all other sounds:
        #self.sound['pop'] = SoundLoader.load('sound/pop.mp3')
        #self.sound['bullet_start'] = SoundLoader.load('sound/bullet_start.mp3')
        
        #self.welcome_screen()

     
    def build_config(self, config):
        config.adddefaultsection('General')
        config.setdefault('General', 'Music', '100')
        config.setdefault('General', 'Sound', '100')
        config.setdefault('General', 'FirstStartup', 'Yes')
        
        config.adddefaultsection('GamePlay')
        config.setdefault('GamePlay', 'BubbleSpeed', '10')
        config.setdefault('GamePlay', 'Levels', '2')

      


#Kör applikationen
if __name__ == "__main__":	
	DbShooter().run()