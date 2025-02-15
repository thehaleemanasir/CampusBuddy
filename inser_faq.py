from database import faq_collection

# Fetch all distinct categories
categories = faq_collection.distinct("category")

# Fetch all FAQ entries
faqs = list(faq_collection.find({}, {"_id": 0}))

print("✅ Categories Found:", categories)
print("✅ FAQs Found:", faqs)

if not categories:
    print("⚠ No categories found! Your database might be empty.")
if not faqs:
    print("⚠ No FAQs found! Your database might be empty.")
