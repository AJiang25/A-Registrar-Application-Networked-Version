#!/usr/bin/env python

#-----------------------------------------------------------------------
# regserverprelim.py
# Authors: Arnold Jiang and Amanda Chan
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# imports
import sys
import sqlite3
import textwrap
import argparse
import contextlib

import socket 
import json
import os

#-----------------------------------------------------------------------

def handle_client(sock):
    n=1

#-----------------------------------------------------------------------
def main():
    DATABASE_URL = 'file:reg.sqlite?mode=ro'

    parser = argparse.ArgumentParser(description =
                                     'Server for the registrar application')
    parser.add_argument('port',  type = int, help =
                        'the port at which the server is listening')

    try:
        # Parses the stdin arguments
        args = parser.parse_args()

        server_sock = socket.socket()
        print('Opened server socket')
        if os.name != 'nt':
            server_sock.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(('', args.port))
        print('Bound server socke tot port')
        server_sock.listen()
        print('Listening')

        while True:
            try:
                sock, client_addr = server_sock.accept()
                with sock:
                    print('Accepted connection')
                    print('Opened socket')
                    print('Server IP addr and port:',
                          sock.getsockname())
                    print('Client IP addr and port:', client_addr)
                    #handle_client(sock)

                # Connects to the database and creates a curser connection
                    with sqlite3.connect(DATABASE_URL, isolation_level = None, uri = True) as connection:
                        with contextlib.closing(connection.cursor()) as cursor:
                            handle_client(sock)

            except Exception as ex:
                print(ex, file=sys.stderr)    

    except Exception as e:
        print(f"{sys.argv[0]}: {str(e)}", file=sys.stderr)
        sys.exit(1)
#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()
