#!/usr/bin/env python
# vim: set fileencoding=utf-8:
import ConfigParser
import logging
import MySQLdb
import os
import sys
import time

import socket
import simplejson as json
from optparse import OptionParser
from sqlalchemy.ext.sqlsoup import SqlSoup

ip_ports = {}
server_ip = ""
server_port = ""
agent_port = ""
db_url = ""

def PreConfig():
    global server_ip
    global server_port
    global agent_port
    config_file = "agent.ini"
    config = ConfigParser.ConfigParser()
    try:
        config.read(config_file)
    except Exception, e:
        print "Exception: Could not parse agent config file"
        LOG.error("Unable to parse config file \"%s\": %s"
                % (config_file, str(e)))
        raise e

    try:
        server_ip = config.get("SERVER", "server_ip")
        server_port = config.get("SERVER", "server_port")
        agent_port = config.get("AGENT", "agent_port")
        db_url = config.get("SQL", "sql_connection")
    except Exception, e:
        pass
    print "readed: server :" + server_ip + "and port: " + server_port
    print "db_url : " + db_url
    


def main():
    global agent_port
    global db_url
    PreConfig()
    #read db for ip and supression
    options = {"sql_connection": db_url}
    db = SqlSoup(options["sql_connection"])
    ips = db.ip_port.all()
    supressions = db.supression.all()
    db.commit()
    for ip in ips:
        ip_ports[ip.ip] = {"port":ip.port_name, "host":ip.host_ip}
    print ip_ports
    sup = {}
    for supress in supressions:
        sup[supress.src] = "20"
#setup sockets
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((server_ip, int(server_port)))
    sock.listen(100)
    while True:  
        connection,address = sock.accept()  
        try:  
            connection.settimeout(5)  
            buf = connection.recv(1024)  
            flow2 = json.loads(buf)
            #flow2 = {u'src_ip': u'10.10.0.5', u'supression': 0}
            print "Server Received: %s " %(flow2)
            try:
                src_ip = flow2['src_ip']
                supression = flow2['supression'] 
                if src_ip in sup:
                    db.supression.get('src_ip').supression = supression
                else:
                    db.supression.insert(src_ip=src_ip,supression=supression)
            except:
                print "fuck,sql wrong?"
        except socket.timeout:  
            print 'time out'  
        except:
            print 'well, something wrong'
        connection.close()   
            

if __name__ == '__main__':
    main()
