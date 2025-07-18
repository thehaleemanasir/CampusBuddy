from flask import Blueprint, render_template, request

from app.routes.decorators import roles_required
from database import campuses_collection, societies_collection

society_bp = Blueprint('society', __name__, template_folder="../templates")


@roles_required('student', 'staff')
@society_bp.route('/societies_list', methods=['GET'])
def societies_list():
    campuses = list(campuses_collection.find({}, {"_id": 0, "name": 1}))
    campus_filter = request.args.get('campus', '')
    page = int(request.args.get('page', 1))
    per_page = 9
    start = (page - 1) * per_page
    end = start + per_page

    if campus_filter:
        all_societies = list(societies_collection.find({"campus": campus_filter},
                                                       {"_id": 0, "name": 1, "category": 1, "description": 1}))
    else:
        all_societies = list(societies_collection.find({}, {"_id": 0, "name": 1, "category": 1, "description": 1}))

    paginated_societies = all_societies[start:end]
    total_societies = len(all_societies)
    total_pages = (total_societies + per_page - 1) // per_page

    return render_template(
        'societies_list.html',
        campuses=campuses,
        societies=paginated_societies,
        selected_campus=campus_filter,
        page=page,
        total_pages=total_pages
    )


