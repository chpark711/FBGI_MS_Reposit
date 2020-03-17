#   Python Network Programming Cookbook -- Chapter - 2
#   This program is optimized for Python 2.7.
#   It may run on any other version with/without modifications.

import socket
import threading
import socketserver
import struct

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

            # Unpacking binary packet
            recv_data = struct.unpack('lHHHH512siihhi1024s', data)
            print(recv_data)

             # Command
            recv_cmd = recv_data[5].decode().strip()
            print(type(recv_cmd))

            log = "[%s] %s" % (cur_thread.name, recv_cmd)
            print(log)

            str_req_msg = recv_cmd
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
            n_response_size = len(str_response)

            list_resp = list(recv_data)
            list_resp[0] = n_response_size
            list_resp.append(str_response.encode())

            tp_resp = tuple(list_resp)

            print(len(tp_resp))

            strFormat = 'lHHHH512siihhi1024s%is' % n_response_size

            respond_data = struct.pack(strFormat,
                                       tp_resp[0],tp_resp[1],tp_resp[2],tp_resp[3],tp_resp[4],
                                       tp_resp[5],tp_resp[6],tp_resp[7],tp_resp[8],tp_resp[9],
                                       tp_resp[10],tp_resp[11],tp_resp[12])

            self.request.sendall(respond_data)
            # self.request.sendall(str_response.encode())

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











