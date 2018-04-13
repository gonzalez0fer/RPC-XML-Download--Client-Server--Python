from xmlrpclib import ServerProxy
from os import remove
from time import sleep
from thread import start_new_thread
domainCentralServer = "http://localhost:8123"


class Cliente:

############################################################################################################
# FUNCION CONSTRUCTORA:
#----------------------------------------------------------------------------------------------------------
#	DEFINE LOS ELEMENTOS MINIMOS PARA LA CREEACION DEL OBJETO CLIENTE, RECIBE UN NOMBRE EL CUAL POR DEFECTO
#	SERA USUARIO1 Y TOMA EL STRING DEL DOMINIO Y PUERTO DONDE CORRERA EL SERVIDOR CENTRAL
#

	def __init__(self, nombre = "usuario1", servidorCentral = domainCentralServer):
		self.username = nombre
		self.proxy = ServerProxy(servidorCentral)
		self.proxy.autenticarCliente(self.username)

############################################################################################################
# FUNCION INICIALIZAR:
#----------------------------------------------------------------------------------------------------------
#	FUNCION QUE INICIALIZA EL OBJETO CLIENTE, RECIBE UN NOMBRE QUE SE LE SOLICITA AL CLIENTE AL EJECUTAR
#	EL CODIGO. FUNCIONA COMO UN MENU EL CUAL GESTIONA LOS REQUERIMIENTOS DEL CLIENTE, CREANDO UN HILO 
#	EN EL MOMENTO DE SOLICITAR UN LIBRO
#
	def inicializar(self, nombre):
		while (True):
			print("Elija un opcion: "+ "\n" + "1 ==> Libros disponibles." + "\n" + "2 ==> Bajar libro.")
			aux = raw_input()
			if (aux != '1' and aux != '2' and aux !='3'):
				print("Opcion invalida, intente de nuevo.")
				continue
			if (aux == '1'):
				self.listarLibros()
			elif(aux == '2'):
				requerimiento = raw_input("Que libro desea?: \n")
				start_new_thread(self.descargarLibro,(nombre,requerimiento,))


############################################################################################################
# FUNCION LISTAR LIBROS:
#----------------------------------------------------------------------------------------------------------
#	ESTA FUNCION LE SOLICITA AL SERVIDOR CENTRAL LA LISTA DE SERVIDORES CONECTADOS Y PARA CADA UNO DE
#	ESTOS HACE LA SOLICITUD DE LOS LIBROS QUE POSEEN Y LOS VA MOSTRANDO AL CLIENTE
#  
	def listarLibros(self):
		servidores      = self.proxy.listaServidores()		
		librosXservidor = self.proxy.librosXservidor()
		tam = len(servidores)
		for aux in range(tam):
			servidor = servidores[aux]
			print("El servidor " + servidor + " posee los siguientes titulos: \n" )
			libros  = librosXservidor[aux]			
			if (len(libros) == 0):
				print("Nuestro servidor no posee libros")
			else:
				for libro in libros:
					print("# )  " + libro)
			


############################################################################################################
# FUNCION DESCARGAR LIBROS:
#----------------------------------------------------------------------------------------------------------
#	ESTA FUNCION RECIBE EL NOMBRE DEL USUARIO SOLICITANTE Y EL LIBRO A DESCARGAR DESDE LA FUNCION DE 
#	INICIALIZACION. SE ENCARGA DE ENVIAR AMBOS DATOS AL SERVIDOR CENTRAL PARA QUE ESTE DETERMINE SI
#	EL LIBRO SE ENCUENTRA EN ALGUNO D LOS SERVIDORES, SI ESTA DISPONIBLE INICIA LA DESCARGA DEL MISMO
#	DESDE EL SERVIDOR QUE LO TIENE. DE NO TENER ACCESO A LOS SERVIDORES, LO NOTIFICA OPORTUNAMENTE AL
# 	USUARIO.
#  

	def descargarLibro(self,name,libro):
		estaServidores = self.proxy.pedirLibro(name, libro)
		if (estaServidores):
			intentos = 0
			servidorInt = 0
			aux = 0
			numServidores = len(estaServidores)
			auxBool = True

			print("\n En disponibilidad inmediata: " + libro )

			while(auxBool):
				try:
					if (intentos < numServidores):
						if (servidorInt < 2):
							ServidorDescarga = ServerProxy(estaServidores[aux])
							tamLibro = ServidorDescarga.tamLibro(libro)
							break
						else:
							intentos = intentos + 1
							try:
								self.proxy.actReportes(2,estaServidores[aux])
							except:
								print("El servidor central esta caido o fuera de alcance.")
							print("El servidor" + estaServidores[aux] + " esta fuera de linea o no es alcanzable.")
						aux = (aux + 1) % numServidores
						servidorInt = 0
					else:
						auxBool = False
				except:
					servidorInt = servidorInt + 1
					sleep(4)
			rutaDescargas = "Descargas/" + libro + ".pdf"
			ArchivoDescarga = open(rutaDescargas,'wb')
			tamfragmento = tamLibro/numServidores
			intentos = 0
			servidorInt = 0
			aux = 0
			fragmento = 1
			while(fragmento <= numServidores and auxBool):
				sleep(3);
				try:
					if (intentos < numServidores):
						if (servidorInt < 3):
							ServidorDescarga = ServerProxy(estaServidores[aux])
							paquete = ServidorDescarga.bajarDatos(self.username, libro, tamfragmento, fragmento, fragmento==numServidores)
							ArchivoDescarga.write(paquete.data)
							ServidorDescarga.actReportes(0,self.username, libro)
							ServidorDescarga.actReportes(1,self.username, libro)
							fragmento = fragmento + 1
						else:
							intentos = intentos + 1
							try:
								self.proxy.actReportes(2,estaServidores[aux])
							except:
								print("El servidor central esta caido o fuera de alcance.")
							print("El servidor" + estaServidores[aux] + " esta fuera de linea o no es alcanzable.")
						servidorInt = 0
						aux = (aux + 1) % numServidores
						
					else:
						auxBool = False
				except:
					servidorInt = servidorInt + 1
					sleep(2)
			ArchivoDescarga.close()
			if (auxBool):
				print(libro + " ha sido descargado satisfactoriamente. Disfrutelo!!!")
			else:
				print("No se logro establecer conexion con ningun servidor de descarga. \n Descarga fallida, intente mas tarde")
				remove(rutaDescargas)		
				
		else:
			print("su requerimiento no esta disponible de momento. :(")

############################################################################################################
#MAIN:
#----------------------------------------------------------------------------------------------------------
#	HACE LOS LLAMADOS DE LAS FUNCIONES PRIMORDIALES
if __name__ == '__main__':
    nickname = raw_input("Bienvenido a nuestra libreria!!! "+"\n" + " Cual es su username?: ")
    user = Cliente(nickname)
    user.inicializar(nickname)