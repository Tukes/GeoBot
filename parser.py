In = open('unparsed.txt', 'r')
Out = open('parsed.txt', 'w')
In_txt = In.readlines()
for s in In_txt:
    a = s.find("<coordinates>") + len("<coordinates>")
    b = s.find("</coordinates>")
    if (a!=-1) and (b!=-1):
        us = s[a:b:1]
        print(us, file = Out)
In.close()
Out.close()
