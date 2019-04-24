# -*- coding: utf-8 -*- 

import pygame
#import math
import  commands
import json
import requests

#from beeprint import pp
from libs.roundrects import aa_round_rect
#import gobject
#from wicd import misc 
## local UI import
from UI.constants import Width,Height,ICON_TYPES
from UI.page   import Page,PageSelector
from UI.label  import Label
from UI.fonts  import fonts
from UI.util_funcs import midRect
from UI.keys_def   import CurKeys, IsKeyStartOrA, IsKeyMenuOrB
from UI.scroller   import ListScroller
from UI.icon_pool  import MyIconPool
from UI.icon_item  import IconItem
from UI.multi_icon_item import MultiIconItem
from UI.lang_manager import MyLangManager

from UI.multilabel import MultiLabel
from libs.DBUS       import is_wifi_connected_now

class WeatherPage(Page):
    _FootMsg =  ["Nav","","","Back","Update"]
    _MyList = []
    _ListFontObj = MyLangManager.TrFont("varela13")
    
    _AList = {}

    _Scrolled = 0
    
    _BGwidth = 96
    _BGheight = 96

    _DrawOnce = False
    _Scroller = None

    _EasingDur = 120

    _airwire_y = 0
    _dialog_index = 0

    #_City = "Tehran"
    _Temp = "---"

    with open('/home/cpi/launcher/Menu/GameShell/94_weather/config.json', 'r') as f:
         config = json.load(f)
         _api_key = config['api']
         _location = config['location']
    
    def __init__(self):
        Page.__init__(self)
        self._Icons = {}

        
    def GetWeather(self):
        icon_family = {
                       "01" : "1",
                       "02" : "2",
                       "03" : "3",
                       "04" : "4",
                       "09" : "5",
                       "10" : "6",
                       "11" : "7",
                       "13" : "8",
                       "50" : "9",
                      }
        url = "https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}".format(self._location, self._api_key)
        r = requests.get(url)
        openmap =r.json()
        temp = str(openmap['main']['temp'])
        id_icon = openmap['weather'][0]['icon'][0:2]
        iconOpenmap = int(icon_family[id_icon])
        temp = temp+" C"
        return temp, iconOpenmap
        
    def CurWeather(self):
            self._upTemp, self._dialog_index = self.GetWeather()
            #self._dialog_index = 7
            pygame.time.delay(120)
            self._Templabel.SetText(self._upTemp)
            self._Screen.Draw()
            self._Screen.SwapAndShow()

    def KeyDown(self,event):
        if IsKeyMenuOrB(event.key):
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()

        #if IsKeyStartOrA(event.key):
        #    self.CurWeather()
        
        if IsKeyStartOrA(event.key):
           if is_wifi_connected_now():
              self.CurWeather()
           else:
               self._Screen.Draw()
               self._Screen._MsgBox.SetText("CheckWifiConnection")
               self._Screen._MsgBox.Draw()
               self._Screen.SwapAndShow()


    def Init(self):
        self._curTemp = "---" 
        
        self._CanvasHWND = self._Screen._CanvasHWND
        
        allsign = MultiIconItem()
        allsign._ImgSurf = MyIconPool._Icons["allsign"]
        allsign._MyType = ICON_TYPES["STAT"]
        allsign._Parent = self
        allsign._IconWidth = 140
        allsign._IconHeight = 110
        allsign.Adjust(0,0,134,372,0)
        self._Icons["allsign"] = allsign
        
            
        self._Citylabel = Label()
        self._Citylabel.SetCanvasHWND(self._CanvasHWND)
        
        self._Citylabel.Init(self._location,fonts["varela25"])

        self._Templabel = Label()
        self._Templabel.SetCanvasHWND(self._CanvasHWND)
        
        self._Templabel.Init(self._Temp,fonts["varela25"])

    def Draw(self):
        self.ClearCanvas()

        self._Citylabel.NewCoord(50,50)
        self._Citylabel.Draw()

        self._Templabel.NewCoord(50,80)
        self._Templabel.Draw()
        
        self._Icons["allsign"].NewCoord(165,23)        
        self._Icons["allsign"]._IconIndex = self._dialog_index
        self._Icons["allsign"].DrawTopLeft()
        


class APIOBJ(object):

    _Page = None
    def __init__(self):
        pass
    def Init(self,main_screen):
        self._Page = WeatherPage()
        self._Page._Screen = main_screen
        self._Page._Name ="Weather"
        self._Page.Init()
        
    def API(self,main_screen):
        if main_screen !=None:
            main_screen.PushPage(self._Page)
            main_screen.Draw()
            main_screen.SwapAndShow()

OBJ = APIOBJ()
def Init(main_screen):    
    OBJ.Init(main_screen)
def API(main_screen):
    OBJ.API(main_screen)
    
        
