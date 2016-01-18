import xbmc
from resources.lib.handler.ParameterHandler import ParameterHandler

LOG_LEVEL_INFO = 0;
LOG_LEVEL_ERROR = 1;
LOG_LEVEL_FATAL = 2;

logLevel = LOG_LEVEL_INFO# (config.getSetting("debug")=="true")

def info(sInfo):
    if (logLevel <= LOG_LEVEL_INFO):
        __writeLog(sInfo, xbmc.LOGNOTICE);

def error(sInfo):
    if (logLevel <= LOG_LEVEL_FATAL):
         __writeLog(sInfo, xbmc.LOGERROR);

def fatal(sInfo):
    if (logLevel <= LOG_LEVEL_FATAL):
         __writeLog(sInfo, xbmc.LOGFATAL);

def __writeLog(sLog, cLogLevel):
    params = ParameterHandler()
    if params.exist('site'):
        site = params.getValue('site')
        print "\t[xStream] ->" + site + ": " + str(sLog)
    else:
        print "\t[xStream] " + str(sLog)
