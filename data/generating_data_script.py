"""
================================================================================
GÉNÉRATEUR DE DONNÉES SYNTHÉTIQUES - PROJET MARKETING & SEGMENTATION CLIENT
================================================================================

OBJECTIF
--------
Générer un jeu de données réaliste et cohérent pour le projet pédagogique
"Analyse & Optimisation Marketing basée sur la Segmentation Client".

FICHIERS GÉNÉRÉS (dans data/generated/)
---------------------------------------
1. customers_data.csv   → Profils clients + Churn + Total_Spent   (1000 lignes)
2. products_data.csv    → Catalogue produits                       (100 lignes)
3. sales_data.csv       → Transactions + Campaign_ID                (~15 000 lignes)
4. marketing_data.csv   → Campagnes marketing                       (200 lignes)
5. data_dictionary.md   → Dictionnaire des données auto-généré

COUVERTURE DES MODULES
----------------------
M2 (Exploration)   : 4 tables propres, types corrects
M3 (Segmentation)  : Features RFM calculables depuis sales_data
M4 (Profilage)     : Corrélation Âge ↔ Catégorie pour clusters lisibles
M5 (Campagnes)     : Sales.Campaign_ID → ROI réel par campagne
M6 (Churn/CLV)     : Colonne Churn (0/1) exportée directement
M7 (Stratégie)     : Segments + performances par canal
M8 (Dashboard)     : Toutes les tables joignables par clés

RÈGLES DE COHÉRENCE GARANTIES
-----------------------------
✅ Aucune date d'achat avant la date d'inscription du client
✅ Sale_Price = prix unitaire du produit (Revenue = Quantity × Sale_Price)
✅ Total_Spent = somme exacte des Revenue du client
✅ Impressions ≥ Clics ≥ Conversions pour chaque campagne
✅ End_Date > Start_Date pour chaque campagne
✅ Campaign_ID dans sales pointe vers une campagne active et de même canal

AUTEUR   : Équipe Projet SMD IA & PRSD
DATE     : 2026-09
================================================================================
"""

# =============================================================================
# IMPORTS
# =============================================================================
import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker


# =============================================================================
# CONFIGURATION GLOBALE
# =============================================================================
# Les graines (seeds) garantissent que le script produit EXACTEMENT les mêmes
# données à chaque exécution. Essentiel pour la reproductibilité en équipe.

random.seed(42)
np.random.seed(42)
fake = Faker()
Faker.seed(42)

# Volumes
N_CUSTOMERS = 1000
N_PRODUCTS = 100
N_CAMPAIGNS = 200

# Période couverte par les données
START_DATE = datetime(2022, 1, 1)
END_DATE = datetime(2025, 12, 31)
REFERENCE_DATE = END_DATE  # Date de référence pour calculer la recency

# Dossier de sortie
OUTPUT_DIR = Path("data/generated")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================
def random_date(start, end):
    """Retourne une date aléatoire entre start et end (inclus)."""
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


def weighted_choice(items, weights):
    """Tirage aléatoire pondéré (ex: 60% Active, 20% At Risk, 20% Churned)."""
    return random.choices(items, weights=weights, k=1)[0]


# =============================================================================
# 1. GÉNÉRATION DES PRODUITS (100 lignes)
# =============================================================================
# 100 produits répartis dans 4 catégories avec des gammes de prix réalistes.
# Chaque produit a un ID unique (101-200), un nom, une catégorie, un prix
# et une marque.
# -----------------------------------------------------------------------------

categories = {
    "Clothing": ["T-shirt", "Shirt", "Jeans", "Hoodie", "Sweater",
                 "Dress", "Skirt", "Shorts", "Pants", "Blouse"],
    "Footwear": ["Sneakers", "Boots", "Sandals", "Running Shoes", "Casual Shoes"],
    "Outerwear": ["Jacket", "Coat", "Blazer", "Raincoat", "Windbreaker"],
    "Accessories": ["Hat", "Cap", "Belt", "Scarf", "Backpack",
                    "Handbag", "Wallet", "Sunglasses"]
}

brands = ["Brand A", "Brand B", "Brand C", "Brand D", "Brand E",
          "Brand F", "Brand G", "Brand H", "Brand I", "Brand J"]

# Fourchettes de prix par catégorie (logique métier réaliste)
price_ranges = {
    "Accessories": (10, 80),
    "Clothing": (20, 150),
    "Footwear": (50, 220),
    "Outerwear": (80, 300),
}

products_list = []
product_id = 101

for i in range(N_PRODUCTS):
    category = random.choice(list(categories.keys()))
    product_name = random.choice(categories[category])
    low, high = price_ranges[category]
    price = random.uniform(low, high)

    products_list.append({
        "Product_ID": product_id,
        "Product_Name": f"{product_name} {i + 1}",
        "Category": category,
        "Price": round(price, 2),
        "Brand": random.choice(brands)
    })
    product_id += 1

products = pd.DataFrame(products_list)


# =============================================================================
# 2. GÉNÉRATION DES CLIENTS (1000 lignes) - SANS Total_Spent pour l'instant
# =============================================================================
# Chaque client reçoit :
#   - Un comportement interne ("Active", "At Risk", "Churned") qui déterminera
#     son activité d'achat et servira à générer la cible Churn (M6).
#   - Une date d'inscription entre 2022-01-01 et 2024-12-31.
# -----------------------------------------------------------------------------

locations = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
    "Austin", "Jacksonville"
]

genders = ["Male", "Female"]

# Distribution des comportements clients (réaliste pour un e-commerce)
#   60% Active    → achètent régulièrement jusqu'à la fin
#   20% At Risk   → ralentissent leurs achats fin 2025
#   20% Churned   → arrêtent d'acheter courant 2025
customer_behaviors = ["Active", "At Risk", "Churned"]
behavior_weights = [0.60, 0.20, 0.20]

customers_list = []
customer_id = 2001

for _ in range(N_CUSTOMERS):
    join_date = random_date(START_DATE, datetime(2024, 12, 31))
    behavior = weighted_choice(customer_behaviors, behavior_weights)

    customers_list.append({
        "Customer_ID": customer_id,
        "Name": fake.name(),
        "Age": random.randint(18, 70),
        "Gender": random.choice(genders),
        "Location": random.choice(locations),
        "Join_Date": join_date,
        "_Behavior": behavior  # Colonne interne (supprimée avant export)
    })
    customer_id += 1

customers_internal = pd.DataFrame(customers_list)


# =============================================================================
# 3. GÉNÉRATION DES CAMPAGNES MARKETING (200 lignes)
# =============================================================================
# On génère les campagnes EN PREMIER pour pouvoir ensuite lier chaque vente à
# une campagne active à la date de l'achat (colonne Sales.Campaign_ID).
#
# Chaque canal a un profil de performance distinct :
#   - CTR (Click-Through Rate)  : clics / impressions
#   - Taux de conversion        : conversions / clics
# Cela permet à B3 (M5) d'analyser des performances réalistes.
# -----------------------------------------------------------------------------

marketing_channels = ["Online", "In-Store", "Social", "Email", "TV"]

channel_performance = {
    "Online":    {"ctr": (0.02, 0.08), "conversion": (0.04, 0.12)},
    "In-Store":  {"ctr": (0.01, 0.04), "conversion": (0.08, 0.20)},
    "Social":    {"ctr": (0.02, 0.10), "conversion": (0.02, 0.08)},
    "Email":     {"ctr": (0.03, 0.15), "conversion": (0.05, 0.18)},
    "TV":        {"ctr": (0.005, 0.03), "conversion": (0.01, 0.05)},
}

marketing_list = []

for campaign_id in range(1, N_CAMPAIGNS + 1):
    start_date = random_date(START_DATE, END_DATE - timedelta(days=30))
    end_date = start_date + timedelta(days=random.randint(7, 30))
    channel = random.choice(marketing_channels)
    budget = round(random.uniform(500, 10000), 2)
    impressions = random.randint(10000, 500000)

    ctr_min, ctr_max = channel_performance[channel]["ctr"]
    ctr = random.uniform(ctr_min, ctr_max)
    clicks = int(impressions * ctr)

    conv_min, conv_max = channel_performance[channel]["conversion"]
    conversion_rate = random.uniform(conv_min, conv_max)
    conversions = int(clicks * conversion_rate)

    marketing_list.append({
        "Campaign_ID": campaign_id,
        "Channel": channel,
        "Start_Date": start_date,
        "End_Date": end_date,
        "Budget": budget,
        "Impressions": impressions,
        "Clicks": clicks,
        "Conversions": conversions
    })

marketing = pd.DataFrame(marketing_list)


# =============================================================================
# 4. GÉNÉRATION DES VENTES
# =============================================================================
# Pour chaque client, on génère un nombre d'achats proportionnel à son
# comportement (Active > At Risk > Churned), sur des dates cohérentes.
#
# NOUVEAUTÉS par rapport à la version précédente :
#   - Canal d'achat étendu aux 5 canaux marketing (Online, In-Store, Social,
#     Email, TV) → permet un ROI par canal réel.
#   - Colonne Campaign_ID : lien vers une campagne active (même canal + date
#     dans l'intervalle). 50% des ventes sont "attribuées" à une campagne,
#     50% sont considérées organiques (Campaign_ID = NaN).
#   - Corrélation Âge ↔ Catégorie de produit : les jeunes achètent plutôt
#     du Clothing/Footwear, les plus âgés plutôt de l'Outerwear/Accessories.
#     Cela rend les clusters (M3/M4) interprétables métier.
# -----------------------------------------------------------------------------

sales_list = []
sale_id = 1

# Pools de produits par catégorie (pour la corrélation âge ↔ catégorie)
products_by_category = {
    cat: products[products["Category"] == cat]
    for cat in categories.keys()
}

# Pools de prix (pour At Risk / Churned qui achètent moins cher)
active_products = products[products["Price"] <= products["Price"].quantile(0.70)]
premium_products = products[products["Price"] >= products["Price"].quantile(0.60)]


def pick_product_for_customer(customer_age, behavior):
    """
    Choisit un produit de manière pondérée selon l'âge du client et son
    comportement. Crée ainsi une corrélation interprétable pour le clustering.
    """
    if behavior == "Active":
        # Les actifs achètent parfois premium (35%)
        if random.random() < 0.35:
            return premium_products.sample(1).iloc[0]
        pool = products
    else:
        pool = active_products

    # Corrélation âge ↔ catégorie
    if customer_age < 30:
        # Jeunes : Clothing / Footwear / Accessories
        preferred = ["Clothing", "Footwear", "Accessories"]
    elif customer_age < 50:
        # Middle : toutes catégories
        preferred = list(categories.keys())
    else:
        # Seniors : Outerwear / Accessories / Clothing
        preferred = ["Outerwear", "Accessories", "Clothing"]

    # Filtrer le pool sur les catégories préférées
    filtered = pool[pool["Category"].isin(preferred)]
    if filtered.empty:
        filtered = pool  # Fallback de sécurité
    return filtered.sample(1).iloc[0]


for _, customer in customers_internal.iterrows():
    behavior = customer["_Behavior"]
    join_date = customer["Join_Date"]
    age = customer["Age"]

    # --- Définition de la fenêtre d'achat selon le comportement ---
    if behavior == "Active":
        last_purchase_limit = END_DATE
        purchase_count = np.random.poisson(random.uniform(12, 25)) + 3
        quantity_max = 5
    elif behavior == "At Risk":
        last_purchase_limit = datetime(2025, 9, 30)
        purchase_count = np.random.poisson(random.uniform(5, 12)) + 1
        quantity_max = 4
    else:  # Churned
        last_purchase_limit = datetime(2025, 4, 30)
        purchase_count = np.random.poisson(random.uniform(2, 7)) + 1
        quantity_max = 3

    if last_purchase_limit < join_date:
        last_purchase_limit = join_date

    # --- Génération des achats ---
    for _ in range(purchase_count):
        # Date d'achat : distribution Beta pour simuler des patterns réalistes
        if behavior == "Active":
            sale_date = random_date(join_date, last_purchase_limit)
        else:
            total_days = (last_purchase_limit - join_date).days
            if total_days <= 0:
                sale_date = join_date
            else:
                # Beta(2,4) pour At Risk → concentration précoce
                # Beta(2,6) pour Churned → concentration très précoce
                a, b = (2, 4) if behavior == "At Risk" else (2, 6)
                position = np.random.beta(a, b)
                sale_date = join_date + timedelta(days=int(position * total_days))

        # Choix du produit (corrélé à l'âge + au comportement)
        product = pick_product_for_customer(age, behavior)
        quantity = random.randint(1, quantity_max)

        # Canal d'achat (pondéré, cohérent avec les canaux marketing)
        sale_channel = weighted_choice(
            ["Online", "In-Store", "Social", "Email", "TV"],
            [0.55, 0.25, 0.10, 0.05, 0.05]
        )

        # Attribution d'une campagne (50% des ventes)
        # On cherche les campagnes actives à cette date ET de même canal
        campaign_id = None
        if random.random() < 0.50:
            active_campaigns = marketing[
                (marketing["Start_Date"] <= sale_date) &
                (marketing["End_Date"] >= sale_date) &
                (marketing["Channel"] == sale_channel)
            ]
            if not active_campaigns.empty:
                campaign_id = int(
                    active_campaigns.sample(1).iloc[0]["Campaign_ID"]
                )

        sales_list.append({
            "Sale_ID": sale_id,
            "Product_ID": int(product["Product_ID"]),
            "Customer_ID": int(customer["Customer_ID"]),
            "Date": sale_date,
            "Quantity": quantity,
            "Sale_Price": float(product["Price"]),  # Prix UNITAIRE
            "Channel": sale_channel,
            "Campaign_ID": campaign_id  # Peut être NaN (vente organique)
        })
        sale_id += 1

sales = pd.DataFrame(sales_list)


# =============================================================================
# 5. CALCUL DU TOTAL_SPENT (cohérence garantie)
# =============================================================================
# Total_Spent = somme EXACTE de (Quantity × Sale_Price) pour chaque client.
# Le contrôle qualité en fin de script prouvera cette cohérence.
# -----------------------------------------------------------------------------

sales["_Revenue"] = sales["Quantity"] * sales["Sale_Price"]

customer_spending = (
    sales.groupby("Customer_ID")["_Revenue"]
    .sum()
    .reset_index()
    .rename(columns={"_Revenue": "Total_Spent"})
)

# On supprime la colonne interne _Revenue de sales (on ne l'exporte pas)
sales = sales.drop(columns=["_Revenue"])


# =============================================================================
# 6. FUSION CLIENTS + TOTAL_SPENT + CHURN
# =============================================================================
# On ajoute la colonne Churn (0/1) à partir du comportement interne :
#   - Active   → Churn = 0
#   - At Risk  → Churn = 1  (futurs churners, cible réaliste pour M6)
#   - Churned  → Churn = 1
#
# La colonne _Behavior est ensuite supprimée pour ne pas "tricher" lors de
# l'entraînement ML (elle servirait de fuite de données).
# -----------------------------------------------------------------------------

customers = customers_internal.copy()
customers["Churn"] = customers["_Behavior"].apply(
    lambda b: 0 if b == "Active" else 1
)

customers = customers.merge(
    customer_spending,
    on="Customer_ID",
    how="left"
)

customers["Total_Spent"] = customers["Total_Spent"].fillna(0).round(2)

# On supprime les colonnes internes
customers = customers.drop(columns=["_Behavior"])


# =============================================================================
# 7. FORMATAGE DES DATES POUR EXPORT CSV
# =============================================================================
customers["Join_Date"] = pd.to_datetime(customers["Join_Date"]).dt.strftime("%Y-%m-%d")
sales["Date"] = pd.to_datetime(sales["Date"]).dt.strftime("%Y-%m-%d")
marketing["Start_Date"] = pd.to_datetime(marketing["Start_Date"]).dt.strftime("%Y-%m-%d")
marketing["End_Date"] = pd.to_datetime(marketing["End_Date"]).dt.strftime("%Y-%m-%d")


# =============================================================================
# 8. EXPORT DES FICHIERS CSV
# =============================================================================
customers.to_csv(OUTPUT_DIR / "customers_data.csv", index=False)
products.to_csv(OUTPUT_DIR / "products_data.csv", index=False)
sales.to_csv(OUTPUT_DIR / "sales_data.csv", index=False)
marketing.to_csv(OUTPUT_DIR / "marketing_data.csv", index=False)


# =============================================================================
# 9. GÉNÉRATION DU DICTIONNAIRE DE DONNÉES (data_dictionary.md)
# =============================================================================
# Ce fichier est le "Data Contract V1" demandé en J1 par le planning.
# Il sera livré au Binôme 2 (ML) pour qu'il sache exactement quelles colonnes
# il recevra et ce qu'elles signifient.
# -----------------------------------------------------------------------------

data_dict_content = """# 📘 Dictionnaire de Données — Data Contract V1

Généré automatiquement par `generate_data.py`.

## 1. `customers_data.csv` (1000 lignes)

| Colonne | Type | Description |
|---------|------|-------------|
| Customer_ID | int | Clé primaire (2001-3000) |
| Name | str | Nom complet du client |
| Age | int | Âge entre 18 et 70 |
| Gender | str | Male / Female |
| Location | str | Ville de résidence (12 villes US) |
| Join_Date | date | Date d'inscription (YYYY-MM-DD) |
| Total_Spent | float | Somme exacte des achats du client |
| Churn | int | 0 = Actif, 1 = À risque/Parti (cible M6) |

## 2. `products_data.csv` (100 lignes)

| Colonne | Type | Description |
|---------|------|-------------|
| Product_ID | int | Clé primaire (101-200) |
| Product_Name | str | Nom du produit |
| Category | str | Clothing / Footwear / Outerwear / Accessories |
| Price | float | Prix unitaire (USD) |
| Brand | str | Marque (Brand A à J) |

## 3. `sales_data.csv` (~15000 lignes)

| Colonne | Type | Description |
|---------|------|-------------|
| Sale_ID | int | Clé primaire de la transaction |
| Product_ID | int | Clé étrangère → products_data |
| Customer_ID | int | Clé étrangère → customers_data |
| Date | date | Date de l'achat (>= Join_Date du client) |
| Quantity | int | Quantité achetée (1 à 5) |
| Sale_Price | float | Prix UNITAIRE au moment de l'achat |
| Channel | str | Online / In-Store / Social / Email / TV |
| Campaign_ID | int or NaN | Campagne active attribuée (50% des ventes), sinon organique |

**⚠️ À retenir** : `Revenue = Quantity × Sale_Price` (à calculer par B1/B2).

## 4. `marketing_data.csv` (200 lignes)

| Colonne | Type | Description |
|---------|------|-------------|
| Campaign_ID | int | Clé primaire |
| Channel | str | Online / In-Store / Social / Email / TV |
| Start_Date | date | Début de la campagne |
| End_Date | date | Fin de la campagne (> Start_Date) |
| Budget | float | Budget dépensé (USD) |
| Impressions | int | Nombre de vues |
| Clicks | int | Nombre de clics (<= Impressions) |
| Conversions | int | Nombre de conversions (<= Clicks) |
"""
