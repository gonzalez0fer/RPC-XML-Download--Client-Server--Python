#!/usr/bin/env python
from __future__ import print_function
import threading
import time
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer
from ast import *

nameFile = 'reportesCentral.txt'
messages = [ "1. Libros solicitados por servidor de descarga.",
			 "2. Numero de clientes atendidos por servidor de descarga.",
			 "3. Servidores de descarga que se han caido." ]

def autenticarCliente(username):
	# REGION CRITICA
	usuarios.append(username)
	return "ok"

def registerServer(server):
	# REGION CRITICA
	servidores.append(server)
	return "ok"

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


def actReportes(option, server, book = ""):

	file = open(nameFile, 'r')
	reportes    = file.readlines()
	serverBooks   = literal_eval(reportes[0])
	serverClients = literal_eval(reportes[1])
	downServers   = literal_eval(reportes[2])
	file.close()
	if (option == 0):
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
	return "ACK"

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


# Clase del servidor Central que escucha las peticiones
# (con hilos)
class CentralServer(threading.Thread):
	def run(self):
		server  = SimpleXMLRPCServer(("localhost", 8000))
		server.register_function(autenticarCliente,"autenticarCliente")
		server.register_function(registerServer,   "registerServer")
		server.register_function(pedirLibro,      "pedirLibro")
		server.register_function(actReportes, "actReportes")
		server.register_function(listaServidores,   "listaServidores")
		server.register_function(librosXservidor,  "librosXservidor")
		server.serve_forever()


class Informe():
	# Muestra las estadisticas segun la opcion elegida
	def verReportes(self, option):
		file = open(nameFile, 'r')
		reportes  = file.readlines()
		data = literal_eval(reportes[int(option)-1])
		if (option == '1'):
			for server in data:
				print(server + ":")
				for book in data[server]:
					print("\t" + book + ": " + str(data[server][book]))
		else:
			for server in data:
				print(server + ": " + str(data[server]))
		print()
		file.close()

	# Interaccion del servidor central
	def run(self):
		while (True):
			print("Elija un opcion: \n 1 ==> Libros X Servidor. \n 2 ==> Usuarios X Servidor \n 3 ==> Servidores de descarga que se han caido. \n")
			option = raw_input()
			if (not (option == '1' or option == '2' or option == '3')):
				print("Opcion invalida")
				continue
			self.verReportes(option)

if __name__ == '__main__':
	informe = Informe()
	usuarios = []
	servidores = []
	centralServer = CentralServer(name = "server")
	centralServer.start()
	informe.run()