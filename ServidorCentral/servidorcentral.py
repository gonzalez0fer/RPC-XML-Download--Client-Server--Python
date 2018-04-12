#!/usr/bin/env python
from __future__ import print_function
import threading
import time
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer
from ast import *

nameFile = 'reportesCentral.txt'




def librosXservidor():
	print("Client is in serversBooks")
	listaLibros = []
	for server in servidores:
		try:
			proxy = xmlrpclib.ServerProxy(server)
			libros = proxy.ListaLibros()
			listaLibros.append(libros)
		except:
			listaLibros.append([])
	return listaLibros

def listaServidores():
	return servidores


def actReportes(aux, server, book = ""):

	file = open(nameFile, 'r')
	reportes    = file.readlines()
	serverBooks   = literal_eval(reportes[0])
	serverClients = literal_eval(reportes[1])
	downServers   = literal_eval(reportes[2])
	file.close()
	if (aux == 0):
		if (not server in serverBooks):
			serverBooks[server] = {}
		if (not book in serverBooks[server]):
			serverBooks[server][book] = 0
		serverBooks[server][book] = serverBooks[server][book] + 1
		if not (server in serverClients):
			serverClients[server] = 0
		serverClients[server] = serverClients[server] + 1
	else:
		if not (server in downServers):
			downServers[server] = 0
		downServers[server] = downServers[server] + 1
	file = open(nameFile, 'w')
	file.write(str(serverBooks)   + '\n')
	file.write(str(serverClients) + '\n')
	file.write(str(downServers)   + '\n')
	file.close()
	return "ok"

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
		file = open(nameFile, 'r')
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