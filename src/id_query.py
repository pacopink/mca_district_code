#!/usr/bin/env python3
import re
from data_struct import DistrictCodeDate, IdInfo, DISTRICT_CODE_FILE

genders = ('女', '男')
r = re.compile(r'\d{17}[0-9X]')
factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
expects = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']


def get_code_map():
    h = {}
    with open(DISTRICT_CODE_FILE, "r", encoding='utf8') as f:
        for l in f:
            if l[0] == "#":
                continue
            l = l.strip()
            v = l.split(",")
            if len(v) != len(DistrictCodeDate._fields):
                continue
            dist = DistrictCodeDate(*v)
            h[dist.code] = dist
    return h


def _district_lookup():
    """this is a closure, keep a code_map as h in its context to reuse"""
    h = get_code_map()
    return lambda c: h.get(c[0:6])


# refer to the closure
district_lookup = _district_lookup()


def get_gender(code):
    return genders[int(code[16:17]) % 2]


def checksum(code):
    """根据factors和expects计算输入的身份证号前17位校验和"""
    index = sum([factor * int(digit) for factor, digit in zip(factors, code)]) % len(expects)
    return expects[index]


def id_validation_check(code):
    m = r.match(code)
    if m is None:
        print("invalid code pattern")
        return False

    expected_cksum = checksum(code)
    # 和实际的第18位比对校验和
    if code[17] == expected_cksum:
        return True
    else:
        print("checksum failed: expect=", expected_cksum, "but actual:", code[17])
        return False


def parse_id(code, name='NA'):
    if not id_validation_check(code):
        return None
    dist = district_lookup(code)
    gender = get_gender(code)
    return IdInfo(name=name, code=code, validity=True, gender=gender, district_info=dist, birthday=code[6:14])


if __name__ == '__main__':
    while True:
        code = input("请输入要查询的身份证号码: ")
        code = code.upper()
        if code.lower() in ("quit", "exit", "q"):
            print("good bye")
            break
        info = parse_id(code)
        if info is None:
            print("非法的身份证号码,无法查询!")
        else:
            print("查询成功！结果:\n", info)