#!/usr/bin/env python
from __future__ import print_function
import threading
import time
from xmlrpclib import ServerProxy, Binary
from SimpleXMLRPCServer import SimpleXMLRPCServer,SimpleXMLRPCRequestHandler
import SocketServer
from os import stat,walk
from ast import literal_eval
domainCentralServer = "http://localhost:8123"
domainServer = "http://localhost:8131"
archivoReportes = "reportes.txt"
activas = {}

############################################################################################################
# FUNCION BAJARDATOS:
#----------------------------------------------------------------------------------------------------------	
#	FUNCION QUE RECIBE NOMBRE DEL USUARIO A REALIZAR LA DECARGA, LA DIVISION DE LA DATA Y UN IDENTIFICADOR
#	DEL FRAGMENTO DE DATO, Y UN BOOLEANO QUE LE INDICA CUANDO PARAR. ABRE LA RUTA DEL LIBRO Y RETORNA LA 
# 	DATA EN BINARIO PARA SU TRANSFERENCIA.
#
def bajarDatos(username, libro, tamfragmento, fragmento, centinela):
	if (not username in activas):
		activas[username] = []
	activas[username].append(libro)	
	print("Enviando libro...")
	ruta = "Repositorio/" + libro + ".pdf"
	file = open(ruta, "rb")
	file.read(tamfragmento * (fragmento - 1))
	if (centinela):
		aux = file.read()
	else:
		aux = file.read(tamfragmento)
	file.close()
	return Binary(aux)

############################################################################################################
# FUNCION ACTREPORTES:
#----------------------------------------------------------------------------------------------------------	
#	FUNCION QUE SE ENCARGA DE LA ACTUALIZACION DE LOS REPORTES ESTADITICOS, DICHOS REPORTES SE ALMACENAN
#	EN UN ARCHIVO .TXT QUE POSEE TRES DICCIONARION EN LOS CUALES SE ALMACENAN, NUMERO DE DESCARGAS POR
#	USUARIO, Y NUMERO DE VECES QUE HA SIDO DESCARGADO CADA LIBRO. 
#	LA FUNCIONALIDAD DE DESCARGA EN CURSO ***NO ESTA IMPLEMENTADA***
#  
def actReportes(eleccion, username, tituloLibro):
	file = open(archivoReportes, 'r')
	reportes = file.readlines()
	libros      = literal_eval(reportes[0])
	usuarios    = literal_eval(reportes[1])
	file.close()
	if (eleccion == 0):
		activas[username].remove(tituloLibro)
		if (not activas[username]):
			del activas[username]
		if not (tituloLibro in libros):
			libros[tituloLibro] = 0
		libros[tituloLibro] = libros[tituloLibro] + 1
		try:
			centralServer = ServerProxy(domainCentralServer)
			centralServer.actReportes(0, domainServer, tituloLibro)
		except:
			print("El servidor central esta caido o no es alcanzable.")
	else:
		if not (username in usuarios):
			usuarios[username] = 0
		usuarios[username] = usuarios[username] + 1
	file = open(archivoReportes, 'w')
	file.write(str(libros)   + '\n')
	file.write(str(usuarios) + '\n')
	file.close()
	return "works..."

def ListaLibros():
	return server.libros

############################################################################################################
# FUNCION CARGARLISTALIBROS:
#----------------------------------------------------------------------------------------------------------
#	FUNCION QUE SE EJECUTA AL INICIALIZAR EL OBJETO SERVIDOR LA CUAL SE ENCARGA DE ELABORAR UNA LISTA DE
#	TODOS LOS LIBROS DISPONIBLES EN EL DIRECTORIO CON LA RUTA PREDETERMIANDA.
#

def cargarListaLibros():
	libros = []
	for root,dir,file in walk("Repositorio"):
		for aux in file:
			libros.append(aux.split('.')[0])
	return libros

############################################################################################################
# FUNCION TAMLIBRO:
#----------------------------------------------------------------------------------------------------------
# 	FUNCION QUE CALCULA Y RETORNA EL TAMANO DE UN LIBBRO A PARTIR DE LA CONSTRUCCION DE SU RUTA ENTERA
#	PREDEFINIDA, PARA ELLO SOLO RECIBE EL NOMBRE DEL LIBRO A CALCULAR.
#
def tamLibro(libro):
	ruta = "Repositorio/" + libro + ".pdf"
	print(ruta)
	return stat(ruta).st_size

############################################################################################################
# FUNCION COMPROBARLIBRO:
#----------------------------------------------------------------------------------------------------------
# 	FUNCION QUE COMPRUEBA LA DISPONIBILIDAD DE UN LIBRO EN EL OBJETO SERVIDOR. SI ESTA DISPONIBLE EN 
#	SU LISTA DE LIBROS, REGRESARA UN BOOLEANO QUE ASI LO INDIQUE, PARA ELLO RECIBE EL NOMBRE DEL LIBRO
#
def ComprobarLibro(libro):
	print("comprobando libro...")
	for aux in server.libros:
		if (aux == libro):
			return True
	return False


class Server:
############################################################################################################
# FUNCION CONSTRUCTORA:
#----------------------------------------------------------------------------------------------------------
#	DEFINE LOS ELEMENTOS MINIMOS PARA LA CREEACION DEL OBJETO SERVIDOR, RECIBE UN DOMINIO PROPIO EL CUAL
# 	REPOSA EN UNA VARIABLE DE ENTORNO Y RECIBE EL DOMINIO DEL SERVIDOR CENTRAL AL CUAL HARA SU CONEXION
# 	EN EL MISMO MOMENTO DE SU CREACION.
#
	def __init__(self, central = domainCentralServer, server = domainServer):
		self.proxy = ServerProxy(domainCentralServer)
		self.proxy.autenticarRegistro(domainServer)
		self.downloadServer = DownloadServer()
		self.downloadServer.start()
		self.libros = cargarListaLibros()

############################################################################################################
# FUNCION VERREPORTES:
#----------------------------------------------------------------------------------------------------------	
#	FUNCION QUE RETORNA AL ADMINISTRADOR DEL SERVIDOR LA INFORMACION RELATIVA A LAS DESCARGAS QUE SE HAN
#	GESTIONADO POR MEDIO DE EL, TOMA UNA OPCION DEL ADMIN Y CONSULTA EN EL ARCHIVO QUE ALMACENA LOS 
# 	DICCIONARIOS CON LA INFORMACION REQUERIDA.
#
	def verReportes(self, eleccion):
		if (eleccion == '1'):
			for usuario in activas:
				print(usuario)
				for libro in activas[usuario]:
					print("\t" + libro)
		else:
			file = open(archivoReportes, 'r')
			reportes  = file.readlines()
			informacion = literal_eval(reportes[int(eleccion)-2])
			lineas = [(informacion[nombre], nombre) for nombre in informacion]
			for val, nombre in lineas:
				print("\t ==> " + nombre + "= " + str(val))
			print()
			file.close()

############################################################################################################
# FUNCION INICIALIZAR:
#----------------------------------------------------------------------------------------------------------
#	FUNCION QUE INICIALIZA EL OBJETO SERVER, FUNCIONA COMO UN MENU EL CUAL GESTIONA LOS REQUERIMIENTOS DEL 
#	ADMINISTRADOR DEL SERVIDOR PARA VER LOS REPORTES ESTADISTICOS DE LAS DIVERSAS DESCARGAS.
#
	def inicializar(self):
		while (True):
			print("Elija un opcion: \n 1 ==> Libros en proceso. \n 2 ==> Libros bajados. \n 3 ==> Reportes de usuarios.\n")
			eleccion = raw_input()
			if ( not (eleccion == '1' or eleccion == '2' or eleccion == '3')):
				print("Opcion invalida, intente de nuevo.")
				continue
			if  (eleccion == '1'):
				self.verReportes(eleccion)
			else:
				self.verReportes(eleccion)

#CLASE QUE PERMITE HILAR LAS FUNCIONALIDADES DEL SERVIDOR DE DESCARGA
class DownloadServer(threading.Thread):
	def run(self):
		server = SimpleXMLRPCServer(("localhost", 8131))
		server.register_function(ComprobarLibro,    "ComprobarLibro")
		server.register_function(bajarDatos, "bajarDatos")
		server.register_function(ListaLibros,    "ListaLibros")
		server.register_function(tamLibro,     "tamLibro")
		server.register_function(actReportes, "actReportes")
		server.serve_forever()

    
############################################################################################################
#MAIN:
#----------------------------------------------------------------------------------------------------------
#	HACE LOS LLAMADOS DE LAS FUNCIONES PRIMORDIALES.  CREA EL ELEMENTO DEL TIPO SERVIDOR PARA VER LOS
# 	DIVERSOS REPORTES, Y LLAMA A LAS FUNCIONES DE INICIALIZACION CORRESPONDIENTES.
#
if __name__ == '__main__':
	server = Server()
	server.inicializar()