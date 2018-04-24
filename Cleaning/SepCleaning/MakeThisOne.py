import csv
import re
import os

path1 = "/home/atltt/Documents/SideProjects/TwitterData/putme/tmp2/Fixed/this"
path2 = "/home/atltt/Documents/SideProjects/TwitterData/putme"

g = open(path2 + "/" + "MegaFile.csv", "w")
csv_wf = csv.writer(g)


for fname in os.listdir('/home/atltt/Documents/SideProjects/TwitterData/putme/tmp2/Fixed/this'):
    if fname.endswith(".csv"):
        f = open(path1 + "/" + fname, "rb")
        csv_f = csv.reader(f)

        for row in csv_f:
            csv_wf.writerow(row)



        f.close()
g.close()
