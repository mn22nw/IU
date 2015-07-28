# -*- coding: utf-8 -*-
import kivy
kivy.require('1.9.0')

from kivy.properties import NumericProperty, StringProperty
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.graphics import Color, Point
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

from kivy.utils import boundary
from kivy.uix.popup import Popup
from kivy.vector import Vector
from kivy.uix.label import Label
from kivy.uix.button import Button
from functools import partial
import random

class Threat(Image):
    title = StringProperty()
    question = StringProperty()
    answers = []
    correctAnswer = StringProperty()
    threatColor= StringProperty()
    animation = None
    colorList = ['blue', 'green', 'red', 'purple', 'yellow']
    exploding = False
    questionScreen = None
        
    '''
    ####################################
    ##
    ##   Threat Behavioral
    ##
    ####################################
    '''
    
    def __init__(self, **kwargs):
        super(Threat, self).__init__(**kwargs)
        #skapa grunden för popupen
        self.questionScreen = Popup( title=self.title, auto_dismiss=False,
                            attach_to=self,
                            size_hint=(0.90, 0.5), pos_hint={'center_x': 0.5, 'center_y': .6}
                            )
    # collide_point + on_touch_down taken from https://groups.google.com/forum/#!topic/kivy-users/LBdragxkYDA


    def collide_point(self, x, y):
        # Do not want to upset the read_pixel method, in case of a bound error
        try:
            color = self._coreimage.read_pixel(x - self.x, self.height - (y - self.y))
        except:
            color = 0, 0, 0, 0
        if color[-1] > 0:
            return True
        return False

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.opacity = 1
        else:
            self.opacity = .3

    def checkAnswer(self, instance):
        if instance.id == self.correctAnswer:
            print('HELT RÄÄÄTTT')
            self.questionScreen.content = Label(text= 'RÄTT')
        else:
            self.questionScreen.content = Label(text= 'Feeel')

        # dismiss window after 1 seconds
        Clock.schedule_once(self.questionScreen.dismiss, 1)

    def displayQuestionScreen(self):
        # display the question screen on a Popup
        
        #design this later!!
        image = Image(source='graphics/questionScreen.png')
        
        layout = BoxLayout(orientation = 'vertical')
        l = Label(text= self.question)

        btn1 = Button(id= '0', text=self.answers[0])
        btn1.bind(on_press= self.checkAnswer)
        btn2 = Button(id= '1', text=self.answers[1])
        btn2.bind(on_press=self.checkAnswer)
        btn3 = Button(id= '2', text=self.answers[2])
        btn3.bind(on_press=self.checkAnswer)
        
        layout.add_widget(l)
        layout.add_widget(btn1)
        layout.add_widget(btn2)

        
        self.questionScreen.title = self.title
        self.questionScreen.content = layout

        self.questionScreen.open()
        
    
    def create_animation(self, speed, destination):
        # create the animation
        time = Vector(self.center).distance(destination) / (speed * +70.0)
        # the splitting of the position animation in (x,y) is a work-around for the kivy issue #2667 for version < 1.9.0
        return Animation(x=destination[0],y=destination[1], duration=time, transition='linear')
        


    #TODO - flytta till threat!!!?!
    def threat_explode(self):
        if self.exploding == True:
            return
        self.exploding = True
        
        self.unbind(pos=self.callback_pos)
        self.animation.unbind(on_complete=self.on_collision_with_edge)
        self.animation.stop(self)
        
        self.parent.threat_exploding()
        
    
    #returns a string with the color name  
    def setRandomColor(self):
        c = random.randint(0,(len(self.colorList) - 1))
        self.bubbleColor = self.colorList[c]
        return self.bubbleColor

        #for c in range(0,len(colorList)):
    def getColor(self):
        #print(self.bubbleColor, 'threatCOlor')
        return self.bubbleColor


