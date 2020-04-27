from multiprocessing.sharedctypes import Array
from random import choice
from time import sleep
import multiprocessing
from socket import *
from signal import *
from os import *

Clients = [("Osman", 1299), ("Orhan", 1326), ("Murad", 1359), ("Bayezid", 1389), ("Mehmed", 1413), ("Selim", 1512), ("Suleiman", 1520), ("Ahmed", 1603), ("Mustafa", 1607),
           ("Ibrahim", 1640), ("Mahmud", 1730), ("Abdulhamid", 1774), ("Abdulmejid", 1839), ("Abdulaziz", 1861)]

Messages = Array ("c", b" " * 100, lock = multiprocessing.Lock ())
MessagesUDP = Array ("c", b" " * 100, lock = multiprocessing.Lock ())
PIDs = Array ("c", b"." + b" " * 96, lock = multiprocessing.Lock ())
PIDUDPs = Array ("c", b"." + b" " * 96, lock = multiprocessing.Lock ())

#######################################################################################################

class Callable:
    def __init__ (self, Client): self.Client = Client
    def __call__ (self, Signal, Frame):
        global Messages
        self.Client.send (bytes (str (Messages.value), "utf-8"))

class CallableUDP:
    def __init__ (self, Socket, Address):
        self.Socket = Socket
        self.Address = Address
    def __call__ (self, Signal, Frame):
        global MessagesUDP
        self.Socket.sendto (bytes (str (MessagesUDP.value), "utf-8"), self.Address)

#######################################################################################################

def Parse (PIDs):
    String = str (PIDs.value)
    Start = 2
    Dot = String.find (".", Start)
    List = []
    while Dot > 0:
        if Dot - Start > 1: List.append (String [Start : Dot])
        Start = Dot + 1
        Dot = String.find (".", Start)
    return List

def Communicate (Index, Buffer):
    global PIDs
    with socket (AF_INET, SOCK_STREAM) as Delegate:
        Delegate.bind ((gethostname (), Clients [Index][1]))
        Delegate.listen ()
        Client, Address = Delegate.accept ()
        Handler = Callable (Client)
        signal (SIGTERM, Handler)
        while True:
            Message = Client.recv (1024).decode ()
            if Message:
                Buffer.value = bytes (Message, "utf-8")
                print ("TCP: " + str (Buffer.value, "utf-8"))
                for I in Parse (PIDs): kill (int (I), SIGTERM)

def CommunicateUDP (Index, Buffer):
    global PIDUDPs
    with socket (AF_INET, SOCK_DGRAM) as Delegate:
        Delegate.bind ((gethostname (), Clients [Index][1]))
        Data, Address = Delegate.recvfrom (1024)
        Handler = CallableUDP (Delegate, Address)
        signal (SIGTERM, Handler)
        while True:
            Data, Address = Delegate.recvfrom (1024)
            Buffer.value = Data
            print ("UDP: " + str (Buffer.value, "utf-8"))
            for I in Parse (PIDUDPs): kill (int (I), SIGTERM)

#######################################################################################################

def Main ():
    Index = 0
    global PIDs
    global PIDUDPs
    Server = socket (AF_INET, SOCK_STREAM)
    Server.bind ((gethostname (), 1526))
    Server.listen (14)
    Lock = multiprocessing.Lock ()
    while True:
        ClientSocket, Address = Server.accept ()
        ClientSocket.send (bytes (Clients [Index][0] + " " + str (Clients [Index][1]), "utf-8"))
        Communication = multiprocessing.Process (target = Communicate, args = (Index, Messages))
        Communication.start ()
        Tempor = str (PIDs.value)
        Tempor = Tempor [2 : Tempor.rfind (".") + 1]
        Tempor = str (Communication.pid) + "." + Tempor + (89 - len (Tempor)) * " "
        PIDs.value = bytes (Tempor, "utf-8")
        CommunicationUDP = multiprocessing.Process (target = CommunicateUDP, args = (Index, MessagesUDP))
        CommunicationUDP.start ()
        Tempor = str (PIDUDPs.value)
        Tempor = Tempor [2 : Tempor.rfind (".") + 1]
        Tempor = str (CommunicationUDP.pid) + "." + Tempor + (89 - len (Tempor)) * " "
        PIDUDPs.value = bytes (Tempor, "utf-8")
        Index += 1

if __name__ == "__main__": Main ()