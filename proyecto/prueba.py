#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf8")
import web
import json
from shapely.geometry import Point
from shapely.geometry import MultiLineString
from shapely.geometry import MultiPolygon
from shapely.geometry import Polygon
from shapely.geometry import LineString
from shapely.wkt import dumps, loads

def cargarFicheros(fname1, fname2) :
	ficheros = []

	fich = open(fname1,"r")
	lSendas = fich.readlines()
	fich.close()

	fich2 = open(fname2,"r")
	lEspacios = fich2.readlines()
	fich2.close()

	ficheros.append(lSendas)
	ficheros.append(lEspacios)
	return ficheros

def cargarIdSendas(listaSendas) :
	dicc = {}
	for linea in listaSendas :
		aux = linea.split(";")
		dicc[int(aux[0])] = aux[10]
	return dicc

aux = cargarFicheros("sendas.txt","geometry.txt")
lSendas = aux[0]
lEspacios = aux[1]
identificadoresSendas = cargarIdSendas(lSendas)

print "datos cargados\n"

urls = (
	'/sendas/', 'listaSendas',
	'/sendaId/(.*)', 'sendaId',
	'/espacios/(.*)', 'espacios',
	'/(.*)', 'basura'
)

app = web.application(urls, globals())

class listaSendas:
	def GET(self):
		web.header("Content-Type","application/json; charset=utf-8")
		print lSendas
		aux = []
		for senda in lSendas :
			aux2 = senda.split(";")
			aux.append({"id":int(aux2[0]), "name":aux2[7]})
			#aux += aux2[0] + " " + aux2[7] + "\n"

		dicc = {}

		dicc["status"] = 200
		dicc["lista"] = aux
		return json.dumps(dicc)
			

class sendaId:
	def GET(self, idSenda):
		web.header("Content-Type","application/json; charset=utf-8")
		dicc = {}
		senda_id = int(idSenda)

		if not senda_id in identificadoresSendas :
			dicc["status"] = 500
			return json.dumps(dicc)

		lista = []
		lat = "lat"
		lon = "lon"
		print identificadoresSendas
		aux = identificadoresSendas[senda_id]

		aux = "MULTILINESTRING " + aux.split("LINESTRING ")[1]
		aux = aux.split("))")[0] + "))"

		multilinea = MultiLineString(loads(aux))

		aux4 = []
		for linea in multilinea :
			aux2 = []
			for coord in list(linea.coords) :
				aux3 = {}
				aux3[lat] = float(coord[0])
				aux3[lon] = float(coord[1])
				aux2.append(aux3)
			aux4.append(aux2)
			
		dicc["status"] = 200
		dicc["geometry"] = aux4
		return json.dumps(dicc)

class espacios :
	def GET(self, espacio_id) :
		web.header("Content-Type","application/json; charset=utf-8")
		espacio_id = int(espacio_id)
		dicc = {}
	
		if espacio_id >= len(lEspacios) - 1 :
			dicc["status"] = 123
			return json.dumps(dicc)

		lista = []
		lat = "lat"
		lon = "lon"
		aux = lEspacios[espacio_id]
		aux2 = "MULTIPOLYGON (((" + aux.split("\"MULTIPOLYGON (((")[1]
		aux2 = aux2.split(")))\",")[0] + ")))"
		objeto = MultiPolygon (loads(aux2))
		
		for polygon in objeto :
			dicc2 = {}
			aux3 = []
			for coordenada in list(polygon.exterior.coords) :
				aux4 = {}
                                aux4[lat] = float(coordenada[0])
                                aux4[lon] = float(coordenada[1])
                                aux3.append(aux4)
                        dicc2["exterior"] = aux3
			aux3 = []
			for hole in list(polygon.interiors) :
				aux4 = []
				for coordenada in list(hole.coords) :
					dicc3 = {}
					dicc3[lat] = float(coordenada[0])
					dicc3[lon] = float(coordenada[1])
					aux4.append(dicc3)
				aux3.append(aux4)
			dicc2["interior"] = aux3
	
			lista.append(dicc2)
		dicc["status"] = 200	
		dicc["geometry"] = lista
		return json.dumps(dicc)

class basura:
	def GET(self, basura):
		return "<h1>Nop</h1>"

if __name__ == "__main__":
	app.run()
