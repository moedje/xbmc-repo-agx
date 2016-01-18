#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os, os.path as Path, re
import xbmc, xbmcplugin, xbmcaddon, xbmcvfs, xbmcgui
from xbmcUtils import xbmcUtils
import urllib, urllib2
from urllib2 import Request, URLError, urlopen
from urlparse import parse_qs
from urllib import unquote_plus, basejoin
import htmlentitydefs
from htmlentitydefs import name2codepoint as n2cp
from xml.sax.saxutils import unescape

thisPlugin = int(sys.argv[1])
addonId = "plugin.video.dagay"
__addon__ = xbmcaddon.Addon(id=addonId)
dataPath = xbmc.translatePath('special://profile/addon_data/{0}'.format(addonId))
xutil = xbmcUtils(pluginhandle=thisPlugin)
try:
    if not os.path.exists(dataPath):
        xbmcvfs.mkdir(dataPath)
    __addonpath__ = __addon__.getAddonInfo("path")
    if os.path.exists(__addonpath__):
        __res__ = os.path.join(__addonpath__, "resources")
    else:
        __addonpath__ = os.path.join(xbmc.translatePath('special://home/addons/'), addonId)
        __res__ = os.path.join(xbmc.translatePath('special://home/addons/{0}'.format(addonId)), "resources/")
except:
    __addonpath__ = xbmc.translatePath('special://home/addons/{0}/'.format(addonId))
    __res__ = os.path.join(__addonpath__, "resources/")
try:
    Hostbase = str(__addon__.getSetting("hostname"))
    sortBy = str(__addon__.getSetting("sortby"))
    searchQ = str(__addon__.getSetting("lastsearch"))
    viewMode = str(__addon__.getSetting("viewmode"))
    paginate = str(__addon__.getSetting("dopaginate")).lower()
    if paginate.find("true") == -1:
        doPaginate = False
    else:
        doPaginate = True
except:
    doPaginate = False
    viewMode = 500
    sortBy = "recent"
    searchQ = ""
    Hostbase = "http://www.dagay.com"
imgSearch = os.path.join(__addonpath__, "search.png")
imgFolder = os.path.join(__addonpath__, "dagay.png")
Host = basejoin(Hostbase, "/categories")
HostSearch = basejoin(Hostbase, "/s/")
Hostall = basejoin(Hostbase,"/videos?sort=editorchoice")
Hostsorted = basejoin(Hostbase, "/videos?sort={0}".format(sortBy))
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

def showSorts():
    addDirectoryItem("Recent", {"name": "Recent", "url": "sort=recent", "mode": 201}, "DefaultFolder.png")
    addDirectoryItem("Rated", {"name": "Rated", "url": "sort=rated", "mode": 201}, "DefaultFolder.png")
    addDirectoryItem("Viewed", {"name": "Viewed", "url": "sort=viewed", "mode": 201}, "DefaultFolder.png")
    addDirectoryItem("Popular", {"name": "Popular", "url": "sort=popular", "mode": 201}, "DefaultFolder.png")
    addDirectoryItem("Relevance", {"name": "Relevance", "url": "sort=editorchoice", "mode": 201}, "DefaultFolder.png")
    addDirectoryItem("Longest", {"name": "Longest", "url": "sort=longest", "mode": 201}, "DefaultFolder.png")
    setView()

def showContent():
    addDirectoryItem("Search", {"name": "Search", "url": HostSearch, "mode": 100}, imgSearch)
    addDirectoryItem("Change {0} Sorting".format(sortBy.title()), {"name": "Change {0} Sorting".format(sortBy.title()), "url": "sort", "mode": 200}, imgFolder)
    addDirectoryItem("Latest", {"name": "Latest", "url": Hostall, "mode": 1}, imgFolder)
    dirsortname = "{0} Videos".format(sortBy.title())
    addDirectoryItem(dirsortname, {"name": dirsortname, "url": Hostsorted, "mode": 1}, "DefaultFolder.png")
    content = getUrl(Host)
    icount = 0
    start = 0
    n0 = content.find('<h2>CATEGORIES</h2>', start)
    if n0 < 0:
        return
    content = content[n0:]
    i1 = 0
    if i1 == 0:
        regexcat = '<a href="(.*?)" title="(.*?)">.*?src="(.*?)"'
        match = re.compile(regexcat, re.DOTALL).findall(content)
        for url, name, pic in match:
            url1 = basejoin(Hostbase, url)
            addDirectoryItem(name, {"name": name, "url": url1, "mode": 1}, pic)
    setView()
    return xutil.getListItemPath()

def getSearchResults(name, url):
    pages = [1, 2, 3, 4, 5, 6]
    allitems = []
    surl = str(url) + "&p={0}"
    if doPaginate:
        getPage(name, url)
    else:
        for page in pages:
            allitems.extend(getPageVids(name, surl.format(page)))
        if len(allitems) > 0:
            for item in allitems:
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=item['url'], listitem=item['listitem'], isFolder=item['isFolder'])
    setView()

def getAllPages(name, url):
    pages = [1, 2, 3, 4, 5, 6]
    allitems = []
    for page in pages:
        allitems.extend(getPageVids(name, url + "/videos?sort={0}&p={1}".format(sortBy, str(page))))
    allitems.sort()
    return allitems

def getPage(name, url):
    pages = [1, 2, 3, 4, 5, 6]
    allitems = getAllPages(name, url)
    if not doPaginate:
        for item in allitems:
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=item['url'], listitem=item['listitem'], isFolder=item['isFolder'])
        setView()
    elif doPaginate:
        getPagedResults(name, url)

def getPagedResults(name, url):
    allok = True
    notok = False
    for page in range(1,10):
        url1 = url + "/videos?sort={0}".format(sortBy)
        url1 = url1 + "&p={0}".format(str(page))
        name = "Page " + str(page)
        pic = "DefaultFolder"
        allok = addPage(name, url1, 2, pic)
        if not allok:
            notok = True
    if notok:
        xbmc.log("Problem adding an item in getPage")
    setView()

def getPageVids(nameofpage, urlofpage):
    content = getUrl(urlofpage)
    regexvideo = ur'thumb_container video.*?href="(.*?)" title="(.*?)">.*?src="(.*?)"'
    match = re.compile(regexvideo, re.DOTALL).findall(content)
    litems = []
    for url, name, pic in match:
        name = name.replace('"', '')
        label = str(name.title())
        url = basejoin(Hostbase, url)
        litems.append(makeItem(label, {"name": name, "url": url, "mode": 3}, pic))
    return litems

def makeItem(name, parameters={}, pic="DefaultFolder.png"):
    li = xbmcgui.ListItem(unescapeString(name), iconImage=pic, thumbnailImage=pic)
    url = sys.argv[0] + '?' + urllib.urlencode(parameters)
    litem = dict(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=True)
    litem.setdefault(litem.keys()[0])
    return litem

def addDirectoryItem(name, parameters={}, pic="DefaultFolder.png"):
    item = makeItem(name, parameters, pic)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=item['url'], listitem=item['listitem'], isFolder=item['isFolder'])

def addPage(itemname, urlpath, runmode, thumb):
    return addDirectoryItem(itemname, {"name": itemname, "url": urlpath, "mode": runmode}, thumb)

def setView(endofdir=True):
    xutil.setSortMethodsForCurrentXBMCList(sortKeys=['name', 'file', 'date', 'size', 'none'])
    if endofdir:
        ok = xbmcplugin.endOfDirectory(thisPlugin)
    xbmc.executebuiltin("Container.SetViewMode({0})".format(viewMode))

def getVideos(name1, urlmain):
    content = getUrl(urlmain)
    regexvideo = 'thumb_container video.*?href="(.*?)" title="(.*?)">.*?src="(.*?)"'
    match = re.compile(regexvideo, re.DOTALL).findall(content)
    for url, name, pic in match:
        name = unescapeString(name.replace('"', ''))
        url = basejoin(Hostbase, url)
        pic = pic
        addDirectoryItem(name, {"name": name, "url": url, "mode": 3}, pic)
    setView()

def playVideo(name, url):
    fpage = getUrl(url)
    start = 0
    pos1 = fpage.find("source src", start)
    if (pos1 < 0):
        return
    pos2 = fpage.find("http", pos1)
    if (pos2 < 0):
        return
    pos3 = fpage.find('"', (pos2 + 5))
    if (pos3 < 0):
        return
    url = fpage[(pos2):(pos3)]
    li = xbmcgui.ListItem(name, iconImage=imgFolder, thumbnailImage=imgFolder)
    player = xbmc.Player()
    player.play(url, li)

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

params = parameters_string_to_dict(sys.argv[2])
name = unescapeString(str(params.get("name", "")))
url = unescapeString(str(params.get("url", "")))
mode = str(params.get("mode", ""))

if not sys.argv[2]:
    ok = showContent()
else:
    if mode == str(1):
        ok = getPage(name, url)
    elif mode == str(2):
        ok = getVideos(name, url)
    elif mode == str(3):
        ok = playVideo(name, url)
    elif mode == str(200):
        ok = showSorts()
    elif mode == str(201):
        sortBy = str(name.lower())
        __addon__.setSetting("sortby", sortBy)
        ok = showContent()
        xbmc.executebuiltin("Notification('Sort Saved', 'Results will be sorted by {0} now')".format(sortBy.title()))
        setView()
    elif mode == str(100):
        if searchQ is not None:
            text = str(searchQ).replace('+', ' ')
        else:
            text = ""
        sname = str("Search {0}".format(Hostbase))
        text = xutil.getKeyboard(text, sname)
        #kb = xbmc.Keyboard(line=text, heading=sname, hidden=False)
        #kb.doModal()
        if (text != "" and text is not None):
            text = text.replace(' ', '+')
            searchQ = text.replace('+', ' ')
            __addon__.setSetting("lastsearch", searchQ)
        surl = basejoin(Hostbase, "/s/{0}/?sort={1}".format(text, sortBy))
        getSearchResults(searchQ, surl)
