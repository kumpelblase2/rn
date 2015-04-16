import socket
import sys
import argparse
import threading
import time


def parse(response):
	first_space = response.find(" ")
	if first_space < 0:
		return response, ""
	else:
		code = response[:first_space]
		return code, response[first_space + 1:]

class RequestHandler(threading.Thread):
	def __init__(self, connection, server):
		super(RequestHandler, self).__init__()
		self.client = connection
		self.server = server
		self.handlers = {
			"LOWERCASE": self.lowercase,
			"UPPERCASE": self.uppercase,
			"REVERSE": self.reverse,
			"BYE": self.bye,
			"SHUTDOWN": self.shutdown
		}

	def lowercase(self, message):
		self.send_to_client("OK " + message.lower())
		return True

	def uppercase(self, message):
		self.send_to_client("OK " + message.upper())
		return True

	def reverse(self, message):
		self.send_to_client("OK " + message[::-1])
		return True

	def bye(self, message):
		self.send_to_client("OK BYE")
		self.remove()
		return False

	def shutdown(self, message):
		if self.server.request_shutdown(message):
			self.send_to_client("OK SHUTDOWN")
			self.remove()
			return False
		else:
			self.send_to_client("ERROR INVALID PASSWORD")
			return True

	def run(self):
		while True:
			data = self.receive()
			if not data:
				print("Could not read for client")
				self.remove()
				break

			print "Read ", data
			if len(data) > 255:
				self.send_to_client("ERROR STRING TOO LONG")
			elif not self.execute(data):
				break

	def send_to_client(self, content):
		self.client.send(content + "\n")

	def execute(self, command):
		code, message = parse(command)
		if not self.handlers.__contains__(code):
			self.send_to_client("ERROR INVALID COMMAND")
		else:
			return self.handlers[code](message)

	def remove(self):
		print("Client disconnected: ", self.client.getpeername())
		self.server.on_disconnect(self)

	def receive(self):
		try:
			data = self.client.recv(1024)
			if data[-1:] == '\n':
				return data[:-1]
			else:
				return self.receive()
		except:
			return None


class Server(object):
	def __init__(self, max_clients, port, password):
		self.max_clients = max_clients
		self.port = port
		self.shutdown_password = password
		self.connection = None
		self.clients = []
		self.shutdown_granted = False

	def start(self):
		self.connection = socket.socket()
		try:
			self.connection.bind((socket.gethostname(), self.port))
			self.connection.listen(1)
		except socket.error as error:
			print error
			self.connection.close()
			return error

		return None

	def on_disconnect(self, client):
		self.clients.remove(client)
		if self.shutdown_granted and len(self.clients) == 0:
			self.connection.close()

	def on_client_accept(self, connection):
		handler = RequestHandler(connection, self)
		handler.start()
		self.clients.append(handler)

	def request_shutdown(self, password):
		if password == self.shutdown_password:
			self.shutdown_granted = True
			return True
		else:
			return False

	def wait_clients(self):
		while not self.shutdown_granted:
			if len(self.clients) < self.max_clients:
				client_connection, address = self.connection.accept()
				print("Accepted client from ", address)
				self.on_client_accept(client_connection)
			else:
				time.sleep(0.1)


def configure():
	parser = argparse.ArgumentParser(description="RN Server")
	parser.add_argument("--max-clients", '-n', type=int, help="Number of max clients", default=3)
	parser.add_argument("--port", "-p", type=int, help="Port", default=1337)
	parser.add_argument("--password", '-c', help="Shutdown password", default="beepbeep")
	result = parser.parse_args(sys.argv[1:])
	server =  Server(max_clients=result.max_clients,port=result.port, password=result.password)
	result = server.start()
	if result:
		return None, result
	else:
		return server, None

if __name__ == "__main__":
	server, error = configure()
	if error:
		print("There was an error setting up the server")
	else:
		print "Awaiting connection"
		server.wait_clients()