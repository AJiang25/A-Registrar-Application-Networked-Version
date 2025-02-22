#!/usr/bin/env python

#-----------------------------------------------------------------------
# regdetails.py
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
    print(textwrap.fill(text, width = 72, break_long_words=False,
                        replace_whitespace=False, subsequent_indent=" "*3))
#-----------------------------------------------------------------------
def sendRequest(args, sock):
    # Create request object
    request = ['get_details', args.classid]
    
    print(request)
    # Converts the request object to json
    json_request = json.dumps(request)
            
    # Send the request to the server
    writer = sock.makefile(mode='w', encoding='ascii')
    writer.write(json_request + '\n')
    writer.flush()
    
#-----------------------------------------------------------------------
def receiveResponse(sock):
    reader = sock.makefile(mode='r', encoding='ascii')
    response = reader.readline()
    return response
    
#-----------------------------------------------------------------------
def validateResponse(args, response):
    # work on validation
    if response and response[0]:
        print(response)
        
        # check if response is valid, handle the error -> write the response
        response_data = json.loads(response)
        details = response_data[1]

        print('-------------')
        print('Class Details')
        print('-------------')
        print_wrapped(f"Class Id: {details['classid']}")
        print_wrapped(f"Days: {details['days']}")
        print_wrapped(f"Start time: {details['starttime']}")
        print_wrapped(f"End time: {details['endtime']}")
        print_wrapped(f"Building: {details['bldg']}")
        print_wrapped(f"Room: {details['roomnum']}")
        print('--------------')
        print('Course Details')
        print('--------------')
        print_wrapped(f"Course Id: {details['courseid']}")
        for dept in details['deptcoursenums']:
            print_wrapped(f"Dept and Number: {dept['dept']} {dept['coursenum']}")
        
        print_wrapped(f"Area: {details['area']}")
        print_wrapped(f"Title: {details['title']}")
        print_wrapped(f"Description: {details['descrip']}")
        print_wrapped(f"Prerequisites: {details['prereqs']}")
        for prof in details['profnames']:
            print_wrapped(f"Professor: {prof}")
            
    elif not response: 
        print(f"{sys.argv[0]}: no class with classid " +
                          str(args.classid) + " exists", file=sys.stderr)
        sys.exit(1)
#-----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description =
                                     'Registrar application: show details about a class')
    parser.add_argument('host',  help =
                        'the computer on which the server is running')
    parser.add_argument('port',  type = int, help =
                        'the port at which the server is listening')
    parser.add_argument('classid', type = int, help =
                        'the id of the class whose details should be shown')

    try:
        # Parses the stdin arguments
        args = parser.parse_args()
        host = sys.argv[1]
        port = int(sys.argv[2])
        
        with socket.socket() as sock:
            sock.connect((host, port)) 
            
            sendRequest(args, sock)
            response = receiveResponse(sock)
            validateResponse(args, response)

    except Exception as e:
        print(f"{sys.argv[0]}: {str(e)}", file=sys.stderr)
        sys.exit(1)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()
