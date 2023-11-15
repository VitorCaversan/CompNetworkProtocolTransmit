import socket
import threading
import hashlib
import os
from _thread import *

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 34567  # Port to listen on (non-privileged ports are > 1023)
ENCODING = "utf-8"

headersDict = {
'Server': 'Ludwig/1.0',
'Content-Type': 'text/html'
}

statusCodesDict = {
   200: 'OK',
   404: 'Not Found'
}

lock_thread = threading.Lock()

def threaded(conn, addr) -> int:
   print(f"[NEW CONNECTION] {addr} connected.")
   
   while True:
      data         = conn.recv(1024).decode(ENCODING)
      splittedData = data.split("\r\n")

      if (splittedData[0].find("GET") != -1): # If it is an HTTP request
         cmd = "GET"
      else:
         cmd = splittedData[0]

      print("\nData received from client: ", str(data))

      ##### TREATING DATA FOR EACH COMMAND #####
      if not data or ("EXIT" == cmd):
         print("vlwflw")
         conn.send("DISCONNECTED@Dead and sleeping".encode(ENCODING))
         break
      elif "WRITE" == cmd:
         gluePaste = " " # Connects the words with a space
         conn.send(("OK@" + gluePaste.join(splittedData[1:])).encode(ENCODING))
      elif "DOWNLOAD" == cmd:
         filePath = splittedData[1]

         file = open(filePath, "r")
         text = file.read()
         file.close()

         filePath = filePath.split("/")
         fileName = filePath[-1]
         textSize = len(text)
         sha256   = hashlib.sha256(text.encode(ENCODING)).hexdigest()

         conn.send(("FILE@" + fileName      + "_" +
                              str(textSize) + "_" +
                              sha256        + "_" + text).encode(ENCODING))
      elif "GET" == cmd: # HTTP GET
         response = handleGETRequest(splittedData)
         conn.send(response)
      else:
         print(data)
         conn.send(data.encode(ENCODING))

   conn.close()
   return 1

def Main():
   socketito = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   ip = getIP()
   print("Server ip:" + ip)
   socketito.bind((ip, PORT))
   print("Socket binded to port", PORT)

   socketito.listen()
   print("Socket is listening")

   while True:
      conn, addr = socketito.accept()

      lock_thread.acquire()

      start_new_thread(threaded, (conn, addr))

      lock_thread.release()

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

def makeResponseLine(statusCode: int) -> bytes:
   sttsCodeMeaning = statusCodesDict[statusCode]
   respLine        = ("HTTP/1.1 " + str(statusCode) + " " + sttsCodeMeaning + "\r\n")

   return respLine.encode("utf-8")

def makeResponseHeaders(extraHeaders:dict = None, contentSize:int = 0, filename:str = " ") -> bytes:
   headers = headersDict.copy()

   if (extraHeaders != None):
      headers.update(extraHeaders)

   headersString = ""
   for key, value in headers.items():
      if (key == "Content-Type"):
         if (filename.endswith(".html")):
            value = "text/html"
         elif (filename.endswith(".jpg")):
            value = "image/jpeg"

      headersString += (key + ": " + value + "\r\n")

   headersString += ("Content-Length: " + str(contentSize) + "\r\n")

   return headersString.encode("utf-8")

def handleGETRequest(splittedData) -> bytes:
   httpRequest = splittedData[0].split(' ')
   method      = httpRequest[0]
   filePath    = httpRequest[1][1:] # Removing the first '/' from the path

   if (os.path.exists(filePath)):
      file         = open(filePath, "rb")
      responseBody = file.read()
      file.close()
      
      respLine    = makeResponseLine(200)
      respHeaders = makeResponseHeaders(contentSize=len(responseBody), filename=filePath)
   else:
      respLine     = makeResponseLine(404)
      responseBody = b"<h1>404 Not Found</h1>"
      respHeaders  = makeResponseHeaders(contentSize=len(responseBody))

   return (respLine + respHeaders + b"\r\n" + responseBody)


Main()