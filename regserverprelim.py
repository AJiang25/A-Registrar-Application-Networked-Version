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
import threading

#-----------------------------------------------------------------------
class ClientHandlerThread (threading.Thread):
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self._sock = sock
    
    def run(self):
        print('Spawned child thread')
    
        reader = self.sock.makefile(mode='r', encoding='ascii')
        json_str = reader.readline()
        data = json.loads(json_str)
        with sqlite3.connect(DATABASE_URL, isolation_level = None, uri = True) as connection:
            with contextlib.closing(connection.cursor()) as cursor:
                if(data[0]=='get_overviews'):
                    getOverviews(cursor = cursor, dept = data['dept'], num = data['coursenum'],
                               area = data['area'], title = data['title'])
                elif(data[0]=='get_details'):
                    getDetails(cursor = cursor, classid=data['classid'])
        #response = json.loads(json_str)


        print('Closed socket in child thread')
        print('Exiting child thread')

#-----------------------------------------------------------------------
def getOverviews(cursor, dept = None, num = None, area = None, title = None):
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
    ans = cursor.fetchall()

    # print('%5s %4s %6s %4s %s' % ("ClsId", "Dept", "CrsNum", "Area", "Title"))
    # print('%5s %4s %6s %4s %s' % ("-----", "----", "------", "----", "-----"))

    for row in ans:
        res = '%5s %4s %6s %4s %s' % (row[0], row[1], row[2], row[3], row[4])
        # print(textwrap.fill(res, width = 72, break_long_words= False, subsequent_indent=" "*23))

#-----------------------------------------------------------------------
def getDetails(cursor, classid = None):
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

    print('-------------')
    print('Class Details')
    print('-------------')
    for row in class_row:
        print_wrapped(f"Class Id: {row[0]}")
        print_wrapped(f"Days: {row[1]}")
        print_wrapped(f"Start time: {row[2]}")
        print_wrapped(f"End time: {row[3]}")
        print_wrapped(f"Building: {row[4]}")
        print_wrapped(f"Room: {row[5]}")

    print('--------------')
    print('Course Details')
    print('--------------')

    print_wrapped(f"Course Id: {course_row[0]}")
    for dept in dept_row:
        print_wrapped(f"Dept and Number: {dept[0]} {dept[1]}")
    print_wrapped(f"Area: {course_row[1]}")

    print_wrapped(f"Title: {course_row[2]}")
    print_wrapped(f"Description: {course_row[3]}")
    print_wrapped(f"Prerequisites: {course_row[4]}")

    for prof in prof_row:
        print_wrapped(f"Professor: {prof[0]}")
    return True

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
