import status

class TransactionState():
	def __init__(self, handler):
		self.handler = handler
		self.commands = {
			"stat": self.handle_stat,
			"list": self.handle_list,
			"retr": self.handle_retr,
			"dele": self.handle_dele,
			"noop": self.handle_noop,
			"rset": self.handle_rset,
			"uidl": self.handle_uidl,
			"quit": self.handle_quit
		}

	def run(self):
		self.handler.load_and_lock()

		while True:
			command, content = self.handler.wait_receive()
			if not self.commands.__contains__(command):
				self.handler.send_error("Cannot execute such a command right now")
			else:
				if self.commands[command](content):  # TODO exit out
					return None

	def handle_list(self, content):
		if len(content) == 0:
			not_deleted = self.handler.not_deleted_mails()
			self.handler.send_response(status.OK, str(len(not_deleted)), "Messages")
			for i, mail in enumerate(not_deleted):
				self.handler.send_to_client(str(i) + " " + str(mail.size()) + "\r\n")

			self.handler.send_to_client(".\r\n")
		else:
			index = -1
			not_deleted = self.handler.not_deleted_mails()
			try:
				index = int(content[0]) - 1
			except:
				self.handler.send_error("Invalid index")

			if len(not_deleted) <= index or index == -1:
				self.handler.send_error("Invalid message index")
			else:
				self.handler.send_response(status.OK, str(index), str(not_deleted[index].size()))

	def handle_stat(self, content):
		not_deleted = self.handler.not_deleted_mails()
		contentlength = 0
		for mail in not_deleted:
			if not mail.deleted:
				contentlength += mail.size()

		self.handler.send_response(status.OK, str(len(not_deleted)), str(contentlength))

	def handle_retr(self, content):
		if len(content) == 0:
			self.handler.send_error("Invalid message index")
			return

		index = -1
		try:
			index = int(content[0]) - 1
		except:
			self.handler.send_error("Invalid index")

		if len(self.handler.mails) <= index or index == -1:
			self.handler.send_error("Invalid message index")
		else:
			if self.handler.mails[index].deleted:
				self.handler.send_error("Message is marked as deleted")
			else:
				self.handler.send_response(status.OK, "Message", "will follow")
				mail = self.handler.mails[index]
				for line in mail.content:
					self.handler.send_to_client(line + "\r\n")

				self.handler.send_to_client(".\r\n")

	def handle_dele(self, content):
		if len(content) == 0:
			self.handler.send_error("Invalid message index")
			return

		index = -1
		try:
			index = int(content[0]) - 1
		except:
			self.handler.send_error("Invalid index")

		if len(self.handler.mails) <= index or index == -1:
			self.handler.send_error("Invalid message index")
		else:
			if self.handler.mails[index].deleted:
				self.handler.send_error("Message is marked as deleted")
			else:
				self.handler.mails[index].deleted = True
				self.handler.send_response(status.OK, "Message", "deleted")

	def handle_noop(self, content):
		self.handler.send_status(status.OK)

	def handle_rset(self, content):
		for mail in self.handler.mails:
			mail.deleted = False

		self.handler.send_response(status.OK, "Mail", "deletion stopped")

	def handle_uidl(self, content):
		if len(content) == 0:
			not_deleted = self.handler.not_deleted_mails()
			self.handler.send_response(status.OK, str(len(not_deleted)), "Messages")
			for i, mail in enumerate(not_deleted):
				self.handler.send_to_client(str(i) + " " + mail.uid + "\r\n")

			self.handler.send_to_client(".\r\n")

		else:
			index = -1
			not_deleted = self.handler.not_deleted_mails()
			try:
				index = int(content[0]) - 1
			except:
				self.handler.send_error("Invalid index")

			if len(not_deleted) <= index or index == -1:
				self.handler.send_error("Invalid message index")
			else:
				self.handler.send_response(status.OK, str(index), not_deleted[index].uid)

	def handle_quit(self, content):
		self.handler.delete_marked()
		self.handler.unlock()
		return True