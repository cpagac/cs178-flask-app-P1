# author: T. Urness and M. Moore
# description: Flask example using redirect, url_for, and flash
# credit: the template html files were constructed with the help of ChatGPT

from flask import Flask, render_template, request, redirect, url_for, flash, session
from dbCode import (
    execute_query,
    get_random_snippet,
    record_answer,
    get_user_stats,
    get_snippet_accuracy,
    get_leaderboard,
)
from dynamoCode import get_or_create_user, increment_games_played

app = Flask(__name__)
app.secret_key = 'your_secret_key' # this is an artifact for using flash displays; 
                                   # it is required, but you can leave this alone

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if not username:
            flash('Please enter a username.', 'warning')
            return render_template('login.html')

        try:
            user_id = get_or_create_user(username)
            session['username'] = username
            session['user_id'] = user_id
            return redirect(url_for('game'))
        except Exception as e:
            flash(f'Database error: {str(e)}', 'danger')
            return render_template('login.html')

    return render_template('login.html')


@app.route('/game')
def game():
    if 'user_id' not in session:
        flash('Please log in to play.', 'warning')
        return redirect(url_for('login'))

    try:
        snippet = get_random_snippet()
    except Exception as e:
        flash(f'Database error: {str(e)}', 'danger')
        snippet = None

    return render_template('arena.html', snippet=snippet, username=session.get('username'))


@app.route('/result', methods=['POST'])
def result():
    if 'user_id' not in session:
        flash('Please log in to play.', 'warning')
        return redirect(url_for('login'))

    snippet_id = request.form.get('snippet_id', type=int)
    guess = request.form.get('guess', '').lower().strip()

    if not snippet_id or guess not in ('human', 'ai'):
        flash('Invalid answer submission. Try again.', 'warning')
        return redirect(url_for('game'))

    try:
        rows = execute_query(
            """
            SELECT s.id, s.text, a.name AS author_name, a.is_ai
            FROM Snippets s
            JOIN Authors a ON s.author_id = a.id
            WHERE s.id = %s
            """,
            (snippet_id,),
        )
        if not rows:
            flash('Snippet not found. Try another round.', 'warning')
            return redirect(url_for('game'))

        snippet = rows[0]
        actual_label = 'ai' if snippet['is_ai'] else 'human'
        is_correct = guess == actual_label

        record_answer(session['user_id'], snippet_id, is_correct)
        increment_games_played(session['username'])
        user_stats = get_user_stats(session['user_id'])
        snippet_stats = get_snippet_accuracy(snippet_id)

        return render_template(
            'result.html',
            snippet=snippet,
            guessed_label=guess,
            actual_label=actual_label,
            is_correct=is_correct,
            user_stats=user_stats,
            snippet_stats=snippet_stats,
            username=session.get('username'),
        )
    except Exception as e:
        flash(f'Database error: {str(e)}', 'danger')
        return redirect(url_for('game'))


@app.route('/leaderboard')
def leaderboard():
    try:
        board = get_leaderboard()
        return render_template('leaderboard.html', board=board)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'danger')
        return redirect(url_for('home'))

@app.route('/add-user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        # Extract form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        genre = request.form['genre']
        
        # Process the data (e.g., add it to a database)
        # For now, let's just print it to the console
        print("Name:", first_name + " " + last_name, ":", "Favorite Genre:", genre)
        
        flash('User added successfully! Huzzah!', 'success')  # 'success' is a category; makes a green banner at the top
        # Redirect to home page or another page upon successful submission
        return redirect(url_for('home'))
    else:
        # Render the form page if the request method is GET
        return render_template('add_user.html')

@app.route('/delete-user',methods=['GET', 'POST'])
def delete_user():
    if request.method == 'POST':
        # Extract form data
        name = request.form['name']
        
        # Process the data (e.g., add it to a database)
        # For now, let's just print it to the console
        print("Name to delete:", name)
        
        flash('User deleted successfully! Hoorah!', 'warning') 
        # Redirect to home page or another page upon successful submission
        return redirect(url_for('home'))
    else:
        # Render the form page if the request method is GET
        return render_template('delete_user.html')


@app.route('/display-users')
def display_users():
    # hard code a value to the users_list;
    # note that this could have been a result from an SQL query :) 
    users_list = (('John','Doe','Comedy'),('Jane', 'Doe','Drama'))
    return render_template('display_users.html', users = users_list)

@app.route('/arena')
def arena():
    return redirect(url_for('game'))


# these two lines of code should always be the last in the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
