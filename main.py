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
from kivy.utils import boundary
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.core.audio import SoundLoader
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.clock import Clock
import time
import webbrowser

from math import sin
from math import cos
from math import radians
import random

from shooter import Shooter
from bubble import Bubble
from threat import Threat

#sätter storleken för huvudfönstret:
Window.size = 560, 836


'''
####################################
##
##   VIEW
##
####################################
'''
class MyView(Widget):
    #properties that has to be accessed in the .kv file are placed outside of the constructor
    lives = NumericProperty(5)
    level = 1
    points = NumericProperty(0)

    #def __init__(self,vc):
    def __init__(self, vc=None, **kwargs):
        super(MyView, self).__init__(**kwargs)
        
        #properties of the view 
        self.app = App.get_running_app()
        self.vc = vc
        self.settingsPopup = None
        self.settingsPopupDismissed = False
        self.bubble = None
        self.upcomingBubble = None
        self.angle = NumericProperty()
        self.rowspaceY = 0
        self.bubbleSpaceX = 0
        self.bubbleList = []
        self.bubbleGridList = []
        self.threatList = []
        self.threatListCopy = []
       
    
    #loading the view (called in the controller)
    def loadView(self):
        self.bubble = Bubble()

        #create all the bubbles and threats for the startup
        self.createObsticles()

        #create the grid for the bubbles to fit in
        self.createBubbleGrid()

        #add the first upcoming bubble to the view
        self.addUpcomingBubbletoView()

    def resetView(self):
        self.bubbleList = []
        print( 'LEN CHILDREN', len(self.bubbleLayout.children))
        self.bubbleLayout.clear_widgets()
        self.createObsticles()
        self.setTakenPositions()
        self.nextBubbleLayout.clear_widgets()
        self.addUpcomingBubbletoView()


    def changeUpcomingBubbleColor(self):
        self.upcomingBubble.setRandomColor()
        self.upcomingBubble.source = 'graphics/bubbles/' + self.upcomingBubble.getColor() + '.png'


    def addUpcomingBubbletoView(self):
        self.upcomingBubble = self.createBubble(0,0)
        self.upcomingBubble.pos_hint={'x': 0.55, 'center_y': .5}
        #add the upcomingBubble to the preview-window
        self.nextBubbleLayout.add_widget(self.upcomingBubble)

    def createFiredBubble(self):
        self.bubble = Bubble(pos=(500,500)) 
        #set the shooting bubble to the same color as the upcoming previewd bubble
        self.bubble.bubbleColor = self.upcomingBubble.getColor()
        self.bubble.source = 'graphics/bubbles/' + self.bubble.getColor() + '.png'
        return self.bubble
    

    #setters and getters for the properties  
    
    def setLevel(self, value):
        self.level = value
     
    def setPoints(self, value):
        self.points += value

    def getPoints(self, value): #TODO - not using this?
        return self.points

    def setLives(self, value):
        self.lives += value
     
    def setBubbleStartPosition(self, bubble):
        bubble.center = self.shooter.center

    # popups
    def displaySettingsScreen(self):
        #self.app.sound['switch'].play()
        self.settingsPopupDismissed = False
        # the first time the setting dialog is called, initialize its content.
        if self.settingsPopup is None:
            
            self.settingsPopup = Popup(attach_to=self,
                                       title= 'DBShooter Settings'
                                       )
                      
            self.settingDialog = SettingDialog(root=self)
            
            self.settingsPopup.content = self.settingDialog
            
            self.settingDialog.music_slider.value = boundary(self.app.config.getint('General', 'Music'), 0, 100)
            self.settingDialog.sound_slider.value = boundary(self.app.config.getint('General', 'Sound'), 0, 100)
            
        self.settingsPopup.open()


    def displayHelpScreen(self):
        # display the help screen on a Popup
        image = Image(source='graphics/help_screen.png')
        
        help_screen = Popup(title='Help Screen',
                            attach_to=self,
                            size_hint=(0.98, 0.98),
                            content=image)
        image.bind(on_touch_down=help_screen.dismiss)
        help_screen.open()

    def displayLifeIsLostScreen(self):
        lifeIsLostScreen = Popup( title='Life is lost', auto_dismiss=False,
                            attach_to=self,
                            size_hint=(None,None), pos_hint={'center_x': 0.5, 'center_y': .6} 
                            )
        layout = BoxLayout(orientation = 'vertical')
        image = Image(source='graphics/lifeLost.png', pos_hint={'center_x': 0.5, 'center_y': 0.4})
        layout.add_widget(image)
        lifeIsLostScreen.content = layout
        lifeIsLostScreen.open()
        Clock.schedule_once(lifeIsLostScreen.dismiss, 1.5)
        Clock.schedule_once(self.removeLife, 1.6)

    def removeLife(self, instance):
        self.setPoints(-self.points)
        self.setLives(-1)


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
        if len(self.threatList) > 0:
            #get a random threat from the list
            threatIndex = random.randint(0, len(self.threatList)-1)
            
            threat = self.threatList.pop(threatIndex)
            threat.pos_hint={'x': x, 'center_y': y}
            #b.setRandomColor()
            #t.setQuestion()
            self.bubbleLayout.add_widget(threat)
            print('THREAT.POS YO', threat.pos)
            self.threatListCopy.append(threat)

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
                    threatPosX = (startNumber - 1) * bubbleSizeX + 0.005
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
            
            self.setTakenPositions()


    def setTakenPositions(self):       
            numberUnTakenPositions = 115
            #reverse the bubblegridList and set all the bubblepositions on the 'first' eight rows to taken (since they will be taken by the default bubbles)
            for gridBubble in self.bubbleGridList[numberUnTakenPositions:]:
                gridBubble.posTaken = True
                gridBubble.opacity= .8
                #set all the bubbles that are where a threat is places to available positions
                for threat in self.threatListCopy:
                    #print('POSITION THREAT: ', threat.pos, 'POSITION GRIDBUBBLE: ', gridBubble.pos)
                    if threat.collide_point(gridBubble.center_x , gridBubble.center_y):
                        #print('butWAI taken')
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
        self.app = App.get_running_app()
        self.level = 1
        self.availableBubblePositions = []
        self.pointList = []

        #instantiation of view
        self.view = MyView(vc=self)
        
        #get all the Questions for the game
        self.getAllQuestions() 
        
        #load the view (this needs to be called after getting the questions)
        self.view.loadView()

        self.view.bind(points=self.checkPoints)
        self.view.bind(lives=self.checkLives)
           

    def fireBubble(self):

        print('******************** FIREEEE ********************')
        '''
        #hej = App.get_running_app()
        #hej.sound['bullet_start'].play()
        ###
        '''
        # create the shooting bubble
        self.bubble = self.view.createFiredBubble()

        #change the color of the upcoming bubble
        self.view.changeUpcomingBubbleColor()

        self.view.angle= radians(float(self.view.shooter.shootDirectionAngle))

        #set the bubble angle to the same as shooter angle (in radians)
        self.bubble.angle =  self.view.angle
        
        #calculate the start position
        self.view.setBubbleStartPosition(self.bubble)

        #add the bubble to the correct layout
        self.view.bubbleLayout.add_widget(self.bubble)

        self.bubble.fire()

    def checkPoints(self,instance, value):
        if value < 0:
            self.view.displayLifeIsLostScreen()


    def checkLives(self,instance,value):
        #if lives goes out, reset the level
        if value < 5:
            print('*******VALUE BELLOWOWOWO')
            self.resetLevel(self.level)
            

    #get all the questions from a json file 
    def getAllQuestions(self):

        import json
        #I took a little help from http://xmodulo.com/how-to-parse-json-string-in-python.html
        try:
            #get the json-file were the questions are stored
            with open('questions.json', "r") as f:
                data = json.loads(f.read())

            #get all CSRF questions
            self.addQuestionsToThreats('CSRF', data)
            
            #get all SQL-Injection questions
            self.addQuestionsToThreats('SQL-Injection', data)

            #get all SQL-Injection questions
            self.addQuestionsToThreats('XSS', data)
            

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


    def resetLevel(self, level):
        print('VIIIIIIIIIIIIIIIW',self.view)
        self.view.threatList = []
        self.view.threatListCopy = []
        self.getAllQuestions()

        self.view.resetView()
        #self.level = 6



    #this function is called from inside the bubble (I couldn't find another solution since it has to be executed exactly when the animation is completed)
    def removeOrKeepBubbles(self, instance):
        #check if it targeted the same color/s and if so, remove the bubble itself.
        firstColorMatches = self.bubble.findClosestColorMatches()
        #print('FIRST COLORMATCHES', len(firstColorMatches))
        allColorMatches = self.bubble.findAllRelatedColorMatches(firstColorMatches)

        #if there's only one match the bubble needs to be re-added to the bubbleList (since it's being removed in the findAllRelatedColorMatches function)
        if len(allColorMatches) == 1:
            self.view.bubbleList.append(allColorMatches[0])
        #don't forget to add the recently fired bubble since allColorMaches only contains the matches for the fired bubble
        allColorMatches.append(self.bubble)
        print('ALL COLOR MATCHES', len(allColorMatches))
        if len(allColorMatches) >= 3:
            
            #delete all the color matches including the recently fired bubble
            for bubble in allColorMatches:
                bubble.posTaken = False
                #add bubble to gridList 
                self.view.bubbleGridList.append(bubble)

                #replace the bubble with a points-picture and remove it
                bubble.changeToPointsPicture()
                bubble.animatePointsPicture()
                 
        else: 
            print('it does add the bubble to the bubblelist')
            #add bubble to the list of bubbles 
            self.view.bubbleList.append(self.bubble)
            print(len(self.view.bubbleList))
            #set the bubblespace in grid to available
            self.posTaken = False
            #add bubble to gridList 
            self.view.bubbleGridList.append(self.bubble)  

    #TODO - maybe move findAvailableBubblePositions and fitBubbleToGrid back to the bubbleclass....
    def findAvailableBubblePositions(self):
        self.availableBubblePositions = []
        if not len(self.view.bubbleGridList) == 0:
            for gridBubble in self.view.bubbleGridList[::-1]: #start from the last added bubble
                if not gridBubble.posTaken:
                    self.availableBubblePositions.append(gridBubble)

    #this function is called from inside the bubble (I couldn't find another solution since it has to be executed when the animation is completed)
    def fitBubbleToGrid(self):
        bubblesToCompareList = []
        distancesToCompareList = []
        self.findAvailableBubblePositions()
        for b in self.availableBubblePositions:
            #get the distance of the closest gridBubbles to the bubble
            distance = self.bubble.getGridBubbleDistance(b)
            b.distanceToClostestGridBubble = distance
            
            #if the distance is close enough we have a potential position for the bubble, add this gridBubble to a list
            if b.distanceToClostestGridBubble > 0: 

                bubblesToCompareList.append(b)
                distancesToCompareList.append(b.distanceToClostestGridBubble)

        #checks which one of the nearby gridBubbles that are the closest, and sets the recently fired bubble position to it 
        if not len(distancesToCompareList) == 0:
            smallestDistance = min(distancesToCompareList)       
            for b in bubblesToCompareList:

                if b.distanceToClostestGridBubble == smallestDistance:
                    self.bubble.pos_hint = b.pos_hint     
                    print('THE BUBBLE IS AT IT\'S RIGHT PLACE IN THE GRID, now do colormatches')         
                    #set the bubble as taken! 
                    if b in self.view.bubbleGridList[::-1]:
                        b.posTaken = True
            return True
        return False


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
'''
####################################
##
##   Setting Dialog Class
##
####################################
'''
class SettingDialog(Widget):
    music_slider = ObjectProperty(None)
    sound_slider = ObjectProperty(None)
    
    root = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(SettingDialog, self).__init__(**kwargs)
        #TODO- uncomment this
        #self.music_slider.bind(value=self.updateMusicVolume)
        #self.sound_slider.bind(value=self.updateSoundVolume)
    
    def updateMusicVolume(self, instance, value):
        # write to app configs
        self.root.app.config.set('General', 'Music', str(int(value)))
        self.root.app.config.write()
        self.root.app.music.volume = value / 100.0
    
    def updateSoundVolume(self, instance, value):
        # write to app configs
        self.root.app.config.set('General', 'Sound', str(int(value)))
        self.root.app.config.write()
        for item in self.root.app.sound:
            self.root.app.sound[item].volume = value / 100.0
    
    def displayHelpScreen(self):
        #self.root.settingsPopup.dismiss()
        self.root.displayHelpScreen()
    
    def dismissSettingsDialog(self):
        self.root.settingsPopupDismissed = True
        self.root.settingsPopup.dismiss()

    def redirectToHyperLink(self):
        webbrowser.open("http://kivy.org/")
    

'''
####################################
##
##   Main Application Class
##
####################################
'''
class DbShooter(App):
	
    def build(self):
        self.sound = {}
        self.title = 'DB Shooter'      
	    
        from kivy.base import EventLoop
        EventLoop.ensure_window()
        self.window = EventLoop.window

        # start the background music:
        #self.music = SoundLoader.load('sound/background.mp3')
        #self.music.volume = self.config.getint('General', 'Music') / 100.0
        #self.music.bind(on_stop=self.replaySound)
        #self.music.play()


        # create the root widget and give it a reference of the view / application instance 
        self.MyViewController = MyViewController(app=self)
        self.root = self.MyViewController.view        

        # load all other sounds:
        #self.sound['pop'] = SoundLoader.load('sound/pop.mp3')
        #self.sound['bullet_start'] = SoundLoader.load('sound/bullet_start.mp3')
        
        #self.welcome_screen()

        # if the user started the game the first time, display quick start guide
        if self.config.get('General', 'FirstStartup') == 'Yes':
            
            #Clock.schedule_once(self.welcome_screen, 2)
            
            self.config.set('General', 'FirstStartup', 'No')
            self.config.write()
     
    def build_config(self, config):
        config.adddefaultsection('General')
        config.setdefault('General', 'Music', '100')
        config.setdefault('General', 'Sound', '100')
        config.setdefault('General', 'FirstStartup', 'Yes')

    def replaySound(self, instance):
        if self.music.status != 'play':
            self.music.play()


#Run the application
if __name__ == "__main__":	
	DbShooter().run()