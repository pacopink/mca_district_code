from data_struct import DistrictCodeDate, IdInfo

def cksum(code):
    pass

def parse_id(code):
    pass


FILE = '../out/area_code.csv'


def area_code_map(filename):
    import re
    r = re.compile('\s*(\d{6})\s+(\w+)')
    h = {}
    with open(filename, 'r', encoding='utf8') as f:
        for l in f:
            m = r.match(l)
            if m is not None:
                code, name = m.groups()
                if code[-4:] == '0000':
                    # 省级
                    h[code[0:2]] = name
                elif code[-2:] == '00':
                    # 市级
                    h[code[0:4]] = name
                else:
                    # 区县
                    h[code] = name
    def _area_code_lookup(code):
        l = len(code)
        return h.get(code[0:2]) if l>=2 else None, h.get(code[0:4]) if l>4 else None, h.get(code[0:6]) if l>6 else None
    return _area_code_lookup


area_code_lookup = area_code_map(FILE)


if __name__=='__main__':
    print(area_code_lookup('440583198106174516'))
    print(area_code_lookup('441202198008200529'))
