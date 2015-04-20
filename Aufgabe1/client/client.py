import socket
import sys

def decode_to_utf8(text):
	encoding = sys.stdin.encoding
	decoded = text.decode(encoding)
	return decoded.encode("UTF-8", "strict")

def parse(response):
	first_space = response.find(" ")
	if first_space < 0:
		return response, ""
	else:
		code = response[:first_space]
		return code, response[first_space + 1:]

class Client(object):
	def __init__(self):
		self.connection = socket.socket()

	def connect(self, host, port):
		try:
			self.connection.connect((host, port))
		except socket.error as connectionerror:
			return connectionerror

	def close(self):
		self.connection.close()

	def send(self, content):
		try:
			sent = self.connection.send(content + "\n")
			if sent < 0:
				return IOError("Was not able to send content")
			else:
				return None
		except socket.timeout as timeout:
			return timeout

	def wait_receive(self):
		data = self.connection.recv(1024)
		if data[-1:] == '\n':
			return data[:-1]
		else:
			return self.wait_receive()


def connect_to_server(host, port):
	client = Client()
	error = client.connect(host, port)
	return client, error


def ask_user_for_host_and_port():
	host = raw_input("Host: ")
	port = -1
	while port < 0:
		port_string = raw_input("Port: ")
		try:
			port = int(port_string)
		except ValueError:
			print("Invalid port.")

	return host, port

def command_prompt(client):
	while True:
		input = decode_to_utf8(raw_input("> "))
		result = client.send(input)
		if result is IOError:
			print("There was an error sending: ", result)
			break
		elif result is socket.timeout:
			print("Connection lost to server")
			break

		code, message = parse(client.wait_receive())
		if code == "ERROR":
			print("Server reponded with an error: ", message)
		elif code == "OK":
			if message == "BYE":
				print("Said goodbye to server")
				break
			elif message == "SHUTDOWN":
				print("Server is shutting down")
				break
			else:
				print("Server responded with: ", code, message)


if __name__ == "__main__":
	connected = False
	client = None
	while not connected:
		host, port = ask_user_for_host_and_port()
		client, error = connect_to_server(host, port)
		if error:
			print("There was an error connecting: ", error)
		else:
			connected = True

	try:
		command_prompt(client)
	finally:
		client.close()
