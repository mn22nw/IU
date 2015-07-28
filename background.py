import kivy


from kivy.uix.image import Image
from kivy.base import EventLoop
from kivy.vector import Vector

MIN_DEFLECTOR_LENGTH = 100


'''
####################################
##
##   Background Image Class
##
####################################
'''
class Background(Image):
    
    '''
    ####################################
    ##
    ##   On Touch Down
    ##
    ####################################
    '''
    def on_touch_down(self, touch):
        ud = touch.ud
        
        # if a bullet has been fired and is flying now, don't allow ANY change!
        if self.parent.bubble != None:
            return True

        print('a bullet has landed..........BOOOM')

