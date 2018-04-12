from xmlrpclib import ServerProxy
from os import remove
from time import sleep
from thread import start_new_thread
domainCentralServer = "http://localhost:8000"


class Cliente:
	def __init__(self, nombre = "usuario1", servidorCentral = domainCentralServer):
		self.username = nombre
		self.proxy = ServerProxy(servidorCentral)
		self.proxy.autenticarCliente(self.username)


	def listarLibros(self):
		librosXservidor = self.proxy.librosXservidor()
		servidores      = self.proxy.listaServidores()
		for aux in range(len(servidores)):
			servidor = servidores[aux]
			libros  = librosXservidor[aux]
			print("El servidor " + servidor + " posee los siguientes titulos: \n" )
			if (len(libros) == 0):
				print("Nuestro servidor no posee libros")
			else:
				for libro in libros:
					print("\t # )  " + libro)
			print




	def descargarLibro(self,name,libro):
		estaServidores = self.proxy.pedirLibro(name, libro)
		if (estaServidores):
			numServidores = len(estaServidores)
			auxBool = True
			intentos = 0
			servidorInt = 0
			aux = 0
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
					sleep(3)
			rutaDescargas = "Descargas/" + libro + ".pdf"
			downloadFile = open(rutaDescargas,'wb')
			tamfragmento = tamLibro/numServidores
			intentos = 0
			servidorInt = 0
			aux = 0
			fragmento = 1
			while(fragmento <= numServidores and auxBool):
				try:
					if (intentos < numServidores):
						if (servidorInt < 3):
							ServidorDescarga = ServerProxy(estaServidores[aux])
							paquete = ServidorDescarga.transferData(self.username, libro, tamfragmento, fragmento, fragmento==numServidores)
							downloadFile.write(paquete.data)
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
						aux = (aux + 1) % numServidores
						servidorInt = 0
					else:
						auxBool = False
				except:
					servidorInt = servidorInt + 1
					sleep(1)
			downloadFile.close()
			if (auxBool):
				print(libro + " ha sido descargado satisfactoriamente. Disfrutelo!!!")
			else:
				remove(rutaDescargas)		
				print("No se logro establecer conexion con ningun servidor de descarga.")
				print("Descarga fallida, intente mas tarde")		
		else:
			print("su requerimiento no esta disponible de momento. :(")



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
				requerimiento = raw_input("Escriba el nombre del libro: ")
				start_new_thread(self.descargarLibro,(nombre,requerimiento,))


if __name__ == '__main__':
    nickname = raw_input("Bienvenido a nuestra libreria!!! "+"\n" + " Cual es su username?: ")
    user = Cliente(nickname)
    user.inicializar(nickname)