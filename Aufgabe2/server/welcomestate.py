import status
import authstate

class WelcomeState():
	def __init__(self, handler):
		self.handler = handler

	def run(self):
		self.handler.send_response(status.OK, "POP3", "I'm a teapot")
		return authstate.AuthorizationState(self.handler)