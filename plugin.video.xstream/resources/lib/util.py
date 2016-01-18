import re
import urllib
import htmlentitydefs

class cUtil:

    def removeHtmlTags(self, sValue, sReplace = ''):
        p = re.compile(r'<.*?>')
        return p.sub(sReplace, sValue)


    def formatTime(self, iSeconds):
        iSeconds = int(iSeconds)

        iMinutes = int(iSeconds / 60)
        iSeconds = iSeconds - (iMinutes * 60)
        if (iSeconds < 10):
            iSeconds = '0' + str(iSeconds)

        if (iMinutes < 10):
            iMinutes = '0' + str(iMinutes)

        return str(iMinutes) + ':' + str(iSeconds)

    def urlDecode(self, sUrl):
        return urllib.unquote(sUrl)

    def urlEncode(self, sUrl):
        return urllib.quote(sUrl)

    def unquotePlus(self, sUrl):
        return urllib.unquote_plus(sUrl)

    def quotePlus(self, sUrl):
        return urllib.quote_plus(sUrl)
        
    # Removes HTML character references and entities from a text string.
    def unescape(self, sText):
        def fixup(m):
            sText = m.group(0)
            if sText[:2] == "&#":
                # character reference
                try:
                    if sText[:3] == "&#x":
                        return unichr(int(sText[3:-1], 16))
                    else:
                        return unichr(int(sText[2:-1]))
                except ValueError:
                    pass
            else:
                # named entity
                try:
                    sText = unichr(htmlentitydefs.name2codepoint[sText[1:-1]])
                except KeyError:
                    pass
            return sText # leave as is
        return re.sub("&#?\w+;", fixup, sText)
