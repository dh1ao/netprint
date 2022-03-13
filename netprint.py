import threading
from time import sleep
from socket import socket, gethostname
from io import StringIO
import sys


class NetPrint(socket):
    port = None
    throttle = None
    running = False
    outputThread = None
    outputSocket = None
    client = None
    
    def __init__(self, port=65432, throttle=0.1, family=-1, type=-1, proto=-1, fileno=None):
        super().__init__(family, type, proto, fileno)

        NetPrint.port = port
        NetPrint.throttle = throttle
        NetPrint.outputThread = threading.Thread(target=NetPrint.outputLoop)
        
        NetPrint.outputSocket = socket()
        for _ in range(10):
            try:
                NetPrint.outputSocket.bind(('', NetPrint.port))
            except OSError as e:
                if e.errno == 98:
                    print("Waiting")
                    sleep(10)
                
        NetPrint.outputSocket.listen(4)

    @classmethod
    def _redirectOutput(cls):
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        
    @classmethod
    def _restoreOutput(cls):
        if isinstance(sys.stdout, StringIO):
            sys.stdout.close()
        
        if isinstance(sys.stderr, StringIO):
            sys.stderr.close()
        
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        
    @classmethod
    def outputLoop(cls):
        NetPrint.client, _ = NetPrint.outputSocket.accept()
        while(cls.running):
            try:
                so = sys.stdout.getvalue()
                se = sys.stderr.getvalue()
                
                if len(so+se) > 0:
                    cls._restoreOutput()
                    try:
                        NetPrint.client.sendall((so+se).encode())
                    except OSError as e:
                        if e.errno == 32:
                            NetPrint.client, _ = NetPrint.outputSocket.accept()
                    cls._redirectOutput()
                sleep(cls.throttle)
            except (KeyboardInterrupt, OSError):
                cls.stop()

    def __repr__(self):
        # flake8: noqa: 
        rep = f'''StdIONetServer(family={self.family},\
            type={self.type},\
            proto={self.proto},\
            fileno=aFileNo))'''
        return rep.replace('  ', '')

    def __str__(self):
        return f'StdIONetserver addr: {gethostname()} port: {self.port}'
    
    @classmethod
    def run(cls):
        cls._redirectOutput()
        cls.running = True
        if cls.outputThread is not None:
            cls.outputThread.start()
        else:
            raise Exception("NetPrint().run() not NetPrint.run() :)")
        return cls
        
        
    @classmethod
    def stop(cls):
        cls.running = False
        cls._restoreOutput()
        NetPrint.outputSocket.close()
        return cls
        
    @classmethod
    @property
    def is_running(cls):
        return cls.running


if __name__ == "__main__":
    NetPrint(12345).run()
    
    for i in range(100000):
        print("TEST ", i)
        sleep(1)
 
    NetPrint.stop()
    print("Bis gliggens")
