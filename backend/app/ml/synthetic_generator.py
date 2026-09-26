import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Ground-truth synthetic cybercrime hubs & ATM clusters across India
SYNTHETIC_CLUSTERS = [
    {
        "cluster_id": "OD-BBSR-27",
        "cluster_name": "Bhubaneswar — ATM Cluster #27",
        "locality": "Chandrasekharpur / Patia Tech Corridor",
        "district": "Khordha",
        "state": "Odisha",
        "lat": 20.3168,
        "lng": 85.8234,
        "base_risk": 92,
        "atms_count": 14,
        "primary_crime": "UPI Fraud",
        "peak_window": "20:00–23:00",
        "banks": ["State Bank of India", "HDFC Bank", "ICICI Bank", "Punjab National Bank", "Axis Bank"],
        "lea_station": "Chandrasekharpur Cyber Police Station, Bhubaneswar-Cuttack Police Commissionerate",
        "jurisdiction_lea": "Khordha District Cyber Cell / Odisha CID-CB",
        "mule_network": "Eastern Coastal Mule Syndicate (M-OD-44)"
    },
    {
        "cluster_id": "JH-JMT-09",
        "cluster_name": "Jamtara-Deoghar Cyber Cashout Corridor",
        "locality": "Main Market Road & Station Chowk",
        "district": "Jamtara",
        "state": "Jharkhand",
        "lat": 23.9632,
        "lng": 86.8014,
        "base_risk": 88,
        "atms_count": 11,
        "primary_crime": "Phishing & KYC Fraud",
        "peak_window": "19:00–22:00",
        "banks": ["State Bank of India", "Bank of India", "Canara Bank", "Union Bank"],
        "lea_station": "Jamtara Cyber Crime Police Station",
        "jurisdiction_lea": "Jamtara District Police / Jharkhand CID Cyber Cell",
        "mule_network": "Tri-Border Phishing Ring (M-JH-12)"
    },
    {
        "cluster_id": "HR-MEW-14",
        "cluster_name": "Mewat-Alwar High-Risk Corridor",
        "locality": "Punhana Road & Tauru Junction",
        "district": "Nuh (Mewat)",
        "state": "Haryana",
        "lat": 28.1065,
        "lng": 77.0042,
        "base_risk": 89,
        "atms_count": 12,
        "primary_crime": "Sextortion & Marketplace Fraud",
        "peak_window": "21:00–00:00",
        "banks": ["Sarva Haryana Gramin Bank", "Punjab National Bank", "HDFC Bank", "SBI"],
        "lea_station": "Nuh Cyber Crime Police Station",
        "jurisdiction_lea": "Haryana Police Cyber Command / Nuh District",
        "mule_network": "Aravalli Fraud Operations (M-HR-07)"
    },
    {
        "cluster_id": "GJ-SRT-05",
        "cluster_name": "Surat Diamond City Mule Nexus",
        "locality": "Varachha & Katargam Financial Belt",
        "district": "Surat",
        "state": "Gujarat",
        "lat": 21.2064,
        "lng": 72.8485,
        "base_risk": 85,
        "atms_count": 18,
        "primary_crime": "Investment & Task Scams",
        "peak_window": "18:00–21:00",
        "banks": ["ICICI Bank", "Kotak Mahindra Bank", "Bank of Baroda", "HDFC Bank"],
        "lea_station": "Surat City Cyber Crime Police Station",
        "jurisdiction_lea": "Surat City Police / Gujarat CID Crime",
        "mule_network": "Western Commercial Mule Layer (M-GJ-31)"
    },
    {
        "cluster_id": "TG-CYB-03",
        "cluster_name": "Cyberabad IT Corridor Gateway",
        "locality": "Madhapur / Gachibowli Junction",
        "district": "Hyderabad",
        "state": "Telangana",
        "lat": 17.4416,
        "lng": 78.3846,
        "base_risk": 78,
        "atms_count": 22,
        "primary_crime": "Part-Time Job & Crypto Fraud",
        "peak_window": "20:00–23:00",
        "banks": ["State Bank of India", "HDFC Bank", "Axis Bank", "Standard Chartered"],
        "lea_station": "Cyberabad Cyber Crime Police Station, Gachibowli",
        "jurisdiction_lea": "Cyberabad Police Commissionerate / TG Cyber Security Bureau (TGCSB)",
        "mule_network": "Deccan Tech Mule Conduit (M-TG-19)"
    },
    {
        "cluster_id": "DL-NCR-11",
        "cluster_name": "East Delhi-Noida Transit Belt",
        "locality": "Laxmi Nagar & Anand Vihar Inter-State Hub",
        "district": "East Delhi",
        "state": "Delhi",
        "lat": 28.6312,
        "lng": 77.2798,
        "base_risk": 82,
        "atms_count": 25,
        "primary_crime": "Digital Arrest & Impersonation",
        "peak_window": "19:00–22:00",
        "banks": ["Punjab National Bank", "SBI", "Canara Bank", "Federal Bank"],
        "lea_station": "Delhi Police Cyber Cell (IFSO), Special Cell",
        "jurisdiction_lea": "Delhi Police Cyber Operations / Special Cell",
        "mule_network": "Capital Transit Cashout Ring (M-DL-82)"
    },
    {
        "cluster_id": "KA-BLR-08",
        "cluster_name": "Bengaluru South Financial Hub",
        "locality": "Electronic City Phase 1 & Hosur Road",
        "district": "Bengaluru Urban",
        "state": "Karnataka",
        "lat": 12.8452,
        "lng": 77.6602,
        "base_risk": 74,
        "atms_count": 16,
        "primary_crime": "Loan App & Extortion",
        "peak_window": "17:00–20:00",
        "banks": ["Canara Bank", "State Bank of India", "ICICI Bank", "Kotak Bank"],
        "lea_station": "Bengaluru CEN Crime Police Station (South Division)",
        "jurisdiction_lea": "CID Karnataka Cyber Wing / Bengaluru City Police",
        "mule_network": "Southern Tech Corridor Mules (M-KA-15)"
    },
    {
        "cluster_id": "WB-KOL-17",
        "cluster_name": "Kolkata Salt Lake Sector V Ring",
        "locality": "Sector V & Karunamoyee Hub",
        "district": "North 24 Parganas",
        "state": "West Bengal",
        "lat": 22.5804,
        "lng": 88.4312,
        "base_risk": 79,
        "atms_count": 15,
        "primary_crime": "Tech Support Scam",
        "peak_window": "21:00–00:00",
        "banks": ["State Bank of India", "UCO Bank", "Bandhan Bank", "HDFC Bank"],
        "lea_station": "Bidhannagar Cyber Crime Police Station",
        "jurisdiction_lea": "Bidhannagar Police Commissionerate / West Bengal CID",
        "mule_network": "Eastern Delta Tech Syndicate (M-WB-23)"
    },
    {
        "cluster_id": "MH-THN-04",
        "cluster_name": "Thane-Navi Mumbai Cashout Axis",
        "locality": "Vashi Sector 17 & Turbhe Commercial Zone",
        "district": "Thane",
        "state": "Maharashtra",
        "lat": 19.0760,
        "lng": 72.9986,
        "base_risk": 81,
        "atms_count": 20,
        "primary_crime": "OTP Bypass & SIM Swap",
        "peak_window": "20:00–23:00",
        "banks": ["Bank of Maharashtra", "HDFC Bank", "Axis Bank", "IDBI Bank"],
        "lea_station": "Navi Mumbai Cyber Crime Police Station, CBD Belapur",
        "jurisdiction_lea": "Maharashtra State Cyber / Navi Mumbai Police",
        "mule_network": "Konkan Financial Mule Network (M-MH-55)"
    },
    {
        "cluster_id": "BR-PAT-06",
        "cluster_name": "Patna Kankarbagh Withdrawal Belt",
        "locality": "Kankarbagh Main Road & Old Bypass",
        "district": "Patna",
        "state": "Bihar",
        "lat": 25.5941,
        "lng": 85.1588,
        "base_risk": 76,
        "atms_count": 14,
        "primary_crime": "Lottery & Reward Points Scam",
        "peak_window": "18:00–21:00",
        "banks": ["Punjab National Bank", "State Bank of India", "Central Bank of India"],
        "lea_station": "Patna Cyber Crime Police Station, Gandhi Maidan",
        "jurisdiction_lea": "Bihar Police Cyber Cell / Economic Offences Unit (EOU)",
        "mule_network": "Gangetic Plain Mule Network (M-BR-09)"
    },
    {
        "cluster_id": "UP-LKO-12",
        "cluster_name": "Lucknow Gomti Nagar Financial Node",
        "locality": "Vibhuti Khand & Patrakarpuram",
        "district": "Lucknow",
        "state": "Uttar Pradesh",
        "lat": 26.8524,
        "lng": 80.9984,
        "base_risk": 77,
        "atms_count": 17,
        "primary_crime": "Investment & Crypto Fraud",
        "peak_window": "19:00–22:00",
        "banks": ["Bank of Baroda", "State Bank of India", "HDFC Bank", "ICICI Bank"],
        "lea_station": "Lucknow Cyber Crime Police Station, Hazratganj",
        "jurisdiction_lea": "UP Police Cyber Crime Headquarters / Lucknow Commissionerate",
        "mule_network": "Awadh Cyber Mules (M-UP-62)"
    },
    {
        "cluster_id": "RJ-JAI-15",
        "cluster_name": "Jaipur Mansarovar ATM Cluster",
        "locality": "Madhyam Marg & New Sanganer Road",
        "district": "Jaipur",
        "state": "Rajasthan",
        "lat": 26.8568,
        "lng": 75.7681,
        "base_risk": 73,
        "atms_count": 13,
        "primary_crime": "Online Gaming & Betting Scam",
        "peak_window": "20:00–23:00",
        "banks": ["State Bank of India", "Punjab National Bank", "HDFC Bank", "Canara Bank"],
        "lea_station": "Jaipur Cyber Police Station, Police Commissionerate",
        "jurisdiction_lea": "Rajasthan Police Special Operations Group (SOG) Cyber",
        "mule_network": "Thar Mule Syndicate (M-RJ-41)"
    }
]

CRIME_CATEGORIES = [
    "UPI Fraud",
    "Phishing & KYC Fraud",
    "Investment & Task Scams",
    "OTP Bypass & SIM Swap",
    "Digital Arrest & Impersonation",
    "Part-Time Job Scam",
    "Loan App Extortion",
    "Online Marketplace Fraud"
]

BANKS = [
    "State Bank of India", "HDFC Bank", "ICICI Bank", "Punjab National Bank",
    "Bank of Baroda", "Axis Bank", "Canara Bank", "Union Bank of India", "Kotak Mahindra Bank"
]

FIRST_NAMES = ["Amit", "Rahul", "Pooja", "Vikram", "Sneha", "Rajesh", "Priya", "Sunil", "Ananya", "Deepak", "Meera", "Karan", "Rohan", "Suresh", "Kavita", "Abhishek"]
LAST_NAMES = ["Sharma", "Verma", "Patel", "Nayak", "Singh", "Das", "Rao", "Mishra", "Joshi", "Mohanty", "Gupta", "Chatterjee", "Kulkarni", "Reddy", "Mehta", "Yadav"]

def generate_masked_mobile():
    prefix = random.choice(["98", "97", "94", "88", "79", "99", "81", "90"])
    suffix = str(random.randint(1000, 9999))
    return f"+91 {prefix}XXXX{suffix}"

def generate_masked_account(bank_name):
    bank_code = "".join([w[0] for w in bank_name.split()[:2]]).upper() + "B"
    suffix = str(random.randint(1000, 9999))
    return f"{bank_code}XXXXXX{suffix}"

def generate_synthetic_dataset(num_complaints: int = 5200) -> Dict[str, Any]:
    """
    Generates a rich, realistic synthetic cybercrime dataset structured for
    demonstration of National Cybercrime Reporting Portal (NCRP) complaints,
    ATM clusters, mule accounts, and 24-hour predictive cash withdrawal hotspots.
    """
    random.seed(42)  # Deterministic seed for reproducible evaluation metrics
    complaints = []
    atms = []
    
    # 1. Generate ATM nodes per cluster
    for cluster in SYNTHETIC_CLUSTERS:
        for idx in range(cluster["atms_count"]):
            # Slight random offset around cluster centroid (~200m to 800m)
            lat_offset = (random.random() - 0.5) * 0.012
            lng_offset = (random.random() - 0.5) * 0.012
            bank = random.choice(cluster["banks"])
            atm_id = f"ATM-{cluster['cluster_id']}-{idx+1:02d}"
            
            atms.append({
                "id": atm_id,
                "name": f"{bank} ATM #{idx+1} — {cluster['locality'].split('/')[0].strip()}",
                "bank": bank,
                "lat": round(cluster["lat"] + lat_offset, 5),
                "lng": round(cluster["lng"] + lng_offset, 5),
                "cluster_id": cluster["cluster_id"],
                "cluster_name": cluster["cluster_name"],
                "district": cluster["district"],
                "state": cluster["state"],
                "historical_withdrawal_volume": round(random.uniform(8.5, 45.0), 2),
                "surveillance_rating": random.choice(["High", "Medium", "High", "Low"]),
                "is_active": True
            })

    # 2. Generate complaints with realistic spatial/temporal clustering
    base_time = datetime.now() - timedelta(days=7)
    
    for i in range(num_complaints):
        # 65% of complaints correlate with known high-risk clusters, 35% scattered across districts
        is_cluster_correlated = random.random() < 0.65
        
        if is_cluster_correlated:
            target_cluster = random.choice(SYNTHETIC_CLUSTERS)
            # Weights favoring Bhubaneswar (OD-BBSR-27) for the primary demo storyline
            if random.random() < 0.28:
                target_cluster = SYNTHETIC_CLUSTERS[0]  # Bhubaneswar
            
            lat = target_cluster["lat"] + (random.random() - 0.5) * 0.03
            lng = target_cluster["lng"] + (random.random() - 0.5) * 0.03
            state = target_cluster["state"]
            district = target_cluster["district"]
            crime_cat = target_cluster["primary_crime"] if random.random() < 0.7 else random.choice(CRIME_CATEGORIES)
            cluster_id = target_cluster["cluster_id"]
        else:
            target_cluster = random.choice(SYNTHETIC_CLUSTERS)
            lat = target_cluster["lat"] + (random.random() - 0.5) * 0.15
            lng = target_cluster["lng"] + (random.random() - 0.5) * 0.15
            state = target_cluster["state"]
            district = target_cluster["district"]
            crime_cat = random.choice(CRIME_CATEGORIES)
            cluster_id = None

        # Temporal generation with realistic evening surge
        hour_weights = [1, 1, 1, 1, 1, 2, 3, 4, 6, 7, 8, 8, 8, 8, 9, 9, 10, 11, 13, 16, 18, 15, 12, 6]
        hour = random.choices(range(24), weights=hour_weights, k=1)[0]
        minute = random.randint(0, 59)
        day_offset = random.uniform(0, 7)
        timestamp = base_time + timedelta(days=day_offset, hours=hour, minutes=minute)

        # Loss amount distributions: typical cyber fraud amounts in INR
        if crime_cat in ["Investment & Task Scams", "Digital Arrest & Impersonation"]:
            loss_amount = round(random.uniform(75000, 1850000), 2)
        elif crime_cat == "UPI Fraud":
            loss_amount = round(random.uniform(12000, 195000), 2)
        else:
            loss_amount = round(random.uniform(5000, 95000), 2)

        v_bank = random.choice(BANKS)
        b_bank = random.choice(BANKS)
        
        # Risk classification
        if loss_amount > 200000 or cluster_id == "OD-BBSR-27":
            risk_level = "CRITICAL" if random.random() < 0.65 else "HIGH"
        elif loss_amount > 50000:
            risk_level = "HIGH" if random.random() < 0.7 else "MEDIUM"
        else:
            risk_level = "MEDIUM" if random.random() < 0.6 else "LOW"

        status_pool = ["Reported", "Layer_1_Frozen", "Pending_Investigation", "Action_Initiated"]
        status = random.choices(status_pool, weights=[0.45, 0.25, 0.20, 0.10], k=1)[0]

        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)

        complaints.append({
            "id": f"NCRP-2026-{100000 + i}",
            "case_reference": f"CYB-2026-{4000 + (i % 890):04d}",
            "complaint_timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "crime_category": crime_cat,
            "victim_name": f"{first} {last[0]}.",
            "victim_mobile": generate_masked_mobile(),
            "victim_account": generate_masked_account(v_bank),
            "victim_bank": v_bank,
            "loss_amount": loss_amount,
            "beneficiary_account": generate_masked_account(b_bank),
            "beneficiary_bank": b_bank,
            "beneficiary_upi": f"pay.mule{random.randint(100,999)}@{b_bank.split()[0].lower()}",
            "state": state,
            "district": district,
            "lat": round(lat, 5),
            "lng": round(lng, 5),
            "risk_level": risk_level,
            "status": status,
            "nearest_predicted_hotspot_id": cluster_id
        })

    return {
        "clusters": SYNTHETIC_CLUSTERS,
        "atms": atms,
        "complaints": complaints
    }
