# Knitting Machine hack for the Brother KM-950i

## Contents

- Introduction
- Dependencies
- Instructions - Simple Two Colour
- Instructions - Multi Colour
- Developer Notes



## Introduction

This python script is designed to convert image files to knitting patterns in a format that can be uploaded to a Brother KM-950i knitting machine.

This work is a fork of the original hack for the Brother KM-930e by Adafruit. The KM-950i has special requirements that doesn't work for the KM-930e (namely it understands 32bit, not 16bit).



## Dependencies

- pillow (Python Image Library)
```bash
pil install pillow
```
- In order to upload the patterns you generate here to your knitting machine you need to hack an FTDI cable. Instructions on how to do this can be found at https://learn.adafruit.com/electroknit/cable


## Instructions - Simple Two Colour Patterns

### 1. Copy the right sized blank directory into a new working directory.

**Note:** each blank is 60 wide x 150 tall and the first level directories are the number of blanks wide, the second level is the number of blanks tall. So If you have an image that's 120px wide then you want ```blankPatterns/2``` and 50px tall then you want subdirectory ```1/```. If you have an image that's 40px wide you want ```blankPatterns/1/``` and 310px tall then you want subdirectory ```3/```.

```bash
cp -r blankPatterns/1/1/ patterns/foobar
```

### 2. Copy your image into your working directory
```bash
cp foobar/myImage.png patterns/foobar/
```

### 3. Convert image to pattern
```bash
python insertpattern.py patterns/foobar/file-01.dat 901 patterns/foobar/myImage.png patterns/foobar/file-01.dat
```

### 4. Convert pattern to tracks
```bash
cd patterns/foobar/ && python ../../splitfile2track.py ./file-01.dat 2>&1 && cd ../../
```

### 5. Output result to check your work
```bash
python dumppattern.py patterns/foobar/file-01.dat 901
```

### 6. Connect to knitting machine to upload.

**Note:** you'll need to clear the memory on your knitting machine (command 888), then power cycle it, set it to load state (command 551), press 1 and M

```bash
python PDDemulate.py patterns/foobar/ /dev/cu.usbserial-A4WYNI7I
```



## Instructions - Multi Colour Patterns

### 1. Copy the right sized blank directory into a new working directory.

**Note:** each blank is 60 wide x 150 tall and the first level directories are the number of blanks wide, the second level is the number of blanks tall. So If you have an image that's 120px wide then you want ```blankPatterns/2``` and 50px tall then you want subdirectory ```1/```. If you have an image that's 40px wide you want ```blankPatterns/1/``` and 310px tall then you want subdirectory ```3/```.

**Note:** multi colour patterns are a little more complicated than two colour. The height of multi patterns are the number of colours * the height of your image. For example, if you have an image that's 40px tall and uses 4 colours, then the output pattern will actually be 160 rows tall so will need a subdirectory ```2/```.

```bash
cp -r blankPatterns/1/1/ patterns/foobar
```

### 2. Copy your image into your working directory.
```bash
cp foobar/myImage.png patterns/foobar/
```

### 3. Convert image to pattern.

**Note:** make sure you change the '3' interger to the correct number of colors as this is used for validation.

**Note:** there are four different algorithms available to convert your image to a multi colour pattern: doubleHeight, offsetRows, blankSecondPass and ditheredRows. Please read this blog post which briefly introduces the four algorithms and provides a benchmark: http://heartofpluto.co/2017/04/02/algorithms-of-multi-coloured-knitting/

By default offsetRows is chosen.

```bash
python insertpatternMultiColour.py patterns/foobar/file-01.dat 901 patterns/foobar/myImage.png 3 patterns/foobar/file-01.dat offsetRows
```

### 4. Convert pattern to tracks.
```bash
cd patterns/foobar/ && python ../../splitfile2track.py ./file-01.dat 2>&1 && cd ../../
```

### 5. Output result to check your work
```bash
python dumppattern.py patterns/foobar/file-01.dat 901
```

### 6. Connect to knitting machine to upload.

**Note:** you'll need to clear the memory on your knitting machine (command 888), then power cycle it, set it to load state (command 551), press 1 and M

```bash
python PDDemulate.py patterns/foobar/ /dev/cu.usbserial-A4WYNI7I
```


## Developer Notes

Please see the Changelog file for the latest changes

These files are related to the Brother KH-930E knitting machine, and other similar models.

=== NOTE ===

The emulator script was named PDDemulate-1.0.py, and the instructions in a lot of forums for using it have that name.
The script has been renamed, and is now simply PDDemulate.py.

============

The files in the top directory are the ones used for the knitting project that Becky Stern and Limor Fried did:

http://blog.makezine.com/archive/2010/11/how-to_hacking_the_brother_kh-930e.html
http://blog.craftzine.com/archive/2010/11/hack_your_knitting_machine.html

The subdirectories contain the following:

* docs:

  Documentation for the project, including the data file format information and
  scans of old manuals which are hard to find.

* experimental:

  Some never-tested code to talk to a Tandy PDD-1 or Brother disk drive.

* file-analysis:

  Various scripts used to reverse-engineer the brother data format, as well as some spreadsheets used.
  These may or may nor work, but may be useful for some.

* test-data:

  A saved set of data from the PDDemulator, with dicumentation abotu what's saved in each memory location.
  A good way to play with the file analysis tools, and may give some insight into the reverse engineering
  process.

* textconversion

  The beginnings of work to convert text to a knittable banner.

--------------------------

The Brother knitting machines can save data to an external floppy disk drive, which connects to the machine using a serial cable.

These external floppy drives are difficult to find and expensive, and the physical format of the floppy disks is different than 3.25" PC drives.

The program PDDemulate acts like a floppy drive, and runs on linux machines, allowing you to save and restore data from the knitting machine.

Most of the formatting of the saved data files has been figured out, and the tools used to do that are also in this repository.

There is also an example of how to generate a text banner in a .png image file, 
which may be useful to some.

The work that Steve Conklin did was based on earlier work by John R. Hogerhuis.

This extended by Becky and Limor and others, including Travis Goodspeed:

http://travisgoodspeed.blogspot.com/2010/12/hacking-knitting-machines-keypad.html
