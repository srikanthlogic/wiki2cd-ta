# -*- coding: utf-8 -*-

import codecs
import urllib
import urllib2
import os,sys
from sgmllib import SGMLParser
from pyquery import PyQuery as pq

def cleanup(page):
    """
    remove unwanted sections of the page.
    Uses pyquery.
    """
    document = pq(page)
    #If you want to remove any section, just add the class or id of the section below with comma seperated
    unwanted_sections_list="""
    .editsection,#mw-panel,script,#mw-head,.infobox,#toc,#jump-to-nav,.reference,
    .navbox,#footer,#catlinks,mw-js-message,.magnify,#mainartcle"""
    unwanted_divs = unwanted_sections_list.split(",")
    for section in unwanted_divs:
        document.remove(section.strip())
    return document.wrap('<div></div>').html().encode("utf-8")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        inp = codecs.open(filename, encoding="utf-8", mode="r")
        outp = codecs.open("result.html", encoding="utf-8", mode="w+")
        page = inp.read()
        result = cleanup(page)
        outp.write(result.decode('utf-8'))
        outp.close()
        inp.close()

    else:
        print("Error: Missing arguments. Eg usage: python cleanup.py source.html")

