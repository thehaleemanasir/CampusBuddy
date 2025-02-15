from flask import Blueprint, render_template

# The blueprint name is 'home'
home_bp = Blueprint('home', __name__, template_folder="../templates")

@home_bp.route('/')
def homepage():
    return render_template('homepage.html')

@home_bp.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@home_bp.route('/academic-support')
def academic_support():
    return render_template('academic_support.html')

@home_bp.route('/mental-health')
def mental_health():
    return render_template('mental_health.html')

@home_bp.route('/events')
def events():
    return render_template('events.html')

@home_bp.route('/social-networking')
def social_networking():
    return render_template('social_networking.html')

@home_bp.route('/contact')
def contact():
    return render_template('contact.html')

@home_bp.route('/about')
def about():
    return render_template('about.html')


@home_bp.route('/map')
def map_page():
    return render_template('map.html')
