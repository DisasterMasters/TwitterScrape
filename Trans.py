from googletrans import Translator
import csv

translater = Translator()
f = open("@ElNuevoDia.csv", "rb")
csv_f = csv.reader(f)
g = open("Out.csv", "w")
csv_wf = csv.writer(g)
tmp = {}
x = 0
heading = csv_f.next()
heading.append('Translation');
csv_wf.writerow(heading)

for row in csv_f:
    try:
        tmp[x] = translater.translate(row[4], dest="en")
        row.append(tmp[x].text.encode('utf-8')) # for Translation)
        csv_wf.writerow(row)
        print(tmp[x].text)
        print("\n")
    #lines[x][10] = tmp[x].text
        x = x + 1
    except Exception():
        pass

f.close()
