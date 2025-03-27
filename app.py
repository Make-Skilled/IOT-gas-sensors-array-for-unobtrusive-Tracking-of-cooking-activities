from flask import Flask, render_template, jsonify, request
from datetime import datetime

app = Flask(__name__)

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

@app.route('/')
def index():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template('index.html', 
                         current_time=current_time,
                         cooking_guides=COOKING_GUIDES)

@app.route('/cooking_activities')
def cooking_activities():
    return render_template('cooking_activities.html',
                         cooking_guides=COOKING_GUIDES,
                         activities=ACTIVE_ACTIVITIES)

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

if __name__ == '__main__':
    app.run(debug=True)


