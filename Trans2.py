from googletrans import Translator
import csv
import os
import sys, re

#translater = Translator()

#Sets path to files and outbound file path
path = 'TranslatorTestFiles'
path2 = path + '/Translated'
lskipped = 0
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
      translater = Translator()
      #r4 = re .sub ('__NEWLINE__', '\n', row [4])
      #sys.stderr.write(r4)
      try:
        tmp[x] = translater.translate(row[4], dest="en")
        sys.stderr.write(str(x)+";"+row[4]+";"+tmp[x].text+"\n")
        row.append(tmp[x].text)
        
        g.write('|'.join(row))
        g.write('\n')
                #Used these to guage if still working.
        x = x + 1
                #print(x)
      except:
        lskipped += 1
        pass
      #except ValueError:
                #weird error, text seems normal but throws error
                #Tried working this to print out the error items
                #but it wouldn't print, will look into further
                #print(tmp[x].text)
      #  pass

    f.close()
    g.close()
print(str(lskipped) + ' lines skippde due to bad encoding')
