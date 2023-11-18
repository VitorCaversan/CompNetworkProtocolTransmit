import socket
import hashlib
from enum import Enum
from File import File

class RxResponse(Enum):
   NEXT_PACKET = 0
   RESEND      = 1
   FILE_ERROR  = 2
   ALL_DONE    = 3

HOST = "127.0.0.1"
PORT = 34567
ENCODING = "utf-8"

responseLines = ["File Name:", "Ack:"]
rxFile = File("", 0, "", 0)

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

   realSha256 = hashlib.sha256(packData.encode(ENCODING)).hexdigest()

   print("\nFile Name: "        + fileName +
         "\nSequence Number: "  + str(seqNum) +
         "\nFile Size: "        + str(fileSize) +
         "\nReceived SHA 256: " + receivedSha256 +
         "\nReal SHA 256: "     + realSha256)
   
   if (receivedSha256 == realSha256):
      if (0 == seqNum):
         rxFile.setFilename(fileName)
         rxFile.setFileData(packData)
         rxFile.setFileSize(fileSize)
         rxFile.setAck(seqNum+len(packData))
         rxResponse = RxResponse.NEXT_PACKET
         if (rxFile.getAck() >= (rxFile.getFileSize()-1)):
            rxFile.saveFile()
            rxResponse = RxResponse.ALL_DONE
      elif (seqNum == rxFile.getAck()):
         rxFile.addData(packData)
         rxFile.setAck(seqNum+len(packData))
         rxResponse = RxResponse.NEXT_PACKET
         if (rxFile.getAck() >= (rxFile.getFileSize()-1)):
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

      ###### RECEIVING DATA ######
      data, addr = s.recvfrom(1024)
      data = data.decode(ENCODING)
      print("\nData received from server: ", str(data))

      data = data.split("\r\n")
      cmd  = data[0]
      msg  = data[1:]
      
      if "DISCONNECTED" == cmd:
         print("[SERVER]: ", str(msg))
         break
      elif "OK" == cmd:
         print(str(msg))
      elif "FILE" == cmd:
         response = handleReceivedFile(msg)
         print("\nResponse: ", response)
         if ((RxResponse.NEXT_PACKET == response) or (RxResponse.RESEND == response)):
            print(rxFile)
            response = makeNextResponse()
            s.sendto(response.encode(ENCODING), addr)
         elif (RxResponse.ALL_DONE == response):
            print(rxFile)
            rxFile.resetAll()
            print("File received!\n")
         else:
            response = makeFileError(msg)
            s.sendto(response.encode(ENCODING), addr)
      else:
         print("Command not recognized: ", cmd)

   print("Disconnected from server")
   s.close()