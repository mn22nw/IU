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

from math import sin
from math import cos
from math import radians
import random

from shooter import Shooter
from bubble import Bubble
from threat import Threat

#sätter storleken för huvudfönstret
Window.size = 560, 836


#Custom styles for Label
class TableLabel(Label):  
    title = Label.text


'''
####################################
##
##   Setting Dialog Class
##
####################################
'''
class SettingDialog(BoxLayout):
    music_slider = ObjectProperty(None)
    sound_slider = ObjectProperty(None)
    speed_slider = ObjectProperty(None)
    
    root = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(SettingDialog, self).__init__(**kwargs)
        
        self.music_slider.bind(value=self.update_music_volume)
        self.sound_slider.bind(value=self.update_sound_volume)
        self.speed_slider.bind(value=self.update_speed)
    
    def update_music_volume(self, instance, value):
        # write to app configs
        self.root.app.config.set('General', 'Music', str(int(value)))
        self.root.app.config.write()
        self.root.app.music.volume = value / 100.0
    
    def update_sound_volume(self, instance, value):
        # write to app configs
        self.root.app.config.set('General', 'Sound', str(int(value)))
        self.root.app.config.write()
        for item in self.root.app.sound:
            self.root.app.sound[item].volume = value / 100.0
    
    def update_speed(self, instance, value):
        # write to app configs
        self.root.app.config.set('GamePlay', 'BulletSpeed', str(int(value)))
        self.root.app.config.write()
    
    def display_help_screen(self):
        self.root.setting_popup.dismiss()
        self.root.display_help_screen()
    
    def dismiss_parent(self):
        self.root.setting_popup.dismiss()



# huvudklassen för applikationen, detta är med andra ord den kod som körs när applikationen byggs och blir huvudcontainern där alla widgetar placeras. 
class DbShooterWidget(Widget):
    #app = ObjectProperty(None)
    level = 1
    lives = 5
    points = NumericProperty()
    bubble = None
    upcomingBubble = None
    bubbleList = []
    bubbleGridList = []
    threatList = []
    threatListCopy = []
    angle = NumericProperty()
    rowspaceY = 0
    bubbleSpaceX = 0
    
    #constructor, decides what happens when the class gets instanciated 
    def __init__(self, **kwargs):
        super(DbShooterWidget, self).__init__(**kwargs)

        #get all the questions and answers and make threats out of them
        self.getAllThreats()

        self.bubble = Bubble()

        #create all the bubbles and threats for the startup
        self.createObsticles()
        
        #create the grid for the bubbles to fit in
        self.createBubbleGrid()

        #add the first upcoming bubble to the view
        self.addUpcomingBubbletoView()

        #self.points.bind(value=self.updatePoints)

    def updatePoints(self, instance, value):
        pass
        #self.updateLabel(self.ids.pointsLbl, value)
        

    def changeUpcomingBubbleColor(self):
        self.upcomingBubble.setRandomColor()
        self.upcomingBubble.source = 'graphics/bubbles/' + self.upcomingBubble.getColor() + '.png'


    def addUpcomingBubbletoView(self):
        layout = self.ids.nextBubbleLayout
        self.upcomingBubble = self.createBubble(0,0)
        self.upcomingBubble.pos_hint={'x': 0.55, 'center_y': .5}
        #add the upcomingBubble to the preview-window
        layout.add_widget(self.upcomingBubble)
        print (layout.children, 'CHIIIIIILD')

    def createShootingBubble(self):
        self.bubble = Bubble(pos=(500,500)) 
        #set the shooting bubble to the same color as the upcoming previewd bubble
        self.bubble.bubbleColor = self.upcomingBubble.getColor()
        self.bubble.source = 'graphics/bubbles/' + self.bubble.getColor() + '.png'

    '''
    ####################################
    ##
    ##   Game Play Functions
    ##
    ####################################
    '''
    def fireBubble(self):

        print('FIREEEE')
        '''
        #hej = App.get_running_app()
        #hej.sound['bullet_start'].play()
        ###
        '''
        # create a bubble, calculate the start position and fire it.
        self.createShootingBubble()

        #change the color of the upcoming bubble
        self.changeUpcomingBubbleColor()

        self.angle= radians(float(self.shooter.shootDirectionAngle))

        #set the bubble angle to the same as tower angle (in radiant)
        self.bubble.angle =  self.angle
        self.setBubbleStartPosition()
        #add the bullet to the correct layout
        layout = self.ids.bubbleLayout
        layout.add_widget(self.bubble)
        self.bubble.fire()
     
    def setBubbleStartPosition(self):
        self.bubble.center = self.shooter.center

    def bubble_exploding(self):
        #self.app.sound['pop'].play()
    
        # create an animation on the old bullets position:
        # bug: gif isn't transparent
        #old_pos = self.bullet.center
        #self.bullet.anim_delay = 0.1
        #self.bullet.size = 96, 96
        #self.bullet.center = old_pos
        #self.bullet.source = 'graphics/explosion.gif'
        #Clock.schedule_once(self.bullet_exploded, 1)
        
        self.remove_widget(self.bubble)
        self.bubble = None
        
        self.lives -= 1
        self.update_label(self.ids.livesLbl, self.lives)
        print(self.lives , 'LIIIIVES')
        #if self.lives == 0:
            #self.reset_level()


    def display_help_screen(self):
        # display the help screen on a Popup
        image = Image(source='graphics/help_screen.png')
        
        help_screen = Popup(title='Help Screen',
                            attach_to=self,
                            size_hint=(0.98, 0.98),
                            content=image)
        image.bind(on_touch_down=help_screen.dismiss)
        help_screen.open()

    def updateLabel(self, label, text):
        label.text = str(text) 

    def createBubble(self, x, y):
        b = Bubble(pos_hint={'x': x, 'center_y': y}) 
        b.setRandomColor()
        b.source = 'graphics/bubbles/' + b.getColor() + '.png'
        return b

    def createBubbleRow(self, spaces, bubblesLeft, bubblesRight, x, y):       
        bubbleSizeX =  0.08333333333333 
        layout = self.ids.bubbleLayout
        
        #create bubbles to the left
        for i in range(bubblesLeft):
            b = self.createBubble(x, y)
            layout.add_widget(b)
            self.bubbleList.append(b)
            x += bubbleSizeX
        
        #add empty space for the threat
        x += (bubbleSizeX * spaces)
        
        #create bubbles to right
        for i in range(bubblesRight):
            b = self.createBubble(x, y)
            layout.add_widget(b)
            self.bubbleList.append(b)
            x += bubbleSizeX
    
    def createBubbleGridRow(self, numberOfBubbles):  
        if (numberOfBubbles % 2 == 1): #odd
            self.bubbleSpaceX = 0.041666666666665    
        else:
            self.bubbleSpaceX = 0

        layout = self.ids.bubbleGrid
        
        #create bubbles to the left
        for i in range(numberOfBubbles):
            b = self.createBubble(self.bubbleSpaceX, self.rowspaceY)
            layout.add_widget(b)
            self.bubbleGridList.append(b)
            self.bubbleSpaceX += self.bubble.bubbleSizeX
        
        self.rowspaceY +=self.bubble.bubbleSizeY
           
    def createThreat(self, x, y):
        #get a random threat from the list
        threatIndex = random.randint(0, len(self.threatList)-1)
        
        threat = self.threatList.pop(threatIndex)
        layout = self.ids.bubbleLayout
        
        threat.pos_hint={'x': x, 'center_y': y}
        #b.setRandomColor()
        #t.setQuestion()
        layout.add_widget(threat)

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

            

    def addThreats(self, subject, data):
        for item in data['level' + str(self.level)][subject]:
                threat = Threat()
                threat.title = subject
                threat.question = item['question']
                threat.answers = item['answers']
                threat.correctAnswer = str(item['correctAnswer'])
                threat.imageSrc = 'graphics/threats/threat.png' #+ b.getColor() + '.png'
                #print('THREAT ANW', threat)
                print(threat.question)
                self.threatList.append(threat)
          
    def getAllThreats(self):

        import json
        #I took help from http://xmodulo.com/how-to-parse-json-string-in-python.html
        try:
            #get the json-file were the questions are stored
            with open('questions.json', "r") as f:
                data = json.loads(f.read())

            #get all CSRF questions
            self.addThreats('CSRF', data)
            
            #get all SQL-Injection questions
            self.addThreats('SQL-Injection', data)
            
            #need a copy of the threatList to be able to check for collision later (the original threatList is manipulated later)
            self.threatListCopy = list(self.threatList)
        except (ValueError, KeyError, TypeError):
            print "JSON format error"
    

Factory.register("Shooter", Shooter)

#Huvudklassen som bygger applicationen och returnerar MainWidget
class DbShooter(App):
	
    def build(self):

        self.sound = {}
        self.title = 'DB Shooter'      
	    
        from kivy.base import EventLoop
        EventLoop.ensure_window()
        self.window = EventLoop.window


        # create the root widget and give it a reference of the application instance (so it can access the application settings)
        self.DbShooterWidget = DbShooterWidget(app=self)
        self.root = self.DbShooterWidget

        self.root.bind(points=self.root.updatePoints)
        # load all other sounds:
        #self.sound['pop'] = SoundLoader.load('sound/pop.mp3')
        #self.sound['bullet_start'] = SoundLoader.load('sound/bullet_start.mp3')
        
        self.welcome_screen()

     
    def build_config(self, config):
        config.adddefaultsection('General')
        config.setdefault('General', 'Music', '100')
        config.setdefault('General', 'Sound', '100')
        config.setdefault('General', 'FirstStartup', 'Yes')
        
        config.adddefaultsection('GamePlay')
        config.setdefault('GamePlay', 'BubbleSpeed', '10')
        config.setdefault('GamePlay', 'Levels', '2')

    def welcome_screen(self):
        self.root.display_help_screen()    


    def close(self):
        App.get_running_app().stop()
        raise SystemExit(0)

#Kör applikationen
if __name__ == "__main__":	
	DbShooter().run()