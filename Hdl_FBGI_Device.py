import socket
from time import sleep

class Handle_FBGI_Device():

    def __init__(self):
        # 소켓 객체를 생성합니다.
        # 주소 체계(address family)로 IPv4, 소켓 타입으로 TCP 사용합니다.
        self.m_isConnected = False
        self.m_previous_write_buffer = ''
        self.m_previous_read_buffer = ''
        self.m_terminalChar = '\r\n'
        self.m_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def Dev_Conndect(self, ip, port):
        ret_isConnected = 0
        try:
            self.m_Socket.settimeout(3)
            self.m_Socket.connect((ip, port))
            self.m_Socket.settimeout(2)
        except socket.error as msg:
            print('connection error')
            ret_isConnected = -1;
            self.m_Socket.close()
            self.m_Socket = None

        # 접속 결과를 멤버에 저장.
        if (ret_isConnected >= 0):
             self.m_isConnected = True
        return ret_isConnected

    def Dev_Disconnect(self):
        # socket close
        if (self.m_isConnected == True):
            self.m_isConnected = False
            self.m_Socket.close()


    def Dev_Send_Msg(self, msg):
        if (self.m_isConnected == False):
            return 0

        if (type(msg) != type(b'')):
            msg = msg + self.m_terminalChar
            toBe_send_cmd = bytes(msg, 'UTF-8')
        else:
            toBe_send_cmd = msg

        Tot_sentMsg = 0
        Tobe_sendMsg = len(toBe_send_cmd)
        print(toBe_send_cmd)
        print(type(toBe_send_cmd))
        while Tot_sentMsg < Tobe_sendMsg:
            Count_sentMsg = self.m_Socket.send(toBe_send_cmd[Tot_sentMsg:])
            if Count_sentMsg == 0:
                raise RuntimeError("socket connection broken")
            Tot_sentMsg = Tot_sentMsg + Count_sentMsg
        return Tot_sentMsg

    def Dev_Get_Msg(self, buff_size=1024):
        if (self.m_isConnected == False):
            return ''

        try:
            data = self.m_Socket.recv(buff_size)
            self.m_previous_read_buffer = data
            # print ('Received', repr(data))
        except socket.timeout:
            print('-----------------read(): timeout error for command: ' + self.m_previous_write_buffer)
            print('-----------------socket timeout: ' + str(self.m_Socket.gettimeout()))
            # s = datetime.datetime.now()
            # print (s)
            data = ''
        return data

    def Dev_Query_Msg(self, msg, sleep_sec=0.1, buff_size=1024, time_out_sec=2):
        strResponsMsg = ''
        nRet = self.Dev_Send_Msg(msg)
        if nRet == 0:
            return strResponsMsg
        sleep(sleep_sec)

        strResponsMsg = self.Dev_Get_Msg()
        return strResponsMsg

    def Get_IDN(self):
        return self.Dev_Query_Msg('*IDN?')

    def Get_MeasInfo(self):
        return self.Dev_Query_Msg('MEAS:INFO?')

    def SET_Meas_Cont(self, bIsCont):
        nRet = 0
        if bIsCont == True:
            nRet = self.Dev_Send_Msg("MEAS:CONT 1")
        else:
            nRet = self.Dev_Send_Msg("MEAS:CONT 0")
        return nRet

    def GET_Meas_Cont(self):
        return self.Dev_Query_Msg('MEAS:CONT?')



if __name__=='__main__':

    dev_fi3000 = Handle_FBGI_Device()

    # Connect
    nRet = dev_fi3000.Dev_Conndect('192.168.1.74', 4000)

    # Get IDN
    print(dev_fi3000.Get_IDN())

    # Get Meas Info
    print(dev_fi3000.Get_MeasInfo())

    # Get MeasCont
    respond_mas = dev_fi3000.GET_Meas_Cont()
    nMeasStatus = int(respond_mas)
    print('MEAS STATUS : %d' % nMeasStatus)

    if nMeasStatus == 0:
        nRet = dev_fi3000.SET_Meas_Cont(True)
    else:
        nRet = dev_fi3000.SET_Meas_Cont(False)

    # Get MeasCont
    nMeasStatus = int(dev_fi3000.GET_Meas_Cont())
    print('MEAS STATUS : %d' % nMeasStatus)

    # Disconnect
    nRet = dev_fi3000.Dev_Disconnect()

    print('Bye~')
































