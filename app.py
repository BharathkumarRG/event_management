import mysql.connector,sys
import datetime
from mysql.connector import Error
from flask import Flask, request, jsonify, render_template,redirect, url_for
from random import randint


app = Flask(__name__)

# @app.route('/', methods=['GET', 'POST'])
# def renderLoginPage():
#     events = runQuery("SELECT * FROM events")
#     branch = runQuery("SELECT * FROM branch")

#     if request.method == 'POST':
#         Name = request.form['FirstName'] + " " + request.form['LastName']
#         Mobile = request.form['MobileNumber']
#         Branch_id = request.form['Branch']
#         Event = request.form['Event']
#         Email = request.form['Email']
#         College = request.form.get('College', '')  # Assuming there's a College field in the form

#         # Validate mobile number length
#         if len(Mobile) != 10:
#             return render_template('loginfail.html', errors=["Invalid Mobile Number!"])

#         # Validate email format
#         if not Email.endswith('.com'):
#             return render_template('loginfail.html', errors=["Invalid Email!"])

#         # Check if the student is already registered for the event
#         existing_participant = runQuery("SELECT * FROM participants WHERE event_id={} AND mobile='{}'".format(Event, Mobile))
#         if len(existing_participant) > 0:
#             return render_template('loginfail.html', errors=["Student already Registered for the Event!"])

#         # Check if the participants count is full
#         participant_count = runQuery("SELECT COUNT(*) as count FROM participants WHERE event_id={}".format(Event))[0]['count']
#         max_participants = runQuery("SELECT participants FROM events WHERE event_id={}".format(Event))[0]['participants']

#         if participant_count >= max_participants:
#             return render_template('loginfail.html', errors=["Participants count fulfilled already!"])

#         # Insert the new participant
#         insert_query = """
#             INSERT INTO participants (event_id, fullname, email, mobile, branch_id, college) 
#             VALUES ({}, '{}', '{}', '{}', {}, '{}');
#         """.format(Event, Name.replace("'", "''"), Email.replace("'", "''"), Mobile, Branch_id, College.replace("'", "''"))

#         try:
#             runQuery(insert_query)
#             return render_template('index.html', events=events, branchs=branch, errors=["Successfully Registered!"])
#         except Exception as e:
#             print(f"Error inserting participant: {e}")
#             return render_template('loginfail.html', errors=["Registration failed due to an internal error."])

#     return render_template('index.html', events=events, branchs=branch)


@app.route('/',methods=['GET', 'POST'])
def renderLoginPage():
    events = runQuery("SELECT * FROM events")
    branch =  runQuery("SELECT * FROM branch")
    if request.method == 'POST':
        Name = request.form['FirstName'] + " " + request.form['LastName']
        Mobile = request.form['MobileNumber']
        Branch_id = request.form['Branch']
        Event = request.form['Event']
        Email = request.form['Email']

        if len(Mobile) != 10:
            return render_template('loginfail.html',errors = ["Invalid Mobile Number!"])

        if Email[-4:] != '.com':
            return render_template('loginfail.html', errors = ["Invalid Email!"])

        if len(runQuery("SELECT * FROM participants WHERE event_id={} AND mobile={}".format(Event,Mobile))) > 0 :
            return render_template('loginfail.html', errors = ["Student already Registered for the Event!"])

        if runQuery("SELECT COUNT(*) FROM participants WHERE event_id={}".format(Event)) >= runQuery("SELECT participants FROM events WHERE event_id={}".format(Event)):
            return render_template('loginfail.html', errors = ["Participants count fullfilled Already!"])

        # runQuery("INSERT INTO participants(event_id,fullname,email,mobile,college,branch_id) VALUES({},\"{}\",\"{}\",\"{}\",\"{}\");".format(Event,Name,Email,Mobile,Branch_id))
        # runQuery("UPDATE participants SET fullname=Name,email=Email,mobile=Mobile,event_id=1560 ")
        runQuery("Insert into participants(fullname='{}', email='{}', mobile='{}')".format(Name, Email, Mobile))
        # print(runQuery("SELECT * FROM participants"))

        return render_template('index.html',events = events,branchs = branch,errors=["Succesfully Registered!"])

    return render_template('index.html',events = events,branchs = branch)
    


@app.route('/loginfail',methods=['GET'])
def renderLoginFail():
    return render_template('loginfail.html')


@app.route('/admin', methods=['GET', 'POST'])
def renderAdmin():
    if request.method == 'POST':
        UN = request.form['username']
        PS = request.form['password']

        cred = runQuery("SELECT * FROM admin")
        print(cred)
        for user in cred:
            if UN==user[0] and PS==user[1]:
                return redirect('/eventType')

        return render_template('admin.html',errors=["Wrong Username/Password"])

    return render_template('admin.html')    

from flask import Flask, request, render_template

@app.route('/eventType', methods=['GET', 'POST'])
def getEvents():
    # Fetch event types, events, types, and locations
    eventTypes = runQuery("""
        SELECT *,
               (SELECT COUNT(*) 
                FROM participants AS P 
                WHERE T.type_id IN 
                      (SELECT type_id 
                       FROM events AS E 
                       WHERE E.event_id = P.event_id)) AS COUNT 
        FROM event_type AS T;
    """)

    events = runQuery("""
        SELECT event_id, event_title,
               (SELECT COUNT(*) 
                FROM participants AS P 
                WHERE P.event_id = E.event_id) AS count 
        FROM events AS E;
    """)

    types = runQuery("SELECT * FROM event_type;")
    location = runQuery("SELECT * FROM location;")

    if request.method == "POST":
        try:
            # Fetch form data
            Name = request.form["newEvent"]
            fee = request.form["Fee"]
            participants = request.form["maxP"]
            Type = request.form["EventType"]
            Location = request.form["EventLocation"]
            Date = request.form['Date']

            # Debugging print statements
            print(f"Form Data: Name={Name}, Fee={fee}, Participants={participants}, Type={Type}, Location={Location}, Date={Date}")

            # Insert event into the database
            query = """
                INSERT INTO events (event_title, event_price, participants, type_id, location_id, date) 
                VALUES ('{}', {}, {}, {}, {}, '{}');
            """.format(Name, fee, participants, Type, Location, Date)

            runQuery(query)
            print(f"Query executed: {query}")

        except Exception as e:
            print(f"Error inserting event: {e}")

            # Handling deletion of an event if insertion fails
            try:
                EventId = request.form["EventId"]
                delete_query = "DELETE FROM events WHERE event_id={}".format(EventId)
                runQuery(delete_query)
                print(f"Query executed: {delete_query}")
            except Exception as e:
                print(f"Error deleting event: {e}")

    # Render the events page
    return render_template('events.html', events=events, eventTypes=eventTypes, types=types, locations=location)


# @app.route('/eventType',methods=['GET','POST'])
# def getEvents():
#     eventTypes = runQuery("SELECT *,(SELECT COUNT(*) FROM participants AS P WHERE T.type_id IN (SELECT type_id FROM events AS E WHERE E.event_id = P.event_id ) ) AS COUNT FROM event_type AS T;") 

#     events = runQuery("SELECT event_id,event_title,(SELECT COUNT(*) FROM participants AS P WHERE P.event_id = E.event_id ) AS count FROM events AS E;")

#     types = runQuery("SELECT * FROM event_type;")

#     location = runQuery("SELECT * FROM location")


#     if request.method == "POST":
#         try:

#             Name = request.form["newEvent"]
#             fee=request.form["Fee"]
#             participants = request.form["maxP"]
#             Type=request.form["EventType"]
#             Location = request.form["EventLocation"]
#             Date = request.form['Date']
#             runQuery("INSERT INTO events(event_title,event_price,participants,type_id,location_id,date) VALUES(\"{}\",{},{},{},{},\'{}\');".format(Name,fee,participants,Type, Location,Date))

#         except:
#             EventId=request.form["EventId"]
#             runQuery("DELETE FROM events WHERE event_id={}".format(EventId))

#     return render_template('events.html',events = events,eventTypes = eventTypes,types = types,locations = location) 


@app.route('/eventinfo')
def rendereventinfo():
    events=runQuery("SELECT *,(SELECT COUNT(*) FROM participants AS P WHERE P.event_id = E.event_id ) AS count FROM events AS E LEFT JOIN event_type USING(type_id) LEFT JOIN location USING(location_id);")

    return render_template('events_info.html',events = events)

@app.route('/participants',methods=['GET','POST'])
def renderParticipants():
    
    events = runQuery("SELECT * FROM events;")

    if request.method == "POST":
        Event = request.form['Event']

        participants = runQuery("SELECT p_id,fullname,mobile,email FROM participants WHERE event_id={}".format(Event))
        return render_template('participants.html',events = events,participants=participants)

    return render_template('participants.html',events = events)

def runQuery(query):

    try:
        db = mysql.connector.connect( host='localhost',database='event_mgmt',user='root',password='bkguna447')

        if db.is_connected():
            print("Connected to MySQL, running query: ", query)
            cursor = db.cursor(buffered = True)
            cursor.execute(query)
            db.commit()
            res = None
            try:
                res = cursor.fetchall()
            except Exception as e:
                print("Query returned nothing, ", e)
                return []
            return res

    except Exception as e:
        print(e)
        return []

    db.close()

    print("Couldn't connect to MySQL")
    return None


if __name__ == "__main__":
    app.run(debug=True) 
