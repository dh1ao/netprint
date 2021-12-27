from netprint import NetPrint
from time import sleep

NetPrint(12345).run()

for i in range(100000):
    print("TEST ", i)
    sleep(1)
 
NetPrint.stop()