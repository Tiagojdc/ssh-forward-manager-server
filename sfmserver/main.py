#!/usr/bin/env python
# coding: utf-8 

import socket
import threading
import Queue
import time
import os
import sys
import logging
import json

import settings

from Packet import Packet, PacketClient, PacketAdmin, PacketQueue
from Client import Client
from Admin import Admin

settings.init()

def parseRetCode(code):

    if code == 0 :
        pass
    elif code == 1 :
        pass
    elif code == 2 :
        pass
    elif code == 3 :
        pass
    else :
        return "Error occured"
class ConnectionState():
    CONNECTED = "Connected"
    DISCONNECTED = "Disconnected"
    CHECKING = "Checking"

  
def main() :
    aQueue = Queue.Queue()
    HOST = "0.0.0.0"
    PORT = 8000
    logging.basicConfig(level=logging.DEBUG)

    AdminThd = Admin(aQueue)
    AdminThd.daemon = True
    AdminThd.start()

    tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcpsock.bind((HOST,PORT))
    tcpsock.listen(10)

    print( "En écoute...")
    while True:
        (cs, (ip, port)) = tcpsock.accept()
        cQueue = Queue.Queue()
        newThread = Client(cQueue, aQueue, ip, port, cs)
        newThread.daemon = True
        settings.cThreads.append(newThread)
        newThread.start()

    AdminThd.join()
if __name__ == "__main__" :
    main()
