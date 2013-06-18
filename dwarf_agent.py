#!/usr/bin/env python
# vim: set fileencoding=utf-8:

import ConfigParser
import logging
#import MySQLdb
import os
import sys
import time

import socket


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


    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    sock.connect((server_ip, int(server_port)))  
    sock.send('1')  
    print sock.recv(1024)  
    sock.close()  
            

if __name__ == '__main__':
    main()
