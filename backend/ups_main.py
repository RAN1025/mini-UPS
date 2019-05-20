# system lib
import socket
import select
from _thread import *
import threading
from concurrent.futures import ThreadPoolExecutor
import psycopg2
import signal

# google protobuf
import world_ups_pb2 as wupb
import ups_amazon_pb2 as uapb

# self-written lib
from tool import *
from database import *


# Connect to World
def ConnectWorld(world_addr, world_port):
    print('Connecting to World...')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((world_addr, world_port))
    return s


# Connect to Amazon
def ConnectAmazon(amazon_addr, amazon_port):
    print('Connecting to Amazon...')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((amazon_addr, amazon_port))
    return s


# Start interaction with World
def StartWorld(wSock, aSock, db):
    print('world starts')
    
    # once done getting connection, can start listen and process once receive
    while True:
    
        with world_lock:
            UResponse = URecv(wSock)

        # process response with thread
        t1 = threading.Thread(target = ProcessURes,args=(UResponse, wSock, aSock, db))
        t1.start()
        t1.join()

        
# Start interaction with Amazon
def StartAmazon(wSock, aSock, db):
    print('amazon start')

    #start listen and process once receive
    while True:
        
        with amazon_lock:
            AResponse = ARecv(aSock)

        #process response with thread
        t1 = threading.Thread(target = ProcessARes,args=(AResponse, aSock, wSock, db))
        t1.start()
        t1.join()


# Start database, return the connection    
def DataBase():
    global world
    conn = Connectdb()
    if not world:
        Droptable(conn)
        Createtable(conn)
    print('construct needed table in the database, set up postgresql')
    return conn


def Main():
    global wHost
    global wPort
    global aHost
    global aPort
    global world

    # connect to world, return a socket
    print(wHost, wPort)
    wSock = ConnectWorld(wHost, wPort)
    
    # connect to amazon, return a socket
    aSock = ConnectAmazon(aHost, aPort)
    
    # set up database
    db = DataBase()

    world = GetWorld(wSock,world,db)
    message = uapb.AUConnect()
    message.worldid = world
    Send(aSock,message)
    
    # Thread
    try:
        t1 = threading.Thread(target = StartWorld,args=( wSock, aSock, db,))
        t2 = threading.Thread(target = StartAmazon,args=( wSock, aSock, db,))
        t3 = threading.Thread(target = PacketDrop,args=( wSock, aSock, db,))
        t4 = threading.Thread(target = QueryTruck,args=(wSock,aSock,db,))
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t1.join()
        t2.join()
        t3.join()
        t4.join()
    except KeyboardInterrupt:
        print('Keyboard Interruption')
    finally:
        print('close')
        wSock.close()
        aSock.close()


# Global variable needed before starting
#wHost = 'vcm-8250.vm.duke.edu'
wHost = 'vcm-5869.vm.duke.edu'
wPort = 12345
#aHost = '152.3.53.20'
aHost = 'vcm-8250.vm.duke.edu'
#aHost = 'vcm-8230.vm.duke.edu'
aPort = 55555
world = 0

# main
if __name__ == '__main__':
    Main()
