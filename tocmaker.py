# -*- coding: utf-8 -*-
import codecs
import urllib
import urllib2
import os,sys
from sgmllib import SGMLParser
from pyquery import PyQuery as pq


def maketoc(topicslist,outputfolder, toc_filename="/toc.html"):
    """
    Create the table of contents file.
    Outputs to toc.html by default.
    """
    ensure_dir(toc_filename)
    toc_file = codecs.open(outputfolder + toc_filename, "w", "utf-8")
    toc_cdfix_file = codecs.open("toc_cd_fix.sh","w","utf-8")
    fp = codecs.open(topicslist, "r", "utf-8")
    toc_header=codecs.open("templates/toc_header.html", "r", "utf-8").read()
    toc_footer = codecs.open("templates/toc_footer.html", "r", "utf-8").read()
    toc_file.write(toc_header)
    index = 0
    currentlevel = 0
    previouslevel = -1
    atleaf = False
    counter = 1000
    while 1:
        text = unicode(fp.readline())
        text= text.strip()
        if text.strip() == "": 
            break
        if text[0] == "#":
            continue #It is a comment
        if text.count("=") > 0:
            currentlevel =  text.count("=")
            text = text.replace("=","")
            leveldiff = previouslevel-currentlevel
            if leveldiff == 0:
                leveldiff = 1
            if atleaf:
                leveldiff =currentlevel-1        
            if atleaf and previouslevel-currentlevel == 0:
                leveldiff = 1        
            if previouslevel-currentlevel > 0:
                leveldiff = -1                
            if atleaf and previouslevel-currentlevel > 0:
                leveldiff = -1                
            if atleaf and previouslevel-currentlevel < 0:
                leveldiff = 2                    
            #print previouslevel , " > " , currentlevel , " : ",    leveldiff ,atleaf
            for i in range(0,leveldiff):
                toc_file.write("</ul>\n")
                toc_file.write("</li>\n")
            toc_file.write("<li class='closed'><span class='folder'>"+text+"</span>\n")
            toc_file.write("<ul>\n")
            previouslevel = currentlevel
            atleaf = False    
            continue
        atleaf = True
        link = text.strip().replace(" ", "_")
        toc_file.write("<li><span class='file'><a href='"+link+".html' target='content'>"+text+"</a></span></li>\n")
        link = link.replace("(", "\(")
        link = link.replace(")", "\)")
        toc_cdfix_file.write("mv " + outputfolder + "/"+link+".html "+outputfolder+"/" + str(counter)+".html\n"  )
        toc_cdfix_file.write("perl -e \"s/"+link+".html/"+str(counter)+".html/g\"  -pi "+outputfolder+"/toc.html\n"  )
        counter+=1
    toc_file.write("</li>\n</ui>\n")    
    toc_file.write(toc_footer+"\n")
    toc_file.close()
    toc_cdfix_file.close()

def ensure_dir(f):
    """
    Check if the given directory is existing or not
    If not existing, create it.
    """
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)


if __name__ == "__main__":
    maketoc("sample_topicslist.txt","content")
