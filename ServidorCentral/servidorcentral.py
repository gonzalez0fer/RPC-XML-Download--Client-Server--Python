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

# FUNCION DE APOYO QUE RETORNA LOS OBJETOS 
# DE TIPO SERVIDOR QUE SE ENCUENTRAN 
# CONECTADOS A LA LISTA.
def listaServidores():
	return servidores

############################################################################################################
# FUNCION ACTREPORTES:
#----------------------------------------------------------------------------------------------------------	
#	FUNCION QUE SE ENCARGA DE LA ACTUALIZACION DE LOS REPORTES ESTADITICOS, DICHOS REPORTES SE ALMACENAN
#	EN UN ARCHIVO .TXT QUE POSEE TRES DICCIONARION EN LOS CUALES SE ALMACENAN, NUMERO DE DESCARGAS DE TITULOS 
# 	POR SERVIDOR, CLIENTES QUE HAN CONSULTADO CADA SERVIDOR Y FINALMENTE CUANTAS VECES SE HA CAIDO CADA 
# 	SERVIDOR DESDE LA ENTRADA EN FUNCIONAMIENTO.
#  
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

# FUNCION DE APOYO QUE ALMACENA A LOS
# USUARIOS EN UNA LISTA DEL OBJETO
# TIPO SERVIDOR CENTRAL.
def autenticarCliente(username):
	usuarios.append(username)
	return "true"

############################################################################################################
# FUNCION PEDIRLIBRO:
#----------------------------------------------------------------------------------------------------------
#	FUNCION EN LA CUAL SE LE RETORNA AL USUARIO LA LISTA DE LOS SERVIDORES QUE TIENEN AL LIBRO QUE 
#	DESEA DESCARGAR
#
def pedirLibro(username, libro):
	print("el usuario: " + str(username) + " esta por descargar el libro "+ str(libro)+"...")
	disponibleEn = []
	for server in servidores:
		try:
			servidor = xmlrpclib.ServerProxy(server)
			print(servidor)
			if (servidor.ComprobarLibro(libro)):
				disponibleEn.append(server)
		except:
			continue
	return disponibleEn

# FUNCION DE APOYO QUE ALMACENA A LOS
# SERVIDORES EN UNA LISTA DEL OBJETO
# TIPO SERVIDOR CENTRAL.
def autenticarRegistro(server):
	servidores.append(server)
	return "true"

#CLASE QUE PERMITE HILAR LAS FUNCIONALIDADES DEL SERVIDOR CENTRAL
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


class AdmServid():

############################################################################################################
# FUNCION VERREPORTES:
#----------------------------------------------------------------------------------------------------------	
#	FUNCION QUE RETORNA AL ADMINISTRADOR DEL SERVIDOR LA INFORMACION RELATIVA A LAS DESCARGAS QUE SE HAN
#	GESTIONADO POR MEDIO DE EL, TOMA UNA OPCION DEL ADMIN Y CONSULTA EN EL ARCHIVO QUE ALMACENA LOS 
# 	DICCIONARIOS CON LA INFORMACION REQUERIDA.
#
	def verReportes(self, aux):
		file = open(archivoReporte, 'r')
		reportes  = file.readlines()
		info = literal_eval(reportes[int(aux)-1])
		if (aux == '1'):
			for servidor in info:
				print(servidor + ":")
				for libro in info[servidor]:
					print("\t ===> " + libro + ": " + str(info[servidor][libro]))
		else:
			for servidor in info:
				print("===> " + servidor + ": " + str(info[servidor]))
		file.close()

############################################################################################################
# FUNCION INICIALIZAR:
#----------------------------------------------------------------------------------------------------------
#	FUNCION QUE INICIALIZA EL OBJETO ADMSERV, FUNCIONA COMO UN MENU EL CUAL GESTIONA LOS REQUERIMIENTOS DEL 
#	ADMINISTRADOR DEL SERVIDOR CENTRAL PARA VER LOS REPORTES ESTADISTICOS DE LAS DIVERSAS DESCARGAS.
#
	def inicializar(self):
		while (True):
			print("Escoja una opcion: \n 1 ==> Libros X Servidor. \n 2 ==> Usuarios X Servidor \n 3 ==> Servidores de descarga que se han caido. \n")
			aux = raw_input()
			if (not (aux == '1' or aux == '2' or aux == '3')):
				print("Opcion invalida")
				continue
			self.verReportes(aux)

############################################################################################################
#MAIN:
#----------------------------------------------------------------------------------------------------------
#	HACE LOS LLAMADOS DE LAS FUNCIONES PRIMORDIALES.  CREA EL ELEMENTO DEL TIPO ADMINSER PARA VER LOS
# 	DIVERSOS REPORTES, AUNADO A ESTO DE TIPO SERVIDORCENTRAL Y LLAMA A LAS FUNCIONES DE INICIALIZACION 
# 	CORRESPONDIENTES.
#
if __name__ == '__main__':
	adminSer = AdmServid()
	usuarios = []
	servidores = []
	centralServer = CentralServer(name = "server")
	centralServer.start()
	adminSer.inicializar()