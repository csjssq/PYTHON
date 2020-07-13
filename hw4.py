import urllib.request, urllib
from http import cookiejar
from bs4 import BeautifulSoup

cj = http.cookiejar.CookieJar()
opener = urllib.build_opener(urllib.HTTPCookieProcessor(cj))
urllib.install_opener(opener)

postdata_login = urllib.urlencode({
    'id': '',
    'pw': '',
    'submit': 'login'
})
req = urllib.request.Request(url='https://bbs.sjtu.edu.cn/bbslogin', data=postdata_login)
response = urllib.request.urlopen(req)

text = 'hellobbs12345'
postdata = urllib.urlencode({
    'text': text,
    'type': 'update'
})

req = urllib.request.Request(url='https://bbs.sjtu.edu.cn/bbsplan', data=postdata)
response = urllib.request.urlopen(req)

content = urllib.request.urlopen('https://bbs.sjtu.edu.cn/bbsplan').read()
soup = BeautifulSoup(content, features="html.parser")
print (str(soup.find('textarea').string).strip().decode('utf8'))
