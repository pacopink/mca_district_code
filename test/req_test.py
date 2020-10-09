import urllib.request
from bs4 import BeautifulSoup
import re

LINK='http://www.mca.gov.cn/article/sj/xzqh/2020/202008/20200800029235.shtml'


def get_real_link(link):
    '''there is shtml contains the real html link, try to parse and extract it'''
    data = urllib.request.urlopen(link, timeout=5).read()
    soup = BeautifulSoup(data.decode('utf8'), 'html.parser')
    with open("../src/t.html", "wb") as f:
        f.write(soup.prettify().encode('utf8'))


if __name__=='__main__':
    print(get_real_link(LINK))