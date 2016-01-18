# -*- coding: utf-8 -*-
from resources.lib.parser import cParser
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.gui.gui import cGui
from resources.lib.util import cUtil
from resources.lib.handler.ParameterHandler import ParameterHandler

SITE_IDENTIFIER = 'bundesliga_de'
SITE_NAME = 'Bundesliga.de'
SITE_ICON = 'bl.png'

URL_MAIN = 'http://www.bundesliga.de'
URL_TV = 'http://www.bundesliga.de/de/service/?action=teaserbox&type=video&language=de&amount=25&category='
URL_GET_STREAM = 'http://btd-flv-lbwww-01.odmedia.net/bundesliga/'

def load():
    oGui = cGui()
    __createMainMenuItem(oGui, 'Aktuell', 'new')    
    __createMainMenuItem(oGui, 'Spieltag', 'spieltag')
    __createMainMenuItem(oGui, 'Stars', 'stars')
    __createMainMenuItem(oGui, 'Stories', 'stories')
    __createMainMenuItem(oGui, 'Historie', 'historie')
    __createMainMenuItem(oGui, 'Partner', 'partner')
    __createMainMenuItem(oGui, 'Vereine', 'clubs')
    oGui.setEndOfDirectory()

def __createMainMenuItem(oGui, sTitle, sPlaylistId):
    oGuiElement = cGuiElement()
    oGuiElement.setSiteName(SITE_IDENTIFIER)
    oGuiElement.setFunction('listVideos')
    oGuiElement.setTitle(sTitle)
    oOutputParameterHandler = ParameterHandler()
    oOutputParameterHandler.setParam('playlistId', sPlaylistId)
    oGui.addFolder(oGuiElement, oOutputParameterHandler)
    
def listVideos():
    oGui = cGui()

    params = ParameterHandler()
    if (params.exist('playlistId')):
        sPlaylistId = params.getValue('playlistId')

        if not params.exist('sUrl'):
            sUrl = URL_TV + str(sPlaylistId)
        else:
            sUrl = params.getValue('sUrl')
        
        if sPlaylistId == 'spieltag':
            oParser = cParser()
            
            if not params.exist('saison'):
                oRequest = cRequestHandler('http://www.bundesliga.de/de/bundesliga-tv/index.php')
                sHtmlContent = oRequest.request()
                sPattern = 'data-season="([^"]+)" class="active grey-gradient"'
                aResult = oParser.parse(sHtmlContent, sPattern)
                saison = aResult[1][0]
            else:
                saison = params.getValue('saison')
            
            oRequest = cRequestHandler(sUrl+'&season='+saison+'&matchday=1')
            sHtmlContent = oRequest.request()
            if sHtmlContent.find('"message":"nothing found"') != -1:
                return False
                #ausgewählte Saison
            for matchDay in range(1,35):
                oGuiElement = cGuiElement()
                oGuiElement.setSiteName(SITE_IDENTIFIER)
                oGuiElement.setFunction('listVideos')
                oGuiElement.setTitle('%s Spieltag Saison %s' % (matchDay,saison))

                sUrl = sUrl+'&season='+saison+'&matchday='+str(matchDay)
                oOutputParameterHandler = ParameterHandler()
                oOutputParameterHandler.setParam('sUrl', sUrl)
                oOutputParameterHandler.setParam('saison', saison)
                oOutputParameterHandler.setParam('matchDay', matchDay)
                oOutputParameterHandler.setParam('playlistId', 'spieltagEinzeln')
                oGui.addFolder(oGuiElement, oOutputParameterHandler)
            
            #ältere Saison
            oGuiElement = cGuiElement()
            oGuiElement.setSiteName(SITE_IDENTIFIER)
            oGuiElement.setFunction('listVideos')
            lastSaison = str(int(saison) - 1)
            oGuiElement.setTitle('* Saison %s/%s *' % (lastSaison,saison))

            oOutputParameterHandler = ParameterHandler()
            oOutputParameterHandler.setParam('sUrl', sUrl)
            oOutputParameterHandler.setParam('saison', lastSaison)
            oOutputParameterHandler.setParam('playlistId', 'spieltag')
            oGui.addFolder(oGuiElement, oOutputParameterHandler)

            
        elif sPlaylistId == 'clubs':
            sPattern = '<li data-club="([^"]+)" data-name="([^"]+)".*?src="([^"]+)"'
            oRequest = cRequestHandler('http://www.bundesliga.de/de/bundesliga-tv/index.php')
            sHtmlContent = oRequest.request()
           
            oParser = cParser()
            aResult = oParser.parse(sHtmlContent, sPattern)
            
            if (aResult[0] == False):
                return False
            for aEntry in aResult[1]:
                oGuiElement = cGuiElement()
                oGuiElement.setSiteName(SITE_IDENTIFIER)
                oGuiElement.setFunction('listVideos')
                oGuiElement.setTitle((aEntry[1]))
                sThumbnail = URL_MAIN + str(aEntry[2]).replace('variant27x27.','')
                oGuiElement.setThumbnail(sThumbnail)

                sUrl = sUrl +'&club='+str(aEntry[0])
                oOutputParameterHandler = ParameterHandler()
                oOutputParameterHandler.setParam('sUrl', sUrl)
                oOutputParameterHandler.setParam('playlistId', 'clubVideos')
                oGui.addFolder(oGuiElement, oOutputParameterHandler)
        else:
            sPattern = 'btd-teaserbox-entry.*?<a href="([^"]+)".*?<h3 class=.*?>([^<]+)<.*?src="([^"]+).*?class="teaser-text">([^<]+)'
            oRequest = cRequestHandler(sUrl)
            sHtmlContent = oRequest.request()
            sHtmlContent = sHtmlContent.replace('\\"','"').replace('\\/','/')

            oParser = cParser()
            aResult = oParser.parse(sHtmlContent, sPattern)
            if (aResult[0] == False):
                return False
            for aEntry in aResult[1]:
                sThumbnail = URL_MAIN + str(aEntry[2])
                sUrl = URL_MAIN + str(aEntry[0])
                sTitle = cUtil().unescape(str(aEntry[1]).decode('unicode-escape')).encode('utf-8')
                sDescription = cUtil().unescape(str(aEntry[3]).decode('unicode-escape')).encode('utf-8')
                oGuiElement = cGuiElement()
                oGuiElement.setSiteName(SITE_IDENTIFIER)
                oGuiElement.setFunction('play')
                oGuiElement.setTitle(sTitle)
                oGuiElement.setDescription(sDescription)
                oGuiElement.setThumbnail(sThumbnail)
                
                oOutputParameterHandler = ParameterHandler()
                oOutputParameterHandler.setParam('sUrl', sUrl)
                oOutputParameterHandler.setParam('sTitle', sTitle)
                
                oGui.addFolder(oGuiElement, oOutputParameterHandler, bIsFolder = False)
            oGui.setView('movies')
    oGui.setEndOfDirectory()

def play():
    params = ParameterHandler()
    if (params.exist('sUrl') and params.exist('sTitle')):
        sUrl = params.getValue('sUrl')
        sTitle = params.getValue('sTitle')
        print sUrl
        oRequest = cRequestHandler(sUrl)
        sHtmlContent = oRequest.request()

        sPattern = ': "([^\."]+\.flv)"'
        oParser = cParser()
        aResult = oParser.parse(sHtmlContent, sPattern)
        if (aResult[0] == True):
            sStreamUrl = URL_GET_STREAM + str(aResult[1][0])+'?autostart=true'           
            result = {}
            result['streamUrl'] = sStreamUrl
            result['resolved'] = True
            return result
    return False
