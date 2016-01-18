# -*- coding: utf-8 -*-
from resources.lib.parser import cParser
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.gui.gui import cGui
from resources.lib.config import cConfig
from json import loads
import logger


SITE_IDENTIFIER = 'kkiste_to'
SITE_NAME = 'KKiste.to'
SITE_ICON = 'kinokiste.png'

URL_MAIN = 'http://kkiste.to'
URL_CURRENT_MOVIES = 'http://kkiste.to/aktuelle-kinofilme/'
URL_NEW_MOVIES = 'http://kkiste.to/neue-filme/'
URL_MOVIES_ALL = 'http://kkiste.to/film-index/'
URL_MOVIES_GENRE = 'http://kkiste.to/genres/'

URL_SERIES = 'http://kkiste.to/serien/'
URL_SERIES_EPISODEURL = 'http://kkiste.to/xhr/movies/episodes'
URL_SEARCH = 'http://kkiste.to/search/?q='

PATTERN_DIVBOX = '<div class="mbox.*?" ><a href="([^"]+)".*?<img src="([^_]+)_170_120.jpg".*?<strong>([^<]+)</strong>'
PATTERN_LIST = '<a href="([^"]+)" title="([^"]+)" class="title">'

PARAM_MOVIESEGMENT_KEY = 'sMovieSegment'
PARAM_URL_KEY = 'sUrl'
PARAM_PAGE_KEY = 'iPage'
PARAM_ROOTURL_KEY = "sRootUrl"

def load():
    oGui = cGui()
    __createMainMenuItem(oGui, 'Kinofilme', URL_CURRENT_MOVIES, 'showMovies')
    __createMainMenuItem(oGui, 'Neu!', URL_NEW_MOVIES, 'showMovies')
    __createMainMenuItem(oGui, 'Alle Filme', URL_MOVIES_ALL, 'showCharacters')
    __createMainMenuItem(oGui, 'Genre', URL_MOVIES_GENRE, 'showGenre')
    __createMainMenuItem(oGui, 'Serien', URL_SERIES, 'showMovies')
    __createMainMenuItem(oGui, 'Suche', '', 'showSearch')
    oGui.setEndOfDirectory()

def showGenre():
    oGui = cGui()

    oInputParameterHandler = ParameterHandler()
    if (oInputParameterHandler.exist(PARAM_URL_KEY)):
        sUrl = oInputParameterHandler.getValue(PARAM_URL_KEY)

        oRequest = cRequestHandler(sUrl)
        sHtmlContent = oRequest.request()

        sPattern = '<li><a href="([^"]+)" title="Alle[^"]+">([^<]+)<span>'

        oParser = cParser()
        aResult = oParser.parse(sHtmlContent, sPattern)
        if (aResult[0] == True):
            for aEntry in aResult[1]:
                sUrl = aEntry[0]
                sUrl = URL_MAIN + sUrl
                sTitle = aEntry[1].strip()

                oGuiElement = cGuiElement()
                oGuiElement.setSiteName(SITE_IDENTIFIER)
                oGuiElement.setFunction('showMovies')
                oGuiElement.setTitle(sTitle)

                oOutputParameterHandler = ParameterHandler()
                oOutputParameterHandler.setParam(PARAM_URL_KEY, sUrl)
                oOutputParameterHandler.setParam(PARAM_ROOTURL_KEY, sUrl)
                oOutputParameterHandler.setParam(PARAM_PAGE_KEY,1)
                oGui.addFolder(oGuiElement, oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showMovies():
    oGui = cGui()
    oParams = ParameterHandler()
    if (oParams.exist(PARAM_URL_KEY)):
        sUrl = oParams.getValue(PARAM_URL_KEY)
        sRootUrl = sUrl
        iPage = 1
        if (oParams.exist(PARAM_PAGE_KEY)):
            iPage = oParams.getValue(PARAM_PAGE_KEY)
            sRootUrl = oParams.getValue(PARAM_ROOTURL_KEY)

            if (sRootUrl.startswith(URL_MOVIES_ALL) |
                  sRootUrl.startswith(URL_SEARCH)):
                sPattern = PATTERN_LIST
            elif (sRootUrl.startswith(URL_CURRENT_MOVIES) |
                sRootUrl.startswith(URL_NEW_MOVIES) |
                sRootUrl.startswith(URL_MAIN)):
                sPattern = PATTERN_DIVBOX
            else:
                oGui.showError('Error','wrong root url')
                return
            _parseMedia(sUrl,sRootUrl,iPage,sPattern, oGui)
        else:
            oGui.showError('Error','wrong page count')
            return

    else:
        oGui.showError('Error','No request url found')
    oGui.setEndOfDirectory()

def _parseMedia(sUrl,sRootUrl,iPage,sPattern, oGui):
    logger.error("parse %s with pattern %s" % (sUrl, sPattern))

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    _parseMovie(sHtmlContent,sUrl,sRootUrl,iPage,sPattern,oGui)

def _parseMovie(sHtmlContent,sUrl,sRootUrl,iPage,sPattern, oGui):
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        total = len(aResult[1])
        for aEntry in aResult[1]:
            oOutputParameterHandler = ParameterHandler()
            movieUrlSegment = str(aEntry[0])
            newUrl = URL_MAIN + '/' + movieUrlSegment;

            if (sRootUrl.startswith(URL_MOVIES_ALL) |
                sRootUrl.startswith(URL_SEARCH)):
                sMovieTitle = str(aEntry[1])
                # pattern Jetzt <TITLE> Stream ansehen
                sMovieTitle = sMovieTitle[6:len(sMovieTitle)-15]
                coverUrl = ''
            else:
                coverUrl = str(aEntry[1])+"_145_215.jpg"
                sMovieTitle = str(aEntry[2]).replace(" Stream","")
            oGuiElement = cGuiElement()
            oGuiElement.setSiteName(SITE_IDENTIFIER)
            serie = False
            if (sRootUrl.startswith(URL_SERIES) | ((not sRootUrl.startswith(URL_CURRENT_MOVIES)) & _mediaIsASerie(newUrl))):
                serie = True
                oGuiElement.setFunction('showAllSeasons')
                oGuiElement.setMediaType('tvshow')
                oOutputParameterHandler.setParam(PARAM_MOVIESEGMENT_KEY,movieUrlSegment)
            else:
                oGuiElement.setMediaType('movie')
                oGuiElement.setFunction('showHosters')
            oGuiElement.setTitle(sMovieTitle)
            oGuiElement.setThumbnail(coverUrl)

            oOutputParameterHandler.setParam(PARAM_URL_KEY, newUrl)
            oOutputParameterHandler.setParam('sMovieTitle', sMovieTitle)
            if not serie:
                oGui.addFolder(oGuiElement, oOutputParameterHandler, bIsFolder = False, iTotal = total)
            else:
                oGui.addFolder(oGuiElement, oOutputParameterHandler, iTotal = total)

        sNextPageNo = __checkForNextPage(sHtmlContent, iPage)
        if (sNextPageNo != False):
            params = ParameterHandler()
            params.setParam(PARAM_ROOTURL_KEY,sRootUrl)
            params.setParam(PARAM_URL_KEY, sRootUrl + '?page=' + sNextPageNo)
            params.setParam(PARAM_PAGE_KEY,int(sNextPageNo))
            oGui.addNextPage(SITE_IDENTIFIER, 'showMovies',params)

        oGui.setView('movies')
    else:
        oGui.showError('Fehler','Keine Eintraege gefunden')

def showAllSeasons():
    oGui = cGui()

    iParams = ParameterHandler()
    sUrl = iParams.getValue(PARAM_URL_KEY)
    sMovieTitle = iParams.getValue('sMovieTitle')
    sHtmlContent = cRequestHandler(sUrl).request()

    sPattern = '<option value="([0-9]+)">Staffel'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0] == True:
        logger.info("create season menu")
        Seasons = sorted([int(i) for i in aResult[1]])
        total = len(Seasons)
        for season in Seasons:
            oGuiElement = cGuiElement()
            oGuiElement.setSiteName(SITE_IDENTIFIER)
            oGuiElement.setFunction('showEpisodes')
            oGuiElement.setTitle('Staffel '+str(season))
            oGuiElement.setMediaType('season')
            oGuiElement.setSeason(season)

            oOutputParameterHandler = ParameterHandler()
            oOutputParameterHandler.setParam(PARAM_MOVIESEGMENT_KEY,iParams.getValue(PARAM_MOVIESEGMENT_KEY))
            oOutputParameterHandler.setParam(PARAM_ROOTURL_KEY, sUrl)
            oOutputParameterHandler.setParam(PARAM_URL_KEY, sUrl)
            oOutputParameterHandler.setParam('sMovieTitle',sMovieTitle)
            oOutputParameterHandler.setParam('season', season)

            oGui.addFolder(oGuiElement,oOutputParameterHandler, iTotal = total)
            logger.info('add object for season %s' % (season))

        logger.info("done")

    oGui.setView('seasons')
    oGui.setEndOfDirectory()

def showEpisodes():
    oGui = cGui()


    oParams = ParameterHandler()
    sSeason = oParams.getValue('season')
    sMovieTitle = oParams.getValue('sMovieTitle')
    sMovie = oParams.getValue(PARAM_MOVIESEGMENT_KEY).replace(".html","/")
    sUrl = URL_SERIES_EPISODEURL + sMovie
    oRequest = cRequestHandler(sUrl)
    #oRequest.setHeaderEntry("Accept","application/json, text/javascript, */*; q=0.01")
    oRequest.addParameters("season",sSeason)
    oRequest.addHeaderEntry("X-Requested-With","XMLHttpRequest")
    oRequest.addHeaderEntry('Referer', sUrl)
    oRequest.addHeaderEntry('Accept', '*/*')
    oRequest.addHeaderEntry('Host', SITE_NAME.lower())
    sHtmlContent = oRequest.request()
    aData = sorted(loads(sHtmlContent)['episodes'])
    for aEntry in aData:
        logger.info(aEntry['episode'])
        oGuiElement = cGuiElement()
        oGuiElement.setFunction('_playEpisode')
        oGuiElement.setSiteName(SITE_IDENTIFIER)
        oGuiElement.setTitle(sMovieTitle + '- S'+sSeason+'E'+str(aEntry['episode']))
        oGuiElement.setMediaType('episode')
        oGuiElement.setEpisode(aEntry['episode'])

        oOutputParameterHandler = ParameterHandler()
        oOutputParameterHandler.setParam('link',aEntry['link'])
        oOutputParameterHandler.setParam('season',sSeason)
        oOutputParameterHandler.setParam('episode',aEntry['episode'])
        oOutputParameterHandler.setParam('sMovieTitle',sMovieTitle)
        oOutputParameterHandler.setParam(PARAM_URL_KEY,"http://www.ecostream.tv/stream/"+aEntry['link']+".html")
        oGui.addFolder(oGuiElement, oOutputParameterHandler, bIsFolder=False, iTotal = len(aData))

    oGui.setView('episodes')
    oGui.setEndOfDirectory()

def _playEpisode():
    params = ParameterHandler()
    sUrl = params.getValue(PARAM_URL_KEY)
    results = []
    result = {}
    result['streamUrl'] = params.getValue(PARAM_URL_KEY)
    result['resolved'] = False
    result['title'] = params.getValue('sMovieTitle')+ '- S'+ params.getValue('season') + 'E' + params.getValue('episode')
    results.append(result)
    return results


def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if (sSearchText != False and sSearchText != ''):
        _search(oGui, sSearchText)
    else:
        return
    oGui.setEndOfDirectory()

def showCharacters():
    oGui = cGui()

    oInputParameterHandler = ParameterHandler()
    baseUrl = oInputParameterHandler.getValue(PARAM_URL_KEY)

    for letter in range(10):
        __createCharacters(oGui, letter, baseUrl)

    import string
    for letter in string.uppercase[:26]:
        __createCharacters(oGui, letter, baseUrl)
    oGui.setEndOfDirectory()


def showHosters():
    oInputParameterHandler = ParameterHandler()
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sUrl = oInputParameterHandler.getValue(PARAM_URL_KEY)
    sHtmlContent = cRequestHandler(sUrl).request()

    sPattern = '<a href="http://www.ecostream.tv/([^"]+)" target="_blank">Ecostream <small>([^<]+)</small>'
    aResult = cParser().parse(sHtmlContent, sPattern)
    results = []

    if aResult[0]: # multipart stream
        for aEntry in aResult[1]:
            result = {}
            result['streamUrl'] = 'http://www.ecostream.tv/'+aEntry[0]
            result['resolved'] = False
            result['title'] = sMovieTitle + ' ' +aEntry[1]
            results.append(result)
    return results

def _mediaIsASerie(sUrl):
    logger.info('check if %s is a serie' % (sUrl))

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, '<select class="seasonselect"')
    return aResult[0]

def __createCharacters(oGui, sCharacter, sBaseUrl):
    oGuiElement = cGuiElement()
    oGuiElement.setSiteName(SITE_IDENTIFIER)
    oGuiElement.setFunction('showMovies')
    oGuiElement.setTitle(str(sCharacter))
    sUrl = sBaseUrl  + str(sCharacter) + '/'
    oOutputParameterHandler = ParameterHandler()
    oOutputParameterHandler.setParam(PARAM_URL_KEY, sUrl)
    oOutputParameterHandler.setParam(PARAM_ROOTURL_KEY,sUrl)
    oOutputParameterHandler.setParam(PARAM_PAGE_KEY,1)
    oGui.addFolder(oGuiElement, oOutputParameterHandler)

def _search(oGui, sSearchText):
    sUrl = URL_SEARCH + sSearchText
    _parseMedia(sUrl,sUrl,1,PATTERN_LIST, oGui)

def __checkForNextPage(sHtmlContent, iCurrentPage):
    iNextPage = int(iCurrentPage) + 1
    iNextPage = str(iNextPage)

    sPattern = '<li><a href="\?page=([^"]+)">' + iNextPage + '</a></li>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if (aResult[0] == True):
        return aResult[1][0]
    return False

def __createMainMenuItem(oGui, sTitle, sUrl, sFunction):
    oGuiElement = cGuiElement()
    oGuiElement.setSiteName(SITE_IDENTIFIER)
    oGuiElement.setFunction(sFunction)
    oGuiElement.setTitle(sTitle)
    oOutputParameterHandler = ParameterHandler()

    if (sUrl != ''):
        oOutputParameterHandler.setParam(PARAM_PAGE_KEY,1)
        oOutputParameterHandler.setParam(PARAM_ROOTURL_KEY, sUrl)
        oOutputParameterHandler.setParam(PARAM_URL_KEY, sUrl)
    oGui.addFolder(oGuiElement, oOutputParameterHandler)