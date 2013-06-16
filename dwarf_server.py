#!/usr/bin/env python
# vim: set fileencoding=utf-8:

import logging
import MySQLdb
import os
import sys
import time

import socket

def main():
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 8001))
    sock.listen(5)
            

if __name__ == '__main__':
    main()
