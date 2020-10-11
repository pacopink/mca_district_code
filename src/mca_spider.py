#!/usr/bin/env python3
# 从民政部网站爬取全国6位行政区划代码，输出到out/district_code.csv
# 仅供参考，不对信息的准确性和完整性负任何责任
import urllib.request
from bs4 import BeautifulSoup
import re
from data_struct import *
import concurrent.futures

# 控制并发度，不建议太高可能会被网站封IP
WORKERS = 2

# 民政部网站主页
PREFIX = 'http://www.mca.gov.cn'
# 民政部各个时期的地区码列表
LINKS = ['http://www.mca.gov.cn/article/sj/xzqh/1980/',
         'http://www.mca.gov.cn/article/sj/xzqh/1980/?2',
         'http://www.mca.gov.cn/article/sj/xzqh/1980/?3',
         'http://www.mca.gov.cn/article/sj/xzqh/2020/',
         'http://www.mca.gov.cn/article/sj/xzqh/2020/?2',
         ]
# 地区码链接的名称pattern, 存在两种形式
r = re.compile(r'(20\d{2})年(\d{1,2})月.*行政区划代码')
r2 = re.compile(r'\d{4}年.*行政区划代码.*截止([12]\d{3})年(\d{1,2})月.*')


def get_link(self):
    """预期传入一个CodeLink，有link字段就返回link，否则返回href"""
    return self.link if self.link is not None else self.href


# monkey patch on CodeLink to get a valid link
CodeLink.get_link = get_link


def get_real_link(link):
    """CodeLink的href很可能是个shtml页面，需要通过解析它获得真实的地址代码列表页面地址"""
    data = urllib.request.urlopen(link, timeout=5).read()
    soup = BeautifulSoup(data.decode('utf8'), 'html.parser')

    # try this way
    r = re.compile(r'.*window.location.href="(http://.*\.html.*)".*', re.S)
    for i in soup.find_all('script'):
        if i.string is None:
            continue
        m = r.match(i.string)
        if m is not None:
            return m.groups()[0]

    # if not returned in previous way, try another way
    for i in soup.find_all('a'):
        if i.string is None:
            continue
        m = r2.match(i.string)
        if m is not None and 'href' in i.attrs:
            return i.attrs['href']


def get_code_link(link):
    print(link)
    data = urllib.request.urlopen(link, timeout=10).read()
    soup = BeautifulSoup(data.decode('utf8'), 'html.parser')
    l = []
    for i in soup.find_all("a"):
        if 'title' in i.attrs and 'href' in i.attrs:
            title = i.attrs['title']
            m = r.match(title)
            if m is None:
                m = r2.match(title)

            if m is not None:
                y, mm = [int(i) for i in m.groups()]
                month = "%04d%02d" % (y, mm)
                href = PREFIX + i.attrs['href']
                # 分析href，获得实际的地区码地址的link
                link = get_real_link(href)
                l.append(CodeLink(month, href, link, title))
    return l


def get_code_links(*args):
    """从传入的多个地区码列表页读取到每个时期的地区码链接列表"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        from itertools import chain
        # 返回含多个列表的列表，通过*展开后由chain做flatten
        return list(chain(*executor.map(get_code_link, list(args))))


def generate_code_map(h, link):
    '''请求地区码页面到字典'''
    data = urllib.request.urlopen(link, timeout=30).read()
    soup = BeautifulSoup(data.decode('utf8'), 'html.parser')

    r = re.compile(r"\d{6}")
    code = None
    province = '-'
    city = '-'
    district = '-'
    count = 0
    for td in soup.find_all("td"):
        for s in td.strings:
            if s is not None:
                s = s.strip()
                if len(s) == 0:
                    continue

                if code is None and r.match(s) is not None:
                    code = s
                elif code is not None:
                    name = s
                    dist = None
                    if code[-4:] == '0000':
                        # 省级
                        province = name
                        # 可能是直辖市
                        city = '-' if '市' != province[-1] else province
                        district = '-'
                        dist = DistrictCode(code=code, province=province, city=city, district=district)
                    elif code[-2:] == '00':
                        # 市级
                        city = name
                        district = '-'
                        dist = DistrictCode(code=code, province=province, city=city, district=district)
                    else:
                        # 区县
                        district = name
                        dist = DistrictCode(code=code, province=province, city=city, district=district)
                    h[dist.code] = dist
                    count += 1
                    code = None
    return count


def code_link_to_map(l):
    """CodeLink to (month, map{code->DistrictInfo}"""
    print("processing:", l)
    link = l.get_link()
    if link is not None:
        h = {}
        generate_code_map(h, link)
        return l.month, h
    else:
        print("cannot find valid link")
        return None


if __name__ == '__main__':
    result = get_code_links(*LINKS)
    # 按时间倒序，最新一个被第一个处理
    result.sort(key=lambda x: x.month, reverse=True)
    # 按顺序，每个CodeLink获取到对应的list(month, map{code->DistrictInfo})列表，列表元素是month和code字典的2元组
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        historical_list = list(filter(None, executor.map(code_link_to_map, result)))

    # 倒序扫描每个时期的地区码结果字典，更新时间点
    INFINITE_YYYYMM = '999999'
    final_dict = {}
    last_month = '-'
    first = True
    for month, h in historical_list:
        for k, v in h.items():
            if k in final_dict:
                # 遇到出现过的区域，把区域产生的时间往前推
                vv = final_dict[k]
                final_dict[k] = DistrictCodeDate(vv.code, vv.province, vv.city, vv.district, month, vv.out_date)
            else:
                # 遇到没出现过的区域，如果这个map不是扫描的第一个(first is False)说明这个区域在那个时间段被撤销了，
                # in_date暂时设置为那个月份
                # out_date如果first is True，设置为9999999，否则，是当前month之后被取消的地区码
                final_dict[k] = DistrictCodeDate(v.code, v.province, v.city, v.district, month,
                                                 INFINITE_YYYYMM if first else month)
        first = False
        last_month = month

    with open(DISTRICT_CODE_FILE, "wb") as f:
        for key in sorted(final_dict.keys()):
            # print(final_dict[key])
            f.write((",".join(final_dict[key]) + "\n").encode("utf8"))
