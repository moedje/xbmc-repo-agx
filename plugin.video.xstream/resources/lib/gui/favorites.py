# -*- coding: utf-8 -*-
import os
import xbmcaddon
from xbmc import translatePath

class FavGui:

    def __init__(self):
        profilePath = translatePath(xbmcaddon.Addon(id='plugin.video.xstream').getAddonInfo('profile'))
        favPath = os.path.join(profilePath,'Favourites')
       
    def showFavs(self):
        return True
    def addFavs(self):
        if os.path.exists(self.favPath):
            open(favPath,'a').write("test")
        return True
    def getFavs(self):
        return True