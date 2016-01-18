#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
from os import getcwd
from os.path import join
from sys import path
from xbmc import translatePath
from xbmc import log
from resources.lib import common

__settings__ = common.addon
__cwd__ = common.addonPath

# Add different library path
path.append(translatePath(join(__cwd__, "resources", "lib")))
path.append(translatePath(join(__cwd__, "resources", "lib", "gui")))
path.append(translatePath(join(__cwd__, "resources", "lib", "handler")))
path.append(translatePath(join(__cwd__, "resources", "art", "sites")))
path.append(translatePath(join(__cwd__, "sites")))

log("The new sys.path list: %s" % sys.path, level = xbmc.LOGDEBUG)

# Run xstream
from xstream import run
log('*---- Running xStream, version %s ----*' % __settings__.getAddonInfo('version'))
#import cProfile
#cProfile.run('run()',translatePath(join(__cwd__,'xstream.pstats')))
try:
    run()
except Exception, err:
    import traceback
    import xbmcgui
    print traceback.format_exc()
    dialog = xbmcgui.Dialog().ok('xStream Error',str(err.__class__.__name__),str(err))
    