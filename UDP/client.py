import socket
import hashlib
from enum import Enum
from File import File

class RxResponse(Enum):
   NEXT_PACKET = 0
   RESEND      = 1
   FILE_ERROR  = 2
   ALL_DONE    = 3

class SysState(Enum):
   CMD_INPUT    = 0
   SENDING_FILE = 1

HOST = "127.0.0.1"
PORT = 34567
ENCODING = "utf-8"

responseLines = ["File Name:", "Ack:"]
rxFile = File("", 0, "", 0)
sysState = SysState.CMD_INPUT

# Handles received file
# Return: Next packet, Resend, File error, All done
def handleReceivedFile(msg) -> RxResponse:
   rxResponse = RxResponse.RESEND

   fileName       = msg[0].split(':')
   seqNum         = msg[1].split(':')
   fileSize       = msg[2].split(':')
   receivedSha256 = msg[3].split(':')
   packData       = msg[4].split(':')

   # Takes away the command in the line
   fileName       = fileName[1]
   seqNum         = int(seqNum[1])
   fileSize       = int(fileSize[1])
   receivedSha256 = receivedSha256[1]
   packData       = packData[1]

   destroyData = input("Destroy data? (y/n): ")
   if ("y" == destroyData):
      packData = ""

   realSha256 = hashlib.sha256(packData.encode(ENCODING)).hexdigest()

   print("\nFile Name: "        + fileName +
         "\nSequence Number: "  + str(seqNum) +
         "\nFile Size: "        + str(fileSize) +
         "\nReceived SHA 256: " + receivedSha256 +
         "\nReal SHA 256: "     + realSha256)
   
   if ("N/A" == fileName):
      rxResponse = RxResponse.FILE_ERROR
   elif (receivedSha256 == realSha256):
      if (0 == seqNum):
         rxFile.replaceAll(fileName, fileSize, packData, seqNum+len(packData))
         rxResponse = RxResponse.NEXT_PACKET
         if (rxFile.getAck() >= (rxFile.getFileSize())):
            rxFile.saveFile()
            rxResponse = RxResponse.ALL_DONE
      elif (seqNum == rxFile.getAck()):
         rxFile.addData(packData)
         rxFile.setAck(seqNum+len(packData))
         rxResponse = RxResponse.NEXT_PACKET
         if (rxFile.getAck() >= (rxFile.getFileSize())):
            rxFile.saveFile()
            rxResponse = RxResponse.ALL_DONE
      else:
         rxResponse = RxResponse.RESEND
   else:
      rxResponse = RxResponse.RESEND

   return rxResponse

def makeFileError(msg):
   fileName = msg[0].split(':')
   fileName = fileName[1]
   ack = ""
   response = ("FILEERROR\r\n" +
               responseLines[0] + fileName + "\r\n" +
               responseLines[1] + ack)

   return response

def makeNextResponse() -> str:
   response = ("GET\r\n" +
               responseLines[0] + rxFile.getFilename() + "\r\n" +
               responseLines[1] + str(rxFile.getAck()) + "\r\n")
   
   return response

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
   serverIp = input("Write the server ip: ")

   while True:
      ##### WRITING INPUT #####
      if (SysState.CMD_INPUT == sysState):
         ans         = input("\n> ")
         splittedAns = ans.split(" ")
         cmd         = splittedAns[0]

         ##### SENDING COMMAND #####
         if ("WRITE" == cmd):
            gluePaste = " "
            s.sendto(((cmd + "\r\n" + gluePaste.join(splittedAns[1:])).encode(ENCODING)), (serverIp, PORT))
         elif ("GET" == cmd):
            filePath = splittedAns[1]
            rxFile.setFilename(filePath)
            response = makeNextResponse()
            s.sendto(response.encode(ENCODING), (serverIp, PORT))
         elif ("EXIT" == cmd):
            print("No request sent.")
            break
         else:
            continue

      ###### RECEIVING DATA ######
      data, addr = s.recvfrom(1024)
      data = data.decode(ENCODING)
      # print("\nData received from server: ", str(data))

      data = data.split("\r\n")
      cmd  = data[0]
      msg  = data[1:]
      
      if "FILE" == cmd:
         response = handleReceivedFile(msg)
         print("\nResponse: ", response)
         if ((RxResponse.NEXT_PACKET == response) or (RxResponse.RESEND == response)):
            sysState = SysState.SENDING_FILE
            response = makeNextResponse()
            s.sendto(response.encode(ENCODING), addr)
         elif (RxResponse.ALL_DONE == response):
            sysState = SysState.CMD_INPUT
            rxFile.resetAll()
         else:
            response = makeFileError(msg)
            s.sendto(response.encode(ENCODING), addr)
      else:
         print("\nReceived command not recognized: ", cmd)

   print("Disconnected from server")
   s.close()