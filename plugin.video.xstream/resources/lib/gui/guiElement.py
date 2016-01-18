from os import path
from  resources.lib.common import addon
from resources.lib.config import cConfig
import logger

class cGuiElement:
    '''
    This class "abstracts" a xbmc listitem.

    Kwargs:
        sTitle    (str): title/label oft the GuiElement/listitem
        sSite     (str): siteidentifier of the siteplugin, which is called if the GuiElement is selected 
        sFunction (str): name of the function, which is called if the GuiElement is selected
    
        These arguments are mandatory. If not given on init, they have to be set by their setter-methods, before the GuiElement is added to the Gui. 
    '''

    DEFAULT_FOLDER_ICON = 'DefaultFolder.png'
    DEFAULT_FANART = path.join(addon.getAddonInfo('path'),'fanart.jpg')
    MEDIA_TYPES = ['movie','tvshow','season','episode']

    def __init__(self, sTitle = '', sSite = None, sFunction = None):
        self.__sType = 'video'
        self.__sMediaUrl = ''
        self.__sTitle = sTitle
        self.__sTitleSecond = ''
        self.__sDescription = ''
        self.__sThumbnail = ''
        self.__sIcon = self.DEFAULT_FOLDER_ICON
        self.__aItemValues = {}
        self.__aProperties = {}
        self.__aContextElements = []
        self.__sFanart = self.DEFAULT_FANART
        self.__sSiteName = sSite
        self.__sFunctionName = sFunction
        self._sLanguage = ''
        self._sSubLanguage = ''
        self._sYear = ''
        self._sQuality = ''
        self._mediaType = ''
        self._season = ''
        self._episode = ''
        self._imdbID = ''
        self._rating = ''
        self._isMetaSet = False

    def setType(self, sType):
        self.__sType = sType

    def getType(self):
        return self.__sType

    def setMediaUrl(self, sMediaUrl):
        self.__sMediaUrl = sMediaUrl

    def getMediaUrl(self):
        return self.__sMediaUrl

    def setSiteName(self, sSiteName):
        self.__sSiteName = sSiteName

    def getSiteName(self):
        return self.__sSiteName

    def setFunction(self, sFunctionName):
        self.__sFunctionName = sFunctionName

    def getFunction(self):
        return self.__sFunctionName

    def setTitle(self, sTitle):
        self.__sTitle = sTitle;

    def getTitle(self):
        return self.__sTitle

    def setMediaType(self, mediaType):
        '''
        Set mediatype for GuiElement

        Args:
            mediaType(str): 'movie'/'tvshow'/'season'/'episode'
        '''
        mediaType = mediaType.lower()
        if mediaType in self.MEDIA_TYPES:
            self._mediaType = mediaType
        else:
            logger.info('Unknown MediaType given for %s' % self.getTitle())

    def setSeason(self, season):
        self._season = season
        self.__aItemValues['season'] = str(season)

    def setEpisode(self, episode):
        self._episode = episode
        self.__aItemValues['episode'] = str(episode)

    def setTVShowTitle(self, tvShowTitle):
        self.__aItemValues['TVShowTitle'] = str(tvShowTitle)

    def setYear(self, year):
        try:
            year = int(year)
        except:
            logger.info('Year given for %s seems not to be a valid number' % self.getTitle())
            return False
        if len(str(year)) != 4:
            logger.info('Year given for %s has %s digits, required 4 digits' % (self.getTitle(), len(str(year))))
            return False
        if year > 0:
            self._sYear = str(year)
            self.__aItemValues['year'] = year
            return True
        else:
            logger.info('Year given for %s must be greater than 0' % self.getTitle())
            return False

    def setTitleSecond(self, sTitleSecond):
        self.__sTitleSecond = str(sTitleSecond)

    def getTitleSecond(self):
        return self.__sTitleSecond

    def setDescription(self, sDescription):
        self.__sDescription = sDescription
        self.__aItemValues['plot'] = sDescription

    def getDescription(self):
        return self.__sDescription

    def setThumbnail(self, sThumbnail):
        self.__sThumbnail = sThumbnail

    def getThumbnail(self):
        return self.__sThumbnail

    def setIcon(self, sIcon):
        self.__sIcon = sIcon

    def getIcon(self):
        return self.__sIcon
    
    def setFanart(self, sFanart):
        self.__sFanart = sFanart

    def getFanart(self):
        return self.__sFanart

    def addItemValue(self, sItemKey, sItemValue):
        self.__aItemValues[sItemKey] = sItemValue
        
    def setItemValues(self, aValueList):
        self.__aItemValues = aValueList

    def getItemValues(self):
        self.__aItemValues['title'] = self.getTitle()
        if self.getDescription() != '':
            self.__aItemValues['plot'] = self.getDescription()
        for sPropertyKey in self.__aProperties.keys():
            self.__aItemValues[sPropertyKey] = self.__aProperties[sPropertyKey]
        return self.__aItemValues
    
    def addItemProperties(self, sPropertyKey, sPropertyValue):
        self.__aProperties[sPropertyKey] = sPropertyValue
  
    def getItemProperties(self):
        for sItemValueKey in self.__aItemValues.keys():
            if not self.__aItemValues[sItemValueKey]=='':
                try:
                    self.__aProperties[sItemValueKey] = str(self.__aItemValues[sItemValueKey])
                except:
                    pass
        return self.__aProperties

    def addContextItem(self, oContextElement):
        self.__aContextElements.append(oContextElement)

    def getContextItems(self):
        return self.__aContextElements

    def setLanguage(self, sLang):
        self._sLanguage = str(sLang)

    def setSubLanguage(self, sLang):
        self._sSubLanguage = str(sLang)

    def getMeta(self, mediaType, imdbID='', TVShowTitle = '', season='', episode ='', mode = 'add'):
        '''
        Fetch metainformations for GuiElement.
        Args:
            mediaType(str): 'movie'/'tvshow'/'season'/'episode'

        Kwargs:
            imdbID (str)        :
            TVShowTitle (str)   :
            mode (str)          : 'add'/'replace' defines if fetched metainformtions should be added to existing informations, or if they should replace them.
        '''

        if cConfig().getSetting('metahandler')=='false':
           return False
        if not self._mediaType:
            self.setMediaType(mediaType)
        if not mode in ['add','replace']:
            logger.info('Wrong meta set mode')
        if not season and self._season:
            season = self._season
        if not episode and self._episode:
            episode = self._episode

        try:
            from metahandler import metahandlers
        except:
            import traceback
            logger.info(traceback.format_exc())
            return False
        if not self._mediaType:
            logger.info('Could not get MetaInformations for %s, mediaType not defined' % self.getTitle())
            return False
        oMetaget = metahandlers.MetaData()
        if self._mediaType == 'movie' or self._mediaType == 'tvshow':
            meta = oMetaget.get_meta(self._mediaType, self.__sTitle)
            #if self._mediaType == 'tvshow' and not self.__aItemValues['TVShowTitle']:
            #    self.setTVShowTitle(self.__sTitle)
        elif self._mediaType == 'season':
            meta = oMetaget.get_seasons(TVShowTitle, imdbID, str(season))
        elif self._mediaType == 'episode':
            meta = oMetaget.get_episode_meta(TVShowTitle, imdbID, str(season), str(episode))
        else:
            return False

        if not meta:
            return False

        if self._mediaType == 'season':
            meta = meta[0]

        if mode == 'replace':
            self.setItemValues(meta)
            if not meta['cover_url'] == '':
                self.setThumbnail(meta['cover_url'])
            if not meta['backdrop_url'] == '':
                self.setFanart(meta['backdrop_url'])
        else:
            meta.update(self.__aItemValues)
            meta.update(self.__aProperties)
            if meta['cover_url'] != '' and self.__sThumbnail == '':
                self.setThumbnail(meta['cover_url'])
            if meta['backdrop_url'] != '' and self.__sFanart == self.DEFAULT_FANART:
                self.setFanart(meta['backdrop_url'])
            self.setItemValues(meta)

        if meta['imdb_id']:
            self._imdbID = meta['imdb_id']

        self._isMetaSet = True
        return meta