from web3 import Web3,HTTPProvider
from flask import Flask, jsonify, render_template, redirect, request, session, url_for
from functools import wraps
import json
from werkzeug.utils import secure_filename
import os
import hashlib
from datetime import datetime
from threading import Thread
from gas_monitor import monitor_gas_levels

app=Flask(__name__)
app.secret_key="M@keskilled0"

userManagementArtifactPath="../build/contracts/userManagement.json"
blockchainServer="http://127.0.0.1:7545"

def connectWithContract(wallet,artifact=userManagementArtifactPath):
    web3=Web3(HTTPProvider(blockchainServer)) # it is connecting with server
    print('Connected with Blockchain Server')

    if (wallet==0):
        web3.eth.defaultAccount=web3.eth.accounts[0]
    else:
        web3.eth.defaultAccount=wallet
    print('Wallet Selected')

    with open(artifact) as f:
        artifact_json=json.load(f)
        contract_abi=artifact_json['abi']
        contract_address=artifact_json['networks']['5777']['address']
    
    contract=web3.eth.contract(abi=contract_abi,address=contract_address)
    print('Contract Selected')
    return contract,web3

@app.route('/')
def homePage():
    return render_template('index.html')

@app.route('/login')
def loginPage():
    return render_template('login.html')

@app.route('/signup')
def signupPage():
    return render_template('signup.html')

@app.route('/register',methods=['POST']) # page (1 Route), page (2 Route)
def register():
    wallet=request.form['address']
    username=request.form['username']
    email=request.form['email']
    password=request.form['password']
    confirmPassword=request.form['confirmPassword']
    
    if(password!=confirmPassword):
        return render_template('signup.html',message='passwords not matched, try again')
    
    contract,web3=connectWithContract(wallet) # UserManagement
    try:
        tx_hash=contract.functions.userSignUp(wallet,username,password,email).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)
        print('Transaction Successful')
        return render_template('signup.html',message='Signup Successful')
    except:
        return render_template('signup.html',message='there is problem in creating account')

@app.route('/loginForm', methods=['POST'])
def loginForm():
    username = request.form['username']
    password = request.form['password']

    contract, web3 = connectWithContract(0)
    try:
        result = contract.functions.userLogin(username, password).call()
        if result:
            response = contract.functions.viewUserByUsername(username).call()
            # Store user info in session
            session['username'] = username
            session['wallet'] = response[0]  # Assuming wallet address is first element
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', message='Invalid credentials')
    except Exception as e:
        return render_template('login.html', message='Invalid details of username')    

# Store active cooking activities
ACTIVE_ACTIVITIES = []

# Predefined cooking information
COOKING_GUIDES = {
    'pizza': {
        'name': 'Pizza',
        'recommended_temp': 220,
        'cooking_time': 15,
        'instructions': [
            'Preheat oven to 220°C',
            'Place pizza on middle rack',
            'Cook for 12-15 minutes until cheese is golden',
            'Check crust is crispy and golden brown'
        ],
        'tips': 'For extra crispy crust, preheat pizza stone if available'
    },
    'chicken_curry': {
        'name': 'Chicken Curry',
        'recommended_temp': 180,
        'cooking_time': 45,
        'instructions': [
            'Heat oil in large pan',
            'Cook onions until golden',
            'Add spices and cook for 2 minutes',
            'Add chicken and simmer for 40-45 minutes'
        ],
        'tips': 'Marinate chicken beforehand for better flavor'
    },
    'chocolate_cake': {
        'name': 'Chocolate Cake',
        'recommended_temp': 175,
        'cooking_time': 30,
        'instructions': [
            'Preheat oven to 175°C',
            'Mix wet and dry ingredients separately',
            'Combine mixtures and pour into pan',
            'Bake for 30-35 minutes'
        ],
        'tips': 'Insert toothpick in center to check if done'
    },
    'grilled_salmon': {
        'name': 'Grilled Salmon',
        'recommended_temp': 200,
        'cooking_time': 20,
        'instructions': [
            'Preheat grill to high heat',
            'Season salmon with herbs and lemon',
            'Grill for 4-6 minutes per side',
            'Check internal temperature reaches 63°C'
        ],
        'tips': 'Leave skin on while grilling to retain moisture'
    }
}

@app.route('/get_cooking_guide/<recipe_id>')
def get_cooking_guide(recipe_id):
    if recipe_id in COOKING_GUIDES:
        return jsonify(COOKING_GUIDES[recipe_id])
    return jsonify({'error': 'Recipe not found'}), 404

@app.route('/add_activity', methods=['POST'])
def add_activity():
    activity = {
        'dish_name': request.form.get('dish_name'),
        'cooking_time': request.form.get('cooking_time'),
        'temperature': request.form.get('temperature'),
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'status': 'In Progress',
        'current_step': 0
    }
    
    recipe_type = request.form.get('recipe_type')
    if recipe_type in COOKING_GUIDES:
        activity['instructions'] = COOKING_GUIDES[recipe_type]['instructions']
        activity['tips'] = COOKING_GUIDES[recipe_type]['tips']
    
    ACTIVE_ACTIVITIES.append(activity)
    return jsonify({'status': 'success'})

@app.route('/update_step/<int:activity_index>/<int:step>')
def update_step(activity_index, step):
    if 0 <= activity_index < len(ACTIVE_ACTIVITIES):
        ACTIVE_ACTIVITIES[activity_index]['current_step'] = step
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Activity not found'}), 404

@app.route('/complete_activity/<int:index>')
def complete_activity(index):
    if 0 <= index < len(ACTIVE_ACTIVITIES):
        ACTIVE_ACTIVITIES[index]['status'] = 'Completed'
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Activity not found'}), 404

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('homePage'))

# Add session check for protected routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('loginPage'))
        return f(*args, **kwargs)
    return decorated_function

# Apply login_required to protected routes
@app.route('/dashboard')
@login_required
def dashboard():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template('dashboard.html', 
                         current_time=current_time,
                         cooking_guides=COOKING_GUIDES)

@app.route('/cooking_activities')
@login_required
def cooking_activities():
    return render_template('cooking_activities.html',
                         cooking_guides=COOKING_GUIDES,
                         activities=ACTIVE_ACTIVITIES)

if __name__ == "__main__":
    # Start the monitoring in a separate thread
    monitor_thread = Thread(target=monitor_gas_levels, daemon=True)
    monitor_thread.start()
    
    # Start Flask app
    app.run(debug=True)
