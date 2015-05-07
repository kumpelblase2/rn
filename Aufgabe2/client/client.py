import socket
import sys
import ConfigParser
import sched, time
import traceback

OK = '+OK'
ERROR = '-ERR'

def parse(response):
	if not response.__contains__(' '):
		return response, '', ''

	code, info = response.split(' ', 1)
	keyword, addition = info.split(' ', 1)
	return code, keyword, addition

class Client(object):
	def __init__(self):
		self.user = None
		self.password = None
		self.connection = socket.socket()
		self.state = None

	def connect(self, host, port):
		try:
			self.connection.connect((host, int(port)))
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
		data = self.connection.recv(512)  # Max 512 character including CRLF
		if data[-2:] == '\r\n':  # Should always end with CRLF
			return data[:-2]
		else:
			return self.wait_receive()

	def wait_command_result(self):
		data = self.wait_receive()
		return parse(data)

	def wait_multi_line(self):
		data = []
		received = self.wait_receive()
		while received != '.':
			received.append(received)
			received = self.wait_receive()

		return data

	def send_command(self, keyword, *args):
		return self.send(' '.join([keyword, ' '.join(args)]))

	def run(self):
		self.state = GreetingState(self)
		while self.state is not None:
			self.state = self.state.run()

	def quit(self):
		self.send_command("QUIT")
		self.wait_command_result()
		self.close()


class GreetingState(object):
	def __init__(self, client):
		self.client = client

	def run(self):
		greeting, keyword, info = self.client.wait_command_result()
		if greeting != OK:
			raise RuntimeError("Greeting was not ok")

		print("Successful greeting: ", keyword, info)
		return AuthenticationState(self.client)

class AuthenticationState():
	def __init__(self, client):
		self.client = client

	def run(self):
		err = self.client.send_command("USER", self.client.user)
		if err:
			print("Error when sending user: ", err)
			return None

		response, keyword, info = self.client.wait_command_result()
		if response != OK:
			print("Got error when sending user", ' '.join([keyword, info]))
			return None

		err = self.client.send_command("PASS", self.client.password)
		if err:
			print("Error when sending password: ", err)
			return None

		response, keyword, info = self.client.wait_command_result()
		if response != OK:
			print("Got error when sending password", ' '.join([keyword, info]))
			return None

		print("Logged in")
		return TransactionState(self.client)


class TransactionState():
	def __init__(self, client):
		self.client = client

	def run(self):
		err = self.client.send_command("STAT", '')
		if err:
			print("Error when sending status: ", err)
			return None

		response, messages, octets = self.client.wait_command_result()
		if response != OK:
			print("Got error when receiving status", ' '.join([messages, octets]))
			return None

		for i in range(1, int(messages)):
			err = self.client.send_command("RETR", i)
			if err:
				print("Error when sending retrieve: ", err)
				return None

			response, octets, info = self.client.wait_command_result()
			if response != OK:
				print("Got error when receiving message", ' '.join([octets, info]))
				return None

			lines = self.client.wait_multi_line()
			save_message(self.client.user, lines)
			err = self.client.send_command("DELE", i)
			if err:
				print("Error when sending delete: ", err)
				return None

			response, message, info = self.client.wait_command_result()
			if response != OK:
				print("Got error when receiving delete", ' '.join([message, info]))
				return None

		return QuitState(self.client)

class QuitState():
	def __init__(self, client):
		self.client = client

	def run(self):
		self.client.quit()
		return None

def save_message(user, lines):
	pass


def connect_to_server(config):
	client = Client()
	client.user = config.get('username','')
	client.password = config.get('password','')
	error = client.connect(config.get('host','127.0.0.1'), config.get('port',110))
	return client, error

def load_config():
	config = ConfigParser.ConfigParser()
	config.read("./client.ini")
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

def pull_for_server(config):
	print("Starting mail collection for ", config.get(host,'127.0.0.1'), config.get(port,'110'))
	client, error = connect_to_server(config)
	if error:
		print("Error connecting to server",  error)
		return

	client.run()

def pull_mails(config):
	scheduler = sched.scheduler(time.time, time.sleep)
	for server in config:
		serverConfig = config[server]
		scheduler.enter(10, 1, pull_for_server, [serverConfig])

	scheduler.run()


if __name__ == "__main__":
	config = load_config()
	try:
		print("config loaded")
		pull_mails(config)
	except Exception as e:
		print("Exception ", e)
		traceback.print_exc()