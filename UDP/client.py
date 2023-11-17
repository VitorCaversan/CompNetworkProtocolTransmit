import socket
import hashlib

HOST = "127.0.0.1"
PORT = 34567
ENCODING = "utf-8"

responseLines = ["File Name:", "File Ack:"]

# Handles received file
# Return: True if the data is integral
#         False if not
def handleReceivedFile(fileName, fileSize, receivedSha256, fileContent) -> bool:
   realSha256 = hashlib.sha256(fileContent.encode(ENCODING)).hexdigest()
   isDataIntegral = False

   print("\nFile Name: "        + fileName +
         "\nText Size: "        + fileSize +
         "\nReceived SHA 256: " + receivedSha256 +
         "\nReal SHA 256: "     + realSha256)
   
   if (receivedSha256 == realSha256):
      print("\nThe SHA's match!\nSaving file...")

      file = open(fileName, 'w')
      file.write(fileContent + "Look behind you.")
      file.close()

      print("\nFile saved!\n")
      isDataIntegral = True
   else:
      print("\nFile SHA's don't match.\nAborting save.\n")

   return isDataIntegral

def createFileError(fileName):
   ack = ""
   response = ("FILEERROR\r\n" +
               responseLines[0] + fileName + "\r\n" +
               responseLines[1] + ack)

   return response

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
   serverIp = input("Write the server ip: ")

   while True:
      ##### WRITING INPUT #####
      ans         = input("\n> ")
      splittedAns = ans.split(" ")
      cmd         = splittedAns[0]

      ##### SENDING COMMAND #####
      if ("WRITE" == cmd) or ("EXIT" == cmd):
         gluePaste = " "
         s.sendto(((cmd + "\r\n" + gluePaste.join(splittedAns[1:])).encode(ENCODING)), (serverIp, PORT))
      elif ("GET" == cmd):
         filePath = splittedAns[1]
         s.sendto((cmd + "\r\n" + filePath).encode(ENCODING), (serverIp, PORT))
      else:
         print("No request sent. Data was: ", ans)
         break

      ###### RECEIVING DATA ######
      print("before receive\n")
      data, addr = s.recvfrom(1024)
      print("after receive\n")
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
         fileName       = msg[0].split(':')
         fileSize       = msg[1].split(':')
         receivedSha256 = msg[2].split(':')
         fileData       = msg[3].split(':')

         # Takes away the command in the line
         fileName       = fileName[1]
         fileSize       = fileSize[1]
         receivedSha256 = receivedSha256[1]
         fileData       = fileData[1]

         if (True == handleReceivedFile(fileName, fileSize, receivedSha256, fileData)):
            print("Noice\n")
         else:
            response = createFileError(fileName)
            s.sendto(response.encode(ENCODING), addr)
      else:
         print("Command not recognized: ", cmd)

   print("Disconnected from server")
   s.close()