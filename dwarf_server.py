#!/usr/bin/env python
# vim: set fileencoding=utf-8:

import logging
import MySQLdb
import os
import sys
import time

import socket
import simplejson as json

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
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', 8001))
    sock.listen(100)
    while True:  
        connection,address = sock.accept()  
        try:  
            connection.settimeout(5)  
            buf = connection.recv(1024)  
            flow2 = json.loads(buf)
            print "Server Received: %s " %(flow2)
        except socket.timeout:  
            print 'time out'  
        connection.close()   
            

if __name__ == '__main__':
    main()
