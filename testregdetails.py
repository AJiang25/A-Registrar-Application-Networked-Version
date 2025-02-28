#!/usr/bin/env python

#-----------------------------------------------------------------------
# testregdetails.py
# Author: Bob Dondero, Arnold Jiang, Amanda Chan
#-----------------------------------------------------------------------

import os
import sys
import shutil

#-----------------------------------------------------------------------

MAX_LINE_LENGTH = 72
UNDERLINE = '-' * MAX_LINE_LENGTH

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

    if len(sys.argv) != 2:
        print('Usage: ' + sys.argv[0] + ' regdetailsprogram',
            file=sys.stderr)
        sys.exit(1)

    program = sys.argv[1]

    # Coverage Case Testing
    exec_command(program, '8321')
    exec_command(program, '9032')
    exec_command(program, '8293')
    exec_command(program, '9977')
    exec_command(program, '9012')
    exec_command(program, '10188')
    exec_command(program, '9158')

    # Error Case Testing
    exec_command(program, '-h')
    exec_command(program, '')
    exec_command(program, '8321 9032')
    exec_command(program, 'abc123')
    exec_command(program, '9034')
    exec_command(program, '1000000000')

    # Additional Error Case Testing
    exec_command(program, '["invalid_request_type", {}]')
    exec_command(program, '[123, {}]')
    exec_command(program, '["get_overviews", "not_a_dict"]')
    exec_command(
        program,
        '["get_overviews", {"dept": 123, "coursenum": "COS"}]'
    )
    exec_command(program, '["get_details", "not_an_int"]')
    exec_command(program, '["get_details", -5]')

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
