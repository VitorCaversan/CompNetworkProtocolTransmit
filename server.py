import socket
import threading
from _thread import *

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

lock_thread = threading.Lock()

def threaded(conn):
   while True:
      data = conn.recv(1024)

      if not data:
         print("vlwflw")
         lock_thread.release()
         break

      data = data[::-1] # Reversing the received string

      conn.send(data)

   conn.close()

def Main():
   socketito = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   socketito.bind((HOST, PORT))
   print("Socket binded to port", PORT)

   socketito.listen()
   print("socket is listening")

   while True:
      conn, addr = socketito.accept()

      lock_thread.acquire()
      print('Connected to :', addr[0], ':', addr[1])

      start_new_thread(threaded, (conn,))

   socketito.close()

Main()

# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: # IPV4 and TCP
#    s.bind((HOST, PORT))
#    s.listen()
#    conn, addr = s.accept()
#    with conn:
#       print(f"Connected by {addr}")
#       while True:
#          data = conn.recv(1024)
#          if not data:
#                break
#          conn.sendall(data)