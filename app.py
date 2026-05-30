from flask import Flask, request, redirect, url_for, render_template
from database import create_table, add_expense, get_all_expenses, get_weekly_summary, get_ai_insights, reset_expenses

app = Flask(__name__)
create_table() # create the DB table when app starts

@app.route('/')
def home():
    expenses = get_all_expenses()
    summary = get_weekly_summary()
    insights = get_ai_insights(summary)
    return render_template('index.html', expenses = expenses, summary = summary, insights = insights)

@app.route('/add', methods = ['POST'])
def add():
    amount = float(request.form['amount'])
    category = request.form['category']
    description = request.form['description']
    add_expense(amount, category, description)
    return redirect(url_for('home'))


@app.route('/reset', methods=['POST'])
def reset():
    reset_expenses()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)