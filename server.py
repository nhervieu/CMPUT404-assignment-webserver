#  coding: utf-8 
import socketserver
import os
from os import path
import codecs
import datetime

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributtimeed on an "AS IS" BASIS,
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


def requestParser(data):
	#takes the request from the client and returns the request type and the requested directory
	data = data.split("\r\n")

	method, directory, host = '', '', ''

	request = data[0].split(" ")

	#only parse if http1.1 request
	if len(request)==3:
		if request[2] == 'HTTP/1.1':
			#parse the request
			method = request[0]
			directory = request[1]	
			host = data[1].split(" ")[1]
		else: 
			directory = ""

	return method, directory, host, data


def validPath(path):
	#check if path exists. 
	#if the directory exists and no file specified, returns the index.html file by default
	#if the path is to a file that exists, returns the file
	#if the path is not to a file or directory that exists, returns False

	#return full path
	#https://stackoverflow.com/questions/973473/getting-a-list-of-all-subdirectories-in-the-current-directory
	all_files = []
	all_dirs = [x[0] for x in os.walk("www/")]
	for x in range(len(all_dirs)):
		if all_dirs[x] != "www/":
			all_dirs[x] = all_dirs[x][3:] +"/"
		else: 
			all_dirs[x] = all_dirs[x][3:]  

		for filename in os.listdir("www/"+all_dirs[x]):
			if filename.endswith('.html') or filename.endswith(".css"):
				all_files.append(all_dirs[x] + filename)

	print(all_files)
	print(all_dirs)

	if path in all_dirs:
		if path + "index.html" in all_files:
	 		return "www/" + path + "index.html"
	elif path in all_files:
		return "www/" + path
	else:
		return False

	return path


def mimeType(path):
#returns the mime type associated with the file defined by path
	if path[-4:] == ".css":
		return"text/css"
	elif path[-5:] == ".html":
		return"text/html"	
	else:
		return "text/plain"


def chooseResponse(method, directory):
	new_path = False
	
	#plain by default
	ctype = "text/plain"

	if method == "GET":
		new_path = validPath(directory)
		if new_path == False:
			new_path = validPath(directory + "/")
			if new_path == False:
				response = 404
			else:
				#variation of path exists. redirect
				response = 301
				ctype = mimeType(new_path)
		else:
			#if directory exists
			response = 200
			ctype = mimeType(new_path)

	#if method is not GET then return 405 method not allowed error
	else:
		response = 405
	return response, ctype, directory, new_path



def createHeader(response, ctype, directory, new_path, parsed_data, host):
	
	body = ""

	if response == 200:
		header = "HTTP/1.1 200 OK\r\n"
	
		f=open(new_path, 'r')
		body = f.read()

	elif response == 404:
		header = "HTTP/1.1 404 Error\r\n\r\n" + "404 Error. This page doesn't exist.\r\n"
		return header
	elif response == 301:
		header = "HTTP/1.1 301 Moved Permanently\r\n"
		#add redirects
	elif response == 405:
		header = "HTTP/1.1 405 Method Not Allowed\r\n\r\n" + "405 Error. Request type not allowed\r\n"
		return header

	header += "Host: " + host + "\r\n"
	header += "Date: " + str(datetime.datetime.now()) + "\r\n"
	header += "Content-Type: "+ctype + "\r\n" 
	#content length
	header +="\r\n"
	header += body


	#server = ...
	#header += "Server :" + server + "\r\n"


	# connection = 
	# header += "Connection: " +  connection + "\r\n"


	#for 301 time
	#loc+ + ation = 
	#header += "Location: " +  location + "\r\n"

	header += "\r\n"
#	closing = "Connection: close"


	print(header)

	return header







class MyWebServer(socketserver.BaseRequestHandler):
    
	def handle(self):
		self.data = self.request.recv(1024).strip()
		print ("Got a request of: %s\n" % self.data)

		#parse the requ+ est
		method, directory, host, parsed_data = requestParser(self.data.decode())
		response, ctype, directory, new_path = chooseResponse(method, directory)
		message = createHeader(response, ctype, directory, new_path, parsed_data, host)


		#send back the data
		self.request.sendall(bytearray(message,'utf-8'))





if __name__ == "__main__":
	HOST, PORT = "localhost", 8080
	socketserver.TCPServer.allow_reuse_address = True
	# Create the server, binding to localhost on port 8080
	server = socketserver.TCPServer((HOST, PORT), MyWebServer)

	# Activate the server; this will keep running until you
	# interrupt the program with Ctrl-C
	server.serve_forever()






