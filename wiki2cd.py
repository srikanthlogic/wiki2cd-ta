# -*- coding: utf-8 -*-
"""
  Copyright (c) 2010 Santhosh Thottingal

  This is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 3.0 of the License, or
  (at your option) any later version.

  This software is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU Lesser General Public License
  along with this software; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import codecs
import urllib
import urllib2
import os,sys
import hashlib
from sgmllib import SGMLParser
from pyquery import PyQuery as pq

class ImageLister(SGMLParser):
	"""
	An image listerner class for the sgml parser
	Used for finding out the image links in the page
	"""
	
	def reset(self):							  
		SGMLParser.reset(self)
		self.images = []
		
	def start_img(self, attrs):		 
		src = [v for k, v in attrs if k=='src'] 
		if src:
			self.images.extend(src)
			
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
			#print previouslevel , " > " , currentlevel , " : ",	leveldiff ,atleaf
			for i in range(0,leveldiff):
				toc_file.write("</ul>\n")
				toc_file.write("</li>\n")
			toc_file.write("<li class='closed'><span class='folder'>"+text+"</span>\n")
			toc_file.write("<ul>\n")
			previouslevel = currentlevel
			atleaf = False	
			continue
		atleaf = True
		link = text.split(',')[0].strip().replace(" ", "_")
		toc_file.write("<li><span class='file'><a href='"+link+".html' target='content'>"+text.split(',')[0]+"</a></span></li>\n")
		link = link.replace("(", "\(")
		link = link.replace(")", "\)")
		toc_cdfix_file.write("mv " + outputfolder + "/"+link+".html "+outputfolder+"/" + str(counter)+".html\n"  )
		toc_cdfix_file.write("perl -e \"s/'"+link+".html'/'"+str(counter)+".html'/g\"  -pi "+outputfolder+"/toc.html\n"  )
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

def grab_pages(wikibase, topicslist,outputfolder):
	"""
	Read each topic and get that page using grab_page function
	"""
	fp = codecs.open(topicslist, "r", "utf-8")
	counter =1000 
	while 1:
		try:
			text = unicode(fp.readline())
			text= text.strip()
			if text.strip() == "": 
				break
			if text[0] == "#":
				continue #It is a comment	
			if text[0]== "=": 
				continue
			articlename = text.split(',')[0].replace(" ", "_")
			if (len(text.split(',')) > 1):
				revid = text.split(',')[1]
				grab_page_rev(wikibase,articlename,outputfolder,counter,revid)
			else:
				grab_page(wikibase, wikibase + "/wiki/"+articlename,outputfolder,counter)			
				counter+=1
		except KeyboardInterrupt:
			return 

def grab_page(wikibase, pagelink,outputfolder, pagenum):
	"""
	grab the page from wiki
	"""
	#Note: You might need to edit he below line for the bottom links- contributors, latest version in wiki etc.
	metacontent ="""
	<hr/>
	<ul>
	<li><a href="$ONWIKI$" target="_blank" class="metalinks">விக்கிப்பீடியாவில் அண்மைய பதிப்பை படிக்க</a></li>
	<li><a href="http://toolserver.org/~daniel/WikiSense/Contributors.php?wikilang=ta&wikifam=.wikipedia.org&since=&until=&grouped=on&order=-edit_count&max=100&order=-edit_count&format=html&page=$PAGE$" target="_blank"  class="metalinks">பங்களிப்பாளர்கள்</a></li>
	<ul>
	"""
	path = outputfolder+"/"
	imageoutputfolder = "wikiimages/"
	imagenamefixscript = codecs.open("imagenamefix.sh", "a", "utf-8")
	imagenamefixscript.write("mkdir " +path+ imageoutputfolder +"\n")
	try:
		link= pagelink.strip()
		parts = link.split("/")
		filename = parts[len(parts)-1]
		print "GET " + link + " ==> " + outputfolder + "/"+ filename+  ".html"
		if os.path.isfile(outputfolder + "/"+ filename+  ".html"):
			print "File " + outputfolder + "/"+ filename+  ".html" + " already exists"
			return
		quotedfilename = urllib.quote(filename.encode('utf-8')) 
		link = wikibase +"/wiki/"+quotedfilename
		opener = urllib2.build_opener()
		opener.addheaders = [('User-agent', 'Mozilla/5.0')]
		infile = opener.open(link)
		page = infile.read()
		htmlname =outputfolder + "/"+ filename+  ".html"
		f= open(htmlname,'w')
		metacontent = metacontent.replace("$ONWIKI$",link)
		metacontent = metacontent.replace("$PAGE$",quotedfilename)
		page = page.replace("</body>",metacontent+"</body>")
		# The next line is where the page cleanup happens.
		page = cleanup(page)
		parser = ImageLister()
		parser.feed(page)
		parser.close()
		f.write(page)
		f.close()
		for image in parser.images:
			if not image[0]=="/": #relative reference
				grab_image(image,outputfolder)
				extension=image.split(".")[-1]
				link= image.strip()
				link=link.replace("//","http://")
				filename=link.split("/")[-1]
				m = hashlib.md5()
				m.update(filename.encode("utf-8"))
				md5filename= m.hexdigest()[0:7]
				oldimagefile= link.strip().replace("/", "\/")
				newimagefile= md5filename+"."+extension
				output_filename = str(outputfolder + "/" + newimagefile)
				imagenamefixscript.write(("mv " + path +  newimagefile + "  " +path  + imageoutputfolder +"/" + newimagefile+"\n"))
				outputfilepath=str(imageoutputfolder +"/" + newimagefile).strip().replace("/", "\/")
				imagenamefixscript.write("perl -e \"s/"+oldimagefile+"/"+ outputfilepath+"/g\"  -pi "+ htmlname.replace("(","\(").replace(")","\)")+"\n" )				 
	except KeyboardInterrupt:
		sys.exit()
	except urllib2.HTTPError:
		print("Error: Could not download the page")
		pass
	imagenamefixscript.close()



def grab_page_rev(wikibase,articlename,outputfolder, pagenum,revid):
	"""
	grab the page from wiki
	"""
	counter = 1000
	#Note: You might need to edit he below line for the bottom links- contributors, latest version in wiki etc.
	metacontent ="""
	<hr/>
	<ul>
	<li><a href="$LATESTONWIKI$" target="_blank" class="metalinks">விக்கிப்பீடியாவில் அண்மைய பதிப்பை படிக்க</a></li>
	<li><a href="$ONWIKI$" target="_blank" class="metalinks">விக்கிப்பீடியாவில் இந்த பதிப்பை படிக்க</a></li>
	<li><a href="http://toolserver.org/~daniel/WikiSense/Contributors.php?wikilang=ta&wikifam=.wikipedia.org&since=&until=&grouped=on&order=-edit_count&max=100&order=-edit_count&format=html&page=$PAGE$" target="_blank"  class="metalinks">பங்களிப்பாளர்கள்</a></li>
	<ul>
	"""
	path = outputfolder+"/"
	imageoutputfolder = "wikiimages/"
	imagenamefixscript = codecs.open("imagenamefix.sh", "a", "utf-8")
	imagenamefixscript.write("mkdir " +path+ imageoutputfolder +"\n")
	try:
		print "GET " + wikibase + "/wiki/" + articlename + " ==> " + outputfolder + "/"+ articlename+  ".html"
		if os.path.isfile(outputfolder + "/"+ articlename+  ".html"):
			print "File " + outputfolder + "/"+ articlename+  ".html" + " already exists"
			return
		quotedfilename = urllib.quote(articlename.encode('utf-8')) 
		latestpagelink = wikibase +"/wiki/"+quotedfilename
		link = wikibase + "/w/index.php?title"+quotedfilename+"&oldid="+revid
		opener = urllib2.build_opener()
		opener.addheaders = [('User-agent', 'Mozilla/5.0')]
		infile = opener.open(link)
		page = infile.read()
		htmlname =outputfolder + "/"+ articlename+  ".html"
		f= open(htmlname,'w')
		metacontent = metacontent.replace("$ONWIKI",link.encode('utf-8'))
		metacontent = metacontent.replace("$LATESTONWIKI$",latestpagelink)
		metacontent = metacontent.replace("$PAGE",quotedfilename)
		page = page.replace("</body>",metacontent+"</body>")
		# The next line is where the page cleanup happens.
		page = cleanup(page)
		parser = ImageLister()
		parser.feed(page)
		parser.close()
		f.write(page)
		f.close()
		for image in parser.images:
			#print image
			#if not image[0]=="/": #relative reference
			#print 'before grab image for' + image
			grab_image(image,outputfolder)
			extension=image.split(".")[-1]
			link= image.strip()
			link=link.replace("//","")
			filename=link.split("/")[-1]
			m = hashlib.md5()
			m.update(filename.encode("utf-8"))
			md5filename= m.hexdigest()[0:7]
			oldimagefile= link.strip().replace("/", "\/")
			newimagefile= md5filename+"."+extension
			output_filename = str(outputfolder + "/" + newimagefile)
			imagenamefixscript.write(("mv " + path +  newimagefile + "  " +path  + imageoutputfolder + newimagefile+"\n"))
			outputfilepath=str(imageoutputfolder +"/" + newimagefile).strip().replace("/", "\/")
			imagenamefixscript.write("perl -e \"s/"+oldimagefile+"/"+ outputfilepath+"/g\"  -pi "+ htmlname.replace("(","\(").replace(")","\)")+"\n" )				 
			counter+=1
	except KeyboardInterrupt:
		sys.exit()
	except urllib2.HTTPError:
		print("Error: Could not download the page")
		pass
	imagenamefixscript.close()
	
def grab_image(imageurl, outputfolder):
	"""
	Get the image from wiki
	"""
	try:
		link= imageurl.strip()
		parts = link.split("/")
		filename = parts[len(parts)-1]
		extension = link.split(".")[-1]
		m = hashlib.md5()
		m.update(filename.encode("utf-8"))
		md5filename= m.hexdigest()[0:7]
		output_filename = str(outputfolder + "/" + md5filename + "." + extension)
		print("GET IMAGE " + link + " ==> " + output_filename)
		if os.path.isfile(output_filename):
			print("File " + output_filename + " already exists")
			return
		opener = urllib2.build_opener()
		opener.addheaders = [('User-agent', 'Mozilla/5.0')]
		infile = opener.open('http:'+link)
		page = infile.read()
		ensure_dir(output_filename)
		f= open(output_filename,"w")
		f.write(page)
		f.close()
	except KeyboardInterrupt:
		sys.exit()
	except urllib2.HTTPError:
		print("Error: Cound not download the image")
		pass

def cleanup(page):
	"""
	remove unwanted sections of the page.
	Uses pyquery.
	"""
	document = pq(page)
	#If you want to remove any other section, just add the class or id of the section below with comma seperated
	unwanted_sections_list="""
	.editsection,#mw-panel,script,#mw-head,.infobox,#toc,#jump-to-nav,.reference,
	.navbox,#footer,#catlinks,#mw-js-message,.magnify,#mainarticle,.printfooter,#siteSub,
	#protected-icon,.dablink,.boilerplate,#mw-revision-info,#mw-revision-nav
	"""
	unwanted_divs = unwanted_sections_list.split(",")
	for section in unwanted_divs:
		document.remove(section.strip())
	return document.wrap('<div></div>').html().encode("utf-8")
	
if __name__ == '__main__':
	if len(sys.argv)> 2:
		wikibase = sys.argv[1]
		topicslist = sys.argv[2]
		outputfolder = sys.argv[3]
		maketoc(topicslist,outputfolder)
		grab_pages(wikibase,topicslist,outputfolder)
	else:
		print("Error: Missing arguments. Eg usage: toc_maker.py http://ta.wikipedia.org topics.txt wikiofflinefolder")

