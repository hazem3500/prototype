import requests
from lxml import etree, html
import time
import MySQLdb
import urllib2
import urllib
import json


page = requests.get("https://www.loc.gov/standards/iso639-2/php/code_list.php")
tree = etree.HTML(page.content)

results = [a for a in tree.find('.//tr[@valign="top"]').getparent()]
results2 = []
for s in results[1:]:
    results2.append({
        "name": etree.tostring(s.find('.//td').getnext().getnext(), method="text", encoding="UTF-8").strip().decode("utf-8"),
        "iso": (etree.tostring(s.find('.//td'), method="text", encoding="UTF-8").strip().decode("utf-8"))[0:3]
    })

# for result in results2:
#     print(str(result['name'] + "     " + result['iso']))
print( str(results2))
