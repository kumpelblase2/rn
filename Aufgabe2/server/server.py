import socket
import sys
import argparse
from thread import allocate_lock
import time
import select
import requesthandler
import ConfigParser


class Server(object):
	def __init__(self, max_clients, port, accounts):
		self.max_clients = max_clients
		self.port = port
		self.accounts = accounts
		self.connection = None
		self.clients = []
		self.shutdown_granted = False
		self.lock = allocate_lock()
		self.loggedInUsers = {}

	def start(self):
		self.connection = socket.socket()
		try:
			self.connection.bind(('0.0.0.0', self.port))
			self.connection.listen(1)
		except socket.error as error:
			print error
			self.connection.close()
			return error

		return None

	def on_disconnect(self, client):
		self.clients.remove(client)
		if self.shutdown_granted and len(self.clients) == 0:
			self.close()

	def on_client_accept(self, connection):
		handler = requesthandler.RequestHandler(connection, self)
		handler.start()
		self.clients.append(handler)

	def wait_clients(self):
		while not self.shutdown_granted:
			if len(self.clients) < self.max_clients:
				print "Waiting"
				readable_list = [self.connection]
				readable, writeable, errorlist = select.select(readable_list, [], [])
				for s in readable:
					if s is self.connection:
						try:
							client_connection, address = self.connection.accept()
							print("Accepted client from ", address)
							self.on_client_accept(client_connection)
						except socket.error as accept_error:
							print("Error while accepting client: ", accept_error)
			else:
				time.sleep(0.1)

	def close(self):
		try:
			self.connection.shutdown(socket.SHUT_RDWR)
			self.connection.close()
		except:
			pass

	def try_login(self, username, password):
		self.lock.acquire()
		state = True
		if self.loggedInUsers.__contains__(username) and self.loggedInUsers[username]:
			state = False
		else:
			account = self.get_account(username)
			if account:
				state = account['password'] == password
			else:
				state = False

		self.lock.release()
		return state

	def get_account(self, username):
		for accountDef in self.accounts:
			account = self.accounts[accountDef]
			if account['username'] == username:
				return account

		return None

	def set_logged_in(self, username, state):
		self.lock.acquire()
		self.loggedInUsers[username] = state
		self.lock.release()


def load_config():
	config = ConfigParser.ConfigParser()
	config.read("../config.ini")
	servers = {}
	for section in config.sections():
		values = {}
		for option in config.options(section):
			try:
				values[option] = config.get(section, option)
			except:
				print("exception when parsing", option)
				values[option] = None

		servers[section] = values

	return servers


def configure():
	parser = argparse.ArgumentParser(description="RN Server")
	parser.add_argument("--max-clients", '-n', type=int, help="Number of max clients", default=3)
	parser.add_argument("--port", "-p", type=int, help="Port", default=1337)
	result = parser.parse_args(sys.argv[1:])

	server = Server(max_clients=result.max_clients, port=result.port, accounts=load_config())
	result = server.start()
	return server, result

if __name__ == "__main__":
	server, error = configure()
	if error:
		print("There was an error setting up the server")
	else:
		print "Awaiting connection"
		server.wait_clients()
		server.close()
