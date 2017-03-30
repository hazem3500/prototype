import schedule
import time
from bond import make_bond
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import MySQLdb
import json
import requests
import os
import sys
import datetime
import urllib


db = MySQLdb.connect(host="127.0.0.1", user="root", passwd="", db="tup")

cur = db.cursor()



def imgGenerator(engword,userID,count):

    worden = engword
    langage = "eng"
    a = {'from': langage, 'dest': 'ara', 'format': 'json', 'phrase': worden}
    a = urllib.urlencode(a)
    url = 'https://glosbe.com/gapi/translate?' + a
    page = requests.get(url)
    obj = json.loads(page.content)

    response = requests.get("https://wordsapiv1.p.mashape.com/words/" + worden,
      headers={
        "X-Mashape-Key": "aSH092p7LTmsh691lcammFWNNk19p1Qr71hjsnj9IPHPG75Eaj",
        "Accept": "application/json"
      }
    )

    obj2 = json.loads(response.content)
    wordsar = []
    wordsen = []
    for word in obj['tuc']:
        try:
            wordsar.append(word['phrase']['text'])
        except:
            pass
        #
        # try:
        #     for one in word['meanings']:
        #         wordsen.append(one['text'])
        # except:
        #     pass

    meanings = obj2['results']
    for mean in meanings:
        wordsen.append(mean['definition'])

    pro = obj2['pronunciation']['all']
    bidi_text2 = get_display(pro)
    img = Image.new('RGB', (700, 500), color='#02bdf4')

    draw = ImageDraw.Draw(img)
    # font = ImageFont.truetype(<font-file>, <font-size>)

    font = ImageFont.truetype("Arial.ttf", 30)
    font1 = ImageFont.truetype("Arial.ttf", 14)
    font2 = ImageFont.truetype("Arial.ttf", 24)
    # font = ImageFont.truetype("sans-serif.ttf", 16)
    # draw.text((x, y),"Sample Text",(r,g,b))
    txt = wordsar[0]
    reshaped_text = arabic_reshaper.reshape(txt)
    bidi_text = get_display(reshaped_text)

    draw.text((350, 75), bidi_text, fill='#ffffff', font=font)
    draw.text((210, 75), "=", fill='#d32824', font=font)
    draw.text((25, 75), worden, fill='#ffffff', font=font)
    draw.text((25, 200), "Pronunciation:", fill='#ffffff', font=font2)
    draw.text((190, 200), get_display(pro), fill='#ffffff', font=font2)
    draw.text((25, 250), "definition", fill='#d32824', font=font1)
    q = 300
    for i in range(3):
        qq = wordsen[i].split(" ")
        if qq > 11:
            ww = " ".join(qq[0:11]) + "\n" + " ".join(qq[11:])
            wordsen[i] = ww
        draw.text((25, q + i * 50), str(i + 1) + ". " +
                  wordsen[i], fill='#ffffff', font=font1)

    img.save(str(userID) + "_" + str(count) + '.png')

def generateVideo(userID,count):
    os.system("ffmpeg -f image2 -r 1/5 -start_number 0 -i " + str(userID) + "_" + "%01d.png -vframes " + str(count) + " -vcodec mpeg4 -y " + str(userID) + ".mp4")

def job():
    # print("I'm working...")
    timea = datetime.date.today() - datetime.timedelta(7)
    # print(timea)
    cur.execute("SELECT * FROM words")
    words = cur.fetchall()
    print(str(words))
    no = list()
    while True:
        if len(no) > 0:
            cur.execute(("SELECT * FROM words WHERE userID = {} AND time = %s AND userID NOT IN {}").format(words[0][0], timea, "(" + ",".join(no) + ")"))
        else:
            cur.execute("SELECT * FROM words WHERE userID = %s AND time = %s", (words[0][0], timea))
        if cur.rowcount == 0:
            break

        no.append("'" + str(words[0][0]) + "'")
        words = cur.fetchall()
        count = 0
        for word in words:
            imgGenerator(word[1],word[0],count)
            count+= 1

        time.sleep(15)
        generateVideo(words[0][0],count)


schedule.every().day.at("00:10").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)

job()
