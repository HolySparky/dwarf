#!/usr/bin/env python
# vim: set fileencoding=utf-8:

import logging
#import MySQLdb
import os
import sys
import time

import socket

def main():
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', 8001))
    sock.listen(100)
    while True:  
        connection,address = sock.accept()  
        try:  
            connection.settimeout(5)  
            buf = connection.recv(1024)  
            print "Server Received: %s " %(buf)
        except socket.timeout:  
            print 'time out'  
        connection.close()   
            

if __name__ == '__main__':
    main()
