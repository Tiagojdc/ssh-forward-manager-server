#/usr/bin/env python
# coding: utf-8 

import threading
import Queue
import socket
import logging

import settings
from Packet import Packet, PacketClient, PacketQueue

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
        self.state = ""
        self.init = False

        print("[+] Nouveau thread pour %s %s" % (self.ip, self.port, ))
    
    def run(self): 
        print("Connection de %s %s" % (self.ip, self.port, ))
        #get informations about client
        try :
            self.cs.settimeout(10)
            info = self.cs.recv(2048)

            self.name = Packet.parse(info)["name"]
            #define port
            lport = settings.base_port + len(settings.cThreads) 
            self.cs.send(self.buildReq(lport))
            pAck = self.cs.recv(2048)
            pAck = Packet.parse(pAck)
            if pAck['code'] != 0 :
                raise Exception('Error on port attribution')
            self.lport = lport
            self.init = True
            while True :
                    logging.debug("Client %s:%s wait for message" % (self.ip, self.port))
                    data = None
                    while 1 :
                        try : 
                            data = self.cQueue.get(block=True, timeout=10)
                            break
                        except Exception :
                            logging.debug("Send ping to " + self.name)
                            self.cs.send("ping")
                            pong = self.cs.recv(2048)
                            logging.debug(pong)
                            if "pong" in pong:
                                continue
                            else :
                                raise Exception("Connection error for client " + self.name)

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
        settings.cThreads.remove(self)
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



