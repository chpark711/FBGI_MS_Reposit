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

        if Tot_sentMsg == 0:
            return -1
        return 0

    def Dev_Get_Msg(self, respons_msg,  buff_size=10240):
        if (self.m_isConnected == False):
            return ''
        nRet = 0
        try:
            data = self.m_Socket.recv(buff_size).decode()
            self.m_previous_read_buffer = data
            # print ('Received', repr(data))
        except socket.timeout:
            print('-----------------read(): timeout error for command: ' + self.m_previous_write_buffer)
            print('-----------------socket timeout: ' + str(self.m_Socket.gettimeout()))
            # s = datetime.datetime.now()
            # print (s)
            data = ''
            nRet = -1
        respons_msg.append(data)
        return nRet

    def Dev_Query_Msg(self, msg, strResponsMsg, sleep_sec=0.1, buff_size=1024, time_out_sec=2):
        nRet = self.Dev_Send_Msg(msg)
        if nRet == -1:
            return strResponsMsg
        sleep(sleep_sec)
        nRet = self.Dev_Get_Msg(strResponsMsg)
        return nRet

    def Get_IDN(self, respons_msg):
        return self.Dev_Query_Msg('*IDN?', respons_msg)

    def Get_MeasInfo(self, respons_msg):
        return self.Dev_Query_Msg('MEAS:INFO?', respons_msg)

    def SET_Meas_Cont(self, bIsCont):
        nRet = 0
        if bIsCont == True:
            nRet = self.Dev_Send_Msg("MEAS:CONT 1")
        else:
            nRet = self.Dev_Send_Msg("MEAS:CONT 0")
        return nRet

    def SET_ICUR(self, nChannel, nCurrent):
        return self.Dev_Send_Msg("ICUR %d" % nCurrent)

    def SET_SSPEC(self, nChannel, nGain, nInteTime):
        return self.Dev_Send_Msg("SSPEC %d,%d,%d" % (nChannel, nGain, nInteTime))

    def SET_THRE(self, nChannel, nThreshold):
        return self.Dev_Send_Msg("THRE %d,%d" % (nChannel, nThreshold))

    def GET_SPEC(self, respons_msg):
        return self.Dev_Query_Msg('SPEC?', respons_msg)

    def GET_SPAN(self, respons_msg):
        return self.Dev_Query_Msg('SPAN?', respons_msg)

    def GET_Meas_Cont(self, respons_msg):
        return self.Dev_Query_Msg('MEAS:CONT?', respons_msg)

    def Handle_Command(self, cmd, pararmList, isQuery, response):
        nRet = 0;
        if isQuery == True:
            if cmd == "IDN":
                nRet = self.Get_IDN(response)
            elif cmd == "GET_SPEC":
                nRet = self.GET_SPEC(response)
            elif cmd == "GET_SPAN":
                nRet = self.GET_SPAN(response)
            return nRet
        else:
            if cmd == "SET_OUTPUTLEV":
                nChannel = int(pararmList[0])
                output_lev = int(pararmList[1])
                nRet = self.SET_ICUR(nChannel,output_lev)
                response.append('NULL')
                print("SET_OUTPUTLEV")
            elif cmd == "SET_SPEC":
                nChannel = int(pararmList[0])
                nGain = int(pararmList[1])
                nIntegralTime = int(pararmList[2])
                nRet = self.SET_SSPEC(nChannel,nGain,nIntegralTime)
                response.append('NULL')
                print("SET_SPEC")
            elif cmd == "SET_THRELEV":
                nChannel = int(pararmList[0])
                threshold = int(pararmList[1])
                nRet = self.SET_THRE(nChannel, threshold)
                response.append('NULL')
                print("SET_THRELEV")
            else:
                print("else")
                nRet = -1

            return nRet

if __name__=='__main__':

    dev_fi3000 = Handle_FBGI_Device()

    # Connect
    nRet = dev_fi3000.Dev_Conndect('192.168.1.74', 4000)

    # Get IDN
    response_msg = []
    dev_fi3000.Get_IDN(response_msg)
    print(response_msg)

    # Get Meas Info
    response_msg.clear()
    dev_fi3000.Get_MeasInfo(response_msg)
    print(response_msg)

    # Get MeasCont
    response_msg.clear()
    nRet = dev_fi3000.GET_Meas_Cont(response_msg)
    nMeasStatus = int(response_msg[0])
    print('MEAS STATUS : %d' % nMeasStatus)

    if nMeasStatus == 0:
        nRet = dev_fi3000.SET_Meas_Cont(True)
    else:
        nRet = dev_fi3000.SET_Meas_Cont(False)

    # Get MeasCont
    response_msg.clear()
    nRet = dev_fi3000.GET_Meas_Cont(response_msg)
    nMeasStatus = int(response_msg[0])
    print('MEAS STATUS : %d' % nMeasStatus)

    # Disconnect
    nRet = dev_fi3000.Dev_Disconnect()
    print('Bye~')
































