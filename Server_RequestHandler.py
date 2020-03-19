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

HDR_FORMAT = 'lHHHH512siihhi1024s'


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """ Nothing to add here, inherited everythin necessary from parents """
    pass

class Server_RequestHandler(socketserver.BaseRequestHandler):

    m_DataService_Mgr = Mgr_DataService()
    m_Mornitoring_Mgr = Mgr_Monitoring()

    str_terminal = "\r\n"

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
            recv_data = struct.unpack(HDR_FORMAT, data)
            print(recv_data)

             # Command
            recv_cmd = recv_data[5].decode().strip()
            log = "[%s] %s" % (cur_thread.name, recv_cmd)
            print(log)

            # Command List
            tobe_excute_cmdList = recv_cmd.split('^')
            count_of_cmdList = len(tobe_excute_cmdList)

            str_response = []
            str_response_msg = ''
            cmd_return = 0

            nIndex_of_cmd = 0
            for msg in tobe_excute_cmdList:
                print(msg)
                str_req_msg = msg
                cmd_property_list = str_req_msg.split(":")
                cmd_target = cmd_property_list[0]
                str_response.clear()

                # Handling Request
                if cmd_target[:4] == "FBGI" or cmd_target[:3] == "DTS":
                    cmd_return = self.m_Mornitoring_Mgr.Handle_Command(str_req_msg, str_response)
                elif str_req_msg[:12] == "DB":
                    cmd_return = self.m_Mornitoring_Mgr.Set_Settings_on_device(str_response)
                elif str_req_msg[:5] == "Close":
                    str_response[0] = "Socket is closing..." + self.str_terminal
                    cmd_return = 0
                else:
                    str_response[0] = "Unknown command."
                    cmd_return = -1

                nIndex_of_cmd = nIndex_of_cmd + 1;
                if nIndex_of_cmd != count_of_cmdList:
                    str_response_msg = str_response_msg + str_response[0] + '^'
                else:
                    str_response_msg = str_response_msg + str_response[0]

                if cmd_return == -1:
                    break

            # 응답 메세지
            str_response_msg = str_response_msg + self.str_terminal
            n_response_size = len(str_response_msg)

            # 헤더를 수정하기 위한 리스트 변환
            list_resp = list(recv_data)

            # 헤더에 결과값 갱신
            list_resp[0] = n_response_size
            list_resp[8] = cmd_return
            list_resp.append(str_response_msg.encode())

            # Make packet
            strFormat = HDR_FORMAT + ('%is' % n_response_size)
            respond_data = struct.pack(strFormat,
                                       list_resp[0],list_resp[1],list_resp[2],list_resp[3],list_resp[4],
                                       list_resp[5],list_resp[6],list_resp[7],list_resp[8],list_resp[9],
                                       list_resp[10],list_resp[11],list_resp[12])

            # 전송하기.
            self.request.sendall(respond_data)

            # Close 명령어 이면 소켓(클라이언트) 닫기.
            if str_req_msg[:5] == "Close":
                print("Socket is closed!!!")
                break

   # def handle_command(self, data):

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











