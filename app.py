from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import datetime

app = Flask(__name__)

# MySQL connection details
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="pharmacy_gemini_db"
)

mycursor = mydb.cursor()

@app.route('/')
def index():
    mycursor.execute("SELECT * FROM drugs")
    drugs = mycursor.fetchall()
    return render_template('index.html', drugs=drugs)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        price = request.form['price']
        expiration_date = request.form['expiration_date']

        # Validate input data
        if not name or not quantity or not price or not expiration_date:
            return render_template('add.html', error_message="Please fill in all fields.")

        try:
            quantity = int(quantity)
            price = float(price)
            expiration_date = datetime.datetime.strptime(expiration_date, "%Y-%m-%d")
        except ValueError:
            return render_template('add.html', error_message="Invalid input format.")

        mycursor.execute("INSERT INTO drugs (name, quantity, price, expiration_date) VALUES (%s, %s, %s, %s)", (name, quantity, price, expiration_date))
        mydb.commit()
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/view/<int:id>')
def view(id):
    mycursor.execute("SELECT * FROM drugs WHERE id = %s", (id,))
    drug = mycursor.fetchone()
    if drug:
        return render_template('view.html', drug=drug)
    else:
        return "Drug not found."

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        mycursor.execute("SELECT * FROM drugs WHERE name LIKE %s OR id LIKE %s", (f"%{query}%", f"%{query}%"))
        drugs = mycursor.fetchall()
        return render_template('search.html', drugs=drugs, query=query)
    return render_template('search.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    mycursor.execute("SELECT * FROM drugs WHERE id = %s", (id,))
    drug = mycursor.fetchone()
    if drug:
        if request.method == 'POST':
            name = request.form['name']
            quantity = request.form['quantity']
            price = request.form['price']
            expiration_date = request.form['expiration_date']

            # Validate input data
            if not name or not quantity or not price or not expiration_date:
                return render_template('edit.html', drug=drug, error_message="Please fill in all fields.")

            try:
                quantity = int(quantity)
                price = float(price)
                expiration_date = datetime.datetime.strptime(expiration_date, "%Y-%m-%d")
            except ValueError:
                return render_template('edit.html', drug=drug, error_message="Invalid input format.")

            mycursor.execute("UPDATE drugs SET name = %s, quantity = %s, price = %s, expiration_date = %s WHERE id = %s", (name, quantity, price, expiration_date, id))
            mydb.commit()
            return redirect(url_for('index'))
        return render_template('edit.html', drug=drug)
    else:
        return "Drug not found."

@app.route('/delete/<int:id>')
def delete(id):
    mycursor.execute("DELETE FROM drugs WHERE id = %s", (id,))
    mydb.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)