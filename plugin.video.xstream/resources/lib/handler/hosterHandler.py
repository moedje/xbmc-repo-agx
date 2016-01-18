# -*- coding: utf-8 -*-
from resources.lib.parser import cParser
from resources.lib.handler.requestHandler import cRequestHandler
import re
import urlresolver

class cHosterHandler:

    def getUrl(self, oHoster):
        sUrl = oHoster.getUrl()
        if (oHoster.checkUrl(sUrl)):
            oRequest = cRequestHandler(sUrl)            
            sContent = oRequest.request()
            pattern = oHoster.getPattern()
            if type(pattern) == type(''):
                aMediaLink = cParser().parse(sContent, oHoster.getPattern())
                if (aMediaLink[0] == True):
                    logger.info('hosterhandler: ' + aMediaLink[1][0])
                    return True, aMediaLink[1][0]
            else:
                for p in pattern:
                    aMediaLink = cParser().parse(sContent, p)
                    if (aMediaLink[0] == True):
                        logger.info('hosterhandler: ' + aMediaLink[1][0])
                        return True, aMediaLink[1][0]
                        
        return False, ''

    def getHoster2(self, sHoster):    
        # if (sHoster.find('.') != -1):
            # Arr = sHoster.split('.')
            # if (Arr[0].startswith('http') or Arr[0].startswith('www')):
                # sHoster = Arr[1]
            # else:
                # sHoster = Arr[0]
        return self.getHoster(sHoster)        
    '''
    checks if there is a resolver for a given hoster or url
    '''    
    def getHoster(self, sHosterFileName):
        if sHosterFileName != '':
            source = [urlresolver.HostedMediaFile(url=sHosterFileName)]
            if (urlresolver.filter_source_list(source)):
                return source[0].get_host()
            # media_id is in this case only a dummy
            source = [urlresolver.HostedMediaFile(host=sHosterFileName, media_id='ABC123XYZ')]            
            if (urlresolver.filter_source_list(source)):
                return source[0].get_host()
        return False   