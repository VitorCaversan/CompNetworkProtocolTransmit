import socket
import threading
import hashlib
from _thread import *

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 23456  # Port to listen on (non-privileged ports are > 1023)
ENCODING = "utf-8"

lock_thread = threading.Lock()

def threaded(conn, addr) -> int:
   print(f"[NEW CONNECTION] {addr} connected.")
   conn.send("OK@Alive and kicking!".encode(ENCODING))

   while True:
      data         = conn.recv(1024).decode(ENCODING)
      splittedData = data.split("\r\n")
      cmd          = splittedData[0]

      print("\nData received from client: ", str(data))

      ##### TREATING DATA FOR EACH COMMAND #####
      if not data or ("EXIT" == cmd):
         print("vlwflw")
         conn.send("DISCONNECTED@Dead and sleeping".encode(ENCODING))
         break
      elif "WRITE" == cmd:
         gluePaste = " "
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

Main()