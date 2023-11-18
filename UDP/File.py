class File:
   def __init__(self, filename: str, fileSize: int, data: str, ack: int):
      self.filename = filename
      self.fileData = data
      self.ack      = ack
      self.fileSize = fileSize
   
   def __str__(self):
      return ("\nFile Name: "   + self.filename +
              "\nFile Size: " + str(self.fileSize) +
              "\nFile Data: " + self.fileData +
              "\nAck: "       + str(self.ack) + "\n")

   def addData(self, data: str):
      self.fileData += data
   
   def saveFile(self):
      file = open(self.filename, 'w')
      file.write(self.fileData)
      file.close()
   
      print("\nFile saved!\n")
   
   def resetAll(self):
      self.filename = ""
      self.fileSize = 0
      self.fileData = ""
      self.ack      = 0

   def getFilename(self):
      return self.filename
   def getFileData(self):
      return self.fileData
   def getAck(self):
      return self.ack
   def getFileSize(self):
      return self.fileSize
   
   def setFilename(self, filename: str):
      self.filename = filename
   def setFileData(self, fileData: str):
      self.fileData = fileData
   def setAck(self, ack: int):
      self.ack = ack
   def setFileSize(self, fileSize: int):
      self.fileSize = fileSize