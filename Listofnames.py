import os
import csv

temp = list()

for fname in os.listdir('/home/atltt/Documents/SideProjects/TwitterData'):
    if fname.endswith(".csv"):
        f = open('/home/atltt/Documents/SideProjects/TwitterData/' + fname, "rb")
        csv_f = csv.reader(f)
        #temp.append(x[0] for x in csv_f)

        #for row in csv_f:
        #    for col in row:
        #        temp.append(row[0])

        for row in csv_f:
            if row[0] == "username":
                pass
            else:
                tmptmp = row[0]
                #print(tmptmp)
                tmptmp = tmptmp[:tmptmp.find("|")]
                print(tmptmp)
                temp.append(tmptmp)

tempNEW = set(temp)

while 1:
#for x in tempNEW:
    tmpstr = tempNEW.pop()
    print(tmpstr)
    totalstring = """python Exporter.py --username "@%s" """ % (tmpstr, )
    os.system(totalstring)
    #os.system("python Exporter.py --username @%s ") % (tmpstr, )
