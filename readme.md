## mca_spider.py
用于从民政部网站爬取所有的6位行政区划码保存到文件out/district_code.csv
注意由于爬取对象的网页可能改版，当你看到这个项目的时候，可能已经发生变化了，
test下面有些用于测试分析的小脚本，可能有帮助。

作为示例，已经爬取了一个out/district_code.csv文件在本repo
## id_query.py
演示了对18位身份证号码的校验和信息提取，前6位位置码依赖于前面爬取的数据

## data_struct.py
一些基本的数据结构和常量的定义