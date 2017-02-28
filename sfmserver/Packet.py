import logging
import json


class Packet():
    Request = 'Request'
    Response = 'Response'
    Info = 'Info'
    typeArray = ['Request','Response', 'Info']

    def __init__(self, pType):
        try :
            if pType in self.typeArray : 
                self.pType = pType 
            else :
                raise Exception('Packet type does not exists')
        except Exception, e:
            logging.error(e)
            del self
           
    def build(self):
        try :
            self.content = {
                'pType': self.pType 
            }

            buildMethod = getattr(self, 'build'+self.pType)
            return buildMethod()
        except Exception, e :
            logging.error(e)
            return False

    def get(self):
        return json.dumps(self.content)    

    @staticmethod
    def parse(data) :
        return json.loads(data)

class PacketAdmin(Packet) :

    def __init__(self, pType) :
        Packet.__init__(self, pType)
    
    def buildResponse(self):
        try :
            if self.data != None :
                self.content.update({
                    'name': self.name,
                    'port': self.port,
                    'data': self.data
                })
                return True
            else :
                raise Exception('Please fill data field')
        except Exception, e:
            logging.error(e)
            return False

    def buildRequest(self) :
        try :
            if self.command != None :
                self.content.update({
                    'command': self.command
                }) 
                return True
            else :
                raise Exception('Please fill tid and command fields')
        except Exception, e:
            logging.error(e)
            return False
    def get(self):
        return json.dumps(self.content)    



class PacketClient(Packet):
    def __init__(self, pType):
        Packet.__init__(self, pType)

    def buildRequest(self) :
        try :
            if self.command != None :
                self.content.update({
                    'command': self.command
                }) 
                return True
            else :
                raise Exception('Please fill command fields')
        except Exception, e:
            logging.error(e)
            return False
 
    def buildResponse(self) :
        try :
            if self.code != None :
                self.content.update({
                    'code': self.code
                }) 
                return True
            else :
                raise Exception('Please fill code field')
        except Exception, e:
            logging.error(e)
            return False

    def buildInfo(self) :
        try :
            if self.name != None :
                self.content.update({
                    'name': self.name     
                })
                return True
            else :
                raise Exception('Please fill port field')
        except Exception, e:
            logging.error(e)
            return False



class PacketQueue(Packet):
    def __init__(self, pType) :
        Packet.__init__(self, pType)

    def buildRequest(self) :
        try :
            if self.command != None :
                self.content.update({
                    'command': self.command
                })
                return True
            else :
                raise Exception('Please fill command fields')
        except Exception, e:
            logging.error(e)
            return False

    def buildResponse(self) :
        try :
            if self.code != None :
                self.content.update({
                    'code': self.code
                })
                return True
            else :
                raise Exception('Please fill code field')
        except Exception, e:
            logging.error(e)
            return False



