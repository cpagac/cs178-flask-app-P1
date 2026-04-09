# dbCode.py
# Author: Coleman Pagac
# Generic helper functions for database connection and queries

import pymysql
import creds


def get_conn():
    """Returns a connection to the MySQL RDS instance."""
    return pymysql.connect(
        host=creds.host,
        user=creds.user,
        password=creds.password,
        db=creds.db,
        cursorclass=pymysql.cursors.DictCursor,
    )


def execute_query(query, args=()):
    """Executes a SELECT query and returns all rows as dictionaries."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(query, args)
            return cur.fetchall()
    finally:
        conn.close()


def execute_write(query, args=()):
    """Executes an INSERT/UPDATE/DELETE query and returns the last row id."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(query, args)
            conn.commit()
            return cur.lastrowid
    finally:
        conn.close()

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



def get_random_snippet():
    """Returns one random snippet with author metadata."""
    query = """
        SELECT s.id, s.text, a.name AS author_name, a.is_ai
        FROM Snippets s
        JOIN Authors a ON s.author_id = a.id
        ORDER BY RAND()
        LIMIT 1
    """
    rows = execute_query(query)
    return rows[0] if rows else None


def record_answer(user_id, username, snippet_id, is_correct):
    """Inserts a user answer and updates snippet counters."""
    execute_write(
        """
        INSERT INTO Answers (user_id, username, snippet_id, is_correct)
        VALUES (%s, %s, %s, %s)
        """,
        (user_id, username, snippet_id, int(bool(is_correct))),
    )

    if is_correct:
        execute_write(
            "UPDATE Snippets SET correct_guesses = correct_guesses + 1 WHERE id = %s",
            (snippet_id,),
        )
    else:
        execute_write(
            "UPDATE Snippets SET incorrect_guesses = incorrect_guesses + 1 WHERE id = %s",
            (snippet_id,),
        )


def get_snippet_accuracy(snippet_id):
    """Returns aggregate snippet accuracy stats."""
    query = """
        SELECT
            COUNT(*) AS total_answers,
            SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) AS correct_answers
        FROM Answers
        WHERE snippet_id = %s
    """
    stats = execute_query(query, (snippet_id,))[0]
    total = stats["total_answers"] or 0
    correct = stats["correct_answers"] or 0
    pct = (correct / total * 100) if total else 0
    return {
        "total_answers": total,
        "correct_answers": correct,
        "correct_pct": pct,
    }


def get_user_stats(user_id):
    """Returns aggregate and streak stats for a user."""
    summary_query = """
        SELECT
            COUNT(*) AS total_answers,
            SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) AS correct_answers
        FROM Answers
        WHERE user_id = %s
    """
    summary = execute_query(summary_query, (user_id,))[0]
    total_answers = summary["total_answers"] or 0
    correct_answers = summary["correct_answers"] or 0

    history = execute_query(
        """
        SELECT is_correct
        FROM Answers
        WHERE user_id = %s
        ORDER BY timestamp, id
        """,
        (user_id,),
    )
    outcomes = [bool(row["is_correct"]) for row in history]

    current_streak = 0
    for value in reversed(outcomes):
        if value:
            current_streak += 1
        else:
            break

    longest_correct_streak = 0
    longest_wrong_streak = 0
    run_value = None
    run_length = 0

    for value in outcomes:
        if value == run_value:
            run_length += 1
        else:
            if run_value is True:
                longest_correct_streak = max(longest_correct_streak, run_length)
            elif run_value is False:
                longest_wrong_streak = max(longest_wrong_streak, run_length)
            run_value = value
            run_length = 1

    if run_value is True:
        longest_correct_streak = max(longest_correct_streak, run_length)
    elif run_value is False:
        longest_wrong_streak = max(longest_wrong_streak, run_length)

    accuracy_pct = (correct_answers / total_answers * 100) if total_answers else 0

    return {
        "total_answers": total_answers,
        "correct_answers": correct_answers,
        "accuracy_pct": accuracy_pct,
        "current_streak": current_streak,
        "longest_correct_streak": longest_correct_streak,
        "longest_wrong_streak": longest_wrong_streak,
    }


def get_leaderboard():
    """Returns all leaderboard category datasets."""
    most_correct = execute_query(
        """
        SELECT
            username,
            SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) AS correct_answers
        FROM Answers
        GROUP BY username
        ORDER BY correct_answers DESC, username ASC
        LIMIT 10
        """
    )

    best_accuracy = execute_query(
        """
        SELECT
            username,
            COUNT(*) AS total_answers,
            SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) AS correct_answers,
            (SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) / COUNT(*)) * 100 AS accuracy_pct
        FROM Answers
        GROUP BY username
        HAVING COUNT(*) >= 10
        ORDER BY accuracy_pct DESC, total_answers DESC, username ASC
        LIMIT 10
        """
    )

    tripped_up = execute_query(
        """
        SELECT
            s.id AS snippet_id,
            LEFT(s.text, 120) AS snippet_preview,
            COUNT(a.id) AS total_answers,
            SUM(CASE WHEN a.is_correct = 1 THEN 1 ELSE 0 END) AS correct_answers,
            (SUM(CASE WHEN a.is_correct = 1 THEN 1 ELSE 0 END) / COUNT(a.id)) * 100 AS correct_pct
        FROM Snippets s
        JOIN Answers a ON a.snippet_id = s.id
        GROUP BY s.id, s.text
        ORDER BY correct_pct ASC, total_answers DESC
        LIMIT 1
        """
    )

    users = execute_query("SELECT DISTINCT user_id, username FROM Answers ORDER BY username")
    longest_correct = []
    longest_wrong = []

    for user in users:
        stats = get_user_stats(user["user_id"])
        longest_correct.append({"username": user["username"], "streak": stats["longest_correct_streak"]})
        longest_wrong.append({"username": user["username"], "streak": stats["longest_wrong_streak"]})

    longest_correct.sort(key=lambda row: (-row["streak"], row["username"]))
    longest_wrong.sort(key=lambda row: (-row["streak"], row["username"]))

    return {
        "most_correct": most_correct,
        "longest_correct": [row for row in longest_correct if row["streak"] > 0][:10],
        "longest_wrong": [row for row in longest_wrong if row["streak"] > 0][:10],
        "most_tripped_up": tripped_up[0] if tripped_up else None,
        "best_accuracy": best_accuracy,
    }
