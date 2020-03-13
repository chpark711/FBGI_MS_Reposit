#   Python Network Programming Cookbook -- Chapter - 2
#   This program is optimized for Python 2.7.
#   It may run on any other version with/without modifications.

import socket
import threading
import socketserver

from time import sleep
from configparser import ConfigParser

from Mgr_Monitoring import *
from Mgr_DataService import *

# tells the kernel to pickup a port dynamically
BUF_SIZE = 5120

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """ Nothing to add here, inherited everythin necessary from parents """
    pass

class Server_RequestHandler(socketserver.BaseRequestHandler):

    m_DataService_Mgr = Mgr_DataService()
    m_Mornitoring_Mgr = Mgr_Monitoring()

    # def __init__(self):
    #     print("Server_RequestHandler init...")

    def init_MonitoringMgr():
        print("Init - MonitoringMgr")

    def init_DataServiceMgr():
        print("Init - DataServiceMgr")

    def init_Server():
        print("init - Server")

    """ An example of threaded TCP request handler """
    def handle(self):
        while True:
            data = self.request.recv(BUF_SIZE)
            cur_thread = threading.current_thread()
            log = "[%s] %s" % (cur_thread.name, data.decode())
            print(log)

            str_req_msg = data.decode().strip()
            str_response = ""

            str_terminal = "\r\n"

            # Handling Request
            if str_req_msg == "GET_DATA":
                str_response = self.m_DataService_Mgr.Get_Data()
            elif str_req_msg == "SET_SETTINGS":
                str_response = self.m_Mornitoring_Mgr.Set_Settings_on_device()

            elif str_req_msg == "Close":
                str_response = "Socket is closing..." + str_terminal
                self.request.sendall(str_response.encode())
                break
            else:
                str_response = "Unknown command."

            str_response = str_response + str_terminal
            self.request.sendall(str_response.encode())

def main_():

    DEFAULT_SERVER_HOST = 'localhost'
    DEFAULT_SERVER_PORT = 8887

    # Run server
    server = ThreadedTCPServer((DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT), Server_RequestHandler)
    ip, port = server.server_address  # retrieve ip address

    # Start a thread with the server -- one thread per request
    server_thread = threading.Thread(target=server.serve_forever)

    # Exit the server thread when the main thread exits
    server_thread.daemon = True
    server_thread.start()

    # Run clients
    # client(ip, port, "Hello from client 1")
    # client(ip, port, "Hello from client 2")
    # client(ip, port, "Hello from client 3")
    # client(ip, port, "exit")

    while True:
        sleep(0.5)
        print("Main thread running....")

    # Server cleanup
    print("Server shutdown....")
    server.shutdown()
    print("Main thread closed !!!")

# def main():
#     m_ReqHandler = Server_RequestHandler()
#
# if __name__ == '__main__':
#     main()











