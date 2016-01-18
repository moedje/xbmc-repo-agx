#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os, os.path
import xbmc, xbmcplugin, xbmcvfs, xbmcaddon, xbmcgui
from xbmcUtils import xbmcUtils
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
xutil = xbmcUtils(pluginhandle=thisPlugin)
addonId = "plugin.video.largecamtube"
__addon__ = xbmcaddon.Addon(id=addonId)
__addonpath__ = __addon__.getAddonInfo('path')
dataPath = xbmc.translatePath('special://profile/addon_data/%s' % (addonId))
viewMode = 500
try:
    if not os.path.exists(dataPath) or xbmcvfs.exists(dataPath):
        xbmcvfs.mkdir(dataPath)
    __addonpath__ = __addon__.getAddonInfo("path")
    if path.exists(__addonpath__):
        __res__ = os.path.join(__addonpath__, "resources")
    else:
        __addonpath__ = os.path.join(xbmc.translatePath('special://home/addons/'), addonId)
        __res__ = os.path.join(xbmc.translatePath('special://home/addons/{0}'.format(addonId)), "resources/")
except:
    __addonpath__ = xbmc.translatePath('special://home/addons/{0}/'.format(addonId))
    __res__ = os.path.join(__addonpath__, "resources/")
try:
    sortBy = __addon__.getSetting("sortby")
    searchQ = __addon__.getSetting("lastsearch")
    viewMode = int(__addon__.getSetting("viewmode"))
    doPaginate = bool(__addon__.getSetting("dopaginate"))
except:
    doPaginate = False
    viewMode = 500
    sortBy = "recent"
    searchQ = ""
imgSearch = os.path.join(__addonpath__, "search.png")
imgGay = os.path.join(__addonpath__, "gaylogo.png")
Host = "http://www.largecamtube.com/"

def setView(vmode=viewMode, enddir=True):
    xutil.setSortMethodsForCurrentXBMCList(sortKeys=['none', 'file', 'size', 'name'])
    try:
        if vmode is None or vmode == "":
            vmode = 500
            __addon__.setSetting('viewmode', vmode)
    except:
        vmode = 500
    xbmc.executebuiltin("Container.SetViewMode({0})".format(vmode))
    if enddir:
        ok = xbmcplugin.endOfDirectory(thisPlugin)
        return ok

def getUrlGay(url):
    pass  # print "Here in getUrl url =", url
    urlofpage = url
    urlsetgay = "http://www.tubesex.com/backend/setting/change/3/1"
    req = urllib2.Request(urlsetgay)
    req.add_data('cset=1&s_s%5B%5D=2')
    req.add_header('Set-Cookie', 'CSC0=W10%3D')
    req.add_header('User-Agent',
                   'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link = response.read()
    newreq = urllib2.Request(urlofpage, data=req.get_data(), headers=req.headers, origin_req_host=req.get_origin_req_host())
    response = urllib2.urlopen(newreq)
    link = response.read()
    response.close()
    return link


def getUrl(url):
    urlofpage = url.replace(' ', '+')
    urlsetgay = "http://www.tubesex.com/backend/setting/change/3/1"
    req = urllib2.Request(urlsetgay)
    req.add_data('cset=1&s_s%5B%5D=2')
    req.add_header('Set-Cookie', 'CSC0=W10%3D')
    req.add_header('User-Agent',
                   'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link = response.read()
    newreq = urllib2.Request(urlofpage, data=req.get_data(), headers=req.headers, origin_req_host=req.get_origin_req_host())
    response = urllib2.urlopen(newreq)
    link = response.read()
    response.close()
    return link

def showContent():
    pic = "special://home/addons/{0}/search.png".format(addonId)
    picgay = "special://home/addons/{0}/gaylogo.png".format(addonId)
    addDirectoryItem("Search", {"name": "Search", "url": Host, "mode": 4}, pic)
    i = 0
    content = getUrl(Host)
    n1 = content.find('<div class="list bullet clear">', 0)
    n2 = content.find('</div>', n1)
    content = content[n1:n2]
    regexvideo = '<a href="(.*?)">(.*?)<'
    match = re.compile(regexvideo, re.DOTALL).findall(content)
    litems = []
    gitems = []
    for url, name in match:
        name = name.lower()
        name = name.replace('"','')
        name = name.replace('+', ' ')
        url1 = str(url.replace(' ', '+'))
        if (name.find("gay") != -1 or name.find("boy") != -1 or name.find("twink") != -1 or name.find("dick") != -1)  and (name.find("ladyboy") == -1 and name.find("boyfriend") == -1 and name.find("girl") == -1):
            item = str("[COLOR red]" + name.title() + "[/COLOR]"), url1, 1, picgay
            gitems.append(item)
        elif name.find("girl") == -1 and name.find("lesb") == -1 and name.find("lady") == -1 and name.find("bisex") == -1 and name.find("tran") == -1:
            item = name.title(), url1, 1, "DefaultFolder.png"
            litems.append(item)
    litems.sort()
    gitems.sort()
    gitems.extend(litems)
    for name, url, mode, pic in gitems:
        addDirectoryItem(name, {"name": name, "url": url, "mode": mode}, pic)
    setView(51, False)
    return xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), cacheToDisc=True, updateListing=True, succeeded=True)

# http://www.tubesex.com/search/?q=Anal&kwid=5462&c=1&p=2&lid=1
def getPage(name, urlmain):
    pages = [1, 2, 3, 4, 5, 6]
    n1 = str(urlmain).find("&lid=1", 0)
    if (n1 < 0):
        return
    url1 = urlmain[:(n1)]
    url2 = urlmain[n1:]
    for page in pages:
        text = "?q=&p=" + str(page - 1)
        url = url1 + text.replace(' ', '+') + url2
        name = "Page " + str(page)
        pic = "DefaultFolder.png"
        if doPaginate:
            addDirectoryItem(name, {"name": name, "url": url, "mode": 2}, pic)
        else:
            getVideos(name, url, False)
    if doPaginate:
        setView(51)
    else:
        setView(viewMode)
    #xbmcplugin.endOfDirectory(thisPlugin)
    #xbmc.executebuiltin("Container.SetViewMode(51)")

def getVideos(name1, urlmain, enddir=True):
    content = getUrl(urlmain.replace(' ', '+'))
    regexvideo = '<div class="thumb">.*?href="(.*?)".*?img src="(.*?)" alt="(.*?)"'
    match = re.compile(regexvideo, re.DOTALL).findall(content)
    smatches = []
    matches, smatches = getGayMatch(match)
    for url, pic, nameof in matches:
        name = nameof.replace("[Cr]","[CR]")
        name = name.replace("[Color Red","[COLOR RED")
        name = name.replace("[/Color","[/COLOR")
        addDirectoryItem(name, {"name": name, "url": url, "mode": 3}, pic)
    if enddir:
        setView()
    #xbmcplugin.endOfDirectory(thisPlugin)
    #xbmc.executebuiltin("Container.SetViewMode(500)")

def getGayMatch(matches):
    boymatches = []
    others = []
    goodwords = ["gay", "twink", "boy", "male", "man", "guy", "bro", "men"]
    for url, pic, name in matches:
        name = str(name.replace('"', '')).lower()
        name = name.replace("free", "")
        name = name.replace("xxx", "")
        name = name.replace("www.", "")
        name = name.replace('-','[CR]')
        if name.find("gf") == -1 and name.find("tran") == -1 and name.find("bisex") == -1 and name.find("latina") == -1 and name.find("gilr") == -1 and name.find("chick") == -1 and name.find("breast") == -1 and name.find("mom") == -1 and name.find("gran") == -1 and name.find("girl") == -1 and name.find("boob") == -1 and name.find("milf") == -1 and name.find("her") == -1 and name.find("female") == -1 and name.find("straight") == -1 and name.find("babe") == -1 and name.find("woman") == -1 and name.find("pussy") == -1 and name.find("lesbian") == -1 and name.find("she") == -1 and name.find("tit") == -1 and name.find("lady") == -1:
            found = False
            for w in goodwords:
                if name.find(w) != -1:
                    found = True
                    name = name.replace(w, "[COLOR red]{0}[/COLOR]".format(w.title()))
            if found:
                name = "[B]{0}[/B]".format(name.title())
                item = url, pic, name
                boymatches.append(item)
            else:
                item = url, pic, name.title()
                others.append(item)
            found = False
    others.sort()
    boymatches.sort()
    boymatches.extend(others)
    return boymatches, others


# http://www.tubesex.com/search/?lid=1&q=german+nikita&submit=Search
def getSearchQuery(name, url):
    text = ""
    try:
        text = __addon__.getSetting('lastsearch')
    except:
        text = ""
    searchQ = text.replace('+', ' ').title()
    newtext = xutil.getKeyboard(text, "Search")
    #kb = xbmc.Keyboard(text, 'Search', True)
    #kb.doModal()
    if newtext is not None:
        text = newtext.replace(' ', '+')
        searchQ = newtext.title()
        __addon__.setSetting('lastsearch', searchQ)
    name = '{0}'.format(searchQ)
    url1 = "http://www.tubesex.com/search/?lid=1&q=" + text + "&submit=Search"
    getVideos2(name, url1)


def getVideos2(name, url):
    pass  # print "Here in getVideos2 url =", url
    content = getUrl(url)
    regexvideo = '<iframe src="(.*?)"'
    match = re.compile(regexvideo, re.DOTALL).findall(content)
    url = match[0]

    """
        try:
               regexvideo = "clip.*?'(.*?)'"
               match = re.compile(regexvideo,re.DOTALL).findall(content)
               pass#print "match =", match
               vurl = match[0]
        except:
               pass
        try:
               regexvideo = "video_url: '(.*?)'"
               match = re.compile(regexvideo,re.DOTALL).findall(content)
               pass#print "match =", match
               vurl = match[0]
        except:
               pass
        try:
               regexvideo = 'var videoFile="(.*?)"'
               match = re.compile(regexvideo,re.DOTALL).findall(content)
               pass#print "match =", match
               vurl = match[0]
        except:
               pass
        try:
               regexvideo = '<source src="(.*?)"'
               match = re.compile(regexvideo,re.DOTALL).findall(content)
               pass#print "match =", match
               vurl = match[0]
        except:
               pass
        try:
               regexvideo = 'file="(.*?)"'
               match = re.compile(regexvideo,re.DOTALL).findall(content)
               pass#print "match =", match
               vurl = match[0]
        except:
               pass       
        try:
               regexvideo = 'file:"(.*?)"'
               match = re.compile(regexvideo,re.DOTALL).findall(content)
               pass#print "match =", match
               vurl = match[0]
        except:
               pass   
        try:
               regexvideo = 'Quality FLV.*?a href="(.*?)"'
               match = re.compile(regexvideo,re.DOTALL).findall(content)
               pass#print "match =", match
               vurl = "http:" + match[0]
        except:
               pass   
        """
    if "xvideos" in url:
        url = url.replace("http://flashservice.xvideos.com/embedframe/", "http://www.xvideos.com/video") + "/"
        pass  # print "content B3 =", content

        regexvideo = 'flv_url=(.*?)&amp;'
        match = re.compile(regexvideo, re.DOTALL).findall(content)
        for url in match:
            url = url.replace("%3A", ":")
            url = url.replace("%2F", "/")
            url = url.replace("%3F", "?")
            url = url.replace("%3D", "=")
            url = url.replace("%26", "&")
            player = xbmc.Player()
            player.play(url)
            break

    elif "pornhub" in url.lower():
        regexvideo = 'iframe src=&quot;(.*?)&quot;'
        match = re.compile(regexvideo, re.DOTALL).findall(content)
        url1 = match[0]
        content = getUrl(url1)
        n1 = content.find(".mp4", 0)
        n2 = content.rfind("http", 0, n1)
        n3 = content.find("'", n1)
        url11 = content[n2:n3]
        player = xbmc.Player()
        player.play(url11)
    """
    if "tubeq" in url:
            regexvideo = "clip.*?'(.*?)'"
    elif "theclassicporn" in url:
            regexvideo = "video_url: '(.*?)'"
    elif "fantasy8" in url:
            regexvideo = 'var videoFile="(.*?)"'
    elif "kinkytube" in url:
            regexvideo = 'var videoFile="(.*?)"'
    elif "alphaporno" in url:
            regexvideo = "video_url: '(.*?)'"
    elif "vid2c" in url:
            regexvideo = 'var videoFile="(.*?)"'
    elif "hd21" in url:
            regexvideo = '<source src="(.*?)"'
    elif "winporn" in url:
            regexvideo = '<source src="(.*?)"'
    elif "wankoz" in url:
            regexvideo = "video_url: '(.*?)'"
    elif "drtuber" in url:
            regexvideo = '<source src="(.*?)"'
    elif "hd21" in url:
            regexvideo = '<source src="(.*?)"'
    elif "winporn" in url:
            regexvideo = '<source src="(.*?)"'
 else:
        regexvideo = '<source src="(.*?)"'
    match = re.compile(regexvideo,re.DOTALL).findall(content)
    pass#print "match =", match
    vurl = match[0]
    pass#print "vurl =", vurl
    player = xbmc.Player()
    player.play(vurl)
    """


def getVideos4(name1, urlmain):
    n1 = urlmain.find(".html", 0)
    if (n1 < 0):
        return
    n2 = urlmain.rfind("-", 0, n1)
    if (n2 < 0):
        return
    pn = "4"
    url1 = urlmain[:(n2 + 1)]
    url2 = urlmain[n1:]
    # pass#print "Here in getVideos2 url1 =", url1
    # pass#print "Here in getVideos2 url2 =", url2
    url = url1 + pn + url2
    # pass#print "Here in getVideos2 url =", url
    content = getUrl(url)
    # pass#print "content B2 =", content
    pos0 = content.find("Promoted Videos", 0)
    if (pos0 < 0):
        return
    pos1 = content.find("<div class='video'", pos0)
    if (pos1 < 0):
        return
    content = content[pos1:]

    regexvideo = "><a href='(.*?)'.*?alt=(.*?)/>"
    matches = re.compile(regexvideo, re.DOTALL).findall(content)
    smatch = []
    match, smatch = getGayMatch(matches)
    for url, pic, name in match:
        addDirectoryItem(name, {"name": name, "url": url, "mode": 3}, pic)
    name = "More videos"
    addDirectoryItem(name, {"name": name, "url": urlmain, "mode": 7}, pic)
    xbmcplugin.endOfDirectory(thisPlugin)
    xbmc.executebuiltin("Container.SetViewMode(500)")

def getVideos5(name1, urlmain):
    n1 = urlmain.find(".html", 0)
    if (n1 < 0):
        return
    n2 = urlmain.rfind("-", 0, n1)
    if (n2 < 0):
        return
    pn = "5"
    url1 = urlmain[:(n2 + 1)]
    url2 = urlmain[n1:]
    url = url1 + pn + url2
    content = getUrl(url)
    pos0 = content.find("Promoted Videos", 0)
    if (pos0 < 0):
        return
    pos1 = content.find("<div class='video'", pos0)
    if (pos1 < 0):
        return
    content = content[pos1:]
    regexvideo = "><a href='(.*?)'.*?alt=(.*?)/>"
    matches = re.compile(regexvideo, re.DOTALL).findall(content)
    smatch = []
    match, smatch = getGayMatch(matches)
    for url, pic, name in match:
        addDirectoryItem(name, {"name": name, "url": url, "mode": 3}, pic)
    xbmcplugin.endOfDirectory(thisPlugin)
    xbmc.executebuiltin("Container.SetViewMode(500)")

def playVideo(name, url):
    pass  # print "Here in playVideo url =", url
    fpage = getUrl(url)
    pass  # print "fpage C =", fpage
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

    pic = "DefaultFolder.png"
    pass  # print "Here in playVideo url B=", url
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

    ok = showContent()
else:
    if mode == str(1):
        ok = getVideos(name, url)
    elif mode == str(3):
        ok = getVideos2(name, url)
    elif mode == str(4):
        ok = getSearchQuery(name, url)
    elif mode == str(5):
        ok = getPage(name, url)  # getVideos3x
    elif mode == str(6):
        ok = getVideos4(name, url)
    elif mode == str(7):
        ok = getVideos5(name, url)
