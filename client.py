import socket

HOST = "127.0.0.1"
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
   s.connect((HOST, PORT))

   while True:
      message = "testing connectionnnnnnn"
      s.send(message.encode("ascii"))
      data = s.recv(1024)

      print("Data received from server: ", str(data.decode("ascii")))

      ans = input("\nContinue? (y/n): ")
      if ('y' == ans):
         continue
      else:
         break

   s.close()