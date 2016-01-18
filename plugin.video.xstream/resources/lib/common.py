import xbmcaddon

addonID = 'plugin.video.xstream'
addon = xbmcaddon.Addon(id = addonID)
addonPath = addon.getAddonInfo('path')
profilePath = addon.getAddonInfo('profile')