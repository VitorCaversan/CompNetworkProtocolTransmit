import socket
import hashlib

HOST = "127.0.0.1"
PORT = 23456
ENCODING = "utf-8"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
   s.connect((HOST, PORT))

   while True:
      ###### RECEIVING DATA ######
      data = s.recv(1024).decode(ENCODING)
      print("\nData received from server: ", str(data))

      cmd, msg = data.split("@")
      if "DISCONNECTED" == cmd:
         print("[SERVER]: ", str(msg))
         break
      elif "OK" == cmd:
         print(str(msg))
      elif "FILE" == cmd:
         msg = msg.split("_")

         fileName       = msg[0]
         textSize       = msg[1]
         receivedSha256 = msg[2]
         text           = msg[3]

         realSha256 = hashlib.sha256(text.encode(ENCODING)).hexdigest()

         print("\nFile Name: "        + fileName +
               "\nText Size: "        + textSize +
               "\nReceived SHA 256: " + receivedSha256 +
               "\nReal SHA 256: "     + realSha256)
         
         if (receivedSha256 == realSha256):
            print("\nThe SHA's match!\nSaving file...")

            file = open(fileName, 'w')
            file.write(text + "Look behind you.")
            file.close()

            print("\nFile saved!\n")
         else:
            print("\nFile SHA's don't match.\nAborting save.\n")
      else:
         print("Command not recognized: ", cmd)

      ##### WRITING INPUT #####
      ans         = input("\n> ")
      splittedAns = ans.split(" ")
      cmd         = splittedAns[0]

      ##### SENDING COMMAND WITH DATA #####
      if ("WRITE" == cmd) or ("EXIT" == cmd):
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