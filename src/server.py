import pickle
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Lock

import bcrypt
from rich import print

from enums import RequestType, ResponseCode
from models import LoginRequestDto, Request, Response, User, Message


def hash_password(password: str) -> str:
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


class Server:

    def __init__(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.users: dict = {}
        self.messages: dict = {}
        self.lock = Lock()

    def client(self, sock: socket):
        print('Received connection from ' + str(sock.getpeername()))

        while True:
            request: Request = pickle.loads(sock.recv(1024))

            match request.request_type:

                # Register
                case RequestType.REGISTER:
                    user: User = request.body

                    # Username validation
                    if user.username in self.users.keys():
                        Response(ResponseCode.ERROR, 'Username already registered').send(sock)
                        print(f'User tried {user.username} to register, but already registered')
                        continue

                    with self.lock:
                        self.users[user.username] = user

                    user.password = hash_password(user.password)

                    Response(ResponseCode.SUCCESS, 'User registered').send(sock)
                    print(f'User {user.username} registered')

                # Login
                case RequestType.LOGIN:
                    login_request: LoginRequestDto = request.body

                    if login_request.username not in self.users.keys():
                        Response(ResponseCode.ERROR, 'Wrong username or password').send(sock)
                        print(f'User tried {login_request.username} to login, but not registered')
                        continue

                    target: User = self.users[login_request.username]

                    if not verify_password(login_request.password, target.password):
                        Response(ResponseCode.ERROR, 'Wrong username or password').send(sock)
                        print(f'User tried {login_request.username} to login, but wrong credentials')
                        continue

                    #if not target.password == login_request.password:
                    #    Response(ResponseCode.ERROR, 'Wrong username or password').send(sock)
                    #    print(f'User tried {login_request.username} to login, but wrong credentials')
                    #    continue

                    Response(ResponseCode.SUCCESS, f'Successfully logged in as {target.name}').send(sock)
                    print(f'User {login_request.username} logged in successfully')

                # Send message
                case RequestType.MESSAGE:
                    message: Message = request.body

                    if not message.recipient in self.users.keys():
                        Response(ResponseCode.ERROR, f'Unknown recipient "{message.recipient}"').send(sock)
                        print(f'User {message.sender} tried to send message to {message.recipient}, but not found')
                        continue

                    if message.recipient == message.sender:
                        Response(ResponseCode.ERROR, 'You can not send an email to yourself').send(sock)
                        print(f'User {message.sender} tried to email themselves')
                        continue

                    if not self.messages.get(message.recipient):
                        self.messages[message.recipient] = []

                    with self.lock:
                        self.messages[message.recipient].append(message)

                    Response(ResponseCode.SUCCESS, f'Message sent successfully').send(sock)
                    print(f'User {message.sender} sent message to {message.recipient}')

                # Download messages
                case RequestType.DOWNLOAD_MESSAGE:
                    username = request.body

                    if not username in self.messages.keys():
                        Response(ResponseCode.ERROR, f'There are no messages for the user "{username}"').send(sock)
                        print(f'User {username} tried to download messages, but they were not found')
                        continue

                    if len(self.messages[username]) == 0:
                        Response(ResponseCode.ERROR, f'There are no messages for the user "{username}"').send(sock)
                        print(f'User {username} tried to download messages, but there were no messages')
                        continue

                    # Download and clean server messages for user
                    with self.lock:
                        messages = self.messages.get(username)
                        self.messages[username] = []

                    Response(ResponseCode.SUCCESS, messages).send(sock)
                    print(f'User {username} successfully downloaded messages')

                # Default
                case _:
                    Response(ResponseCode.BAD_REQUEST, 'Unknown request type').send(sock)
                    print(f'Unknown request received from {sock.getpeername()[0]}')

    def listen(self, host: str = '0.0.0.0', port: int = 8000):
        self.socket.bind((host, port))
        self.socket.listen()

        print(f'Listening on {host} port {port}...')

        while True:
            sock, addr = self.socket.accept()
            client_handler = Thread(target=self.client, args=(sock,))
            client_handler.start()


if __name__ == '__main__':
    server = Server()
    server.listen()
