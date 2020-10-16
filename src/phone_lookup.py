#!/usr/bin/env python3

import collections
import time
import gzip

PhoneRecord = collections.namedtuple("PhoneRecord", "prefix,phone,province,city,isp,post_code,city_code,area_code")
FILE = "../out/phone-segment.txt.gz"
IspPrefixRecord = collections.namedtuple("IspPrefixRecord", "prefix,isp")

if __name__ == '__main__':
    h = {}
    ih = {}
    t0 = time.time()
    with gzip.open(FILE, 'r') as f:
        c = 0
        for l in f:
            v = l.decode('utf-8').split()
            r = PhoneRecord(*v)
            if r.prefix not in ih:
                ih[r.prefix] = IspPrefixRecord(r.prefix, r.isp)
            h[r.phone] = r
    for v in sorted(ih.values(), key=lambda x:(x.isp,x.prefix)):
        print(v.isp, v.prefix)
    print("--- info loaded %d lines in %f seconds ---" % (len(h), time.time() - t0))


    while True:
        num = input("enter your mobile number (input 'q' to exit): ")
        print(num)
        if num.lower() in ("q", "quit", "exit"):
            print("goodbye~")
            break
        else:
            res = None
            if len(num) >= 7:
                res = h.get(num[0:7])
            if res is None and len(num) >= 3:
                res = ih.get(num[0:3])
            if res is None:
                print(" sorry I cannot find any info about your input.")
            else:
                print(res)
