#!/usr/bin/env python

#-----------------------------------------------------------------------
# regdetails.py
# Authors: Arnold Jiang and Amanda Chan
#-----------------------------------------------------------------------


#-----------------------------------------------------------------------
# imports
import sys
import sqlite3
import textwrap
import argparse
import contextlib
#-----------------------------------------------------------------------
def print_wrapped(text):
    print(textwrap.fill(text, width = 72, break_long_words=False,
                        replace_whitespace=False, subsequent_indent=" "*3))

#-----------------------------------------------------------------------

def display_class_info(cursor, classid = None):
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
                                     'Registrar application: show details about a class')
    parser.add_argument('host',  help =
                        'the computer on which the server is running')
    # type is IP address or domain name for host
    parser.add_argument('port',  type = int, help =
                        'the port at which the server is listening')
    parser.add_argument('classid', type = int, help =
                        'the id of the class whose details should be shown')

    try:
        # Parses the stdin arguments
        args = parser.parse_args()

        # Connects to the database and creates a curser connection
        with sqlite3.connect(DATABASE_URL, isolation_level = None, uri = True) as connection:
            with contextlib.closing(connection.cursor()) as cursor:

                # Calls the displayClassInfo function
                successful = display_class_info(cursor = cursor, classid=args.classid)

                # Error statement
                if not successful:
                    print(f"{sys.argv[0]}: no class with classid " +
                          str(args.classid) + " exists", file=sys.stderr)
                    sys.exit(1)

    except Exception as e:
        print(f"{sys.argv[0]}: {str(e)}", file=sys.stderr)
        sys.exit(1)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()
