# -*- coding: utf-8 -*-

# Définition d'un serveur réseau gérant un système de chat simplifié.
# Utilise les threads pour gérer les connexions clientes en parallèle

import setup
import os
import socket
import select
import sys
import threading

HOST = setup.HOST
PORT = setup.PORT
NB_CONNEXIONS_MAX = setup.NB_CLIENTS_MAX

if os.name == "nt":  # Cas Windows
    os.system("cls")
else:
    os.system("clear")


class ThreadClient(threading.Thread):
    """Dérivation d'un objet thread pour gérer la connexion avec un client"""

    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.connexion = conn

    def run(self):
        """ L'utilité du thread est de réceptionner tous les message provenant
        d'un client particulier. Il faut donc pour cela une boucle de
        répétition perpétuelle, qui ne s'interrompt qu'à la réception
        du message "FIN".
        """

        # Dialogue avec le client
        nom = self.getName()  # Chaque thread possède un nom
        while 1:
            msgClient = self.connexion.recv(1024).decode("utf-8")
            if not msgClient or msgClient.upper() == "FIN":
                break
            message = "{}> {}".format(nom, msgClient)
            print(message)
            # On fait suivre le message à tous les autres clients
            for cle in conn_client:
                if cle != nom:  # On ne le renvoie pas à l'émetteur
                    conn_client[cle].send(message.encode("utf-8"))

        # Fermeture de la connexion
        msgServeur = "Vous êtes déconnecté."
        conn_client[nom].send(msgServeur.encode("utf-8"))
        self.connexion.close()  # On coupe la connexion côté serveur
        del conn_client[nom]    # On supprime le client dans le dictionnaire
        print("Client '{}' déconnecté.".format(nom))
        # Le thread se termine ici
        # On fait suivre le message à tous les autres clients
        msgServeurBroadcast = "Le client '{}' s'est déconnecté".format(nom)
        for cle in conn_client:
            conn_client[cle].send(msgServeurBroadcast.encode("utf-8"))
        # Solution suivante à creuser : fermeture du serveur si plus aucun
        # client connecté
        # if conn_client == {}:
        #     mySocket.close()
        # else:
        #     for cle in conn_client:
        #         conn_client[cle].send(msgServeurBroadcast.encode("utf-8"))

# class ThreadServeurCommande(threading.Thread):
#     """Objet Thread gérant l'émission des messages du serveur"""

#     def __init__(self):
#         threading.Thread.__init__(self)
#         self.serveur_lance = True

#     def run(self):
#         # Boucle d'envoi des messages : à chaque itération, le flux
#         # d'instructions s'interrompt sur input("S> "), dans l'attente
#         # d'une entrée clavier - mais le reste du programme n'est pas figé
#         # (les autres threads continuent leur travail indépendamment)
#         commande = ""
#         while 1:
#             # if "conn_client" in globals():
#             #     for conn_objet in conn_client_objets:
#             #         print(conn_objet)
#             #     for conn_thread in conn_threads_objets:
#             #         print(conn_thread)
#             if commande.upper() == "Q":
#                 msgServeurBroadcast = "Q"
#                 # S'il y a des clients connectés
#                 if "conn_client" in globals():
#                     for cle in conn_client:
#                         conn_client[cle].send(msgServeurBroadcast.encode("utf-8"))
#             #     # Arrêt des threads clients
#             #     # for conn_thread in conn_threads_objets:
#             #     #     conn_thread._stop()
#             #     # # Clôture des connexions clients
#             #     # for conn_objet in conn_client_objets:
#             #     #     conn_objet.close()
#                 break
#             commande = input("S> ")

#         # Le thread <commande serveur> se termine ici.
#         print("Le thread émission serveur s'est terminé correctement.")
#         print("serveur_lance : ", self.serveur_lance)
#         # self.stop()
#         # print("Socket AVANT : ", socket)
#         # mySocket.close()
#         # print("Socket APRES : ", socket)

#         self.serveur_lance = False
#         sys.exit()

# Initialisation du serveur - Mise en place du socket
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
liaisonOK = False
print(PORT)
try:
    mySocket.bind((HOST, PORT))
    liaisonOK = True
except socket.error:
    print("Erreur : la liaison du socket à l'adresse choisie a échoué.")
if liaisonOK is False:
    print("Nouvelle tentative en cours...")
    PORT += 1
    print(PORT)
    try:
        mySocket.bind((HOST, PORT))
    except socket.error:
        print("Erreur : la liaison du socket à l'adresse choisie a échoué.")
        sys.exit()
print("Serveur prêt, en attente de requêtes de connexion...")
mySocket.listen(NB_CONNEXIONS_MAX)

# Création d'un nouvel objet thread pour gérer l'émission des messages serveur
# th_serveur_E = ThreadServeurCommande()
# print("serveur_lance : ", th_serveur_E.serveur_lance)
# th_serveur_E.start()

# Attente et prise en charge des connexions demandées par les clientes
conn_client = {}  # Dictionnaire des connexions clients
conn_client_objets = []  # Dictionnaire des objets connexions clients
conn_threads_objets = []  # Dictionnaire des objets connexions clients
"""
Note : on place les connexions clients dans un dictionnaire plutôt que dans une
liste car on doit pouvoir ajouter ou enlever des références dans n'importe quel
ordre, de plus on dispose ainsi d'un identifiant unique pour chaque connexion
(fourni par la classe Thread(), lequel servira de clé d'accès dans le
dictionnaire.
"""
# La boucle de répétition attend constamment l'arrivée de nouvelles connexions.
# Pour chacune d'entre elles, un nouvel objet ThreadClient() est créé, lequel
# pourra s'occuper d'elle indépendamment de toutes les autres.
clients_connectes = []
serveur_lance = True
# serveur_lance = th_serveur_E.serveur_lance
while 1:
    connexion, adresse = mySocket.accept()
    conn_client_objets.append(connexion)
    # Création d'un nouvel objet thread pour gérer la connexion
    th_client = ThreadClient(connexion)
    conn_threads_objets.append(th_client)
    th_client.start()
    # On mémorise la connexion dans le Dictionnaire
    identifiant = th_client.getName()  # Identifiant du thread
    conn_client[identifiant] = connexion
    print("Client {} connecté, adresse IP {}, port {}.".format(identifiant, adresse[0], adresse[1]))
    # Dialogue avec le client
    msg = "Vous êtes connecté. Envoyez vos messages."
    connexion.send(msg.encode("utf-8"))
    # On informe les autres clients
    for cle in conn_client:
        if cle != identifiant:  # On ne le renvoie pas à l'émetteur
            msgServeurBroadcast_bienvenue = "'{} a rejoint le chat.'".format(identifiant)
            conn_client[cle].send(msgServeurBroadcast_bienvenue.encode("utf-8"))

print("A bientôt...")
sys.exit()
