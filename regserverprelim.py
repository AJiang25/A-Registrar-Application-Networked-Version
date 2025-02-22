#!/usr/bin/env python

#-----------------------------------------------------------------------
# regserverprelim.py
# Authors: Arnold Jiang and Amanda Chan
#-----------------------------------------------------------------------
# imports
import sys
import sqlite3
import argparse
import contextlib
import socket
import json
import os
import threading
import time
#-----------------------------------------------------------------------

CDELAY = int(os.environ.get('CDELAY','0'))
IODELAY = int(os.environ.get('IODELAY', '0'))

#-----------------------------------------------------------------------
class ClientHandlerThread (threading.Thread):

    def __init__(self, sock):
        threading.Thread.__init__(self)
        self._sock = sock

    def run(self):
        try:
            print('Spawned child thread')
            with self._sock:
                handleClient(self._sock)
            print('Closed socket in child thread')
            print('Exiting child thread')

        except Exception as e:
            print(f"{sys.argv[0]}: {str(e)}", file=sys.stderr)
            sys.exit(1)
#-----------------------------------------------------------------------
def consume_cpu_time(delay):
    initial_thread_time = time.thread_time()
    while (time.thread_time() - initial_thread_time) < delay:
        pass

#-----------------------------------------------------------------------
def handleClient(sock):
    data = readRequest(sock)
    checkRequest(data)

    time.sleep(IODELAY)
    consume_cpu_time(CDELAY)

    if(data[0]=='get_overviews'):
        # data[1].get('dept', '')
        response = getOverviews(dept = data['dept'], num = data['coursenum'],
                               area = data['area'], title = data['title'])
    elif(data[0]=='get_details'):
        response = getDetails(classid=data['classid'])
    else:
        response = [False, "Invalid Request"]
    writeResponse(response, sock)
    
#-----------------------------------------------------------------------
def readRequest(sock):
    reader = sock.makefile(mode='r', encoding='ascii')
    json_str = reader.readline()
    data = json.loads(json_str)
    return data

#-----------------------------------------------------------------------
def checkRequest(data):
    data

#-----------------------------------------------------------------------
def writeResponse(response, sock):
    writer = sock.makefile(mode='w', encoding='ascii')
    
    # Converts the response object to json
    json_response = json.dumps(response)
    writer.write(json_response + '\n')
    writer.flush()
#-----------------------------------------------------------------------
def getOverviews(dept = None, num = None, area = None, title = None):
    
    DATABASE_URL = 'file:reg.sqlite?mode=ro'
    
    with sqlite3.connect(DATABASE_URL, isolation_level = None, uri = True) as connection:
        with contextlib.closing(connection.cursor()) as cursor:
            
            conditions = []
            descriptors = []
            query = """
                SELECT DISTINCT cl.classid, cr.dept, cr.coursenum, c.area, c.title 
                FROM courses c 
                JOIN crosslistings cr ON c.courseid = cr.courseid 
                JOIN classes cl ON c.courseid = cl.courseid
            """
            if dept:
                conditions.append("cr.dept LIKE ? ESCAPE '\\'")
                descriptor = dept.lower().replace("%", r"\%").replace("_", r"\_")
                descriptors.append(f"%{descriptor}%")
            if num:
                conditions.append("cr.coursenum LIKE ? ESCAPE '\\'")
                descriptor = num.lower().replace("%", r"\%").replace("_", r"\_")
                descriptors.append(f"%{descriptor}%")
            if area:
                conditions.append("c.area LIKE ? ESCAPE '\\'")
                descriptor = area.lower().replace("%", r"\%").replace("_", r"\_")
                descriptors.append(f"%{descriptor}%")
            if title:
                conditions.append("c.title LIKE ? ESCAPE '\\'")
                descriptor = title.lower().replace("%", r"\%").replace("_", r"\_")
                descriptors.append(f"%{descriptor}%")
            if conditions:
                query += "WHERE " + " AND ".join(conditions)

            query += "ORDER BY cr.dept ASC, cr.coursenum ASC, cl.classid ASC;"
            cursor.execute(query, descriptors)
            courses = cursor.fetchall()
            result = []
            for row in courses:
                result.append({
                    'classid': row[0],
                    'dept': row[1],
                    'coursenum': row[2],
                    'area': row[3],
                    'title': row[4]
                })
            return [True, result]      

#-----------------------------------------------------------------------
def getDetails(classid = None):

    DATABASE_URL = 'file:reg.sqlite?mode=ro'

    with sqlite3.connect(DATABASE_URL, isolation_level = None, uri = True) as connection:
        with contextlib.closing(connection.cursor()) as cursor:

            class_query = """
                SELECT classid, days, starttime, endtime, bldg, roomnum, courseid
                FROM classes
                WHERE classid = ?
            """
            course_query = """
                SELECT DISTINCT c.courseid, c.area, c.title, c.descrip, c.prereqs
                    FROM courses c
                    WHERE c.courseid = ?
            """
            dept_query = """
                SELECT DISTINCT cr.dept, cr.coursenum
                    FROM crosslistings cr
                    WHERE cr.courseid = ?
                    ORDER BY cr.dept ASC, cr.coursenum ASC
            """
            prof_query = """
                SELECT DISTINCT p.profname
                    FROM courses c
                    JOIN coursesprofs cp ON c.courseid = cp.courseid
                    JOIN profs p ON cp.profid = p.profid
                    WHERE c.courseid = ?
                    ORDER BY p.profname ASC
            """

            cursor.execute(class_query, [classid])
            class_row = cursor.fetchall()
            if not class_row:
                return False

            courseid = class_row[0][6]

            cursor.execute(course_query, [courseid])
            course_row = cursor.fetchone()

            cursor.execute(dept_query, [courseid])
            dept_row = cursor.fetchall()

            cursor.execute(prof_query, [courseid])
            prof_row = cursor.fetchall()
            
            result = {
                'classid': course_row[0],
                'days': course_row[1],
                'starttime': course_row[2],
                'endtime': course_row[3],
                'bldg': course_row[4],
                'roomnum': course_row[5],
                'courseid': courseid,
                'deptcoursenums': [{'dept': dept[0], 'coursenum': dept[1]} for dept in dept_row],
                'area': course_row[5],
                'title': course_row[5],
                'description': course_row[5],
                'prereqs': course_row[5],
                'profnames': [prof[0] for prof in prof_row]
            }
            return [True, result]

#-----------------------------------------------------------------------
def main():

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
        print('Bound server socket to port')
        server_sock.listen()
        print('Listening')

        while True:
            try:
                sock, _ = server_sock.accept()
                print('Accepted connection')
                print('Opened socket')
                client_handler_thread=ClientHandlerThread(sock)
                client_handler_thread.start()
           
                #with sock change to threading lecture (handle client in threading class),
                #  handleclient function is pretty intensive and long, no sqlite connection, handle JSON documents
                # JSON functions, interact with database part is kept from the sql database,

                # with sqlite should be in handle_client. overarching sqlite kept from 
                # last assignment and put in getoverviews function. handle threading in the main function. Call 
                # something that handles threading. In a client_handler_thread, you will call 
                # handle_client which is a function that will process JSON documents and getoverviews function. 

                # DON'T NEED THIS START 
                # with sock:
                #     print('Accepted connection')
                #     print('Opened socket')
                #     print('Server IP addr and port:',
                #           sock.getsockname())
                #     print('Client IP addr and port:', client_addr)
                #     #handle_client(sock)
                # DON'T NEED THIS END

                handleClient(sock)

            except Exception as ex:
                print(ex, file=sys.stderr)    

    except Exception as e:
        print(f"{sys.argv[0]}: {str(e)}", file=sys.stderr)
        sys.exit(1)
#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()
