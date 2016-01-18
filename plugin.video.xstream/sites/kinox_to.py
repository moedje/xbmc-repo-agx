# -*- coding: utf-8 -*-
import urllib
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.util import cUtil
from resources.lib.config import cConfig
from resources.lib import logger
from json import loads
import re
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib import jsunprotect

SITE_IDENTIFIER = 'kinox_to'
SITE_NAME = 'Kinox.to'
SITE_ICON = 'kinox.png'
oConfig = cConfig()
domain = oConfig.getSetting('kinox_to-domain')
####
URL_MAIN = 'http://' + domain
URL_NEWS = URL_MAIN + '/index.php'
URL_CINEMA_PAGE = URL_MAIN + '/Cine-Films.html'
URL_GENRE_PAGE = URL_MAIN +'/Genre.html'
URL_MOVIE_PAGE = URL_MAIN + '/Movies.html'
URL_SERIE_PAGE = URL_MAIN + '/Series.html'
URL_DOCU_PAGE = URL_MAIN + '/Documentations.html'

URL_FAVOURITE_MOVIE_PAGE = URL_MAIN + '/Popular-Movies.html'
URL_FAVOURITE_SERIE_PAGE = URL_MAIN + '/Popular-Series.html'
URL_FAVOURITE_DOCU_PAGE = URL_MAIN + '/Popular-Documentations.html'

URL_LATEST_SERIE_PAGE = URL_MAIN + '/Latest-Series.html'
URL_LATEST_DOCU_PAGE = URL_MAIN + '/Latest-Documentations.html'

URL_SEARCH = URL_MAIN + '/Search.html'
URL_MIRROR = URL_MAIN + '/aGET/Mirror/'
URL_EPISODE_URL = URL_MAIN + '/aGET/MirrorByEpisode/'
URL_AJAX = URL_MAIN + '/aGET/List/'
URL_LANGUAGE = URL_MAIN + '/aSET/PageLang/1'


def load():
    logger.info("Load %s" % SITE_NAME)

    sSecurityValue = __getSecurityCookieValue()
    if sSecurityValue == '':
        pass
    elif sSecurityValue == False:
        return
    oParams = ParameterHandler()
    oParams.setParam('securityCookie', sSecurityValue)
    ## Create all main menu entries
    oGui = cGui()
    
    oParams.setParam('sUrl', URL_NEWS)
    oParams.setParam('page', 1)
    oParams.setParam('mediaType', 'news')
    oGui.addFolder(cGuiElement('Neues von Heute',SITE_IDENTIFIER,'showNews'),oParams)
    oParams.setParam('sUrl', URL_MOVIE_PAGE)
    oParams.setParam('mediaType', 'movie')
    oGui.addFolder(cGuiElement('Filme',SITE_IDENTIFIER,'showMovieMenu'),oParams)
    oParams.setParam('sUrl', URL_SERIE_PAGE)
    oParams.setParam('mediaType', 'series')
    oGui.addFolder(cGuiElement('Serien',SITE_IDENTIFIER,'showSeriesMenu'),oParams)
    oParams.setParam('sUrl', URL_DOCU_PAGE)
    oParams.setParam('mediaType', 'documentation')
    oGui.addFolder(cGuiElement('Dokumentationen',SITE_IDENTIFIER,'showDocuMenu'),oParams)
    oParams.setParam('sUrl', URL_SEARCH)
    oParams.setParam('mediaType', '')
    oGui.addFolder(cGuiElement('Suche',SITE_IDENTIFIER,'showSearch'),oParams)
    oGui.setEndOfDirectory()

######## Allgemeines
def __createMenuEntry(oGui, sFunction, sLabel, dOutputParameter):
  oParams = ParameterHandler()

  # Create all paramters out of lOuputParameter
  try:
    for param,value in dOutputParameter.items():
      oParams.setParam(param, value)
  except Exception, e:
    logger.error("Can't add parameter to menu entry with label: %s: %s" % (sLabel, e))
    #oParams = ""

  # Create the gui element
  oGuiElement = cGuiElement()
  oGuiElement.setSiteName(SITE_IDENTIFIER)
  oGuiElement.setFunction(sFunction)
  oGuiElement.setTitle(sLabel)
  oGui.addFolder(oGuiElement, oParams)
  
######## Seitenspezifisch 
def showMovieMenu():
    oGui = cGui()
    oParams = ParameterHandler()
    
    oGui.addFolder(cGuiElement('Kinofilme',SITE_IDENTIFIER,'showCinemaMovies'),oParams)
    oGui.addFolder(cGuiElement('A-Z',SITE_IDENTIFIER,'showCharacters'),oParams)
    oGui.addFolder(cGuiElement('Genres',SITE_IDENTIFIER,'showGenres'),oParams)
    oParams.setParam('sUrl', URL_FAVOURITE_MOVIE_PAGE)
    oGui.addFolder(cGuiElement('Beliebteste Filme', SITE_IDENTIFIER, 'showFavItems'),oParams)
    oGui.setEndOfDirectory()
    
def showSeriesMenu():
    oGui = cGui()
    oParams = ParameterHandler()
    
    oGui.addFolder(cGuiElement('A-Z',SITE_IDENTIFIER,'showCharacters'),oParams)
    #oGui.addFolder(cGuiElement('Genres',SITE_IDENTIFIER,'showGenres'),oParams)
    oParams.setParam('sUrl', URL_FAVOURITE_SERIE_PAGE)
    oGui.addFolder(cGuiElement('Beliebteste Serien',SITE_IDENTIFIER,'showFavItems'),oParams)
    oParams.setParam('sUrl', URL_LATEST_SERIE_PAGE)
    oGui.addFolder(cGuiElement('Neuste Serien',SITE_IDENTIFIER,'showFavItems'),oParams)
    oGui.setEndOfDirectory()
    
def showDocuMenu():
    oGui = cGui()
    oParams = ParameterHandler()
    
    oGui.addFolder(cGuiElement('A-Z',SITE_IDENTIFIER,'showCharacters'),oParams)
    #oGui.addFolder(cGuiElement('Genres',SITE_IDENTIFIER,'showGenres'),oParams)
    oParams.setParam('sUrl', URL_FAVOURITE_DOCU_PAGE)
    oGui.addFolder(cGuiElement('Beliebteste Dokumentationen',SITE_IDENTIFIER,'showFavItems'),oParams)
    oParams.setParam('sUrl', URL_LATEST_DOCU_PAGE)
    oGui.addFolder(cGuiElement('Neuste Dokumentationen',SITE_IDENTIFIER,'showFavItems'),oParams)
    oGui.setEndOfDirectory()

def __createLanguage(sLangID):
        if sLangID == "1":
            return 'de'
        elif sLangID == "2" or sLangID == "15":
            return 'en'
        elif sLangID == "7":
            return 'tu'
        elif sLangID == "4":
            return 'ch'
        elif sLangID == "5":
            return 'sp'
        elif sLangID == "6":
            return 'fr'
        elif sLangID == "8":
            return 'jp'
        elif sLangID == '11':
            return 'it'
        elif sLangID == "16":
            return 'nl'
        elif sLangID == "25":
            return 'ru'
        return sLangID

def __checkSubLanguage(sTitle):
        if not ' subbed*' in sTitle:
            return [sTitle, '']
        temp = sTitle.split(' *')            
        subLang = temp[-1].split('subbed*')[0].strip()
        title = ' '.join(temp[0:-1]).strip()
        if subLang == 'german':
            return [title, 'de']
        else:
            return [title, subLang] 


def __getHtmlContent(sUrl = None, sSecurityValue = None):
    oParams = ParameterHandler()
    # Test if a url is available and set it
    if sUrl is None and not oParams.exist('sUrl'):
        logger.error("There is no url we can request.")
        return False
    else:
        if sUrl is None:
            sUrl = oParams.getValue('sUrl')
    # Test if a security value is available
    if sSecurityValue is None:
        if oParams.exist("securityCookie"):
            sSecurityValue = oParams.getValue("securityCookie")
    if not sSecurityValue:
        sSecurityValue = ''
    # preferred language
    sPrefLang = __getPreferredLanguage()
    # Make the request
    oRequest = cRequestHandler(sUrl)
    oRequest.addHeaderEntry('Cookie', sPrefLang+sSecurityValue+'ListDisplayYears=Always;')
    oRequest.addHeaderEntry('Referer', URL_MAIN)
    oRequest.addHeaderEntry('Accept', '*/*')
    oRequest.addHeaderEntry('Host', domain)

    return oRequest.request()
    
def __getPreferredLanguage():
    sLanguage = oConfig.getSetting('prefLanguage')
    if sLanguage == '0':
        sPrefLang = 'ListNeededLanguage=25%2C24%2C26%2C2%2C5%2C6%2C7%2C8%2C11%2C15%2C16%2C9%2C12%2C13%2C14%2C17%2C4'
    elif sLanguage == '1':
        sPrefLang = 'ListNeededLanguage=25%2C24%2C26%2C5%2C6%2C7%2C8%2C11%2C15%2C16%2C9%2C12%2C13%2C14%2C17%2C4%2C1'
    else:
        sPrefLang = ''
    return sPrefLang    
  
def __getSecurityCookieValue():
    oRequestHandler = cRequestHandler(URL_NEWS, False)
    oRequestHandler.removeNewLines(False)
    oRequestHandler.removeBreakLines(False)
    sHtmlContent = oRequestHandler.request()
    sPattern = "var hash=\[(.*?)\]"
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0] == False:
        logger.error("Can't find script file for cookie")
    result = jsunprotect.jsunprotect(sHtmlContent)
    if not result:
        logger.error("Not protected or Deactivator not found")
        return ''
    else:
        logger.info(result)
        oRequestHandler = cRequestHandler(URL_MAIN+'/?'+result, False)
        oRequestHandler.addHeaderEntry('Referer', URL_MAIN)
        #oRequestHandler.addHeaderEntry('Accept', '*/*')
        oRequestHandler.addHeaderEntry('Host', domain)
        oRequestHandler.request()
        return ''
    for aEntry in aResult[1][0].split(","):
		sScriptFile = URL_MAIN +'/'+ str(aEntry).replace("'","").strip()
		sScriptFile.replace(" ","")

		logger.info("scriptfile: %s" % sScriptFile)
		oRequestHandler = cRequestHandler(sScriptFile)
		oRequestHandler.addHeaderEntry('Referer', URL_MAIN)
		oRequestHandler.addHeaderEntry('Accept', '*/*')
		oRequestHandler.addHeaderEntry('Host', domain)
		sHtmlContent = oRequestHandler.request()

    sPattern = "escape\(hsh \+ \"([^\"]+)\"\)"
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if not aResult[0]:
        logger.info("No hash value found for the cookie")
        return ''

    sHash = aResult[1][0]

    sHash = sHashSnippet + sHash
    sSecurityCookieValue = "sitechrx=" + str(sHash) + ";Path=/"

    oRequestHandler = cRequestHandler(URL_MAIN)
    oRequestHandler.addHeaderEntry("Cookie", sSecurityCookieValue)
    oRequestHandler.request()

    logger.info("Token: %s" % sSecurityCookieValue)

    return sSecurityCookieValue    
    
def showSearch():   
    oGui = cGui()
    # Show the keyboard and test if anything was entered
    sSearchText = oGui.showKeyBoard()
    if not sSearchText:
        oGui.setEndOfDirectory()
        return
    _search(oGui, sSearchText)
    oGui.setEndOfDirectory()

def _search(oGui, sSearchText):
    # Create the request with the search value
    sFullSearchUrl = URL_SEARCH + ("?q=%s" % sSearchText)
    logger.info("Search URL: %s" % sFullSearchUrl)
    sHtmlContent = __getHtmlContent(sFullSearchUrl)
    # Display all items returned...
    __displayItems(oGui, sHtmlContent)


def __displayItems(oGui, sHtmlContent):
    # Test if a cookie was set, else define the default empty one
    sSecurityValue = ""
    oParams = ParameterHandler()
    if oParams.exist("securityCookie"):
        sSecurityValue = oParams.getValue("securityCookie")

    # The pattern to filter every item of the list
    sPattern = '<td class="Icon"><img width="16" height="11" src="/gr/sys/lng/(\d+).png" alt="language"></td>'+\
    '.*?title="([^\"]+)".*?<td class="Title">.*?<a href="([^\"]+)" onclick="return false;">([^<]+)</a> <span class="Year">([0-9]+)</span>'

    # Parse to get all items of the list
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if not aResult[0]:
        logger.error("Could not find an item")
        return
    # Go throught all items and create a gui element for them.
    total = len(aResult[1])
    for aEntry in aResult[1]:
        sTitle = cUtil().unescape(aEntry[3])
        # split title and subtitle language
        sTitle, subLang = __checkSubLanguage(sTitle)
        # get audio language
        sLang = __createLanguage(aEntry[0])
        sUrl = URL_MAIN + aEntry[2]
        mediaType = ''
        if aEntry[1] == 'movie' or aEntry[1] == 'cinema':
            mediaType = 'movie'
        elif aEntry[1] == 'series': 
            mediaType = 'series'
        else:
            mediaType = 'documentation'

        oGuiElement = cGuiElement(sTitle, SITE_IDENTIFIER, 'parseMovieEntrySite')
        oGuiElement.setLanguage(sLang)
        oGuiElement.setSubLanguage(subLang)
        oGuiElement.setYear(aEntry[4])
        oParams.setParam('sUrl',sUrl)
        oParams.setParam('mediaType',mediaType)
        if mediaType == 'series':
            oGuiElement.setMediaType('tvshow')
            oGui.addFolder(oGuiElement, oParams, iTotal = total)
        elif mediaType == 'movie':
            oGuiElement.setMediaType('movie')
            oGui.addFolder(oGuiElement,oParams,bIsFolder=False, iTotal = total)
        else:
            oGui.addFolder(oGuiElement,oParams,bIsFolder=False, iTotal = total)

    
def showFavItems():
    oGui = cGui()
    sHtmlContent = __getHtmlContent()
    __displayItems(oGui, sHtmlContent)
    oGui.setEndOfDirectory()

    
def showNews():
    oParams = ParameterHandler()
    sSecurityValue = oParams.getValue('securityCookie')
    sUrl = oParams.getValue('sUrl')
    
    sPattern = '<div class="Opt leftOpt Headlne"><h1>([a-zA-Z0-9\s.]+)'+\
    '</h1></div>\s*<div class="Opt rightOpt Hint">Insgesamt: (.*?)</div>'
    
    sHtmlContent = __getHtmlContent(sUrl = sUrl, sSecurityValue = sSecurityValue)
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    oGui = cGui()
    if (aResult[0] == True):
        for aEntry in aResult[1]:
            sTitle = str(aEntry[0]) + ' (' + str(aEntry[1]) + ')'
            oGuiElement = cGuiElement(sTitle, SITE_IDENTIFIER,'parseNews')
            oParams.addParams({'sUrl':URL_NEWS, 'page':1, 'mediaType':'news', 'sNewsTitle':aEntry[0]})
            oGui.addFolder(oGuiElement, oParams)
    oGui.setEndOfDirectory()

    
def parseNews():
    oGui = cGui()

    oParams = ParameterHandler()
    sSecurityValue = oParams.getValue('securityCookie')
    sUrl = oParams.getValue('sUrl')
    sNewsTitle = oParams.getValue('sNewsTitle')
    oParser = cParser()
    aResult = oParser.parse(sNewsTitle, 'Neue (.*?) online')
    if aResult[0]:
        if str(aResult[1][0]) == 'Serien':
            mediaType = 'series'
        else:
            mediaType = 'movie'
    sPattern = '<div class="Opt leftOpt Headlne"><h1>'+sNewsTitle\
    +'</h1></div>(.*?)<div class="ModuleFooter">' 
    sHtmlContent = __getHtmlContent(sUrl = sUrl, sSecurityValue = sSecurityValue)   
    aResult = oParser.parse(sHtmlContent, sPattern)
    
    if not aResult[0]:
        logger.info("Can't get any news")
        oGui.setEndOfDirectory()
        return
    sPattern = '<td class="Icon"><img src="/gr/sys/lng/(\d+).png" alt="language" width="16" '+\
    'height="11".*?<td class="Title.*?rel="([^"]+)"><a href="([^\"]+)".*?class="OverlayLabel">([^<]+)<'+\
    '(span class="EpisodeDescr">)?([^<]+)'

    aResult = oParser.parse(aResult[1][0], sPattern)
    if not aResult[0]:
        logger.info("Can't get any news")
        oGui.setEndOfDirectory()
        return
    total = len(aResult[1])
    # Create an entry for every news line
    for aEntry in aResult[1]:
        sLang = __createLanguage(aEntry[0])
        sTitle = cUtil().unescape(aEntry[3]).strip()
        if sTitle.endswith(':'):
            sTitle = sTitle[:-1]
        sTitle, subLang = __checkSubLanguage(sTitle)
        sUrl = aEntry[2]
        # If there are several urls, just pick the first one
        aUrl = sUrl.split(",")
        if len(aUrl) > 0:
            sUrl = aUrl[0]
            oGuiElement = cGuiElement(sTitle, SITE_IDENTIFIER,'parseMovieEntrySite')
            oGuiElement.setLanguage(sLang)
            oGuiElement.setSubLanguage(subLang)
            oGuiElement.setThumbnail(URL_MAIN + str(aEntry[1]))

            oParams.setParam('sUrl',URL_MAIN + sUrl)
            oParams.setParam('mediaType',mediaType)
            if mediaType == 'series':
                oGuiElement.setMediaType('tvshow')
                oGui.addFolder(oGuiElement, oParams, iTotal = total)
                oGui.setView('tvshows')
            else:
                oGuiElement.setMediaType('movie')
                oGui.addFolder(oGuiElement, oParams, bIsFolder = False, iTotal = total)
                oGui.setView('movies')
    oGui.setEndOfDirectory()


def showCharacters():
  logger.info('load showCharacters') 
  oGui = cGui()

  oParams = ParameterHandler()
  sSecurityValue = oParams.getValue('securityCookie')
  if (oParams.exist('sUrl') and oParams.exist('page') and oParams.exist('mediaType')):
    siteUrl = oParams.getValue('sUrl')
    #iPage = oParams.getValue('page')
    #sMediaType = oParams.getValue('mediaType')
    # request
    sHtmlContent =__getHtmlContent(siteUrl, sSecurityValue)
    # parse content
    sPattern = 'class="LetterMode.*?>([^>]+)</a>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == True):
      for aEntry in aResult[1]:
        oGuiElement = cGuiElement(aEntry, SITE_IDENTIFIER, 'ajaxCall')
        #oOutputParameterHandler = ParameterHandler()
        oParams.setParam('character', aEntry[0])
        #oOutputParameterHandler.addParameter('page', iPage)
        #oOutputParameterHandler.addParameter('mediaType', sMediaType)
        #oOutputParameterHandler.addParameter('securityCookie', sSecurityValue)
        if oParams.exist('mediaTypePageId'):
            sMediaTypePageId = oParams.getValue('mediaTypePageId')
            oParams.setParam('mediaTypePageId', sMediaTypePageId)
        oGui.addFolder(oGuiElement, oParams)

  oGui.setEndOfDirectory()

def showGenres():
    logger.info('load displayGenreSite')
    sPattern = '<td class="Title"><a.*?href="/Genre/([^"]+)">([^<]+)</a>.*?Tipp-([0-9]+).html">'

    oParams = ParameterHandler()
    sSecurityValue = oParams.getValue('securityCookie')

    # request
    sHtmlContent =__getHtmlContent(URL_GENRE_PAGE, sSecurityValue)
    # parse content
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    oGui = cGui()
    if (aResult[0] == True):
        for aEntry in aResult[1]:
            iGenreId = aEntry[2]
            __createMenuEntry(oGui, 'showCharacters', aEntry[1],
            {'page':1, 'mediaType':'fGenre', 'mediaTypePageId': iGenreId,
            'securityCookie':sSecurityValue, 'sUrl':URL_MOVIE_PAGE})
    oGui.setEndOfDirectory()

def showCinemaMovies():
    logger.info('load displayCinemaSite')    
    oGui = cGui()   
    _cinema(oGui)
    oGui.setView('movies')
    oGui.setEndOfDirectory()
    
def _cinema(oGui):
    sPattern = '<div class="Opt leftOpt Headlne"><a title="(.*?)" href="(.*?)">.*?src="(.*?)".*?class="Descriptor">(.*?)</div.*?/lng/([0-9]+).png".*?IMDb:</b> (.*?) /'
    oParams = ParameterHandler()
    sSecurityValue = oParams.getValue('securityCookie')
    sHtmlContent = __getHtmlContent(URL_CINEMA_PAGE, sSecurityValue)
    # parse content
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    # iterate result and create GuiElements
    if (aResult[0] == True):
        total = len(aResult[1])
        for aEntry in aResult[1]:
            sMovieTitle = aEntry[0]
            lang = __createLanguage(aEntry[4])
            rating = aEntry[5]
            oGuiElement = cGuiElement()
            oGuiElement.setSiteName(SITE_IDENTIFIER)
            oGuiElement.setFunction('parseMovieEntrySite')
            oGuiElement.setLanguage(lang)
            oGuiElement.setTitle(sMovieTitle)
            oGuiElement.setDescription(aEntry[3])
            oGuiElement.setMediaType('movie')
            oGuiElement.setThumbnail(URL_MAIN + str(aEntry[2]))
            oGuiElement.addItemValue('rating',rating)
            oParams.setParam('sUrl', URL_MAIN + str(aEntry[1]))
            oGui.addFolder(oGuiElement, oParams, bIsFolder = False, iTotal = total)

def parseMovieEntrySite():
    oParams = ParameterHandler()
    sSecurityValue = oParams.getValue('securityCookie')
    if (oParams.exist('sUrl')):
        sUrl = oParams.getValue('sUrl')
        # get movieEntrySite content
        sHtmlContent = __getHtmlContent(sUrl, sSecurityValue)
        sMovieTitle = __createMovieTitle(sHtmlContent)
        # get thumbnail
        result = cParser().parse(sHtmlContent, '<div class="Grahpics">.*?<img src="([^"]+)"')
        thumbnail = ''
        if result[0]:
            thumbnail = URL_MAIN + str(result[1][0])

        bIsSerie = __isSerie(sHtmlContent)
        if (bIsSerie):
            oGui = cGui()
            aSeriesItems = parseSerieSite(sHtmlContent)
            if (len(aSeriesItems) > 0):
                imdbID = oParams.getValue('imdbID')
                for item in aSeriesItems:
                    oGuiElement = cGuiElement(item['title'], SITE_IDENTIFIER, 'showHosters')
                    sShowTitle = sMovieTitle.split('(')[0].split('*')[0]
                    oGuiElement.setThumbnail(thumbnail)
                    oGuiElement.setMediaType('episode')
                    oGuiElement.setSeason(item['season'])
                    oGuiElement.setEpisode(item['episode'])
                    oGuiElement.setTVShowTitle(sShowTitle)

                    oParams.addParams({'sUrl':item['url'], 'episode':item['episode'], 'season':item['season']})
                    oGui.addFolder(oGuiElement, oParams, bIsFolder = False, iTotal = len(aSeriesItems))
            oGui.setView('episodes')
            oGui.setEndOfDirectory()
        else:
            logger.info('Movie')
            result = showHosters(sHtmlContent, sMovieTitle)
            return result    

def __createMovieTitle(sHtmlContent):
    sPattern = '<h1><span style="display: inline-block">(.*?)</h1>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == True):
        sTitle = cUtil().removeHtmlTags(str(aResult[1][0]))
        return sTitle
    return False

def __createInfoItem(oGui, sHtmlContent):
  sThumbnail = __getThumbnail(sHtmlContent)
  sDescription = __getDescription(sHtmlContent)

  oGuiElement = cGuiElement()
  oGuiElement.setSiteName(SITE_IDENTIFIER)
  oGuiElement.setTitle('info (press Info Button)')
  oGuiElement.setThumbnail(sThumbnail)
  oGuiElement.setFunction('dummyFolder')
  oGuiElement.setDescription(sDescription)

  oOutputParameterHandler = ParameterHandler()
  oOutputParameterHandler.setParam('sThumbnail', sThumbnail)
  oOutputParameterHandler.setParam('sDescription', sDescription)

  oGui.addFolder(oGuiElement, oOutputParameterHandler)


def dummyFolder():
  oGui = cGui()
  oGui.setEndOfDirectory()


def parseSerieSite(sHtmlContent):
  aSeriesItems = []

  sPattern = 'id="SeasonSelection" rel="([^"]+)"'
  oParser = cParser()
  aResult = oParser.parse(sHtmlContent, sPattern)
  if (aResult[0] == True):
    aSeriesUrls = aResult[1][0].split("&amp;")
    sSeriesUrl = '&' + str(aSeriesUrls[0]) + '&' + str(aSeriesUrls[1])

    sPattern = '<option.*?rel="([^"]+)".*?>Staffel ([^<]+)</option'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if (aResult[0] == True):
      for aEntry in aResult[1]:
        aSeriesIds = aEntry[0].split(",")
        for iSeriesIds in aSeriesIds:
          aSeries = {}
          iEpisodeNum = iSeriesIds
          iSeasonNum = aEntry[1]
          sTitel = 'Staffel '+ str(iSeasonNum) + ' - ' + str(iEpisodeNum)
          sUrl = URL_EPISODE_URL + sSeriesUrl + '&Season=' + str(iSeasonNum) + '&Episode=' + str(iEpisodeNum)

          aSeries['title'] = sTitel
          aSeries['url'] = sUrl
          aSeries['season'] = iSeasonNum
          aSeries['episode'] = iEpisodeNum
          aSeriesItems.append(aSeries)
  return aSeriesItems


def __isSerie(sHtmlContent):
  sPattern = 'id="SeasonSelection" rel="([^"]+)"'
  oParser = cParser()
  aResult = oParser.parse(sHtmlContent, sPattern)

  if (aResult[0] == True):
    return True
  else:
    return False


def ajaxCall():
    oGui = cGui()
    metaOn = oGui.isMetaOn
    oParams = ParameterHandler()
    sSecurityValue = oParams.getValue('securityCookie')

    if (oParams.exist('page') and oParams.exist('mediaType')):
        iPage = oParams.getValue('page')
        sMediaType = oParams.getValue('mediaType')
    iMediaTypePageId = False
    if (oParams.exist('mediaTypePageId')):
        iMediaTypePageId = oParams.getValue('mediaTypePageId')
    sCharacter = 'A'
    if (oParams.exist('character')):
        sCharacter = oParams.getValue('character')

    logger.info('MediaType: ' + sMediaType + ' , Page: ' + str(iPage) + ' , iMediaTypePageId: ' + str(iMediaTypePageId) + ' , sCharacter: ' + str(sCharacter))

    sHtmlContent = __getAjaxContent(sMediaType, iPage, iMediaTypePageId, metaOn, sCharacter)
    if not sHtmlContent:
        return
    if metaOn and not sMediaType == 'documentation': 
        aData = loads(sHtmlContent)['aaData']
        total = len(aData)
        oParser = cParser()
        for aEntry in aData:
            sPattern = '<a href="([^"]+)".*?onclick="return false;">([^<]+)<.*?>([0-9]{4})<'
            aResult = oParser.parse(aEntry[2], sPattern)
            if (aResult[0] == True):
                sYear = str(aResult[1][0][2]).strip()
                sTitle = cUtil().unescape(aResult[1][0][1]).encode('utf-8')
                sLang = aEntry[0]
                sUrl = URL_MAIN + str(aResult[1][0][0])
                sUrl = sUrl.replace('\\', '')
                oGuiElement = cGuiElement(sTitle,SITE_IDENTIFIER,'parseMovieEntrySite')
                oGuiElement.setYear(sYear)
                oGuiElement.setLanguage(sLang)

                oParams.setParam('sUrl', sUrl)
                if sMediaType == 'series':
                    oGuiElement.setMediaType('tvshow')
                    oGui.addFolder(oGuiElement, oParams, iTotal = total)
                else:
                    oGuiElement.setMediaType('movie')
                    oGui.addFolder(oGuiElement, oParams, bIsFolder = False, iTotal = total)

        # check for next site
        sPattern = '"iTotalDisplayRecords":"([^"]+)'
        aResult = oParser.parse(sHtmlContent, sPattern)
        if (aResult[0] == True):
            for aEntry in aResult[1]:
                iTotalCount = aEntry[0]
                iNextPage = int(iPage) + 1
                iCurrentDisplayStart = __createDisplayStart(iNextPage)
                if (iCurrentDisplayStart < iTotalCount):
                    oParams = ParameterHandler()
                    oParams.setParam('page', iNextPage)
                    oParams.setParam('character', sCharacter)
                    oParams.setParam('mediaType', sMediaType)
                    oParams.setParam('securityCookie', sSecurityValue)
                if (iMediaTypePageId != False):
                    oParams.setParam('mediaTypePageId', iMediaTypePageId)
                oGui.addNextPage(SITE_IDENTIFIER, 'ajaxCall', oParams)

    else:
        aData = loads(sHtmlContent)
        sPattern = '<div class="Opt leftOpt Headlne"><a title="(.*?)" href="(.*?)">.*?src="(.*?)".*?class="Descriptor">(.*?)</div.*?lng/(.*?).png'
        # parse content
        oParser = cParser()
        aResult = oParser.parse(aData['Content'].encode('utf-8'), sPattern)
        # iterated result and create GuiElements
        if (aResult[0] == True):
            total = len(aResult[1])
            for aEntry in aResult[1]:
                sMovieTitle, subLang = __checkSubLanguage(aEntry[0])
                lang = __createLanguage(aEntry[4])
                oGuiElement = cGuiElement(sMovieTitle, SITE_IDENTIFIER, 'parseMovieEntrySite')
                oGuiElement.setDescription(aEntry[3])
                oGuiElement.setThumbnail(URL_MAIN + str(aEntry[2]))
                oGuiElement.setLanguage(lang)
                oGuiElement.setSubLanguage(subLang)
                oParams.setParam('sUrl', URL_MAIN + str(aEntry[1]))
                if sMediaType == 'series':
                    oGui.addFolder(oGuiElement, oParams, iTotal = total)
                else:
                    oGui.addFolder(oGuiElement, oParams, bIsFolder = False, iTotal = total)
            #next page
            iTotalCount = int(aData['Total'])
            iNextPage = int(iPage)+1           
            if __createDisplayStart(iNextPage) < iTotalCount:
                oParams = ParameterHandler()
                oParams.setParam('page', iNextPage)
                if (iMediaTypePageId != False):
                    oParams.setParam('mediaTypePageId', iMediaTypePageId)
                oGui.addNextPage(SITE_IDENTIFIER, 'ajaxCall', oParams)

    if sMediaType == 'series':
        oGui.setView('tvshows')
    else:
        oGui.setView('movies')
    oGui.setEndOfDirectory()


def __createDisplayStart(iPage):
  return (30 * int(iPage)) - 30


def __getAjaxContent(sMediaType, iPage, iMediaTypePageId, metaOn , sCharacter=''):
    iDisplayStart = __createDisplayStart(iPage)        
    oParams = ParameterHandler()
    # Test if a security value is available
    if oParams.exist("securityCookie"):
        sSecurityValue = oParams.getValue("securityCookie")
    else:
        sSecurityValue = ''
    # preferred language
    sPrefLang = __getPreferredLanguage()
    # perform the request
    oRequest = cRequestHandler(URL_AJAX)
    if (iMediaTypePageId == False):
        #{"fType":"movie","fLetter":"A"}
        oRequest.addParameters('additional', '{"fType":"' + str(sMediaType) + '","fLetter":"' + str(sCharacter) + '"}')
    else:
        #{"foo":"bar","fGenre":"2","fType":"","fLetter":"A"}
        oRequest.addParameters('additional', '{"foo":"bar","' + str(sMediaType) + '":"' + iMediaTypePageId + '","fType":"movie","fLetter":"' + str(sCharacter) + '"}')
    oRequest.addParameters('iDisplayLength', '30')
    oRequest.addParameters('iDisplayStart', iDisplayStart)
    if metaOn and not sMediaType == 'documentation':
        oRequest.addParameters('bSortable_0', 'true')
        oRequest.addParameters('bSortable_1', 'true')
        oRequest.addParameters('bSortable_2', 'true')
        oRequest.addParameters('bSortable_3', 'false')
        oRequest.addParameters('bSortable_4', 'false')
        oRequest.addParameters('bSortable_5', 'false')
        oRequest.addParameters('bSortable_6', 'true')
        oRequest.addParameters('iColumns', '7')
        oRequest.addParameters('iSortCol_0', '2')
        oRequest.addParameters('iSortingCols', '1')
        oRequest.addParameters('sColumns', '')
        oRequest.addParameters('sEcho', iPage)
        oRequest.addParameters('sSortDir_0', 'asc')
        sUrl = oRequest.getRequestUri()
        logger.info("Url: "+sUrl)
        oRequest = cRequestHandler(sUrl)
    else:
        oRequest.addParameters('ListMode', 'cover')
        oRequest.addParameters('Page', str(iPage))
        oRequest.addParameters('Per_Page', '30')
        oRequest.addParameters('dir', 'desc')
    oRequest.addHeaderEntry('Cookie', sPrefLang+sSecurityValue+'ListDisplayYears=Always;')
    oRequest.addHeaderEntry('Referer', URL_MAIN)
    oRequest.addHeaderEntry('Accept', '*/*')
    oRequest.addHeaderEntry('Host', domain)
    return oRequest.request()

def showHosters(sHtmlContent = '', sTitle = False):
    oParams = ParameterHandler()
    sSecurityValue = oParams.getValue('securityCookie')
    if (sTitle == False):
        sTitle = oParams.getValue('title')
    if (oParams.exist('sUrl')):
        sUrl = oParams.getValue('sUrl')
    
    sHtmlContent = __getHtmlContent(sUrl, sSecurityValue)
    sPattern = 'class="MirBtn.*?rel="([^"]+)".*?class="Named">([^<]+)</div>(.*?)</div>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    hosters = []
    if (aResult[0]):
        for aEntry in aResult[1]:
            sHoster = aEntry[1]
            # check for additional mirrors
            sPattern = '<b>Mirror</b>: [1-9]/([1-9])<br/>'
            oParser = cParser()
            aResult = oParser.parse(aEntry[2], sPattern)
            mirrors = 1
            if (aResult[0]):
                mirrors = int(aResult[1][0])
            for i in range(1,mirrors+1):
                sUrl = URL_MIRROR + urllib.unquote_plus(aEntry[0])
                mirrorName = ""
                if (mirrors > 1):
                    mirrorName = "  Mirror " +str(i)
                    sUrl = re.sub(r'Mirror=[1-9]','Mirror='+str(i),sUrl)
                hoster = {}
                hoster['name'] = sHoster
                hoster['link'] = sUrl
                hoster['displayedName'] = sHoster+mirrorName
                hosters.append(hoster)
        hosters.append('getHosterUrlandPlay') 
    return hosters
                        

def getHosterUrlandPlay(sUrl = False):
  results = []
  oParams = ParameterHandler()
  sSecurityValue = oParams.getValue('securityCookie')
  sTitle = oParams.getValue('title')
  if not sUrl:
    sUrl = oParams.getValue('url')
  sUrl = sUrl.replace('&amp;', '&')
  oRequest = cRequestHandler(sUrl)
  oRequest.addHeaderEntry('Cookie', sSecurityValue)
  oRequest.addHeaderEntry('Referer', URL_MAIN)
  sHtmlContent = oRequest.request()
  #pattern for multipart stream
  sPattern = '<a rel=\\\\"(.*?)\\\\"'
  oParser = cParser()
  aResult = oParser.parse(sHtmlContent, sPattern)
  if (aResult[0]):
    aMovieParts = aResult[1]
    ii = 1
    for sPartUrl in aMovieParts:
        sPartUrl = sPartUrl.replace('\\/', '/')
        oRequest = cRequestHandler(sUrl+'&Part='+str(ii))
        oRequest.addHeaderEntry('Cookie', sSecurityValue)
        oRequest.addHeaderEntry('Referer', URL_MAIN)
        sHtmlContent = oRequest.request()
        #pattern for stream url (single part)
        sPattern = '<a\shref=\\\\".*?(http:.*?)\\\\"'
        oParser = cParser()
        aResult = oParser.parse(sHtmlContent, sPattern)
        if (aResult[0]):
            aParts = aResult[1]
            sPartUrl = aParts[0].replace('\\/', '/')
            result = {}
            result['streamUrl'] = sPartUrl
            result['resolved'] = False
            result['title'] = sTitle + ' Part '+str(ii)
            results.append(result)
            ii +=1
  else:
    #pattern for stream url (single part)
    sPattern = '<a\shref=\\\\".*?(http:.*?)\\\\"'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if (aResult[0]):
        aMovieParts = aResult[1]
        sPartUrl = aMovieParts[0].replace('\\/', '/')
        result = {}
        result['streamUrl'] = sPartUrl
        result['resolved'] = False
        results.append(result)
  return results

  
# Metainformations on Moviepage
def __getDescription(sHtmlContent):
  sRegex = '<div class="Descriptore">([^<]+)<'
  oParser = cParser()
  aResult = oParser.parse(sHtmlContent, sRegex, 1)
  if (aResult[0] == True):
    return aResult[1][0]

  return ''


def __getThumbnail(sHtmlContent):
  sRegex = '<div class="Grahpics">.*? src="([^"]+)"'
  oParser = cParser()
  aResult = oParser.parse(sHtmlContent, sRegex)
  if (aResult[0] == True):
    return aResult[1][0]

  return ''


def __getDetails(sHtmlContent):
    sRegex = '<li class="DetailDat" title="Director"><span class="Director"></span>(.*?)</li><li class="DetailDat" title="Country"><span class="Country"></span>(.*?)</li><li class="DetailDat" title="Runtime"><span class="Runtime"></span>(.*?)</li><li class="DetailDat" title="Genre"><span class="Genre"></span>(.*?)</li><li class="DetailDat" title="Views"><span class="Views"></span>(.*?)</li>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sRegex)

    aDetails = {}

    if (aResult[0] == True):
      aDetails['writer'] = aResult[1][0][0]
      aDetails['country'] = aResult[1][0][1]
      aDetails['duration'] = aResult[1][0][2]
      aDetails['genre'] = aResult[1][0][3]
      aDetails['playcount'] = oParser.getNumberFromString(aResult[1][0][4])

    return aDetails