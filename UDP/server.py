import socket
import threading
import hashlib
import os
from _thread import *

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 34567  # Port to listen on (non-privileged ports are > 1023)
ENCODING = "utf-8"
BUFFER_SIZE = 1024
DATA_BUFF_SIZE = 768

responseLines = ["File Name:", "SeqNum:", "File Size:", "File Hash:", "File Content:"]

lock_thread = threading.Lock()

def Main():
   socketito = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   ip = getIP()
   print("Server ip:" + ip)
   socketito.bind((ip, PORT))
   print("Socket binded to port", PORT)

   while True:
      msg, addr = socketito.recvfrom(BUFFER_SIZE)

      if (msg != 0):
         treatNewMsg(msg, addr, socketito)

   socketito.close()

def getIP():
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   s.settimeout(0)
   try:
      # doesn't even have to be reachable
      s.connect(('10.254.254.254', 1))
      ip = s.getsockname()[0]
   except Exception:
      ip = '127.0.0.1'
   finally:
      s.close()
   return ip

def treatNewMsg(msg, addr, socketi: socket) -> int:
   msg = msg.decode(ENCODING)
   print(f"[NEW MESSAGE] {addr} connected. Data: ", str(msg))
   msg = msg.split("\r\n")
   cmd = msg[0]

   respLine = b""

   if "GET" == cmd:
      respLine = handleGETRequest(msg[1:])

   socketi.sendto(respLine, addr)

   return 1

def handleGETRequest(msg) -> bytes:
   filePath = msg[0].split(":")
   ack      = msg[1].split(":")

   # Removes the command from the line
   filePath = filePath[1]
   ack      = int(ack[1])

   respLine = b""

   if (os.path.exists(filePath)):
      file     = open(filePath, "rb")
      fileData = file.read()
      file.close()
      
      partialFileData = getFractionedFileData(fileData, ack)
      respLine = makeResponseLine(filePath, len(fileData), ack, partialFileData)
   else:
      respLine = makeResponseLine("N/A", 0, 0, respLine)

   return (b"FILE\r\n" + respLine)

# Gets a portion of the file data and returns it in bytes
def getFractionedFileData(fileData: bytes, ack: int) -> bytes:
   package = b""

   if ack < len(fileData):
      if ((ack + DATA_BUFF_SIZE) < len(fileData)):
         package = fileData[ack:ack+DATA_BUFF_SIZE]
      else:
         package = fileData[ack:(len(fileData))]

   return package

def makeResponseLine(fileName: str, fileSize: int, ack: int, partialData: bytes) -> bytes:
   sha256   = hashlib.sha256(partialData).hexdigest()

   respLine = (responseLines[0] + fileName + "\r\n" +
               responseLines[1] + str(ack) + "\r\n" +
               responseLines[2] + str(fileSize) + "\r\n" +
               responseLines[3] + sha256 + "\r\n" +
               responseLines[4] + partialData.decode(ENCODING) + "\r\n").encode(ENCODING)
   
   return respLine


Main()