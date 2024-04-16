from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
from datetime import datetime
from flask_mail import Mail,Message
import pickle
import pandas as pd
import xgboost as xgb


app = Flask(__name__)

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='root'
app.config['MYSQL_DB']='major'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Use your email service provider's SMTP server
app.config['MAIL_PORT'] = 587  # Port for outgoing email
app.config['MAIL_USE_TLS'] = True  # Use TLS encryption
app.config['MAIL_USERNAME'] = 'disasterprediction37@gmail.com'  # Your email address
app.config['MAIL_PASSWORD'] =  'osibbsjgihevazwj' # Your email password

app.secret_key="super secret key"
mail=Mail(app)


mysql=MySQL(app)

model = pickle.load(open('xgboost_earthquake_model.pkl', 'rb'))


@app.route('/home')
def index():  # put application's code here
    return render_template('one.html')

@app.route('/earthquake_awareness')
def earthquake_awareness():
    return render_template('earthquake_awareness.html')

@app.route('/flood_awareness')
def flood_awareness():
    return render_template('flood_awareness.html')

@app.route('/landslide_awareness')
def landslide_awareness():
    return render_template('landslide_awareness.html')

@app.route('/tsunami_awareness')
def tsunami_awareness():
    return render_template('tsunami_awareness.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/earthquake')
def earthquake():
    return render_template('earthquake.html')

@app.route('/tsunami')
def tsunami():
    return render_template('tsunami.html')

@app.route('/flood')
def flood():
    return render_template('flood.html')

@app.route('/landslide')
def landslide():
    return render_template('landslide.html')

@app.route('/earthquake_location')
def earth_Locate():
    # method to display cities from database
    cur = mysql.connection.cursor()
    cur.execute("SELECT city, latitude, longitude FROM City")
    cities_data = cur.fetchall()
    cities = [{'name': city[0], 'latitude': city[1], 'longitude': city[2]} for city in cities_data]
    cur.close()
    return render_template('earthquake_location.html', cities=cities,predicted_alert='', alert_class='')



@app.route('/tsunami_location')
def tsunami_Locate():
    # method to display cities from database
    cur = mysql.connection.cursor()
    cur.execute("SELECT city FROM City")
    cities_data = cur.fetchall()
    cities = [city[0] for city in cities_data]
    cur.close()
    return render_template('tsunami_location.html', cities = cities)

@app.route('/flood_location')
def flood_Locate():
    # method to display cities from database
    cur = mysql.connection.cursor()
    cur.execute("SELECT city FROM City")
    cities_data = cur.fetchall()
    cities = [city[0] for city in cities_data]
    cur.close()
    return render_template('flood_location.html', cities = cities)

@app.route('/landslide_location')
def landslide_Locate():
    # method to display cities from database
    cur = mysql.connection.cursor()
    cur.execute("SELECT city FROM City")
    cities_data = cur.fetchall()
    cities = [city[0] for city in cities_data]
    cur.close()
    return render_template('landslide_location.html', cities = cities)


@app.route('/user-form', methods=['POST'])
def useradd():
    location_earthquake = request.form['location_earthquake']
    magnitude = float(request.form['magnitude'])
    depth = float(request.form['depth'])

    cur = mysql.connection.cursor()
    cur.execute("SELECT city, latitude, longitude FROM City")
    cities_data = cur.fetchall()
    cities = [{'name': city[0], 'latitude': city[1], 'longitude': city[2]} for city in cities_data]
    cur.close()

    selected_city = next((city for city in cities if city['name'] == location_earthquake), None)
    if selected_city:
        latitude = selected_city['latitude']
        longitude = selected_city['longitude']
    else:
        return "Error: Selected city not found", 400

    # Create a DataFrame from user input
    input_data = pd.DataFrame({
        'magnitude': [magnitude],
        'depth': [depth],
        'latitude': [latitude],
        'longitude': [longitude]
    })
    #print(latitude," ",longitude)

    # Make prediction on input data
    input_dmatrix = xgb.DMatrix(input_data)
    prediction = model.predict(input_dmatrix)

    # Mapping prediction to alert levels and colors
    alert_levels = {0: ('green alert', 'green'), 3: ('yellow alert', 'yellow'),
                    1: ('orange alert', 'orange'), 2: ('red alert', 'red')}
    predicted_alert, alert_color = alert_levels.get(prediction[0], ("Unknown alert level", "black"))
    print(predicted_alert," ",alert_color)

    # Create a new record in the database
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO Disaster (location, date, disaster, magnitude, depth, prediction) VALUES (%s, %s, %s, %s, %s, %s)",
                (location_earthquake, datetime.now().date(), "Earthquake", magnitude, depth, predicted_alert))
    mysql.connection.commit()
    cur.close()

    return render_template('earthquake_location.html', cities=cities, predicted_alert=predicted_alert, alert_class=alert_color)

@app.route('/user-form-landslide', methods=['POST'])
def useradd_landslide():
    location_earthquake = request.form['location_earthquake']

    # Create a new record in the database
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO location (location, date, disaster) VALUES (%s, %s, %s)",
                (location_earthquake, datetime.now().date(), "Landslide"))
    mysql.connection.commit()
    cur.close()

    return redirect('/landslide')

@app.route('/user-form-flood', methods=['POST'])
def useradd_flood():
    location_earthquake = request.form['location_earthquake']

    # Create a new record in the database
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO location (location, date, disaster) VALUES (%s, %s, %s)",
                (location_earthquake, datetime.now().date(), "Flood"))
    mysql.connection.commit()
    cur.close()

    return redirect('/flood')

@app.route('/user-form-tsunami', methods=['POST'])
def useradd_tsunami():
    location_earthquake = request.form['location_earthquake']

    # Create a new record in the database
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO location (location, date, disaster) VALUES (%s, %s, %s)",
                (location_earthquake, datetime.now().date(), "Tsunami"))
    mysql.connection.commit()
    cur.close()

    return redirect('/tsunami')

@app.route('/smtp_form', methods=['POST'])
def email():
    if request.method == 'POST':
        subject = request.form['subject']
        message = request.form['message']

    student_email = ['aishwarya.bangar@mitaoe.ac.in','shubhan.ansari@mitaoe.ac.in','visharad.baderao@mitaoe.ac.in']
    msg = Message(subject, sender='your_email@gmail.com', recipients=student_email)
    msg.body = message

    mail.send(msg)
    return redirect('/home')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login-form', methods=['POST'])
def login_form():
    msg=""
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM LOGIN WHERE email=%s AND password=%s',(username,password))
        record=cursor.fetchone()
        if record:
            session['loggedin']=True
            session['username']=record[1]
            return redirect('/add_city')
        else:
            msg='Incorrect username/password'

    return render_template('login.html',msg=msg)

@app.route('/add_city')
def add_city():
    if 'loggedin' in session:
        return render_template('add_city.html', username=session['username'])
    else:
        return redirect('/login')

@app.route('/logout')
def logout():
    if 'loggedin' in session and session['loggedin']:
        # Clear the admin session data
        session.pop('loggedin', None)
        session.pop('username', None)
        flash('Admin logged out successfully', 'success')
        return redirect('/login')
    else:
        flash('You are not currently logged in as an admin', 'error')

    # session.pop('loggedin',None)
    # session['loggedin']=False
    # session.pop('username',None)



if __name__ == '__main__':
    app.run(debug=True)