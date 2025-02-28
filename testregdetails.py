#!/usr/bin/env python

#-----------------------------------------------------------------------
# testregdetails.py
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
        "class details requests")
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

#-----------------------------------------------------------------------

def main():

    program, host, port = parse_args()

    exec_command(program, '-h')

    prefix = host + ' ' + str(port) + ' '

    exec_command(program, prefix + '8321')

    # Coverage Case Testing
    exec_command(program, '8321')
    exec_command(program, '9032')
    exec_command(program, '8293')
    exec_command(program, '9977')
    exec_command(program, '9012')
    exec_command(program, '10188')
    exec_command(program, '10261')
    exec_command(program, '10262')
    exec_command(program, '10263')
    exec_command(program, '10264')
    exec_command(program, '9158')

    # Error Case Testing
    exec_command(program, '-h')
    exec_command(program, '')
    exec_command(program, '8321 9032')
    exec_command(program, 'abc123')
    exec_command(program, '9034')
    exec_command(program, '1000000000')

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

if __name__ == '__main__':
    main()
