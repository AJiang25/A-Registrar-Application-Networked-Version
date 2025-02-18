#!/usr/bin/env python

#-----------------------------------------------------------------------
# regoverviews.py
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

#-----------------------------------------------------------------------
def display_classes(cursor, dept = None, num = None, area = None, title = None):
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

    print('%5s %4s %6s %4s %s' % ("ClsId", "Dept", "CrsNum", "Area", "Title"))
    print('%5s %4s %6s %4s %s' % ("-----", "----", "------", "----", "-----"))

    for row in ans:
        res = '%5s %4s %6s %4s %s' % (row[0], row[1], row[2], row[3], row[4])
        print(textwrap.fill(res, width = 72, break_long_words= False, subsequent_indent=" "*23))

#-----------------------------------------------------------------------
def main():
    DATABASE_URL = 'file:reg.sqlite?mode=ro'

    parser = argparse.ArgumentParser(description =
                                     'Registrar application: show overviews of classes')
    parser.add_argument('host',  help =
                        'the computer on which the server is running')
    # type is IP address or domain name for host
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
        
        with socket.socket() as sock:
            sock.connect((args.host, args.port)) 
            flo = sock.makefile(mode='r', encoding='utf-8')
            for line in flo:
                print(line, end='')

            

        # Connects to the database and creates a curser connection
        with sqlite3.connect(DATABASE_URL, isolation_level = None, uri = True) as connection:
            with contextlib.closing(connection.cursor()) as cursor:

                # Calls the displayClasses function
                display_classes(cursor = cursor, dept = args.d, num = args.n,
                               area = args.a, title = args.t)

    except Exception as e:
        print(f"{sys.argv[0]}: {str(e)}", file=sys.stderr)
        sys.exit(1)
#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()
