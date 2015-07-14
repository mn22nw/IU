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

        '''
        for deflector in self.parent.deflector_list:
            if deflector.collide_grab_point(*touch.pos):
                # pass the touch to the deflector scatter
                return super(Background, self).on_touch_down(touch)
        
        # if i didn't wanted to move / scale a deflector and but rather create a new one:
        # search for other 'lonely' touches
              
        for search_touch in EventLoop.touches[:]:
            if 'lonely' in search_touch.ud:
                del search_touch.ud['lonely']
                # so here we have a second touch: try to create a deflector:
                if self.parent.stockbar.new_deflectors_allowed == True:
                    length = Vector(search_touch.pos).distance(touch.pos)
                    # create only a new one if he's not too big and not too small
                    if MIN_DEFLECTOR_LENGTH <= length <= self.parent.stockbar.width:
                        self.create_deflector(search_touch, touch, length)
                    else:
                        self.parent.app.sound['no_deflector'].play()
                else:
                    self.parent.app.sound['no_deflector'].play()
                
                return True
        
        # if no second touch was found: tag the current one as a 'lonely' touch
        ud['lonely'] = True
        '''
    
    def create_deflector(self, touch_1, touch_2, length):
        self.parent.app.sound['deflector_new'].play()
        deflector = Deflector(touch1=touch_1, touch2=touch_2, length=length)
        self.parent.deflector_list.append(deflector)
        self.add_widget(deflector)
        
        self.parent.stockbar.new_deflector(length)
        
    
    def delete_deflector(self, deflector):
        self.parent.app.sound['deflector_delete'].play()
        self.parent.stockbar.deflector_deleted(deflector.length)
        
        self.remove_widget(deflector)
        self.parent.deflector_list.remove(deflector)
    
    def delete_all_deflectors(self):
        for deflector in self.parent.deflector_list:
            self.remove_widget(deflector)
        self.parent.deflector_list = []
        
        if self.parent.stockbar is not None:        
            self.parent.stockbar.recalculate_stock()
