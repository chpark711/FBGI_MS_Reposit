import socket
from time import sleep
import struct


class FBGI_BIN_HDR_V0:
    HDR_SZ = 24
    def __init__(self,  hdr=b''):
        # print(len(hdr))
        if ( (hdr!=None) and (len(hdr)>=self.HDR_SZ) ):
            self.tot_packet_count,  self.tot_fbg_count = struct.unpack('HH',  hdr[0:4])
            self.tot_count_of_channel_with_sensors = struct.unpack('b',  hdr[4:5])
            self.tot_data_size,  self.tot_trans_count = struct.unpack('ii', hdr[5:13] )
            self.reserve = struct.unpack('11s',  hdr[13:24])

    def print_info(self):
        msg1 = 'tot_packet_count={}, tot_fbg_count={}\r\n'.format(self.tot_packet_count,  self.tot_fbg_count)
        msg2 = 'tot_count_of_channel_with_sensors={}\r\n'.format(self.tot_count_of_channel_with_sensors)
        msg3 = 'tot_data_size={}, tot_trans_count={},\r\n'.format(self.tot_data_size,  self.tot_trans_count)
        # print(msg1 + msg2 + msg3)

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
            self.SET_SOUR(True)
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
        # print(toBe_send_cmd)
        # print(type(toBe_send_cmd))
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
            return nRet
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

    def SET_SOUR(self, nIsON):
        return self.Dev_Send_Msg("SOUR %d" % nIsON)

    def SET_CHANNEL(self, nChannel, isEnable):
        return self.Dev_Send_Msg("CHAN %d,%d" % (nChannel, isEnable))

    def Get_CHANNEL(self, nChannel, respons_msg):
        return self.Dev_Query_Msg('CHAN? %d' % nChannel, respons_msg)

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

    def GET_MeasStat(self, respons_msg):
        return self.Dev_Query_Msg('MSTAT?', respons_msg)

    def SET_MeasStart(self):
        return self.Dev_Send_Msg("START")

    def SET_MeasStop(self):
        return self.Dev_Send_Msg("STOP")


    def GET_BIN_MFBG(self, respons_msg):
        nRet = self.Dev_Send_Msg("MFBG?")
        if nRet == -1:
            return nRet
        sleep(0.02)
        nRet = self.Dev_Get_Bin_for_mfbg(respons_msg)
        return nRet

    def Dev_Get_Bin_for_mfbg(self, respons_msg, sleep_sec=0.1, buff_size=1024, time_out_sec=2):
        ''' function for read:bin:temp? read:bin:data:stokes? '''
        # return: hdr, data
        hdr_data = self.m_Socket.recv(FBGI_BIN_HDR_V0.HDR_SZ)
        if (len(hdr_data) != FBGI_BIN_HDR_V0.HDR_SZ):
            return -1
        hdr = FBGI_BIN_HDR_V0(hdr_data)
        # hdr.print_info()

        bytes_left = hdr.tot_data_size
        data = b''
        data += hdr_data
        while (bytes_left > 0):
            read_bin = self.m_Socket.recv(bytes_left)
            nread = len(read_bin)
            if (nread == 0):
                break
            bytes_left -= nread
            data += read_bin

        if bytes_left != 0:
            return -1
        # to_be_read_pos = 0
        # data_size = 4
        # for packet_no in range(0,hdr.tot_packet_count):
        #     tmp_channel = struct.unpack('f', data[to_be_read_pos:(to_be_read_pos+data_size)])
        #     to_be_read_pos += data_size
        #     tmp_sensorCount = struct.unpack('f', data[to_be_read_pos:(to_be_read_pos+data_size)])
        #     to_be_read_pos += data_size
        #
        #     nSensorCount = (int)(tmp_sensorCount[0])
        #     for sensor_No in range(0, nSensorCount):
        #         sennsor_val = struct.unpack('f', data[to_be_read_pos:(to_be_read_pos+data_size)])
        #         print("CH:%f, SensorNo:%d, Data:%f, Data Pos: %d, " % (tmp_channel[0], sensor_No, sennsor_val[0], to_be_read_pos))
        #         # TO DO
        #         to_be_read_pos += data_size

        # respons_msg.append(hdr)
        respons_msg.append(data)
        return 0


    def Handle_Command(self, cmd, pararmList, isQuery, response):
        nRet = 0;
        if isQuery == True:
            if cmd == "IDN":
                nRet = self.Get_IDN(response)
            elif cmd == "GET_SPEC":
                nRet = self.GET_SPEC(response)
            elif cmd == "GET_SPAN":
                nRet = self.GET_SPAN(response)
            elif cmd == "GET_MFBG":
                nRet = self.GET_BIN_MFBG(response)
            elif cmd == "GET_CHAN":
                nChannel = int(pararmList[0])
                nRet = self.Get_CHANNEL(nChannel, response)
            return nRet
        else:
            if cmd == "SET_OUTPUTLEV":
                nChannel = int(pararmList[0])
                output_lev = int(pararmList[1])
                nRet = self.SET_ICUR(nChannel,output_lev)
                response.append('NULL')
                # print("SET_OUTPUTLEV")

            elif cmd == "SET_CHAN":
                nChannel = int(pararmList[0])
                nEnable = int(pararmList[1][0:1])
                nRet = self.SET_CHANNEL(nChannel, nEnable)
                response.append('NULL')
                # print("SET_CHAN")

            elif cmd == "SET_SPEC":
                nChannel = int(pararmList[0])
                nGain = int(pararmList[1])
                nIntegralTime = int(pararmList[2])
                nRet = self.SET_SSPEC(nChannel,nGain,nIntegralTime)
                response.append('NULL')
                # print("SET_SPEC")

            elif cmd == "SET_THRELEV":
                nChannel = int(pararmList[0])
                threshold = int(pararmList[1])
                nRet = self.SET_THRE(nChannel, threshold)
                response.append('NULL')
                # print("SET_THRELEV")

            elif cmd == "START_MEAS":
                nRet = self.SET_MeasStart()
                response.append('NULL')
                # print("START_MEAS")

            elif cmd == "STOP_MEAS":
                nRet = self.SET_MeasStop()
                response.append('NULL')
                # print("START_MEAS")
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
    sleep(0.5)

    nRet = dev_fi3000.SET_SOUR(1)
    sleep(0.5)

    nRet = dev_fi3000.SET_CHANNEL(2, 1)
    sleep(0.5)

    nRet = dev_fi3000.SET_MeasStart()
    sleep(0.5)

    # Get Meas Stat
    response_msg.clear()
    dev_fi3000.GET_MeasStat(response_msg)
    print("MEAS STAT" + response_msg[0])


    # Get Meas Stat
    response_msg.clear()
    response_data = b''

    nRsponseRet = dev_fi3000.GET_BIN_MFBG(response_msg)
    if nRsponseRet != 0:
        print("Failed reading current binary data!")

    response_data = response_msg[0]

    hdr_data = (response_data[0:FBGI_BIN_HDR_V0.HDR_SZ])
    hdr = FBGI_BIN_HDR_V0(hdr_data)
    hdr.print_info()

    data = response_data[FBGI_BIN_HDR_V0.HDR_SZ:]

    to_be_read_pos = 0
    data_size = 4
    for packet_no in range(0, hdr.tot_packet_count):
        tmp_channel = struct.unpack('f', data[to_be_read_pos:(to_be_read_pos + data_size)])
        to_be_read_pos += data_size
        tmp_sensorCount = struct.unpack('f', data[to_be_read_pos:(to_be_read_pos + data_size)])
        to_be_read_pos += data_size

        nSensorCount = (int)(tmp_sensorCount[0])
        for sensor_No in range(0, nSensorCount):
            sennsor_val = struct.unpack('f', data[to_be_read_pos:(to_be_read_pos + data_size)])
            print("CH:%f, SensorNo:%d, Data:%f, Data Pos: %d, " % (
            tmp_channel[0], sensor_No, sennsor_val[0], to_be_read_pos))
            # TO DO
            to_be_read_pos += data_size


    # print("MEAS STAT" + response_msg[0])


    # Get Meas Info
    #response_msg.clear()
    #dev_fi3000.Get_MeasInfo(response_msg)
    #print(response_msg)


    # # Get MeasCont
    # response_msg.clear()
    # nRet = dev_fi3000.GET_Meas_Cont(response_msg)
    # nMeasStatus = int(response_msg[0])
    # print('MEAS STATUS : %d' % nMeasStatus)
    #
    # if nMeasStatus == 0:
    #     nRet = dev_fi3000.SET_Meas_Cont(True)
    # else:
    #     nRet = dev_fi3000.SET_Meas_Cont(False)

    # Get MeasCont
    # response_msg.clear()
    # nRet = dev_fi3000.GET_Meas_Cont(response_msg)
    # nMeasStatus = int(response_msg[0])
    # print('MEAS STATUS : %d' % nMeasStatus)

    # Disconnect
    nRet = dev_fi3000.Dev_Disconnect()
    print('Bye~')
































