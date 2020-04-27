from time import strftime, gmtime
from time import sleep
import multiprocessing
from os import getpid
import tkinter as Tk
from socket import *
from signal import *

class Chat (Tk.Tk):
    def __init__ (self):
        super ().__init__ ()
        self.ConfigureWindow ()
        self.ConfigureSocket ()

    def ConfigureWindow (self):
        self.Counter = 0
        self.Name = ""
        self.Port = 0
        self.MessagesCanvas = Tk.Canvas (self)
        self.MessagesFrame = Tk.Frame (self.MessagesCanvas)
        self.TextFrame = Tk.Frame (self)
        self.Scrollbar = Tk.Scrollbar (self.MessagesCanvas, orient = "vertical", command = self.MessagesCanvas.yview)
        self.MessagesCanvas.configure (yscrollcommand = self.Scrollbar.set)
        self.title ("Chat")
        self.geometry ("800x600")
        self.MessageText = Tk.Text (self.TextFrame, height = 3, background = "white", foreground = "black")
        self.MessagesCanvas.pack (side = Tk.TOP, fill = Tk.BOTH, expand = 1)
        self.Scrollbar.pack (side = Tk.RIGHT, fill = Tk.Y)
        self.CanvasFrame = self.MessagesCanvas.create_window ((0, 0), window = self.MessagesFrame, anchor = "n")
        self.MessageText.pack (side = Tk.BOTTOM, fill = Tk.X)
        self.TextFrame.pack (side = Tk.BOTTOM, fill = Tk.X)
        self.MessageText.focus_set ()
        Title = Tk.Label (self.MessagesFrame, text = (strftime ("%d.%m.%Y %H:%M", gmtime ())), background = "black", foreground = "white", pady = 10)
        Title.pack (side = Tk.TOP, fill = Tk.X)
        self.bind ("<Return>", self.Get)
        self.bind ("<Configure>", self.FrameConfigure)
        self.bind_all ("<MouseWheel>", self.MouseScroll)
        self.bind_all ("<Button-4>", self.MouseScroll)
        self.bind_all ("<Button-5>", self.MouseScroll)
        self.MessagesCanvas.bind ("<Configure>", self.MessagesWidth)

#######################################################################################################

    def ConfigureSocket (self):
        try:
            self.Socket = socket (AF_INET, SOCK_STREAM)
            self.Socket.connect ((gethostname (), 1526))
            Data = self.Socket.recv (4096).decode ("utf-8")
            self.Name = Data [0 : Data.find (" ")]
            self.Port = int (Data [Data.find (" ") + 1 :])
            self.Socket.close ()
            sleep (3)
            self.Socket = socket (AF_INET, SOCK_STREAM)
            self.Socket.connect ((gethostname (), self.Port))
            self.Communication = multiprocessing.Process (target = self.Communicate)
            self.Communication.start ()
            self.SocketUDP = socket (AF_INET, SOCK_DGRAM)
            self.CommunicationUDP = multiprocessing.Process (target = self.CommunicateUDP)
            self.CommunicationUDP.start ()
            self.SocketUDP.sendto (bytes ("\/", "utf-8"), ("Devlet", self.Port))

        except ConnectionRefusedError as Error:
            print ("Włącz Serwer!")
            exit (30)

#######################################################################################################

    def Communicate (self):
        while True:
            Data = self.Socket.recv (4096).decode ("utf-8")
            # if Data: self.Add (Data)
            print (Data)

    def CommunicateUDP (self):
        while True:
            Buffer, Address = self.SocketUDP.recvfrom (1024)
            # self.Add (str (Buffer, "utf-8"))
            print (str (Buffer, "utf-8"))

#######################################################################################################

    def Get (self, Event = None):
        Text = self.MessageText.get (1.0, Tk.END).strip ()
        Description = strftime ("%H:%M:%S ", gmtime ()) + "(" + self.Name + ")> "
        if Text [0] == "T":
            self.Socket.send (bytes (Description + Text [1 :], "utf-8"))
            self.Add (Description + Text [1 :])
        elif Text [0] == "U":
            self.SocketUDP.sendto (bytes (Description + Text [1 :], "utf-8"), ("Devlet", self.Port))
            self.Add (Description + Text [1 :])
        else: print ("TCP | UDP")
        self.MessageText.delete (1.0, Tk.END)

    def Add (self, Text):
        if len (Text):
            New = Tk.Label (self.MessagesFrame, text = Text, pady = 10, background = ["lightgrey", "darkgrey"][self.Counter % 2])
            New.pack (side = Tk.TOP, fill = Tk.X)
            self.Counter += 1

    def FrameConfigure (self, Event = None):
        self.MessagesCanvas.configure (scrollregion = self.MessagesCanvas.bbox ("all"))

    def MessagesWidth (self, Event):
        self.MessagesCanvas.itemconfig (self.CanvasFrame, width = Event.width)

    def MouseScroll (self, Event):
        if Event.delta:
            self.MessagesCanvas.yview_scroll (int (-1 * Event.delta / 120), "units")
        else:
            if Event.num == 5: Move = 1
            else: Move = -1
            self.MessagesCanvas.yview_scroll (Move, "units")

#######################################################################################################

if __name__ == "__main__":
    Application = Chat ()
    Application.mainloop ()