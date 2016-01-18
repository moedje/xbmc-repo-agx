# -*- coding: utf-8 -*-
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib import logger
from resources.lib.handler.ParameterHandler import ParameterHandler


SITE_IDENTIFIER = 'kinoleak'
SITE_NAME = 'KinoLeak.Tv'
SITE_ICON = 'kinoleak.png'

URL_MAIN = 'http://kinoleak.tv/'
URL_NEW  = 'http://kinoleak.tv/index.php?site=Addons&do=NewMovies'
URL_ALL  = 'http://kinoleak.tv/index.php?site=Addons&do=ALLMovies'

URL_COMEDY    = 'http://kinoleak.tv/index.php?site=Addons&do=Genres&S=Komödie'
URL_ACTION    = 'http://kinoleak.tv/index.php?site=Addons&do=Genres&S=Action'
URL_HORROR    = 'http://kinoleak.tv/index.php?site=Addons&do=Genres&S=Horror'
URL_THRILLER  = 'http://kinoleak.tv/index.php?site=Addons&do=Genres&S=Thriller'
URL_DRAMA     = 'http://kinoleak.tv/index.php?site=Addons&do=Genres&S=Drama'
URL_FANTASY   = 'http://kinoleak.tv/index.php?site=Addons&do=Genres&S=Fantasy'
URL_ADVENTURE = 'http://kinoleak.tv/index.php?site=Addons&do=Genres&S=Abenteuer'
URL_ANIMATION = 'http://kinoleak.tv/index.php?site=Addons&do=Genres&S=Animation'
URL_SCIFI     = 'http://kinoleak.tv/index.php?site=Addons&do=Genres&S=Sci-Fi'


def load():
  oGui = cGui()
  oGui.addFolder(cGuiElement('Neuste Filme', SITE_IDENTIFIER, 'showNewMovies'))
  oGui.addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'))
  oGui.addFolder(cGuiElement('Alle Filme', SITE_IDENTIFIER, 'showAllMovies'))
  oGui.addFolder(cGuiElement('Sci-Fi', SITE_IDENTIFIER, 'showGenreSciFi'))
  oGui.addFolder(cGuiElement('Komödie', SITE_IDENTIFIER, 'showGenreKomoedie'))
  oGui.addFolder(cGuiElement('Action', SITE_IDENTIFIER, 'showGenreAction'))
  oGui.addFolder(cGuiElement('Horror', SITE_IDENTIFIER, 'showGenreHorror'))  
  oGui.addFolder(cGuiElement('Thriller', SITE_IDENTIFIER, 'showGenreThriller'))
  oGui.addFolder(cGuiElement('Drama', SITE_IDENTIFIER, 'showGenreDrama'))
  oGui.addFolder(cGuiElement('Fantasy', SITE_IDENTIFIER, 'showGenreFantasy'))
  oGui.addFolder(cGuiElement('Abenteuer', SITE_IDENTIFIER, 'showGenreAbenteuer'))
  oGui.addFolder(cGuiElement('Animation', SITE_IDENTIFIER, 'showGenreAnimation'))
  oGui.setEndOfDirectory()

def showNewMovies():
    _parseMovieList(URL_NEW)

def showAllMovies():
    _parseMovieList(URL_ALL)

def showGenreSciFi():
    _parseMovieList(URL_SCIFI)
  
def showGenreKomoedie():
    _parseMovieList(URL_COMEDY)

def showGenreAction():
    _parseMovieList(URL_ACTION)

def showGenreHorror():
    _parseMovieList(URL_HORROR)
    
def showGenreThriller():
    _parseMovieList(URL_THRILLER)

def showGenreDrama():
    _parseMovieList(URL_DRAMA)

def showGenreFantasy():
    _parseMovieList(URL_FANTASY)

def showGenreAbenteuer():
    _parseMovieList(URL_ADVENTURE)

def showGenreAnimation():
    _parseMovieList(URL_ANIMATION)

def showSearch():
    oGui = cGui()

    sSearchText = oGui.showKeyBoard()
    if (sSearchText != False and sSearchText != ''):
        _search(oGui, sSearchText)
    else:
        return
    oGui.setEndOfDirectory()
 
       
def _search(oGui, sSearchString):
    searchUrl = URL_MAIN + 'livesearch.php?q='
    
    oRequest = cRequestHandler(searchUrl + sSearchString)
    content = oRequest.request()
    searchPattern = "<table.*?<a href='([^']+)'.*?<img src='([^']+)'.*?>([^<>']+)</a>"
    oParser = cParser()
    aResult = oParser.parse(content, searchPattern)
    if not aResult[0]:
        return
    ###### parse entries
    params = ParameterHandler()
    function = 'getHosters'
    iTotal = len(aResult[1])
    for link, img, title in aResult[1]:
        sLabel = title.split('(')
        sTitle = sLabel[0].strip()
        sNextUrl = link
        params.setParam('siteUrl',sNextUrl)
        oGuiElement = cGuiElement(sTitle, SITE_IDENTIFIER, function)
        oGuiElement.setThumbnail(img)
        #oGuiElement.setMediaType('movie')
        if len(sLabel)>1:
            year = sLabel[-1].replace(')','')
            oGuiElement.setYear(year)
        if 'site=Movies' in link:
            oGuiElement.setMediaType('movie')
            oGui.addFolder(oGuiElement, params, bIsFolder = False, iTotal = iTotal)
        else:
            continue


def _parseMovieList(url): 
    oGui = cGui()  
    params = ParameterHandler()    
    oRequestHandler = cRequestHandler(url)
    sHtmlContent = oRequestHandler.request()
    # parse movie entries
    pattern = 'class="tabel-topasd".*?<a href="([^"]+)"><img src="([^"]+)" title="([^"]+)".*?<span.*?>([^<>]+)</span>.*?title="([^"]+)"/>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, pattern)
    if not aResult[0]:
        return
    total = len(aResult[1]) # Anzahl der Treffer
    for link, img, title, plot, qual in aResult[1]:
        titleParts = title.split('(') # Titel von Jahr trennen
        movieTitle = titleParts[0].strip().decode('iso-8859-1').encode('utf-8') # encoding anpassen wegen Umlauten
           
        guiElement = cGuiElement(movieTitle, SITE_IDENTIFIER, 'getHosters')
        guiElement.setThumbnail(img) #Cover als Thumbnail setzen
        guiElement.setDescription(plot.decode('iso-8859-1')) # Filmbeschreibung setzen, decode wegen Umlauten
        if len(titleParts)>1:
            tag = titleParts[-1].replace(')','')
            if tag.isdigit() and len(tag)==4:
                guiElement.setYear(tag)
        guiElement.setMediaType('movie')
        if '720p' in qual: # erst mal unwichtig
            guiElement._sQuality = 720
        elif '1080p' in qual:
            guiElement._sQuality = 1080
            
        params.setParam('siteUrl',link)
        oGui.addFolder(guiElement, params, bIsFolder = False, iTotal = total)
    oGui.setView('movies') #diese Liste unterliegt den automatisch ViewSettings für Filmlisten 
    oGui.setEndOfDirectory()

#---------------------------------------------------------------------   
  
def getHosters():
    oParams = ParameterHandler() #Parameter laden
    sUrl = oParams.getValue('siteUrl')  # Weitergegebenen Urlteil aus den Parametern holen

    oRequestHandler = cRequestHandler(URL_MAIN+sUrl) # gesamte Url zusammesetzen
    sHtmlContent = oRequestHandler.request()         # Seite abrufen
    
    sPattern = 'iframe src="(http[^"]+)"'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern, ignoreCase = True)
    hosters = []                                     # hosterliste initialisieren
    sFunction='getHosterUrl'                         # folgeFunktion festlegen
    if (aResult[0] == True):
        for aEntry in aResult[1]:
            hoster = {}
            hoster['link'] = aEntry
            # extract domain name
            hoster['name'] = aEntry.split('//')[-1].split('/')[0].split('.')[-2]
            hosters.append(hoster)
        hosters.append(sFunction)
    return hosters
  
def getHosterUrl(sStreamUrl = False):
   if not sStreamUrl:
       params = ParameterHandler()
       sStreamUrl = oParams.getValue('url')
   results = []
   result = {}
   result['streamUrl'] = sStreamUrl
   result['resolved'] = False
   results.append(result)
   return results