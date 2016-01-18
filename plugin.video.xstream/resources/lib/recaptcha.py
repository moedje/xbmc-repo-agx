import urllib,re

def checkForReCaptcha(html):
     #check for recaptcha in the page source, and return true or false.
     if 'recaptcha_challenge_field' in html:
          return True
     else:
          return False


def checkIfSuceeded(html):
     #reverse the boolean to check for success.
     if 'recaptcha_challenge_field' in html:
          return False
     else:
          return True

def getCaptcha(html):
     #get the captcha image url and save the challenge token
     print 'initiating recaptcha passthrough'

     try:
         token = (re.compile('http://www.google.com/recaptcha/api/noscript\?k\=(.+?)"').findall(html))[0]
     except:
         print "couldn't find the challenge token"

     try:
         challengehtml = urllib.urlopen('http://www.google.com/recaptcha/api/challenge?k=' + token)
     except:
         print "couldn't load the challenge url"
         

     try:
         challengeToken = (re.compile("challenge : '(.+?)'").findall(challengehtml.read()))[0]
     except:
         print "couldn't get challenge code"
        
     imageurl = 'http://www.google.com/recaptcha/api/image?c=' + challengeToken

     return (imageurl, challengeToken)


def buildResponse(solved, challengeToken):
    #build the response
     print 'challenge token: '+challengeToken
         
     parameters = urllib.urlencode({'recaptcha_challenge_field': challengeToken, 'recaptcha_response_field': solved})

     return parameters