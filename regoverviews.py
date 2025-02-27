#!/usr/bin/env python

#-----------------------------------------------------------------------
# regoverviews.py
# Authors: Arnold Jiang and Amanda Chan
#-----------------------------------------------------------------------
# imports
import sys
import argparse
import socket
import json
import textwrap
#-----------------------------------------------------------------------
def print_wrapped(text):
    print(textwrap.fill(
        text,
        width = 72,
        break_long_words=False,
        replace_whitespace=False,
        subsequent_indent=" "*3
        )
    )
#-----------------------------------------------------------------------
def send_request(args, sock):
    # Create request object
    request = ['get_overviews', {
        'dept': args.d if args.d else '',
        'coursenum': args.n if args.n else '',
        'area': args.a if args.a else '',
        'title': args.t if args.t else ''
    }]

    # Converts the request object to json
    json_request = json.dumps(request)

    # Send the request to the server
    writer = sock.makefile(mode='w', encoding='ascii')
    writer.write(json_request + '\n')
    writer.flush()

#-----------------------------------------------------------------------
def receive_response(sock):
    reader = sock.makefile(mode='r', encoding='ascii')
    response = reader.readline()
    return response

#-----------------------------------------------------------------------
def validate_response(args, response):
    # DO WE NEED ARGS?
    # work on validation
    if response and response[0]:

        # check if response is valid, handle the error
        # -> write the response
        response_data = json.loads(response)
        response_details = response_data[1]
        return response_details
        
    # elif not response:
    #     print(f"{sys.argv[0]}: no class with classid " +
    #                       str(args.classid) + " exists",
    # file=sys.stderr)
    #     sys.exit(1)

#-----------------------------------------------------------------------
def print_response(response_details):
    try: 
        print('%5s %4s %6s %4s %s' %
                ("ClsId", "Dept", "CrsNum", "Area", "Title"))
        print('%5s %4s %6s %4s %s' %
                ("-----", "----", "------", "----", "-----"))

        for row in response_details:
            res = '%5s %4s %6s %4s %s' % (
                row['classid'],
                row['dept'],
                row['coursenum'],
                row['area'],
                row['title']
            )
        print(textwrap.fill(
            res,
            width = 72,
            break_long_words= False,
            subsequent_indent=" "*23
            )
        )
    except Exception as e:
        print(f"{sys.argv[0]}: {str(e)}", file=sys.stderr)
        sys.exit(1)
#-----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description =
        'Registrar application: show overviews of classes')
    parser.add_argument('host',  help =
                        'the computer on which the server is running')
    parser.add_argument('port',  type = int, help =
                        'the port at which the server is listening')
    parser.add_argument(
        '-d', 
        type=str,
        metavar = 'dept',
        help = 'show only those classes whose department contains dept')
    parser.add_argument(
        '-n', 
        type=str,
        metavar = 'num',
        help =
        'show only those classes whose course number contains num')
    parser.add_argument(
        '-a',
        type=str,
        metavar = 'area',
        help =
        'show only those classes whose distrib area contains area')
    parser.add_argument(
        '-t',
        type=str,
        metavar = 'title',
        help =
        'show only those classes whose course title contains title')

    try:
        # Parses the stdin arguments
        args = parser.parse_args()
        host = sys.argv[1]
        port = int(sys.argv[2])

        with socket.socket() as sock:
            sock.connect((host, port))
            send_request(args, sock)
            response = receive_response(sock)
            response_details = validate_response(args, response)
            print_response(response_details)

    except Exception as e:
        print(f"{sys.argv[0]}: {str(e)}", file=sys.stderr)
        sys.exit(1)
#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()
