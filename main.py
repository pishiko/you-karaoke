import youtube_dl
import requests
import xml.etree.ElementTree as ET
import util
import subprocess
import re
import os

SUB_LANG_URL = "http://video.google.com/timedtext?type=list&v="
SUB_URL = "http://video.google.com/timedtext?hl={}&lang={}&name={}&v={}"

def getyou(url):
    params = {
        'outtmpl': 'temp/tmp_%(id)s.%(ext)s'
    }
    ydl = youtube_dl.YoutubeDL(params)

    try:
        m= ydl.extract_info(url)
    except:
        print("失敗しました")
        return None
    else:
        print("ダウンロード成功:{}".format(m['title']))
        return m

def get_sub(info,add_time=1.5,max_char=18):
    if info is None:
        return None
    txt = requests.get(SUB_LANG_URL+info["id"]).text
    root = ET.fromstring(txt)
    c = None
    for child in root:
        if child.attrib["lang_code"] == "ja":
            c = child.attrib
    if c is None:
        print("日本語の字幕が見つかりませんでした。")
        return None

    sub = requests.get(SUB_URL.format(c["lang_code"],c["lang_code"],c["name"],info["id"])).text
    name = "temp/sub_{}.srt".format(info['id'])
    util.xml2srt(sub,name,add_time=add_time,max_char=max_char)
    return name

def call_ffmpeg(info, srt, output,font="",del_flag=False):
    if srt is None:
        return False

    p = '^tmp_'+info['id']+'\.[a-zA-Z0-9]{1,}$'
    for f in os.listdir('temp/'):
        m = re.match(p,f)
        if not m is None:
            vname = f
            break
    else:
        print("動画ファイルが見つかりません")
        return None

    output = re.sub(r'[\\|/|:|?|.|"|<|>|\|]', '-', output)

    try:
        subprocess.call("ffmpeg -y -i "+srt+" temp/sub.ass")
        subprocess.call('ffmpeg -y -i temp/' + vname +' -filter:v "subtitles=temp/sub.ass:\'force_style='+font+'Fontsize=32,OutlineColour=&H00000000,Outline=3,MarginV=30\'" -f mp4 "'+ output+'.mp4"')
    except:
        print("失敗しました。ffmpegエラー")
        return False
    print("出力完了。処理時間が短い場合はエラーの可能性があります")
    if not del_flag:
        try:
            os.remove("temp/"+vname)
        except:
            print("動画ファイル消去失敗")
        try:
            os.remove(srt)
        except:
            print("字幕.srt 消去失敗")
        try:
            os.remove("temp/sub.ass")
        except:
            print("sub.ass 消去失敗")
    return True

def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    if sys.stdin.isatty():
        parser.add_argument("url",help="YoutubeのURLを指定",type=str)
    parser.add_argument("--font",help="フォントの名前を指定",type=str,default=None)
    parser.add_argument("--temp",help="一時保存ファイルを残すかどうか",action="store_true",default=False)
    parser.add_argument("--name",help="拡張子を除いた出力ファイルの名前を指定",type=str,default=None)
    parser.add_argument("--delay",help="どれくらい早めに文字を表示するか指定(秒)",type=float,default=1.5)
    parser.add_argument("--maxlen",help="指定文字以上を真ん中で改行する。0で無効",type=int,default=0)
    parser.add_argument("--sub", help="字幕ファイルを編集", type=str)

    args = parser.parse_args()

    if hasattr(args,'url'):
        url = args.url
    else:
        url = sys.stdin

    if args.font is None:
        font = ""
    else:
        font = "FontName={},".format(args.font)


    info = getyou(url)

    if not args.sub is None:
        srt = args.sub
    else:
        srt = get_sub(info,add_time=args.delay,max_char=args.maxlen)
        print("srtへエンコード完了")

    if args.name is None:
        name = "【カラオケ】"+info['title']
    else:
        name = args.name


    call_ffmpeg(info,srt,name,font=font,del_flag=args.temp)

if __name__ == "__main__":
    main()

    # font = "FontName=HGP明朝E,"
    # font = "FontName=MSP明朝,"

