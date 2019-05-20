# system lib
import socket
import threading
from concurrent.futures import ThreadPoolExecutor
import psycopg2
import time
import select
import smtplib, ssl

# google protobuf lib
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint
import world_ups_pb2 as wupb
import ups_amazon_pb2 as uapb

# self-written lib
from database import *

# global variable
world_lock = threading.Lock()
amazon_lock = threading.Lock()
seq_lock = threading.Lock()
SeqNum = 0

# email set up
smtp_server = "smtp.gmail.com"
email_port = 587  # For starttls
sender_email = "568.hw1.yh218.yx139@gmail.com"
password ='QWE123!@#'

# send email to user
def SendEmail(db, packageid):
    global smtp_server
    global email_port
    global sender_email
    global password
    message = 'Your package ' + str(packageid) + ' has been delivered!'
    message = 'Subject: Package Delivered\n\n' + message
    context = ssl.create_default_context()
    receiver_email = GetEmail(db, packageid)
    if receiver_email == -1:
        return
    with smtplib.SMTP(smtp_server, email_port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

        
# Only use this method to send
def Send(sock, msg):
    print('sending out the following: ')
    print(msg)
    req = msg.SerializeToString()
    _EncodeVarint(sock.send, len(req), None)
    sock.send(req)
    print('send finish')


# Only use this method to receive from Amazon
# Return a Message object
def ARecv(sock):
    #    sock_lock.acquire()
    all_data = b''
    data = sock.recv(4)
    if not data:
        print('connection to amazomn is closed')
    data_len, new_pos = _DecodeVarint32(data, 0)
    all_data += data[new_pos:]

    data_left = data_len - len(all_data)
    while True:
        data = sock.recv(data_left)
        all_data += data
        data_left -= len(data)

        if data_left <= 0:
            break

    msg = uapb.ACommunicate()
    msg.ParseFromString(all_data)
    return msg
    
    
# Only use this method to receive from World
# Return a Message object
def URecv(sock, isUConnect=False):
    all_data = b''
    data = sock.recv(4)
    if not data:
        print('connection to world is closed')
    data_len, new_pos = _DecodeVarint32(data, 0)
    all_data += data[new_pos:]

    data_left = data_len - len(all_data)
    while True:
        data = sock.recv(data_left)
        all_data += data
        data_left -= len(data)

        if data_left <= 0:
            break
        
    if isUConnect:
        msg = wupb.UConnected()
        msg.ParseFromString(all_data)
        return msg

    msg = wupb.UResponses()
    msg.ParseFromString(all_data)
    return msg


# Get World ID and set Trucks
def GetWorld(wSock, world,db):
    print('getting world id')
    connMsg = wupb.UConnect()
    connMsg.isAmazon = False
    if world ==0:
        num_truck = 100
        # store trucks in database while put it in connMsg
        for i in range(num_truck):
            t = connMsg.trucks.add()
            t.id = i
            t.x = 99
            t.y = 99
            Inserttruck(db,i,'idle')

    if world > 0:
        connMsg.worldid = world

    Send(wSock, connMsg)
    res = URecv(wSock, True)

    print('World connection status: ', res.result)
    return res.worldid
    

# Process UResponse
def ProcessURes(msg, wSock, aSock, db):
    print('Process UResponse...')
    print(msg)
    global SeqNum
    toAmazonEmpty = True
    toWorldEmpty = True
    
    # Prepare UCommand & UCommunicate
    ToWorld = wupb.UCommands()
    ToAmazon = uapb.UCommunicate()
    
    # check for UFinished
    print('Looking into UFinished msg')
    for ufin in msg.completions:
        toWorldEmpty = False
        
        # Add ACK
        ToWorld.acks.append(ufin.seqnum)

        # Check ufinished status, notify amazon
        # first check whether this ufin has been processed before
        entry = Wrecvseq(db, ufin.seqnum)
        if entry:
            continue

        # record the seqnum from World
        Insertwrecv(db, ufin.seqnum)
        
        if ufin.status == 'ARRIVE WAREHOUSE':
            toAmazonEmpty = False
            print('notify amazon')
            arrive = ToAmazon.uarrived.add()
            arrive.truckid = ufin.truckid 
            with seq_lock:
                arrive.seqnum = SeqNum
                SeqNum += 1
            Insertusend(db, arrive.seqnum, arrive.SerializeToString(), 'UArrivedAtWarehouse')
            Truckstatus(db,ufin.truckid,'loading')
            
        elif ufin.status == 'IDLE':
            print('dont need notify, notify in delivered')
            # update truck status in database to idle
            Truckstatus(db, ufin.truckid, 'idle')
                
    # check for UDeliveryMade
    print('Looking into UDeliveryMade Msg...')
    for udel in msg.delivered:
        toWorldEmpty = False
        toAmazonEmpty = False
        
        # Add ACK
        ToWorld.acks.append(udel.seqnum)

        #  first check whether this udel has been processed before
        if Checkdelivered(db, udel.packageid):
            continue

        # send out notification email
        SendEmail(db, udel.packageid)
        
        # record the seqnum from World
        Insertwrecv(db, udel.seqnum)
        
        # update delivery status for package in db, send to amazon
        delivered = ToAmazon.udelivered.add()
        delivered.packageid = udel.packageid
        Packagestatus(db, udel.packageid, 'delivered')
        Truckamount(db, udel.truckid, False)
        
        # record this MSG in database
        with seq_lock:
            delivered.seqnum = SeqNum
            Insertusend(db, SeqNum, delivered.SerializeToString(), 'UPackageDelivered')
            SeqNum += 1
            
    # add ack for truckstatus, if any
    for utruck in msg.truckstatus:
        toWorldEmpty = False
        # Add ACK
        ToWorld.acks.append(utruck.seqnum)
        UpdatePackagePos(db, utruck.truckid, utruck.x, utruck.y)

    # Check the acks field, delete those in UPS seqnum table
    for ACK in msg.acks:
        Deleteusend(db, ACK)
        
    # Send ACK to World & updates to Amazon
    if not toWorldEmpty:
        Send(wSock, ToWorld)
    if not toAmazonEmpty:
        Send(aSock, ToAmazon)

    
# Process AResponse
def ProcessARes(msg, aSock, wSock,conn):
    print('process aresponse')
    print(msg)
    global SeqNum
    toWorldEmpty = True
    toAmazonEmpty = True
    
    # Check the acks field, delete those in UPS seqnum table
    for ack in msg.acks:
        Deleteusend(conn,ack)

    # Prepare UCommand & UCommunicate            
    ToWorld = wupb.UCommands()
    ToAmazon = uapb.UCommunicate()

    # Check for AOrderPlaced
    for aor in msg.aorderplaced:        
        print('process AOrderPlace')

        # Select one truck from truck table
        truck = Findidle(conn)
        if truck == -1:
            truck = Findtruck(conn)
            if truck ==-1:
                print('no truck available, ignore the order')
                continue
        
        # Store in amazon seqnum table
        exists = Arecvseq(conn,aor.seqnum)
        if not exists:
            Insertarecv(conn,aor.seqnum)
        else:
            print('process before')
            continue

        toWorldEmpty =False
        toAmazonEmpty =False

        # Add ACK
        ToAmazon.acks.append(aor.seqnum)

        # Add package in package table
        items = ''
        amount = 0
        for thing in aor.things:
            if not items:
                items = thing.name
            else:
                items = items + ',' + thing.name
            amount +=thing.count
        Insertpackage(conn,aor.packageid,aor.x,aor.y,'created',items,amount,truck,aor.UPSuserid)
            
        # Add UGoPickup to ToWorld
        pick = ToWorld.pickups.add()
        pick.truckid = truck
        pick.whid = aor.whid
        with seq_lock:
            pick.seqnum = SeqNum
            SeqNum += 1
        
        # Add UOrderplaced to toAmazon
        order = ToAmazon.uorderplaced.add()
        order.packageid = aor.packageid
        order.truckid = truck
        with seq_lock:
            order.seqnum = SeqNum
            SeqNum += 1
        
        # Add send message to usend table
        Insertusend(conn, pick.seqnum, pick.SerializeToString(), 'UGoPickup')
        Insertusend(conn, order.seqnum,order.SerializeToString(), 'UOrderPlaced')
        
        # Update status of package and truck
        Truckstatus(conn,truck,'to warehouse')
        Packagestatus(conn,aor.packageid,'truck en-route to warehouse')
                
    # Check for ALoadingFinished
    for alod in msg.aloaded:
        toWorldEmpty =False
        toAmazonEmpty = False
        print('process ALoadingFinished')

        # Store in amazon seqnum table
        exists = Arecvseq(conn,alod.seqnum)
        if not exists:
            Insertarecv(conn,alod.seqnum)
        else:
            print('process before')
            continue
        
        # Add ACK
        ToAmazon.acks.append(alod.seqnum)

        # Update status of package & update the truck amount
        Packagestatus(conn,alod.packageid,'out for delivery')
        Truckamount(conn,alod.truckid,True)
        Truckstatus(conn,alod.truckid,'delivering')
        
        # Add UGoDeliver to ToWorld
        xy = Packageaddress(conn,alod.packageid)
        deliver = ToWorld.deliveries.add()
        deliver.truckid = alod.truckid
        package = deliver.packages.add()
        package.packageid = alod.packageid
        package.x = xy[0]
        package.y = xy[1]
        with seq_lock:
            deliver.seqnum = SeqNum
            SeqNum += 1
        
        # Add send message to usend table
        Insertusend(conn, deliver.seqnum, deliver.SerializeToString(), 'UGoDeliver')
    
    # Send ACK to World & Amazon
    if not toAmazonEmpty:
        Send(aSock, ToAmazon)
    if not toWorldEmpty:
        Send(wSock, ToWorld)


# Resend msg whose ACK is missing
def PacketDrop(wSock, aSock, db):
    print('check seqnum table every 30s, resend all those request/ACK')

    while True:
        time.sleep(30)
        print('start to check ack')
        with db_lock:
            cur = db.cursor()
            sql = 'SELECT * FROM usend'
            cur.execute(sql)
            row = cur.fetchone()

        ToWorld = wupb.UCommands()
        ToAmazon = uapb.UCommunicate()
        ToWorld_empty = True
        ToAmazon_empty = True
        
        while row:
            with db_lock:
                # TOCHECK: distinguish what type of Msg, add to ToWorld or ToAmazon
                if row[2] == 'UGoPickup':
                    print('resend UGoPickup')
                    tp = ToWorld.pickups.add()
                    ToWorld_empty = False
                elif row[2] == 'UGoDeliver':
                    print('resend UGoDeliver')
                    tp = ToWorld.deliveries.add()
                    ToWorld_empty = False
                elif row[2] == 'UQuery':
                    print('resend UQuery')
                    tp = ToWorld.queries.add()
                    ToWorld_empty = False
                elif row[2] == 'UOrderPlaced':
                    print('resend UOrderPlaced')
                    tp = ToAmazon.uorderplaced.add()
                    ToAmazon_empty = False
                elif row[2] == 'UArrivedAtWarehouse':
                    print('resend UArrivedAtwarehouse')
                    tp = ToAmazon.uarrived.add()
                    ToAmazon_empty = False
                elif row[2] == 'UPackageDelivered':
                    print('resend UPackageDelivered')
                    tp = ToAmazon.udelivered.add()
                    ToAmazon_empty = False
                    
                tp.ParseFromString(row[1]);
                row = cur.fetchone()

        if not ToWorld_empty:
            Send(wSock, ToWorld)
        else:
            print('world empty')
        if not ToAmazon_empty:
            Send(aSock, ToAmazon)
        else:
            print('amazon empty')


# Check truck status, update position of package
def QueryTruck(wSock, aSock, db):
    print('query truck status, update front end')
    global SeqNum
    
    while True:
        time.sleep(20)
        print('truck query start')
        with db_lock:
            cur = db.cursor()
            sql = '''SELECT truckid FROM truck WHERE status = 'delivering';'''
            cur.execute(sql)
            row = cur.fetchone()

        ToWorld = wupb.UCommands()
        ToWorld_empty = True

        while row:
            ToWorld_empty = False
            msg = ToWorld.queries.add()
            msg.truckid = row[0]
            with seq_lock:
                msg.seqnum = SeqNum
                SeqNum += 1
                Insertusend(db, msg.seqnum, msg.SerializeToString(), 'UQuery')
            with db_lock:
                row = cur.fetchone()
            
        if not ToWorld_empty:
            Send(wSock, ToWorld)

