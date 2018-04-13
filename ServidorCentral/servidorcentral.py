#!/usr/bin/env python
from __future__ import print_function
import threading
import time
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer
from ast import *
archivoReporte = 'reportesCentral.txt'



############################################################################################################
# FUNCION LIBROSXSERVIDOR:
#----------------------------------------------------------------------------------------------------------
# ESTA FUNCION ES INVOCADA POR EL CLIENTE Y ARMA UNA LISTA DE LISTAS DE LOS LIBROS QUE SE ENCUENTRAN EN 
# CADA UNO DE LOS SERVIDORES QUE SE ENCUENTRAN EN CONEXION CON EL SERVIDOR CENTRAL. DE ALGUNO DE ELLOS 
# NO POSEER LIBROS, AGREGA UNA LISTA VACIA A LA LISTA DE LISTAS.
#
def librosXservidor():
	print("cargando informacion de libros...")
	listaLibros = []
	for server in servidores:
		try:
			dominioServidor = xmlrpclib.ServerProxy(server)
			libros = dominioServidor.ListaLibros()
			listaLibros.append(libros)
		except:
			listaLibros.append([])
	return listaLibros

#FUNCION DE APOYO QUE RETORNA LOS OBJETOS DE TIPO SERVIDOR QUE SE ENCUENTRAN CONECTADOS A LA LISTA
def listaServidores():
	return servidores


def actReportes(aux, servidor, libro = ""):

	file = open(archivoReporte, 'r')
	reportes    = file.readlines()
	servidorLibros   = literal_eval(reportes[0])
	clientesServidor = literal_eval(reportes[1])
	servDescargas   = literal_eval(reportes[2])
	file.close()
	if (aux == 0):
		if (not servidor in servidorLibros):
			servidorLibros[servidor] = {}
		if (not libro in servidorLibros[servidor]):
			servidorLibros[servidor][libro] = 0
		servidorLibros[servidor][libro] = servidorLibros[servidor][libro] + 1
		if not (servidor in clientesServidor):
			clientesServidor[servidor] = 0
		clientesServidor[servidor] = clientesServidor[servidor] + 1
	else:
		if not (servidor in servDescargas):
			servDescargas[servidor] = 0
		servDescargas[servidor] = servDescargas[servidor] + 1
	file = open(archivoReporte, 'w')
	file.write(str(servidorLibros)   + '\n')
	file.write(str(clientesServidor) + '\n')
	file.write(str(servDescargas)   + '\n')
	file.close()
	return "working..."

def autenticarCliente(username):
	usuarios.append(username)
	return "true"


def pedirLibro(username, libro):
	print("el usuario: " + str(username) + " esta por descargar...")
	availableServers = []
	for server in servidores:
		try:
			proxy = xmlrpclib.ServerProxy(server)
			print(proxy)
			if (proxy.ComprobarLibro(libro)):
				availableServers.append(server)
		except:
			continue
	return availableServers

def autenticarRegistro(server):
	servidores.append(server)
	return "true"


class CentralServer(threading.Thread):
	def run(self):
		server  = SimpleXMLRPCServer(("localhost", 8123))
		server.register_function(autenticarCliente,"autenticarCliente")
		server.register_function(autenticarRegistro,   "autenticarRegistro")
		server.register_function(pedirLibro,      "pedirLibro")
		server.register_function(actReportes, "actReportes")
		server.register_function(listaServidores,   "listaServidores")
		server.register_function(librosXservidor,  "librosXservidor")
		server.serve_forever()


class Informe():
	def verReportes(self, aux):
		file = open(archivoReporte, 'r')
		reportes  = file.readlines()
		data = literal_eval(reportes[int(aux)-1])
		if (aux == '1'):
			for server in data:
				print(server + ":")
				for libro in data[server]:
					print("\t ===> " + libro + ": " + str(data[server][libro]))
		else:
			for server in data:
				print("===> " + server + ": " + str(data[server]))
		print()
		file.close()

	def run(self):
		while (True):
			print("Escoja una opcion: \n 1 ==> Libros X Servidor. \n 2 ==> Usuarios X Servidor \n 3 ==> Servidores de descarga que se han caido. \n")
			aux = raw_input()
			if (not (aux == '1' or aux == '2' or aux == '3')):
				print("Opcion invalida")
				continue
			self.verReportes(aux)

if __name__ == '__main__':
	informe = Informe()
	usuarios = []
	servidores = []
	centralServer = CentralServer(name = "server")
	centralServer.start()
	informe.run()