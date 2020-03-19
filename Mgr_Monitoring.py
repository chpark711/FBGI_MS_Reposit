from Hdl_FBGI_Device import *

class Mgr_Monitoring:


    def __init__(self):
        self.m_dev_fi3000 = Handle_FBGI_Device()
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

    def Handle_Command(self, cmd_msg, cmd_response):
        print("Call Handle_Command")
        cmd_nReturn = 0
        singleCmd = cmd_msg
        singleCmd_parts = singleCmd.split(':')
        cmd_target = singleCmd_parts[0]
        cmd_type = singleCmd_parts[1]
        cmd_name = singleCmd_parts[2]
        cmd_params = singleCmd_parts[3].split(',')

        if cmd_type == 'SET':
            print('single cmd type is set')
            if cmd_target == 'FBGI':
                cmd_nReturn = self.m_dev_fi3000.Handle_Command(cmd_name, cmd_params, False,cmd_response)
                print("Do")
            else:
                print("Device is not supported")

        elif cmd_type== 'GET':
            print('single cmd type is get')
            if cmd_target == 'FBGI':
                cmd_nReturn = self.m_dev_fi3000.Handle_Command(cmd_name, cmd_params, True, cmd_response)
                print("Do")
            else:
                print("Device is not supported")

        return cmd_nReturn;

# Test
def main():
    mon_mgr = Mgr_Monitoring()
if __name__ == '__main__':
     main()