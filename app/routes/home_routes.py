from flask import Blueprint, render_template

from app.routes.decorators import roles_required

home_bp = Blueprint('home', __name__, template_folder="../templates")

@home_bp.route('/home')
@roles_required('student', 'staff', 'admin')
def homepage():
    return render_template('homepage.html')

@home_bp.route('/chatbot')
@roles_required('student', 'staff', 'admin')
def chatbot():
    return render_template('chatbot.html')

@home_bp.route('/academic-support')
@roles_required('student', 'staff', 'admin')
def academic_support():
    return render_template('academic_support.html')

@home_bp.route('/mental-health')
@roles_required('student', 'staff', 'admin')
def mental_health():
    return render_template('mental_health.html')


@home_bp.route('/calendar')
@roles_required('student', 'staff', 'admin')
def calendar():
    return render_template('calendar.html')


@home_bp.route('/about')
@roles_required('student', 'staff', 'admin')
def about():
    return render_template('about.html')




