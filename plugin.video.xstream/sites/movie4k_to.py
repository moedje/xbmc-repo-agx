# -*- coding: utf-8 -*-
from resources.lib.util import cUtil
from resources.lib.parser import cParser
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.gui.gui import cGui
from resources.lib.config import cConfig
import re
import logger
from resources.lib import jsunprotect


SITE_IDENTIFIER = 'movie4k_to'
SITE_NAME = 'Movie4k.to'
SITE_ICON = 'movie2k.jpg'
oConfig = cConfig()
DOMAIN = oConfig.getSetting('movie4k_to-domain')
####
URL_MAIN = 'http://www.' + DOMAIN
URL_MOVIES = URL_MAIN + '/index.php'
URL_MOVIES_ALL = URL_MAIN + '/movies-all'
URL_MOVIES_GENRE = URL_MAIN + '/genres-movies.html'

URL_SERIES = URL_MAIN + '/tvshows_featured.php'
URL_SERIES_ALL = URL_MAIN + '/tvshows-all'
URL_SERIES_TOP = URL_MAIN + '/tvshows-top.html'
URL_SERIES_GENRE = URL_MAIN + '/genres-tvshows.html'

URL_XXX = URL_MAIN + '/xxx-updates.html'
URL_XXX_ALL = URL_MAIN +'/xxx-all'
URL_XXX_GENRE = URL_MAIN + '/genres-xxx.html'

URL_SEARCH = URL_MAIN + '/movies.php?list=search'


def load():
    oGui = cGui()
    __clearProtection()
    __createMainMenuItem(oGui, 'Filme', '', 'showMovieMenu')
    __createMainMenuItem(oGui, 'Serien', '', 'showSeriesMenu')
    if showAdult():
        __createMainMenuItem(oGui, 'XXX', '', 'showXXXMenu')
    __createMainMenuItem(oGui, 'Suche', '', 'showSearch')
    oGui.setEndOfDirectory()
    
def showMovieMenu():
    oGui = cGui()
    __createMainMenuItem(oGui, 'Kinofilme', URL_MOVIES, 'showFeaturedMovies')
    __createMainMenuItem(oGui, 'Alle Filme', URL_MOVIES_ALL, 'showCharacters')
    __createMainMenuItem(oGui, 'Genre', URL_MOVIES_GENRE, 'showGenre')
    oGui.setEndOfDirectory()
 
def showSeriesMenu():
    oGui = cGui()
    __createMainMenuItem(oGui, 'Featured', URL_SERIES, 'showFeaturedSeries')
    __createMainMenuItem(oGui, 'Alle Serien', URL_SERIES_ALL, 'showCharacters')
    __createMainMenuItem(oGui, 'Top Serien', URL_SERIES_TOP, 'parseMovieSimpleList')
    __createMainMenuItem(oGui, 'Genre', URL_SERIES_GENRE, 'showGenre')
    oGui.setEndOfDirectory()
    
def showXXXMenu():
    oGui = cGui()
    __createMainMenuItem(oGui, 'Aktuelles', URL_XXX, 'showFeaturedMovies')
    __createMainMenuItem(oGui, 'Alle XXXFilme', URL_XXX_ALL, 'showCharacters')
    __createMainMenuItem(oGui, 'Genre', URL_XXX_GENRE, 'showGenre')
    oGui.setEndOfDirectory()

def __getHtmlContent(sUrl = False, sSecurityValue = False):
    params = ParameterHandler()
    # Test if a url is available and set it
    if not sUrl:
        sUrl = params.getValue('siteUrl')
        if not sUrl:
            logger.info('no request url given')

    # Test is a security value is available
    if not sSecurityValue:
        sSecurityValue = params.getValue('securityCookie')
        if not sSecurityValue:
            sSecurityValue = ''
    # preferred language
    sPrefLang = __getPreferredLanguage()
    # adult Cookie
    if showAdult():
        adultCookie ='xxx2=ok;'
    else:
        adultCookie = ''
    # Make the request
    oRequest = cRequestHandler(sUrl)
    oRequest.addHeaderEntry('Cookie', sPrefLang+sSecurityValue+adultCookie)
    return oRequest.request()
    
def __getPreferredLanguage():
    oConfig = cConfig()
    sLanguage = oConfig.getSetting('prefLanguage')
    if sLanguage == '0':
        sPrefLang = 'lang=de;onlylanguage=de;'
    elif sLanguage == '1':
        sPrefLang = 'lang=us;onlylanguage=en;'
    else:
        sPrefLang = ''
    return sPrefLang
    
def showAdult():
    oConfig = cConfig()
    if oConfig.getSetting('showAdult')=='true':    
        return True
    return False 
    
def __clearProtection():
    oRequestHandler = cRequestHandler(URL_MAIN+'/index.php', False)
    oRequestHandler.removeNewLines(False)
    oRequestHandler.removeBreakLines(False)
    sHtmlContent = oRequestHandler.request()
    result = jsunprotect.jsunprotect(sHtmlContent)
    if not result:
        logger.info("Not protected or Deactivator not found")
        return ''
    else:
        logger.info(result)
        oRequestHandler = cRequestHandler(URL_MAIN+'?'+result, False)
        oRequestHandler.addHeaderEntry('Referer', URL_MAIN)
        oRequestHandler.addHeaderEntry('Host', 'www.'+DOMAIN)
        oRequestHandler.request()
        return ''
    
def showCharacters():
    oGui = cGui()
    
    params = ParameterHandler()
    baseUrl = params.getValue('sUrl')

    __createCharacters(oGui, '#', baseUrl)
    import string   
    for letter in string.uppercase[:26]:
        __createCharacters(oGui, letter, baseUrl) 
    oGui.setEndOfDirectory()

def __createCharacters(oGui, sCharacter, sBaseUrl):
    oGuiElement = cGuiElement()
    oGuiElement.setSiteName(SITE_IDENTIFIER)
    oGuiElement.setFunction('parseMovieSimpleList') 
    oGuiElement.setTitle(sCharacter)
    if (sCharacter == '#'):
        sUrl = sBaseUrl + '-1-1.html'
    else:
        sUrl = sBaseUrl + '-' + str(sCharacter) + '-1.html'
    oOutputParameterHandler = ParameterHandler()
    oOutputParameterHandler.setParam('sUrl', sUrl)
    oGui.addFolder(oGuiElement, oOutputParameterHandler)        
        
def showAllSeasons():
    params = ParameterHandler()
    sUrl = ''
    if (params.exist('sUrl')):
        sUrl = params.getValue('sUrl')
        __getAllSeasons(sUrl)
    else:
        return

def __getAllSeasons(sUrl):
    oGui = cGui()
    oRequest = cRequestHandler(sUrl)
    sHtmlContent = oRequest.request()

    sPattern = '<SELECT name="season".*?>(.*?)</SELECT>'
    oParser = cParser()
    
    aResult = oParser.parse(sHtmlContent, sPattern)
    if not aResult[0]:
        return
    sPattern = '<OPTION value="(\d+)".*?>([^<]+)</OPTION>'
    aResult = oParser.parse(sHtmlContent,sPattern)
    if (aResult[0] == True):
        total = len(aResult[1])
        for aEntry in aResult[1]:
            season = aEntry[0]
            oGuiElement = cGuiElement()
            oGuiElement.setSiteName(SITE_IDENTIFIER)
            oGuiElement.setFunction('showAllEpisodes')

            sTitle = aEntry[1].strip()
            oGuiElement.setTitle(sTitle)
            oGuiElement.setSeason(season)
            oGuiElement.setMediaType('season')

            oOutputParameterHandler = ParameterHandler()
            oOutputParameterHandler.setParam('sUrl', sUrl)
            oOutputParameterHandler.setParam('season', season)
                
            oGui.addFolder(oGuiElement, oOutputParameterHandler, iTotal = total)
    oGui.setView('seasons')
    oGui.setEndOfDirectory()
        
def showAllEpisodes():
    oGui = cGui()
    params = ParameterHandler()
    sUrl = ''
    if not params.exist('sUrl'):
        return
    sUrl = params.getValue('sUrl')
    if  not params.exist('season'):
        return
    sSeason = params.getValue('season')
    oRequest = cRequestHandler(sUrl)
    sHtmlContent = oRequest.request()


        
    sPattern = '<FORM name="episodeform' + sSeason + '">(.*?)</FORM>'
    aResult = cParser().parse(sHtmlContent, sPattern)
    sHtmlContent = aResult[1][0]

    sPattern = '<SELECT name="episode".*?>(.*?)</SELECT>'
    oParser = cParser()
    
    aResult = oParser.parse(sHtmlContent, sPattern)
    if not aResult[0]:
        return
    sPattern = '<OPTION value="([^"]+)".*?>([^<]+)</OPTION>'
    aResult = oParser.parse(aResult[1][0],sPattern)
    if not aResult[0]:
        return
    for aEntry in aResult[1]:
        sUrl = aEntry[0]
        if not sUrl.startswith('http'):
            sUrl = URL_MAIN +'/'+ sUrl
        sMovieTitle = aEntry[1].strip()
        episodeNr = aEntry[1].strip().split(' ')[-1]
                
        oGuiElement = cGuiElement(sMovieTitle, SITE_IDENTIFIER, 'showHostersSeries')
        oGuiElement.setEpisode(episodeNr)
        if sSeason:
            oGuiElement.setSeason(sSeason)
        oGuiElement.setMediaType('episode')
                  
        params.setParam('sUrl', sUrl)
        params.setParam('sMovieTitle', sMovieTitle) 
        params.setParam('episode', episodeNr)               
        oGui.addFolder(oGuiElement, params, bIsFolder = False, iTotal = len(aResult[1]))
    oGui.setView('episodes')
    oGui.setEndOfDirectory()    
    
def showSearch():
    oGui = cGui()

    sSearchText = oGui.showKeyBoard()
    if (sSearchText != False and sSearchText != ''):
        _search(oGui, sSearchText)
    else:
        return
    oGui.setView('movies')
    oGui.setEndOfDirectory()

def _search(oGui, sSearchText):
    # add wildcard to find results where seatchText is part of a word
    sSearchText = '%'+sSearchText+'%'
    # perform search
    oRequest = cRequestHandler(URL_SEARCH)
    oRequest.addParameters('search', sSearchText)
    #oRequest.addParameters('securekey', key)
    response = oRequest.request()
    sUrl = URL_SEARCH
    __parseMovieSimpleList(sUrl, 1, oGui, response)

def __checkForNextPage(sHtmlContent, iCurrentPage):
    iNextPage = int(iCurrentPage) + 1
    iNextPage = str(iNextPage) + ' '

    sPattern = '<a href="([^"]+)">' + iNextPage + '</a>'

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if (aResult[0] == True):
        return aResult[1][0]
    return False

def showGenre():
    oGui = cGui()

    params = ParameterHandler()
    if (params.exist('sUrl')):
        sUrl = params.getValue('sUrl')

        oRequest = cRequestHandler(sUrl)
        sHtmlContent = oRequest.request()

        sPattern = '<TR>.*?<a href="([^"]+)">([^<]+)</a>.*?>([^<]+)</TD>'

        oParser = cParser()
        aResult = oParser.parse(sHtmlContent, sPattern)

        if (aResult[0] == True):
            for aEntry in aResult[1]:
                sUrl = aEntry[0].strip()
                if not (sUrl.startswith('http')):
                    sUrl = URL_MAIN +'/'+ sUrl
                sTitle = aEntry[1] + ' (' + aEntry[2] + ')'
                
                oGuiElement = cGuiElement()
                oGuiElement.setSiteName(SITE_IDENTIFIER)
                oGuiElement.setFunction('parseMovieSimpleList')
                oGuiElement.setTitle(sTitle)

                oOutputParameterHandler = ParameterHandler()
                oOutputParameterHandler.setParam('sUrl', sUrl)
                oGui.addFolder(oGuiElement, oOutputParameterHandler)

        oGui.setEndOfDirectory()

def parseMovieSimpleList():
    oGui = cGui()
    params = ParameterHandler()
    oParser = cParser()
    
    if (params.exist('iPage')):
        iPage = params.getValue('iPage')
    else:
        iPage = 1

    if (params.exist('sUrl')):
        sUrl = params.getValue('sUrl')
        logger.info(sUrl)
        if (sUrl.find('tvshows-season-') != -1):
            sPattern = '<TR>\s*<TD.*?id="tdmovies".*?<a href="([^"]+)">(.*?)\s*</a>.*?<img border=0 src="http://[^/]+/img/([^"]+)".*?</TR>'
            if params.exist('sLanguageToken'):
                sLanguageToken = params.getValue('sLanguageToken')
                oRequest = cRequestHandler(sUrl)
                sHtmlContent = oRequest.request()
                aResult = oParser.parse(sHtmlContent, sPattern)
                if aResult[0] == True:
                    for aEntry in aResult[1]:
                        sUrl = str(aEntry[0]).strip()
                        if not (sUrl.startswith('http')):
                            sUrl = URL_MAIN +'/'+ sUrl
                        if aEntry[2] == sLanguageToken:
                            break
                    oRequest = cRequestHandler(sUrl)
                    sHtmlContent = oRequest.request()
                    aResult = oParser.parse(sHtmlContent, sPattern)
                    if aResult[0] == True:
                        for aEntry in aResult[1]:
                            sUrl = str(aEntry[0]).strip()
                            if not (sUrl.startswith('http')):
                                sUrl = URL_MAIN +'/'+ sUrl
                            if aEntry[2] == sLanguageToken:
                                break
                                
            else:
                oRequest = cRequestHandler(sUrl)
                sHtmlContent = oRequest.request()
                aResult = oParser.parse(sHtmlContent, sPattern)
                if aResult[0] == True:
                    sUrl = str(aResult[1][0][0]).strip()
                    if not (sUrl.startswith('http')):
                        sUrl = URL_MAIN + sUrl
                    oRequest = cRequestHandler(sUrl)
                    sHtmlContent = oRequest.request()
                    aResult = oParser.parse(sHtmlContent, sPattern)
                    if aResult[0] == True:
                        sUrl = str(aResult[1][0][0]).strip()
                        if not (sUrl.startswith('http')):
                            sUrl = URL_MAIN +'/'+ sUrl
            __getAllSeasons(sUrl)
            
        else:
            __parseMovieSimpleList(sUrl, iPage, oGui)
            oGui.setView('movies')
            oGui.setEndOfDirectory()
      
def __parseMovieSimpleList(sUrl, iPage, oGui, sHtmlContent = False):
    oParser = cParser()
    if not sHtmlContent:
        oRequest = cRequestHandler(sUrl)
        sHtmlContent = __getHtmlContent(sUrl)
    
    sPattern = '<TR.*?<TD.*?id="tdmovies".*?<a href="([^"]+)">(.*?)\s*</a>.*?<img border=0 src="/img/([^"]+)".*?</TR>'
    aResult = oParser.parse(sHtmlContent, sPattern)

    pattern = "coverPreview([0-9]+)\"\)\.hover.*?<p id='coverPreview'><img src='(.*?)' alt='Image preview'"
    result = re.finditer(pattern, sHtmlContent, re.DOTALL)
    thumbs = dict()
    for set in result:
        id, thumb = set.groups()
        thumbs.update({id:thumb})
    if (aResult[0] == True):
        total = len(aResult[1])
        for aEntry in aResult[1]:
            newUrl = aEntry[0].strip()
            if not (newUrl.startswith('http')):
                newUrl = URL_MAIN +'/'+ newUrl
            sMovieTitle = cUtil().unescape(aEntry[1].strip().decode('utf-8')).encode('utf-8')
            sMovieTitle = ' '.join(sMovieTitle.split())
            sMovieTitle = ' '.join(sMovieTitle.split())
            sLanguageToken = aEntry[2]
                       
            oGuiElement = cGuiElement()
            oGuiElement.setSiteName(SITE_IDENTIFIER)
            oGuiElement.setTitle(sMovieTitle)
            oGuiElement.setLanguage(__getLanguage(sLanguageToken.replace('.png','')))

            oOutputParameterHandler = ParameterHandler()            
            oOutputParameterHandler.setParam('sMovieTitle', sMovieTitle)
            oOutputParameterHandler.setParam('sUrl', newUrl)
            
            type, id = getTypeAndID(newUrl)
            if type == 'tvshow':
                if sUrl.find(URL_SERIES_TOP) != -1:
                    oGuiElement.setFunction('showHostersSeries')
                elif sUrl.find('tvshows-') != -1:
                    oOutputParameterHandler.setParam('sLanguageToken',sLanguageToken)
                    oGuiElement.setMediaType('tvshow')
                    oGuiElement.setFunction('parseMovieSimpleList')
                else:
                    oGuiElement.setFunction('showAllSeasons')
            elif type == 'movie':
                oGuiElement.setMediaType('movie')
                oGuiElement.setFunction('showHosters')
            else:
                oOutputParameterHandler.setParam('sLanguageToken',sLanguageToken)
                oGuiElement.setFunction('parseMovieSimpleList')
            if id in thumbs:
                oGuiElement.setThumbnail(thumbs[id].replace('4k.to','4k.tv'))
            if type == 'movie':
                oGui.addFolder(oGuiElement, oOutputParameterHandler, bIsFolder = False, iTotal = total)
            else:
                oGui.addFolder(oGuiElement, oOutputParameterHandler, iTotal = total)
    
    sNextUrl = __checkForNextPage(sHtmlContent, iPage)
    if (sNextUrl != False):      
        if not (sNextUrl.startswith(URL_MAIN)):
            sNextUrl = URL_MAIN +'/'+ sNextUrl     
        params = ParameterHandler()
        params.setParam('sUrl', sNextUrl)
        params.setParam('iPage', int(iPage) + 1)
        oGui.addNextPage(SITE_IDENTIFIER, 'parseMovieSimpleList',params)
    return oGui

def getTypeAndID(url):    
    #####################################################################
    # Examples:
    # http://www.movie4k.to/Die-Simpsons-online-serie-656673.html
    # http://www.movie4k.to/Die-Simpsons-Der-Film-online-film-783507.html
    # http://www.movie4k.to/The-Simpsons-watch-tvshow-660732.html
    # http://www.movie4k.to/The-Simpsons-Movie-watch-movie-693640.html
    #####################################################################
    sPattern = '([^-]+)-(\d+).html$'
    aResult = cParser().parse(url, sPattern)
    if aResult[0] == True:
        match = aResult[1][0]
        type = match[0]
        id = match[1]
        if type in ['serie','tvshow','tvshows']:
            return 'tvshow',id
        elif type in ['film','movie']:
            return 'movie',id
    return '',''
    
def showFeaturedMovies():
    params = ParameterHandler()
    if (params.exist('sUrl')):
        sUrl = params.getValue('sUrl')
        sHtmlContent = __getHtmlContent(sUrl = sUrl)
        sPattern = ('<div style="float:left">\s*<a href="([^"]+)".{0,1}><img src="([^"]+)".*?alt="([^"]+)".*?'
                    '<img src="(.*?)".*?IMDB Rating: <a href="http://www.imdb.de/title/[0-9a-zA-z]+" '
                    'target="_blank">(.*?)</a>.*?smileys/([0-9])\.gif.*?class="info"><STRONG>.*?</STRONG><BR>(.*?)(?:<BR>|</div>).*?id="xline">')
        aResult = cParser().parse(sHtmlContent, sPattern)
        if (aResult[0] == True):
            oGui = cGui()
            total = len(aResult[1])
            for aEntry in aResult[1]:
                newUrl = aEntry[0]
                if not (newUrl.startswith('http')):
                    newUrl = URL_MAIN +'/'+ newUrl
                
                sThumbnail = aEntry[1]             
                sMovieTitle = cUtil().unescape(aEntry[2].strip().replace('kostenlos', ''))                
                
                oGuiElement = cGuiElement()
                oGuiElement.setSiteName(SITE_IDENTIFIER)
                oGuiElement.setFunction('showHosters')
                oGuiElement.setMediaType('movie')
                fRating = float(aEntry[4])
                sDescription = cUtil().unescape(aEntry[6].strip().decode('utf-8')).encode('utf-8')
                sDescription = cUtil().removeHtmlTags(sDescription)
                oGuiElement.setDescription(sDescription)
                oGuiElement.addItemValue('Rating',fRating)
                oGuiElement.setThumbnail(sThumbnail.replace('https','http'))           
                oGuiElement.setTitle(sMovieTitle)
                oGuiElement.setLanguage(__getLanguage(aEntry[3]))
                oGuiElement._sQuality = aEntry[5]            
                oOutputParameterHandler = ParameterHandler()
                oOutputParameterHandler.setParam('sUrl', newUrl)
                oOutputParameterHandler.setParam('sMovieTitle', sMovieTitle)
                
                oGui.addFolder(oGuiElement, oOutputParameterHandler, bIsFolder=False, iTotal = total)
            oGui.setView('movies')
            oGui.setEndOfDirectory()

def showFeaturedSeries():
    params = ParameterHandler()
    if (params.exist('sUrl')):
        sUrl = params.getValue('sUrl')

        oRequest = cRequestHandler(sUrl)
        sHtmlContent = oRequest.request()
        
        sPattern = '<div id="maincontenttvshow">(.*?)<BR><BR>'
        aResult = cParser().parse(sHtmlContent,sPattern)
        if aResult[0] == True:
            sPattern = '<div style="float:left"><a href="([^"]+)"><img src="([^"]+)" border=0.*?title="([^"]+)"></a>.*?<img src="/img/(.*?).png"'
            sHtmlContent = aResult[1][0]
            aResult = cParser().parse(sHtmlContent, sPattern)
            if aResult[0] == True:
                oGui = cGui()
                for aEntry in aResult[1]:
                    newUrl = str(aEntry[0]).strip()
                    if not (newUrl.startswith('http')):
                        newUrl = URL_MAIN +'/'+ newUrl
                    sThumbnail = aEntry[1]
                    sMovieTitle = aEntry[2].strip().replace('\t', '')                     
                    oGuiElement = cGuiElement()
                    oGuiElement.setSiteName(SITE_IDENTIFIER)
                    oGuiElement.setFunction('showAllSeasons')
                    oGuiElement.setTitle(sMovieTitle)
                    oGuiElement.setThumbnail(sThumbnail.replace('https','http'))
                    oGuiElement.setLanguage(__getLanguage(aEntry[3]))
                    oGuiElement.setMediaType('tvshow')
                    oOutputParameterHandler = ParameterHandler()
                    oOutputParameterHandler.setParam('sUrl', newUrl)
                    
                    oGui.addFolder(oGuiElement, oOutputParameterHandler)
                oGui.setView('tvshows')
                oGui.setEndOfDirectory()
        

def showHostersSeries():
    params = ParameterHandler()
    if (params.exist('sUrl') and params.exist('sMovieTitle')):
        sUrl = params.getValue('sUrl')
        sMovieTitle = params.getValue('sMovieTitle')
        
        sHtmlContent = cRequestHandler(sUrl).request()        
        sPattern = '<tr id="tablemoviesindex2".*?<a href="([^"]+)".*? width="16">([^<]+)<'
        aResult = cParser().parse(sHtmlContent.replace('\\',''), sPattern)       
        if (aResult[0] == True):
            hosters = []
            previousName = ''
            iMatches = 2
            for aEntry in aResult[1]:
                sHoster = aEntry[1].strip()
                hoster = {}
                hoster['name'] = sHoster
                hoster['link'] = URL_MAIN +'/'+ aEntry[0] 
                if hoster['name'] == previousName:
                    hoster['displayedName'] = hoster['name'] + ' ('+str(iMatches)+')'
                    iMatches += 1
                else:
                    previousName = hoster['name']
                    iMatches = 2            
                hosters.append(hoster)
            hosters.append('showHoster')
            return hosters
        
def showHosters():
    params = ParameterHandler()
    if (params.exist('sUrl') and params.exist('sMovieTitle')):
        sUrl = params.getValue('sUrl')
        sMovieTitle = params.getValue('sMovieTitle')
        
        sHtmlContent = cRequestHandler(sUrl).request()
        sPattern = '<tr id="tablemoviesindex2">.*?<a href="([^"]+)">([^<]+)<.*?alt="(.*?) .*?width="16">.*?</a>.*?smileys/([1-9]).gif"'
        aResult = cParser().parse(sHtmlContent.replace('\\',''), sPattern)
        if (aResult[0] == True):
            hosters = []
            for aEntry in aResult[1]:
                sHoster = aEntry[2].strip()
                hoster = {}
                hoster['name'] = sHoster
                hoster['link'] = URL_MAIN +'/'+ aEntry[0]
                hoster['displayedName'] = aEntry[1] + ' - ' + sHoster + ' - Quality: ' + aEntry[3]
                hoster['quality'] = aEntry[3]
                hoster['date'] = aEntry[1].strip()
                hosters.append(hoster)
            hosters.append('showHoster')
            return hosters

def showHoster(sUrl=False):
    params = ParameterHandler()
    if not sUrl:
        sUrl = params.getValue('url') 
    sMovieTitle = params.getValue('sMovieTitle')    
    #type,id = getTypeAndID(sUrl)
    sHtmlContent = cRequestHandler(sUrl).request()

    #if type == 'Film' or type=='Serie':
    sPattern = '<a href="(movie.php\?id=(\d+)&part=(\d+))">'
    aResult = cParser().parse(sHtmlContent, sPattern)
    results = []
    if aResult[0]: # multipart stream
        for aEntry in aResult[1]:
            result = parseHosterDirect(sHtmlContent)#, sHoster.lower(), sMovieTitle)
            result['title'] = sMovieTitle + ' Part ' + aEntry[2]
            results.append(result)  
        return results
    else:
        result = parseHosterDirect(sHtmlContent)#, sHoster.lower(), sMovieTitle)
        results.append(result)
        return results
  
            
def __getMovieTitle(sHtmlContent):
    sPattern = '<title>(.*?) online anschauen.*?</title>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == True):
        return str(aResult[1][0]).strip()
    else:
        sPattern = 'Watch (.*?) online.*?</title>'
        aResult = oParser.parse(sHtmlContent, sPattern)

        if (aResult[0] == True):
            return str(aResult[1][0]).strip()
    return False

def parseHosterDirect(sHtmlContent, sHoster = '', sMovieTitle = ''):
    oParser = cParser()
    #Link oder Iframe suchen der den Hosternamen enthält
    sPattern = 'id="maincontent5".*?(?:target="_blank" href|iframe[^<]+src|value)="([^"]+)".*?id="underplayer">'
    aResult = oParser.parse(sHtmlContent, sPattern)
    if (aResult[0] == True):
        sStreamUrl = aResult[1][0]    
        result = {}
        result['streamUrl'] = sStreamUrl
        result['resolved'] = False
        return result
    return False
    
def __getLanguage(sString):
    if 'us_ger_small' in sString:
        return 'de'
    return 'en'

def __createMainMenuItem(oGui, sTitle, sUrl, sFunction):
    oGuiElement = cGuiElement()
    oGuiElement.setSiteName(SITE_IDENTIFIER)
    oGuiElement.setFunction(sFunction)
    oGuiElement.setTitle(sTitle)
    oOutputParameterHandler = ParameterHandler()
    if (sUrl != ''):
        oOutputParameterHandler.setParam('sUrl', sUrl)
    oGui.addFolder(oGuiElement, oOutputParameterHandler)
