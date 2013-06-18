#!/usr/bin/env python
# vim: set fileencoding=utf-8:

import logging
#import MySQLdb
import os
import sys
import time

import socket

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    sock.connect(('10.50.8.42', 8001))  
    sock.send('1')  
    print sock.recv(1024)  
    sock.close()  
            

if __name__ == '__main__':
    main()
