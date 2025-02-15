from flask import Blueprint, render_template, request, redirect
from database import campuses_collection, societies_collection, joined_collection

# The blueprint name must be 'society'
society_bp = Blueprint('society', __name__, template_folder="../templates")

@society_bp.route('/society_club')
def society_club():
    campuses = list(campuses_collection.find({}, {"_id": 0, "name": 1}))
    joined_societies = list(joined_collection.find({}, {"_id": 0}))

    return render_template('society_club.html', campuses=campuses, joined_societies=joined_societies)

@society_bp.route('/societies_list', methods=['GET'])
def societies_list():
    campuses = list(campuses_collection.find({}, {"_id": 0, "name": 1}))

    # Get campus filter from the query parameter
    campus_filter = request.args.get('campus', '')

    # Fetch societies based on the selected campus
    if campus_filter:
        societies = list(societies_collection.find({"campus": campus_filter},
                                                   {"_id": 0, "name": 1, "category": 1, "description": 1}))
    else:
        societies = list(societies_collection.find({}, {"_id": 0, "name": 1, "category": 1, "description": 1}))

    return render_template(
        'societies_list.html',  # Ensure this template file exists
        campuses=campuses,
        societies=societies,
        selected_campus=campus_filter
    )


@society_bp.route('/join_society', methods=['GET', 'POST'])
def join_society():
    if request.method == 'POST':
        try:
            campus = request.form.get('campus')
            society = request.form.get('society')
            contact_by_email = 'contactByEmail' in request.form

            if not campus or not society:
                return "Campus and society selection are required.", 400

            joined_collection.insert_one({
                'campus': campus,
                'society': society,
                'contact_by_email': contact_by_email
            })

            return redirect('/society_club')
        except Exception as e:
            print("Error during form submission:", str(e))
            return "An error occurred. Check server logs.", 500

    campus_filter = request.args.get('campus', '')
    campuses = list(campuses_collection.find({}, {"_id": 0, "name": 1}))
    societies = []

    if campus_filter:
        societies = list(societies_collection.find({"campus": campus_filter}, {"_id": 0, "name": 1}))

    return render_template(
        'join_society.html',
        campuses=campuses,
        societies=societies,
        selected_campus=campus_filter
    )
