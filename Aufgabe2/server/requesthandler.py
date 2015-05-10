import threading
import status
import welcomestate
import mail as mailC
import os
from os import listdir
from os.path import isfile, join, abspath


def parse(response):
	splitted = response.split(' ')
	keyword, args = splitted[0], splitted[1:] if len(splitted) > 1 else []
	for arg in args:
		if len(arg) > 40:
			raise IOError("Invalid argument length")

	return keyword.lower(), args

class RequestHandler(threading.Thread):
	def __init__(self, connection, server):
		super(RequestHandler, self).__init__()
		self.client = connection
		self.server = server
		self.state = welcomestate.WelcomeState(self)
		self.account = None
		self.mails = []

	def run(self):
		while self.state:
			self.state = self.state.run()

		self.send_response(status.OK, "QUIT", "DONE")
		self.client.close()
		self.remove()

	def wait_receive(self):
		data = self.receive()
		if not data:
			print("Could not read for client")
			self.remove()
			return False

		print "Read ", data
		try:
			data = parse(data)
		except Exception as error:
			print(error)
			self.send_error()
			return self.wait_receive()

		return data

	def send_error(self, message = "Message was incorrectly formatted"):
		self.send_response(status.ERR, "Error", message)

	def send_to_client(self, content):
		self.client.send(content)

	def send_response(self, status, command, data):
		self.send_to_client(status + " " + command + " " + data + "\r\n")

	def send_status(self, status):
		self.send_to_client(status + "\r\n")

	def remove(self):
		self.server.on_disconnect(self)
		self.unlock()

	def receive(self):
		try:
			data = self.client.recv(1024)
			if data[-2:] == '\r\n':
				return data[:-2]
			else:
				return self.receive()
		except:
			return None

	def load_and_lock(self):
		self.server.set_logged_in(self.account['username'], True)
		mailboxdir = abspath(join(os.path.dirname(os.path.realpath(__file__)), self.account['maildir']))
		files = [f for f in listdir(mailboxdir) if isfile(join(mailboxdir, f))]
		for file in files:
			mail = mailC.Mail(join(mailboxdir, file))
			self.mails.append(mail)
			mail.load()

	def not_deleted_mails(self):
		return [mail for mail in self.mails if not mail.deleted]

	def delete_marked(self):
		for mail in self.mails:
			if mail.deleted:
				mail.remove()

	def unlock(self):
		self.server.set_logged_in(self.account['username'], False)
		del self.mails[:]