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
    print(textwrap.fill(text, width = 72, break_long_words=False,
                        replace_whitespace=False, subsequent_indent=" "*3))
#-----------------------------------------------------------------------
def sendRequest(args, sock):
    # Create request object
    request = ['get_details', {
        'class_id': args.class_id
    }]
        
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
        
        # check if response is valid, handle the error -> write the response
        response_data = json.loads(response)
        for line in response_data:
            print_wrapped(line, end='') 
            
    elif not response: 
        print(f"{sys.argv[0]}: no class with classid " +
                          str(args.classid) + " exists", file=sys.stderr)
        sys.exit(1)
                    

#-----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description =
                                     'Registrar application: show overviews of classes')
    parser.add_argument('host',  help =
                        'the computer on which the server is running')
    parser.add_argument('port',  type = int, help =
                        'the port at which the server is listening')
    parser.add_argument('-d', type=str, metavar = 'dept', help =
                        'show only those classes whose department contains dept')
    parser.add_argument('-n', type=str, metavar = 'num', help =
                        'show only those classes whose course number contains num')
    parser.add_argument('-a', type=str, metavar = 'area', help =
                        'show only those classes whose distrib area contains area')
    parser.add_argument('-t', type=str, metavar = 'title', help =
                        'show only those classes whose course title contains title')

    try:
        # Parses the stdin arguments
        args = parser.parse_args()
        host = sys.argv[1]
        port = int(sys.argv[2])
        
        
        # Create request object
        request = ['get_overviews', {
            'dept': args.d if args.d else '',
            'coursenum': args.n if args.n else '',
            'area': args.a if args.a else '',
            'title': args.t if args.t else ''
        }]
        
        # Converts the request object to json
        json_request = json.dumps(request)
        
        with socket.socket() as sock:
            sock.connect((host, port)) 
            writer = sock.makefile(mode='w', encoding='ascii')
            reader = sock.makefile(mode='r', encoding='ascii')
            
            # Send the request to the server
            writer.write(json_request + '\n')
            writer.flush()
            
            # Processes the response
            response = reader.readline()
            if response:
                response_data = json.loads(response)
                for line in response_data:
                    print_wrapped(line, end='')
            
            
        #     # Create file objects for socket I/O
        #     with sock.makefile(mode='w', encoding='utf-8') as writer:
        #         with sock.makefile(mode='r', encoding='utf-8') as reader:
                    
        #             # Send request to server
        #             writer.write(json_request + '\n')
        #             writer.flush()
                    
        #             # Receive and print response
        #             response = reader.readline()
        #             if response:
        #                 response_data = json.loads(response)
        #                 if isinstance(response_data, list) and len(response_data) == 2:
        #                     if response_data[0]:  # Success
        #                         print(response_data[1])  # Print formatted results
        #                     else:
        #                         print(f"Error: {response_data[1]}", file=sys.stderr)
        #                         sys.exit(1)
       
    except Exception as e:
        print(f"{sys.argv[0]}: {str(e)}", file=sys.stderr)
        sys.exit(1)
#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()
