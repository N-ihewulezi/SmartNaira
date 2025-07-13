def categorize_expense(description, entry_type):
    desc = description.lower()
    if entry_type == "Expense":
        if any(word in desc for word in ["fuel", "transport", "uber", "bus"]):
            return "Transportation"
        elif any(word in desc for word in ["rent", "house", "apartment"]):
            return "Housing & Rent"
        elif any(word in desc for word in ["data", "airtime", "electricity", "power"]):
            return "Utilities"
        elif any(word in desc for word in ["food", "rice", "bread", "meat"]):
            return "Food & Groceries"
        elif any(word in desc for word in ["school", "fees", "lesson"]):
            return "Childcare & School Costs"
        elif any(word in desc for word in ["clothes", "shoes", "salon"]):
            return "Clothing & Upkeep"
        elif any(word in desc for word in ["hospital", "drugs", "medication", "clinic"]):
            return "Health & Medication"
        elif any(word in desc for word in ["movie", "cinema", "netflix", "fun"]):
            return "Entertainment"
        elif any(word in desc for word in ["travel", "flight", "transport fare"]):
            return "Travel Expenses"
        elif any(word in desc for word in ["emergency", "repair", "urgent"]):
            return "Emergency Fund"
        else:
            return "Others"
    else:
        return "Income"
