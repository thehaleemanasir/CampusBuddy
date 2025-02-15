
from flask import Blueprint, render_template, request
from database import faq_collection  # Ensure you have the correct import

academic_bp = Blueprint('academic', __name__)



@academic_bp.route('/academic-support', methods=['GET'])
def academic_support():
    categories = faq_collection.distinct("category")  # Fetch unique categories
    faqs = list(faq_collection.find({}, {"_id": 0}))  # Fetch FAQs

    return render_template("academic_support.html", categories=categories, faqs=faqs)