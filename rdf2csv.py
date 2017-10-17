#!/usr/bin/python

import sys
import csv

from HTMLParser import HTMLParser

#spamwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
#https://docs.python.org/2/library/csv.html
#http://stackoverflow.com/questions/14693646/writing-to-csv-with-python-adds-blank-lines

#allrest=[]
csvFile = open('test.csv', 'w')
csvWriter = csv.writer(csvFile, delimiter='\t')
csvWriter.writerow(['Nom', 'Adreca', 'Poblacio', 'C.P.', 'Telefon', 'Latitud', 'Longitud'])

class restaurant: 
    nom='\t'
    addr='\t'
    pobl='\t'
    postal='\t'
    tel="\t"
    lat="\t"
    long="\t"
    def afegir_nom(self,nom):
        self.nom = nom
    
    def afegir_addr(self,addr):
        self.addr = addr
        
    def afegir_pobl(self,pobl):
        self.pobl = pobl
    
    def afegir_postal(self,postal):
        self.postal = postal
        
    def afegir_tel(self,tel):
        self.tel = tel
        
    def afegir_lat(self,lat):
        self.lat = lat
        
    def afegir_long(self,long):
        self.long = long

        
# creem una subclasse i sobreescribim el metodes del han
class MHTMLParser(HTMLParser):

    crest = restaurant()
    ctag = ""
    tagInTel = False

    def handle_starttag(self, tag, attrs):
        self.ctag = tag
        if tag == 'v:vcard':
            self.crest = restaurant()
        elif tag == 'v:tel':
            self.tagInTel = True

    def handle_endtag(self, tag):
        self.ctag = ""
        if tag == 'v:vcard':
            #allrest.append(self.crest)
            csvWriter.writerow([self.crest.nom, self.crest.addr, self.crest.pobl, self.crest.postal, self.crest.tel, self.crest.lat, self.crest.long])
        elif tag == 'v:tel':
            self.tagInTel = False

    def handle_data(self, data):
        if self.ctag == 'v:fn':
            self.crest.afegir_nom(data)
            
        elif self.ctag == 'v:street-address':
            self.crest.afegir_addr(data)
  
        elif self.ctag == 'v:locality':
            self.crest.afegir_pobl(data)
            
        elif self.ctag == 'v:postal-code':
            self.crest.afegir_postal(data)
            
        elif self.ctag == 'rdf:value' and self.tagInTel == True:
            self.crest.afegir_tel(data)
            self.tagInTel = False
            
        elif self.ctag == 'v:latitude':
            self.crest.afegir_lat(data)
            
        elif self.ctag == 'v:longitude':
            self.crest.afegir_long(data)

f = open('restaurants.rdf', 'rb') # obre l'arxiu
rdfSource = f.read()                            
f.close()

parser = MHTMLParser()
parser.feed(rdfSource)


#data = [['Me', 'You'],\
#        ['293', '219'],\
#        ['54', '13']]
#csvWriter.writerows([allrest])
csvFile.close()

#print len(allrest)
#for r in allrest:
    #print r.nom

