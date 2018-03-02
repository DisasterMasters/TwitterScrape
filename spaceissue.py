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

path1 = "/home/atltt/Documents/SideProjects/TwitterData/putme/tmp2"
path2 = "/home/atltt/Documents/SideProjects/TwitterData/putme/tmp2/Fixed"

for fname in os.listdir('/home/atltt/Documents/SideProjects/TwitterData/putme/tmp2'):
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
            try:
                temp[x] = str(row[4])
                temp[x] = re.sub(r"https:// ","https://",temp[x])
                temp[x] = re.sub(r"http:// ","https://",temp[x])

                row.append(temp[x])
                csv_wf.writerow(row)
                x = x + 1
            except Exception():
                pass
            except ValueError:
                pass
        f.close()
        g.close()




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
