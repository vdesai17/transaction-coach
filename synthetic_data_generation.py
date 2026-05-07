from faker import Faker
import random
import pandas as pd
import calendar
import os

fake = Faker()

categories = [
    "Groceries",
    "Housing and Utilities",
    "Rent Payments",
    "Home Goods and Furniture",
    "Fuel and Transport",
    "Vehicle Loans and Fines",
    "Salary / Payroll",
    "Business or Freelance Income",
    "Government Support and Pensions",
    "Charity Donations",
    "Bank Charges",
    "Insurance",
    "Shopping & Retail",
    "Dining and Cafes",
    "Entertainment and Leisure",
    "Travel and Hotels",
    "Medical and Health",
    "Education",
    "Savings and Investments",
    "Loan Payments",
    "Other / Uncategorized",
    "Telecom"
]

merchants = {
    "Groceries": [
        # Oman
        "Lulu Hypermarket", "Carrefour Oman", "Al Fair", "KM Trading", "Al Meera",
        "Nesto", "SPAR Oman", "Sultan Center", "Spinneys", "HyperMax Qurum City Centre",
        "Viva Supermarket", "Asian Cold Store", "Al Khoud Market", "Al Hashar Supermarket",
        "Al Qurum Market", "Al Ghubra Market", "Al Madina Supermarket", "Al Rawda Supermarket",
        "Al Tadamun", "Oman Cooperative Society", "Al Musannah Market", "Al Hamra Supermarket",
        "Muscat Cooperative Society", "Bin Ali Supermarket", "Safeer Market", "Ansar Gallery",
        "Baqala", "Express by Lulu", "Meera Express", "Grand Khan Supermarket",
        "City Market Oman", "Right Price", "Food Basket", "Carrefour", "Carrefour Express",
        # Canada
        "Loblaws", "No Frills", "Metro Ontario", "Sobeys", "Food Basics",
        "FreshCo", "Farm Boy", "Longos", "Walmart Canada", "Costco Canada",
        "T&T Supermarket", "Independent Grocer", "Rabba Fine Foods", "Grocery Gateway",
        "Whole Foods Market Canada", "Fortinos", "Zehrs", "Valu-mart"
    ],

    "Housing and Utilities": [
        # Oman
        "Majan Electricity", "Muscat Electricity Distribution", "Diam Water", "OPWP", "Be'ah Oman",
        "Muscat Municipality Water", "Oman Electricity Transmission Company",
        "Nama Electricity Supply Company", "Muscat Municipality",
        "Muscat Municipality Parking", "Municipal Parking Fees", "Muscat Municipality Cleaning Services",
        "Muscat Municipality Water & Sewerage",
        # Canada
        "Toronto Hydro", "Enbridge Gas", "Union Gas", "Hydro One",
        "Toronto Water", "Alectra Utilities", "PowerStream", "Enersource",
        "Rogers Home Internet", "Bell Home Internet", "Telus Home",
        "City of Toronto Utilities", "Reliance Home Comfort"
    ],

    "Fuel and Transport": [
        # Oman
        "Shell Oman", "Oman Oil", "Al Maha Petroleum", "Mwasalat", "Muscat Taxi",
        "Careem", "Uber", "PDO Petrol Station", "OQ Fuels", "National Oil Company",
        "Muscat Fuel Station", "Gulf Petro", "Majan Fuel Station", "Petromin",
        "Bahla Petrol Station", "Suhar Fuel Station", "Al Madina Garage", "Muscat Airport Taxi",
        "Oman Rail", "Oman Bus Company", "Al Sharq Transport", "Crossroads Rental",
        "Petromin Express", "ZipCar Oman", "YANGO", "Tasleem Taxi", "Dhofar Bus Company",
        "Al Rawda Transport", "Muscat Taxi Service", "Oman Car Rentals", "Oman Chauffeur Services",
        "Oman Railway Corporation", "Oman Roads & Transport Authority (Mwasalat)", "Al Maha Petroleum",
        "Oman Automobile Services", "Al Maha Car Wash", "National Oil Company", "Muscat Fuel Station", "Gulf Petro",
        "Majan Fuel Station", "Bahla Petrol Station", "Sohar Fuel Station",
        # Canada
        "TTC Toronto Transit", "Presto Card", "GO Transit", "MiWay Transit",
        "Brampton Transit", "York Region Transit", "OC Transpo Ottawa",
        "Via Rail Canada", "Porter Airlines", "Air Canada",
        "Petro-Canada", "Esso Canada", "Shell Canada", "Canadian Tire Gas",
        "Ultramar", "Husky Energy", "Pioneer Gas", "Sunoco Canada",
        "Uber Canada", "Lyft Canada", "Enterprise Rent-A-Car Canada",
        "Budget Car Rental Canada", "Hertz Canada", "ZipCar Canada"
    ],

    "Dining and Cafes": [
        # Oman
        "PAUL", "Nandos", "Wagamama", "Shawarma Time", "Yellow Chilli", "Caribou Coffee",
        "Starbucks Oman", "Costa Coffee Oman", "Mado Cafe", "Tea Corner", "Kaldi Coffee",
        "KFC", "McDonalds", "RFC", "P.F. Chang's", "Burger King", "Hardee's", "Pizza Hut",
        "Domino's Pizza", "Papa John's", "Chili's Grill & Bar", "Tim Hortons", "The Coffee Bean & Tea Leaf",
        "Operation Falafel", "Al Tanoor", "Zaytoon", "Elevate Lounge", "Al Khod Café", "Pita Pan",
        "Bosphorus Turkish Restaurant", "Saffron Lounge", "Taste of India", "Indian Palace",
        "Beirut Restaurant", "Al Boom Steak & Seafood", "Bin Ateeq", "Bait Al Luban", "Hafez Restaurant",
        "Nando's", "Al Angham", "Cafe Bateel", "Golden Dragon Restaurant", "Fauchon Paris", "Caffe Farah",
        "D'Arcy's Kitchen", "CHAR", "Al Khiran Kitchen", "The Backstage", "Lebanese Village", "Ramssa Restaurant",
        "Nabu Cafe", "WET Deck Muscat", "HARVEST", "MLS Steakhouse", "NANA's Restaurant", "Mint & Coco",
        "Kalabash Restaurant & Lounge", "Irishman", "KAIA", "Mango Talat", "Begum's Kitchen",
        "Jazirat Al Jazeera Restaurant", "Bandar Seafood", "Al Ajmi Family Restaurant", "Coffee Talk",
        "Shawarma Factory", "Coffee Republic", "Wow Momo", "Urban Brew Cafe", "Harvest Bistro",
        "Luna Ristorante", "Sea Breeze Grill", "Spice Route", "Mazoon Dairy",
        # Canada
        "Tim Hortons Canada", "Second Cup", "Pilot Coffee Co", "Dineen Coffee",
        "Dark Horse Espresso", "Te Aro Coffee", "Balzac's Coffee",
        "Harvey's", "Swiss Chalet", "The Keg Steakhouse", "Montana's BBQ",
        "East Side Mario's", "St. Louis Bar and Grill", "Jack Astor's",
        "Osmow's Shawarma", "Shawarma Empire", "Paramount Fine Foods",
        "Popeyes Canada", "Subway Canada", "Five Guys Canada",
        "Fran's Restaurant", "Terroni", "Pai Northern Thai Kitchen",
        "Banjara Indian Cuisine", "Sushi Couture", "Sansotei Ramen"
    ],

    "Shopping & Retail": [
        # Oman
        "Centrepoint", "Max Fashion", "Splash Oman", "REDTAG", "Brands for Less",
        "H&M", "ZARA", "Bershka", "Mango", "Pull and Bear", "Nike", "Adidas",
        "Marks & Spencer", "New Look", "Debenhams", "Charles & Keith",
        "Sun & Sand Sports", "Accessorize", "The Body Shop", "Pandora", "Sephora",
        "Babyshop", "Mothercare", "Timberland", "Levi's", "Tommy Hilfiger", "Noor Shopping",
        "Malabar Gold and Diamonds", "Joyalukkas Jewellery", "Cochin Gold & Diamonds",
        "Matalan Oman", "SBK FASHIONS", "Aeropostale", "Beverly Hills Polo Club", "Hollister",
        "L'Occitane", "Mom & Baby", "Jarir Bookstore", "Borders", "Miniso",
        "Muji", "Bath & Body Works", "Skechers", "Urban Outfitters Oman",
        "Guess Oman", "Calvin Klein Oman", "Superdry Oman", "GAP Oman",
        # Canada
        "Canadian Tire", "Winners", "HomeSense", "Sport Chek", "Hudson's Bay",
        "Indigo Books", "Chapters", "Roots Canada", "Reitmans", "Simons",
        "Aritzia", "Lululemon Canada", "MEC Mountain Equipment",
        "Mark's Work Warehouse", "Giant Tiger", "Dollar Tree Canada",
        "Value Village", "Home Depot Canada", "IKEA Canada",
        "Best Buy Canada", "Apple Store Canada", "Microsoft Store Canada",
        "Staples Canada", "Bureau en Gros", "GAP Canada", "H&M Canada",
        "Zara Canada", "Forever 21 Canada", "Urban Outfitters Canada"
    ],

    "Home Goods and Furniture": [
        # Oman
        "Fahmy Furniture", "Luxury Homes Oman", "Home Centre", "The Container Store",
        "IKEA (Oman Branch)", "PanHome Furniture", "Home Box", "Midas Furniture",
        # Canada
        "IKEA Canada", "The Brick", "Leon's Furniture", "Ashley HomeStore Canada",
        "Structube", "Article Furniture", "HomeSense Canada", "Crate and Barrel Canada",
        "Pottery Barn Canada", "West Elm Canada", "CB2 Canada"
    ],

    "Government Services": [
        # Oman
        "Royal Oman Police", "Ministry of Education", "Ministry of Health",
        "Oman Tax Authority", "Public Authority for Social Insurance (PASI)",
        "Civil Aviation Authority", "Muscat Municipality", "Oman Customs Authority",
        "Land Transport Regulatory Authority", "Muscat Municipal Parking", "ROP Visa Department",
        "Ministry of Housing", "MOM Licensing", "Municipal Parking Fees", "TRA Oman",
        "Land Tax Dept Oman", "Vehicle Registration Oman",
        "Residency Permit Fees", "Customs Duty Payments", "Municipality Zoning Fees",
        # Canada
        "Service Ontario", "Service Canada", "Canada Revenue Agency",
        "City of Toronto Parking", "Toronto Parking Authority", "Ministry of Transportation Ontario",
        "DriveTest Ontario", "Passport Canada", "IRCC Immigration Canada",
        "Canada Post", "OHIP Ontario Health"
    ],

    "Medical and Health": [
        # Oman
        "Muscat Pharmacy", "Aster Hospital", "Starcare Hospital", "Badr Al Samaa",
        "Boots Pharmacy", "Seef Pharmacy", "Mediclinic Oman", "Zulekha Hospital",
        "Royal Hospital Pharmacy", "NMC Healthcare Oman", "Lifeline Hospital",
        "Al Amal Medical Center", "Advanced Eye Care Center", "Health 360 Clinic",
        # Canada
        "Shoppers Drug Mart", "Rexall Pharmacy", "Pharmasave Canada",
        "Medcan Toronto", "Cleveland Clinic Canada", "Maple Telehealth",
        "Sunnybrook Hospital", "SickKids Foundation", "Unity Health Toronto",
        "Wellwise by Shoppers", "Life Labs Canada", "Dynacare Labs"
    ],

    "Education": [
        # Oman
        "Sultan Qaboos University", "Majan University", "Caledonian College",
        "Middle East College", "Gulf College", "Indian School Muscat",
        "British School Muscat", "American British Academy", "Oman Dental College",
        "German University of Technology", "Pakistan School Muscat",
        "Muscat International School", "International Grammar School", "Indian School Al Ghubra",
        "Al Yusr School", "Al Injaz International Private School", "Leaders Private School",
        "American Lyceum International School", "Qurum International Private School",
        "Knowledge Haven Academy", "SkillUp Institute", "Bright Future Prep",
        "Excel Language Center", "STEM Hub Muscat",
        # Canada
        "University of Toronto", "Toronto Metropolitan University", "York University",
        "Seneca College", "Humber College", "George Brown College",
        "Coursera Canada", "Udemy Canada", "LinkedIn Learning",
        "Toronto District School Board", "Kumon Canada", "Sylvan Learning Canada"
    ],

    "Entertainment and Leisure": [
        # Oman
        "VOX Cinemas", "Magic Planet", "Fun City", "Oman Aquarium",
        "Muscat Festival Events", "City Centre Muscat", "Royal Opera House Muscat",
        "Adventure HQ Oman", "Wadi Adventure", "Wave Waterpark",
        "Oman National Museum", "Royal Opera House", "Oman Convention Centre",
        # Canada
        "Cineplex Odeon", "Scotiabank Arena", "Rogers Centre Toronto",
        "Ontario Science Centre", "Toronto Zoo", "CN Tower Toronto",
        "Ripley's Aquarium Toronto", "Steam Whistle Brewery",
        "Netflix Canada", "Spotify Canada", "Apple iTunes Canada",
        "Disney Plus Canada", "Crave TV", "Amazon Prime Canada",
        "Rec Room Toronto", "Playdium Canada", "TopGolf Canada",
        "Dave and Busters Canada", "Escape Manor Toronto"
    ],

    "Travel and Hotels": [
        # Oman
        "Oman Air", "SalamAir", "Al Bustan Palace", "Shangri-La Barr Al Jissah",
        "Hilton Muscat", "InterContinental Muscat", "The Chedi Muscat", "Novotel",
        "Radisson Blu", "Crowne Plaza", "City Seasons Hotel", "Al Falaj Hotel",
        "Muscat Hills Resort", "Grand Hyatt Muscat", "Salalah Express",
        "Gulf Air", "Emirates Airlines", "Qatar Airways", "Etihad Airways",
        # Canada
        "Air Canada", "WestJet", "Porter Airlines", "Sunwing Airlines",
        "Marriott Toronto", "Hilton Toronto", "Westin Harbour Castle Toronto",
        "Delta Hotels Toronto", "Fairmont Royal York", "Hotel X Toronto",
        "Airbnb Canada", "Expedia Canada", "Booking.com Canada",
        "Via Rail Canada", "Greyhound Canada", "Megabus Canada"
    ],

    "Bank Charges": [
        # Oman
        "Bank Muscat", "HSBC Oman", "Bank Dhofar", "National Bank of Oman",
        "OAB", "Ahli Bank", "Alizz Islamic Bank", "Bank Sohar", "Bank Nizwa",
        "Gulf International Bank", "Oman Arab Bank", "Oman Arab Finance",
        # Canada
        "TD Bank Canada", "RBC Royal Bank", "Scotiabank Canada",
        "BMO Bank of Montreal", "CIBC Canada", "Tangerine Bank",
        "EQ Bank Canada", "Simplii Financial", "National Bank Canada",
        "HSBC Canada", "Meridian Credit Union", "PC Financial"
    ],

    "Insurance": [
        # Oman
        "AXA Oman", "National Life Insurance", "Dhofar Insurance",
        "Oman Insurance Company", "AXA Gulf", "Al Madina Insurance",
        "Oman Reinsurance", "Noor Takaful", "Oman United Insurance", "Vision Insurance",
        "SecureLife Takaful", "HealthGuard Oman", "FutureShield Insurance",
        "OmanCare Insurance", "SafeFuture Insurance", "Al Madina Takaful",
        "Oman Reinsurance Company",
        # Canada
        "Intact Insurance Canada", "Desjardins Insurance", "Aviva Canada",
        "TD Insurance Canada", "Sonnet Insurance", "Belairdirect",
        "Manulife Canada", "Sun Life Canada", "Great-West Life",
        "CAA Insurance Ontario", "Wawanesa Insurance"
    ],

    "Charity Donations": [
        # Oman
        "Dar Al Atta'a", "Oman Charitable Organization", "Zakat Fund",
        "Oman Cancer Association", "Sultan Qaboos Fund",
        # Canada
        "United Way Canada", "Red Cross Canada", "SickKids Foundation",
        "Food Banks Canada", "Habitat for Humanity Canada",
        "World Vision Canada", "UNICEF Canada", "Canadian Cancer Society"
    ],

    "Rent Payments": [
        # Oman
        "Al Habib Real Estate", "Savills Oman", "Hamptons International",
        "Wave Homes LLC", "Hilal Properties", "Vista Real Estate",
        "Platinum Properties", "Luxe Properties", "Tamlik Properties",
        "Golden Sands Leasing", "Sunrise Apartments",
        "Royal Vista Rentals", "Emerald Bay Homes", "Pearl Coast Residence",
        # Canada
        "CondoRent Toronto", "Greenwin Property Management", "Minto Apartments",
        "Boardwalk Rental Communities", "Oxford Properties Toronto",
        "Realstar Management", "Briarlane Rental Property Management",
        "Medallion Corporation Toronto", "Tridel Rental", "Concert Properties"
    ],

    "Other / Uncategorized": [
        # Oman
        "Talabat Oman", "Netflix MENA", "OSN Oman", "MidLand Developers",
        "TechConnect Oman", "SmartCity Exhibition", "GadgetWorld Oman",
        "Artisan Craft Bazaar", "EcoFest Oman",
        # Canada
        "DoorDash Canada", "SkipTheDishes", "Instacart Canada",
        "Amazon Canada", "eBay Canada", "Etsy Canada",
        "PayPal Canada", "Shopify Canada", "Stripe Canada"
    ],

    "Telecom": [
        # Oman
        "Ooredoo", "Omantel", "Renna Mobile", "Friendi Mobile", "SalamMobile",
        "Telecom Oman", "Arab International Connect", "Mwasalat WiFi",
        "Oman Broadband", "OBN (Oman Broadband Network)", "Vodafone",
        # Canada
        "Rogers Wireless", "Bell Mobility", "Telus Mobility",
        "Fido Mobile", "Koodo Mobile", "Freedom Mobile",
        "Virgin Plus Canada", "Public Mobile Canada", "Chatr Wireless",
        "Lucky Mobile", "Shaw Mobile"
    ],

    "Savings and Investments": [
        # Oman
        "Muscat Securities Market", "Oman Investment Fund", "Bank Muscat Savings",
        "National Bank of Oman Savings", "Meethaq Islamic Banking",
        # Canada
        "Wealthsimple Invest", "Questrade Canada", "TD Direct Investing",
        "RBC Direct Investing", "CIBC Investor's Edge", "BMO InvestorLine",
        "Scotiabank iTRADE", "Manulife Investments", "Fidelity Canada",
        "iShares Canada", "Vanguard Canada"
    ],

    "Loan Payments": [
        # Oman
        "Bank Muscat Loan", "NBO Personal Loan", "Bank Dhofar Loan",
        "Ahli Bank Loan", "HSBC Oman Loan",
        # Canada
        "TD Loan Payment", "RBC Personal Loan", "BMO Loan Payment",
        "Scotiabank Loan", "CIBC Loan Payment", "Mogo Loan",
        "Fairstone Financial", "easyfinancial Canada"
    ],

    "Vehicle Loans and Fines": [
        # Oman
        "Royal Oman Police Fine", "Muscat Traffic Fine", "Oman Vehicle Loan",
        "Al Maha Auto Loan", "Bank Muscat Auto Finance",
        # Canada
        "City of Toronto Parking Fine", "Ontario Court Fine",
        "Toronto Police Ticket", "407 ETR Toll",
        "TD Auto Finance", "RBC Auto Loan", "Scotiabank Auto Finance"
    ],

    "Government Support and Pensions": [
        # Oman
        "PASI Oman Pension", "Oman Social Insurance", "Ministry of Social Development",
        # Canada
        "Canada Pension Plan CPP", "Ontario Works Payment",
        "CERB Canada", "EI Employment Insurance", "GST HST Credit Canada",
        "Ontario Trillium Benefit", "Canada Child Benefit"
    ],

    "Business or Freelance Income": [
        "Upwork Payment", "Fiverr Income", "PayPal Transfer",
        "Stripe Payout", "Shopify Payout", "Etsy Payout",
        "Freelancer.com Payment", "Toptal Income",
        "Direct Deposit Freelance", "E-Transfer Income"
    ],

    "Salary / Payroll": [
        "Direct Deposit Payroll", "ADP Payroll", "Payworks Canada",
        "Ceridian HCM", "Paylocity", "SAP Payroll",
        "Bank Muscat Salary Credit", "RBC Payroll Deposit",
        "TD Payroll Direct Deposit", "Scotiabank Salary"
    ]
}

# Oman locations
cities = ["Muscat", "Seeb", "Sohar", "Salalah", "Nizwa", "Ibri"]

muscat_areas = [
    "Qurum", "Al Khuwair", "Madinat Qaboos", "Ghubra", "Al Azaiba", "Mabela",
    "Al Mawaleh", "Seeb", "Al Hail", "Bausher", "Amerat", "Ruwi", "Muttrah",
    "Wadi Kabir", "Al Ghubrah North", "Al Ghubrah South", "Al Koudh", "Al Ansab",
    "Wattayah", "Wadi Adai", "Hamriya", "Ghala", "Wadi Al Kabir", "Al Wadi Al Kabir"
]

other_areas = [
    "Suwaiq", "Barka", "Shinas", "Ibri", "Saham", "Bidiya", "Izki",
    "Ibra", "Sinaw", "Adam", "Rustaq", "Sur", "Jalan Bani Bu Ali", "Jalan Bani Bu Hassan",
    "Haima", "Duqm", "Thumrait", "Yanqul", "Bahla", "Masirah", "Mirbat", "Taqah"
]

# Canadian locations added
canadian_locations = [
    "Toronto", "Mississauga", "Scarborough", "North York", "Etobicoke",
    "Brampton", "Markham", "Richmond Hill", "Vaughan", "Oakville",
    "Hamilton", "Ottawa", "Vancouver", "Calgary", "Montreal",
    "Waterloo", "Kitchener", "London Ontario", "Windsor Ontario",
    "Barrie", "Kingston Ontario", "Sudbury", "Thunder Bay"
]

amount_ranges = {
    "Groceries": (1, 250),
    "Housing and Utilities": (20, 300),
    "Rent Payments": (100, 2500),
    "Home Goods and Furniture": (20, 500),
    "Fuel and Transport": (1, 50000),
    "Government Services": (1, 1000),
    "Salary / Payroll": (500, 40000),
    "Business or Freelance Income": (100, 7000),
    "Government Support and Pensions": (100, 1000),
    "Charity Donations": (10, 10000),
    "Bank Charges": (1, 500),
    "Insurance": (20, 1000),
    "Dining and Cafes": (3, 300),
    "Entertainment and Leisure": (5, 100),
    "Shopping & Retail": (1, 500),
    "Travel and Hotels": (100, 5000),
    "Medical and Health": (10, 5000),
    "Education": (500, 15000),
    "Savings and Investments": (50, 2000),
    "Loan Payments": (500, 20000),
    "Other / Uncategorized": (1, 1000),
    "Telecom": (3, 200),
    "Vehicle Loans and Fines": (50, 15000),
    "Salary / Payroll": (500, 40000),
    "Business or Freelance Income": (100, 7000),
    "Government Support and Pensions": (100, 1000),
}

locations = list(set(cities + muscat_areas + other_areas + canadian_locations))
locations.sort()


def generate_transaction():
    category = random.choice(list(merchants.keys()))
    merchant = random.choice(merchants[category])
    city = random.choice(locations)
    card_suffix = str(random.randint(1000, 9999))

    # --- Description formats ---
    formats = [
        f"RECEIPT {merchant.upper()} {city.upper()}",
        f"RECEIVED_FROM_{merchant.replace(' ', '_')}",
        f"TRF TO {merchant.upper()}",
        f"TRF {merchant.upper()}",
        f"{merchant.upper()} PAYMENT",
        f"PAYMENT TO {merchant.upper()} FOR {fake.month_name()} {random.randint(2019, 2025)}",
        f"{merchant} - payment",
        f"Payment:{merchant.upper()}",
        f"{merchant.upper()} SERVICE CHARGE",
        f"Transfer from {merchant}",
        f"{merchant.upper()} *{card_suffix}",
        f"{merchant.lower().replace(' ', '')}{city.upper()}",
        f"{merchant.upper()} {random.choice(['LLC', 'SAOG', 'INC', 'LTD'])}",
        f"www.{merchant.lower().replace(' ', '')}.com",
        f"{merchant.upper()}POS{city.upper()}",
        f"{merchant.upper()}#{random.randint(1000, 9999)}",
        f"POS PURCHASE {merchant.upper()} {fake.date('%b')} {random.randint(1, 28)}",
        f"PUR-{merchant.replace(' ', '')[:8].upper()}",
        f"{merchant.lower()} {random.choice(['debit', 'crd', 'payment', 'trsf'])}",
        f"txn {merchant.upper()}",
        f"{merchant.upper()} / {city.upper()}",
        f"{merchant.upper()}_{city[:3].upper()}",
        f"{merchant.upper()}:{random.choice(['PAY', 'TRF', 'REC'])}",
        f"{merchant.upper()} CARD*{card_suffix}",
        f"@{merchant.lower().replace(' ', '')}",
        f"{merchant.title()} Store #{random.randint(1, 999)}",
        f"{merchant.upper()} {fake.date_object().strftime('%d%m')}",
        f"POS {merchant.upper()} **{card_suffix}",
        f"{merchant.upper()}_{random.randint(10000, 99999)}",
        f"{merchant.upper()} TXNID:{random.randint(1000000, 9999999)}",
        f"{merchant.replace(' ', '')[:5].upper()}_{random.randint(10, 99)}",
        f"{merchant} Trnsfr",
        f"{merchant} x{random.randint(1000, 9999)}",
        f"POS {random.randint(100000, 999999)}-thw-{merchant.replace(' ', '').lower()}",
        f"POS {random.randint(100000, 999999)}-{merchant.upper()} - {random.randint(1, 999)} P O BOX {random.randint(1, 999)}",
        f"Wallet Trx {random.randint(1000000000000, 9999999999999)} {merchant.upper()}",
        f"WAL Cr{random.randint(1000000000000, 9999999999999)} BM",
        f"ATM Cash Withdrw {merchant} {random.randint(100000, 999999)} {fake.time('%H:%M:%S')}",
        f"ATM Cash DEP {merchant} {random.randint(100000, 999999)}",
        f"INTERAC {merchant.upper()} {city.upper()}",
        f"VISA DEBIT {merchant.upper()} {city[:3].upper()}",
        f"MASTERCARD {merchant.upper()} *{card_suffix}",
        f"E-TRANSFER {merchant.upper()}",
        f"ONLINE PURCHASE {merchant.upper()}",
    ]

    description = random.choice(formats)
    if random.random() < 0.3:
        description = description.replace(" ", "")

    # Amount for the transaction
    low, high = amount_ranges.get(category, (1, 500))
    amount = round(random.uniform(low, high), 2)

    income_categories = {
        "Salary / Payroll",
        "Business or Freelance Income",
        "Government Support and Pensions"
    }
    income_keywords = ["received", "transfer from", "received_from", "trnsfr", "credit"]
    desc_lower = description.lower()

    is_income = (
            category in income_categories or
            any(keyword in desc_lower for keyword in income_keywords)
    )

    if not is_income:
        amount *= -1

    # date of the trans
    if is_income:
        year = fake.date_between(start_date='-6M', end_date='today').year
        month = fake.date_between(start_date='-6M', end_date='today').month
        day = random.choice([28, 29, 30])
        try:
            date = pd.Timestamp(year=year, month=month, day=day)
        except ValueError:
            date = pd.Timestamp(year=year, month=month, day=28)
    else:
        # making more expense activity in early month
        base_date = fake.date_between(start_date='-6M', end_date='today')
        day = random.choices(range(1, 29), weights=[3 if d <= 10 else 1 for d in range(1, 29)])[0]
        try:
            date = pd.Timestamp(year=base_date.year, month=base_date.month, day=day)
        except ValueError:
            date = pd.Timestamp(year=base_date.year, month=base_date.month, day=28)

    return {
        "description": description,
        "amount": amount,
        "date": date,
        "category": category
    }


# ── Generate and save ──────────────────────────────────────────────
N = 30000
print(f"Generating {N} transactions...")
transactions = [generate_transaction() for _ in range(N)]
df = pd.DataFrame(transactions)

# Save to server/data folder
output_dir = os.path.join("server", "data")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "transactions.csv")
df.to_csv(output_path, index=False)

print(f"\nSaved {len(df)} transactions to {output_path}")
print(f"\nCategory distribution:")
print(df["category"].value_counts())
print(f"\nSample descriptions:")
print(df["description"].head(10).to_string())


# ── Out-of-sample test data (unlabeled) ────────────────────────────
test_merchant_category_map = {
    # Existing Oman entries
    "Towell Properties": "Rent Payments",
    "Al Meera Hypermarket": "Groceries",
    "Noor Shopping": "Shopping & Retail",
    "Fathima Hypermarket": "Groceries",
    "AGI Express Shop": "Groceries",
    "Oman Electricity Transmission Company": "Housing and Utilities",
    "Nama Electricity Supply Company": "Housing and Utilities",
    "YANGO": "Fuel and Transport",
    "Tasleem Taxi": "Fuel and Transport",
    "Caffe Farah": "Dining and Cafes",
    "Fauchon Paris": "Dining and Cafes",
    "D'Arcy's Kitchen": "Dining and Cafes",
    "CHAR": "Dining and Cafes",
    "Al Khiran Kitchen": "Dining and Cafes",
    "The Backstage": "Dining and Cafes",
    "Lebanese Village": "Dining and Cafes",
    "Ramssa Restaurant": "Dining and Cafes",
    "Nabu Cafe": "Dining and Cafes",
    "WET Deck Muscat": "Dining and Cafes",
    "HARVEST": "Dining and Cafes",
    "MLS Steakhouse": "Dining and Cafes",
    "NANA's Restaurant": "Dining and Cafes",
    "Mint & Coco": "Dining and Cafes",
    "Kalabash Restaurant & Lounge": "Dining and Cafes",
    "Irishman": "Dining and Cafes",
    "KAIA": "Dining and Cafes",
    "Mango Talat": "Dining and Cafes",
    "Muscat Private Hospital": "Medical and Health",
    "Badr Al Samaa Royal Hospital": "Medical and Health",
    "Apollo Hospital Muscat LLC": "Medical and Health",
    "Sagar Polyclinic": "Medical and Health",
    "NMC Specialty Hospital": "Medical and Health",
    "Nike": "Shopping & Retail",
    "Adidas": "Shopping & Retail",
    "Malabar Gold and Diamonds": "Shopping & Retail",
    "Badr Al Samaa Medical Center": "Medical and Health",
    "Royal Hospital Pharmacy": "Medical and Health",
    "NMC Healthcare Oman": "Medical and Health",
    "Mediclinic": "Medical and Health",
    "Al Amal Medical Center": "Medical and Health",
    "Al Hayat Medical Center": "Medical and Health",
    "Zulekha Hospital": "Medical and Health",
    "Al Shifa Pharmacy": "Medical and Health",
    "Al Shifa Medical Center": "Medical and Health",
    "Seef Pharmacy": "Medical and Health",
    "Health 360 Clinic": "Medical and Health",
    "Muscat Dental Clinic": "Medical and Health",
    "Advanced Eye Care Center": "Medical and Health",
    "VOX Cinemas": "Entertainment and Leisure",
    "Magic Planet": "Entertainment and Leisure",
    "Fun City": "Entertainment and Leisure",
    "Oman Aquarium": "Entertainment and Leisure",
    "Oman Diving Center": "Entertainment and Leisure",
    "Oman Golf Club": "Entertainment and Leisure",
    "Muscat Grand Mall Entertainment": "Entertainment and Leisure",
    "Wadi Adventure": "Entertainment and Leisure",
    "City Centre Muscat": "Entertainment and Leisure",
    "Wave Waterpark": "Entertainment and Leisure",
    "Muscat International Exhibition Centre": "Entertainment and Leisure",
    "Oman Convention & Exhibition Centre": "Entertainment and Leisure",
    "Sultan Qaboos Cultural Centre": "Entertainment and Leisure",
    "Oman National Museum": "Entertainment and Leisure",
    "Royal Opera House Muscat": "Entertainment and Leisure",
    "Oman Botanical Garden": "Entertainment and Leisure",
    "Oman Horse Racing": "Entertainment and Leisure",
    "Muscat Festival Events": "Entertainment and Leisure",
    "Adventure HQ Oman": "Entertainment and Leisure",
    "Bank Muscat": "Bank Charges",
    "HSBC Oman": "Bank Charges",
    "National Bank of Oman (NBO)": "Bank Charges",
    "Bank Dhofar": "Bank Charges",
    "Ahli Bank": "Bank Charges",
    "Alizz Islamic Bank": "Bank Charges",
    "Bank Sohar": "Bank Charges",
    "Al Khalij Commercial Bank": "Bank Charges",
    "Oman International Bank": "Bank Charges",
    "Muscat Finance Company": "Bank Charges",
    "Oman Insurance Company": "Insurance",
    "AXA Gulf": "Insurance",
    "Al Madina Insurance": "Insurance",
    "Al Madina Takaful": "Insurance",
    "Oman Reinsurance Company": "Insurance",
    "Noor Takaful": "Insurance",
    "Bank Nizwa": "Bank Charges",
    "Islamic Bank of Oman": "Bank Charges",
    "Oman Arab Finance": "Bank Charges",
    "Gulf International Bank (GIB)": "Bank Charges",
    "Sultan Qaboos University": "Education",
    "Gulf College": "Education",
    "Caledonian College of Engineering": "Education",
    "Middle East College": "Education",
    "Majan University": "Education",
    "American International School of Muscat": "Education",
    "British School Muscat": "Education",
    "Indian School Muscat": "Education",
    "Pakistan School Muscat": "Education",
    "Muscat International School": "Education",
    "International Grammar School & Nursery": "Education",
    "Oman Medical College": "Education",
    "German University of Technology in Oman (GUtech)": "Education",
    "Shangri-La Barr Al Jissah": "Travel and Hotels",
    "The Chedi Muscat": "Travel and Hotels",
    "Grand Hyatt Muscat": "Travel and Hotels",
    "Crowne Plaza Muscat": "Travel and Hotels",
    "Radisson Blu": "Travel and Hotels",
    "Al Bustan Palace": "Travel and Hotels",
    "InterContinental Muscat": "Travel and Hotels",
    "Millennium Hotel Muscat": "Travel and Hotels",
    "City Seasons Hotel": "Travel and Hotels",
    "Novotel Muscat": "Travel and Hotels",
    "Savills Oman": "Rent Payments",
    "Al Madina Properties": "Rent Payments",
    "Royal City Rent": "Rent Payments",
    "Pearl Residency": "Rent Payments",
    "Muscat Hills Rent": "Rent Payments",
    "City Market Oman": "Groceries",
    "Right Price": "Groceries",
    "Food Basket": "Groceries",
    "Meera Express": "Groceries",
    "Express by Lulu": "Groceries",
    "Grand Khan Supermarket": "Groceries",
    "Muscat Coop Society": "Groceries",
    "Splash Oman": "Shopping & Retail",
    "REDTAG": "Shopping & Retail",
    "ZARA": "Shopping & Retail",
    "Bershka": "Shopping & Retail",
    "Mango": "Shopping & Retail",
    "Pull and Bear": "Shopping & Retail",
    "Mothercare": "Shopping & Retail",
    "Timberland": "Shopping & Retail",
    "Levi's": "Shopping & Retail",
    "Tommy Hilfiger": "Shopping & Retail",
    "Skechers": "Shopping & Retail",
    "Majan Electricity": "Housing and Utilities",
    "Diam Water": "Housing and Utilities",
    "Muscat Municipality Water": "Housing and Utilities",
    "OPWP": "Housing and Utilities",
    "Be'ah Oman": "Housing and Utilities",
    "Suhar Fuel Station": "Fuel and Transport",
    "PDO Car Wash": "Fuel and Transport",
    "Airport Taxi Muscat": "Fuel and Transport",
    "SalamAir": "Travel and Hotels",
    "Booking.com": "Travel and Hotels",
    "Hilton Muscat": "Travel and Hotels",
    "OAB": "Bank Charges",
    "AXA Oman": "Insurance",
    "Dhofar Insurance": "Insurance",
    "ROP Visa Department": "Government Services",
    "Civil Aviation Authority": "Government Services",
    "Municipality Muscat": "Government Services",
    "MOM Licensing": "Government Services",
    "TRA Oman": "Government Services",
    "Dar Al Atta'a": "Charity Donations",
    "Oman Diabetes Association": "Charity Donations",
    "Sultan Qaboos Fund": "Charity Donations",
    "Talabat Oman": "Other / Uncategorized",
    "Netflix MENA": "Other / Uncategorized",
    "OSN Oman": "Other / Uncategorized",
    "MidLand Developers": "Other / Uncategorized",
    "Mazoon Dairy": "Dining and Cafes",
    "Golden Sands Leasing": "Rent Payments",
    "Sunrise Apartments": "Rent Payments",
    "Royal Vista Rentals": "Rent Payments",
    "Emerald Bay Homes": "Rent Payments",
    "Pearl Coast Residence": "Rent Payments",
    "Green Mart Express": "Groceries",
    "Oasis Convenience Store": "Groceries",
    "Daily Fresh Market": "Groceries",
    "QuickPick Grocery": "Groceries",
    "Urban Outfitters Oman": "Shopping & Retail",
    "Guess Oman": "Shopping & Retail",
    "Calvin Klein Oman": "Shopping & Retail",
    "Superdry Oman": "Shopping & Retail",
    "GAP Oman": "Shopping & Retail",
    "Oman Sewage Board": "Housing and Utilities",
    "Green Energy Oman": "Housing and Utilities",
    "QuickFuel Station": "Fuel and Transport",
    "EcoFuel Oman": "Fuel and Transport",
    "Express Taxi Co.": "Fuel and Transport",
    "Urban Brew Cafe": "Dining and Cafes",
    "Harvest Bistro": "Dining and Cafes",
    "Luna Ristorante": "Dining and Cafes",
    "Sea Breeze Grill": "Dining and Cafes",
    "Spice Route": "Dining and Cafes",
    "CarePlus Clinic": "Medical and Health",
    "Wellbeing Center": "Medical and Health",
    "LifeLine Diagnostics": "Medical and Health",
    "Knowledge Haven Academy": "Education",
    "SkillUp Institute": "Education",
    "Bright Future Prep": "Education",
    "Excel Language Center": "Education",
    "STEM Hub Muscat": "Education",
    "Birdlife Conservation Oman": "Charity Donations",
    "Water Aid Oman": "Charity Donations",
    "Food for All Oman": "Charity Donations",
    "Child Education Fund": "Charity Donations",
    "Medical Aid Society": "Charity Donations",
    "TechConnect Oman": "Other / Uncategorized",
    "SmartCity Exhibition": "Other / Uncategorized",
    "GadgetWorld Oman": "Other / Uncategorized",
    "Artisan Craft Bazaar": "Other / Uncategorized",
    "EcoFest Oman": "Other / Uncategorized",
    # Canadian out-of-sample merchants
    "Tim Hortons": "Dining and Cafes",
    "Loblaws": "Groceries",
    "Shoppers Drug Mart": "Medical and Health",
    "Canadian Tire": "Shopping & Retail",
    "Rogers Wireless": "Telecom",
    "TTC Toronto Transit": "Fuel and Transport",
    "TD Bank Canada": "Bank Charges",
    "RBC Royal Bank": "Bank Charges",
    "Cineplex Odeon": "Entertainment and Leisure",
    "Air Canada": "Travel and Hotels",
    "Intact Insurance Canada": "Insurance",
    "Wealthsimple Invest": "Savings and Investments",
    "Second Cup": "Dining and Cafes",
    "No Frills": "Groceries",
    "Sport Chek": "Shopping & Retail",
    "Bell Mobility": "Telecom",
    "Petro-Canada": "Fuel and Transport",
    "CIBC Canada": "Bank Charges",
    "Scotiabank Canada": "Bank Charges",
    "GO Transit": "Fuel and Transport",
    "Presto Card": "Fuel and Transport",
    "Harvey's": "Dining and Cafes",
    "Swiss Chalet": "Dining and Cafes",
    "Metro Ontario": "Groceries",
    "WestJet": "Travel and Hotels",
    "Koodo Mobile": "Telecom",
    "Freedom Mobile": "Telecom",
    "Hydro One": "Housing and Utilities",
    "Toronto Hydro": "Housing and Utilities",
    "Enbridge Gas": "Housing and Utilities",
}


def generate_unlabeled_transaction():
    merchant = random.choice(list(test_merchant_category_map.keys()))
    city = random.choice(locations)
    card_suffix = str(random.randint(1000, 9999))

    formats = [
        f"RECEIPT {merchant.upper()} {city.upper()}",
        f"TRF TO {merchant.upper()}",
        f"{merchant.upper()} PAYMENT",
        f"POS PURCHASE {merchant.upper()} {fake.date('%b')} {random.randint(1, 28)}",
        f"{merchant.lower()} {random.choice(['debit', 'crd', 'payment', 'trsf'])}",
        f"txn {merchant.upper()}",
        f"{merchant.upper()} CARD*{card_suffix}",
        f"INTERAC {merchant.upper()} {city.upper()}",
        f"VISA DEBIT {merchant.upper()} {city[:3].upper()}",
    ]

    description = random.choice(formats)
    category = test_merchant_category_map[merchant]
    low, high = amount_ranges.get(category, (1, 500))
    amount = round(random.uniform(low, high), 2) * -1

    date = fake.date_between(start_date='-6M', end_date='today')

    return {
        "description": description,
        "amount": amount,
        "date": date
    }


for i in range(1, 4):
    df_test = pd.DataFrame([generate_unlabeled_transaction() for _ in range(10000)])
    test_path = os.path.join(output_dir, f"test_transactions_{i}.csv")
    df_test.to_csv(test_path, index=False)
    print(f"Saved test file: {test_path}")