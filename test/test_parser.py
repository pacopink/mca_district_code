import html

if __name__=='__main__':
    x = '"<adfdfd>"'
    y = html.escape(x)+"&amp;"
    print(y)
    print(html.unescape(y))