import socket
import threading
import hashlib
from _thread import *

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 23456  # Port to listen on (non-privileged ports are > 1023)
ENCODING = "utf-8"

lock_thread = threading.Lock()

def threaded(conn, addr):
   print(f"[NEW CONNECTION] {addr} connected.")
   conn.send("OK@Alive and kicking!".encode(ENCODING))

   while True:
      data         = conn.recv(1024).decode(ENCODING)
      splittedData = data.split("@")
      cmd          = splittedData[0]

      ##### TREATING DATA FOR EACH COMMAND #####
      if not data or ("EXIT" == cmd):
         print("vlwflw")
         conn.send("DISCONNECTED@Dead and sleeping".encode(ENCODING))
         lock_thread.release()
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
   return

def Main():
   socketito = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   socketito.bind((HOST, PORT))
   print("Socket binded to port", PORT)

   socketito.listen()
   print("Socket is listening")

   while True:
      conn, addr = socketito.accept()

      lock_thread.acquire()

      start_new_thread(threaded, (conn, addr))

   socketito.close()

Main()