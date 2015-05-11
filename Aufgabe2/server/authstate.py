import status
import transactionstate

class AuthorizationState():
	def __init__(self, handler):
		self.handler = handler

	def run(self):
		account = None
		while True:
			command, content = self.handler.wait_receive()
			if command == 'quit':
				return None
			elif command != 'user':
				self.handler.send_error("Requires user to continue")
			elif len(content) < 1:
				self.handler.send_error("Need username")
			else:
				account = self.handler.server.get_account(content[0])
				if account:
					self.handler.send_response(status.OK, "Accepted", "Username was accepted")
					break
				else:
					self.handler.send_error("No such user")

		while True:
			command, content = self.handler.wait_receive()
			if command == 'quit':
				return None
			elif command != 'pass':
				self.handler.send_error("Requires password to continue")
			elif len(content) < 1:
				self.handler.send_error("Need password")
			else:
				if self.handler.server.try_login(account['name'], content[0]):
					self.handler.account = account
					self.handler.send_response(status.OK, "Accepted", "Successfully authorized")
					break
				else:
					self.handler.send_error("Invalid password")

		return transactionstate.TransactionState(self.handler)
