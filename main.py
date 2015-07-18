# -*- coding: utf-8 -*-
#Labb 4, Maria Nygren
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
from kivy.properties import StringProperty
from kivy.core.audio import SoundLoader
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.button import Button

from math import sin
from math import cos
from math import radians

from shooter import Shooter
from bubble import Bubble

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
    points = 0
    bubble = None

    bubble_list = []
    threat_list = []
    #goal_list = []
    
    
    #constructor, decides what happens when the class gets instanciated 
    def __init__(self, **kwargs):
        super(DbShooterWidget, self).__init__(**kwargs)

        #get all the questions and answers for the first level
        question_list = self.getQuestions(1)

        #create all the bubbles and threats for the startup
        self.createObsticles()

    '''
    ####################################
    ##
    ##   GUI Functions
    ##
    ####################################
    '''
    def fire_button_pressed(self):
        if self.bubble:
            # if there is already a bullet existing (which means it's flying around or exploding somewhere)
            # don't fire.
            return
        print('FIREEEE')
        #hej = App.get_running_app()
        #hej.sound['bullet_start'].play()
        
        # create a bubble, calculate the start position and fire it.
        #tower_angle = radians(self.shooter.shooter_tower_scatter.rotation) 
        tower_angle= self.shooter.shooter_tower_angle # * (3.14159265 / 180.) 
        print('TOWER ANGLE FIRE BULLET = ', tower_angle )
        tower_position = self.shooter.pos
        bubble_position = (tower_position[0] + 48 + cos(tower_angle) * 130, tower_position[1] + 70 + sin(tower_angle) * 130)
        self.bubble = Bubble(angle=tower_angle)
        self.bubble.center = bubble_position
        self.add_widget(self.bubble)
        self.bubble.fire()
        

    '''
    ####################################
    ##
    ##   Game Play Functions
    ##
    ####################################
    '''
    
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

    def update_label(self, label, text):
        label.text = 'Lives: ' + str(text) 
    
    def createRow(self, numberOfBubbles, bubblePosX, bubblePosY):
        layout = self.ids.bubbleLayout
        for x in range(numberOfBubbles):
            b = Bubble(pos_hint={'x': bubblePosX, 'center_y': bubblePosY}) 
            b.setRandomColor()
            b.source = 'graphics/bubbles/' + b.getColor() + '.png'
            layout.add_widget(b)
            #self.bubble_list.append(b)
            bubblePosX +=0.08333333333333


    def createObsticles(self):             
        evenRow = True
        bubblePosY = 0

        for r in range(20):
            if evenRow:
                self.createRow(12, 0, bubblePosY)
                evenRow = False
            else: 
                self.createRow(11, 0.041666666666665, bubblePosY)
                evenRow = True

            bubblePosY+=0.045



        #per varannan rad placera hälften till höger minus en 
        
    def getQuestions(self, level):
        #get the json-file were the questions are stored
        store = JsonStore('questions.json')

        level = store.get('level' + str(level))
            
        for subject in level:
            for question in subject:
                print(question)
            print('___________________')

        #print(store, 'iiiiiiiiiiiiiiiiiih')
        '''
                best =  store.get('level1')
                print(best[0])
                test =  store.get('level')['best']
                print test
                #for key in sorted(store):
                 #   print (str(key['test']), 'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWi')
                #res = store.get('CSRF')
                #for item in res:
                   # print "res=", str(item)
                    #print "res=", str(item[1]['answers'])
        '''

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