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


from Packet import Packet, PacketClient, PacketAdmin, PacketQueue

cThreads = None
base_port = 22000

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

class Client(threading.Thread):
    Status = "status"
    Start = "start"
    Stop = "stop"

    def __init__(self, cQueue, aQueue, ip, port, cs):
        threading.Thread.__init__(self)
        self.cQueue = cQueue
        self.aQueue = aQueue
        self.ip = ip
        self.port = port
        self.cs = cs
        print("[+] Nouveau thread pour %s %s" % (self.ip, self.port, ))
    
    def run(self): 
        global cThreads, base_port
        print("Connection de %s %s" % (self.ip, self.port, ))
        #get informations about client
        try :
            info = self.cs.recv(2048)
            self.name = Packet.parse(info)["name"]
            #define port
            lport = base_port + len(cThreads) 
            self.cs.send(self.buildReq(lport))
            pAck = self.cs.recv(2048)
            pAck = Packet.parse(pAck)
            print pAck
            if pAck['code'] != 0 :
                raise Exception('Error on port attribution')
            self.lport = lport

            while True :
                    logging.debug("Client %s:%s wait for message" % (self.ip, self.port))
                    data = self.cQueue.get(block=True, timeout=None)
                    logging.debug("Client %s:%s received message" % (self.ip, self.port))
                    data = Packet.parse(data)
                    logging.debug("Client %s:%s build & send message to client" % (self.ip, self.port))
                    self.cs.send(self.buildReq(data["command"]))
                    cResp = self.cs.recv(2048)
                    cResp = Packet.parse(cResp)
                    print(cResp)
                    logging.debug("Client %s:%s build & send message to admin" % (self.ip, self.port))
                    self.aQueue.put(self.buildResp(cResp['code']))

        except Exception, e:
            logging.error(e)
            self.cs.close()
        logging.info('Client %s disconnect' % (str(self.ip)))
        del self

    @staticmethod 
    def buildReq(command):
        req = PacketClient(Packet.Request)
        req.command = command
        req.build() 
        return req.get()

    @staticmethod
    def buildResp(code) :
        resp = PacketQueue(Packet.Response)
        resp.code = code
        resp.build()
        return resp.get()


class Admin(threading.Thread):
    def __init__(self, queue, args=(), kwargs=None):
        threading.Thread.__init__(self, args=(), kwargs=None)
        self.adminSocketPath = "/tmp/ssh-manager.sock"
        self.Queue = queue

    def run(self):
        global cThreads
        self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            os.remove(self.adminSocketPath)
        except OSError:
            pass
        self.s.bind(self.adminSocketPath)
        self.s.listen(1)
        logging.debug("Wait connection on " + self.adminSocketPath)
        while 1:
            try :
                self.adminCSocket, self.cAddr = self.s.accept()
                data = self.adminCSocket.recv(1024)
                logging.debug("Data received : " + data)
                command = Packet.parse(data)['command']
                if command != '' and command != 'close':
                    self.parseCommand(command)
                else :
                    logging.debug('close socket')
            except Exception, e :
                logging.error('Erreur lors de la communication')
            finally : 
                self.adminCSocket.close()

    def parseCommand(self, data):
        try :
            logging.debug('Entering the parseCommand function')
            response = None
            name = None
            port = None
            if data == "list":
                dataArray = []
                for item in cThreads :
                    dataArray.append("%d-%s-%d" % (cThreads.index(item), item.name, item.lport))
                response = '\n'.join(dataArray)+'\n'
            else :
                cmd = data.split('_')
                if cmd[0] == 'get' :
                    command = Client.Status
                elif cmd[0] == 'start' :
                    command = Client.Start
                elif cmd[0] == 'stop' :
                    command = Client.Stop
                else :
                    raise Exception("Invalid command")

                tid = int(cmd[1])
                logging.debug("Send command to Client Controller through Queue")
                cThreads[tid].cQueue.put(self.buildReq(command))
                r = self.Queue.get(block=True, timeout=None)
                logging.debug("Response received from Client Controller")
                r = Packet.parse(r)
                logging.debug(r)
                response = str(r['code'])+'\n'
                name = cThreads[tid].name
                port = cThreads[tid].lport
            pResponse = self.buildResp(name, port, response)
            logging.debug('Send To Admin Controller')
            print(port)
            self.adminCSocket.send(pResponse)
        except Exception, e :
            logging.error(e)
            #build error Packet

    @staticmethod
    def buildReq(command):
        req = PacketQueue(Packet.Request)
        req.command = command
        req.build()
        return req.get()

    @staticmethod
    def buildResp(name, port, data):
        resp = PacketAdmin(Packet.Response)
        resp.name = name
        resp.port = port
        resp.data = data
        resp.build()
        return resp.get()
   
def main() :
    global cThreads
    aQueue = Queue.Queue()
    HOST = "0.0.0.0"
    PORT = 8000
    logging.basicConfig(level=logging.DEBUG)

    cThreads = []

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
        cThreads.append(newThread)
        newThread.start()

    AdminThd.join()
if __name__ == "__main__" :
    main()
