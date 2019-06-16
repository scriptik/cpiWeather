# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime

import pygame
import requests
from UI.constants import ICON_TYPES
from UI.icon_pool import MyIconPool
from UI.keys_def import IsKeyMenuOrB, IsKeyStartOrA
from UI.label import Label
from UI.lang_manager import MyLangManager
from UI.multi_icon_item import MultiIconItem
from UI.multilabel import MultiLabel
from UI.page import Page
from libs.DBUS import is_wifi_connected_now


class WeatherPage(Page):
    _FootMsg = ["Nav", "", "", "Back", "Update"]
    _MyList = []

    _AList = {}

    _Scrolled = 0

    _BGwidth = 96
    _BGheight = 96

    _DrawOnce = False
    _Scroller = None

    _EasingDur = 120

    _airwire_y = 0
    _dialog_index = 0

    _placeHolderText = "---"
    _errorText = ""

    _api_key = ""
    _location = ""

    def __init__(self):
        Page.__init__(self)
        self._CityLabel = Label()
        self._TempLabel = Label()
        self._TempSummaryLabel = MultiLabel()
        self._WeatherSummaryLabel = MultiLabel()
        self._SummarySunLabel = MultiLabel()
        self._ErrorLabel = Label()
        self._Icons = {}
        self._Fonts = {}

        try:
            with open(os.path.dirname(os.path.abspath(__file__)) + '/config.json', 'r') as f:
                config = json.load(f)
                self._api_key = config['api']
                self._location = config['location']
        except Exception, e:
            print("read 'weather/config.json' error: %s" % str(e))
            self._errorText = "Error: Check your 'config.json' file"

    def get_weather(self):
        icon_family = {
            "01": "1",
            "02": "2",
            "03": "3",
            "04": "4",
            "09": "5",
            "10": "6",
            "11": "7",
            "13": "8",
            "50": "9",
        }

        temp_c = "{} °C"

        url = "https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}".format(self._location,
                                                                                                  self._api_key)
        r = requests.get(url)
        openmap = r.json()
        main = openmap['main']
        weather = openmap['weather'][0]
        sys = openmap['sys']

        description = weather['description']
        wind = openmap['wind']['speed']
        temp = temp_c.format(str(main['temp']))
        pressure = str(main['pressure'])
        humidity = str(main['humidity'])
        temp_min = temp_c.format(str(main['temp_min']))
        temp_max = temp_c.format(str(main['temp_max']))
        temp_sum = "{}/{}\n{}".format(temp_max, temp_min, str(description).capitalize())
        id_icon = weather['icon'][0:2]
        dt = datetime.fromtimestamp(openmap['dt'])

        sunrise = datetime.fromtimestamp(sys['sunrise'])
        sunset = datetime.fromtimestamp(sys['sunset'])

        summary_weather = "Wind: {} m/s" \
                          "\nPressure: {} hpa" \
                          "\nHumidity: {}%". \
            format(wind,
                   pressure,
                   humidity)

        summary_sun = "Sunrise: {}" \
                      "\nSunset: {}" \
                      "\n{}". \
            format(sunrise.strftime("%H:%M"),
                   sunset.strftime("%H:%M"),
                   dt.strftime("%H:%M %b %d, %a"))

        icon_openmap = int(icon_family[id_icon])

        return unicode(temp), unicode(temp_sum), icon_openmap, summary_weather, summary_sun

    def CurWeather(self):

        if len(str(self._location)) < 2:
            self._errorText = "Error: Check 'location' value in your 'config.json' file"
        elif len(str(self._api_key)) != 32:
            self._errorText = "Error: Check 'api' value in your 'config.json' file"
        else:
            try:
                temp, temp_sum, icon_index, summary_weather, summary_sun = self.get_weather()
                pygame.time.delay(120)
                self._TempLabel.SetText(temp)
                self._TempSummaryLabel.SetText(temp_sum)
                self._WeatherSummaryLabel.SetText(summary_weather)
                self._SummarySunLabel.SetText(summary_sun)
                self._Icons["allsign"]._IconIndex = icon_index
                self._errorText = ""
            except Exception, e:
                print("weather.CurWeather error: %s" % str(e))
                self._errorText = "Error: Weather Request Issues..."

        self._ErrorLabel.SetText(self._errorText)
        self._Screen.Draw()
        self._Screen.SwapAndShow()

    def KeyDown(self, event):
        if IsKeyMenuOrB(event.key):
            self.ReturnToUpLevelPage()
            self._Screen.Draw()
            self._Screen.SwapAndShow()

        if IsKeyStartOrA(event.key):
            if is_wifi_connected_now():
                self.CurWeather()
            else:
                self._Screen.Draw()
                self._Screen._MsgBox.SetText("CheckWifiConnection")
                self._Screen._MsgBox.Draw()
                self._Screen.SwapAndShow()

    def Init(self):
        self._CanvasHWND = self._Screen._CanvasHWND

        self._Fonts["normal"] = MyLangManager.TrFont("varela14")
        self._Fonts["big"] = MyLangManager.TrFont("varela25")
        self._Fonts["small"] = MyLangManager.TrFont("veramono12")

        allsign = MultiIconItem()
        allsign._ImgSurf = MyIconPool._Icons["allsign"]
        allsign._MyType = ICON_TYPES["STAT"]
        allsign._Parent = self
        allsign._IconWidth = 140
        allsign._IconHeight = 110
        allsign.Adjust(0, 0, 134, 372, 0)
        self._Icons["allsign"] = allsign
        self._Icons["allsign"].NewCoord(180, 23)

        self._CityLabel.SetCanvasHWND(self._CanvasHWND)
        self._CityLabel.Init(self._location, self._Fonts["big"])
        self._CityLabel.NewCoord(30, 30)

        self._TempLabel.SetCanvasHWND(self._CanvasHWND)
        self._TempLabel.Init("", self._Fonts["big"])
        self._TempLabel.NewCoord(30, 60)

        self._TempSummaryLabel.SetCanvasHWND(self._CanvasHWND)
        self._TempSummaryLabel.Init("", self._Fonts["normal"])
        self._TempSummaryLabel.NewCoord(30, 90)
        self._TempSummaryLabel._Width = 400  # spike

        self._WeatherSummaryLabel.SetCanvasHWND(self._CanvasHWND)
        self._WeatherSummaryLabel.Init(self._placeHolderText, self._Fonts["small"])
        self._WeatherSummaryLabel.NewCoord(30, 130)
        self._WeatherSummaryLabel._Width = 800  # spike

        self._SummarySunLabel.SetCanvasHWND(self._CanvasHWND)
        self._SummarySunLabel.Init(self._placeHolderText, self._Fonts["small"])
        self._SummarySunLabel.NewCoord(180, 130)
        self._SummarySunLabel._Width = 800  # spike

        self._ErrorLabel.SetCanvasHWND(self._CanvasHWND)
        self._ErrorLabel.Init(self._errorText, self._Fonts["small"])
        self._ErrorLabel.NewCoord(0, 180)

    def Draw(self):
        self.ClearCanvas()

        self._CityLabel.Draw()
        self._TempLabel.Draw()
        self._TempSummaryLabel.Draw()
        self._WeatherSummaryLabel.Draw()
        self._SummarySunLabel.Draw()
        self._ErrorLabel.Draw()

        self._Icons["allsign"].DrawTopLeft()


class APIOBJ(object):
    _Page = None

    def __init__(self):
        pass

    def Init(self, main_screen):
        self._Page = WeatherPage()
        self._Page._Screen = main_screen
        self._Page._Name = "Weather"
        self._Page.Init()

    def API(self, main_screen):
        if main_screen != None:
            main_screen.PushPage(self._Page)
            main_screen.Draw()
            main_screen.SwapAndShow()


OBJ = APIOBJ()


def Init(main_screen):
    OBJ.Init(main_screen)


def API(main_screen):
    OBJ.API(main_screen)
