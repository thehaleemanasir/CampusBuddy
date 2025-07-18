
from flask import Blueprint, render_template
from database import faq_collection

academic_bp = Blueprint('academic', __name__)



@academic_bp.route('/academic-support', methods=['GET'])
def academic_support():
    categories = faq_collection.distinct("category")
    faqs = list(faq_collection.find({}, {"_id": 0}))

    return render_template("academic_support.html", categories=categories, faqs=faqs)