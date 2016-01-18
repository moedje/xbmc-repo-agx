import urllib
import sys

class ParameterHandler:
	
    def __init__(self):          
        params = dict()
        if len(sys.argv)>=2 and len(sys.argv[2])>0:               
            params = dict(part.split('=') for part in sys.argv[ 2 ][ 1: ].split('&')) 
        for param in params:
            params[param]=urllib.unquote_plus(params[param])
        self.__params = params

    def getAllParameters(self):
        '''
        returns all parameters as dictionary
        '''
        return self.__params

    def getValue(self, paramName):
        '''
        returns value of one parameter as string, if parameter does not exists "False" is returned
        '''
        if (self.exist(paramName)):
            return self.__params[paramName]
            #paramValue = self.__params[paramName]                    
            #return urllib.unquote_plus(paramValue)
        return False

    def exist(self, paramName):
        '''
        checks if paramter with the name "paramName" exists
        '''
        return paramName in self.__params

    def delParam(self, paramName):
        self.__params.pop(paramName, None)
    
    def setParam(self, paramName, paramValue):
        '''
        set the value of the parameter with the name "paramName" to "paramValue"
        if there is no such parameter, the parameter is created
        if no value is given "paramValue" is set "None"
        '''
        paramValue = str(paramValue)
        self.__params.update( {paramName : paramValue} )


    def addParams(self, paramDict):
        '''
        adds a whole dictionary {key1:value1,...,keyN:valueN} of parameters to the ParameterHandler
        existing parameters are updated
        '''
        for key, value in paramDict.items():
            self.__params.update( {key : str(value)} )


    def getParameterAsUri(self):
        outParams = dict()
        #temp solution
        try:
            del self.__params['params']
        except:
            pass
        try:
            del self.__params['function']
        except:
            pass
        try:
            del self.__params['title']
        except:
            pass
        try:
            del self.__params['site']
        except:
            pass
        
        if len(self.__params) > 0:
            for param in self.__params:
                if len(self.__params[param])<1:
                    continue
                outParams[param]=urllib.unquote_plus(self.__params[param])
            return urllib.urlencode(outParams)
        return 'params=0'