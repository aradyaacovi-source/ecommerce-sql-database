"""
Fake data generator for Zales jewelry e-commerce database.
Generates tables in hierarchical order to preserve referential integrity.
Exports each table to a separate CSV file.
"""

import random
import string

import pandas as pd
from faker import Faker

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
data_amount = {
    # Level 1 – main entities (200–500 rows)
    "customer": 350,
    "jewelry": 300,
    "component": 250,
    # Level 2 – depend on Level 1 (200–500 rows)
    "credit_card": 450,
    "search": 400,
    "jewelry_variant": 400,
    # Level 3 – depend on Level 2 & 1 (1000–2000 rows)
    "order_table": 1500,
    "search_returns": 1500,
    "builds_from": 1200,
    # Level 4 – depend on Level 3 (1000–2000 rows)
    "include": 1800,
}

fake_en = Faker("en_US")

# ---------------------------------------------------------------------------
# Zales realistic data
# ---------------------------------------------------------------------------
Zales_Categories = ["Engagement", "Rings", "Necklaces", "Earrings", "Bracelets", "Watches"]
Zales_Collections = [
    "Vera Wang Bridal",
    "Enchanted Disney",
    "Zales Essentials",
    "Modern Muse",
    "Ethereal Romance",
    "Iconic Classics",
    "Bulova",
]
Zales_Styles = ["Solitaire", "Halo", "Three Stone", "Tennis", "Studs", "Drop", "Bangle", "Pendant", "Pavé"]
Zales_Stones = [
    "Natural Diamond",
    "Lab-Grown Diamond",
    "Sapphire",
    "Ruby",
    "Emerald",
    "Pearl",
    "Amethyst",
]
Zales_Materials = ["Yellow Gold 14K", "White Gold 18K", "Rose Gold 14K", "Platinum", "Sterling Silver"]
Zales_Sizes = ["Size 5", "Size 6", "Size 7", "Size 8", "Size 9", "16 Inch", "18 Inch", "20 Inch"]
Zales_Colors = ["White", "Yellow", "Rose", "Silver", "Clear", "Blue", "Green", "Red"]

EMAIL_PROVIDERS = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"]

realistic_searches = [
    "diamond ring",
    "gold necklace",
    "engagement rings",
    "tennis bracelet",
    "stud earrings",
    "Vera Wang",
    "Disney jewelry",
    "pearl necklace",
    "sapphire ring",
    "white gold band",
    "mens watches",
    "hoop earrings",
    "promise ring",
    "rose gold bracelet",
    "emerald pendant",
    "solitaire ring",
    "anniversary band",
    "birthstone necklace",
    "14k gold chain",
    "lab grown diamond",
    "silver rings",
    "heart necklace",
    "drop earrings",
    "bridal set",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def sequential_ids(count: int) -> list[int]:
    """Generate sequential positive integer IDs starting from 1."""
    return list(range(1, count + 1))


def unique_cc_number(existing: set[str]) -> str:
    """Generate a unique 16-digit credit card number string."""
    while True:
        cc_number = "".join(random.choices(string.digits, k=16))
        if cc_number not in existing:
            existing.add(cc_number)
            return cc_number


def zales_product_name(category: str) -> str:
    """Build a realistic Zales product name from hardcoded catalog lists."""
    return (
        f"{random.choice(Zales_Collections)} "
        f"{random.choice(Zales_Stones)} "
        f"{random.choice(Zales_Styles)} "
        f"{category}"
    )


def us_phone_number() -> str:
    """Return a strict US phone number: +1 followed by exactly 10 digits (12 chars total)."""
    return "+1" + "".join(random.choices(string.digits, k=10))


def customer_email(first_name: str, last_name: str, existing_emails: set[str]) -> str:
    """Build a unique lowercase email from first name, last name, and a random number."""
    first_clean = first_name.lower().replace(" ", "")
    last_clean = last_name.lower().replace(" ", "")

    while True:
        number = random.randint(10, 9999)
        provider = random.choice(EMAIL_PROVIDERS)
        email = f"{first_clean}.{last_clean}{number}@{provider}"
        if email not in existing_emails:
            existing_emails.add(email)
            return email


def random_expiry_date() -> str:
    """Return expiry date as MM/YY string."""
    future = fake_en.date_between(start_date="+1y", end_date="+5y")
    return future.strftime("%m/%y")


def random_order_date() -> str:
    """Return order date as YYYY-MM-DD string."""
    return fake_en.date_between(start_date="-2y", end_date="today").isoformat()


def random_search_datetime() -> str:
    """Return search datetime as YYYY-MM-DD HH:MM:SS string."""
    dt = fake_en.date_time_between(start_date="-1y", end_date="now")
    return dt.strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------------------
# LEVEL 1: Independent Parent Tables
# ---------------------------------------------------------------------------

# 1. CUSTOMER
print("Generating CUSTOMER...")
customer_emails: list[str] = []
customer_data = {
    "Email": [],
    "Password": [],
    "Name_Last": [],
    "Name_First": [],
    "Phone": [],
}

existing_customer_emails: set[str] = set()

for _ in range(data_amount["customer"]):
    name_first = fake_en.first_name()
    name_last = fake_en.last_name()
    email = customer_email(name_first, name_last, existing_customer_emails)
    customer_emails.append(email)
    customer_data["Email"].append(email)
    customer_data["Password"].append(fake_en.password(length=12))
    customer_data["Name_Last"].append(name_last)
    customer_data["Name_First"].append(name_first)
    customer_data["Phone"].append(us_phone_number())

df_customer = pd.DataFrame(customer_data)

# 2. JEWELRY
print("Generating JEWELRY...")
jewelry_ids = sequential_ids(data_amount["jewelry"])
jewelry_categories = [random.choice(Zales_Categories) for _ in jewelry_ids]

jewelry_data = {
    "Jewelry": jewelry_ids,
    "Product_Name": [zales_product_name(category) for category in jewelry_categories],
    "Category": jewelry_categories,
}
df_jewelry = pd.DataFrame(jewelry_data)

# 3. COMPONENT
print("Generating COMPONENT...")
component_ids = sequential_ids(data_amount["component"])

component_data = {
    "Component": component_ids,
    "Material": [random.choice(Zales_Materials) for _ in component_ids],
    "Price_Addition": [random.randint(50, 2000) for _ in component_ids],
}
df_component = pd.DataFrame(component_data)

# ---------------------------------------------------------------------------
# LEVEL 2: Tables depending on Level 1
# ---------------------------------------------------------------------------

# 4. CREDIT_CARD
print("Generating CREDIT_CARD...")
cc_numbers: list[str] = []
existing_cc_numbers: set[str] = set()
credit_card_data = {
    "CCNumber": [],
    "Owner_ID": [],
    "Expiry_Date": [],
    "CVV": [],
}

for _ in range(data_amount["credit_card"]):
    cc_number = unique_cc_number(existing_cc_numbers)
    cc_numbers.append(cc_number)
    credit_card_data["CCNumber"].append(cc_number)
    credit_card_data["Owner_ID"].append(random.choice(customer_emails))
    credit_card_data["Expiry_Date"].append(random_expiry_date())
    credit_card_data["CVV"].append(str(random.randint(100, 999)))

df_credit_card = pd.DataFrame(credit_card_data)

customer_cards: dict[str, list[str]] = {email: [] for email in customer_emails}
for cc_number, owner in zip(credit_card_data["CCNumber"], credit_card_data["Owner_ID"]):
    customer_cards[owner].append(cc_number)

# 5. SEARCH
print("Generating SEARCH...")
search_ids = sequential_ids(data_amount["search"])
search_filters = ["Price", "Material", "Brand", "None"]
sort_methods = ["Price: Low to High", "Price: High to Low", "Newest", "Best Sellers"]

search_data = {
    "Search_ID": search_ids,
    "Search_DT": [random_search_datetime() for _ in search_ids],
    "Search_Text": [random.choice(realistic_searches) for _ in search_ids],
    "Search_Filter": [random.choice(search_filters) for _ in search_ids],
    "Sort_Method": [random.choice(sort_methods) for _ in search_ids],
    "Email": [random.choice(customer_emails) for _ in search_ids],
}
df_search = pd.DataFrame(search_data)

# 6. JEWELRY_VARIANT
print("Generating JEWELRY_VARIANT...")
variant_ids = sequential_ids(data_amount["jewelry_variant"])
variant_types = ["Default", "Customized"]

jewelry_variant_data = {
    "Jewelry_Variant": variant_ids,
    "Jewelry": [random.choice(jewelry_ids) for _ in variant_ids],
    "Variant_Type": [random.choice(variant_types) for _ in variant_ids],
    "Size": [random.choice(Zales_Sizes) for _ in variant_ids],
    "Color": [random.choice(Zales_Colors) for _ in variant_ids],
}
df_jewelry_variant = pd.DataFrame(jewelry_variant_data)

# ---------------------------------------------------------------------------
# LEVEL 3: Tables depending on Level 2 & 1
# ---------------------------------------------------------------------------

# 7. ORDER_TABLE
print("Generating ORDER_TABLE...")
order_ids = sequential_ids(data_amount["order_table"])
delivery_methods = ["Ship to Home", "Pick Up In-Store", "Same Day Delivery"]

order_data = {
    "Order_ID": order_ids,
    "Date": [random_order_date() for _ in order_ids],
    "Address_State": [fake_en.state() for _ in order_ids],
    "Address_City": [fake_en.city() for _ in order_ids],
    "Address_Street": [fake_en.street_name() for _ in order_ids],
    "Address_HouseNum": [str(random.randint(1, 200)) for _ in order_ids],
    "Address_Zip": [fake_en.zipcode() for _ in order_ids],
    "Delivery_Method": [random.choice(delivery_methods) for _ in order_ids],
    "Email": [],
    "CCNumber": [],
}

for _ in order_ids:
    email = random.choice(customer_emails)
    order_data["Email"].append(email)
    owner_cards = customer_cards[email]
    if owner_cards:
        order_data["CCNumber"].append(random.choice(owner_cards))
    else:
        order_data["CCNumber"].append(random.choice(cc_numbers))

df_order_table = pd.DataFrame(order_data)

# 8. SEARCH_RETURNS
print("Generating SEARCH_RETURNS...")
search_returns_pairs: set[tuple[int, int]] = set()
search_returns_data = {
    "Search_ID": [],
    "Jewelry": [],
    "Result_Rank": [],
    "Clicked": [],
}

while len(search_returns_pairs) < data_amount["search_returns"]:
    search_id = random.choice(search_ids)
    jewelry_id = random.choice(jewelry_ids)
    pair = (search_id, jewelry_id)
    if pair not in search_returns_pairs:
        search_returns_pairs.add(pair)
        search_returns_data["Search_ID"].append(search_id)
        search_returns_data["Jewelry"].append(jewelry_id)
        search_returns_data["Result_Rank"].append(random.randint(1, 20))
        search_returns_data["Clicked"].append(random.randint(0, 1))

df_search_returns = pd.DataFrame(search_returns_data)

# 9. BUILDS_FROM
print("Generating BUILDS_FROM...")
builds_from_pairs: set[tuple[int, int]] = set()
builds_from_data = {
    "Jewelry_Variant": [],
    "Component": [],
}

while len(builds_from_pairs) < data_amount["builds_from"]:
    variant_id = random.choice(variant_ids)
    component_id = random.choice(component_ids)
    pair = (variant_id, component_id)
    if pair not in builds_from_pairs:
        builds_from_pairs.add(pair)
        builds_from_data["Jewelry_Variant"].append(variant_id)
        builds_from_data["Component"].append(component_id)

df_builds_from = pd.DataFrame(builds_from_data)

# ---------------------------------------------------------------------------
# LEVEL 4: Tables depending on Level 3
# ---------------------------------------------------------------------------

# 10. INCLUDE
print("Generating INCLUDE...")
include_pairs: set[tuple[int, int]] = set()
include_data = {
    "Order_ID": [],
    "Jewelry_Variant": [],
    "Quantity": [],
}

while len(include_pairs) < data_amount["include"]:
    order_id = random.choice(order_ids)
    variant_id = random.choice(variant_ids)
    pair = (order_id, variant_id)
    if pair not in include_pairs:
        include_pairs.add(pair)
        include_data["Order_ID"].append(order_id)
        include_data["Jewelry_Variant"].append(variant_id)
        include_data["Quantity"].append(random.randint(1, 3))

df_include = pd.DataFrame(include_data)

# ---------------------------------------------------------------------------
# Export to CSV
# ---------------------------------------------------------------------------
print("Exporting CSV files...")

df_customer.to_csv("CUSTOMER.csv", index=False, encoding="utf-8-sig")
df_jewelry.to_csv("JEWELRY.csv", index=False, encoding="utf-8-sig")
df_component.to_csv("COMPONENT.csv", index=False, encoding="utf-8-sig")
df_credit_card.to_csv("CREDIT_CARD.csv", index=False, encoding="utf-8-sig")
df_search.to_csv("SEARCH.csv", index=False, encoding="utf-8-sig")
df_jewelry_variant.to_csv("JEWELRY_VARIANT.csv", index=False, encoding="utf-8-sig")
df_order_table.to_csv("ORDER_TABLE.csv", index=False, encoding="utf-8-sig")
df_search_returns.to_csv("SEARCH_RETURNS.csv", index=False, encoding="utf-8-sig")
df_builds_from.to_csv("BUILDS_FROM.csv", index=False, encoding="utf-8-sig")
df_include.to_csv("INCLUDE.csv", index=False, encoding="utf-8-sig")

print("Done!")
print(f"  CUSTOMER:         {len(df_customer)} rows")
print(f"  JEWELRY:          {len(df_jewelry)} rows")
print(f"  COMPONENT:        {len(df_component)} rows")
print(f"  CREDIT_CARD:      {len(df_credit_card)} rows")
print(f"  SEARCH:           {len(df_search)} rows")
print(f"  JEWELRY_VARIANT:  {len(df_jewelry_variant)} rows")
print(f"  ORDER_TABLE:      {len(df_order_table)} rows")
print(f"  SEARCH_RETURNS:   {len(df_search_returns)} rows")
print(f"  BUILDS_FROM:      {len(df_builds_from)} rows")
print(f"  INCLUDE:          {len(df_include)} rows")
