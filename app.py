from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import jsonify


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model for Expenses
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)

    def __repr__(self):
        return f'<Expense {self.title}>'

# Route for home page
@app.route('/')
def index():
    return render_template('index.html')

# Route to add a new expense
@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        title = request.form['title']
        amount = request.form['amount']
        category = request.form['category']
        date = request.form['date']
        
        # Format date correctly
        date_obj = datetime.strptime(date, '%Y-%m-%d')

        new_expense = Expense(title=title, amount=float(amount), category=category, date=date_obj)
        db.session.add(new_expense)
        db.session.commit()
        
        return redirect(url_for('view_expenses'))
    return render_template('add_expense.html')

# Route to view all expenses
@app.route('/expenses')
def view_expenses():
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    return render_template('view_expenses.html', expenses=expenses)

# Route to delete an expense
@app.route('/delete/<int:id>')
def delete_expense(id):
    expense_to_delete = Expense.query.get_or_404(id)
    db.session.delete(expense_to_delete)
    db.session.commit()
    return redirect(url_for('view_expenses'))
@app.route('/api/expenses', methods=['GET'])
def api_get_expenses():
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    return jsonify([
        {
            'id': e.id,
            'title': e.title,
            'amount': e.amount,
            'category': e.category,
            'date': e.date.strftime('%Y-%m-%d')
        } for e in expenses
    ])

# API: Get a single expense by ID
@app.route('/api/expense/<int:id>', methods=['GET'])
def api_get_expense(id):
    expense = Expense.query.get_or_404(id)
    return jsonify({
        'id': expense.id,
        'title': expense.title,
        'amount': expense.amount,
        'category': expense.category,
        'date': expense.date.strftime('%Y-%m-%d')
    })

# API: Create a new expense
@app.route('/api/expense', methods=['POST'])
def api_add_expense():
    data = request.get_json()
    try:
        title = data['title']
        amount = float(data['amount'])
        category = data['category']
        date_obj = datetime.strptime(data['date'], '%Y-%m-%d')
    except (KeyError, ValueError) as e:
        return jsonify({'error': 'Invalid input'}), 400

    new_expense = Expense(title=title, amount=amount, category=category, date=date_obj)
    db.session.add(new_expense)
    db.session.commit()
    return jsonify({'message': 'Expense created', 'id': new_expense.id}), 201

# API: Delete an expense
@app.route('/api/expenses/<int:id>', methods=['DELETE'])
def api_delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    return jsonify({'message': f'Expense {id} deleted'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)