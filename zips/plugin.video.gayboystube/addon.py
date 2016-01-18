#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import urllib
import urllib2
import re
import xbmcplugin
import xbmc
import xbmcgui
import xbmcaddon, xbmcvfs
import os, os.path
import htmlentitydefs
from urlparse import parse_qs
from urllib import unquote_plus, basejoin
from htmlentitydefs import name2codepoint as n2cp
from xml.sax.saxutils import unescape

# xbmc hooks
__addonid__ = "plugin.video.gayboystube"
__settings__ = xbmcaddon.Addon(id=__addonid__)
__addonpath__ = os.path.join(xbmc.translatePath("special://home/addons/{0}/".format(__addonid__)), "resources/")
__res__ = os.path.join(xbmc.translatePath("special://home/addons/{0}/".format(__addonid__)), "resources/")
Hostbase = 'http://www.gayboystube.com/'
base_url = 'http://www.gayboystube.com/'
urlcats = 'channels/'
search_url = base_url + 'search/videos/'
viewMode = 500
basecaturl = 'http://www.gayboystube.com/channels/'

citems = [("Action","4/action/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat4.jpg"),
          ("Amature","5/amature/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat5.jpg"),
          ("Asian","6/asian/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat6.jpg"),
          ("Ass Play","42/ass-play/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat42.jpg"),
          ("Bareback","7/bareback/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat7.jpg"),
          ("Big Cocks","35/big-cocks/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat35.jpg"),
          ("Bisexual","37/bisexual/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat37.jpg"),
          ("Black","8/black/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat8.jpg"),
          ("Blond Boys","39/blond-boys/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat39.jpg"),
          ("Cartoons","47/cartoons/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat47.jpg"),
          ("Cum Shots","9/cum-shots/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat9.jpg"),
          ("Father and Son","36/father-and-son/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat36.jpg"),
          ("Fetish","11/fetish/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat11.jpg"),
          ("First Time","45/first-time/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat45.jpg"),
          ("Foot Fetish","38/foot-fetish/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat38.jpg"),
          ("Frat Guys","12/frat-guys/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat12.jpg"),
          ("Fun","22/fun/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat22.jpg"),
          ("Glory Holes","13/glory-holes/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat13.jpg"),
          ("Group Sex","14/group-sex/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat14.jpg"),
          ("Handjob","44/handjob/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat44.jpg"),
          ("Interracial","15/interracial/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat15.jpg"),
          ("Latino","16/latino/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat16.jpg"),
          ("Medical","43/medical/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat43.jpg"),
          ("Mix","2/mix/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat2.jpg"),
          ("Movies","3/movies/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat3.jpg"),
          ("Muscle Boys","18/muscle-boys/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat18.jpg"),
          ("Music","46/music/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat46.jpg"),
          ("Oral","17/oral/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat17.jpg"),
          ("Public Outside","40/public-outside/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat40.jpg"),
          ("Redheads","48/redheads/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat48.jpg"),
          ("Short Films","32/short-films/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat32.jpg"),
          ("Solo","34/solo/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat34.jpg"),
          ("Straight Boys","21/straight-boys/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat21.jpg"),
          ("Vintage","33/vintage/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat33.jpg"),
          ("Voyeur","41/voyeur/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat41.jpg"),
          ("Web-Cam","19/web-cam/", "scrapeVideoList", "http://cdn.gayboystube.com/misc/cat19.jpg")]
std_headers = {
    'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.6) Gecko/20100627 Firefox/3.6.6',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-us,en;q=0.5',
}

def getUrl(url):
    pageurl = str(url).lower().replace(' ', '+')
    if pageurl.find("%2f") != -1:
        pageurl = str(Hostbase + '/' + str(url.partition('.com%2f')[-1])).replace('%2f', '/')
    req = urllib2.Request(pageurl)
    req.headers.update(std_headers)
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link

def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param

def displayRootMenu():
    addListItem('Categories', urlcats, 'loadVideoList', 'DefaultFolder.png')
    addListItem('Latest Videos', 'most-recent/', 'scrapeVideoList', 'DefaultFolder.png')
    addListItem('Random Videos', 'random/', 'scrapeVideoList', 'DefaultFolder.png')
    addListItem('Top Rated Videos', 'top-rated/', 'scrapeVideoList', 'DefaultFolder.png')
    addListItem('Top Favorites', 'top-favorites/', 'scrapeVideoList', 'DefaultFolder.png')
    addListItem('Most Viewed', 'most-viewed/', 'scrapeVideoList', 'DefaultFolder.png')
    addListItem('Most Commented', 'most-discussed/', 'scrapeVideoList', 'DefaultFolder.png')
    displayCatMenu()

def displayCatMenu():
    litems = []
    for cats in citems:
        caturl = basejoin(Hostbase, str(urlcats + cats[1]))
        u = sys.argv[0] + "?url=" + caturl + "&mode=scrapeVideoList"
        litems.append(makeListItem(itemname=cats[0], runmode='scrapeVideoListCat', webpageurl=caturl, pic=cats[3], folder=True, itemproperties={"name": cats[0], "thumb": cats[3], "path": u, "url": caturl, "page": "page1.html"}))
    addItems(litems)
    setView()

def addListItem(name, url, mode, thimg, page="page1.html"):
    u = sys.argv[0] + "?url=" + str(url).replace(' ', '+') + "&mode=" + str(mode) + "&name=" + str(
        name).replace(' ', '+') + "&thumb=" + str(thimg) + "&page=" + str(page)
    ok = True
    liz = xbmcgui.ListItem(label=name, label2=mode, iconImage=thimg, thumbnailImage=thimg, path=url)
    if mode == 'loadVideoList':
        liz = xbmcgui.ListItem(label=name, label2=mode, path=url, iconImage=thimg, thumbnailImage=thimg)
    elif mode == 'scrapeVideoList':
        liz = xbmcgui.ListItem(label=name, label2=mode, path=url, iconImage=thimg, thumbnailImage=thimg)
    elif mode == 'playVideo':
        liz = xbmcgui.ListItem(name, iconImage=thimg, thumbnailImage=thimg)
        liz.setInfo(type="Video", infoLabels={"Title": name})
    if mode == 'scrapeVideoList':
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    elif mode == 'playVideo':
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=False)
    return ok

def indexCatVideos(curl, pname):
    litems = []
    pitems = []
    pageurl = str(curl).replace('page1.html', 'page{0}.html')
    if pageurl.find('page{0}.html') == -1:
        pageurl = str(curl).rstrip('/') + '/page{0}.html'
    for page in range(1, 6):
        fullpageurl = pageurl.format(str(page))
        pitems = getPageVids(nameofpage=pname, pageurl=curl)
        litems.extend(pitems)
        pitems = []
    litems.sort()
    addItems(litems, True)

def indexVideos(urlpath, page):
    litems = []
    pitems = []
    fullurl = basejoin(base_url, str(urlpath.rstrip('/') + "/page{0}.html"))
    for pagenum in range(1, 6):
        pitems = getPageVids(pageurl=fullurl.format(str(pagenum)), nameofpage="{0} {1}".format(page, str(pagenum)))
        litems.extend(pitems)
        pitems = []
    litems.sort()
    addItems(litems, True)

def getPageVids(pageurl, nameofpage):
    content = getUrl(pageurl)
    regexvideo = ur'this.src="(?P<thumbnail>http://cdn.gayboystube.com/thumbs/[A-Z0-9a-z/. -_]*[wmvaiflp4]{3}-[0-9].jpg)";\' width="[0-9]{3}" height="[0-9]{3}" alt="(?P<name>[A-Za-z0-9!-@#$%^&*(),.;:\' ]*)" />\r\n\r\n\t\t\t</a>\r\n\r\n\t<a href="http://www.gayboystube.com/(?P<url>video/[0-9]{5,7}/[0-9a-z-]*)" class="title"'
    #regexvideo = ur'thumb_container video.*?href="(.*?)" title="(.*?)">.*?src="(.*?)"'
    match = re.compile(regexvideo, re.UNICODE).findall(content)
    litems = []
    for url, name, pic in match:
        name = name.replace('"', '')
        label = str(name.title())
        vidurl = basejoin(base_url, url)
        litems.append(makeListItem(itemname=label, runmode='playVideo', webpageurl=vidurl, pic=pic, folder=False, itemproperties={"title": label, "thumbnailImage": pic, "name": name, "url": url, "mode": 'playVideo'}))
    return litems

def makeListItem(itemname, runmode, webpageurl, pic="DefaultFolder.png", folder=True, itemproperties={}):
    pathurl = sys.argv[0] + '?' + urllib.urlencode(itemproperties)
    li = xbmcgui.ListItem(label=itemname, label2=runmode, iconImage=pic, thumbnailImage=pic, path=webpageurl.replace(base_url,""))
    li.setProperty(key=url, value=webpageurl)
    li.setInfo(type='Video', infoLabels=itemproperties)
    litem = pathurl, li, folder,
    return litem

def addItems(itemslist=[], isend=False):
    if isend:
        xbmcplugin.addDirectoryItems(handle=int(sys.argv[1]), items=itemslist, totalItems=len(itemslist))
        return setView(endofdir=isend)
    return xbmcplugin.addDirectoryItems(handle=int(sys.argv[1]), items=itemslist, totalItems=len(itemslist))

def scrapeVideos(fullurl):
    curpagenum = "2"
    npage = int(str(fullurl.split('/page', 1)[1]).replace('.html', ''))
    try:
        if npage is not None:
            if npage > 1:
                curpagenum = str(npage + 1)
    except:
        curpagenum = "2"
    urlofpage = str(fullurl.split('/page', 1)[0]) + '/page{0}.html'
    link = getUrl(urlofpage.format(npage))
    match = re.compile(ur'this.src="(?P<thumbnail>http://cdn.gayboystube.com/thumbs/[A-Z0-9a-z/. -_]*[wmvaiflp4]{3}-[0-9].jpg)";\' width="[0-9]{3}" height="[0-9]{3}" alt="(?P<name>[A-Za-z0-9!-@#$%^&*(),.;:\' ]*)" />\r\n\r\n\t\t\t</a>\r\n\r\n\t<a href="http://www.gayboystube.com/(?P<url>video/[0-9]{5,7}/[0-9a-z-]*)" class="title"', re.UNICODE).findall(link)
    for thumbnail, name, url in match:
        addListItem(name, str(base_url + url), 'playVideo', thumbnail, page="page"+str(npage)+".html")
    match2 = re.search('<a href=\'(?P<pge>page[0-9]{1,5}\.html)\' class="next">Next</a>', link)
    npagenum = ""
    if match2 is not None:
        npagenum = str(match2.group('pge'))
        addListItem('Go to next page ({0})'.format(str(npagenum)), fullurl, 'scrapeVideoList', 'DefaultFolder.png', npagenum)
    addListItem('Next', fullurl, 'scrapeVideoList', 'DefaultFolder.png', str(curpagenum))
    setView(False)

def playVideo(vurl, name, thumb):
    link = getUrl(url=vurl)
    match = re.compile(ur"clip: {\r\n\t{7,9}url: \'([A-Za-z0-9_/.:-?&= _]*)\',", re.UNICODE).findall(link)[0]
    name = unescapeString(name) #.replace('+',' ')) #, convertEntities=BeautifulSoup.HTML_ENTITIES).contents[0]
    for url in match:
        li = xbmcgui.ListItem(label=name, label2=vurl, iconImage=os.path.join(__res__, 'logo.png'), thumbnailImage=thumb, path=url)
        li.setInfo('video', {'Title': name.title(), 'Genre': 'Porn'})
        li.setThumbnailImage(unescapeString(thumb))
        pl = xbmc.Player(playerCore=xbmc.PLAYER_CORE_AUTO)
        pl.play(item=url, listitem=li)
    #    req = urllib2.Request(url)
    #    req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    #    response = urllib2.urlopen(req)
    #    link = response.read()
    #    response.close()


def setView(endofdir=True):
    xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_LABEL)
    if endofdir:
        ok = xbmcplugin.endOfDirectory(int(sys.argv[1]))
        xbmc.executebuiltin("Container.SetViewMode({0})".format(viewMode))
        return ok
    else:
        xbmc.executebuiltin("Container.SetViewMode({0})".format(viewMode))

def unescapeHTML(text):
  def fixup(m):
    text = m.group(0)
    if text[:2] == "&#":
      # character reference
      try:
        if text[:3] == "&#x":
          return unichr(int(text[3:-1], 16))
        else:
          return unichr(int(text[2:-1]))
      except ValueError:
        pass
    else:
      # named entity
      try:
        text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
      except KeyError:
        pass
    return text # leave as is
  # Try to avoid broken UTF-8
  try:
    text = unicode(text, 'utf-8')
    ret = re.sub("&#?\w+;", fixup, text)
  except:
    ret = text
  return ret

def unescapeXML(text):
    try:
        ret = unescape(text, {"&apos;": "'", "&quot;": '"'})
    except:
        ret = text
    return ret

# Unesacpe wrapper
def unescapeString(text):
    pass1 = unescapeHTML(text)
    pass2 = unescapeHTML(pass1)
    pass3 = unescapeXML(pass2)
    return pass3

def parameters_string_to_dict(parameters):
    ''' Convert parameters encoded in a URL to a dict. '''
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = unescapeString(paramSplits[1])
    return paramDict

# initialize variables
url = None
name = None
thumb = None
mode = None
page = None

try:
    params = parameters_string_to_dict(sys.argv[2])
    name = unescapeString(str(params.get("name", "")))
    url = unescapeString(str(params.get("url", "")))
    mode = str(params.get("mode", ""))
    thumb = str(params.get("thumb", "DefaultFolder.png"))
    page = str(params.get("page", "1"))
except:
    params = get_params()
    try:
        try:
            url = unescapeString(params[url])
        except:
            url = unquote_plus(params[url])
        try:
            #name = urllib.unquote_plus(params["name"])
            name = unescapeString(str(params[name]).title())
        except:
            name = str(params[name])
        try:
            thumb = unescapeString(params[thumb])
        except:
            thumb = urllib.unquote_plus(params[thumb])
        try:
            mode = unescapeString(str(params[mode]))
        except:
            mode = urllib.unquote_plus(params[mode])
        try:
            if mode is None:
                mode = str(params[mode])
            if len(mode) < 1:
                mode = str(params[mode])
        except:
            pass
        try:
            page = str(params['page'])
        except:
            page = urllib.unquote_plus(params["page"])
    except:
        try:
            params = urllib2.parse_keqv_list(sys.argv[2])
        except:
            displayRootMenu()

if mode == None or url == None or len(url) < 1:
    displayRootMenu()
elif mode == 'loadVideoList':
    displayCatMenu()
elif mode == 'scrapeVideoListCat':
    indexCatVideos(url, name)
elif mode == 'scrapeVideoList':
    indexVideos(urlpath=basejoin(base_url, str(url +'/'+ page)), page="page{0}".format(page))
elif mode == 'playVideo':
    playVideo(url, name, thumb)

#setView(True)
#xbmcplugin.endOfDirectory(int(sys.argv[1]))
#xbmc.executebuiltin("Container.SetViewMode({0})".format(viewMode))
