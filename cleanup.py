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
    #If you want to remove any other section, just add the class or id of the section below with comma seperated
    unwanted_sections_list="""
    div#jump-to-nav, div.top, div#column-one, div#siteNotice, div#purl, div#head,div#footer, div#head-base, div#page-base, div#stub, div#noprint,
    div#disambig,div.NavFrame,#colophon,.editsection,.toctoggle,.tochidden,.catlinks,.navbox,.sisterproject,.ambox,div#mw-panel,#mw-head,
    .toccolours,.topicondiv#f-poweredbyico,div#f-copyrightico,div#featured-star,li#f-viewcount,.infobox,#toc,div#p-views,
    li#f-about,li#f-disclaimer,li#f-privacy,.portal
    """
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

