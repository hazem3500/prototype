# # coding=utf-8
# import arabic_reshaper
# from bidi.algorithm import get_display
# from PIL import Image
# from PIL import ImageFont
# from PIL import ImageDraw
#
# img = Image.new('RGB', (700, 500), color='#02bdf4')
#
#
# draw = ImageDraw.Draw(img)
# # font = ImageFont.truetype(<font-file>, <font-size>)
#
# font = ImageFont.truetype("Arial.ttf", 30)
#
# # font = ImageFont.truetype("sans-serif.ttf", 16)
# # draw.text((x, y),"Sample Text",(r,g,b))
# txt = "يعجب"
# reshaped_text = arabic_reshaper.reshape(txt.decode('utf-8'))
# bidi_text = get_display(reshaped_text)
#
# word = "like"
# draw.multiline_text((500, 75),bidi_text,fill='#ffffff', font=font, align="right")
# draw.multiline_text((330, 75),"=",fill='#ffffff', font=font, align="right")
# draw.multiline_text((100, 75),word,fill='#ffffff', font=font, align="right")
#
# img.save('2.png')

import requests
import json

response = requests.get("https://wordsapiv1.p.mashape.com/words/umbrella",
  headers={
    "X-Mashape-Key": "aSH092p7LTmsh691lcammFWNNk19p1Qr71hjsnj9IPHPG75Eaj",
    "Accept": "application/json"
  }
)

obj = json.loads(response.content)
wordsen = []
meanings = obj['results']
for mean in meanings:
    wordsen.append(mean['definition'])

pro = obj['pronunciation']['all']

print("pro : " + pro)

print(str(wordsen))
