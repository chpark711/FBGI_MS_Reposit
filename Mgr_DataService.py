

class Mgr_DataService:
    def __init__(self):
        print("Init Mgr_DataService ...")

    def Get_Data(self):
        print("Call GetData")
        return "Processed Data in database!"

# Test
def main():
    dataService_mgr = Mgr_DataService()
if __name__ == '__main__':
     main()