from database import canteen_menu_collection

sample_menu = [
    {"item_name": "Chicken Wrap", "price": 5.50, "category": "Lunch", "dietary": "Halal", "availability": True},
    {"item_name": "Vegetarian Pasta", "price": 4.75, "category": "Lunch", "dietary": "Vegetarian", "availability": True},
    {"item_name": "Vegan Salad", "price": 3.99, "category": "Lunch", "dietary": "Vegan", "availability": True},
    {"item_name": "Beef Burger", "price": 6.00, "category": "Lunch", "dietary": "Non-Veg", "availability": True},
    {"item_name": "Latte", "price": 2.50, "category": "Drinks", "dietary": "Vegetarian", "availability": True}
]

canteen_menu_collection.insert_many(sample_menu)
print("✅ Canteen Menu Data Inserted Successfully!")
