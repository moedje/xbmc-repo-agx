#!/usr/bin/env python2.7
import os
import sys
import urllib
import httplib
import mechanize
import xbmc
import xbmcgui

import hashlib
import time
from resources.lib.config import cConfig
from resources.lib import common
from resources.lib import logger

class cRequestHandler:
    REQUEST_TYPE_GET = 0
    REQUEST_TYPE_POST = 1
      
    def __init__(self, sUrl, caching = True, ignoreErrors = False):
        self.__sUrl = sUrl
        self.__sRealUrl = ''
        self.__cType = 0
        self.__aParameters = {}
        self.__aHeaderEntries = []
        self.__cachePath = ''
        self._cookiePath = ''
        self.ignoreDiscard(False)
        self.ignoreExpired(False)
        self.caching = caching
        self.ignoreErrors = ignoreErrors
        self.cacheTime = int(cConfig().getSetting('cacheTime'))
        self.removeBreakLines(True)
        self.removeNewLines(True)
        self.__setDefaultHeader()
        self.setCachePath()
        self.__setCookiePath()
        self.__sResponseHeader = ''


    def removeNewLines(self, bRemoveNewLines):
        self.__bRemoveNewLines = bRemoveNewLines

    def removeBreakLines(self, bRemoveBreakLines):
        self.__bRemoveBreakLines = bRemoveBreakLines

    def setRequestType(self, cType):
        self.__cType = cType

    def addHeaderEntry(self, sHeaderKey, sHeaderValue):
        aHeader = {sHeaderKey : sHeaderValue}
        self.__aHeaderEntries.append(aHeader)

    def addParameters(self, sParameterKey, sParameterValue, quote = False):
        if not quote:
            self.__aParameters[sParameterKey] = sParameterValue
        else:
            self.__aParameters[sParameterKey] = urllib.quote(str(sParameterValue))

    def getResponseHeader(self):
        return self.__sResponseHeader

    # url after redirects
    def getRealUrl(self):
        return self.__sRealUrl;

    def request(self):
        self.__sUrl = self.__sUrl.replace(' ', '+')
        return self.__callRequest()

    def getRequestUri(self):
        return self.__sUrl + '?' + urllib.urlencode(self.__aParameters)

    def __setDefaultHeader(self):
        self.addHeaderEntry('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de-DE; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        self.addHeaderEntry('Accept-Language', 'de-de,de;q=0.8,en-us;q=0.5,en;q=0.3')
        self.addHeaderEntry('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')

    def __callRequest(self):
        cookieJar = mechanize.LWPCookieJar()
        try: #TODO ohne try evtl.
            cookieJar.load(self._cookiePath, self.__bIgnoreDiscard, self.__bIgnoreExpired)
        except Exception as e:
            logger.info(e)
        sParameters = urllib.urlencode(self.__aParameters)

        opener = mechanize.build_opener(SmartRedirectHandler,
                                        mechanize.HTTPEquivProcessor,
                                        mechanize.HTTPRefreshProcessor)
        if (len(sParameters) > 0):
            oRequest = mechanize.Request(self.__sUrl, sParameters)
        else:
            oRequest = mechanize.Request(self.__sUrl)

        for aHeader in self.__aHeaderEntries:                
                for sHeaderKey, sHeaderValue in aHeader.items():
                    oRequest.add_header(sHeaderKey, sHeaderValue)
        cookieJar.add_cookie_header(oRequest)
        
        if self.caching and self.cacheTime > 0:
            sContent = self.readCache(self.getRequestUri())
            if sContent:
                return sContent
        try:
            oResponse = opener.open(oRequest,timeout = 60)             
        except mechanize.HTTPError, e:
            if not self.ignoreErrors:
                xbmcgui.Dialog().ok('xStream','Fehler beim Abrufen der Url:',self.__sUrl, str(e))
                logger.error("HTTPError "+str(e)+" Url: "+self.__sUrl)
                return ''
            else:
                oResponse = e                 
        except mechanize.URLError, e:
            xbmcgui.Dialog().ok('xStream',str(e.reason), 'Fehler')
            logger.error("URLError "+str(e.reason)+" Url: "+self.__sUrl)
            return ''
        except httplib.HTTPException, e:
            xbmcgui.Dialog().ok('xStream', str(e))
            logger.error("HTTPException "+str(e)+" Url: "+self.__sUrl)
            return ''

        cookieJar.extract_cookies(oResponse, oRequest)

        cookieJar = self.__checkCookie(cookieJar)

        cookieJar.save(self._cookiePath, self.__bIgnoreDiscard, self.__bIgnoreExpired)
        sContent = oResponse.read()
        self.__sResponseHeader = oResponse.info()
        # handle gzipped content
        if self.__sResponseHeader.get('Content-Encoding') == 'gzip':
            import gzip
            import StringIO
            data = StringIO.StringIO(sContent)
            gzipper = gzip.GzipFile(fileobj=data, mode='rb')
            try:      
                sContent = gzipper.read()
            except:
                sContent = gzipper.extrabuf
        
        if (self.__bRemoveNewLines == True):
            sContent = sContent.replace("\n","")
            sContent = sContent.replace("\r\t","")

        if (self.__bRemoveBreakLines == True):
            sContent = sContent.replace("&nbsp;","")

        self.__sRealUrl = oResponse.geturl()
        
        oResponse.close()
        if self.caching and self.cacheTime > 0:
            self.writeCache(self.getRequestUri(), sContent)

        return sContent

    def __checkCookie(self, cookieJar):
        for entry in cookieJar:
            if entry.expires > sys.maxint:
                entry.expires = sys.maxint

        return cookieJar

    def getHeaderLocationUrl(self):        
        opened = mechanize.urlopen(self.__sUrl)
        return opened.geturl()

    def __setCookiePath(self):
        profilePath = common.profilePath
        cookieFile = os.path.join(xbmc.translatePath(profilePath),'cookies.txt')
        if not os.path.exists(cookieFile):
            file = open(cookieFile, 'w')
            file.close()
        self._cookiePath = cookieFile

    def getCookie(self, sCookieName):
        cookieJar = mechanize.LWPCookieJar()
        try: #TODO ohne try evtl.
            cookieJar.load(self._cookiePath, self.__bIgnoreDiscard, self.__bIgnoreExpired)
        except Exception as e:
            logger.info(e)

        for entry in cookieJar:
            if entry.name == sCookieName:
                return entry

        return False

    def setCookie(self, oCookie):
        cookieJar = mechanize.LWPCookieJar()
        try: #TODO ohne try evtl.
            cookieJar.load(self._cookiePath, self.__bIgnoreDiscard, self.__bIgnoreExpired)
        except Exception as e:
            logger.info(e)

        cookieJar.set_cookie(oCookie)

        cookieJar.save(self._cookiePath, self.__bIgnoreDiscard, self.__bIgnoreExpired)

    def ignoreDiscard(self, bIgnoreDiscard):
        self.__bIgnoreDiscard = bIgnoreDiscard

    def ignoreExpired(self, bIgnoreExpired):
        self.__bIgnoreExpired = bIgnoreExpired

    ###Caching
    def setCachePath(self, cache=''):
        if not cache:
            profilePath = common.profilePath
            cache = os.path.join(xbmc.translatePath(profilePath),'htmlcache')
        if not os.path.exists(cache):
            os.makedirs(cache)
        self.__cachePath = cache

    def readCache(self, url):
        h = hashlib.md5(url).hexdigest()
        cacheFile = os.path.join(self.__cachePath, h)
        fileAge = self.getFileAge(cacheFile)
        if fileAge > 0 and fileAge < self.cacheTime:
            try:
                fhdl = file(cacheFile,'r')
                content = fhdl.read()
            except:
               logger.info('Could not read Cache')
            if content:
                logger.info('read html for %s from cache' % url)
                return content
        return ''

    def writeCache(self, url, content):
        h = hashlib.md5(url).hexdigest()
        cacheFile = os.path.join(self.__cachePath, h)
        try:
            fhdl = file(cacheFile,'w')
            fhdl.write(content)
        except:                
            logger.info('Could not write Cache')

    def getFileAge(self, cacheFile):
        try:
            fileAge = time.time() - os.stat(cacheFile).st_mtime
        except:
            return 0
        return fileAge

    def clearCache(self):
        files = os.listdir(self.__cachePath)
        for file in files:
            cacheFile = os.path.join(self.__cachePath, file)
            fileAge = self.getFileAge(cacheFile)
            if fileAge > self.cacheTime:
                os.remove(cacheFile)

# get more control over redirect (extract further cookies) 
class SmartRedirectHandler(mechanize.HTTPRedirectHandler):     
    def http_error_301(self, req, fp, code, msg, headers):
        result = mechanize.HTTPRedirectHandler.http_error_301( 
            self, req, fp, code, msg, headers)             
        result.status = code
        return result                                       

    def http_error_302(self, req, fp, code, msg, headers):   
        result = mechanize.HTTPRedirectHandler.http_error_302(
            self, req, fp, code, msg, headers)              
        result.status = code
        self.export_cookies(req, fp, code, msg, headers)
        return result
    
    def export_cookies(self, req, fp, code, msg, headers):
        oRequest = cRequestHandler('dummy')
        resp = mechanize._response.closeable_response(fp, headers, req.get_full_url(), code, msg)
        cookieJar = mechanize.LWPCookieJar()
        try:
            cookieJar.load(oRequest._cookiePath)
        except Exception as e:
            logger.info(e)            
        cookieJar.extract_cookies(resp,req)  
        cookieJar.save(oRequest._cookiePath)