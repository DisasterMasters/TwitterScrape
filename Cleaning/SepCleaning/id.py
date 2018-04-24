import csv
import re
import os

path1 = "/home/atltt/Documents/SideProjects/TwitterData/putme/tmp2/Fixed"
path2 = "/home/atltt/Documents/SideProjects/TwitterData/putme/tmp2/Fixed/this"

for fname in os.listdir('/home/atltt/Documents/SideProjects/TwitterData/putme/tmp2/Fixed'):
    c = 0
    if fname.endswith(".csv"):
        f = open(path1 + "/" + fname, "rb")
        g = open(path2 + "/" + "Fixed" + fname, "w")
        csv_f = csv.reader(f)
        csv_wf = csv.writer(g)

        heading = csv_f.next()
        heading.append('UniqueID')
        csv_wf.writerow(heading)

        for row in csv_f:
            heading2 = csv_f.next()
            stringtmp = fname
            stringtmp2 = stringtmp[:-4]
            stringtmp3 = stringtmp2.replace("Fixed@","")
            for row in csv_f:
                stringtmp4 = stringtmp3 + "-" + str(c)
                row.append(stringtmp4)
                csv_wf.writerow(row)
                c = c + 1


        f.close()
        g.close()
