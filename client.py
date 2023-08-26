import socket

HOST = "127.0.0.1"
PORT = 65432
ENCODING = "utf-8"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
   s.connect((HOST, PORT))

   while True:
      ###### RECEIVING DATA ######
      data = s.recv(1024).decode(ENCODING)
      print("\nData received from server: ", str(data))

      cmd, msg = data.split("@")
      if cmd == "DISCONNECTED":
         print("[SERVER]: ", str(msg))
         break
      elif cmd == "OK":
         print(str(msg))
      elif "FILE" == cmd:
         print(str(msg))
      else:
         print("Command not recognized: ", cmd)

      ##### WRITING INPUT #####
      ans         = input("> ")
      splittedAns = ans.split(" ")
      cmd         = splittedAns[0]

      ##### SENDING COMMAND WITH DATA #####
      if ("WRITE" == cmd):
         gluePaste = " "
         s.send((cmd + "@" + gluePaste.join(splittedAns[1:])).encode(ENCODING))
      elif ("DOWNLOAD" == cmd):
         filePath = splittedAns[1]
         s.send((cmd + "@" + filePath).encode(ENCODING))
      else:
         print("No request sent. Data was: ", ans)
         break

   print("Disconnected from server")
   s.close()