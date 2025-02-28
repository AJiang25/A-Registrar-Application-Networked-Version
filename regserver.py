#!/usr/bin/env python

#-----------------------------------------------------------------------
# regserver.py
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

DATABASE_URL = 'file:reg.sqlite?mode=ro'

#-----------------------------------------------------------------------
class ClientHandlerThread (threading.Thread):

    def __init__(self, sock):
        threading.Thread.__init__(self)
        self._sock = sock

    def run(self):
        try:
            print('Spawned child thread')
            with self._sock:
                handle_client(self._sock)
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
def handle_client(sock):
    try:
        request = read_request(sock)
        valid, error_message = check_request(request)
        if not valid:
            write_response(error_message, sock)

        time.sleep(IODELAY)
        consume_cpu_time(CDELAY)

        request_type = request[0]
        parameters = request[1]

        if request_type=='get_overviews':
            response = get_overviews(parameters)
        elif request_type=='get_details':
            response = get_details(parameters)
        else:
            response = [False, "Invalid Request"]
    except ValueError as ve:
        response = [False, str(ve)]
    except Exception as e:
        response = [
            False,
            f"{sys.argv[0]}: {str(e)}"
        ]

    write_response(response, sock)

#-----------------------------------------------------------------------
def read_request(sock):
    reader = sock.makefile(mode='r', encoding='ascii')
    json_str = reader.readline()
    data = json.loads(json_str)
    return data

#-----------------------------------------------------------------------
def check_request(data):
    response = (True, "")
    if not isinstance(data, list) or len(data) != 2:
        response = (
            False,
            "Invalid format: Request must be a list with two elements."
        )

    request_type = data[0]
    parameters = data[1]

    if not isinstance(request_type, str):
        response = (
            False,
            "Invalid format: First element must be a string."
        )

    if request_type == "get_overviews":
        if not isinstance(parameters, dict):
            response = (
                False,
"Invalid format: Expected a dictionary for get_overview parameters."
            )

        required_keys = {"dept", "coursenum", "area", "title"}
        if set(parameters.keys()) != required_keys:
            response = (
                False,
"Invalid format: Parameters must have [dept, coursenum, area, title]."
)

        for key, value in parameters.items():
            if not isinstance(value, str):
                response = (
                    False,
                    "Invalid format: " + {key} + " must be a string.",
                )

    elif request_type == "get_details":
        if not isinstance(parameters, int):
            response = (
                False,
"Invalid format: Expected an integer for classid in get_details req."
            )

        if parameters <= 0:
            response = (
                False,
"Invalid format: classid must be a positive integer."
            )

    else:
        response = (
            False,
"Invalid type: Request type must be 'get_overviews' or 'get_details'."
        )
    return response

#-----------------------------------------------------------------------
def write_response(response, sock):
    writer = sock.makefile(mode='w', encoding='ascii')

    # Converts the response object to json
    json_response = json.dumps(response)
    print(json_response)
    writer.write(json_response + '\n')
    writer.flush()
#-----------------------------------------------------------------------
def get_overviews(parameters):

    dept = parameters.get("dept", "")
    coursenum = parameters.get("coursenum", "")
    area=parameters.get("area", "")
    title =parameters.get("title", "")

    try:
        with sqlite3.connect(
            DATABASE_URL,
            isolation_level = None,
            uri = True
        ) as connection:
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
                    descriptor = dept.lower(
                        ).replace("%", r"\%").replace("_", r"\_")
                    descriptors.append(f"%{descriptor}%")
                if coursenum:
                    conditions.append("cr.coursenum LIKE ? ESCAPE '\\'")
                    descriptor = coursenum.lower(
                        ).replace("%", r"\%").replace("_", r"\_")
                    descriptors.append(f"%{descriptor}%")
                if area:
                    conditions.append("c.area LIKE ? ESCAPE '\\'")
                    descriptor = area.lower(
                        ).replace("%", r"\%").replace("_", r"\_")
                    descriptors.append(f"%{descriptor}%")
                if title:
                    conditions.append("c.title LIKE ? ESCAPE '\\'")
                    descriptor = title.lower(
                        ).replace("%", r"\%").replace("_", r"\_")
                    descriptors.append(f"%{descriptor}%")
                if conditions:
                    query += "WHERE " + " AND ".join(conditions)

                query += "ORDER BY cr.dept ASC,"
                query += "cr.coursenum ASC, cl.classid ASC;"
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

    except Exception as e:
        return [False, str(e)]

#-----------------------------------------------------------------------
def get_details(classid):
    try:
        with sqlite3.connect(
            DATABASE_URL,
            isolation_level = None,
            uri = True
        ) as connection:
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

                print("class id: ", classid)
                cursor.execute(class_query, [classid])

                class_row = cursor.fetchone()
                if not class_row:
                    return [False, "Class not found"]

                courseid = class_row[6]

                cursor.execute(course_query, [courseid])
                course_row = cursor.fetchone()
                if not course_row:
                    return [False, "Course not found"]

                cursor.execute(dept_query, [courseid])
                dept_row = cursor.fetchall()

                cursor.execute(prof_query, [courseid])
                prof_row = cursor.fetchall()

                result = {
                    'classid': class_row[0],
                    'days': class_row[1],
                    'starttime': class_row[2], 
                    'endtime': class_row[3],
                    'bldg': class_row[4],
                    'roomnum': class_row[5],
                    'courseid': course_row[0],
                    'deptcoursenums': [
                        {
                        'dept': dept[0],
                        'coursenum': dept[1]
                        } for dept in dept_row],
                    'area': course_row[1],
                    'title': course_row[2],
                    'descrip': course_row[3],
                    'prereqs': course_row[4],
                    'profnames': [prof[0] for prof in prof_row]
                }

                return [True, result]

    except Exception as e:
        return [False, str(e)]

#-----------------------------------------------------------------------
def main():

    parser = argparse.ArgumentParser(
        description = 'Server for the registrar application'
    )
    parser.add_argument(
        'port',
        type = int,
        help = 'the port at which the server is listening'
    )

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

            except Exception as ex:
                print(ex, file=sys.stderr)

    except Exception as e:
        print(f"{sys.argv[0]}: {str(e)}", file=sys.stderr)
        sys.exit(1)
#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()
