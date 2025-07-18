from flask import Blueprint

from app.routes.decorators import roles_required
from database import canteen_facilities_collection
from bson import ObjectId

canteen_bp = Blueprint('canteen', __name__, template_folder='templates')

from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from database import canteen_menu_collection

canteen_bp = Blueprint('canteen', __name__, template_folder='templates')

@roles_required('canteen_staff', 'canteen_admin')
@canteen_bp.route('/canteen-menu', methods=['GET'])
def canteen_menu():
    campuses = list(canteen_facilities_collection.find({}, {"_id": 0, "campus": 1}))

    campus_filter = request.args.get('campus', '')
    search_query = request.args.get('search', '').lower()
    price_filter = request.args.get('price', '')

    catering_facilities = list(canteen_facilities_collection.find(
        {"campus": campus_filter} if campus_filter else {},
        {"_id": 0, "campus": 1, "outlets": 1, "hospitality_contact": 1}
    ))

    query = {"archived": False}
    if campus_filter:
        query["campus"] = campus_filter
    if search_query:
        query["$or"] = [
            {"item_name": {"$regex": search_query, "$options": "i"}},
            {"description": {"$regex": search_query, "$options": "i"}}
        ]

    sort_order = []
    if price_filter == "low":
        sort_order = [("price", 1)]
    elif price_filter == "high":
        sort_order = [("price", -1)]

    if sort_order:
        menu_items = list(canteen_menu_collection.find(query, {"_id": 0}).sort(sort_order))
    else:
        menu_items = list(canteen_menu_collection.find(query, {"_id": 0}))

    return render_template(
        'canteen_menu.html',
        campuses=campuses,
        menu_items=menu_items,
        catering_facilities=catering_facilities,
        selected_campus=campus_filter,
        search_query=search_query,
        price_filter=price_filter
    )

@roles_required('canteen_staff', 'canteen_admin')
@canteen_bp.route('/canteen-staff', methods=['GET', 'POST'])
def canteen_staff():
    if "user_id" not in session or session.get("role") not in ["canteen_staff", "canteen_admin"]:
        flash("Access Denied: Only canteen staff can modify the menu.", "danger")
        return redirect(url_for("auth.login"))

    if request.method == 'POST':
        item_name = request.form.get('item_name')
        meal_type = request.form.get('meal_type')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        dietary = request.form.get('dietary')
        campus = request.form.get('campus')
        outlet = request.form.get('outlet')

        canteen_menu_collection.insert_one({
            "item_name": item_name,
            "meal_type": meal_type,
            "description": description,
            "price": price,
            "dietary": dietary,
            "campus": campus,
            "outlet": outlet,
            "archived": False
        })
        flash('Menu item added successfully!', 'success')
        return redirect(url_for('canteen.canteen_staff'))

    campuses = list(canteen_facilities_collection.find({}, {"_id": 0, "campus": 1, "outlets.name": 1}))

    menu_items = list(canteen_menu_collection.find({}))

    return render_template('canteen_staff.html', campuses=campuses, menu_items=menu_items)

@roles_required('canteen_staff', 'canteen_admin')
@canteen_bp.route('/canteen-menu/outlet/<outlet_name>', methods=['GET'])
def outlet_details(outlet_name):
    outlet = canteen_facilities_collection.find_one({"outlets.name": outlet_name}, {"_id": 0, "outlets.$": 1, "campus": 1})

    if not outlet:
        flash("❌ Outlet not found.", "danger")
        return redirect(url_for('canteen.canteen_menu'))

    outlet_info = outlet["outlets"][0] if "outlets" in outlet and len(outlet["outlets"]) > 0 else {}

    menu_items = list(canteen_menu_collection.find(
        {"outlet": outlet_name, "campus": outlet["campus"], "archived": False},
        {"_id": 0}
    ))

    return render_template(
        'outlet_details.html',
        outlet=outlet_info,
        menu_items=menu_items
    )


@canteen_bp.route('/edit-menu-item/<item_id>', methods=['GET', 'POST'])
@roles_required('canteen_staff', 'canteen_admin')
def edit_menu_item(item_id):
    item = canteen_menu_collection.find_one({"_id": ObjectId(item_id)})
    if not item:
        flash("❌ Menu item not found!", "danger")
        return redirect(url_for('canteen.canteen_staff'))

    if request.method == 'POST':
        updated_data = {
            "item_name": request.form.get('item_name'),
            "meal_type": request.form.get('meal_type'),
            "price": float(request.form.get('price')),
            "dietary": request.form.get('dietary'),
            "campus": request.form.get('campus'),
            "outlet": request.form.get('outlet'),
            "description": request.form.get('description')
        }
        canteen_menu_collection.update_one({"_id": ObjectId(item_id)}, {"$set": updated_data})
        flash("✏️ Menu item updated successfully!", "info")
        return redirect(url_for('canteen.canteen_staff'))

    campuses = list(canteen_facilities_collection.find({}, {"_id": 0, "campus": 1, "outlets.name": 1}))

    menu_items = list(canteen_menu_collection.find({}))

    return render_template("edit_menu_item.html", item=item, campuses=campuses, menu_items=menu_items)

@canteen_bp.route('/archive-menu-item/<item_id>')
@roles_required('canteen_staff', 'canteen_admin')
def archive_menu_item(item_id):
    canteen_menu_collection.update_one({"_id": ObjectId(item_id)}, {"$set": {"archived": True}})
    flash("📂 Menu item archived!", "info")
    return redirect(url_for('canteen.canteen_staff'))

@canteen_bp.route('/unarchive-menu-item/<item_id>')
def unarchive_menu_item(item_id):
    canteen_menu_collection.update_one({"_id": ObjectId(item_id)}, {"$set": {"archived": False}})
    flash(" Menu item unarchived!", "success")
    return redirect(url_for('canteen.canteen_staff'))

@canteen_bp.route('/delete-menu-item/<item_id>')
@roles_required('canteen_staff', 'canteen_admin')
def delete_menu_item(item_id):
    canteen_menu_collection.delete_one({"_id": ObjectId(item_id)})
    flash("🗑️ Menu item deleted!", "danger")
    return redirect(url_for('canteen.canteen_staff'))