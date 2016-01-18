# -*- coding: utf-8 -*-
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.config import cConfig
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.player import cPlayer
import xbmc, xbmcgui
import logger
#test
import xbmcplugin
#import sys

class cHosterGui:

    
    SITE_NAME = 'cHosterGui'
    
    
    def __init__(self):
        # if cConfig().getSetting('autoplay')=='true':
            # self.autoPlay = True
        # else:
            # self.autoPlay = False
        self.userAgent = "|User-Agent=Mozilla/5.0 (Windows; U; Windows NT 5.1; de-DE; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3"
        self.maxHoster = int(cConfig().getSetting('maxHoster'))
        self.dialog = False


    def play(self, siteResult=False):
        import urlresolver
        oGui = cGui()
        params = ParameterHandler()
        sMediaUrl = params.getValue('sMediaUrl')
        sFileName = params.getValue('MovieTitle')
        if not sFileName:
            sFileName = params.getValue('Title')
        if not sFileName: #nur vorrübergehend
            sFileName = params.getValue('sMovieTitle')
        if not sFileName:
            sFileName = params.getValue('title')

        sSeason = params.getValue('season')
        sEpisode = params.getValue('episode')
        sShowTitle = params.getValue('TVShowTitle')
        sThumbnail = params.getValue('thumb')
              
        if siteResult:
            sMediaUrl = siteResult['streamUrl']
            logger.info('call play: ' + sMediaUrl)
            if siteResult['resolved']:
                sLink = sMediaUrl
            else:
                sLink = urlresolver.resolve(sMediaUrl)

        elif sMediaUrl:
            logger.info('call play: ' + sMediaUrl)
            sLink = urlresolver.resolve(sMediaUrl)
        else:
            oGui.showError('xStream', 'kein Hosterlink übergeben', 5)
            return False
        if hasattr(sLink, 'msg'):
            msg = sLink.msg
        else:
            msg = False
        if sLink != False and not msg:
            logger.info('file link: ' + str(sLink))
            listItem = xbmcgui.ListItem(path=sLink + self.userAgent)
            info = {}
            info['Title'] = sFileName
            if sThumbnail:
                listItem.setThumbnailImage(sThumbnail)
            if sShowTitle:
                info['Episode'] = sEpisode
                info['Season'] = sSeason
                info['TvShowTitle'] = sShowTitle
            oPlayer = cPlayer()
            if self.dialog:
               try:
                   self.dialog.close()
               except:
                   pass       
            listItem.setInfo(type="Video", infoLabels=info)
            listItem.setProperty('IsPlayable', 'true')

            pluginHandle = oGui.pluginHandle
            xbmcplugin.setResolvedUrl(pluginHandle, True, listItem)
            oPlayer.startPlayer() # autostream loop is still active while playing
            return True #Necessary for autoStream
        else:
            if not msg:
               msg = 'Stream nicht mehr verfügbar oder Link fehlerhaft'
            oGui.showError('xStream',str(msg),7)
            if hasattr(sLink, 'code'):
                logger.info(str(msg) +' UnresolveableCode: '+ str(sLink.code))
            else:
                logger.info(str(msg) +' UnresolveableCode: - ')
            '''
                UnresolveableCode
                0: Unknown Error
                1: The url was resolved, but the file has been permanantly
                    removed
                2: The file is temporarily unavailable for example due to
                    planned site maintenance
                3. There was an error contacting the site for example a
                    connection attempt timed out
            '''
            return False

        
    def addToPlaylist(self, siteResult = False):
        import urlresolver
        oGui = cGui()
        params = ParameterHandler()

        sMediaUrl = params.getValue('sMediaUrl')
        sFileName = params.getValue('MovieTitle')
        if not sFileName:
            sFileName = params.getValue('title')
        if not sFileName:
            sFileName = params.getValue('Title')
        if not sFileName: #nur vorrübergehend
            sFileName = params.getValue('sMovieTitle')
        if not sFileName:
            sFileName = params.getValue('title')
        sSeason = params.getValue('season')
        sEpisode = params.getValue('episode')
        sShowTitle = params.getValue('TvShowTitle')
        sThumbnail = params.getValue('thumb')
        if siteResult:
            sMediaUrl = siteResult['streamUrl']
            if siteResult['resolved']:
                sLink = sMediaUrl
            else:
                sLink = urlresolver.resolve(sMediaUrl)
        else:
            sLink = urlresolver.resolve(sMediaUrl)
        logger.info('call addToPlaylist: ' + sMediaUrl)
        logger.info('file link: ' + str(sLink))
        if (sLink != False):
            oGuiElement = cGuiElement()
            oGuiElement.setSiteName(self.SITE_NAME)
            oGuiElement.setMediaUrl(sLink)
            oGuiElement.setTitle(sFileName)
            if sThumbnail:
                oGuiElement.setThumbnail(sThumbnail)
            if sShowTitle:
                oGuiElement.addItemProperties('Episode',sEpisode)
                oGuiElement.addItemProperties('Season',sSeason)
                oGuiElement.addItemProperties('TvShowTitle',sShowTitle)
            if self.dialog:
                self.dialog.close()
            oPlayer = cPlayer()
            oPlayer.addItemToPlaylist(oGuiElement)
            oGui.showInfo('Playlist', 'Stream wurde hinzugefügt', 5);
        else:
            #oGui.showError('Playlist', 'File deleted or Link could not be resolved', 5);
            return False
        return True
        
        
    def download(self, siteResult = False):
        from resources.lib.download import cDownload
        import urlresolver
        #oGui = cGui()
        params = ParameterHandler()

        sMediaUrl = params.getValue('sMediaUrl')
        sFileName = params.getValue('sFileName')
        sFileName = params.getValue('sMovieTitle')
        if siteResult:
            sMediaUrl = siteResult['streamUrl']
            if siteResult['resolved']:
                sLink = sMediaUrl
            else:
                sLink = urlresolver.resolve(sMediaUrl)
        else:
            sLink = urlresolver.resolve(sMediaUrl)
        logger.info('call download: ' + sMediaUrl)
        logger.info('file link: ' + str(sLink))
        if self.dialog:
            self.dialog.close()
        if (sLink != False):
            oDownload = cDownload()
            oDownload.download(sLink, 'Stream')
        else:
            #cGui().showError('Download', 'File deleted or Link could not be resolved', 5);
            return False
        return True
        
    def sendToPyLoad(self, siteResult = False):
        from resources.lib.handler.pyLoadHandler import cPyLoadHandler
        import urlresolver
        params = ParameterHandler()

        sMediaUrl = params.getValue('sMediaUrl')
        sFileName = params.getValue('MovieTitle')
        if not sFileName:
            sFileName = params.getValue('Title')
        if not sFileName: #nur vorrübergehend
            sFileName = params.getValue('sMovieTitle')
        if not sFileName:
            sFileName = params.getValue('title')

        if siteResult:
            sMediaUrl = siteResult['streamUrl']
            if siteResult['resolved']:
                sLink = sMediaUrl
            else:
                sLink = urlresolver.resolve(sMediaUrl)
        else:
            sLink = urlresolver.resolve(sMediaUrl)   
        try:
            msg = sLink.msg
        except:
            msg = False
        if sLink != False and not msg:
            logger.info('download with pyLoad: ' + sMediaUrl)
            cPyLoadHandler().sendToPyLoad(sFileName,sLink)
            return True
        else:
            cGui().showError('xStream', str(msg), 5)
            return False
        
    def sendToJDownloader(self, sMediaUrl = False):
        from resources.lib.handler.jdownloaderHandler import cJDownloaderHandler
        params = ParameterHandler()
        sHosterIdentifier = params.getValue('sHosterIdentifier')
        if not sMediaUrl:            
            sMediaUrl = params.getValue('sMediaUrl')            
        sFileName = params.getValue('sFileName')
        if self.dialog:
            self.dialog.close()
        logger.info('call send to JDownloader: ' + sMediaUrl)       
        cJDownloaderHandler().sendToJDownloader(sMediaUrl)
        

    def __getPriorities(self, hosterList, filter = True):
        '''
        Sort hosters based on their resolvers priority.
        '''
        import urlresolver
        #          
        ranking = []
        '''
        # multi hosters won't be handled correctly
        urlresolver.lazy_plugin_scan() 
        hosters = {}
        for imp in urlresolver.UrlResolver.implementors():
            prio = imp.priority
            for name in imp.domains:
                hosters[name.split(',')[0]] = prio
        for hoster in hosterList:
            name = hoster['name'].lower()
            if name in hosters:
                ranking.append([hosters[name],hoster])
            elif not filter:
                ranking.append([999,hoster])
        '''

        #handles multihosters but is about 10 times slower
        for hoster in hosterList:
            source = urlresolver.HostedMediaFile(host=hoster['name'].lower(), media_id='dummy')
            if source:
                priority = False
                for resolver in source._HostedMediaFile__resolvers:
                    if resolver.domains[0] != '*':
                        priority = resolver.priority
                        break
                    if not priority:
                        priority = resolver.priority                        
                if priority:
                    ranking.append([priority,hoster])
            elif not filter:
                ranking.append([999,hoster])

        ranking.sort()
        hosterQueue = []
        for i,hoster in ranking:
            hosterQueue.append(hoster)
        return hosterQueue

        
    def stream(self, playMode, siteName, function, url):
        self.dialog = xbmcgui.DialogProgress()
        self.dialog.create('xStream',"get stream/hoster")
        #load site as plugin and run the function
        self.dialog.update(5,'import plugin...')
        plugin = __import__(siteName, globals(), locals())
        function = getattr(plugin, function)
        self.dialog.update(10,'catch links...')
        if url:
            siteResult = function(url)
        else:
            siteResult = function()
        self.dialog.update(40)
        if not siteResult:
            self.dialog.close()
            cGui().showInfo('xStream','stream/hoster not available')
            return
        # if result is not a list, make in one
        if not type(siteResult) is list:
            temp = []
            temp.append(siteResult)
            siteResult = temp
        
        # field "name" marks hosters
        if 'name' in siteResult[0]:
            functionName = siteResult[-1]
            del siteResult[-1]
            if not siteResult:
                self.dialog.close()
                cGui().showInfo('xStream','no hoster available')
                return

            self.dialog.update(60,'prepare hosterlist..')
            if (playMode !='jd') and (playMode != 'pyload') and \
                            cConfig().getSetting('presortHoster')=='true':
                # filter and sort hosters
                siteResult = self.__getPriorities(siteResult)
            if not siteResult:
                self.dialog.close()
                cGui().showInfo('xStream','no supported hoster available')
                return False
            self.dialog.update(90)
            #self.dialog.close()
            if len(siteResult) > self.maxHoster:
                siteResult = siteResult[:self.maxHoster-1]
            if len(siteResult)>1:
                #choose hoster
                if cConfig().getSetting('hosterListFolder')=='true':
                    self.showHosterFolder(siteResult, siteName, functionName)
                    return
                siteResult = self._chooseHoster(siteResult)
                if not siteResult:
                    return
            else:                
                siteResult = siteResult[0]
            # get stream links
            logger.info(siteResult['link'])
            function = getattr(plugin, functionName)
            siteResult = function(siteResult['link'])
	          
            # if result is not a list, make in one
            if not type(siteResult) is list:
                temp = []
                temp.append(siteResult)
                siteResult = temp

        # choose part
        if len(siteResult)>1:
            siteResult = self._choosePart(siteResult)
            if not siteResult:
                self.dialog.close()
                return
        else:
            siteResult = siteResult[0]

        self.dialog = xbmcgui.DialogProgress()
        self.dialog.create('xStream',' ')
        self.dialog.update(95,'start opening stream..')

        if playMode == 'play':
            self.play(siteResult)
        elif playMode == 'download':
            self.download(siteResult)
        elif playMode == 'enqueue':
            self.addToPlaylist(siteResult)
        elif playMode == 'jd':
            self.sendToJDownloader(siteResult['streamUrl'])
        elif playMode == 'pyload':
            self.sendToPyLoad(siteResult)
    
    def _chooseHoster(self, siteResult):
        dialog = xbmcgui.Dialog()
        titles = []
        for result in siteResult:
            if 'displayedName' in result:
                titles.append(result['displayedName'])
            else:                
                titles.append(result['name'])
        index = dialog.select('Hoster wählen', titles)
        if index > -1:
            siteResult = siteResult[index]
            return siteResult
        else:
            return False

            
    def showHosterFolder(self, siteResult, siteName, functionName):
        oGui = cGui()
        total = len(siteResult)
        params = ParameterHandler()
        for hoster in siteResult:
            if 'displayedName' in hoster:
                name = hoster['displayedName']
            else:
                name = hoster['name']
            oGuiElement = cGuiElement(name, siteName, functionName)
            params.setParam('url',hoster['link'])
            params.setParam('isHoster','true')
            oGui.addFolder(oGuiElement, params, iTotal = total, isHoster = True)
        oGui.setEndOfDirectory()

    def _choosePart(self, siteResult):
        self.dialog = xbmcgui.Dialog()
        titles = []
        for result in siteResult:                
            titles.append(result['title'])
        index = self.dialog.select('Part wählen', titles)
        if index > -1:
            siteResult = siteResult[index]
            return siteResult
        else:
            return False

        
    def streamAuto(self, playMode, siteName, function):
        self.dialog = xbmcgui.DialogProgress()
        self.dialog.create('xStream',"get stream/hoster")
        #load site as plugin and run the function
        self.dialog.update(5,'import plugin...')
        plugin = __import__(siteName, globals(), locals())
        function = getattr(plugin, function)
        self.dialog.update(10,'catch links...')
        siteResult = function()
        if not siteResult:
            self.dialog.close()
            cGui().showInfo('xStream','stream/hoster not available')
            return False
        # if result is not a list, make in one
        if not type(siteResult) is list:
            temp = []
            temp.append(siteResult)
            siteResult = temp
        # field "name" marks hosters
        if 'name' in siteResult[0]:
            self.dialog.update(90,'prepare hosterlist..') 
            functionName = siteResult[-1]
            del siteResult[-1]             
            hosters = self.__getPriorities(siteResult)
            if not hosters:
                self.dialog.close()
                cGui().showInfo('xStream','no supported hoster available')
                return False
            if len(siteResult) > self.maxHoster:
                siteResult = siteResult[:self.maxHoster-1]
            check = False
            self.dialog.create('xStream','try hosters...')
            total = len(hosters)
            count = 0
            for hoster in hosters:               
                if self.dialog.iscanceled() or xbmc.abortRequested or check: return
                count = count + 1
                percent = count*100/total
                try:
                    logger.info('try hoster %s' % hoster['name'])
                    self.dialog.update(percent,'try hoster %s' % hoster['name'])
                    # get stream links
                    function = getattr(plugin, functionName)
                    siteResult = function(hoster['link'])
                    check = self.__autoEnqueue(siteResult, playMode)
                    if check:                      
                        return True
                except:
                    self.dialog.update(percent,'hoster %s failed' % hoster['name'])
                    logger.info('playback with hoster %s failed' % hoster['name'])
        # field "resolved" marks streamlinks
        elif 'resolved' in siteResult[0]:
            for stream in siteResult:
                try:
                    if self.__autoEnqueue(siteResult, playMode):
                        self.dialog.close()
                        return True
                except:
                    pass


    def __autoEnqueue(self, partList, playMode):
        # choose part
        if not partList:
            return False
        for i in range(len(partList)-1,-1,-1):
            try:
                if playMode == 'play' and i==0:
                    if not self.play(partList[i]):
                        return False
                elif playMode == 'download':
                    self.download(partList[i])
                elif playMode == 'enqueue' or (playMode=='play' and i>0):
                    self.addToPlaylist(partList[i])
            except:
                return False
                raise
        logger.info('autoEnqueue successful')
        return True


class Hoster:

    def __init__(self, name, link):
        self.name = name
        self.link = link
            
