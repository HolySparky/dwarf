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
db_url = ""

def PreConfig():
    global server_ip
    global server_port
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
	db_url = config.get("SQL", "sql_connection")
    except Exception, e:
	pass
    print "readed: server :" + server_ip + "and port: " + server_port
    print "db_url : " + db_url
    
    options = {"sql_connection": db_url}
    db = SqlSoup(options["sql_connection"])
    ips = db.ip_port.all()
    db.commit()
    for ip in ips:
	ip_ports[ip.ip] = {"port":ip.port_name, "host":ip.host_ip}
    print ip_ports


def main():
    PreConfig()
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((server_ip, int(server_port)))
    sock.listen(100)
    while True:  
        connection,address = sock.accept()  
        try:  
            connection.settimeout(5)  
            buf = connection.recv(1024)  
            flow2 = json.loads(buf)
            print "Server Received: %s " %(flow2)
#Server Received: {u'dst_host': u'la', u'src_host': u'mao'}
	    print flow2["src_ip"]
        except socket.timeout:  
            print 'time out'  
        connection.close()   
            

if __name__ == '__main__':
    main()
