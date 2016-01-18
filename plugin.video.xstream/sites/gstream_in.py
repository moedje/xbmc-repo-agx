# -*- coding: utf-8 -*-
from resources.lib.util import cUtil
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.config import cConfig
from resources.lib import logger
from resources.lib.handler.ParameterHandler import ParameterHandler
import hashlib

SITE_IDENTIFIER = 'gstream_in'
SITE_NAME = 'G-Stream'
SITE_ICON = 'gstream.png'

URL_MAIN = 'http://gstream.to'
URL_LOGIN = URL_MAIN + '/login.php'
URL_SHOW_MOVIE = 'http://gstream.to/showthread.php?t='
URL_CATEGORIES = 'http://gstream.to/forumdisplay.php?f='
URL_SEARCH = 'http://gstream.to/search.php'

oConfig = cConfig()
username = oConfig.getSetting('gstream_in-username')
password = oConfig.getSetting('gstream_in-password')
sortBy = 'lastpost'
sortByCfg = str(oConfig.getSetting('sortorder'))
if sortByCfg:
    sortBy = str(sortByCfg.lower())
else:
    sortBy = 'lastpost'
searchUrl  = 's=&securitytoken=guest&do=process&searchthreadid=&query=gay&titleonly=0&searchuser=&starteronly=0&exactname=1&prefixchoice%5B%5D=Gay&childforums=1&dosearch=Search+Now&sortby={0}&pp=200&p=1'.format(sortBy)
searchUrl2 = '&prefixchoice%5B%5D=hardsextube&prefixchoice%5B%5D=redtube&prefixchoice%5B%5D=tna&prefixchoice%5B%5D=xhamster&prefixchoice%5B%5D=xvideos&replyless=0&replylimit=0&searchdate=180&beforeafter=after&order=descending&showposts=0&forumchoice%5B%5D=530&forumchoice%5B%5D=661&forumchoice%5B%5D=669&forumchoice%5B%5D=1101&forumchoice%5B%5D=829&forumchoice%5B%5D=828&forumchoice%5B%5D=739'
searchUrl3 = '&prefixchoice%5B%5D=Amateure1&prefixchoice%5B%5D=Anal&prefixchoice%5B%5D=Blowjob&prefixchoice%5B%5D=Deutsch&prefixchoice%5B%5D=Fetish&prefixchoice%5B%5D=Gruppensex&prefixchoice%5B%5D=Hardcore&prefixchoice%5B%5D=xxxhd&prefixchoice%5B%5D=International&prefixchoice%5B%5D=Masturbation&prefixchoice%5B%5D=Teens'

def load():
    oGui = cGui()

    sSecurityValue = __getSecurityCookieValue()

    __login()
    oGuiElement = cGuiElement()
    oGuiElement.setSiteName(SITE_IDENTIFIER)
    params = ParameterHandler()
    params.setParam('securityCookie', sSecurityValue)
    params.setParam('searchType', '528')
    oGui.addFolder(oGuiElement, params)
    if showAdult():
        __createMainMenuEntry(oGui, 'Gay', '661&prefixid=Gay', sSecurityValue)
        __createMainMenuEntry(oGui, 'All Porn', 661)
        oGuiElement.setFunction('displaySearch')
        oGuiElement.setTitle('Search XXX Streams')
        params.setParam('searchType', '530')
        oGui.addFolder(oGuiElement, params)
    else:
        __createMainMenuEntry(oGui, 'Aktuelle KinoFilme', 542, sSecurityValue)
        oGui.addFolder(cGuiElement('HD Filme',SITE_IDENTIFIER,'showHDMovies'))
        __createMainMenuEntry(oGui, 'Action', 591, sSecurityValue)
        __createMainMenuEntry(oGui, 'Horror', 593, sSecurityValue)
        __createMainMenuEntry(oGui, 'Komoedie', 592, sSecurityValue)
        __createMainMenuEntry(oGui, 'Thriller', 595, sSecurityValue)
        __createMainMenuEntry(oGui, 'Drama', 594, sSecurityValue)
        __createMainMenuEntry(oGui, 'Fantasy', 655, sSecurityValue)
        __createMainMenuEntry(oGui, 'Abenteuer', 596, sSecurityValue)
        __createMainMenuEntry(oGui, 'Animation', 677, sSecurityValue)
        __createMainMenuEntry(oGui, 'Dokumentation', 751, sSecurityValue)
        #__createMainMenuEntry(oGui, 'Serien', 543, sSecurityValue)

        oGuiElement = cGuiElement()
        oGuiElement.setSiteName(SITE_IDENTIFIER)
        oGuiElement.setFunction('displaySearch')
        oGuiElement.setTitle('Suche Filme')
        oGuiElement = cGuiElement()
        oGuiElement.setSiteName(SITE_IDENTIFIER)
        oGuiElement.setFunction('showXXX')
        oGuiElement.setTitle('XXX')
        oGui.addFolder(oGuiElement, params)

    oGui.setEndOfDirectory()


def __login():
    hPassword = hashlib.md5(password).hexdigest()

    oRequest = cRequestHandler(URL_LOGIN)
    oRequest.addParameters('vb_login_username', username)
    oRequest.addParameters('vb_login_password', password)
    oRequest.addParameters('s', '')
    oRequest.addParameters('do', 'login')
    oRequest.addParameters('vb_login_md5password', hPassword)
    oRequest.addParameters('vb_login_md5password_utf', hPassword)
    oRequest.ignoreDiscard(True)
    oRequest.request()

    # needed to add this, so other sites doesn't delete the cookie in global search
    # alternatively we could call login in showHoster, but this would generate more login requests...
    cookie = oRequest.getCookie("bbsessionhash")

    if cookie:
        cookie.discard = False
        oRequest.setCookie(cookie)


def __createMainMenuEntry(oGui, sMenuName, iCategoryId, sSecurityValue=''):
    oGuiElement = cGuiElement()
    oGuiElement.setSiteName(SITE_IDENTIFIER)
    oGuiElement.setTitle(sMenuName)
    oGuiElement.setFunction('parseMovieResultSite')
    params = ParameterHandler()
    params.setParam('normalySiteUrl', URL_CATEGORIES + str(iCategoryId) + '&sortorder={0}&pp=200&order=desc&page='.format(sortBy))
    params.setParam('siteUrl', URL_CATEGORIES + str(iCategoryId) + '&sortorder={0}&pp=200&order=desc&page=1'.format(sortBy))
    params.setParam('iPage', 1)
    params.setParam('securityCookie', sSecurityValue)
    oGui.addFolder(oGuiElement, params)
    
def __getSecurityCookieValue():
    oRequest = cRequestHandler(URL_MAIN, False, True)
    oRequest.ignoreDiscard(True)
    sHtmlContent = oRequest.request()
    header = oRequest.getResponseHeader()

    sPattern = '>DDoS protection by CloudFlare<'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if not aResult[0]:
        logger.info('No known protection found')
        return ''
    logger.info('CF DDos protection active')
    #Challengeform suchen
    sPattern = ('a\.value = ([0-9\*\+\-]+);.*?<form id="challenge-form" action="([^"]+)".*?'
                'name="([^"]+)" value="([^"]+)".*?name="([^"]+)"/>.*?</form>')
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if not aResult[0]:
        logger.info('ChallengeForm not found')
        return False
    aResult = aResult[1][0]
    constant = len(oRequest.getRealUrl().split('/')[2])
    exp = aResult[0]
    url = aResult[1]
    valueName1 = aResult[2]
    value1 = aResult[3]
    valueName2 = aResult[4]
    value2 = str(eval(exp)+constant)
    url = '%s%s?%s=%s&%s=%s&pp=200' % (URL_MAIN, url, valueName1, value1, valueName2, value2)
    oRequest = cRequestHandler(url, caching = False, ignoreErrors = True)
    oRequest.addHeaderEntry('Host', 'gstream.to')
    oRequest.addHeaderEntry('Referer', URL_MAIN)
    oRequest.addHeaderEntry('Connection', 'keep-alive')
    oRequest.addHeaderEntry('DNT', '1')
    oRequest.ignoreDiscard(True)
    sHtmlContent = oRequest.request()
    return True 

def __getHtmlContent(sUrl = None, sSecurityValue=None):
    params = ParameterHandler()

    # Test if a url is available and set it
    if sUrl is None and not params.exist('siteUrl'):
        logger.info("There is no url we can request.")
        return False
    else:
        if sUrl is None:
            sUrl = params.getValue('siteUrl')

    # Test if a security value is available
    if sSecurityValue is None:
        if params.exist('securityCookie'):
            sSecurityValue = params.getValue('securityCookie')
        else :
            sSecurityValue = ''

    # Make the request
    oRequest = cRequestHandler(sUrl, caching=True)    
    oRequest.ignoreDiscard(True)
    return oRequest.request()
    
def showXXX():
    params = ParameterHandler()
    oGui = cGui()
    __createMainMenuEntry(oGui, 'All Porn', 661)
    oGuiElement = cGuiElement()
    oGuiElement.setSiteName(SITE_IDENTIFIER)
    oGuiElement.setFunction('displaySearch')
    oGuiElement.setTitle('Search XXX Streams')
    params.setParam('searchType', '530')
    oGui.addFolder(oGuiElement, params)
    
    __createMainMenuEntry(oGui, 'Gay', '661&prefixid=Gay')
    __createMainMenuEntry(oGui, 'Amateure', '661&prefixid=Amateure1')
    __createMainMenuEntry(oGui, 'Anal', '661&prefixid=Anal')
    __createMainMenuEntry(oGui, 'Asia', '661&prefixid=Asia')
    __createMainMenuEntry(oGui, 'Black', '661&prefixid=Ebony')
    __createMainMenuEntry(oGui, 'Blowjob', '661&prefixid=Blowjob')
    __createMainMenuEntry(oGui, 'Deutsch', '661&prefixid=Deutsch')
    __createMainMenuEntry(oGui, 'Fetish', '661&prefixid=Fetish')
    __createMainMenuEntry(oGui, 'Gruppensex', '661&prefixid=Gruppensex')
    __createMainMenuEntry(oGui, 'Hardcore', '661&prefixid=Hardcore')
    __createMainMenuEntry(oGui, 'International', '661&prefixid=International')
    __createMainMenuEntry(oGui, 'Lesben', '661&prefixid=Lesben')
    __createMainMenuEntry(oGui, 'Masturbation', '661&prefixid=Masturbation')
    __createMainMenuEntry(oGui, 'Teens', '661&prefixid=Teens')
    oGui.setEndOfDirectory()
    
def showHDMovies():
    oGui = cGui()
    sUrl = 'http://gstream.to/search.php?do=process&prefixchoice[]=hd&pp=200&{0}&p='.format(searchUrl+searchUrl2+searchUrl3)
    oRequest = cRequestHandler(sUrl, caching = True)
    oRequest.ignoreDiscard(True)
    oRequest.request()
    sUrl = oRequest.getRealUrl()
    __parseMovieResultSite(oGui, sUrl)
    oGui.setEndOfDirectory()    

def displaySearch():
    oGui = cGui()       
    sSearchText = oGui.showKeyBoard()    
    if (sSearchText != False):
        _search(oGui, str(sSearchText))
    else:
        return gotoPage()
        #return
    oGui.setEndOfDirectory()

def _search(oGui, sSearchText):
    __login()
    params = ParameterHandler()
    sSearchType = params.getValue('searchType')
    if not sSearchType:
        sSearchType = '528'
    sUrl = URL_SEARCH+'?do=process&childforums=1&do=process&exactname=1&{0}&pp=200&p='.format(searchUrl)
    sUrl = sUrl.replace("query=gay+","query=gay+{0}".format(str(sSearchText).replace(' ', '+')))
    #sUrl = URL_SEARCH+'?do=process&childforums=1&do=process&exactname=1&forumchoice[]={0}&query=gay+{1}&quicksearch=1&s=&securitytoken=guest&titleonly=1&pp=200'.format(sSearchType, str(sSearchText).reprlace(' ', '+') )
    oRequest = cRequestHandler(sUrl, caching = True)
    oRequest.ignoreDiscard(True)
    oRequest.request()
    sUrl = oRequest.getRealUrl()
    __parseMovieResultSite(oGui, sUrl)

def parseMovieResultSite():
    oGui = cGui()
    params = ParameterHandler()
    if (params.exist('siteUrl')):
        siteUrl = params.getValue('siteUrl')
        normalySiteUrl = params.getValue('normalySiteUrl')
        iPage = params.getValue('iPage')
        __parseMovieResultSite(oGui, siteUrl, normalySiteUrl, iPage)
    oGui.setEndOfDirectory()


def __parseMovieResultSite(oGui, siteUrl, normalySiteUrl = '', iPage = 1):
    if not normalySiteUrl:
        normalySiteUrl = siteUrl+'sortorder={0}&pp=200&p='.format(sortBy)
    params = ParameterHandler()  
    sPattern = 'class="p1".*?<img class="large" src="(http://[^"]+)".*?<a href="[^"]+" id=".*?([^"_]+)"(.*?)>([^<]+)</a>(.*?)</tr>'
    sHtmlContent = __getHtmlContent(sUrl = siteUrl)
    # parse content
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if (aResult[0] == False):
        return
    total = len(aResult[1])  
    badwords = ['girl', 'giselle', 'she', 'tran', 'lady', 'sister', 'woman', 'bisex', 'madame', 'bi ', ' bi', 'schwan', 'false advertis', 'super ramon', ' ts', 'ts ', 'milf', 'mom', 'pussy', 'tit', 'boob', 'lesb', 'babe', 'doll', 'chick', 'rogue adventures', 'kuss den', 'overpowered by', 'surprise i have a dick']
    isok = True
    for img, link, hdS, title, yearS  in aResult[1]:
        isok = True
        for w in badwords:
            if title.lower().find(w) != -1:
                isok = False
                break
        if isok:
            sMovieTitle = title.replace('&amp;','&')
            sTitle = sMovieTitle
            sUrl = URL_SHOW_MOVIE + str(link)
            year = ''
            aResult = oParser.parse(yearS, ' ([0-9]{4}) -')
            if aResult[0]:
                year = aResult[1][0]
            aResult = oParser.parse(hdS, '(title="HD Quali")')
            if aResult[0]:
                sTitle = sTitle + ' [HD]'
            oGuiElement = cGuiElement(sTitle,SITE_IDENTIFIER,'getHosters')
            oGuiElement.setMediaType('movie')
            oGuiElement.setYear(year)
            oGuiElement.setThumbnail(img)      
            params.setParam('movieUrl', sUrl)
            params.setParam('sMovieTitle', sMovieTitle)       
            oGui.addFolder(oGuiElement, params, bIsFolder = False, iTotal = total)
        else:
            isok = True
    npage = int(iPage)+1
    # check for next site
    iTotalPages = __getTotalPages(iPage, sHtmlContent)
    if iTotalPages >= npage:
        params = ParameterHandler()
        params.setParam('iPage', npage)
        params.setParam('normalySiteUrl', normalySiteUrl)
        params.setParam('siteUrl', normalySiteUrl + str(npage))
        oGui.addNextPage(SITE_IDENTIFIER,'parseMovieResultSite', params, iTotalPages)
    if  iTotalPages > 1:
        oGuiElement = cGuiElement('#{0} Page [{0} of {1}]'.format(str(iPage), str(iTotalPages)),SITE_IDENTIFIER,'gotoPage')
        params = ParameterHandler()
        oGui.addFolder(oGuiElement, params)
                
    oGui.setView('movies')            

def gotoPage():
    oGui = cGui()
    pageNum = oGui.showNumpad()
    if not pageNum:
        pageNum = iPage + 1
    params = ParameterHandler()
    siteUrl = params.getValue('normalySiteUrl')+pageNum
    __parseMovieResultSite(oGui, siteUrl, iPage = int(pageNum))
    oGui.setEndOfDirectory()
    
def __getTotalPages(iPage, sHtml):
    sPattern = '>Seite [0-9]+ von ([0-9]+)<'
    oParser = cParser()
    aResult = oParser.parse(sHtml, sPattern)
    if (aResult[0] == True):
        iTotalCount = int(aResult[1][0])
        if iTotalCount is not None:
            return iTotalCount
        else:
            return 100
    return 100

def __createDisplayStart(iPage=1):
    npagenum = int((200 * int(iPage)) - 200)
    if npagenum is not None:
        return npagenum
    else:
        return 1

def __createInfo(oGui, sHtmlContent):
    sPattern = '<td class="alt1" id="td_post_.*?<img src="([^"]+)".*?<b>Inhalt:</b>(.*?)<br />'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    
    if (aResult[0] == True):
        for aEntry in aResult[1]:
            sThumbnail = str(aEntry[0])
            sDescription = cUtil().removeHtmlTags(str(aEntry[1])).replace('\t', '').strip()
            oGuiElement = cGuiElement()
            oGuiElement.setSiteName(SITE_IDENTIFIER)
            oGuiElement.setTitle('info (press Info Button)')
            oGuiElement.setThumbnail(sThumbnail)
            oGuiElement.setFunction('dummyFolder')
            oGuiElement.setDescription(sDescription)
            oGui.addFolder(oGuiElement)
            
def showAdult():
    oConfig = cConfig()
    if oConfig.getSetting('showAdult')=='true':    
        return True
    return False

def dummyFolder():
    oGui = cGui()
    oGui.setEndOfDirectory()
#### Hosterhandling
def getHosters():
    hosters = []
    params = ParameterHandler()
    if (params.exist('movieUrl') and params.exist('sMovieTitle')):
        sSiteUrl = params.getValue('movieUrl')
        sMovieTitle = params.getValue('sMovieTitle')
        sHtmlContent = __getHtmlContent(sUrl = sSiteUrl)
        sPattern = 'id="ame_noshow_post.*?<a href="([^"]+)" title="[^"]+" target="_blank">([^<]+)</a>'
        aResult = cParser().parse(sHtmlContent, sPattern)
        if aResult[0] == True:
            for aEntry in aResult[1]:
                sUrl = aEntry[0]
                # extract hoster domainname            
                if 'gstream.to/secure/' in sUrl :
                    sHoster = sUrl.split('secure/')[-1].split('/')[0].split('.')[-2]
                else:
                    sHoster = sUrl.split('//')[-1].split('/')[0].split('.')[-2]
                hoster = {}
                hoster['link'] = sUrl
                hoster['name'] = sHoster
                hosters.append(hoster)
            hosters.append('getHosterUrl')
    return hosters

def getHosterUrl(sUrl = False):
    params = ParameterHandler() 
    if not sUrl:
        sUrl =  params.getValue('url')
    results = []
    if 'gstream.to/secure/' in sUrl :
        sHoster = sUrl.split('secure/')[-1].split('/')[0]       
        oRequest = cRequestHandler(sUrl, False)
        oRequest.addHeaderEntry('Cookie', params.getValue('securityCookie'))
        oRequest.addHeaderEntry('Referer', params.getValue('movieUrl'))
        oRequest.ignoreDiscard(True)
        try:
            oRequest.request()
            sUrl = oRequest.getRealUrl()
            sUrl = 'http://%s%s' % (sHoster, sUrl.split(sHoster)[-1])
        except:
            pass
    result = {}
    result['streamUrl'] = sUrl
    result['resolved'] = False
    results.append(result)
    return results
