##
# This is a quick script that will format/indent HTML
# HTML Tidy is often too destructive, especially with bad HTML, so we're using Beautiful Soup
##
# USAGE: Designed to be used on the command line, just pipe HTML to it, and it will output
#         cat file.html | python format_html.py
### 
# Download & Install Beautiful Soup, if you don't have it already:
# Go to the Beautiful Soup web site, http://www.crummy.com/software/BeautifulSoup/
# Download the package
# Unpack it
# In a Terminal window, cd to the resulting directory
# Type python setup.py install

#
# http://stackoverflow.com/questions/6150108/python-how-to-pretty-print-html-into-a-file
from bs4 import BeautifulSoup as bs
import sys

# This is one way to load a file into a variable:
# lh = open("/Users/mruten/Projects/jacksontriggs/app/assets/javascripts/jt/contactUsComments.html").read()

# But, we'll read from standard input, so we can pipe output to it
# i.e. run with cat filename.html | this_file.py
# data = sys.stdin.readlines()
# print "Counted", len(data), "lines."
with open("index.html", "r") as f:
    data = f.read()
# die
#sys.exit()

#root = data.tostring(sliderRoot) #convert the generated HTML to a string
soup = bs(data)                #make BeautifulSoup
prettyHTML=soup.prettify()   #prettify the html

with open("index_pretty.html", "w") as f:
    f.write(prettyHTML)