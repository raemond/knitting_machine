#!/usr/bin/env python

# Copyright 2009  Steve Conklin 
# steve at conklinhouse dot com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

import sys
import brother
from PIL import Image
import array

TheImage = None

##################

def roundeven(val):
    return (val+(val%2))

def roundeight(val):
    if val % 8:
        return val + (8-(val%8))
    else:
        return val

def roundfour(val):
    if val % 4:
        return val + (4-(val%4))
    else:
        return val

def nibblesPerRow(stitches):
    # there are four stitches per nibble
    # each row is nibble aligned
    return(roundfour(stitches)/4)

def bytesPerPattern(stitches, rows):
    nibbs = rows * nibblesPerRow(stitches)
    bytes = roundeven(nibbs)/2
    return bytes

def bytesForMemo(rows):
    bytes = roundeven(rows)/2
    return bytes

##############


version = '1.0'

if len(sys.argv) < 6:
    print 'Usage: %s oldbrotherfile pattern# image.png numberofcolors newbrotherfile' % sys.argv[0]
    sys.exit()

bf = brother.brotherFile(sys.argv[1])
pattnum = sys.argv[2]
imagefile = sys.argv[3]
maxcolors = sys.argv[4]
multifile = sys.argv[3]+'-multi.txt'

allPatterns = bf.getPatterns()

TheImage = Image.open(imagefile)
TheImage.load()

im_size = TheImage.size
width = im_size[0]
print "width:",width
height = im_size[1]
print "height:", height

# Check the image has the correct number of colors we're expecting 
# It's so easy when preparing the image to miss a shade off here and there
x = 0
y = 0
z = 0
hasColor = False
colors = []
colorSymbols = [' ','*','^','#','&','%','@','$','-','+','=']
symbol = ' '
imageConvertLines = []
imageConvertRow = []

while x < width:
    value = TheImage.getpixel((x,y))
    hasColor = False
    z = 0
    while z < len(colors):
        if value == colors[z]:
            hasColor = True
            break
        z = z+1

    if hasColor == False:
        colors.append(value)

    symbol = colorSymbols[z]
    imageConvertRow.append(z+1)

    sys.stdout.write(str(symbol))
    sys.stdout.write(' ')

    x = x+1
    if x == width: #did we hit the end of the line?
        imageConvertLines.append(imageConvertRow)
        imageConvertRow = []
        y = y+1
        x = 0
        print " "
        if y == height:
            break


if len(colors) != int(maxcolors):
    print 'ERROR: Found',len(colors),'colors when there should be',int(maxcolors),'!\nAborting.\n\n'
    sys.exit()

# Now we have a int for each color, convert imagefile to multifile. 
# Create this interum state because it allows you to alter the order of colors and lines by hand if you wish
y = height-1
colorInt = 0
multiOutfile = open(multifile, 'wb')

while y > -1:

    #print imageConvertLines[y]
    # Always do a line of knitting for every colour even if it's not present in the row (ensures the thickness of the knitting is consistent)
    z = 0
    while z < len(colors):
        multiOutfile.write(str(z+1)+'#')
        x = 0
        while x < width:
            if imageConvertLines[y][x] == (z+1):
                multiOutfile.write('1')
            else:
                multiOutfile.write('0')
            x = x+1
        multiOutfile.write('\n')
        z = z+1

    y = y-1

multiOutfile.close()

# find the program entry
thePattern = None

for pat in allPatterns:
    if (int(pat["number"]) == int(pattnum)):
        #print "found it!"
        thePattern = pat
if (thePattern == None):
    print "Pattern #",pattnum,"not found!"
    exit(0)

# debugging stuff here
x = 0
y = 0

# load multi colour file
lines = [line.strip() for line in open(multifile)]
colours = []

# ok got a bank, now lets figure out how big this thing we want to insert is
width = len(lines[0])-2 #2 chars used for memo data, that doesn't count toward the width of the pattern
print "width:",width
height = len(lines)
print "height:", height

while x < height:
    colours.append(int(lines[x][0]))
    lines[x] = lines[x][2:]
    sys.stdout.write(str(colours[x]))
    sys.stdout.write(' ')
    sys.stdout.write(str(lines[x]))
    sys.stdout.write('\n\r')
    x = x+1

x = 0

# debugging stuff done

# now to make the actual, yknow memo+pattern data

# append colours to the memo data
memoentry = []
r = 0
for r in range(bytesForMemo(height)):
    if(r*2+1 < len(colours)):
        print hex(colours[r*2 + 1] << 4 | colours[r*2])
        memoentry.append(colours[r*2 + 1] << 4 | colours[r*2])
    r = r+1

#pad for odd number of rows
if(len(colours) % 2 != 0):
    memoentry.append(colours[len(colours)-1])

# now for actual real live pattern data!
pattmemnibs = []
allrows = []
for r in range(height):
    row = []  # we'll chunk in bits and then put em into nibbles
    for s in range(width):
        value = lines[r][width-s-1]
        row.append(int(value))

    allrows.append(row)
    #print row
    # turn it into nibz

for r in range(height):
    row = allrows[r]
    for s in range(roundfour(width) / 4):
        n = 0
        for nibs in range(4):
            #print "row size = ", len(row), "index = ",s*4+nibs

            if (len(row) == (s*4+nibs)):
                break       # padding!
            
            if (row[s*4 + nibs]):
                n |= 1 << nibs
        pattmemnibs.append(n)
        #print hex(n),

if (len(pattmemnibs) % 2):
    # odd nibbles, buffer to a byte
    pattmemnibs.append(0x0)

print len(pattmemnibs), "nibbles of data"

# turn into bytes
pattmem = []
for i in range (len(pattmemnibs) / 2):
    pattmem.append( pattmemnibs[i*2] | (pattmemnibs[i*2 + 1] << 4))

#print map(hex, pattmem)
# whew. 


# now to insert this data into the file 

# now we have to figure out the -end- of the last pattern is
endaddr = 0x6df

beginaddr = thePattern["pattend"]
endaddr = beginaddr + bytesForMemo(height) + len(pattmem)
print "beginning will be at ", hex(beginaddr), "end at", hex(endaddr)

#print "Current header data"
#for i in thePattern['header']:
#    print '0x%02X' % ord(i)

for i in range(len(thePattern['header'])):
    thePattern['header'][i] = ord(thePattern['header'][i])
    
# we need to change the mode from 4 to 8 (this will turn off reading the mylar sheet as we knit!)
thePattern['header'][5] = 8 << 4 | 9
# and while we're here we should change the width and height too :)
strHeight = "%03d" % height
strWidth = "%03d" % width
thePattern['header'][2] = int(strHeight[0]) << 4 | int(strHeight[1])
thePattern['header'][3] = int(strHeight[2]) << 4 | int(strWidth[0])
thePattern['header'][4] = int(strWidth[1]) << 4 | int(strWidth[2])

#print thePattern['header'][5]
#print '0x%02X' % (8 << 4 | 9)

# look at the header data
print "New header:",
for i in thePattern['header']:
    print '0x%02X' % i,

# write back the header
seek = 0
for i in range(len(thePattern['header'])):
    bf.setIndexedByte(seek, thePattern['header'][i])
    seek = seek + 1

# Note - It's note certain that in all cases this collision test is needed. What's happening
# when you write below this address (as the pattern grows downward in memory) in that you begin
# to overwrite the pattern index data that starts at low memory. Since you overwrite the info
# for highest memory numbers first, you may be able to get away with it as long as you don't
# attempt to use higher memories.
# Steve

if beginaddr < 0x2BC:
    print "sorry, this will collide with the pattern entry data since %s is < 0x2BC!" % hex(beginaddr)
    exit

# write the memo and pattern entry from the -end- to the -beginning- (up!)
for i in range(len(memoentry)):
    bf.setIndexedByte(endaddr, memoentry[i])
    endaddr -= 1

for i in range(len(pattmem)):
    bf.setIndexedByte(endaddr, pattmem[i])
    endaddr -= 1

# push the data to a file
outfile = open(sys.argv[5], 'wb')

d = bf.getFullData()
outfile.write(d)
outfile.close()
