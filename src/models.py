import pickle
from datetime import datetime
from socket import socket

from src.enums import RequestType, ResponseCode


class LoginRequestDto:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


class User:
    def __init__(self, name: str, username: str, password: str):
        self.name = name
        self.username = username
        self.password = password


class Message:
    def __init__(self, sender: str, recipient: str, subject: str, body: str):
        self.sender = sender
        self.recipient = recipient
        self.date = datetime.now()
        self.subject = subject
        self.body = body

    def __repr__(self):
        return f"""From: {self.sender}
To: {self.recipient}
At: {self.date}
Subject: {self.subject}
Body: {self.body}"""


class Response:
    def __init__(self, code: ResponseCode, content: any):
        self.code: ResponseCode = code
        self.content: any = content

    def send(self, sock: socket):
        sock.sendall(pickle.dumps(self))


class Request:
    def __init__(self, request_type: RequestType, body: any):
        self.request_type: RequestType = request_type
        self.body: any = body

    def send(self, sock: socket) -> Response:
        sock.sendall(pickle.dumps(self))
        response: Response = pickle.loads(sock.recv(1024))
        return response
