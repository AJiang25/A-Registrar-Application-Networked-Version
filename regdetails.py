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
def send_request(args, sock):
    # Create request object
    request = ['get_details', args.classid]

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
    details = json.loads(response)
    return details
    
#-----------------------------------------------------------------------
def validate_response(args, response):
    try: 
        if isinstance(response[0], bool): 
            if isinstance(response[1], dict):
                details = response[1]
                
                # Check if the fields exist
                fields = ['classid', 'days', 'starttime', 'endtime', 'bldg', 'roomnum', 
                            'courseid', 'deptcoursenums', 'area', 'title', 'descrip',
                            'prereqs', 'profnames']

                for field in fields:
                    if field not in details:
                        raise ValueError(f"Missing required field: {field}")
                
                if not isinstance(details['classid'], int):
                    raise TypeError("classid must be an integer")
                # if not isinstance(details['days'], str):
                #     raise TypeError("days must be a string")
                # if not isinstance(details['deptcoursenums'], list):
                #     raise TypeError("deptcoursenums must be a list") 
                return details
                
        elif not response: 
            print(f"{sys.argv[0]}: no class with classid " +
                            str(args.classid) + " exists", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"{sys.argv[0]}: {str(e)}", file=sys.stderr)
        sys.exit(1)
#-----------------------------------------------------------------------
def print_response(details):
    try:
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
    except Exception as e:
        print(f"{sys.argv[0]}: {str(e)}", file=sys.stderr)
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
            
            send_request(args, sock)
            
            response = receive_response(sock)
            
            details = validate_response(args, response)
            print_response(details)

    except Exception as e:
        print(f"{sys.argv[0]}: {str(e)}", file=sys.stderr)
        sys.exit(1)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()
