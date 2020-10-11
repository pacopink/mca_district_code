import id_query

if __name__=='__main__':
    h = id_query.get_code_map()
    l = list(h.values())
    l.sort(key=lambda x:(x.province, x.city, x.district[0:-1], x.in_date))
    with open("../out/distct_code1.csv", "wb") as f1:
        with open("../out/distct_code2.csv", "wb") as f2:
            for ll in l:
                if ll.out_date == '999999':
                    f1.write((",".join(ll)+"\n").encode("utf-8"))
                else:
                    f2.write((",".join(ll)+"\n").encode("utf-8"))

