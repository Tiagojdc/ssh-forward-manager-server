import socket
import os
import json
import argparse
import subprocess

from Packet import Packet, PacketAdmin
class CommandRunner():
   
    @classmethod 
    def run(cls, command):
        socketPath = "/tmp/ssh-manager.sock"
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(socketPath)
        #Build Packet
        s.send(cls.buildRequest(command))
        data = s.recv(2048) #parse Packet 
        s.close()
        data = Packet.parse(data)
        return data

    @staticmethod
    def buildRequest(command):
        p = PacketAdmin(Packet.Request)
        p.command = command
        p.build()
        return p.get()

def main ():
    parser = argparse.ArgumentParser(description='Manage ssh manager')

    parser.add_argument('command', metavar='command', type=str, 
                        help='command available list, get, stop, start, connect')
    parser.add_argument('-i', metavar='id', type=int, dest='id', required=False,
                        help='The id of machine')


    args = parser.parse_args()


    command = args.command

    if command == 'list':
        print(CommandRunner.run(command)['data']) 
    elif command == 'get' or command == 'start' or command == 'stop' or command == 'connect' :
        if args.id != None :
            hid = args.id
            if command != 'connect' :
                data = CommandRunner.run(command+'_'+str(hid))
                print '%s-%s-%s' % (data['name'], data['port'], data['data'])

            else :
                #get the port
                getStr = CommandRunner.run('get_'+str(hid))
                sshPort = getStr.split(' ')[1]
                command = "ssh %s@localhost -p %s" % (sshUser, sshPort)
                os.system(command)
                #open command
        else :
            print "Error : id not specified"
            exit(1) 

if __name__=="__main__" :
    main()
#pythonctl.py -c list
#pythonctl.py -c get -i 1
