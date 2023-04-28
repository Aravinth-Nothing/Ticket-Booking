from flask import Flask,render_template,request,redirect,url_for,session
import sqlite3
app = Flask(__name__)
app.secret_key = 'HereIs!'
@app.template_filter('to_int')
def to_int(value):
    return int(value)
@app.route('/')
def index():
    return render_template('index.html',name='Aravinth',title='Profile',image='index-img.jpg') 
@app.route('/admin/home',methods=['GET','POST'])
def admin_page():
    with sqlite3.connect('ticketbooking.db') as conn:
        cursor = conn.execute("SELECT * FROM venues")
        venues = cursor.fetchall()
        cursor2=conn.execute("SELECT * FROM Shows")
        shows=cursor2.fetchall()
    return render_template('admin_page.html', venues=venues, shows=shows)    
@app.route('/admin/delete_show/<int:show_id>', methods=['POST'])
def delete_show(show_id):
  with sqlite3.connect('ticketbooking.db') as conn:
    cursor=conn.execute('DELETE FROM shows WHERE id = ?', (show_id,))
    conn.commit()
  return redirect(url_for('admin_page'))  
@app.route('/admin/delete_venue/<int:venue_id>', methods=['POST'])
def delete_venue(venue_id):
  with sqlite3.connect('ticketbooking.db') as conn:
    cursor=conn.execute('DELETE FROM venues WHERE id = ?', (venue_id,))
    cursor=conn.execute('DELETE FROM Shows WHERE VenueId=?',(venue_id,))
    conn.commit()
  return redirect(url_for('admin_page'))
@app.route('/admin/home/update_show/<int:show_id>',methods=['GET','POST'])
def update_show(show_id):
    if request.method=='POST':
        name=request.form['name']
        rating=request.form['rating']
        timing=request.form['timing']
        tags=request.form['tags']
        price=request.form['price']
        with sqlite3.connect('ticketbooking.db') as conn:
            conn.execute('UPDATE Shows SET Name=?, Rating=?, Timing=?, Tags=?, TicketPrice=? WHERE Shows.id=?',(name,rating,timing,tags,price,show_id))
            conn.commit()
        return redirect(url_for('admin_page'))
@app.route('/admin/home/update_venue/<int:venue_id>',methods=['GET','POST'])
def update_venue(venue_id):
    if request.method=='POST':
        name=request.form['name']
        place=request.form['place']
        capacity=request.form['capacity']
        location=request.form['location']
        with sqlite3.connect('ticketbooking.db') as conn:
            conn.execute('UPDATE venues SET name=?, place=?, capacity=?, location=? WHERE venues.id=?',(name,place,capacity,location,venue_id))
            conn.commit()
        return redirect(url_for('admin_page'))
@app.route('/admin/edit_show/<int:show_id>', methods=['GET','POST'])
def edit_show(show_id):
    with sqlite3.connect('ticketbooking.db') as conn:
        cursor = conn.execute('SELECT * FROM shows WHERE id = ?', (show_id,))
        show=cursor.fetchone()
    return render_template('edit_show.html', show=show)
@app.route('/admin/edit_venue/<int:venue_id>', methods=['GET','POST'])
def edit_venue(venue_id):
    with sqlite3.connect('ticketbooking.db') as conn:
        cursor = conn.execute('SELECT * FROM venues WHERE id = ?', (venue_id,))
        venue=cursor.fetchone()
    return render_template('edit_venue.html', venue=venue)
@app.route('/admin/login',methods=['GET','POST'])
def admin_login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        with sqlite3.connect('ticketbooking.db') as conn:
            cursor = conn.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
            result = cursor.fetchone()
        if result:
            return redirect(url_for('admin_page'))
        else:
            message="Invalid UserName or Password"
            return render_template('admin_login.html',message=message)
    return render_template('admin_login.html')
@app.route('/user/login',methods=['GET','POST'])
def user_login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        with sqlite3.connect('ticketbooking.db') as conn:
            cursor=conn.execute("SELECT * FROM user WHERE username=? AND password=?",(username,password))
            result=cursor.fetchone()
        if result:
            session['user_id'] = result[0]
            return redirect(url_for('user_page'))
        else:
            message="Invalid UserName or Password"
            return render_template('user_login.html',message=message)
    return render_template('user_login.html')
@app.route('/user/register',methods=['GET','POST'])
def register():
    i=0
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        confirm_password=request.form['confirm_password']
        try:
            if len(str(username))==0 and len(str(password))==0:
                message="User ID or Password Is null."
                return render_template('register.html',message=message)
            if password==confirm_password:
                with sqlite3.connect('ticketbooking.db') as conn:
                    cursor = conn.execute("SELECT MAX(id) FROM user")
                    result = cursor.fetchone()
                    if result[0] is not None:
                        i = result[0] + 1 
                    else:
                        i = 1
                    conn.execute('INSERT INTO user (id, username, password) VALUES(?, ?, ?)',(i,username,password))
                    conn.commit()
                return redirect(url_for('user_login'))
            else:
                message="Passwords don't match!"
                return render_template('register.html',message=message)
        except Exception as e:
            return str(e)
    return render_template('register.html')
@app.route('/admin/home/new_venue',methods=['GET','POST'])
def new_venue():
    if request.method=='POST':
        name=request.form['name']
        place=request.form['place']
        capacity=request.form['capacity']
        location=request.form['location']
        with sqlite3.connect('ticketbooking.db') as conn:
            cursor = conn.execute("SELECT MAX(id) FROM venues")
            row = cursor.fetchone()
            i = 1 if row[0] is None else row[0] + 1 
            conn.execute('INSERT INTO venues (id, name, place, capacity, location) VALUES(?, ?, ?, ?,?)',(i,name,place,capacity,location))
            conn.commit() 
        return redirect(url_for('admin_page'))
    return render_template('new_venue.html')
@app.route('/admin/home/<int:id>/new_show',methods=['GET','POST'])
def new_show(id):
    with sqlite3.connect('ticketbooking.db') as conn:
        cursor = conn.execute("SELECT * FROM venues")
        venues = cursor.fetchall()
    if request.method=='POST':
        name=request.form['name']
        rating=request.form['rating']
        timing=request.form['timing']
        tags=request.form['tags']
        price=request.form['price']
        if request.form.getlist('venues'):
            with sqlite3.connect('ticketbooking.db') as conn:
                people=request.form.getlist('venues')
                for j in people:
                    cursor = conn.execute("SELECT MAX(id) FROM Shows")
                    row = cursor.fetchone() 
                    cursor2=conn.execute("SELECT * FROM venues WHERE id=?",(j,))
                    row2=cursor2.fetchone()  
                    i = 1 if row[0] is None else row[0] + 1 
                    conn.execute('INSERT INTO Shows (ID, Name, Rating, Timing, Tags, TicketPrice, VenueID, capacity) VALUES(?, ?, ?, ?,?,?,?,?)',(i,name,rating,timing,tags,price,j,row2[3]))
                    conn.commit()
            return redirect(url_for('admin_page'))
        with sqlite3.connect('ticketbooking.db') as conn:
            cursor = conn.execute("SELECT MAX(id) FROM Shows")
            row = cursor.fetchone()
            cursor2=conn.execute("SELECT * FROM venues WHERE id=?",(id,))
            row2=cursor2.fetchone()
            i = 1 if row[0] is None else row[0] + 1 
            conn.execute('INSERT INTO Shows (ID, Name, Rating, Timing, Tags, TicketPrice, VenueID, capacity) VALUES(?, ?, ?, ?,?,?,?,?)',(i,name,rating,timing,tags,price,id,row2[3]))
            conn.commit()
        return redirect(url_for('admin_page'))
    return render_template('new_show.html',id=id,venues=venues)
@app.route('/user/home', methods=['GET', 'POST'])
def user_page():
    with sqlite3.connect('ticketbooking.db') as conn:
        cursor = conn.execute("SELECT * FROM venues")
        venues = cursor.fetchall()
        cursor2 = conn.execute("SELECT * FROM Shows")
        shows = cursor2.fetchall()
    user_id = session.get('user_id')
    if request.method == 'POST':
        query = request.form['query']
        if query:
            return redirect(url_for('search_shows', query=query))
    return render_template('user_page.html', venues=venues, shows=shows, user_id=user_id) 
@app.route('/user/search', methods=['GET'])
def search_shows():
    query = request.args.get('query')
    with sqlite3.connect('ticketbooking.db') as conn:
        cursor1=conn.execute("SELECT * FROM venues WHERE name LIKE ? OR place LIKE ? OR location LIKE ?",('%'+query+'%','%'+query+'%','%'+query+'%'))
        cursor = conn.execute("SELECT * FROM Shows JOIN venues ON Shows.VenueId=venues.id WHERE Shows.name LIKE ? OR Shows.tags LIKE ? OR Shows.timing LIKE ? OR Shows.rating LIKE ?", ('%'+query+'%', '%'+query+'%','%'+query+'%','%'+query+'%'))
        shows = cursor.fetchall()
        venues=cursor1.fetchall()
    return render_template('search_results.html', shows=shows, venues=venues)
@app.route('/user/home/book', methods=['GET', 'POST'])
def book():
    global price
    if request.method=='GET':
        session['show_id'] = request.args.get('show_id')
        session['venue_id'] = request.args.get('venue_id')
        show_id=session.get('show_id')
        venue_id=session.get('venue_id')
        user_id = session.get('user_id')
        with sqlite3.connect('ticketbooking.db') as conn:
            cursor = conn.execute("SELECT * FROM Shows WHERE ID=? AND VenueID=?", (show_id, venue_id))
            show_details = cursor.fetchall()
            session['price'] = show_details[0][5]
            price=session.get('price')
            user_id = session.get('user_id')
            return render_template('book.html',price=price)
    if request.method == 'POST':
        no_tickets=request.form['no_tickets']
        show_id = session.get('show_id')
        venue_id = session.get('venue_id')
        price=session.get('price')
        try:
            total_price=price*int(no_tickets)
            user_id = session.get('user_id')
            with sqlite3.connect('ticketbooking.db') as conn:
                cursor = conn.execute("SELECT MAX(id) FROM bookings")
                row = cursor.fetchone()
                i = 1 if row[0] is None else row[0] + 1
                cursor0=conn.execute("SELECT * FROM Shows WHERE id=?",(show_id,)).fetchone()
                cap=cursor0[7]
                new_cap=int(cap)-int(no_tickets)
                if new_cap>=0:
                    cursor1=conn.execute("INSERT INTO bookings(id,no_seats,price,total_price,user_id,venue_id,show_id) VALUES(?,?,?,?,?,?,?)",(i,no_tickets,price,total_price,user_id,venue_id,show_id))
                    cursor2=conn.execute("UPDATE Shows SET capacity=? WHERE id=?",(new_cap,show_id,))
                    conn.commit()
                    return render_template('book.html', no_tickets=no_tickets, price=price)
                else:
                    message="Exceeded the number of seats available."
                    return render_template('book.html',price=price,message=message)
        except ValueError:
            message="Please Enter a valid number of tickets"
            return render_template('book.html',price=price,message=message)
@app.route('/user/home/bookings', methods=['GET', 'POST'])
def bookings():
    user_id = int(session.get('user_id'))
    with sqlite3.connect('ticketbooking.db') as conn:
        cursor=conn.execute("SELECT bookings.id, shows.name,shows.timing, venues.name,bookings.no_seats, bookings.price FROM bookings JOIN Shows ON bookings.show_id = Shows.id JOIN venues ON bookings.venue_id = venues.id WHERE bookings.user_id = ?",(user_id,))
        user_bookings=cursor.fetchall()
    return render_template('bookings.html',bookings=user_bookings)
app.run()