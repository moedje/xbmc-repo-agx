# The documentation written by Voinage was used as a template for this addon
# http://wiki.xbmc.org/?title=HOW-TO_write_plugins_for_XBMC
#
# This addon is licensed with the GNU Public License, and can freely be modified
# http://www.gnu.org/licenses/gpl-2.0.html

import urllib
import urllib2
import re
import xbmcplugin
import xbmcgui
import xbmcaddon
from BeautifulSoup import MinimalSoup as BeautifulSoup

# xbmc hooks
__settings__ = xbmcaddon.Addon( id="plugin.video.gaypornium" )

# examples i'm working from always define functions before the main program code, so I'm assuming that's a requirement.

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
                                
    return param

def displayRootMenu():
    addListItem('Latest Videos',base_url+'most-recent/','scrapeVideoList','DefaultFolder.png')
    addListItem('Random Videos',base_url+'random/','scrapeVideoList','DefaultFolder.png')
    addListItem('Top Rated Videos',base_url+'top-rated/','scrapeVideoList','DefaultFolder.png')
    # todo: channels; search


def addListItem(name,url,mode,iconimage):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&thumb="+urllib.quote_plus(iconimage)
    ok=True
    name=BeautifulSoup(name, convertEntities=BeautifulSoup.HTML_ENTITIES).contents[0]
    if mode=='scrapeVideoList':
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    elif mode=='playVideo':
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    if mode=='scrapeVideoList':
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    elif mode=='playVideo':
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    return ok


def indexVideos(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()

    match=re.compile('<a href="http://www.gaypornium.com(/videos/.*\.html)"><img class="img" src="(.*\.jpg)" alt="(.*)" id=').findall(link)

    for url,thumbnail,name in match:
        addListItem(name,base_url + url,'playVideo',urllib.quote(thumbnail,':/'))

    match2=re.search('<a href=\'(?P<url>page[0-9]{1,5}\.html)\'>Next &raquo;</a>', link)
    if match2 is not None:
        addListItem('Go to next page (' + ')',base_url + '/' + match2.group('url'),'scrapeVideoList','DefaultFolder.png')


def playVideo(url,name,thumb):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    match=re.compile('url: \'([A-Za-z0-9_/.:-?&=]*)\',').findall(link)
    name=BeautifulSoup(urllib.unquote_plus(name), convertEntities=BeautifulSoup.HTML_ENTITIES).contents[0]
    for url in match:
        listitem = xbmcgui.ListItem(name)
        listitem.setInfo('video', {'Title': name, 'Genre': 'Porn'})
        listitem.setThumbnailImage(urllib.unquote_plus(thumb))
       	xbmc.Player().play(url, listitem)


# initialize variables
url=None
name=None
thumb=None
mode=None

# get parameters passed through plugin URL
params=get_params()

# set any parameters that were passed through the plugin URL
try:
    url=urllib.unquote_plus(params["url"])
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    thumb=urllib.unquote_plus(params["thumb"])
except:
    pass
try:
    mode=urllib.unquote_plus(params["mode"])
except:
    pass

# ok - the parameters are initialized where are we scraping?
base_url='http://www.gaypornium.com/'
categories_url=base_url + 'channels/'
search_url=base_url + 'search/videos/'

# log some basics to the debug log for funzies.
print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

if mode==None or url==None or len(url)<1:
    print base_url
    displayRootMenu()
       
elif mode=='scrapeVideoList':
    print ""+url
    indexVideos(url)
        
elif mode=='playVideo':
    print ""+url
    playVideo(url,name,thumb)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
