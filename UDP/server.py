import socket
import threading
import hashlib
import os
from _thread import *

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 34567  # Port to listen on (non-privileged ports are > 1023)
ENCODING = "utf-8"

responseLines = ["File Name:", "File Size:", "File Hash:", "File Content:"]

lock_thread = threading.Lock()

def Main():
   socketito = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   ip = getIP()
   print("Server ip:" + ip)
   socketito.bind((ip, PORT))
   print("Socket binded to port", PORT)

   while True:
      msg, addr = socketito.recvfrom(1024)

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
   print(f"[NEW MESSAGE] {addr} connected.")

   msg = msg.decode(ENCODING)
   msg = msg.split("\r\n")
   cmd = msg[0]

   respLine = b""

   if "GET" == cmd:
      filePath = msg[1]
      respLine = handleGETRequest(filePath)

   socketi.sendto(respLine, addr)

   return 1

def handleGETRequest(filePath: str) -> bytes:
   respLine = b""

   if (os.path.exists(filePath)):
      file     = open(filePath, "rb")
      fileData = file.read()
      file.close()
      
      respLine = makeResponseLine(filePath, fileData)
   else:
      respLine = makeResponseLine(b"N/A", respLine)

   return (b"FILE\r\n" + respLine)

def makeResponseLine(fileName: str, fileData: bytes) -> bytes:
   textSize = len(fileData)
   sha256   = hashlib.sha256(fileData).hexdigest()

   respLine = (responseLines[0] + fileName + "\r\n" +
               responseLines[1] + str(textSize) + "\r\n" +
               responseLines[2] + sha256 + "\r\n" +
               responseLines[3] + fileData.decode(ENCODING) + "\r\n").encode(ENCODING)

   return respLine


Main()