import re
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required
from flask_sqlalchemy import SQLAlchemy
import requests
import sqlite3
from datetime import datetime, timedelta


app = Flask(__name__)



app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///guardian.db")

@app.route("/")
def index():
    """Engine"""
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST
    if request.method == "POST":
        # User sumbit username
        name = request.form.get("name")
        last_name = request.form.get("last_name")
        username = request.form.get("username")
        email = request.form.get("email")
        # User sumbit password
        password = request.form.get("password")
        # User sumbit password confirmation
        confirmation = request.form.get("confirmation")
        # Ensure username was sumbitted
        if not name:
            return apology("Must provide name")

        if not last_name:
            return apology("Must provide last_name")

        if not email:
            return apology("Must provide last_name")
        if not username:
            return apology("Must provide username")
        # Ensure password was sumbitted
        if not password:
            return apology("Must provide password")
        # Ensure password confirmation was sumbitted
        if not confirmation:
            return apology("Must provide password confirmation")
        # Ensure password match with confirmation
        
        if password != confirmation:
            return apology("Password doesn't match with confirmation")

        email_check = db.execute("SELECT * FROM accounts WHERE email = ?", email)
        if len(email_check) == 1:
            return apology("Email has already been used")
        # Hash password
        hash = generate_password_hash(password)
        # Ensure username does not exist
        username_check = db.execute("SELECT * FROM accounts WHERE username = ?", username)
        if len(username_check) == 1:
            return apology("Username has already used")
        # Add to database username and password
        register = db.execute("INSERT INTO accounts (username, name,last_name,email,password) VALUES (?, ?,?,?,?)", username, name,last_name,email,hash)
        # Create session for user
        session["user_id"] = register
        # Flash message
        flash("Registred")
        # Redirect user to home page
        return redirect("/")
    # User reached route via GET
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM accounts WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/filtre", methods=["GET", "POST"])
@login_required
def filtre():
    if request.method == "POST":
        edit = request.form.get("edit")
        cycle = request.form.get("cycle")
        water = request.form.get("water")
        sunlight = request.form.get("sunlight")
        indoor = request.form.get("indoor")
        poisonous = request.form.get("poisonous")
        hardiness = request.form.get("hardiness")

        
        url = f"https://perenual.com/api/species-list?key=sk-GJ5U65676390d6bb73193&watering={water}&sunlight={sunlight}&indoor={indoor}&hardiness={hardiness}"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            filtre_list = data.get('data', [])
            if filtre_list:
                id_list = [filtre.get('id') for filtre in filtre_list[:5]]
                data_details = get_details(id_list)
                if data_details:
                    return render_template("resultsFiltre.html", data_details=data_details)
                else:
                    return apology("plants doesn't exist for your choices")
            else:
                return apology("Plants don't exist for your choices")
        else:
            return apology("plants doesn't exist for your choices")
    else:
        return render_template("filtre.html")


def get_details(id_list):
    data_details = []
    for id in id_list:
        url = f"https://perenual.com/api/species-details/{id}?key=sk-GJ5U65676390d6bb73193"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            data_details.append(data)
    return data_details



@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":
        species = request.form.get("species")

        url = f"https://perenual.com/api/species-list?key=sk-qcer657253529e9463387&q={species}"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data_species_list = response.json()
            species_list = data_species_list.get('data', [])
            print(species_list)
            if species_list:
                # Extract all the IDs from the list
                id_list = [species.get('id') for species in species_list[:5]]

                # Call the function to get species details for each ID
                data_species_details = get_species_details(id_list)

                if data_species_details:
                    print(data_species_details)
                    return render_template("results.html", data=data_species_details)
                else:
                    return apology("Error fetching species details")
            else:
                return apology("Plants don't exist for your choices")
        else:
            return apology("Error fetching data from the API")

    else:
        return render_template("search.html")


def get_species_details(id_list):
    # Create an empty list to store details for each ID
    details_list = []

    for common_id in id_list:
        url_species_details = f"https://perenual.com/api/species/details/{common_id}?key=sk-qcer657253529e9463387"
        payload_details = {}
        headers_details = {}
        response_species_details = requests.request("GET", url_species_details, headers=headers_details, data=payload_details)

        if response_species_details.status_code == 200:
            data_species_details = response_species_details.json()
            details_list.append(data_species_details)
        else:
            # Handle the case where details for a specific ID couldn't be fetched
            details_list.append(None)

    return details_list

@app.route("/details/<int:plant_id>", methods=["GET"])
@login_required
def details(plant_id):
    url = f"https://perenual.com/api/species/details/{plant_id}?key=sk-GJ5U65676390d6bb73193"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        data = response.json()
        disease = search_disease()
        return render_template("details.html", data = data, disease = disease) 
    else:
        return apology("Error fetching data from the API")
    


def search_disease():
    url = "https://perenual.com/api/pest-disease-list?key=sk-qcer657253529e9463387&id=1"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        data = response.json()
        disease = data.get('data', [])
        return disease
    else:
        return apology("Error fetching data from the API")

@app.route("/save", methods=["POST"])
@login_required
def save():
    # User reached route via POST
    if request.method == "POST":
        try:
            plant_id = request.json.get("id")  
            plants_number = request.json.get("plants_number")
            # get user id 
            user_id = session["user_id"]

            # Check if the user has already liked the plant
            if not user_liked_plants(user_id, plant_id):
                # Insert liked plant id into the table of liked plants
                db.execute("INSERT INTO liked_plants (user_id, plant_id,plants_number) VALUES (?, ?,?)", user_id, plant_id,plants_number)
                database_insert(user_id,plant_id)
                # Set liked to True
                liked = True  
                message = "plant liked successfully"
            else:
                # Delete unliked plant id from the table of liked games
                if plants_number == 0 :
                    db.execute("DELETE FROM liked_plants WHERE user_id = ? AND plant_id = ?", user_id, plant_id)
                    db.execute("DELETE from created_plants WHERE user_id = ? AND plant_id = ?", user_id, plant_id) 
                else:
                    db.execute("UPDATE liked_plants SET plants_number = ? WHERE user_id = ? AND plant_id = ?", plants_number, user_id, plant_id)
                # Set liked to False
                liked = False  
                message = "plant unliked successfully"
            # Return a JSON response to indicate success and the updated liked status
            response_data = {
                "message": message,
                "liked": liked
            }
            return jsonify(response_data), 200
        except :
            return jsonify({"error": "Database error"}), 500
        

def user_liked_plants(user_id, plant_id):
    # counts the number of liked plants id in the liked table
    conn = sqlite3.connect('guardian.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM liked WHERE user_id = ? AND game_id = ?", (user_id, plant_id))
    result = cursor.fetchone()
    conn.close()
    return result[0] > 0

def database_insert(user_id,plant_id,plants_number):
    # Fetch plant details from the API
    api_url = f"https://perenual.com/api/species/details/?key=sk-GJ5U65676390d6bb73193"
    api_response = requests.get(api_url)

    if api_response.status_code == 200:
        api_data = api_response.json()

        # Extract relevant information from the API response
        common_name = api_data.get('common_name', '')
        scientific_name = api_data.get('scientific_name', '')
        watering  = api_data.get('depth_water_requirement ', '')
        sunlight   = api_data.get('sunlight ', '')
        default_image  = api_data.get('default_image ', '')
        watering_period  = api_data.get('watering_period', '')
        # Save the information to the SQLite database
        conn = sqlite3.connect('guardian.db')
        cursor = conn.cursor()

        # Insert the plant details into the PlantDetails table
        cursor.execute("INSERT INTO created_garden (user_id,plant_id, common_name, scientific_name,watering,watering_period,sunlight,default_image,plant_number) VALUES (?, ?, ?,?,?,?,?,?,?)",
                       (user_id,plant_id, common_name, scientific_name,watering,watering_period,sunlight,default_image,plants_number))
        
        conn.commit()
        conn.close()
    else:
        # Handle the case when the API request fails
        return apology(f"Failed to fetch details for plant_id {plant_id} from the API")    




@app.route("/schedule", methods=["GET", "POST"])
@login_required
def watering():
    if request.method == "POST":
        try:
            water_quantity = float(request.form.get("water_quantity"))
            duree = int(request.form.get("duree"))
            user_id = session["user_id"]
            
            # Retrieve the user's garden or list of plants from the database
            plants = db.execute("SELECT * FROM created_garden WHERE user_id = ?", user_id)
            
            # Calculate the total water needs of the plants
            total_water_needs = sum(plant['watering'] * plant['plants_number'] for plant in plants)
            
            # Check if available water is sufficient
            if water_quantity < total_water_needs:
                return apology("Insufficient water to meet the plants' needs")
            
            # Calculate the water allocation ratio
            water_allocation_ratio = water_quantity / total_water_needs
            
            # Calculate the watering schedule and water quantities for each plant
            watering_schedule = []
            for plant in plants:
                # Calculate the water quantity for the plant based on its water requirement and allocation ratio
                water_quantity_per_plant = plant['watering'] * water_allocation_ratio
                
                # Calculate the watering schedule for the plant based on the duration
                watering_duration_per_plant = duree / len(plants)
                
                # Save the watering schedule and water quantity for the plant
                watering_schedule.append({
                    'plant_id': plant['plant_id'],
                    'water_quantity': water_quantity_per_plant,
                    'common_name': plant['common_name'],
                    'watering_duration': watering_duration_per_plant,
                    'sunlight': plant['sunlight'],
                })
                
                # Save the watering schedule and water quantity in the database
                db.execute("INSERT INTO watering_schedule (user_id, plant_id, water_quantity, watering_duration) VALUES (?, ?, ?, ?)",
                           user_id, plant['plant_id'], water_quantity_per_plant, watering_duration_per_plant)
            
            # Group the watering schedule by day
            watering_schedule_per_day = group_schedule_by_day(watering_schedule)
            
            # Display the watering schedule to the user
            return render_template("scheduleResult.html", watering_schedule_per_day=watering_schedule_per_day)
        
        except Exception as e:
            return apology(f"Error: {str(e)}")
    
    else:
        return render_template("schedule.html")

def group_schedule_by_day(watering_schedule):
    # Group the watering schedule by day
    watering_schedule_per_day = {}

    for entry in watering_schedule:
        # Calculate the date for each watering entry based on the watering duration
        watering_date = datetime.now() + timedelta(days=int(entry['watering_duration']))
        
        # Format the date as 'YYYY-MM-DD'
        watering_date_str = watering_date.strftime('%Y-%m-%d')

        # Create a dictionary for each day and append the entry
        if watering_date_str not in watering_schedule_per_day:
            watering_schedule_per_day[watering_date_str] = []

        watering_schedule_per_day[watering_date_str].append(entry)

    return watering_schedule_per_day


            
            
            

