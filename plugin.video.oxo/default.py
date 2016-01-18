#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmc, xbmcplugin
import xbmcgui, xbmcaddon, xbmcvfs
import sys
import urllib, urllib2
import time
import re
from htmlentitydefs import name2codepoint as n2cp
import httplib
import urlparse
from os import path, system
import socket
from urllib2 import Request, URLError, urlopen
from urlparse import parse_qs
from urllib import unquote_plus

thisPlugin = int(sys.argv[1])
addonId = "plugin.video.oxo"
__addon__ = xbmcaddon.Addon(id=addonId)
__addonpath__ = __addon__.getAddonInfo('path')
__res__ = path.join(__addonpath__, 'resources')
dataPath = xbmc.translatePath('special://profile/addon_data/%s' % (addonId))
try:
    if not path.exists(dataPath):
        xbmcvfs.mkdir(dataPath)
    sortBy = __addon__.getSetting("sortby")
    searchQ = __addon__.getSetting("lastsearch")
    viewMode = __addon__.getSetting("viewmode")
    doPaginate = __addon__.getSetting("dopaginate")
except:
    sortBy = "recent"
    searchQ = ""
    viewMode = 500
    doPaginate = False
Host = "http://oxotube.com/"
SERVERLIST = "Beeg|bigXvideos|BoysFood|GayFall|Hardsextube|HDporn|KeezMovies|PornerBros|PornHub|PornTube|SunPorno|Tube8|Xhamster"

def getUrl(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent',
                   'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link

def showContentA():
    types = []
    types.append("Tubes")
    types.append("Categories")
    types.append("Popular_Topics")
    types.append("Pornstars")
    i = 0
    pic = path.join(__addonpath__, "search.png")
    addDirectoryItem("Search", {"name": "Search", "url": Host, "mode": 8}, pic)
    while i < 4:
        url = Host
        pic = "DefaultFolder.png"
        name = types[i]
        i = i + 1
        addDirectoryItem(name, {"name": name, "url": url, "mode": 1}, pic)
    return setView()

def showContent(name):
    content = getUrl(Host)
    icount = 0
    start = 0
    n0 = content.find(">-any tube-<", 0)
    if n0 < 0:
        return
    n1 = content.find("</select>", n0)
    if n1 < 0:
        return
    n2 = content.find('<div class="clr"></div>', n1)
    if n2 < 0:
        return
    n3 = content.find('<div class="clr"></div>', (n2 + 5))
    if n3 < 0:
        return
    n4 = content.find('Most Popular <b><u>Free Porn</u></b> Tube Videos', n3)
    if n4 < 0:
        return
    n5 = content.find('Best Sex Tube Movie Sites', n4)
    if n5 < 0:
        return
    contenttub = content[n0:n1]
    contentcat = content[n2:n3]
    contentpop = content[n4:n5]
    names = []
    if name == "Tubes":
        regexcat = 'option value="(.*?)">(.*?)</option'
        match = re.compile(regexcat, re.DOTALL).findall(contenttub)
        for url, name in match:
            if name not in SERVERLIST:
                continue
            url1 = "http://oxotube.com" + url
            pic = "DefaultFolder.png"
            names.append(name)
            addDirectoryItem(name, {"name": name, "url": url1, "mode": 2}, pic)
#        ok = setView()
    if name == "Categories":
        regexcat = 'div class="thumb1.*?a href="(.*?)" title="(.*?)"'
        match = re.compile(regexcat, re.DOTALL).findall(contentcat)
        for url, name in match:
            url = url.replace("?tc=1", "")
            url1 = "http://oxotube.com" + url
            pic = "DefaultFolder.png"
            addDirectoryItem(name, {"name": name, "url": url1, "mode": 6}, pic)
#        ok = setView()
    if name == "Popular_Topics":
        regexcat = '<li><a href="(.*?)" title="(.*?)"'
        match = re.compile(regexcat, re.DOTALL).findall(contentpop)
        for url, name in match:
            url1 = "http://oxotube.com" + url
            pic = "DefaultFolder.png"
            addDirectoryItem(name, {"name": name, "url": url1, "mode": 6}, pic)
#        ok = setView()
    if name == "Pornstars":
        regexcat = '<li><a href="/pornstar/(.*?)/" title="Free.*?Porn">(.*?)<'
        match = re.compile(regexcat, re.DOTALL).findall(content)
        pass  # print "pornstars match =", match
        for url, name in match:
            url1 = "http://oxotube.com/pornstar/" + url + "/"
            pic = "DefaultFolder.png"
            addDirectoryItem(name, {"name": name, "url": url1, "mode": 6}, pic)
    return setView()

def getPage(name1, url):
    pages = [1, 2, 3, 4, 5, 6]
    for page in pages:
        url1 = url + "0/0/1/" + str(page)
        name = name1 + "-Page " + str(page)
        pic = "DefaultFolder.png"
        addDirectoryItem(name, {"name": name, "url": url1, "mode": 3}, pic)
    return setView()

def getPage2(name1, url):
    pages = [1, 2, 3, 4, 5, 6]
    for page in pages:
        url1 = url + "0/0/0/1/" + str(page)
        name = "Page " + str(page)
        pic = "DefaultFolder.png"
        addDirectoryItem(name, {"name": name, "url": url1, "mode": 7}, pic)
    return setView()

def getVideos(name1, urlmain):
    content = getUrl(urlmain)
    n1 = name1.find("Page", 0)
    name1 = name1[:(n1 - 1)]
    regexvideo = 'div class="thumb2.*?a href="(.*?)" title="(.*?)">.*?src="(.*?)"'
    match = re.compile(regexvideo, re.DOTALL).findall(content)
    n1 = 0
    for url, name, pic in match:
        name = name1 + "-" + name.replace('"', '')
        url = "http://oxotube.com" + url
        pic = pic
        n1 = n1 + 1
        addDirectoryItem(name, {"name": name, "url": url, "mode": 5}, pic)
    return setView()

def getVideos2(name1, urlmain):
    content = getUrl(urlmain)
    regexvideo = 'div class="thumb2.*?a href="(.*?)" title="(.*?)">.*?src="(.*?)".*?p class="sp r"><.*?title="(.*?)"'
    match = re.compile(regexvideo, re.DOTALL).findall(content)
    n1 = 0
    for url, name, pic, server in match:
        if server not in SERVERLIST:
            continue
        name = server + "-" + name.replace('"', '')
        url = "http://oxotube.com" + url
        pic = pic
        n1 = n1 + 1
        addDirectoryItem(name, {"name": name, "url": url, "mode": 5}, pic)
    return setView()

def askSearch():
    stext = searchQ
    try:
        kb = xbmc.Keyboard(line=stext, heading="Search Tubes", hidden=False)
        kb.doModal()
        if (kb.isConfirmed()):
            stext = kb.getText()
            stext = stext.replace(" ", "+")
            __addon__.setSetting("lastsearch", stext)
        if stext == "" or stext is None:
            stext = str(__addon__.getSetting('lastsearch'))
    except Exception, e:
        raise e
    return stext

def search(name, url):
    searchQ = askSearch()
    if searchQ is not None:
        __addon__.setSetting('lastsearch', searchQ)
    pic = "DefaultFolder.png"
    name = searchQ.replace('+', ' ')
    url1 = "http://oxotube.com/search/" + searchQ + "/?rsnm=1"
    return getVideos2(name, url1)

def setView():
    ok = xbmcplugin.endOfDirectory(thisPlugin)
    xbmc.executebuiltin("Container.SetViewMode(%s)" % viewMode)
    return ok


def pornoxo(name, url):
    pass  # pass#pass#print  "Here in pornoxo url =", url
    fpage = getUrl(url)
    pass  # pass#print  "fpage C =", fpage


def xhamster(name, url):
    pass  # pass#pass#print  "Here in pornoxo url =", url
    fpage = getUrl(url)
    #	   pass#pass#pass#print  "fpage C =", fpage
    pos1 = fpage.find("/xembed", 0)
    if (pos1 < 0):
        return
    pos2 = fpage.rfind("http", 0, pos1)
    if (pos2 < 0):
        return
    pos3 = fpage.find('"', pos1)
    if (pos2 < 0):
        return
    url = fpage[(pos2):(pos3)]
    fpage = getUrl(url)
    pass  # pass#pass#print  "fpage D =", fpage
    pos1 = fpage.find("http://xhamster.com/movies", 0)
    if (pos1 < 0):
        return
    pos2 = fpage.find("html", pos1)
    if (pos2 < 0):
        return
    url = fpage[(pos1):(pos2 + 4)]
    fpage = getUrl(url)
    pass  # pass#pass#print  "fpage E =", fpage
    start = 0
    pos1 = fpage.find(".flv", start)
    if (pos1 < 0):
        return
    pos2 = fpage.find("a href", pos1)
    if (pos2 < 0):
        return
    pos3 = fpage.find('"', (pos2 + 10))
    if (pos3 < 0):
        return
    url = fpage[(pos2 + 8):pos3]
    playVideo(name, url)


def tube8(name, url):
    pass  # pass#pass#print  "Here in pornoxo url =", url
    fpage = getUrl(url)
    #	   pass#pass#pass#print  "fpage C =", fpage
    pos1 = fpage.find("/embed", 0)
    if (pos1 < 0):
        return
    pos2 = fpage.rfind("http", 0, pos1)
    if (pos2 < 0):
        return
    pos3 = fpage.find('"', pos1)
    if (pos2 < 0):
        return
    url = fpage[(pos2):(pos3)]
    fpage = getUrl(url)
    pass  # pass#pass#print  "fpage D =", fpage
    pos1 = fpage.find("src		:", 0)
    if (pos1 < 0):
        return
    pos2 = fpage.find("http", pos1)
    if (pos2 < 0):
        return
    pos3 = fpage.find("'", pos2)
    if (pos3 < 0):
        return
    url = fpage[(pos2):(pos3)]
    playVideo(name, url)


def pornhub(name, url):
    pass  # pass#pass#print  "Here in pornoxo url =", url
    fpage = getUrl(url)
    #	   pass#pass#pass#print  "fpage C =", fpage
    pos1 = fpage.find("/embed", 0)
    if (pos1 < 0):
        return
    pos2 = fpage.rfind("http", 0, pos1)
    if (pos2 < 0):
        return
    pos3 = fpage.find('"', pos1)
    if (pos2 < 0):
        return
    url = fpage[(pos2):(pos3)]
    fpage = getUrl(url)
    pass  # pass#pass#print  "fpage D =", fpage
    pos1 = fpage.find("mp4", 0)
    if (pos1 < 0):
        return
    pos2 = fpage.rfind("http", 0, pos1)
    if (pos2 < 0):
        return
    pos3 = fpage.find("'", pos2)
    if (pos3 < 0):
        return
    url = fpage[(pos2):(pos3)]
    playVideo(name, url)


def hardsextube(name, url):
    pass  # pass#pass#print  "Here in pornoxo url =", url
    fpage = getUrl(url)
    #	   pass#pass#pass#print  "fpage C =", fpage
    pos1 = fpage.find("/embed", 0)
    if (pos1 < 0):
        return
    pos2 = fpage.find("/", (pos1 + 8))
    if (pos2 < 0):
        return
    url = "http://m.hardsextube.com/play/" + fpage[(pos1 + 7):(pos2)]

    fpage = getUrl(url)
    pass  # pass#pass#print  "fpage D =", fpage
    regexvideo = 'div id="interstitialBtn.*?a href="(.*?)"'
    match = re.compile(regexvideo, re.DOTALL).findall(fpage)
    pass  # pass#pass#print   "match =", match[0]
    url = match[0]
    playVideo(name, url)


def gayfall(name, url):
    pass  # pass#pass#print  "Here in pornoxo url =", url
    fpage = getUrl(url)
    #	   pass#pass#pass#print  "fpage C =", fpage
    pos1 = fpage.find("video_url", 0)
    if (pos1 < 0):
        return
    pos2 = fpage.find("http", pos1)
    if (pos2 < 0):
        return
    pos3 = fpage.find("'", pos2)
    if (pos3 < 0):
        return
    url = fpage[(pos2):(pos3)]
    playVideo(name, url)


def boysfood(name, url):
    pass  # pass#pass#print  "Here in pornoxo url =", url
    fpage = getUrl(url)
    #	   pass#pass#pass#print  "fpage C =", fpage
    pos1 = fpage.find("/embed", 0)
    if (pos1 < 0):
        return
    pos2 = fpage.rfind("http", 0, pos1)
    if (pos2 < 0):
        return
    pos3 = fpage.find('"', pos1)
    if (pos2 < 0):
        return
    url = fpage[(pos2):(pos3)]
    fpage = getUrl(url)
    pass  # pass#pass#print  "fpage D =", fpage
    pos1 = fpage.find("file:", 0)
    if (pos1 < 0):
        return
    pos2 = fpage.find("http", pos1)
    if (pos2 < 0):
        return
    pos3 = fpage.find("'", pos2)
    if (pos3 < 0):
        return
    url = fpage[(pos2):(pos3)]
    playVideo(name, url)


def bigxvideos(name, url):
    pass  # pass#pass#print  "Here in pornoxo url =", url
    fpage = getUrl(url)
    #	   pass#pass#pass#print  "fpage C =", fpage
    pos1 = fpage.find("/embed", 0)
    if (pos1 < 0):
        return
    pos2 = fpage.rfind("http", 0, pos1)
    if (pos2 < 0):
        return
    pos3 = fpage.find('"', pos1)
    if (pos2 < 0):
        return
    url = fpage[(pos2):(pos3)]
    fpage = getUrl(url)
    pass  # pass#pass#print  "fpage D =", fpage
    pos1 = fpage.find(".mp4", 0)
    if (pos1 < 0):
        return
    pos2 = fpage.rfind("http", 0, pos1)
    if (pos2 < 0):
        return
    url = fpage[(pos2):(pos1 + 4)]
    playVideo(name, url)


def beeg(name, url):
    pass  # pass#print  "Here in pornoxo url =", url
    fpage = getUrl(url)
    pass  # pass#print  "fpage C =", fpage

    pos1 = fpage.find(".mp4", 0)
    if (pos1 < 0):
        return
    pos2 = fpage.rfind("http", 0, pos1)
    if (pos2 < 0):
        return
    url = fpage[(pos2):(pos1 + 4)]
    playVideo(name, url)


def hdporn(name, url):
    pass  # pass#pass#print  "Here in pornoxo url =", url
    fpage = getUrl(url)
    #	   pass#pass#pass#print  "fpage C =", fpage
    pos1 = fpage.find("/embed", 0)
    if (pos1 < 0):
        return
    pos2 = fpage.rfind("http", 0, pos1)
    if (pos2 < 0):
        return
    pos3 = fpage.find('"', pos1)
    if (pos2 < 0):
        return
    url = fpage[(pos2):(pos3)]
    fpage = getUrl(url)
    pass  # pass#pass#print  "fpage D =", fpage
    pos1 = fpage.find(".mp4", 0)
    if (pos1 < 0):
        return
    pos2 = fpage.rfind("http", 0, pos1)
    if (pos2 < 0):
        return
    url = fpage[(pos2):(pos1 + 4)]
    playVideo(name, url)


def keezmovies(name, url):
    pass  # pass#pass#print  "Here in pornoxo url =", url
    fpage = getUrl(url)
    #	   pass#pass#pass#print  "fpage C =", fpage
    pos1 = fpage.find("/embed", 0)
    if (pos1 < 0):
        return
    pos2 = fpage.rfind("http", 0, pos1)
    if (pos2 < 0):
        return
    pos3 = fpage.find('"', pos1)
    if (pos2 < 0):
        return
    url = fpage[(pos2):(pos3)]
    fpage = getUrl(url)
    pass  # pass#pass#print  "fpage D =", fpage
    pos1 = fpage.find(".mp4", 0)
    if (pos1 < 0):
        return
    pos11 = fpage.find(".mp4", (pos1 + 2))
    if (pos11 < 0):
        return
    pos2 = fpage.rfind("http", 0, pos11)
    if (pos2 < 0):
        return
    pos3 = fpage.find("'", pos11)
    if (pos3 < 0):
        return
    url = fpage[(pos2):(pos3)]
    playVideo(name, url)


def sunporno(name, url):
    pass  # pass#pass#print  "Here in pornoxo url =", url
    fpage = getUrl(url)
    pass  # pass#pass#print  "fpage C =", fpage
    pos1 = fpage.find("/embed", 0)
    if (pos1 < 0):
        return
    pos2 = fpage.rfind("http", 0, pos1)
    if (pos2 < 0):
        return
    pos3 = fpage.find('"', pos1)
    if (pos2 < 0):
        return
    url = fpage[(pos2):(pos3)]
    fpage = getUrl(url)
    pass  # pass#pass#print  "fpage D =", fpage
    pos1 = fpage.find(".mp4", 0)
    if (pos1 < 0):
        return
    pos2 = fpage.rfind("http", 0, pos1)
    if (pos2 < 0):
        return
    url = fpage[(pos2):(pos1 + 4)]
    playVideo(name, url)


def playVideo(name, url):
    pic = "DefaultFolder.png"
    pass  # pass#pass#print  "Here in playVideo url B=", url
    li = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=pic)
    player = xbmc.Player()
    player.play(url, li)


std_headers = {
    'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.6) Gecko/20100627 Firefox/3.6.6',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-us,en;q=0.5',
}


def addDirectoryItem(name, parameters={}, pic="DefaultFolder.png"):
    li = xbmcgui.ListItem(name, iconImage=pic, thumbnailImage=pic)
    url = sys.argv[0] + '?' + urllib.urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=True)


def parameters_string_to_dict(parameters):
    ''' Convert parameters encoded in a URL to a dict. '''
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


params = parameters_string_to_dict(sys.argv[2])
name = str(params.get("name", ""))
url = str(params.get("url", ""))
url = urllib.unquote(url)
mode = str(params.get("mode", ""))

if not sys.argv[2]:
    ok = showContentA()
else:
    if mode == str(1):
        ok = showContent(name)
    elif mode == str(2):
        ok = getPage(name, url)
    elif mode == str(3):
        ok = getVideos(name, url)
    elif mode == str(4):
        ok = playVideo(name, url)
    elif mode == str(5):
        pass  # pass#print "Here in mode 5 name =", name
        if "Beeg" in name:
            pass  # pass#print "Here in Beeg"
            ok = beeg(name, url)
        if "bigXvideos" in name:
            ok = bigxvideos(name, url)
        if "BoysFood" in name:
            ok = boysfood(name, url)
        if "GayFall" in name:
            ok = gayfall(name, url)
        if "Hardsextube" in name:
            ok = hardsextube(name, url)
        if "HDporn":
            ok = hdporn(name, url)
        if "KeezMovies" in name:
            ok = keezmovies(name, url)
        if "PornerBros" in name:
            ok = pornerbros(name, url)
        if "PornHub" in name:
            ok = pornhub(name, url)
        if "Pornoxo" in name:
            ok = pornoxo(name, url)
        if "PornTube" in name:
            ok = porntube(name, url)
        if "SunPorno" in name:
            ok = sunporno(name, url)
        if "Tube8" in name:
            ok = tube8(name, url)
        if "Xhamster" in name:
            ok = xhamster(name, url)
        if "XVideos" in name:
            ok = pornoxo(name, url)
    elif mode == str(6):
        ok = getPage2(name, url)
    elif mode == str(7):
        ok = getVideos2(name, url)
    elif mode == str(8):
        ok = search(name, url)
