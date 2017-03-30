# coding=utf-8

import json
import requests
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
# import MySQLdb
import psycopg2
from flask import Flask, flash, redirect, render_template, request, session, url_for
import urllib
from functools import wraps
from tempfile import gettempdir
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
import time
from werkzeug import secure_filename

# import cgi
# import cgitb; cgitb.enable()
import os
import sys
# try: # Windows needs stdio set for binary mode.
#     import msvcrt
#     msvcrt.setmode (0, os.O_BINARY) # stdin  = 0
#     msvcrt.setmode (1, os.O_BINARY) # stdout = 1
# except ImportError:
#     pass


# db = MySQLdb.connect(host="127.0.0.1", user="root", passwd="", db="tup")
db = psycopg2.connect("dbname=d2jp4dc6cpjdl8 user=doqkmykqusfyyk")

cur = db.cursor()


app = Flask(__name__)


# ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


app.config['UPLOAD_FOLDER'] = 'static/uploads/'


def save_uploaded_file(form_field, upload_dir):
    """This saves a file uploaded by an HTML form.
       The form_field is the name of the file input field from the form.
       For example, the following form_field would be "file_1":
           <input name="file_1" type="file">
       The upload_dir is the directory where the file will be written.
       If no file was uploaded or if the field does not exist then
       this does nothing.
    """
    form = cgi.FieldStorage()
    if not form.has_key(form_field):
        return
    fileitem = form[form_field]
    if not fileitem.file:
        return
    fout = file(os.path.join(upload_dir, fileitem.filename), 'wb')
    while 1:
        chunk = fileitem.file.read(100000)
        if not chunk:
            break
        fout.write(chunk)
    fout.close()


def apology(top="", bottom=""):
    """Renders message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=escape(top), bottom=escape(bottom))


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.11/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/', methods=['GET'])
@login_required
def index():

    cur.execute("SELECT * FROM users WHERE id = %s", [session["user_id"]])
    user = cur.fetchone()
    # try:
    worden = request.args['word']
    langage = request.args['lang']
    cur.execute("INSERT INTO words (userID, word, time) VALUES (%s , %s, %s)",
                (session["user_id"], worden, time.time()))
    db.commit()

    a = {'from': langage, 'dest': 'ara', 'format': 'json', 'phrase': worden}
    a = urllib.urlencode(a)
    url = 'https://glosbe.com/gapi/translate?' + a
    page = requests.get(url)
    obj = json.loads(page.content)

    # response = requests.get("https://wordsapiv1.p.mashape.com/words/" + worden,
    #   headers={
    #     "X-Mashape-Key": "aSH092p7LTmsh691lcammFWNNk19p1Qr71hjsnj9IPHPG75Eaj",
    #     "Accept": "application/json"
    #   }
    # )

    # obj2 = json.loads(response.content)
    wordsar = []
    wordsen = []
    for word in obj['tuc']:
        try:
            wordsar.append(word['phrase']['text'])
        except:
            pass

        try:
            for one in word['meanings']:
                wordsen.append(one['text'])
        except:
            pass

    # meanings = obj2['results']
    # for mean in meanings:
    #     wordsen.append(mean['definition'])

    # pro = obj2['pronunciation']['all']
    pro = ""
    # bidi_text2 = get_display(pro)
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

    img.save('00001.png')

    # os.system("ffmpeg -f image2 -r 1/10 -start_number 1 -i %05d.png -vframes 3 -vcodec mpeg4 -y movie.mp4")

    return render_template("answer.html", wordsar=wordsar, wordsen=wordsen, worden=worden, userimg=user[7], languages=languages)

    #
    # except:
    #     wordar = "عربى"
    # return render_template("answer.html", wordar = wordar.decode("utf-8"),
    # worden= "english")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        cur.execute("SELECT * FROM users WHERE username = %s",
                    [request.form.get("username")])
        rows = cur.fetchall()
        # ensure username exists and password is correct
        if cur.rowcount != 1 or not pwd_context.verify(request.form.get("password"), rows[0][2]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0][0]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via
    # redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        elif not request.form.get("confirmation"):
            return apology("must provide confirmation")

        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("Password dosn't match")

        cur.execute("SELECT * FROM users WHERE username = %s",
                    [request.form.get("username")])
        rows = cur.fetchall()

        if cur.rowcount == 0:
            file = request.files['img']
            filename = ""
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            hash = pwd_context.encrypt(request.form.get("password"))
            cur.execute("INSERT INTO users (username, hash, imgLink) VALUES (%s , %s, %s)",
                        (request.form.get("username"), hash, filename))
            db.commit()
            cur.execute("SELECT * FROM users WHERE username = %s",
                        [request.form.get("username")])
            rows = cur.fetchall()
            session["user_id"] = rows[0][0]
            return redirect(url_for("index"))
        else:
            return apology("User Already exist")
    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))


@app.route("/track")
def track():
    time = request.form.get("confirmation")


languages = [{'iso': u'aar', 'name': u'Afar'}, {'iso': u'abk', 'name': u'Abkhazian'}, {'iso': u'ace', 'name': u'Achinese'}, {'iso': u'ach', 'name': u'Acoli'}, {'iso': u'ada', 'name': u'Adangme'}, {'iso': u'ady', 'name': u'Adyghe; Adygei'}, {'iso': u'afa', 'name': u'Afro-Asiatic languages'}, {'iso': u'afh', 'name': u'Afrihili'}, {'iso': u'afr', 'name': u'Afrikaans'}, {'iso': u'ain', 'name': u'Ainu'}, {'iso': u'aka', 'name': u'Akan'}, {'iso': u'akk', 'name': u'Akkadian'}, {'iso': u'alb', 'name': u'Albanian'}, {'iso': u'ale', 'name': u'Aleut'}, {'iso': u'alg', 'name': u'Algonquian languages'}, {'iso': u'alt', 'name': u'Southern Altai'}, {'iso': u'amh', 'name': u'Amharic'}, {'iso': u'ang', 'name': u'English, Old (ca.450-1100)'}, {'iso': u'anp', 'name': u'Angika'}, {'iso': u'apa', 'name': u'Apache languages'}, {'iso': u'ara', 'name': u'Arabic'}, {'iso': u'arc', 'name': u'Official Aramaic (700-300 BCE); Imperial Aramaic (700-300 BCE)'}, {'iso': u'arg', 'name': u'Aragonese'}, {'iso': u'arm', 'name': u'Armenian'}, {'iso': u'arn', 'name': u'Mapudungun; Mapuche'}, {'iso': u'arp', 'name': u'Arapaho'}, {'iso': u'art', 'name': u'Artificial languages'}, {'iso': u'arw', 'name': u'Arawak'}, {'iso': u'asm', 'name': u'Assamese'}, {'iso': u'ast', 'name': u'Asturian; Bable; Leonese; Asturleonese'}, {'iso': u'ath', 'name': u'Athapascan languages'}, {'iso': u'aus', 'name': u'Australian languages'}, {'iso': u'ava', 'name': u'Avaric'}, {'iso': u'ave', 'name': u'Avestan'}, {'iso': u'awa', 'name': u'Awadhi'}, {'iso': u'aym', 'name': u'Aymara'}, {'iso': u'aze', 'name': u'Azerbaijani'}, {'iso': u'bad', 'name': u'Banda languages'}, {'iso': u'bai', 'name': u'Bamileke languages'}, {'iso': u'bak', 'name': u'Bashkir'}, {'iso': u'bal', 'name': u'Baluchi'}, {'iso': u'bam', 'name': u'Bambara'}, {'iso': u'ban', 'name': u'Balinese'}, {'iso': u'baq', 'name': u'Basque'}, {'iso': u'bas', 'name': u'Basa'}, {'iso': u'bat', 'name': u'Baltic languages'}, {'iso': u'bej', 'name': u'Beja; Bedawiyet'}, {'iso': u'bel', 'name': u'Belarusian'}, {'iso': u'bem', 'name': u'Bemba'}, {'iso': u'ben', 'name': u'Bengali'}, {'iso': u'ber', 'name': u'Berber languages'}, {'iso': u'bho', 'name': u'Bhojpuri'}, {'iso': u'bih', 'name': u'Bihari languages'}, {'iso': u'bik', 'name': u'Bikol'}, {'iso': u'bin', 'name': u'Bini; Edo'}, {'iso': u'bis', 'name': u'Bislama'}, {'iso': u'bla', 'name': u'Siksika'}, {'iso': u'bnt', 'name': u'Bantu languages'}, {'iso': u'tib', 'name': u'Tibetan'}, {'iso': u'bos', 'name': u'Bosnian'}, {'iso': u'bra', 'name': u'Braj'}, {'iso': u'bre', 'name': u'Breton'}, {'iso': u'btk', 'name': u'Batak languages'}, {'iso': u'bua', 'name': u'Buriat'}, {'iso': u'bug', 'name': u'Buginese'}, {'iso': u'bul', 'name': u'Bulgarian'}, {'iso': u'bur', 'name': u'Burmese'}, {'iso': u'byn', 'name': u'Blin; Bilin'}, {'iso': u'cad', 'name': u'Caddo'}, {'iso': u'cai', 'name': u'Central American Indian languages'}, {'iso': u'car', 'name': u'Galibi Carib'}, {'iso': u'cat', 'name': u'Catalan; Valencian'}, {'iso': u'cau', 'name': u'Caucasian languages'}, {'iso': u'ceb', 'name': u'Cebuano'}, {'iso': u'cel', 'name': u'Celtic languages'}, {'iso': u'cze', 'name': u'Czech'}, {'iso': u'cha', 'name': u'Chamorro'}, {'iso': u'chb', 'name': u'Chibcha'}, {'iso': u'che', 'name': u'Chechen'}, {'iso': u'chg', 'name': u'Chagatai'}, {'iso': u'chi', 'name': u'Chinese'}, {'iso': u'chk', 'name': u'Chuukese'}, {'iso': u'chm', 'name': u'Mari'}, {'iso': u'chn', 'name': u'Chinook jargon'}, {'iso': u'cho', 'name': u'Choctaw'}, {'iso': u'chp', 'name': u'Chipewyan; Dene Suline'}, {'iso': u'chr', 'name': u'Cherokee'}, {'iso': u'chu', 'name': u'Church Slavic; Old Slavonic; Church Slavonic; Old Bulgarian; Old Church Slavonic'}, {'iso': u'chv', 'name': u'Chuvash'}, {'iso': u'chy', 'name': u'Cheyenne'}, {'iso': u'cmc', 'name': u'Chamic languages'}, {'iso': u'cop', 'name': u'Coptic'}, {'iso': u'cor', 'name': u'Cornish'}, {'iso': u'cos', 'name': u'Corsican'}, {'iso': u'cpe', 'name': u'Creoles and pidgins, English based'}, {'iso': u'cpf', 'name': u'Creoles and pidgins, French-based'}, {'iso': u'cpp', 'name': u'Creoles and pidgins, Portuguese-based'}, {'iso': u'cre', 'name': u'Cree'}, {'iso': u'crh', 'name': u'Crimean Tatar; Crimean Turkish'}, {'iso': u'crp', 'name': u'Creoles and pidgins'}, {'iso': u'csb', 'name': u'Kashubian'}, {'iso': u'cus', 'name': u'Cushitic languages'}, {'iso': u'wel', 'name': u'Welsh'}, {'iso': u'cze', 'name': u'Czech'}, {'iso': u'dak', 'name': u'Dakota'}, {'iso': u'dan', 'name': u'Danish'}, {'iso': u'dar', 'name': u'Dargwa'}, {'iso': u'day', 'name': u'Land Dayak languages'}, {'iso': u'del', 'name': u'Delaware'}, {'iso': u'den', 'name': u'Slave (Athapascan)'}, {'iso': u'ger', 'name': u'German'}, {'iso': u'dgr', 'name': u'Dogrib'}, {'iso': u'din', 'name': u'Dinka'}, {'iso': u'div', 'name': u'Divehi; Dhivehi; Maldivian'}, {'iso': u'doi', 'name': u'Dogri'}, {'iso': u'dra', 'name': u'Dravidian languages'}, {'iso': u'dsb', 'name': u'Lower Sorbian'}, {'iso': u'dua', 'name': u'Duala'}, {'iso': u'dum', 'name': u'Dutch, Middle (ca.1050-1350)'}, {'iso': u'dut', 'name': u'Dutch; Flemish'}, {'iso': u'dyu', 'name': u'Dyula'}, {'iso': u'dzo', 'name': u'Dzongkha'}, {'iso': u'efi', 'name': u'Efik'}, {'iso': u'egy', 'name': u'Egyptian (Ancient)'}, {'iso': u'eka', 'name': u'Ekajuk'}, {'iso': u'gre', 'name': u'Greek, Modern (1453-)'}, {'iso': u'elx', 'name': u'Elamite'}, {'iso': u'eng', 'name': u'English'}, {'iso': u'enm', 'name': u'English, Middle (1100-1500)'}, {'iso': u'epo', 'name': u'Esperanto'}, {'iso': u'est', 'name': u'Estonian'}, {'iso': u'baq', 'name': u'Basque'}, {'iso': u'ewe', 'name': u'Ewe'}, {'iso': u'ewo', 'name': u'Ewondo'}, {'iso': u'fan', 'name': u'Fang'}, {'iso': u'fao', 'name': u'Faroese'}, {'iso': u'per', 'name': u'Persian'}, {'iso': u'fat', 'name': u'Fanti'}, {'iso': u'fij', 'name': u'Fijian'}, {'iso': u'fil', 'name': u'Filipino; Pilipino'}, {'iso': u'fin', 'name': u'Finnish'}, {'iso': u'fiu', 'name': u'Finno-Ugrian languages'}, {'iso': u'fon', 'name': u'Fon'}, {'iso': u'fre', 'name': u'French'}, {'iso': u'fre', 'name': u'French'}, {'iso': u'frm', 'name': u'French, Middle (ca.1400-1600)'}, {'iso': u'fro', 'name': u'French, Old (842-ca.1400)'}, {'iso': u'frr', 'name': u'Northern Frisian'}, {'iso': u'frs', 'name': u'Eastern Frisian'}, {'iso': u'fry', 'name': u'Western Frisian'}, {'iso': u'ful', 'name': u'Fulah'}, {'iso': u'fur', 'name': u'Friulian'}, {'iso': u'gaa', 'name': u'Ga'}, {'iso': u'gay', 'name': u'Gayo'}, {'iso': u'gba', 'name': u'Gbaya'}, {'iso': u'gem', 'name': u'Germanic languages'}, {'iso': u'geo', 'name': u'Georgian'}, {'iso': u'ger', 'name': u'German'}, {'iso': u'gez', 'name': u'Geez'}, {'iso': u'gil', 'name': u'Gilbertese'}, {'iso': u'gla', 'name': u'Gaelic; Scottish Gaelic'}, {'iso': u'gle', 'name': u'Irish'}, {'iso': u'glg', 'name': u'Galician'}, {'iso': u'glv', 'name': u'Manx'}, {'iso': u'gmh', 'name': u'German, Middle High (ca.1050-1500)'}, {'iso': u'goh', 'name': u'German, Old High (ca.750-1050)'}, {'iso': u'gon', 'name': u'Gondi'}, {'iso': u'gor', 'name': u'Gorontalo'}, {'iso': u'got', 'name': u'Gothic'}, {'iso': u'grb', 'name': u'Grebo'}, {'iso': u'grc', 'name': u'Greek, Ancient (to 1453)'}, {'iso': u'gre', 'name': u'Greek, Modern (1453-)'}, {'iso': u'grn', 'name': u'Guarani'}, {'iso': u'gsw', 'name': u'Swiss German; Alemannic; Alsatian'}, {'iso': u'guj', 'name': u'Gujarati'}, {'iso': u'gwi', 'name': u"Gwich'in"}, {'iso': u'hai', 'name': u'Haida'}, {'iso': u'hat', 'name': u'Haitian; Haitian Creole'}, {'iso': u'hau', 'name': u'Hausa'}, {'iso': u'haw', 'name': u'Hawaiian'}, {'iso': u'heb', 'name': u'Hebrew'}, {'iso': u'her', 'name': u'Herero'}, {'iso': u'hil', 'name': u'Hiligaynon'}, {'iso': u'him', 'name': u'Himachali languages; Western Pahari languages'}, {'iso': u'hin', 'name': u'Hindi'}, {'iso': u'hit', 'name': u'Hittite'}, {'iso': u'hmn', 'name': u'Hmong; Mong'}, {'iso': u'hmo', 'name': u'Hiri Motu'}, {'iso': u'hrv', 'name': u'Croatian'}, {'iso': u'hsb', 'name': u'Upper Sorbian'}, {'iso': u'hun', 'name': u'Hungarian'}, {'iso': u'hup', 'name': u'Hupa'}, {'iso': u'arm', 'name': u'Armenian'}, {'iso': u'iba', 'name': u'Iban'}, {'iso': u'ibo', 'name': u'Igbo'}, {'iso': u'ice', 'name': u'Icelandic'}, {'iso': u'ido', 'name': u'Ido'}, {'iso': u'iii', 'name': u'Sichuan Yi; Nuosu'}, {'iso': u'ijo', 'name': u'Ijo languages'}, {'iso': u'iku', 'name': u'Inuktitut'}, {'iso': u'ile', 'name': u'Interlingue; Occidental'}, {'iso': u'ilo', 'name': u'Iloko'}, {'iso': u'ina', 'name': u'Interlingua (International Auxiliary Language Association)'}, {'iso': u'inc', 'name': u'Indic languages'}, {'iso': u'ind', 'name': u'Indonesian'}, {'iso': u'ine', 'name': u'Indo-European languages'}, {'iso': u'inh', 'name': u'Ingush'}, {'iso': u'ipk', 'name': u'Inupiaq'}, {'iso': u'ira', 'name': u'Iranian languages'}, {'iso': u'iro', 'name': u'Iroquoian languages'}, {'iso': u'ice', 'name': u'Icelandic'}, {'iso': u'ita', 'name': u'Italian'}, {'iso': u'jav', 'name': u'Javanese'}, {'iso': u'jbo', 'name': u'Lojban'}, {'iso': u'jpn', 'name': u'Japanese'}, {'iso': u'jpr', 'name': u'Judeo-Persian'}, {'iso': u'jrb', 'name': u'Judeo-Arabic'}, {'iso': u'kaa', 'name': u'Kara-Kalpak'}, {'iso': u'kab', 'name': u'Kabyle'}, {'iso': u'kac', 'name': u'Kachin; Jingpho'}, {'iso': u'kal', 'name': u'Kalaallisut; Greenlandic'}, {'iso': u'kam', 'name': u'Kamba'}, {'iso': u'kan', 'name': u'Kannada'}, {'iso': u'kar', 'name': u'Karen languages'}, {'iso': u'kas', 'name': u'Kashmiri'}, {'iso': u'geo', 'name': u'Georgian'}, {'iso': u'kau', 'name': u'Kanuri'}, {'iso': u'kaw', 'name': u'Kawi'}, {'iso': u'kaz', 'name': u'Kazakh'}, {'iso': u'kbd', 'name': u'Kabardian'}, {'iso': u'kha', 'name': u'Khasi'}, {'iso': u'khi', 'name': u'Khoisan languages'}, {'iso': u'khm', 'name': u'Central Khmer'}, {'iso': u'kho', 'name': u'Khotanese; Sakan'}, {'iso': u'kik', 'name': u'Kikuyu; Gikuyu'}, {'iso': u'kin', 'name': u'Kinyarwanda'}, {'iso': u'kir', 'name': u'Kirghiz; Kyrgyz'}, {'iso': u'kmb', 'name': u'Kimbundu'}, {'iso': u'kok', 'name': u'Konkani'}, {'iso': u'kom', 'name': u'Komi'}, {'iso': u'kon', 'name': u'Kongo'}, {'iso': u'kor', 'name': u'Korean'}, {'iso': u'kos', 'name': u'Kosraean'}, {'iso': u'kpe', 'name': u'Kpelle'}, {'iso': u'krc', 'name': u'Karachay-Balkar'}, {'iso': u'krl', 'name': u'Karelian'}, {'iso': u'kro', 'name': u'Kru languages'}, {'iso': u'kru', 'name': u'Kurukh'}, {'iso': u'kua', 'name': u'Kuanyama; Kwanyama'}, {'iso': u'kum', 'name': u'Kumyk'}, {'iso': u'kur', 'name': u'Kurdish'}, {'iso': u'kut', 'name': u'Kutenai'}, {'iso': u'lad', 'name': u'Ladino'}, {'iso': u'lah', 'name': u'Lahnda'}, {'iso': u'lam', 'name': u'Lamba'}, {'iso': u'lao', 'name': u'Lao'}, {'iso': u'lat', 'name': u'Latin'}, {'iso': u'lav', 'name': u'Latvian'}, {'iso': u'lez', 'name': u'Lezghian'}, {'iso': u'lim', 'name': u'Limburgan; Limburger; Limburgish'}, {'iso': u'lin', 'name': u'Lingala'}, {'iso': u'lit', 'name': u'Lithuanian'}, {'iso': u'lol', 'name': u'Mongo'}, {'iso': u'loz', 'name': u'Lozi'}, {'iso': u'ltz', 'name': u'Luxembourgish; Letzeburgesch'}, {'iso': u'lua', 'name': u'Luba-Lulua'}, {'iso': u'lub', 'name': u'Luba-Katanga'}, {'iso': u'lug', 'name': u'Ganda'}, {'iso': u'lui', 'name': u'Luiseno'}, {'iso': u'lun', 'name': u'Lunda'}, {'iso': u'luo', 'name': u'Luo (Kenya and Tanzania)'}, {'iso': u'lus', 'name': u'Lushai'}, {'iso': u'mac', 'name': u'Macedonian'}, {'iso': u'mad', 'name': u'Madurese'}, {'iso': u'mag', 'name': u'Magahi'}, {'iso': u'mah', 'name': u'Marshallese'}, {'iso': u'mai', 'name': u'Maithili'}, {'iso': u'mak', 'name': u'Makasar'}, {'iso': u'mal', 'name': u'Malayalam'}, {'iso': u'man', 'name': u'Mandingo'}, {'iso': u'mao', 'name': u'Maori'}, {'iso': u'map', 'name': u'Austronesian languages'}, {'iso': u'mar', 'name': u'Marathi'}, {'iso': u'mas', 'name': u'Masai'}, {'iso': u'may', 'name': u'Malay'}, {'iso': u'mdf', 'name': u'Moksha'}, {'iso': u'mdr', 'name': u'Mandar'}, {'iso': u'men', 'name': u'Mende'}, {'iso': u'mga', 'name': u'Irish, Middle (900-1200)'}, {'iso': u'mic', 'name': u"Mi'kmaq; Micmac"}, {'iso': u'min', 'name': u'Minangkabau'}, {'iso': u'mis', 'name': u'Uncoded languages'}, {'iso': u'mac', 'name': u'Macedonian'}, {'iso': u'mkh', 'name': u'Mon-Khmer languages'}, {'iso': u'mlg', 'name': u'Malagasy'}, {'iso': u'mlt', 'name': u'Maltese'}, {'iso': u'mnc', 'name': u'Manchu'}, {'iso': u'mni', 'name': u'Manipuri'}, {'iso': u'mno', 'name': u'Manobo languages'}, {'iso': u'moh', 'name': u'Mohawk'}, {'iso': u'mon', 'name': u'Mongolian'}, {'iso': u'mos', 'name': u'Mossi'}, {'iso': u'mao', 'name': u'Maori'}, {'iso': u'may', 'name': u'Malay'}, {'iso': u'mul', 'name': u'Multiple languages'}, {'iso': u'mun', 'name': u'Munda languages'}, {'iso': u'mus', 'name': u'Creek'}, {'iso': u'mwl', 'name': u'Mirandese'}, {'iso': u'mwr', 'name': u'Marwari'}, {'iso': u'bur', 'name': u'Burmese'}, {'iso': u'myn', 'name': u'Mayan languages'}, {'iso': u'myv', 'name': u'Erzya'}, {'iso': u'nah', 'name': u'Nahuatl languages'}, {'iso': u'nai', 'name': u'North American Indian languages'}, {'iso': u'nap', 'name': u'Neapolitan'}, {'iso': u'nau', 'name': u'Nauru'}, {'iso': u'nav', 'name': u'Navajo; Navaho'}, {'iso': u'nbl', 'name': u'Ndebele, South; South Ndebele'}, {'iso': u'nde', 'name': u'Ndebele, North; North Ndebele'}, {'iso': u'ndo', 'name': u'Ndonga'}, {'iso': u'nds', 'name': u'Low German; Low Saxon; German, Low; Saxon, Low'}, {'iso': u'nep', 'name': u'Nepali'}, {'iso': u'new', 'name': u'Nepal Bhasa; Newari'}, {'iso': u'nia', 'name': u'Nias'}, {'iso': u'nic', 'name': u'Niger-Kordofanian languages'}, {'iso': u'niu', 'name': u'Niuean'}, {'iso': u'dut', 'name': u'Dutch; Flemish'}, {'iso': u'nno', 'name': u'Norwegian Nynorsk; Nynorsk, Norwegian'}, {'iso': u'nob', 'name': u'Bokm\xe5l, Norwegian; Norwegian Bokm\xe5l'}, {'iso': u'nog', 'name': u'Nogai'}, {'iso': u'non', 'name': u'Norse, Old'}, {'iso': u'nor', 'name': u'Norwegian'}, {'iso': u'nqo', 'name': u"N'Ko"}, {'iso': u'nso', 'name': u'Pedi; Sepedi; Northern Sotho'}, {'iso': u'nub', 'name': u'Nubian languages'}, {'iso': u'nwc', 'name': u'Classical Newari; Old Newari; Classical Nepal Bhasa'}, {'iso': u'nya', 'name': u'Chichewa; Chewa; Nyanja'}, {'iso': u'nym', 'name': u'Nyamwezi'}, {'iso': u'nyn', 'name': u'Nyankole'}, {'iso': u'nyo', 'name': u'Nyoro'}, {'iso': u'nzi', 'name': u'Nzima'}, {'iso': u'oci', 'name': u'Occitan (post 1500)'}, {'iso': u'oji', 'name': u'Ojibwa'}, {'iso': u'ori', 'name': u'Oriya'}, {'iso': u'orm', 'name': u'Oromo'}, {'iso': u'osa', 'name': u'Osage'}, {'iso': u'oss', 'name': u'Ossetian; Ossetic'}, {'iso': u'ota', 'name': u'Turkish, Ottoman (1500-1928)'}, {'iso': u'oto', 'name': u'Otomian languages'}, {'iso': u'paa', 'name': u'Papuan languages'}, {'iso': u'pag', 'name': u'Pangasinan'}, {'iso': u'pal', 'name': u'Pahlavi'}, {'iso': u'pam', 'name': u'Pampanga; Kapampangan'}, {'iso': u'pan', 'name': u'Panjabi; Punjabi'}, {'iso': u'pap', 'name': u'Papiamento'}, {'iso': u'pau', 'name': u'Palauan'}, {'iso': u'peo', 'name': u'Persian, Old (ca.600-400 B.C.)'}, {'iso': u'per', 'name': u'Persian'}, {'iso': u'phi', 'name': u'Philippine languages'}, {'iso': u'phn', 'name': u'Phoenician'}, {'iso': u'pli', 'name': u'Pali'}, {'iso': u'pol', 'name': u'Polish'}, {'iso': u'pon', 'name': u'Pohnpeian'}, {'iso': u'por', 'name': u'Portuguese'}, {'iso': u'pra', 'name': u'Prakrit languages'}, {'iso': u'pro', 'name': u'Proven\xe7al, Old (to 1500);Occitan, Old (to 1500)'}, {'iso': u'pus', 'name': u'Pushto; Pashto'}, {'iso': u'qaa', 'name': u'Reserved for local use'}, {'iso': u'que', 'name': u'Quechua'}, {'iso': u'raj', 'name': u'Rajasthani'}, {'iso': u'rap', 'name': u'Rapanui'}, {'iso': u'rar', 'name': u'Rarotongan; Cook Islands Maori'}, {'iso': u'roa', 'name': u'Romance languages'}, {'iso': u'roh', 'name': u'Romansh'}, {'iso': u'rom', 'name': u'Romany'}, {'iso': u'rum', 'name': u'Romanian; Moldavian; Moldovan'}, {'iso': u'rum', 'name': u'Romanian; Moldavian; Moldovan'}, {'iso': u'run', 'name': u'Rundi'}, {'iso': u'rup', 'name': u'Aromanian; Arumanian; Macedo-Romanian'}, {'iso': u'rus', 'name': u'Russian'}, {'iso': u'sad', 'name': u'Sandawe'}, {'iso': u'sag', 'name': u'Sango'}, {'iso': u'sah', 'name': u'Yakut'}, {'iso': u'sai', 'name': u'South American Indian languages'}, {'iso': u'sal', 'name': u'Salishan languages'}, {'iso': u'sam', 'name': u'Samaritan Aramaic'}, {'iso': u'san', 'name': u'Sanskrit'}, {'iso': u'sas', 'name': u'Sasak'}, {'iso': u'sat', 'name': u'Santali'}, {'iso': u'scn', 'name': u'Sicilian'}, {'iso': u'sco', 'name': u'Scots'}, {'iso': u'sel', 'name': u'Selkup'}, {'iso': u'sem', 'name': u'Semitic languages'}, {'iso': u'sga', 'name': u'Irish, Old (to 900)'}, {'iso': u'sgn', 'name': u'Sign Languages'}, {'iso': u'shn', 'name': u'Shan'}, {'iso': u'sid', 'name': u'Sidamo'}, {'iso': u'sin', 'name': u'Sinhala; Sinhalese'}, {'iso': u'sio', 'name': u'Siouan languages'}, {'iso': u'sit', 'name': u'Sino-Tibetan languages'}, {'iso': u'sla', 'name': u'Slavic languages'}, {'iso': u'slo', 'name': u'Slovak'}, {'iso': u'slo', 'name': u'Slovak'}, {'iso': u'slv', 'name': u'Slovenian'}, {'iso': u'sma', 'name': u'Southern Sami'}, {'iso': u'sme', 'name': u'Northern Sami'}, {'iso': u'smi', 'name': u'Sami languages'}, {'iso': u'smj', 'name': u'Lule Sami'}, {'iso': u'smn', 'name': u'Inari Sami'}, {'iso': u'smo', 'name': u'Samoan'}, {'iso': u'sms', 'name': u'Skolt Sami'}, {'iso': u'sna', 'name': u'Shona'}, {'iso': u'snd', 'name': u'Sindhi'}, {'iso': u'snk', 'name': u'Soninke'}, {'iso': u'sog', 'name': u'Sogdian'}, {'iso': u'som', 'name': u'Somali'}, {'iso': u'son', 'name': u'Songhai languages'}, {'iso': u'sot', 'name': u'Sotho, Southern'}, {'iso': u'spa', 'name': u'Spanish; Castilian'}, {'iso': u'alb', 'name': u'Albanian'}, {'iso': u'srd', 'name': u'Sardinian'}, {'iso': u'srn', 'name': u'Sranan Tongo'}, {'iso': u'srp', 'name': u'Serbian'}, {'iso': u'srr', 'name': u'Serer'}, {'iso': u'ssa', 'name': u'Nilo-Saharan languages'}, {'iso': u'ssw', 'name': u'Swati'}, {'iso': u'suk', 'name': u'Sukuma'}, {'iso': u'sun', 'name': u'Sundanese'}, {'iso': u'sus', 'name': u'Susu'}, {'iso': u'sux', 'name': u'Sumerian'}, {'iso': u'swa', 'name': u'Swahili'}, {'iso': u'swe', 'name': u'Swedish'}, {'iso': u'syc', 'name': u'Classical Syriac'}, {'iso': u'syr', 'name': u'Syriac'}, {'iso': u'tah', 'name': u'Tahitian'}, {'iso': u'tai', 'name': u'Tai languages'}, {'iso': u'tam', 'name': u'Tamil'}, {'iso': u'tat', 'name': u'Tatar'}, {'iso': u'tel', 'name': u'Telugu'}, {'iso': u'tem', 'name': u'Timne'}, {'iso': u'ter', 'name': u'Tereno'}, {'iso': u'tet', 'name': u'Tetum'}, {'iso': u'tgk', 'name': u'Tajik'}, {'iso': u'tgl', 'name': u'Tagalog'}, {'iso': u'tha', 'name': u'Thai'}, {'iso': u'tib', 'name': u'Tibetan'}, {'iso': u'tig', 'name': u'Tigre'}, {'iso': u'tir', 'name': u'Tigrinya'}, {'iso': u'tiv', 'name': u'Tiv'}, {'iso': u'tkl', 'name': u'Tokelau'}, {'iso': u'tlh', 'name': u'Klingon; tlhIngan-Hol'}, {'iso': u'tli', 'name': u'Tlingit'}, {'iso': u'tmh', 'name': u'Tamashek'}, {'iso': u'tog', 'name': u'Tonga (Nyasa)'}, {'iso': u'ton', 'name': u'Tonga (Tonga Islands)'}, {'iso': u'tpi', 'name': u'Tok Pisin'}, {'iso': u'tsi', 'name': u'Tsimshian'}, {'iso': u'tsn', 'name': u'Tswana'}, {'iso': u'tso', 'name': u'Tsonga'}, {'iso': u'tuk', 'name': u'Turkmen'}, {'iso': u'tum', 'name': u'Tumbuka'}, {'iso': u'tup', 'name': u'Tupi languages'}, {'iso': u'tur', 'name': u'Turkish'}, {'iso': u'tut', 'name': u'Altaic languages'}, {'iso': u'tvl', 'name': u'Tuvalu'}, {'iso': u'twi', 'name': u'Twi'}, {'iso': u'tyv', 'name': u'Tuvinian'}, {'iso': u'udm', 'name': u'Udmurt'}, {'iso': u'uga', 'name': u'Ugaritic'}, {'iso': u'uig', 'name': u'Uighur; Uyghur'}, {'iso': u'ukr', 'name': u'Ukrainian'}, {'iso': u'umb', 'name': u'Umbundu'}, {'iso': u'und', 'name': u'Undetermined'}, {'iso': u'urd', 'name': u'Urdu'}, {'iso': u'uzb', 'name': u'Uzbek'}, {'iso': u'vai', 'name': u'Vai'}, {'iso': u'ven', 'name': u'Venda'}, {'iso': u'vie', 'name': u'Vietnamese'}, {'iso': u'vol', 'name': u'Volap\xfck'}, {'iso': u'vot', 'name': u'Votic'}, {'iso': u'wak', 'name': u'Wakashan languages'}, {'iso': u'wal', 'name': u'Wolaitta; Wolaytta'}, {'iso': u'war', 'name': u'Waray'}, {'iso': u'was', 'name': u'Washo'}, {'iso': u'wel', 'name': u'Welsh'}, {'iso': u'wen', 'name': u'Sorbian languages'}, {'iso': u'wln', 'name': u'Walloon'}, {'iso': u'wol', 'name': u'Wolof'}, {'iso': u'xal', 'name': u'Kalmyk; Oirat'}, {'iso': u'xho', 'name': u'Xhosa'}, {'iso': u'yao', 'name': u'Yao'}, {'iso': u'yap', 'name': u'Yapese'}, {'iso': u'yid', 'name': u'Yiddish'}, {'iso': u'yor', 'name': u'Yoruba'}, {'iso': u'ypk', 'name': u'Yupik languages'}, {'iso': u'zap', 'name': u'Zapotec'}, {'iso': u'zbl', 'name': u'Blissymbols; Blissymbolics; Bliss'}, {'iso': u'zen', 'name': u'Zenaga'}, {'iso': u'zgh', 'name': u'Standard Moroccan Tamazight'}, {'iso': u'zha', 'name': u'Zhuang; Chuang'}, {'iso': u'chi', 'name': u'Chinese'}, {'iso': u'znd', 'name': u'Zande languages'}, {'iso': u'zul', 'name': u'Zulu'}, {'iso': u'zun', 'name': u'Zuni'}, {'iso': u'zxx', 'name': u'No linguistic content; Not applicable'}, {'iso': u'zza', 'name': u'Zaza; Dimili; Dimli; Kirdki; Kirmanjki; Zazaki'}]


if __name__ == '__main__':
    app.run(debug=True)
