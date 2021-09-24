#  coding: utf-8 
import socketserver
import socket
import os
from datetime import datetime
import urllib.parse

# Copyright 2013-2021 Abram Hindle, Eddie Antonio Santos, Jiayuan Sun
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        # Get the date and time
        now = datetime.now()
        now = now.strftime("%d/%m/%Y %H:%M:%S")
        self.request.settimeout(0.02)
        self.getDataBytes = b""
        while True:
            try:
                self.dataTemp = self.request.recv(4096)
            except:
                break
            self.getDataBytes += self.dataTemp
        # print ("Got a request of: %s\n" % self.getDataBytes)
        self.getDataList = self.getDataBytes.decode().split()
        self.method = self.getDataList[0]
        # If the method is "Get" then proceed, if the method is anything else
        # response 405 Method Not Allowed
        if self.method == "GET":
            self.path = self.getDataList[self.getDataList.index('GET') + 1]
            self.path = "www" + self.path
            self.path = urllib.parse.unquote(self.path)
            if self.path[-1] == "/":
                self.path += "index.html"
            try:
                filename, file_extension = os.path.splitext(self.path)
                # Users don't specify the file name, the program will add it
                # and try to open the file. If succeed, response 301 Moved 
                # Permanently and redirect the page. If fail, response 404 
                # Not Found
                if file_extension == "":
                    try:
                        tempPath = self.path + "/index.html"
                        f = open(tempPath, "r")
                        content = "<HTML><HEAD><meta http-equiv=\"content-type\" content=\"text/html;charset=utf-8\">"
                        content += "<TITLE>301 Moved Permanently</TITLE></HEAD><BODY>"
                        content += "<H1>301 Moved Permanently</H1>"
                        content += "The document has moved"
                        content += "<A HREF=\"http://127.0.0.1:8080/deep/\"> here</A>."
                        content += "</BODY></HTML>"
                        contentLength = str(len(content))
                        self.data = "HTTP/1.1 301 Moved Permanently\r\n"
                        self.data += "Location: http://127.0.0.1:8080/deep/\r\n"
                        self.data += "Date: " + now + "\r\n"
                        self.data += "Content-Length: " + contentLength + "\r\n"
                        self.data += "Connection: close\r\n"
                        self.data += "Content-Type: text/html; charset=UTF-8\r\n"
                        self.data += "\r\n"
                        self.data += content + "\r\n\r\n"
                        self.request.sendall(self.data.encode())
                        self.request.shutdown(socket.SHUT_WR)
                    except:
                        content = "<html><body><h1>404 Not Found</h1></body><html>"
                        contentLength = str(len(content))
                        self.data = "HTTP/1.1 404 Not Found\r\n"
                        self.data += "Date: " + now + "\r\n"
                        self.data += "Content-Length: " + contentLength + "\r\n"
                        self.data += "Connection: close\r\n"
                        self.data += "Content-Type: text/html; charset=UTF-8\r\n"
                        self.data += "\r\n"
                        self.data += content + "\r\n\r\n"
                        self.request.sendall(self.data.encode())
                        self.request.shutdown(socket.SHUT_WR)
                # Users specify the file name, try to open the file. If succeed, 
                # response 200 OK, if fail, response 404 Not Found    
                else:
                    f = open(self.path, "r")
                    content = f.read()
                    contentLength = str(len(content))
                    self.data = "HTTP/1.1 200 OK\r\n"
                    self.data += "Date: " + now + "\r\n"
                    self.data += "Content-Length: " + contentLength + "\r\n"
                    self.data += "Connection: Keep-Alive\r\n"
                    if file_extension == ".html":
                        self.data += "Content-Type: text/html; charset=UTF-8\r\n"
                    elif file_extension == ".css":
                        self.data += "Content-Type: text/css; charset=UTF-8\r\n"
                    else:
                        self.data += "Content-Type: application/octec-stream; charset=UTF-8\r\n"
                    self.data += "\r\n"
                    self.data += content + "\r\n\r\n"
                    self.request.sendall(self.data.encode())
                    self.request.shutdown(socket.SHUT_WR)
            except:
                content = "<html><body><h1>404 Not Found</h1></body><html>"
                contentLength = str(len(content))
                self.data = "HTTP/1.1 404 Not Found\r\n"
                self.data += "Date: " + now + "\r\n"
                self.data += "Content-Length: " + contentLength + "\r\n"
                self.data += "Connection: close\r\n"
                self.data += "Content-Type: text/html; charset=UTF-8\r\n"
                self.data += "\r\n"
                self.data += content + "\r\n\r\n"
                self.request.sendall(self.data.encode())
                self.request.shutdown(socket.SHUT_WR)
        else:
            content = "<html><body><h1>405 Method Not Allowed</h1></body><html>"
            contentLength = str(len(content))
            self.data = "HTTP/1.1 405 Method Not Allowed\r\n"
            self.data += "Date: " + now + "\r\n"
            self.data += "Content-Length: " + contentLength + "\r\n"
            self.data += "Connection: close\r\n"
            self.data += "Content-Type: text/html; charset=UTF-8\r\n"
            self.data += "\r\n"
            self.data += content + "\r\n\r\n"
            self.request.sendall(self.data.encode())
            self.request.shutdown(socket.SHUT_WR)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    print("Servr listening on http://127.0.0.1:8080/")
    server.serve_forever()



