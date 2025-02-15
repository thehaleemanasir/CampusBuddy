from database import canteen_facilities_collection

# Data to insert
canteen_facilities_data = [
    {
        "campus": "Moylish",
        "outlets": [
            {"name": "Green Room", "opening_times": {"Breakfast": "8:30am – 11am", "Lunch": "12pm – 3pm (closes 2pm Fri)", "Deli": "10:30am – 8pm (closes 2pm Fri)", "Chip Van": "3pm – 4pm"}},
            {"name": "Starbucks", "opening_times": "8am – 8:30pm (closes 4pm Fri)"},
            {"name": "Millennium Theatre Starbucks", "opening_times": {"Mon–Thu": "8:30am – 3:30pm", "Fri": "8:30am – 1pm"}},
            {"name": "Student Union Starbucks", "opening_times": {"Mon–Thu": "8am – 8:30pm", "Fri": "8am – 1pm"}},
            {"name": "Staff Canteen", "opening_times": {"Mon–Thu": "8:30am – 4pm", "Fri": "8:30am – 2pm"}}
        ],
        "hospitality_contact": "catering.midwest@tus.ie"
    },
    {
        "campus": "Thurles",
        "outlets": [
            {"name": "Thurles Main Canteen", "opening_times": {"Breakfast": "8:30am – 11am", "Lunch": "12pm – 2pm (closes 2pm Fri)" }},
            {"name": "Java Republic Coffee", "opening_times": "8:30am – 4pm (closes 2pm Fri)"}
        ],
        "hospitality_contact": "tusthurles@baxterstorey.com"
    },
    {
        "campus": "Clare Street",
        "outlets": [
            {"name": "Clare Street Main Canteen", "opening_times": {"Breakfast": "8:30am – 11:30am", "Lunch": "12pm – 2pm"}}
        ],
        "hospitality_contact": "tusclarestreet@baxterstorey.com"
    },
    {
        "campus": "Clonmel",
        "outlets": [
            {"name": "Clonmel Main Canteen", "opening_times": {"Breakfast": "9am – 12pm", "Lunch": "12pm – 2:30pm"}}
        ],
        "hospitality_contact": "tusclonmel@baxterstorey.com"
    },
    {
        "campus": "General",
        "outlets": [],
        "hospitality_contact": "catering.midwest@tus.ie (for outside service hours or term time)"
    }
]

# Insert data into MongoDB
canteen_facilities_collection.insert_many(canteen_facilities_data)

# Confirm insertion
print("✅ TUS Campus Catering Facilities data inserted into MongoDB successfully!")
