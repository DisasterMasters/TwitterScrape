# Twitter Project

Repo for Getting and Cleaning Tweets for UTK CURENT


# Getting the Repo
All you need to do is either clone it with Git or if you don't know Git, just download the zip file containing it all.

# Getting Tweets
In the #GetProg# Folder, you'll be using Exporter.py to handle the gathering of Tweets. 
This takes a bit of time so be patentient with it all. 

It operates under several modes but the two main ones are "--username" and "--querysearch".
For most purposes, "--querysearch" is all that's needed unless you want to focus on a certain person. 

Using Unix with Python installed. Once in the directory, open a terminal and input

**python Exporter.py --COMMAND "USERNAME"**

This will gather and store all the tweets doing this. Several instances of this program can be run at the same time. 

# Cleaning the Tweets
In the Cleaning Folder, Main.py will filter by date, remove unicode errors, translate (if enabled), and combine all files into a single one.

This works by doing a bit of hopscotch between two folders thanks to Python's CSV module. All you need to do is update path1 and path2 inside the main file and it should work. Replacing the osdir path needs to be done as well. When tested this worked on cleaning and removing all unneccessary files. 
