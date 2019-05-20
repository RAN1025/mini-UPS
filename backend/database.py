import psycopg2
import threading

db_lock = threading.Lock()

#connect to database
def Connectdb():
    conn = psycopg2.connect(database="ups",user="ups_user",password="ups_user",host="db",port="5432")
    return conn

#drop tables that may already exist
def Droptable(conn):
    with db_lock:
        cur = conn.cursor()
        sql = '''DELETE FROM package_package;
        DROP TABLE IF EXISTS truck; 
        DROP TABLE IF EXISTS usend; 
        DROP TABLE IF EXISTS arecv;
        DROP TABLE IF EXISTS wrecv;'''
        cur.execute(sql)
        conn.commit()
    return

#create truck, usend, arecv, wrecv tables in databse
def Createtable(conn):
    with db_lock:
        cur = conn.cursor()
        trucksql = '''CREATE TABLE truck(
        truckid INT   PRIMARY KEY   NOT NULL,
        status  TEXT                NOT NULL,
        amount  INT                 NOT NULL DEFAULT 0);'''
        usendsql = '''CREATE TABLE usend(
        seqnum  INT   PRIMARY KEY   NOT NULL,
        mesg    BYTEA               NOT NULL,
        title   TEXT                NOT NULL);'''
        arecvsql = '''CREATE TABLE arecv(
        seqnum  INT   PRIMARY KEY   NOT NULL);'''
        wrecvsql = '''CREATE TABLE wrecv(
        seqnum  INT   PRIMARY KEY   NOT NULL);'''
        cur.execute(trucksql)
        cur.execute(usendsql)
        cur.execute(arecvsql)
        cur.execute(wrecvsql)
        conn.commit()
    return

#check ownerid
def checkowner(conn,ownerid):
    with db_lock:
        cur = conn.cursor()
        sql = '''SELECT EXISTS (SELECT 1 FROM users_customuser WHERE "User_ID" = %s);'''
        cur.execute(sql,(ownerid,))                                                              
        exists = cur.fetchone()
        return exists[0]

#insert into package_package
def Insertpackage(conn,packageid,x,y,status,items,amount,truckid,ownerid):
    cur = conn.cursor()
    exists=checkowner(conn,ownerid)
    with db_lock:
        if exists:
            sql = '''INSERT INTO package_package (package_id, status, owner_id, truck_id, amount, items, x, y) VALUES(%s,%s,%s,%s,%s,%s,%s,%s);'''
            cur.execute(sql,(packageid,status,ownerid,truckid,amount,items,x,y))
        else:
            sql = '''INSERT INTO package_package (package_id, status, truck_id, amount, items, x, y) VALUES (%s,%s,%s,%s,%s,%s,%s);'''
            cur.execute(sql,(packageid,status,truckid,amount,items,x,y))
        conn.commit()
    return

#update package status
def Packagestatus(conn,packageid,status):
    with db_lock:
        cur = conn.cursor()
        sql = '''UPDATE package_package SET status = %s WHERE package_id = %s;'''
        cur.execute(sql,(status,packageid))
        conn.commit()
    return

#get address
def Packageaddress(conn,packageid):
    with db_lock:
        cur = conn.cursor()
        sql = '''SELECT x,y FROM package_package WHERE package_id = %s;'''
        cur.execute(sql,(packageid,))
        row = cur.fetchone()
    return row

#insert into truck
def Inserttruck(conn,truckid,status):
    with db_lock:
        cur = conn.cursor()
        sql = '''INSERT INTO truck (truckid,status) VALUES (%s,%s);'''
        cur.execute(sql,(truckid,status))
        conn.commit()
    return

#update truck status
def Truckstatus(conn,truckid,status):
    with db_lock:
        cur = conn.cursor()
        sql = '''UPDATE truck SET status = %s WHERE truckid = %s;'''
        cur.execute(sql,(status,truckid))
        conn.commit()
    return

#update amount in truck
def Truckamount(conn,truckid,add):
    cur = conn.cursor()
    if add == True:
        sql = '''UPDATE truck SET amount = amount +1 WHERE truckid = %s;'''
    else:
        sql = '''UPDATE truck SET amount = amount -1 WHERE truckid = %s;'''
    cur.execute(sql,(truckid,))
    conn.commit()
    return

#find idle truck
def Findidle(conn):
    with db_lock:
        cur = conn.cursor()
        sql = '''SELECT truckid FROM truck WHERE status = 'idle';'''
        cur.execute(sql)
        row = cur.fetchone()
    if not row:
        return -1
    else:
        return row[0]

#select truck with lease amount
def Findtruck(conn):
    with db_lock:
        cur = conn.cursor()
        sql = '''SELECT truckid FROM truck WHERE status = 'delivering' ORDER BY amount;'''
        cur.execute(sql)
        row = cur.fetchone()
    if row == None:
        return -1
    else:
        return row[0]

#insert into usend
def Insertusend(conn,seqnum,mesg,title):
    with db_lock:
        cur = conn.cursor()
        sql = '''INSERT INTO usend (seqnum,mesg,title) VALUES (%s,%s,%s);'''
        cur.execute(sql,(seqnum,mesg,title))
        conn.commit()
    return

#delete from usend
def Deleteusend(conn,seqnum):
    with db_lock:
        cur = conn.cursor()
        sql = '''DELETE FROM usend WHERE seqnum = %s;'''
        cur.execute(sql,(seqnum,))
        conn.commit()
    return

#insert into arecv
def Insertarecv(conn,seqnum):
    with db_lock:
        cur = conn.cursor()
        sql = '''INSERT INTO arecv (seqnum) VALUES (%s);'''
        cur.execute(sql,(seqnum,))
        conn.commit()
    return

#check if the seqnum exists in arecv
def Arecvseq(conn,seqnum):
    with db_lock:
        cur = conn.cursor()
        sql = '''SELECT EXISTS (SELECT 1 FROM arecv WHERE seqnum = %s);'''
        cur.execute(sql,(seqnum,))
        exists = cur.fetchone()
    return exists[0]

#insert into wrecv
def Insertwrecv(conn,seqnum):
    with db_lock:
        cur = conn.cursor()
        sql = '''INSERT INTO wrecv (seqnum) VALUES (%s);'''
        cur.execute(sql,(seqnum,))
        conn.commit()
    return

#check if the seqnum exists in wrecv
def Wrecvseq(conn,seqnum):
    with db_lock:
        cur = conn.cursor()
        sql = '''SELECT EXISTS (SELECT 1 FROM wrecv WHERE seqnum = %s);'''
        cur.execute(sql,(seqnum,))
        exists = cur.fetchone()
    return exists[0]

# check if a package is delivered
def Checkdelivered(conn, packageid):
    with db_lock:
        cur = conn.cursor()
        sql = '''SELECT status FROM package_package WHERE package_id = %s;'''
        cur.execute(sql, (packageid,))
        res = cur.fetchone()
    return res[0] == 'delivered'

# update package position
def UpdatePackagePos(conn, truckid, x, y):
    with db_lock:
        cur = conn.cursor()
        sql = '''UPDATE package_package SET curr_x = %s, curr_y = %s WHERE truck_id = %s AND status = 'out for delivery';'''
        cur.execute(sql, (x, y, truckid,))
        conn.commit()
    return

def GetEmail(conn, packageid):
    with db_lock:
        cur = conn.cursor()
        sql1 = '''SELECT owner_id FROM package_package WHERE package_id = %s;'''
        cur.execute(sql1, (packageid,))
        owner = cur.fetchone()
    if not owner or owner[0] == None:
        print('no owner_id no email!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        return -1
    with db_lock:
        sql2 = '''SELECT email FROM users_customuser WHERE "User_ID" = %s;'''
        cur.execute(sql2, (owner[0],))
        res = cur.fetchone()
    print('find email!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    return res[0]
