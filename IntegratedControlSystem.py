from Server_RequestHandler import *

DEFAULT_SERVER_HOST = 'localhost'
DEFAULT_SERVER_PORT = 8887

def main():
    # Main Thread start...
    print("MainThread Start...")

    # Server RequestHandler
    server = ThreadedTCPServer((DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT), Server_RequestHandler)
    # Start a thread with the server -- one thread per request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread exits
    server_thread.daemon = True
    server_thread.start()

    while True:
        sleep(0.5)
        print("Main thread running....")

    # Server cleanup
    server.shutdown()
    print("Main thread closed !!!")

if __name__ == '__main__':
    main()

