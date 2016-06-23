import re
import csv
from mechanize import Browser
from bs4 import BeautifulSoup
from PIL import Image

#Define a function to avoid global variables
# def FedExAnalyzer():

print ("Starting...")

#Initialize empty zipcode list (zips)
zips = []

#Open CSV with zipcodes in column A
with open("zipcodes.csv","rU") as zipfile:
    for row in zipfile:
        zips.append(row.strip())

#Header row values
shiptime = ["Zip Code", "1 Day", "2 Days", "3 Days", "4 Days", "5 Days", "6 Days", "7+ Days", "Percent in 1-3 Days"]

#Create output CSV called fedexoutput.csv
csvfile = open("fedexoutput.csv","wb")
writer = csv.writer(csvfile)
#Insert header row with columns named for each item in the shiptime list
writer.writerow(shiptime)

#Begin looping through zip codes and analyzing their pixels
for zipcode in zips:

#You can assign all of the varaibles 0 at once with this syntax (note: you have to multiply by the exact number of variables being set to 0)
    brightpink,lightblue,orange,green,pink,yellow,darkblue = (0,)*7

#Open virtual browser, select the form, put in the zipcode, click view map
    br = Browser()
    br.open("http://www.fedex.com/grd/maps/ShowMapEntry.do")
    br.select_form("mapEntryForm")
    br["originZip"] = zipcode
    response = br.submit(label="View map")
    html = response.read()
#Find the url of the map image
    soup = BeautifulSoup(html, "html.parser")
    zipcodemap = str(soup.find("img", src=re.compile("templates/components/apps/wgsm/*")))

    maplink = re.search('src="(.+?)" style',zipcodemap)
    if maplink:
        found = maplink.group(1)

#The found variable doesn't have the http:// etc in front of it so fullmaplink adds that
    fullmaplink = "http://www.fedex.com"+found
    
#Download map
    br.retrieve(fullmaplink,str(zipcode)+".png")

#Analyze pixel colors    
    # im = Image.open("/Users/mattkrueger/Desktop/FedEx/" + zipcode + ".png") #Mac code
    im = Image.open("C:/Users/m.krueger/Desktop/FedEx/" + zipcode + ".png") #Windows code

    for pixel in im.getdata():
        if pixel == (255,0,128):
            brightpink += 1
        elif pixel == (0,255,255):
            lightblue += 1
        elif pixel == (255,128,0):
            orange += 1
        elif pixel == (0,255,0):
            green += 1
        elif pixel == (255,0,255):
            pink += 1
        elif pixel == (254,254,0):
            yellow += 1
        elif pixel == (0,0,255):
            darkblue += 1

#colorlist is a list with each color's pixel count
    colorlist = [brightpink, lightblue, orange, green, pink, yellow, darkblue]
#total is the sum of all of the pixel counts of colorlist
    total = sum(colorlist)
#onetothreedays is the sum of the 1, 2, and 3 day shiptimes which are represented by brightpink, lightblue, and orange
#It is also formatted as a percent cut off at 2 decimals (the values after 2 decimals are actually lost, so get rid of that code if you want to preserve them)
    onetothreedays = "{percent:.2%}".format(percent=float(brightpink + lightblue + orange)/float(total))
#csvoutput has the zipcode in column A, the pixel values for 1-7+ days in columns B:H and the 1-3 day shiptime value in column I
    csvoutput = [zipcode] + colorlist + [onetothreedays]
#This actually writes the row, using csvoutput
    writer.writerow(csvoutput)

#Closes the CSV? Script crashes without this line...
csvfile.close()

print ("Complete")
    
#Run from Python repl by using image2.FedExAnalyzer() (cd Desktop/Fedex, python, import image2, image2.FedExAnalyzer() )
# if __name__ == "__main__":
#     FedExAnalyzer()