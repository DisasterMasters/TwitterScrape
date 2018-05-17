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

path1 = "./tmp"
path2 = "./tmp/Fixed"

for fname in os.listdir(path1):
    c = 0
    if fname.endswith(".csv"):
        f = open(path1 + "/" + fname, "rb")
        g = open(path2 + "/" + "Fixed" + fname, "w")
        temp = {}
        x = 0


        heading = f.readline().rstrip('\n')		  
        heading += '|FixedSpaceIssues\n'
        g.write(heading)

        for line in f:
            line = line.rstrip('\n')
            row = line .split ('|')
            flag = 0
            datetemp = str(row[1])
            temp[x] = str(row[4])
            temp[x] = re.sub(r"https:// ","https://",temp[x])
            temp[x] = re.sub(r"http:// ","https://",temp[x])
            temp[x] = re.sub(r'www. ', "www.", temp[x])
            temp[x] = re.sub(r'\r', "", temp[x])
            temp[x] = re.sub(r'\n', "", temp[x])
            temp[x] = re.sub(r'__PIPE__', "", temp[x])
            temp[x] = re.sub(r'__NEWLINE__', "", temp[x])
            temp[x] = re.sub(r'__CR__', "", temp[x])
            temp[x] = re.sub(r'__NEWLINE__', "", temp[x])
            temp[x] = re.sub(r"pic.*", " ", temp[x])
            temp[x] = re.sub(r"http://[^ ]*", "", temp[x])
            temp[x] = re.sub(r"https://[^ ]*", "", temp[x])
            temp[x] = re.sub(r'"', "", temp[x])
            temp[x] = re.sub(r'  ', " ", temp[x])
            temp[x] = re.sub(r'  ', " ", temp[x])
            row. append (temp[x])
            res = '|'.join(row)
            g.write(res+'\n')
            x = x + 1
        f.close()
        g.close()

for fname in os.listdir(path1):
    try:
        os.remove((path1 + "/" + fname))
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
