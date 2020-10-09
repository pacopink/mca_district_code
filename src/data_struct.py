import collections

# 一个身份证号解析后出来的结果
IdInfo = collections.namedtuple('IdInfo',
                                ['name', 'code', 'validity', 'gender',
                                 'district_code', 'district_info', 'birthday'])


# 最终目标是要获得这样的具名元组, 含历史的（out_date字段表示在什么YYYYMM取消的code, 这些code某些身份证号还在用，所以需要
DistrictCode = collections.namedtuple('DistrictCode', ('code', 'province', 'city', 'district'))
DistrictCodeDate = collections.namedtuple('DistrictCode',
                                          ('code', 'province', 'city', 'district', 'in_date', 'out_date'))

# 中间过程，需要获取各个时期按月更新的
CodeLink = collections.namedtuple('CodeLink', ('month', 'href', 'link', 'title'))

#
DISTRICT_CODE_FILE="../out/district_code.csv"