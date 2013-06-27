#!/usr/bin/env python
# vim: set fileencoding=utf-8:

import ConfigParser
import logging
#import MySQLdb
import os
import sys
import time

import socket
import simplejson as json
from sqlalchemy.ext.sqlsoup import SqlSoup

class Flow_Info:
    def __init__(self):
        self.src_host = ""
        self.dst_host = ""
        self.src_ip = ""
        self.dst_ip = ""

    def set_host(self, src, dst):
        self.src_host = src
        self.dst_host = dst


def main():
    config_file = "agent.ini"
    config = ConfigParser.ConfigParser()
    try:
        config.read(config_file)
    except Exception, e:
        print "Exception: Could not parse agent config file"
        LOG.error("Unable to parse config file \"%s\": %s"
                  % (config_file, str(e)))
        raise e
    server_ip = ""
    server_port = ""

    # Get Dwarf-server parameters
    try:
        server_ip = config.get("SERVER", "server_ip")
        server_port = config.get("SERVER", "server_port")
    except Exception, e:
        pass

    print "readed: server :" + server_ip + "and port: " + server_port

    flow1 = Flow_Info()
    flow1.set_host("mao", "la")

    flow2 = {"src_host":"mao", "dst_host":"la"}

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    sock.connect((server_ip, int(server_port)))  
    sock.send(json.dumps(flow2))  
    print sock.recv(1024)  
    print flow2
    print json.loads(json.dumps(flow2))
    sock.close()  
            

if __name__ == '__main__':
    main()
