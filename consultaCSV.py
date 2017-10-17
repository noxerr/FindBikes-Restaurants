#! /usr/bin/python
import csv
import sys
import math
import urllib
import xml.etree.ElementTree as ET    
import webbrowser  



# graus a radians
DRAD = math.pi/180.0  # radians en 1 grau
ERAD = 6371000.0      # radi terra en metres
def deg2rad(deg): return deg*DRAD

# retorn a la distancia (en metres) entre 2 GeoLoc
def get_distance(geo_loc1, geo_loc2):
  lat1, lon1 = float(geo_loc1.lat), float(geo_loc1.lon)
  lat2, lon2 = float(geo_loc2.lat), float(geo_loc2.lon)
  phi1, phi2 = deg2rad(90.0-lat1), deg2rad(90.0-lat2)
  the1, the2 = deg2rad(lon1), deg2rad(lon2)
  cos = math.sin(phi1)*math.sin(phi2)*math.cos(the1-the2)+math.cos(phi1)*math.cos(phi2)
  return math.acos(cos)*ERAD
  
  
class GeoLoc(object):
  # constructor
  def __init__(self, adresa, lat, lon):
    self.adresa = adresa
    self.lat = lat
    self.lon = lon

  # valida si te coordenades definides
  def valid(self): return self.lat!="" and self.lon!=""
  
  
class Restaurante(GeoLoc):
  nom = ""
  info = ""
  poblacio = ""
  cp = ""
  # constructor
  def __init__(self, line):
    super(Restaurante, self).__init__(line[1], line[5], line[6]) #inicializacion del padre con los elementos 1 5 y 6 de la lista line
    self.nom = line[0] 
    self.info = line[4]
    self.poblacio = line[2]
    self.cp = line[3]
    

      
# torna la llista de restaurants d'un fitxer CSV
def get_restaurants(Constrain):
  ifile  = open('test.csv', "r")
  reader = csv.reader(ifile, delimiter='\t')
  reader.next()
  restaurantes = [ r for r in map(Restaurante, reader) if r.valid() and eval_expr(Constrain, r.nom) ]
  ifile.close()
  return restaurantes

  
def eval_expr(constrain, nom):
    if isinstance(constrain, str): #base case
        return constrain in nom
    elif isinstance(constrain, tuple):
        return (eval_expr(constrain[0], nom) and eval_expr(constrain[1], nom))
    elif isinstance(constrain, list):
        val = False
        for elem in constrain:
            val |= (elem in nom)
        return val
    return False;
  
    

class Estacion(GeoLoc):
    bicisSobran = "0"
    bicisFaltan = "0"
    
    def __init__(self,line): #direccion, bicisFaltan, bicisSobran, latitud, longitud
        super(Estacion,self).__init__(line[0], line[3], line[4])
        self.bicisFaltan = line[1]
        self.bicisSobran = line[2]
        
    def validaAparcar(self):
        return self.bicisFaltan > "10"
    
    def validaCogerBici(self):
        return self.bicisSobran > "0"



    

#obtenemos una lista de listas de estaciones, con su direccion, lat, long, y bicisActuales/Totales 
def get_all_estaciones():
    sock = urllib.urlopen("http://wservice.viabicing.cat/getstations.php?v=1")
    xmlSource = sock.read()
    sock.close()
    root = ET.fromstring(xmlSource)
    estaciones = []
    #obtenemos las estaciones de bicing 
    for element in root.findall('station'):
        elements = []
        if (element.find('streetNumber').text != None):
            elements.append(element.find('street').text + " - " + element.find('streetNumber').text)
        else: elements.append(element.find('street').text)
        elements.append(element.find('slots').text)
        elements.append(element.find('bikes').text)
        lat = element.find('lat')
        long = element.find('long')
        if (lat != None and long != None): 
            elements.append(float(lat.text))
            elements.append(float(long.text))
            estaciones.append(Estacion(elements))

        
    return estaciones



def get_estacions_cogerBici(estaciones):
    return [est for est in estaciones if est.validaCogerBici()]
    

def get_estacions_aparcar(estaciones):
    return [est for est in estaciones if est.validaAparcar()]
 
 
def getDist(item):
    return item[1]
 

 
class TaulaHtml(object):
  # constructor
  def __init__(self, restaurants, estacionesHuecos, estacionesBicis):
    self.restaurants = restaurants
    self.estacionesHuecos = estacionesHuecos
    self.estacionesBicis = estacionesBicis 
 
 
 # escriu una fila de la taula, corresponent a una restaurant
  def escriu_fila_taula_html(self, restaurante, ifile, even):
    
    # ordena les llistes per aquest restaurant
    aparc = [(estac, get_distance(estac, restaurante)) for estac in self.estacionesHuecos if get_distance(estac, restaurante) <= 1000]
    salidas = [(estac,get_distance(estac, restaurante)) for estac in self.estacionesBicis if get_distance(estac, restaurante) <= 1000]
    aparc.sort(key=getDist)
    salidas.sort(key=getDist)
    # escriure l'html per columnes
    rows = max(max(1, len(aparc)), len(salidas))
    bg_color = "#ccc" if even else "#eee"

    ifile.write(""" 
    <tr style="background-color:{};border-bottom:2px solid black">
    <td rowspan="{}" style="border-bottom:2px solid black">{}<br/><br/>{}</td>
    <td rowspan="{}" style="border-bottom:2px solid black">{}<br/><br/>{}<br/><br/>{}</td>
    </tr>""".format(bg_color,rows+1, restaurante.nom, restaurante.info, rows+1, restaurante.adresa, restaurante.cp, restaurante.poblacio))
    i = 0
    while i<rows:
        ifile.write("      <tr style='background-color:{}'>\n".format(bg_color if i%2==0 else "#fff"))
      
        ifile.write("        <td>{}</td>\n".format(aparc[i][0].adresa if i < len(aparc) else ""))
        ifile.write("        <td style='text-align:center'>{}</td>\n".format(aparc[i][0].bicisFaltan if i<len(aparc) else ""))
        ifile.write("        <td style='text-align:left'>{}m</td>\n".format(round(aparc[i][1], 2) if i<len(aparc) else ""))
      
        ifile.write("        <td>{}</td>\n".format(salidas[i][0].adresa if i<len(salidas) else ""))
        ifile.write("        <td style='text-align:center'>{}</td>\n".format(salidas[i][0].bicisSobran if i<len(salidas) else ""))
        ifile.write("        <td style='text-align:left'>{}m</td>\n".format(round(salidas[i][1], 2) if i<len(salidas) else ""))
      
        ifile.write("      </tr>\n")
        i += 1
      
      
 # escriu la taula html de restaurants en el fitxer 'table.html'
  def escriu(self):
    file_name = "table.html"
    ifile = open(file_name, "w")
    ifile.write("""<!DOCTYPE html>
<html>
  <head>
    <title>Practica Python LP - Restaurants</title>
    <meta charset="UTF-8" />
    <style>
      html { font-family:Arial }
      table { border-top:2px solid black;border-bottom:2px solid black; border-left:2px solid black; border-right:2px solid black }
      th { font-size:18px;color:#fff;border-left:1px solid black;border-right:1px solid black;border-bottom:1px solid black }
      td { font-size:14px;border-left:1px solid black;border-right:1px solid black;padding:5px }
    </style>
  </head>
  <body>
    <table style="width:100%;border-collapse:collapse">
      <colgroup style="width:20%"></colgroup>
      <tr style="background-color:#65e">
        <th rowspan="2" style="padding-top:20px;padding-bottom:20px">Nom Restaurant</th>
        <th rowspan="2">Adresa</th>
        <th colspan="3">Bicings amb lloc</th>
        <th colspan="3">Bicings amb bicis</th>
      </tr>
      <tr style="background-color:#65e">
        <th style="font-size:16px">Adresa</th>
        <th style="font-size:16px">Llocs</th>
        <th style="font-size:16px">Dist</th>
        <th style="font-size:16px">Adresa</th>
        <th style="font-size:16px">Bicis</th>
        <th style="font-size:16px">Dist</th>
      </tr>
""")
    even = True
    #escribim les estacions i restaurants separats en files, cambiant el color de fons a cada fila
    for rest in self.restaurants:
      self.escriu_fila_taula_html(rest, ifile, even)
      even = not even
    ifile.write("""    </table>
  </body>
</html>""")
    ifile.close()
    webbrowser.open(file_name)
 
 
 
 

 
 #OBTENEMOS LAS ESTACIONES
estaciones = get_all_estaciones()
#Descartamos las estaciones que no tienen huecos, para no hacer el calculo de distancias innecesariamente
estacionesConSlots = get_estacions_aparcar(estaciones) 
#Descartamos las que no tienen bicis por lo mismo
estacionesConBicis = get_estacions_cogerBici(estaciones)


 
 
#CARGAMOS LOS RESTAURANTES DE DISCO 
#"['bar','Bar']"
#obtenemos los restaurantes, su informacion y las estaciones cercanas
constrain = eval(sys.argv[1])
restaurantes = get_restaurants(constrain)    

#para imprimirlo por terminal

#for r in restaurantes:
    #print r.nom
    #aparcamientos = [estac for estac in estacionesConSlots if get_distance(estac, r) <= 1000]
    #salidas = [estac for estac in estacionesConBicis if get_distance(estac, r) <= 1000]
    #print "\n\nEstaciones Con Huecos"
    #for est in aparcamientos:
    #    print "\nEstacion Con Huecos:"
    #    print est.adresa
    #print "\n\nEstaciones Con Bicis:"
    #for est in salidas:
    #    print "\nEstacion Con Bicis:"
    #    print est.adresa
    #print "----------------"
 
print constrain

# escriu html
TaulaHtml(restaurantes, estacionesConSlots, estacionesConBicis).escriu()

    
    
    
















    
    
    
    
    
