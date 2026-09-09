# Imports
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker


# Config
random.seed(42)
fake = Faker()
Faker.seed(42)

N_CUSTOMERS = 1000
N_PRODUCTS = 100
N_SALES = 15000
N_CAMPAIGNS = 200

START_DATE = datetime(2022, 1, 1)
END_DATE = datetime(2025, 12, 31)

OUTPUT_DIR = Path("data/generated")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Helpers
def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


# Products
categories = {
    "Clothing": [
        "T-shirt", "Shirt", "Jeans", "Hoodie", "Sweater",
        "Dress", "Skirt", "Shorts", "Pants", "Blouse"
    ],
    "Footwear": [
        "Sneakers", "Boots", "Sandals", "Running Shoes",
        "Casual Shoes"
    ],
    "Outerwear": [
        "Jacket", "Coat", "Blazer", "Raincoat", "Windbreaker"
    ],
    "Accessories": [
        "Hat", "Cap", "Belt", "Scarf", "Backpack",
        "Handbag", "Wallet", "Sunglasses"
    ]
}

brands = [
    "Brand A", "Brand B", "Brand C", "Brand D", "Brand E",
    "Brand F", "Brand G", "Brand H", "Brand I", "Brand J"
]

products_list = []

product_id = 101

for i in range(N_PRODUCTS):
    category = random.choice(list(categories.keys()))
    product_name = random.choice(categories[category])

    price = round(random.uniform(10, 250), 2)

    products_list.append({
        "Product_ID": product_id,
        "Product_Name": f"{product_name} {i + 1}",
        "Category": category,
        "Price": price,
        "Brand": random.choice(brands)
    })

    product_id += 1

products = pd.DataFrame(products_list)


# Customers
locations = [
    "New York", "Los Angeles", "Chicago", "Houston",
    "Phoenix", "Philadelphia", "San Antonio", "San Diego",
    "Dallas", "San Jose", "Austin", "Jacksonville"
]

genders = ["Male", "Female"]

customers_list = []

customer_id = 2001

for _ in range(N_CUSTOMERS):
    join_date = random_date(
        datetime(2022, 1, 1),
        datetime(2024, 12, 31)
    )

    customers_list.append({
        "Customer_ID": customer_id,
        "Name": fake.name(),
        "Age": random.randint(18, 70),
        "Gender": random.choice(genders),
        "Location": random.choice(locations),
        "Join_Date": join_date,
        "Total_Spent": 0.0
    })

    customer_id += 1

customers = pd.DataFrame(customers_list)


# Sales
channels = ["Online", "In-Store"]

sales_list = []

for sale_id in range(1, N_SALES + 1):
    customer = customers.sample(1).iloc[0]

    sale_date = random_date(
        customer["Join_Date"],
        END_DATE
    )

    product = products.sample(1).iloc[0]

    quantity = random.randint(1, 5)

    sales_list.append({
        "Sale_ID": sale_id,
        "Product_ID": product["Product_ID"],
        "Customer_ID": customer["Customer_ID"],
        "Date": sale_date,
        "Quantity": quantity,
        "Sale_Price": product["Price"],
        "Channel": random.choice(channels)
    })

sales = pd.DataFrame(sales_list)


# Total spent
sales["Revenue"] = (
    sales["Quantity"] * sales["Sale_Price"]
)

total_spent = (
    sales.groupby("Customer_ID")["Revenue"]
    .sum()
    .reset_index()
)

total_spent.columns = [
    "Customer_ID",
    "Total_Spent"
]

customers = customers.drop(
    columns="Total_Spent"
).merge(
    total_spent,
    on="Customer_ID",
    how="left"
)

customers["Total_Spent"] = (
    customers["Total_Spent"]
    .fillna(0)
    .round(2)
)


# Marketing
marketing_channels = [
    "Online",
    "In-Store",
    "Social",
    "Email",
    "TV"
]

marketing_list = []

for campaign_id in range(1, N_CAMPAIGNS + 1):
    start_date = random_date(
        START_DATE,
        END_DATE - timedelta(days=30)
    )

    end_date = start_date + timedelta(
        days=random.randint(7, 30)
    )

    budget = round(
        random.uniform(500, 10000),
        2
    )

    impressions = random.randint(
        10000,
        500000
    )

    ctr = random.uniform(
        0.01,
        0.10
    )

    clicks = int(
        impressions * ctr
    )

    conversion_rate = random.uniform(
        0.02,
        0.20
    )

    conversions = int(
        clicks * conversion_rate
    )

    marketing_list.append({
        "Campaign_ID": campaign_id,
        "Channel": random.choice(
            marketing_channels
        ),
        "Start_Date": start_date,
        "End_Date": end_date,
        "Budget": budget,
        "Impressions": impressions,
        "Clicks": clicks,
        "Conversions": conversions
    })

marketing = pd.DataFrame(marketing_list)


# Remove Revenue
sales = sales.drop(
    columns="Revenue"
)


# Format dates
customers["Join_Date"] = (
    customers["Join_Date"]
    .dt.strftime("%Y-%m-%d")
)

sales["Date"] = (
    sales["Date"]
    .dt.strftime("%Y-%m-%d")
)

marketing["Start_Date"] = (
    marketing["Start_Date"]
    .dt.strftime("%Y-%m-%d")
)

marketing["End_Date"] = (
    marketing["End_Date"]
    .dt.strftime("%Y-%m-%d")
)


# Save
customers.to_csv(
    OUTPUT_DIR / "customers_data.csv",
    index=False
)

products.to_csv(
    OUTPUT_DIR / "products_data.csv",
    index=False
)

sales.to_csv(
    OUTPUT_DIR / "sales_data.csv",
    index=False
)

marketing.to_csv(
    OUTPUT_DIR / "marketing_data.csv",
    index=False
)


# Summary
print("Generation completed")
print("Customers:", customers.shape)
print("Products:", products.shape)
print("Sales:", sales.shape)
print("Marketing:", marketing.shape)