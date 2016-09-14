# -*- coding: utf-8 -*-

# Définition d'un client réseau gérant en parallèle l'émission et la réception
# des messages (utilisation de 2 threads)

import setup
import os
import socket
import sys
from threading import Thread

HOST = setup.HOST
PORT = setup.PORT

if os.name == "nt":  # Cas Windows
    os.system("cls")
else:
    os.system("clear")


class ThreadReception(Thread):
    """Objet Thread gérant la réception des messages"""

    def __init__(self, conn):
        Thread.__init__(self)
        self.connexion = conn  # Référence du socket de connexion

    def run(self):
        # Boucle de réception des messages : à chaque itération, le flux
        # d'instructions s'interrompt sur self.connexion.recv, dans l'attente
        # d'un nouveau message - mais le reste du programme n'est pas figé
        # (les autres threads continuent leur travail indépendamment)
        while 1:
            message_recu = self.connexion.recv(1024).decode("utf-8")
            if not message_recu or message_recu == "FIN":
                break
            print("*" + message_recu + "*")
        # Le thread <réception> se termine ici.
        # print("Le thread réception s'est terminé correctement.")
        print("Taper Enter pour quitter.")
        # On force la fermeture du thread <émission>
        th_E.stop()
        self.connexion.close()


class ThreadEmission(Thread):
    """Objet Thread gérant l'émission des messages"""

    def __init__(self, conn):
        Thread.__init__(self)
        self.connexion = conn  # Référence du socket de connexion
        self.terminated = False

    def run(self):
        # Boucle d'envoi des messages : à chaque itération, le flux
        # d'instructions s'interrompt sur input("C> "), dans l'attente
        # d'une entrée clavier - mais le reste du programme n'est pas figé
        # (les autres threads continuent leur travail indépendamment)
        while 1:
            message_emis = input("C> ")
            if self.terminated:
                break
            self.connexion.send(message_emis.encode("utf-8"))
            # if message_emis == "FIN":
            #     break
        # Le thread <émission> se termine ici.
        # print("Le thread émission s'est terminé correctement.")
        # print("Client arrêté (Thread Emission). Connexion interrompue.")
        sys.exit()

    def stop(self):
        self.terminated = True

# Programme principal - Etablissement de la connexion
connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexionOK = False
print(PORT)
try:
    connexion.connect((HOST, PORT))
    connexionOK = True
except socket.error:
    print("La connexion a échoué.")
if connexionOK is False:
    connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Nouvelle tentative en cours...")
    PORT += 1
    print(PORT)
    try:
        connexion.connect((HOST, PORT))
    except socket.error:
        print("La connexion a échoué.")
        sys.exit()
print("Connexion établie avec le serveur.")

# Dialogue avec le serveur : on instancie deux threads enfants pour gérer
# indépendamment l'émission et la réception des messages
th_E = ThreadEmission(connexion)
th_R = ThreadReception(connexion)

th_E.start()
th_R.start()
