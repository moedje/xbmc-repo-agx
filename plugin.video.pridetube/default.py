# The documentation written by Voinage was used as a template for this addon
# http://wiki.xbmc.org/?title=HOW-TO_write_plugins_for_XBMC
#
# This addon is licensed with the GNU Public License, and can freely be modified
# http://www.gnu.org/licenses/gpl-2.0.html

import urllib,urllib2,re,xbmcplugin,xbmcgui
from xbmcaddon import Addon
from BeautifulSoup import MinimalSoup as BeautifulSoup

def MAIN():
        addDir('Categories',base_url,3,'DefaultFolder.png')
        INDEX(base_url + getOptions())

def CATEGORIES():
        req = urllib2.Request(categories_url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()

        match=re.compile('<a class=\'box\' href=\'([-A-Za-z0-9/]*)\'>\n<img alt="([-A-Za-z0-9\'&!/ ]*)".*src="([A-Za-z0-9_.:/&=;?]*)"').findall(link)
        print match
        for url,name,thumbnail in match:
                addDir(name,base_url + url + getOptions(),1,thumbnail)

def INDEX(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
		
        match=re.compile('<img alt="([A-Za-z0-9\'!()?;:,._&# -]*)".*src="([A-Za-z0-9_.:/&=;?]*)"(?:.*\n){1,5}.*<a href="(/video/[a-zA-Z0-9-]*)">').findall(link)
        for name,thumbnail,url in match:
                addDownLink(name,base_url + url,2,thumbnail)

        match2=re.search('<a rel="next" href="(?P<url>[-A-Za-z0-9.?&/_:;+=]*)">(?P<pageno>[0-9]{0,2})</a>', link)
        if match2 is not None:
                addDir('Go to next page (' + match2.group('pageno') + ')',base_url + match2.group('url'),1,'DefaultFolder.png')

def VIDEOLINKS(url,name,thumb):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        match=re.compile('<div class=\'(?:video|videohd)\'>\n<a href="([A-Za-z0-9_/.:-?&=]*)"').findall(link)
        name=BeautifulSoup(urllib.unquote_plus(name), convertEntities=BeautifulSoup.HTML_ENTITIES).contents[0]
        for url in match:
                listitem = xbmcgui.ListItem(name)
                listitem.setInfo('video', {'Title': name, 'Genre': 'Porn'})
                listitem.setThumbnailImage(urllib.unquote_plus(thumb))
               	xbmc.Player().play(url, listitem)
        

                
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




def addDownLink(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&thumb="+urllib.quote_plus(iconimage)
        ok=True
	name=BeautifulSoup(name, convertEntities=BeautifulSoup.HTML_ENTITIES).contents[0]
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok


def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&thumb="+urllib.quote_plus(iconimage)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
        
def getOptions():
        if hd == "true" and full_scene == "true":
                return '/?hd=true&full_scene=true'
        elif hd == "true" and full_scene == "false":
                return '/?hd=true'
        elif hd == "false" and full_scene == "true":
                return '/?full_scene=true'
        else:
                return ''


# xbmc hooks
__settings__ = Addon( id="plugin.video.pridetube" )
__language__ = __settings__.getLocalizedString

params=get_params()
url=None
name=None
thumb=None
mode=None
hd=__settings__.getSetting( "hd" )
full_scene=__settings__.getSetting( "full_scene" )


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
        mode=int(params["mode"])
except:
        pass

base_url='http://pridetube.com'
categories_url=base_url + '/videos/categories'
search_url=base_url + '/videos/search?query='

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)


if mode==None or url==None or len(url)<1:
        print base_url + getOptions()
        MAIN()
       
elif mode==1:
        print ""+url
        INDEX(url)
        
elif mode==2:
        print ""+url
        VIDEOLINKS(url,name,thumb)

elif mode==3:
        print categories_url 
        CATEGORIES()

xbmcplugin.endOfDirectory(int(sys.argv[1]))
