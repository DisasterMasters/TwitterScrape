import re
import os


for fname in os.listdir('/home/atltt/Documents/SideProjects/TwitterData'):
    if fname.endswith(".csv"):
        f = open('/home/atltt/Documents/SideProjects/TwitterData/' + fname, "rb")
        g = open('/home/atltt/Documents/SideProjects/TwitterData/' + "extracol" + fname, "a")
        
