from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.config import cConfig
import logger
from resources.lib.gui.gui import cGui
import xbmc
import time

class XstreamPlayer(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self, *args, **kwargs)        
        self.streamFinished = False
        self.playedTime = 0
        self.totalTime = 999999
        logger.info('player instance created')
    
    def onPlayBackStarted(self):
        logger.info('starting playeback')
        self.totalTime = self.getTotalTime()
    def onPlayBackStopped(self):
        logger.info('Playback stopped')
        self.streamFinished = True
        if cConfig().getSetting('metahandler')=='true':
            META = True
            try:
                from metahandler import metahandlers
            except Exception as e:
                META = False
                logger.info("Could not import package 'metahandler'")
                logger.info(e)
        else:
            META = False
        if META:
            try:                       
                percent = self.playedTime/self.totalTime
                logger.info('Watched percent '+str(int(percent*100)))                   
                if percent >= 0.80:
                    logger.info('Attemt to change watched status')
                    meta = metahandlers.MetaData()
                    params = ParameterHandler()
                    season = ''
                    episode = ''
                    mediaType = params.getValue('mediaType')
                    imdbID = params.getValue('imdbID')
                    name = params.getValue('Title')
                    TVShowTitle = params.getValue('TVShowTitle')
                    if params.exist('season'):
                        season = params.getValue('season')
                        if int(season) > 0:mediaType = 'season'
                    if params.exist('episode'):
                        episode = params.getValue('episode')
                        if int(episode) > 0: mediaType = 'episode'
                    if imdbID and mediaType:
                        if mediaType == 'movie' or mediaType == 'tvshow':
                            metaInfo = meta.get_meta(self._mediaType, self.__sTitle, imdbID)
                        elif mediaType == 'season':
                            metaInfo = meta.get_seasons(TVShowTitle, imdbID, str(season))
                        elif mediaType == 'episode' and TVShowTitle:
                            metaInfo = meta.get_episode_meta(TVShowTitle, imdbID, str(season), str(episode))
                        if metaInfo and int(metaInfo['overlay']) == 6:
                            meta.change_watched(mediaType, name, imdbID, season=season, episode=episode)
                            xbmc.executebuiltin("XBMC.Container.Refresh")
                    else:
                        logger.info('Could not change watched status; imdbID or mediaType missing')
            except Exception as e:
                logger.info(e)
                
    def onPlayBackEnded(self):
        logger.info('Playback completed')
        self.onPlayBackStopped()
        
class cPlayer:
      
    
    def clearPlayList(self):
        oPlaylist = self.__getPlayList()
        oPlaylist.clear()

    def __getPlayList(self):
        return xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

    def addItemToPlaylist(self, oGuiElement):
        oGui = cGui()
        oListItem =  oGui.createListItem(oGuiElement)
        self.__addItemToPlaylist(oGuiElement, oListItem)
	
    def __addItemToPlaylist(self, oGuiElement, oListItem):    
        oPlaylist = self.__getPlayList()	
        oPlaylist.add(oGuiElement.getMediaUrl(), oListItem )

    def startPlayer(self):
        logger.info('start player')
        xbmcPlayer = XstreamPlayer()
        #logger.info('add playlist to player instance')
        #oPlayList = self.__getPlayList()
        #xbmcPlayer.play(oPlayList)

        if not cConfig().getSetting('metahandler')=='true':
            logger.info('MetaHandler is deactivated, stopping player monitor')
            return
        while (not xbmc.abortRequested) & (not xbmcPlayer.streamFinished):
            while xbmcPlayer.isPlayingVideo():
                xbmcPlayer.playedTime = xbmcPlayer.getTime()
                xbmc.sleep(1000)
            xbmc.sleep(1000)
            
        
