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
        
        # Create request object
        request = ['get_details', {
            'class_id': args.class_id
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
                    print(line, end='') 
            
            # Something like this...?
            
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
