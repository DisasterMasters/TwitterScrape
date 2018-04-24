import csv
import re
import os

#FIX THIS ISSUES REEEEEEEEEEEE


#f = open("@CBS12.csv", "rb")
#csv_f = csv.reader(f)
#g = open("Fixed@CBS12.csv", "w")
#csv_wf = csv.writer(g)

#temp = {}
#x = 0

#heading = csv_f.next()
#heading.append('FixedNonsense')
#csv_wf.writerow(heading)


#print out debugging stage
#and try to fix that within the item and edit the retrieval script.
#maybe work with this thing to fix this issue
#use regex to create new csv file of the dudes based on the date.
#time trends topics over time.
#work on creating this into mongodb format so we can work on this more easily.
#

path1 = "/home/atltt/Documents/SideProjects/TwitterData/putme/tmp2"
path2 = "/home/atltt/Documents/SideProjects/TwitterData/putme/tmp2/Fixed"

for fname in os.listdir('/home/atltt/Documents/SideProjects/TwitterData/putme/tmp2'):
    c = 0
    if fname.endswith(".csv"):
        f = open(path1 + "/" + fname, "rb")
        g = open(path2 + "/" + "Fixed" + fname, "w")
        csv_f = csv.reader(f)
        csv_wf = csv.writer(g)
        temp = {}
        x = 0


        heading = csv_f.next()
        heading.append('FixedSpaceIssues')
        csv_wf.writerow(heading)

        for row in csv_f:
            flag = 0
            datetemp = str(row[1])
            if datetemp.startswith("2018-01"):
                flag = 1
            if datetemp.startswith("2018-02"):
                flag = 1
            if datetemp.startswith("2018-03"):
                flag = 1
            if datetemp.startswith("2017-12"):
                flag = 1
            if datetemp.startswith("2017-11"):
                flag = 1
            if datetemp.startswith("2017-10"):
                flag = 1
            if datetemp.startswith("2017-09"):
                flag = 1
            if datetemp.startswith("2017-08"):
                flag = 1
            if datetemp.startswith("2017-07"):
                flag = 1
            if datetemp.startswith("2017-06"):
                flag = 1
            if datetemp.startswith("2017-05"):
                flag = 1
            else:
                pass
            if flag == 1:
                try:
                    temp[x] = str(row[4])
                    temp[x] = re.sub(r"https:// ","https://",temp[x])
                    temp[x] = re.sub(r"http:// ","https://",temp[x])
                    temp[x] = re.sub(r'www. ', "www.", temp[x])
                    temp[x] = re.sub(r'\r', "", temp[x])
                    temp[x] = re.sub(r'\n', "", temp[x])

                    #temp[x] = re.sub(r"pic.*", " ", temp[x])

                    row.append(temp[x])
                    csv_wf.writerow(row)
                    x = x + 1
                except Exception():
                    pass
                except ValueError:
                    pass

        f.close()
        g.close()

for fname in os.listdir('/home/atltt/Documents/SideProjects/TwitterData/putme/tmp2'):
    try:
        os.remove((path1 + "/" + fname))
    except Exception:
        pass
    except OSError():
        pass

tempstr = path1
path1 = path2
path2 = tempstr

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

for fname in os.listdir('/home/atltt/Documents/SideProjects/TwitterData/putme/tmp2/Fixed'):
    path3 = '/home/atltt/Documents/SideProjects/TwitterData/putme/tmp2/Fixed'
    try:
        os.remove((path3 + "/" + fname))
    except Exception:
        pass
    except OSError():
        pass

g = open(path2 + "/" + "MegaFile.csv", "w")
csv_wf = csv.writer(g)


for fname in os.listdir('/home/atltt/Documents/SideProjects/TwitterData/putme/tmp2/Fixed'):
    path1 = '/home/atltt/Documents/SideProjects/TwitterData/putme/tmp2/Fixed'
    if fname.endswith(".csv"):
        f = open(path1 + "/" + fname, "rb")
        csv_f = csv.reader(f)

        for row in csv_f:
            csv_wf.writerow(row)



        f.close()
g.close()


for fname in os.listdir('/home/atltt/Documents/SideProjects/TwitterData/putme/tmp2'):
    path3 = '/home/atltt/Documents/SideProjects/TwitterData/putme/tmp2'
    try:
        os.remove((path3 + "/" + fname))
    except Exception:
        pass
    except OSError():
        pass
#
#for row in csv_f:
#    try:
#        temp[x] = str(row[4])
#        temp[x] = re.sub(r"https:// ","https://",temp[x])
#        temp[x] = re.sub(r"http:// ","http://", temp[x])
#        row.append(temp[x])
#        csv_wf.writerow(row)
#        x = x + 1
#    except Exception():
#        pass
#    except ValueError:
#        pass
#f.close()
#g.close()
