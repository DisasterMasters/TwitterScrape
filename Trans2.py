from googletrans import Translator
import csv
import os

translater = Translator()

#Sets path to files and outbound file path
path = 'TranslatorTestFile'
path2 = path + '/Translated'

for fname in os.listdir(path):
  if fname.endswith(".csv"):
    f = open(path + "/" + fname, "rb")
    csv_f = csv.reader(f)
    g = open(path2 + "/" + "Translated" + fname, "w")
    csv_wf = csv.writer(g)
    tmp = {}
    x = 0
    heading = csv_f.next()
    heading.append('Translation')
    csv_wf.writerow(heading)

    for row in csv_f:
      try:
        tmp[x] = translater.translate(row[4], dest="en")
        row.append(tmp[x].text.encode('utf-8'))
        csv_wf.writerow(row)
                #Used these to guage if still working.
                #x = x + 1
                #print(x)
      except Exception():
        pass
      except ValueError:
                #weird error, text seems normal but throws error
                #Tried working this to print out the error items
                #but it wouldn't print, will look into further
                #print(tmp[x].text)
        pass

    f.close()
    g.close()
