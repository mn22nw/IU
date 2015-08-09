# -*- coding: utf-8 -*-
import kivy
kivy.require('1.9.0')

from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.graphics import Color, Point
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior

from kivy.utils import boundary
from kivy.uix.popup import Popup
from kivy.vector import Vector
from kivy.uix.label import Label
from kivy.uix.button import Button
from functools import partial
import random


#custom class for question buttons (so they can be styled in the KV file)
class QuestionButton(Button):  
    pass
#makes it possible to click on the image as well(the number next to the questions)
class ImageButton(ButtonBehavior, Image):
    pass

#custom triangle class for threat
# point_inside_polygon and collide_point is taken from kivys own examples https://github.com/kivy/kivy/blob/master/examples/widgets/customcollide.py
def point_inside_polygon(x, y, poly):
    n = len(poly)
    inside = False
    p1x = poly[0]
    p1y = poly[1]
    for i in range(0, n + 2, 2):
        p2x = poly[i % n]
        p2y = poly[(i + 1) % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

'''
####################################
##
##   Threat Class
##
####################################
'''

class Threat(Widget):
    #these are needed to calculate the correct collide point
    p1 = ListProperty([0, 0])
    p2 = ListProperty([0, 0])
    p3 = ListProperty([0, 0])

    #properties
    title = StringProperty()
    question = StringProperty()
    answers = []
    correctAnswer = StringProperty()
    threatColor= StringProperty()
    animation = None
    colorList = ['blue', 'green', 'red', 'purple', 'yellow']
    exploding = False
    questionScreen = None
    imageSrc = StringProperty()
        
    def __init__(self, **kwargs):
        super(Threat, self).__init__(**kwargs)
        
        self.app = self.app = App.get_running_app()
        #creates the base for the popup
        self.questionScreen = Popup( title=self.title, auto_dismiss=False,
                            attach_to=self,
                            size_hint=(None,None), pos_hint={'center_x': 0.5, 'center_y': .6}
                            )

    def collide_point(self, x, y):
        x, y = self.to_local(x, y)
        return point_inside_polygon(x, y,
                self.p1 + self.p2 + self.p3)

    def checkAnswer(self, instance):
        try:
            layout = BoxLayout(orientation = 'vertical')

            if instance.id == self.correctAnswer:
                image = Image(source='graphics/success.jpg', pos_hint={'center_x': 0.5, 'center_y': 0.4})
                layout.add_widget(image)
                self.questionScreen.content = layout

                # increase points
                self.parent.parent.setPoints(500)

                #remove threat if success
                Clock.schedule_once(self.animateThreat, 1.1)
                Clock.schedule_once(self.removeThreat, 2)
                # dismiss window after 1 seconds
                Clock.schedule_once(self.questionScreen.dismiss, 1)

                
            else:
                image = Image(source='graphics/fail.jpg', pos_hint={'center_x': 0.5, 'center_y': 0.4})
                layout.add_widget(image)
                self.questionScreen.content = layout
                # dismiss window after 1.5 seconds and remove points after
                Clock.schedule_once(self.questionScreen.dismiss, 1.5)
                Clock.schedule_once(self.delayRemovingPoints, 1.6)
        except:
            pass
          

    def displayQuestionScreen(self):
        # display the question screen in a Popup
        layout = BoxLayout(orientation = 'vertical')
        l = Label(text= self.question,  size_hint_y=0.3, font_size=20)
        layout.add_widget(l)
        gridlayout = GridLayout(cols=3, size_hint_y=0.7)      
        
        for i in range(3):
            imageBtn = ImageButton(id= str(i), source='graphics/questions/'+ str(i)+'.png', size_hint_x=0.15, on_press= self.checkAnswer)
            btn = QuestionButton(id= str(i), text=self.answers[i])
            btn.bind(on_press= self.checkAnswer)
            spaceFillGrid = Widget(size_hint_x= 0.05)
            gridlayout.add_widget(spaceFillGrid)
            gridlayout.add_widget(imageBtn)
            gridlayout.add_widget(btn)

        spaceFill = Widget(size_hint_y= 0.2)
        layout.add_widget(gridlayout)
        layout.add_widget(spaceFill)
        self.questionScreen.title = self.title
        self.questionScreen.content = layout

        self.questionScreen.open()
        
    def animateThreat(self, instance):
        self.changeToPointsPicture()
        X = self.width
        Y = self.height
        threatAnimation = Animation( size=(X *1.5, X*1.5), opacity = 0, duration=0.6)
        threatAnimation.start(self)

    def removeThreat(self, instance):
        #first remove it from the threat list!
        try:
            self.parent.parent.threatListCopy.remove(self)
            self.parent.remove_widget(self)
        except:
            pass
    def delayRemovingPoints(self, instance):
        try:
            self.parent.parent.setPoints(-200)
        except:
            pass

    def changeToPointsPicture(self):
        self.imageSrc = 'graphics/500.png'
        self.app.sound['swoosh'].play()

    #returns a string with the color name  
    def setRandomColor(self):
        c = random.randint(0,(len(self.colorList) - 1))
        self.bubbleColor = self.colorList[c]
        return self.bubbleColor

    def getColor(self):
        return self.bubbleColor


