#/usr/bin/env python
# coding: utf-8 

import logging
import threading
import socket
import Queue
import os

import settings
from Packet import Packet, PacketQueue, PacketAdmin
from Client import Client
class Admin(threading.Thread):
    def __init__(self, queue, args=(), kwargs=None):
        threading.Thread.__init__(self, args=(), kwargs=None)
        self.adminSocketPath = "/tmp/ssh-manager.sock"
        self.Queue = queue

    def run(self):
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
                self.adminCSocket.settimeout(10)
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
                for item in settings.cThreads :
                    if item.init :
                        dataArray.append("ID : %d\n\t- Name : %s\n\t- Port : %d" % (settings.cThreads.index(item), item.name, item.lport))
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
                if settings.cThreads[tid].init : 
                    settings.cThreads[tid].cQueue.put(self.buildReq(command))
                    r = self.Queue.get(block=True, timeout=10)
                    logging.debug("Response received from Client Controller")
                    r = Packet.parse(r)
                    logging.debug(r)
                    response = str(r['code'])+'\n'
                    name = settings.cThreads[tid].name
                    port = settings.cThreads[tid].lport
                else :
                   name = "error"
                   port = 0
                   response = 0
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
 
