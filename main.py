# -*- coding: utf-8 -*-
# Inlämningsuppgift, Maria Nygren
# Plattform: Windows 8.1
# Python version 3.4.3
# kivy 1.9.0 (http://kivy.org/# home) - http://www.lfd.uci.edu/~gohlke/pythonlibs/# kivy

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

# sätter storleken för huvudfönstret:
Window.size = 600, 836


'''
####################################
##
##  VIEW
##
####################################
'''
class MyView(Widget):
    # properties that needs to be accessed in the .kv file are placed outside of the constructor
    lives = NumericProperty(5)
    level = NumericProperty(1)
    points = NumericProperty(0)
    layoutPositionY = NumericProperty(0)

    # def __init__(self,vc):
    def __init__(self, vc=None, **kwargs):
        super(MyView, self).__init__(**kwargs)
        
        # properties of the view 
        self.app = App.get_running_app()
        self.vc = vc
        self.settingsPopup = None
        self.helpPopup = None
        self.settingsPopupDismissed = False
        self.helpPopupDismissed = False
        self.bubble = None
        self.upcomingBubble = None
        self.angle = NumericProperty()
        self.rowspaceY = 0
        self.bubbleSpaceX = 0
        self.bubbleList = []
        self.bubbleGridList = []
        self.threatList = []
        self.threatListCopy = []
        self.layoutPositionY = self.y + (self.height * 1.5) # * (0.045 * 4.6) 
        self.startPositionY =   self.y + (self.height * 1.5)
        self.stepsMovedDown = NumericProperty()
       
    
    # loading the view (called in the controller)
    def loadView(self):
        self.bubble = Bubble()
        # create all the bubbles and threats for the startup
        self.createObsticles()

        # create the grid for the bubbles to fit in
        self.createBubbleGrid()

        # set the bubbles in the grid to taken if there's an bubble in it's place
        self.setTakenGridPositions()

        # add the first upcoming bubble to the view
        self.addUpcomingBubbletoView()

    def resetView(self):
        self.layoutPositionY = self.startPositionY 
        self.bubble = None
        self.rowspaceY = 0
        self.bubbleSpaceX = 0
        self.bubbleList = []
        self.bubbleGridList = []
        self.bubbleLayout.clear_widgets()
        self.bubbleGridLayout.clear_widgets()
        self.nextBubbleLayout.clear_widgets()

        self.loadView()
        self.points = 0
        self.lives = 5
        self.level = 1       

    def changeUpcomingBubbleColor(self):
        self.upcomingBubble.setRandomColor()
        self.upcomingBubble.source = 'graphics/bubbles/' + self.upcomingBubble.getColor() + '.png'


    def addUpcomingBubbletoView(self):
        self.upcomingBubble = self.createBubble(0,0)
        self.upcomingBubble.pos_hint={'x': 0.55, 'center_y': .5}
        # add the upcomingBubble to the preview-window
        self.nextBubbleLayout.add_widget(self.upcomingBubble)

    def createFiredBubble(self):
        self.bubble = Bubble(pos=(500,500)) 
        # set the shooting bubble to the same color as the upcoming previewd bubble
        self.bubble.bubbleColor = self.upcomingBubble.getColor()
        self.bubble.source = 'graphics/bubbles/' + self.bubble.getColor() + '.png'
        return self.bubble
    

    # setters and getters for the properties  
    
    def setLevel(self, value):
        self.level = value
     
    def setPoints(self, value):
        self.points += value

    def getPoints(self, value): # TODO - not using this?
        return self.points

    def setLives(self, value):
        self.lives += value
     
    def setBubbleStartPosition(self, bubble):
        bubble.center = self.shooter.center

    # popups
    def displaySettingsScreen(self):
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
        self.helpPopupDismissed = False
        if self.helpPopup is None:
            self.helpPopup = Popup(title = 'Rules', attach_to=self)
                      
            self.helpContent = HelpScreen(root=self)
            
            self.helpPopup.content = self.helpContent
            
            
        self.helpPopup.open()

    #TODO - make one standard popup for theese and just change the title and image!  to remove DRY (Had no time to do this)
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
        Clock.schedule_once(lifeIsLostScreen.dismiss, 2.5)
        Clock.schedule_once(self.removeLife, 2.6)

    def displayGameOverScreen(self):
        gameOverScreen = Popup( title='Game Over!', auto_dismiss=False,
                            attach_to=self,
                            size_hint=(None,None), pos_hint={'center_x': 0.5, 'center_y': .6} 
                            )
        layout = BoxLayout(orientation = 'vertical')
        image = Image(source='graphics/gameOver.png', pos_hint={'center_x': 0.5, 'center_y': 0.4})
        layout.add_widget(image)
        gameOverScreen.content = layout
        gameOverScreen.open()
        Clock.schedule_once(gameOverScreen.dismiss, 2.5)

    def displayCollisionScreen(self):
        collisionScreen = Popup( title='Collision!', auto_dismiss=False,
                            attach_to=self,
                            size_hint=(None,None), pos_hint={'center_x': 0.5, 'center_y': .6} 
                            )
        layout = BoxLayout(orientation = 'vertical')
        image = Image(source='graphics/onCollision.png', pos_hint={'center_x': 0.5, 'center_y': 0.4})
        layout.add_widget(image)
        collisionScreen.content = layout
        collisionScreen.open()
        Clock.schedule_once(collisionScreen.dismiss, 2.5)     

    def displayVictoryScreen(self):
        victoryScreen = Popup( title='EPIC WIN!', auto_dismiss=True,
                            attach_to=self,
                            size_hint=(None,None), pos_hint={'center_x': 0.5, 'center_y': .6} 
                            )
        layout = BoxLayout(orientation = 'vertical')
        image = Image(source='graphics/victory.png', pos_hint={'center_x': 0.5, 'center_y': 0.4})
        layout.add_widget(image)
        victoryScreen.content = layout
        victoryScreen.open()     

    def removeLife(self, instance):
        self.setPoints(-self.points)
        self.setLives(-1)

    def moveDownAllBubbles(self): 
        newPosition = self.layoutPositionY - (self.height * 0.045) 
        self.layoutPositionY = newPosition

    def createBubble(self, x, y):
        b = Bubble(pos_hint={'x': x, 'center_y': y}) 
        b.setRandomColor()
        b.source = 'graphics/bubbles/' + b.getColor() + '.png'
        return b

    def createBubbleRow(self, spaces, bubblesLeft, bubblesRight, x, y):       
        bubbleSizeX =  0.08333333333333 
        
        # create bubbles to the left
        for i in range(bubblesLeft):
            b = self.createBubble(x, y)
            self.bubbleLayout.add_widget(b)
            self.bubbleList.append(b)
            x += bubbleSizeX
        
        # add empty space for the threat
        x += (bubbleSizeX * spaces)
        
        # create bubbles to right
        for i in range(bubblesRight):
            b = self.createBubble(x, y)
            self.bubbleLayout.add_widget(b)
            self.bubbleList.append(b)
            x += bubbleSizeX
    
    def createBubbleGridRow(self, numberOfBubbles):  
        if (numberOfBubbles % 2 == 1): # odd
            self.bubbleSpaceX = 0.041666666666665    
        else:
            self.bubbleSpaceX = 0
        
        # create bubbles to the left
        for i in range(numberOfBubbles):
            b = self.createBubble(self.bubbleSpaceX, self.rowspaceY)
            self.bubbleGridLayout.add_widget(b)
            self.bubbleGridList.append(b)
            self.bubbleSpaceX += self.bubble.bubbleSizeX
        
        self.rowspaceY +=self.bubble.bubbleSizeY
           
    def createThreat(self, x, y):
        if len(self.threatList) > 0:
            # get a random threat from the list
            threatIndex = random.randint(0, len(self.threatList)-1)            
            threat = self.threatList.pop(threatIndex)
            threat.pos_hint={'x': x, 'center_y': y}
            # b.setRandomColor()
            self.bubbleLayout.add_widget(threat)
            self.threatListCopy.append(threat)

    def createObsticles(self):    

        # each block contains one threat and 3 rows of bubbles
        numberOfBlocks = 6  
        # setting procentual values for bubblesize, to be able to make the game responsive
        bubbleSizeX =  0.08333333333333 
        bubbleSizeY = 0.045
        x = 0
        y = bubbleSizeY * 10
        threatPosY = y + bubbleSizeY *1.3
        rowCount = 0
        numberOfBubbles = 12        
        xOdd = 0.041666666666665

        # the range is number of rows
        for r in range(numberOfBlocks):
            numberOfBubbles = 12
            # number of spaces that's needed for the threat to fit within the bubbles
            spaces = 3
            # set startnumber for threat
            startNumber = random.randint(1,9)

            # bubbles and posistion for first row of threat
            bubblesLeft = startNumber -1
            bubblesRight = numberOfBubbles - startNumber - spaces + 1

            # this will create 3 rows of bubbles with a threat inside at a random position
            for i in range(3): # remember! first time in range i will be equal to 0            
                # create a threat only on first row of block
                if i == 0:
                    threatPosX = (startNumber - 1) * bubbleSizeX + 0.005
                     # if threat starts at an uneven row, add half a bubble of extra space on it's left
                    if (rowCount % 2 == 1): 
                        threatPosX += xOdd

                    # create a threat
                    self.createThreat(threatPosX, threatPosY)

                    # increase the y-value for the threat position
                    threatPosY += bubbleSizeY * 3
                if (rowCount % 2 == 0): # even 
                    if i == 1:  # if row is even for every fourth row then add one bubble to left, and remove one right
                        bubblesLeft += 1
                        bubblesRight -= 1
                    if i == 2: 
                        bubblesRight -= 1
                    self.createBubbleRow(spaces, bubblesLeft, bubblesRight, x, y)
                    numberOfBubbles -= 1
                else: # odd
                    if i == 2:  # if row is uneven for every third row then take one bubble off left
                        bubblesLeft -= 1                     
                    self.createBubbleRow(spaces, bubblesLeft, bubblesRight -1, xOdd, y)
                    numberOfBubbles += 1
                spaces -= 1
                # bubbles and posistion for second row of threat
                if i == 1:
                    bubblesLeft +=1
                    
                bubblesRight += 1 
                y+=bubbleSizeY
                rowCount +=1 
     
    def createBubbleGrid(self):    
            # each block contains one threat and 3 rows of bubbles
            numberOfBlocks = 10  # needs to be even  
            numberOfBubbles = 12
            # the range is number of rows
            for i in range(numberOfBlocks):

                # set if the block should start with a row of 11 or 12 bubbles
                if (numberOfBlocks % 2 == 0): # even 
                    # STARTONEVEN 
                    self.createBubbleGridRow(numberOfBubbles)
                    self.createBubbleGridRow(numberOfBubbles-1)
                    self.createBubbleGridRow(numberOfBubbles)
                else: # odd
                    # STARTONODD
                    self.createBubbleGridRow(numberOfBubbles-1)
                    self.createBubbleGridRow(numberOfBubbles)
                    self.createBubbleGridRow(numberOfBubbles-1)        

                numberOfBlocks -= 1    

    def setTakenGridPositions(self):       
        for gridBubble in self.bubbleGridList:
            gridBubble.posTaken = False
            for bubble in self.bubbleList:
                if gridBubble.pos_hint == bubble.pos_hint:
                    gridBubble.posTaken = True
       

'''
####################################
##
##  VIEWCONTROLLER
##
####################################
'''
class MyViewController(Widget):
    # misses property needs to be up here so kivy can bind it in the constructor
    misses = NumericProperty(0)
    lowestBubblePositionY = NumericProperty(0)

    def __init__(self, **kwargs):
        super(MyViewController, self).__init__(**kwargs)
        
        # properties of the controller 
        self.app = App.get_running_app()
        self.level = 1
        self.availableBubblePositions = []
        self.pointList = []

        # instantiation of view
        self.view = MyView(vc=self)
        
        # get all the Questions for the game
        self.getAllQuestions() 
        
        # load the view (this needs to be called after getting the questions)
        self.view.loadView()

        self.view.bind(points=self.checkPoints)
        self.view.bind(points=self.checkGameStatus)
        self.view.bind(lives=self.checkLives)
        self.bind(misses = self.moveDownAllBubbles)
        self.bind(lowestBubblePositionY = self.checkCollideWithDatabase)
        

    def fireBubble(self):
        # create the shooting bubble
        self.bubble = self.view.createFiredBubble()

        # change the color of the upcoming bubble
        self.view.changeUpcomingBubbleColor()

        self.view.angle= radians(float(self.view.shooter.shootDirectionAngle))

        # set the bubble angle to the same as shooter angle (in radians)
        self.bubble.angle =  self.view.angle
        
        # calculate the start position
        self.view.setBubbleStartPosition(self.bubble)

        # add the bubble to the correct layout
        self.view.bubbleLayout.add_widget(self.bubble)

        self.bubble.fire()

    def checkPoints(self,instance, value):
        if value < 0:
            self.view.displayLifeIsLostScreen()

    def checkGameStatus(self, instance, value):
        #check if all threats are removed, if so the user won!  
        if len(self.view.threatListCopy) == 0:
            self.view.displayVictoryScreen() #Todo- should move up a level but I didn't have time to implement this
            self.resetLevel(self.level)

    def checkLives(self,instance,value):
        # if lives goes out, reset the level
        if value < 1:
            # Game Over! 
            self.view.displayGameOverScreen()
            self.resetLevel(self.level)

    def checkCollideWithDatabase(self, instance, value):
        collidePointTable = self.view.dbImage.top - self.view.shooter.height
        collidePointShooter = self.view.shooter.pos
        if value < collidePointTable:
            print('collided with table') #Todo - if time, add functionality here
    
    def checkCollistionWithShooter(self):
        # checks if a bubble or threat collides with the shooter
        collision = False
        for bubble in self.view.bubbleList:
            if bubble.collide_widget(self.view.shooter):               
                collision= True
                break

        for threat in self.view.threatListCopy:
            if threat.collide_widget(self.view.shooter):               
                collision= True
                break
        if collision:
            # keep points/lives if needed, then end game or reset scene
            currentLives = self.view.lives
            if currentLives -1 == 0:
                # Game over
                self.view.displayGameOverScreen()
                self.resetLevel(self.level)
            else:
                self.view.displayCollisionScreen()
                currentPoints = self.view.points
                self.resetLevel(self.level)
                self.view.lives = currentLives - 1
                self.view.points = currentPoints


    # get all the questions from a json file 
    def getAllQuestions(self):

        import json 
        try:
            # get the json-file were the questions are stored
            with open('questions.json', "r") as f:
                data = json.loads(f.read())

            # get all CSRF questions
            self.addQuestionsToThreats('CSRF', data)
            
            # get all SQL-Injection questions
            self.addQuestionsToThreats('SQL-Injection', data)

            # get all SQL-Injection questions
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
                threat.imageSrc = 'graphics/threats/threat.png' # + b.getColor() + '.png'
                self.view.threatList.append(threat)

    def resetLevel(self, level):
        if self.view.settingsPopup:
            self.view.settingsPopup.dismiss()
        self.view.threatList = []
        self.view.threatListCopy = []
        self.getAllQuestions()
        self.view.resetView()


    # this function is called from inside the bubble (I couldn't find another solution since it has to be executed exactly when the animation is completed)
    def removeOrKeepBubbles(self, instance):
        # check if it targeted the same color/s and if so, remove the bubble itself.
        firstColorMatches = self.bubble.findClosestColorMatches()
        allColorMatches = self.bubble.findAllRelatedColorMatches(firstColorMatches)

        # if there's only one match the bubble needs to be re-added to the bubbleList (since it's being removed in the findAllRelatedColorMatches function)
        if len(allColorMatches) == 1:
            self.view.bubbleList.append(allColorMatches[0])
        # don't forget to add the recently fired bubble since allColorMaches only contains the matches for the fired bubble
        allColorMatches.append(self.bubble)
        if len(allColorMatches) >= 3:           
            # delete all the color matches including the recently fired bubble
            for bubble in allColorMatches:
                # set the bubble in grid to available 
                for b in self.view.bubbleGridList:
                    if bubble.pos_hint == b.pos_hint:
                        b.posTaken = False
                
                # replace the bubble with a points-picture and remove it
                bubble.changeToPointsPicture()
                bubble.animatePointsPicture()

                self.app.sound['popping'].play()

            # check if any bubble collides with the shooter
            self.checkCollistionWithShooter()
        else: 
            # add bubble to the list of bubbles 
            self.view.bubbleList.append(self.bubble)
            # add one miss to the list of misses
            self.misses += 1

            # set the bubble in grid to taken 
            for b in self.view.bubbleGridList:
                if self.bubble.pos_hint == b.pos_hint:
                    self.bubble.posTaken = True
            
            # update/set the lowestbubblePosition  #TODO - don't really want to call these functions from here, move them later if there's time. 
            self.setlowestBubblePositionY()
        

        Clock.schedule_once(self.checkForLonelyBubbles, 0.2)
    
    def checkForLonelyBubbles(self, instance):
        # check if there is any 'lonely' bubbles (that is not attached to any other bubbles)
            for bubble in self.view.bubbleList:
                surroundingBubbles = bubble.findSurroundingBubbles()
                if len(surroundingBubbles) == 0:
                    for b in self.view.bubbleGridList:
                        if bubble.pos_hint == b.pos_hint:
                            b.posTaken = False
                            # remove it from the bubbleList
                            for bl in self.view.bubbleList:
                                if bl.pos_hint == bubble.pos_hint:
                                    self.view.bubbleList.remove(bl)
                            # replace the bubble with a points-picture and remove it
                            bubble.changeToPointsPicture()
                            bubble.animatePointsPicture()         

    def setlowestBubblePositionY(self):
        posList = []
        for bubble in self.view.bubbleList:
            posList.append(bubble.y)       
        self.lowestBubblePositionY = min(posList)


    # TODO - maybe move findAvailableBubblePositions and fitBubbleToGrid back to the bubbleclass....
    def findAvailableBubblePositions(self):
        self.availableBubblePositions = []
        if not len(self.view.bubbleGridList) == 0:
            for gridBubble in self.view.bubbleGridList[::-1]: # start from the last added bubble
                if not gridBubble.posTaken:
                    self.availableBubblePositions.append(gridBubble)

    # this function is called from inside the bubble (I couldn't find another solution since it has to be executed when the animation is completed)
    def fitBubbleToGrid(self):
        bubblesToCompareList = []
        distancesToCompareList = []
        self.findAvailableBubblePositions()
        for b in self.availableBubblePositions:
            # get the distance of the closest gridBubbles to the bubble
            distance = self.bubble.getGridBubbleDistance(b)
            b.distanceToClostestGridBubble = distance
            
            # if the distance is close enough we have a potential position for the bubble, add this gridBubble to a list
            if b.distanceToClostestGridBubble > 0: 

                bubblesToCompareList.append(b)
                distancesToCompareList.append(b.distanceToClostestGridBubble)

        # checks which one of the nearby gridBubbles that are the closest, and sets the recently fired bubble position to it 
        if not len(distancesToCompareList) == 0:
            smallestDistance = min(distancesToCompareList)       
            for b in bubblesToCompareList:

                if b.distanceToClostestGridBubble == smallestDistance:
                    self.bubble.pos_hint = b.pos_hint          
                    # set the bubble as taken! 
                    if b in self.view.bubbleGridList[::-1]:
                        b.posTaken = True
                    self.app.sound['pop'].play()
            return True
        return False

    def moveDownAllBubbles(self, instance, value):
        if value > 4: 
           self.view.moveDownAllBubbles()
           self.misses = 0

        self.checkCollistionWithShooter()

# Handlers 
    # when quit is pressed 
    def close(self, instance):
        App.get_running_app().stop()
        raise SystemExit(0)

    def confirmClose(self):
        quitScreen = Popup( title='Quit Application', auto_dismiss=False,
                            attach_to=self,
                            size_hint=(None,None), pos_hint={'center_x': 0.5, 'center_y': .6}
                            )

        layout = BoxLayout(orientation = 'vertical')
        innerLayout = BoxLayout(size_hint_y = 0.2)
        l = Label(text='Are you sure you want to quit?',  size_hint_y = 0.8)
        layout.add_widget(l)
        btn = Button(text = 'Yes', on_press = self.close)
        btn2 = Button(text = 'No', on_press = quitScreen.dismiss)
        innerLayout.add_widget(btn)
        innerLayout.add_widget(btn2)
        layout.add_widget(innerLayout)

        quitScreen.content = layout
        quitScreen.open()


'''
####################################
##
##  Setting Dialog Class
##
####################################
'''

class SettingDialog(Widget):
    music_slider = ObjectProperty(None)
    sound_slider = ObjectProperty(None)
    
    root = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(SettingDialog, self).__init__(**kwargs)
            
        self.music_slider.bind(value=self.updateMusicVolume)
        self.sound_slider.bind(value=self.updateSoundVolume)
         
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
        self.dismissSettingsDialog()
        self.root.displayHelpScreen()
    
    def dismissSettingsDialog(self):
        self.root.settingsPopupDismissed = True
        self.root.settingsPopup.dismiss()

    def redirectToHyperLink(self):
        webbrowser.open("https://www.youtube.com/watch?v=bxcxx_wuerk")


'''
####################################
##
##  Help Screen
##
####################################
'''

class HelpScreen(Widget):
    page = NumericProperty(1)

    root = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(HelpScreen, self).__init__(**kwargs)

    def goToNextPage(self): 
        if self.page < 3:
            self.page += 1 
            self.changeImage(self.page)

    def goToPrevPage(self):
        if self.page > 1:
            self.page -= 1
            self.changeImage(self.page)

    def changeImage(self, page):
        self.helpImage.source = 'graphics/helpScreen/' + str(page) + '.png'

    def dismissHelpScreen(self):
        self.root.helpPopup.dismiss()
        self.root.helpPopupDismissed = True
'''
####################################
##
##  Main Application Class
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
        self.music = SoundLoader.load('sound/background.mp3')
        self.music.volume = self.config.getint('General', 'Music') / 100.0
        self.music.bind(on_stop=self.replaySound)
        self.music.play()


        # create the root widget and give it a reference of the view / application instance 
        self.MyViewController = MyViewController(app=self)
        self.root = self.MyViewController.view        

        # load all other sounds:
        self.sound['pop'] = SoundLoader.load('sound/pop.mp3')
        self.sound['popping'] = SoundLoader.load('sound/popping.mp3')
        self.sound['swoosh'] = SoundLoader.load('sound/swoosh.mp3')
        
        
        sound_volume = self.config.getint('General', 'Sound') / 100.0
        for item in self.sound:
            self.sound[item].volume = sound_volume

        # if the user started the game the first time, display quick start guide
        if self.config.get('General', 'FirstStartup') == 'Yes':            
            Clock.schedule_once(self.displayHelpScreen,0)
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

    def displayHelpScreen(self,instance):
        self.root.displayHelpScreen()

# Run the application
if __name__ == "__main__":	
	DbShooter().run()