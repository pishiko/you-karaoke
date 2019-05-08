import xml.etree.ElementTree as ET
import datetime
import html
import re

def encode_srt(params,n,add_time,max_char):
    param = params.attrib
    dt = datetime.datetime(2000,1,1,0,0,0)
    stime = float(param['start']) - add_time
    start = dt + datetime.timedelta(seconds=stime if stime>0 else 0)
    end = dt + datetime.timedelta(seconds=float(param['dur'])+float(param['start']))

    stext = start.strftime('%H:%M:%S,')+str(start.microsecond).zfill(6)[0:3]
    etext = end.strftime('%H:%M:%S,')+str(end.microsecond).zfill(6)[0:3]

    content = params.text
    content = html.unescape(content)
    p = re.compile(r"<[^>]*?>")
    content = p.sub("", content)

    if max_char>0:
        con = content.split('\n')
        for c in con:
            if len(c) > max_char:
                content = content.replace(c,c[:int(len(c)/2)]+'\n'+c[int(len(c)/2):])

    t = str(n)+'\n'+\
        stext+' --> '+etext+'\n'+\
        content+'\n\n'
    return t,n+1

def xml2srt(xml,file,add_time,max_char):
    root = ET.fromstring(xml)
    text=""
    n=1
    for t in root.findall('text'):
        t,n = encode_srt(t,n,add_time=add_time,max_char=max_char)
        text += t

    with open(file,'w',encoding='utf_8') as f:
        f.write(text)
    return

if __name__ == "__main__":
    with open('sub.xml','r',encoding='utf_8') as f:
        xml = f.read()
    xml2srt(xml,"test.srt")
