# CompNetworkTCPTransmit

A server Socket for TCP connection that supports multiple connections.

## Functionalities
It creates a server with a TCP socket that listens to a specific IP and port, given to te user when
first running the server.py file.

Once the server is running, two options are available:
 - Connection to the server by running the client.py file:
    - WRITE _string_: writes the following string in the server terminal;
    - DOWNLOAD _file name_: downloads a file with the specified _file name_ that is present on the
      server's folder.
 - Connection by accessing a web page with the server's ip and port:
    - It answers to the HTTP GET request with the object of the htmlPage.html file.