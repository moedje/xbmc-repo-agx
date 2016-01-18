from resources.lib.gui.gui import cGui
from resources.lib.config import cConfig
import urllib2
import xbmc
import xbmcgui
import string
import logger
import time

class cDownload:

    def __createProcessDialog(self):
        oDialog = xbmcgui.DialogProgress()
        oDialog.create('Download')
        self.__oDialog = oDialog

    def __createDownloadFilename(self, sTitle):
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        filename = ''.join(c for c in sTitle if c in valid_chars)
        filename = filename.replace(' ','_')
        return filename

    def download(self,url, sTitle):
        self.__processIsCanceled = False
        # extract header
        try: header = dict([item.split('=') for item in (url.split('|')[1]).split('&')])
        except: header = {}
        logger.info('Header for download: %s' % (header))

        url = url.split('|')[0]    
        sTitle = self.__createTitle(url, sTitle)
        self.__sTitle = self.__createDownloadFilename(sTitle)
        
        oGui = cGui()
        self.__sTitle = oGui.showKeyBoard(self.__sTitle)
        if (self.__sTitle != False and len(self.__sTitle) > 0):
            sPath = cConfig().getSetting('download-folder')

            if sPath == '':
                dialog = xbmcgui.Dialog()
                sPath = dialog.browse(3, 'Downloadfolder', 'files', '')

            if (sPath != ''):                
                sDownloadPath = xbmc.translatePath(sPath +  '%s' % (self.__sTitle, ))
                try:
                    logger.info('download file: ' + str(url) + ' to ' + str(sDownloadPath))
                    self.__createProcessDialog()
                    request = urllib2.Request(url, headers=header)
                    self.__download(urllib2.urlopen(request), sDownloadPath)   
                except Exception as e:
                    logger.error(e)

                self.__oDialog.close()

    def __download(self, oUrlHandler, fpath):
        headers = oUrlHandler.info()

        iTotalSize = -1
        if "content-length" in headers:
            iTotalSize = int(headers["Content-Length"])

        chunk = 4096
        f = open(fpath, "wb")
        iCount = 0
        self._startTime = time.time()      
        while 1:
            iCount = iCount +1
            data = oUrlHandler.read(chunk)
            if not data or self.__processIsCanceled == True:                
                break
            f.write(data)
            self.__stateCallBackFunction(iCount, chunk, iTotalSize)
            

    def __createTitle(self, sUrl, sTitle):        
        aTitle = sTitle.rsplit('.')        
        if (len(aTitle) > 1):
            return sTitle
        
        aUrl = sUrl.rsplit('.')        
        if (len(aUrl) > 1):
            sSuffix = aUrl[-1]
            sTitle = sTitle + '.' + sSuffix
            
        return sTitle

    def __stateCallBackFunction(self, iCount, iBlocksize, iTotalSize):
        timedif = time.time() - self._startTime
        currentLoaded = float(iCount * iBlocksize)
        if timedif > 0.0:
            avgSpd = int(currentLoaded/timedif/1024.0)
        else:
            avgSpd = 5
        iPercent = int( currentLoaded*100/ iTotalSize)
        self.__oDialog.update(iPercent, self.__sTitle, '%s/%s@%dKB/s' %(self.__formatFileSize(currentLoaded),self.__formatFileSize(iTotalSize),avgSpd))

        if (self.__oDialog.iscanceled()):
            self.__processIsCanceled = True
            self.__oDialog.close()
            
    
    def __formatFileSize(self, iBytes):
        iBytes = int(iBytes)
        if (iBytes == 0):
            return '%.*f %s' % (2, 0, 'MB')
        
        return '%.*f %s' % (2, iBytes/(1024*1024.0) , 'MB')


