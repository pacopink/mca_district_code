import urllib.request as request
import re
from bs4 import BeautifulSoup

LINK='http://www.mca.gov.cn//article/sj/xzqh/2020/2020/2020092500801.html'
LINK='http://www.mca.gov.cn/article/sj/xzqh/1980/201507/20150715854852.shtml'
LINK='http://www.mca.gov.cn//article/sj/xzqh/2020/202006/202008310601.shtml'
FILE = '../src/sample.html'



def update_code_map(h, link):
    data = request.urlopen(link, timeout=5).read()
    soup = BeautifulSoup(data.decode('utf8'), 'html.parser')

    r = re.compile(r"\d{6}")
    code = None
    count = 0
    for td in soup.find_all("td"):
        for s in td.strings:
            if s is not None:
                s=s.strip()
                if len(s) == 0:
                    continue

                if code is None and r.match(s) is not None:
                    code = s
                elif code is not None:
                    name = s
                    if code[-4:] == '0000':
                        # 省级
                        h[code[0:2]] = name
                    elif code[-2:] == '00':
                        # 市级
                        h[code[0:4]] = name
                    else:
                        # 区县
                        h[code] = name
                    count+=1
                    code = None
    return count

if __name__=='__main__':
    h = {}
    count = update_code_map(h, LINK)
    print(h, count)
