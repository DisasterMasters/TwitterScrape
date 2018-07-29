from googletrans import Translator
import csv
import os
import sys

translater = Translator()

#Sets path to files and outbound file path
path = 'TranslatorTestFiles'
path2 = path + '/Translated'

for fname in os.listdir(path):
  if fname.endswith(".txt"):
    print (fname)
    f = open(path + "/" + fname, "rt", encoding="utf8")
    g = open(path2 + "/" + "Translated" + fname, "wt", encoding="utf8")
    tmp = {}
    x = 0
    heading = f.readline().rstrip().split('|')
    heading .append('Translation\n')
    g.write('|'.join (heading))

    for line in f:
      row = line.rstrip().split('|')
      try:
        if row[4] is not None:
          tmp[x] = translater.translate(row[4], dest="en")
        sys.stderr.write(str(x)+";"+row[4]+";"+tmp[x].text+"\n")
        row.append(tmp[x].text)
        
        g.write('|'.join(row))
        g.write('\n')
                #Used these to guage if still working.
        x = x + 1
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
