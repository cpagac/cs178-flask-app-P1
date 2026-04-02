# dbCode.py
# Author: Coleman Pagac
# Generic helper functions for database connection and queries

import pymysql
import creds

def get_conn():
    """Returns a connection to the MySQL RDS instance."""
    conn = pymysql.connect(
        host=creds.host,
        user=creds.user,
        password=creds.password,
        db=creds.db,
    )
    return conn

def execute_query(query, args=()):
    """Executes a SELECT query and returns all rows as dictionaries."""
    cur = get_conn().cursor(pymysql.cursors.DictCursor)
    cur.execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows

def get_all_snippets():
    """Returns all snippets joined with their category name and author info."""
    #NOTE: This function's JOIN query was generated with AI assistance
    query = """
        SELECT s.id, s.text, c.name AS category, a.name AS author, a.is_ai
        FROM Snippets s
        JOIN Categories c ON s.category_id = c.id
        JOIN Authors a ON s.author_id = a.id
        ORDER BY s.id
    """
    return execute_query(query)
