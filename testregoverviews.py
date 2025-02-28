#!/usr/bin/env python

#-----------------------------------------------------------------------
# testregoverviews.py
# Author: Bob Dondero, Arnold Jiang, Amanda Chan
#-----------------------------------------------------------------------

import os
import sys
import shutil
import argparse

#-----------------------------------------------------------------------

MAX_LINE_LENGTH = 72
UNDERLINE = '-' * MAX_LINE_LENGTH

#-----------------------------------------------------------------------

def parse_args():

    parser = argparse.ArgumentParser(
        description=
        "Test the Registrar's application's handling of " +
        "class overviews requests")
    parser.add_argument('program', metavar='program', type=str,
        help='the client program to run')
    parser.add_argument('host', metavar='host', type=str,
        help='the host on which the server is running')
    parser.add_argument('port', metavar='port', type=int,
        help='the port at which the server is listening')
    args = parser.parse_args()

    return (args.program, args.host, args.port)

#-----------------------------------------------------------------------

def print_flush(message):
    print(message)
    sys.stdout.flush()

#-----------------------------------------------------------------------

def exec_command(program, args):

    print_flush(UNDERLINE)
    command = 'python ' + program + ' ' + args
    print_flush(command)
    exit_status = os.system(command)
    if os.name == 'nt':  # Running on MS Windows?
        print_flush('Exit status = ' + str(exit_status))
    else:
        print_flush('Exit status = ' + str(os.WEXITSTATUS(exit_status)))


def main():

    program, host, port = parse_args()

    exec_command(program, '-h')

    prefix = host + ' ' + str(port) + ' '

    exec_command(program, prefix + '-d COS')
    exec_command(program, prefix + '-d COS -a qr -n 2 -t intro')

    #testing
    #Coverage Case Testing
    exec_command(program, '')
    exec_command(program, '-d COS')
    exec_command(program, '-n 333')
    exec_command(program, '-n 240')
    exec_command(program, '-n 226')
    exec_command(program, '-n 217')
    exec_command(program, '-n 445')
    exec_command(program, '-n b')
    exec_command(program, '-a Qr')
    exec_command(program, '-t intro')
    exec_command(program, '-t science')
    exec_command(program, '-t C_S')
    exec_command(program, '-t c%S')
    exec_command(program, '-d cos -n 3')
    exec_command(program, '-d COS -a qr -n 2 -t intro')
    exec_command(program, '-d COS -a qr -n 2 -t apple')
    exec_command(program, '-t "Independent Study"')
    exec_command(program, '-t "Independent Study "')
    exec_command(program, '-t "Independent Study  "')
    exec_command(program, '-t " Independent Study"')
    exec_command(program, '-t "  Independent Study"')
    exec_command(program, '-t=-c')

    #Error Case Testing
    exec_command(program, 'a qr')
    exec_command(program, '-A qr')
    exec_command(program, '-A \br')
    exec_command(program, '"-a " qr')
    exec_command(program, '-a qr st')
    exec_command(program, '-a')
    exec_command(program, '-a qr -d')
    exec_command(program, '-a -d cos')
    exec_command(program, '-x')

    # Database Testing
    try:
        shutil.copy('reg.sqlite', 'regbackup.sqlite')
        os.remove('reg.sqlite')
        exec_command(program, '-d ENG')
        shutil.copy('regflawed.sqlite', 'reg.sqlite')
        exec_command(program, '-d ENG')
        shutil.copy('regbackup.sqlite', 'reg.sqlite')
    except FileNotFoundError:
        print(
            'Database file not found, skipping database error tests.',
            file=sys.stderr
        )

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()
