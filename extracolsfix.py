import re
import os


for fname in os.listdir('/home/atltt/Documents/SideProjects/TwitterData'):
    if fname.endswith(".csv"):
        f = open('/home/atltt/Documents/SideProjects/TwitterData/' + fname, "rb")
        g = open('/home/atltt/Documents/SideProjects/TwitterData/' + "extracol" + fname, "a")
        line = f.readline()
        re.sub("|||", "|", line)
        re.sub("||", "|", line)
        re.sub("||||","|", line)
        g.write(line)

        while line:
            line = f.readline()
            re.sub("|||", "|", line)
            re.sub("||", "|", line)
            re.sub("||||","|", line)
            g.write(line)
        f.close()
        g.close()
    try:
        os.unlink('/home/atltt/Documents/SideProjects/TwitterData/' + fname)
    except:
        pass
