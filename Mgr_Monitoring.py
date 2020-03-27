from Hdl_FBGI_Device import *
import threading

class Mgr_Monitoring:


    def __init__(self):
        self.m_dev_fi3000 = Handle_FBGI_Device()
        self.m_isMonitor_senssing = False
        self.m_Thread_Monitor_Sensing = None
        # Connect
        nRet = self.m_dev_fi3000.Dev_Conndect('192.168.1.74', 4000)
        if self.m_dev_fi3000.m_isConnected == True:
            print("FBGI device opened!")
        else:
            print("FBGI device not opened!")

        print("Init Mgr_Monitoring ...")

    def Set_Settings_on_device(self,cmd_respond):
        cmd_respond = "Call Set_Settings_on_device"
        print(cmd_respond)
        return 0

    def Set_Monitor(self, isStart):
        if isStart == 1:
            self.m_isMonitor_senssing = True
            self.m_Thread_Monitor_Sensing = threading.Thread(target=self.Do_Monitor_Sensing)
            self.m_Thread_Monitor_Sensing.start()
        else:
            self.m_isMonitor_senssing = False
            self.m_Thread_Monitor_Sensing.join()
        return 0

    def Do_Monitor_Sensing(self):
            while True:
                if self.m_isMonitor_senssing == False:
                    break

                print("Do_Monitor_Sensing....")
                response_msg = []
                response_data = b''

                nRsponseRet = self.m_dev_fi3000.GET_BIN_MFBG(response_msg)
                if nRsponseRet != 0:
                    print("Failed reading current binary data!")
                    continue

                response_data = response_msg[0]

                hdr_data = (response_data[0:FBGI_BIN_HDR_V0.HDR_SZ])
                data = response_data[FBGI_BIN_HDR_V0.HDR_SZ:]

                hdr = FBGI_BIN_HDR_V0(hdr_data)
                hdr.print_info()

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

                sleep(1)
            print("STOP Do_Monitor_Sensing!!!")

    def Handle_Command(self, cmd_msg, cmd_response):
        # print("Call Handle_Command")
        cmd_nReturn = 0
        singleCmd = cmd_msg.strip()
        singleCmd_parts = singleCmd.split(':')
        cmd_target = singleCmd_parts[0]
        cmd_type = singleCmd_parts[1]
        cmd_name = singleCmd_parts[2]
        cmd_params = singleCmd_parts[3].split(',')

        if cmd_type == 'SET':
            # print('single cmd type is set')
            if cmd_target == 'FBGI':
                cmd_nReturn = self.m_dev_fi3000.Handle_Command(cmd_name, cmd_params, False,cmd_response)
                # print("Do")
            else:
                print("Device is not supported")

        elif cmd_type== 'GET':
            # print('single cmd type is get')
            if cmd_target == 'FBGI':
                cmd_nReturn = self.m_dev_fi3000.Handle_Command(cmd_name, cmd_params, True, cmd_response)
                # print("Do")
            else:
                print("Device is not supported")

        return cmd_nReturn;

# Test
def main():
    mon_mgr = Mgr_Monitoring()

    print("Thread Start... !!!")
    mon_mgr.Set_Monitor(1)

    nCount = 0

    while True:
        if nCount == 10:
            break
        nCount = nCount + 1
        print("Main Operation !!!!")
        sleep(1)

    print("Thread Stop... !!!")
    mon_mgr.Set_Monitor(0)

    nCount = 0
    while True:
        if nCount == 5:
            break
        print("Main Operation !!!!")
        nCount = nCount + 1
        sleep(1)



if __name__ == '__main__':
     main()