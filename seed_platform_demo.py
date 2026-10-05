import os
import sys
import random
from datetime import datetime, timedelta

base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from app.db.session import init_db, get_session_factory
from app.db.models import (
    UserModel,
    ComplaintModel,
    ComplaintStatusHistoryModel,
    Base
)
from app.services.auth_service import AuthService
from app.services.complaint_service import ComplaintService
from app.schemas.auth import CitizenRegisterRequest, AuthorityRegisterRequest
from app.schemas.complaint_dto import ComplaintCreateRequest

# 50 realistic Indian citizen profiles
CITIZEN_PROFILES = [
    ("Anita Roy", "anita.roy@gmail.com", "9820112233", "Andheri West"),
    ("Nikhil Deshmukh", "nikhil.d@gmail.com", "9820223344", "Andheri West"),
    ("Priya Nair", "priya.nair@outlook.com", "9820334455", "Dadar East"),
    ("Vikram Sethi", "vikram.sethi@yahoo.com", "9820445566", "Dadar West"),
    ("Kavita Rao", "kavita.rao@gmail.com", "9820556677", "Bandra West"),
    ("Arun Kumar", "arun.k@rediffmail.com", "9820667788", "Bandra East"),
    ("Sneha Patil", "sneha.patil@gmail.com", "9820778899", "Kurla West"),
    ("Rohan Mehta", "rohan.mehta@gmail.com", "9820889900", "Kurla East"),
    ("Deepak Sharma", "deepak.s@yahoo.co.in", "9830112233", "Malad West"),
    ("Sunita Kulkarni", "sunita.k@gmail.com", "9830223344", "Malad East"),
    ("Rajesh Iyer", "rajesh.iyer@gmail.com", "9830334455", "Borivali West"),
    ("Meera Joshi", "meera.joshi@gmail.com", "9830445566", "Borivali East"),
    ("Amitabh Sen", "amitabh.sen@hotmail.com", "9830556677", "Ghatkopar West"),
    ("Pooja Hegde", "pooja.h@gmail.com", "9830667788", "Ghatkopar East"),
    ("Gaurav Kapoor", "gaurav.k@gmail.com", "9830778899", "Vile Parle West"),
    ("Ananya Mishra", "ananya.m@gmail.com", "9830889900", "Vile Parle East"),
    ("Sanjay Verma", "sanjay.verma@gmail.com", "9840112233", "Santacruz West"),
    ("Divya Menon", "divya.menon@gmail.com", "9840223344", "Santacruz East"),
    ("Karan Chawla", "karan.c@gmail.com", "9840334455", "Chembur"),
    ("Ritu Saxena", "ritu.saxena@gmail.com", "9840445566", "Chembur East"),
    ("Manoj Tiwari", "manoj.tiwari@gmail.com", "9840556677", "Sion"),
    ("Shilpa Shetty", "shilpa.s@gmail.com", "9840667788", "Matunga"),
    ("Vivek Agarwal", "vivek.a@gmail.com", "9840778899", "Wadala"),
    ("Neha Gupta", "neha.gupta@gmail.com", "9840889900", "Parel"),
    ("Siddharth Roy", "siddharth.r@gmail.com", "9850112233", "Lower Parel"),
    ("Aarti Chauhan", "aarti.c@gmail.com", "9850223344", "Worli"),
    ("Prashant Shinde", "prashant.s@gmail.com", "9850334455", "Prabhadevi"),
    ("Tanvi Bhatt", "tanvi.bhatt@gmail.com", "9850445566", "Mahim"),
    ("Abhishek Pandey", "abhishek.p@gmail.com", "9850556677", "Colaba"),
    ("Swati Reddy", "swati.reddy@gmail.com", "9850667788", "Fort"),
    ("Harish Pillai", "harish.p@gmail.com", "9850778899", "Marine Lines"),
    ("Madhuri Dixit", "madhuri.d@gmail.com", "9850889900", "Churchgate"),
    ("Alok Nath", "alok.nath@gmail.com", "9860112233", "Byculla"),
    ("Farhan Khan", "farhan.k@gmail.com", "9860223344", "Nagpada"),
    ("Zoya Akhtar", "zoya.a@gmail.com", "9860334455", "Mazgaon"),
    ("Ashwin Dave", "ashwin.d@gmail.com", "9860445566", "Girgaon"),
    ("Shruti Hassan", "shruti.h@gmail.com", "9860556677", "Kandivali West"),
    ("Varun Dhawan", "varun.d@gmail.com", "9860667788", "Kandivali East"),
    ("Tara Sutaria", "tara.s@gmail.com", "9860778899", "Dahisar West"),
    ("Aditya Roy", "aditya.roy@gmail.com", "9860889900", "Dahisar East"),
    ("Juhi Chawla", "juhi.c@gmail.com", "9870112233", "Mulund West"),
    ("Sunil Shetty", "sunil.s@gmail.com", "9870223344", "Mulund East"),
    ("Kiran Rao", "kiran.rao@gmail.com", "9870334455", "Powai"),
    ("Chetan Bhagat", "chetan.b@gmail.com", "9870445566", "Hiranandani Powai"),
    ("Citizen Demo", "citizen@example.com", "9876543210", "Andheri West")
]

# 5 Authority profiles
AUTHORITY_PROFILES = [
    {
        "name": "Rajesh Verma",
        "designation": "Executive Engineer - Road Infrastructure",
        "department": "Public Works Department",
        "employeeId": "PWD-1092",
        "email": "authority@gov.in",
        "phone": "9811001100",
        "password": "password123"
    },
    {
        "name": "Dr. Sunita Rao",
        "designation": "Chief Health & Sanitation Officer",
        "department": "Sanitation",
        "employeeId": "SAN-8832",
        "email": "sanitation@gov.in",
        "phone": "9811002200",
        "password": "password123"
    },
    {
        "name": "Er. Arvind Joshi",
        "designation": "Superintending Water Supply Engineer",
        "department": "Water Supply",
        "employeeId": "WAT-4419",
        "email": "water@gov.in",
        "phone": "9811003300",
        "password": "password123"
    },
    {
        "name": "Mahesh Patil",
        "designation": "Deputy Chief Electrical Inspector",
        "department": "Electricity",
        "employeeId": "ELE-7721",
        "email": "electricity@gov.in",
        "phone": "9811004400",
        "password": "password123"
    },
    {
        "name": "Smt. Leela Nair",
        "designation": "Ward 12 Municipal Commissioner",
        "department": "Municipal Corporation",
        "employeeId": "MC-0012",
        "email": "admin@gov.in",
        "phone": "9811005500",
        "password": "password123"
    }
]

# 55 Realistic complaints with semantic duplicate clusters
COMPLAINT_TEMPLATES = [
    # Cluster A: MG Road Junction Potholes (Roads)
    ("roads", "Massive deep pothole at MG Road junction near metro pillar 42 causing 2-wheelers to fall.", "MG Road Junction", "Ward 12", "Metro Pillar 42", "urgent", 19.1136, 72.8697, 2, "IN_PROGRESS"),
    ("roads", "Severe pothole at MG Road traffic signal, cars getting stuck and damaging tires.", "MG Road Junction", "Ward 12", "MG Road Signal", "high", 19.1138, 72.8699, 3, "ASSIGNED"),
    ("roads", "Water-filled dangerous pothole on MG Road near city hospital, huge traffic blockage.", "MG Road Junction", "Ward 12", "City Hospital", "high", 19.1137, 72.8696, 4, "SUBMITTED"),
    ("roads", "Road surface completely caved in at MG Road junction, accident hazard.", "MG Road Junction", "Ward 12", "Opposite Bank of Baroda", "urgent", 19.1139, 72.8700, 1, "IN_PROGRESS"),
    ("roads", "Pothole on MG Road fixed poorly last week has opened up again with rain.", "MG Road Junction", "Ward 12", "Metro Pillar 43", "medium", 19.1135, 72.8695, 5, "SUBMITTED"),

    # Cluster B: Station Road Waste & Sanitation
    ("garbage", "Overflowing garbage dumpster outside Dadar Station West, rotting waste on main road.", "Station Road", "Ward 8", "Dadar Station Gate 2", "high", 19.1190, 72.8465, 3, "IN_PROGRESS"),
    ("garbage", "Trash not cleared for 4 days outside railway station market, terrible foul smell.", "Station Road", "Ward 8", "Vegetable Market", "high", 19.1192, 72.8468, 4, "ASSIGNED"),
    ("garbage", "Stray dogs and cattle scattering garbage from open bin on station approach road.", "Station Road", "Ward 8", "Station Approach", "medium", 19.1191, 72.8466, 6, "SUBMITTED"),
    ("garbage", "Commercial waste dumped on footpath near station bridge, pedestrians forced onto road.", "Station Road", "Ward 8", "Foot overbridge", "medium", 19.1189, 72.8463, 7, "RESOLVED"),
    ("garbage", "Open garbage dump attracting flies and mosquitoes near station tea stalls.", "Station Road", "Ward 8", "Tea Stall Corner", "low", 19.1193, 72.8470, 8, "RESOLVED"),

    # Cluster C: Sector 12 Pipeline Leakage & Low Pressure (Water)
    ("water", "Major underground water pipeline burst near Sector 12 park, clean water flooding road.", "Sector 12 Housing", "Ward 15", "Community Park Gate", "urgent", 19.1250, 72.8520, 2, "IN_PROGRESS"),
    ("water", "Drinking water supply has zero pressure on 3rd floor in Sector 12 apartments.", "Sector 12 Housing", "Ward 15", "Building A-4", "high", 19.1253, 72.8522, 5, "ASSIGNED"),
    ("water", "Contaminated brownish water coming from municipal tap in Sector 12 since yesterday.", "Sector 12 Housing", "Ward 15", "Sector 12 Market", "urgent", 19.1251, 72.8521, 1, "IN_PROGRESS"),
    ("water", "Pipeline leaking at valve junction near community hall, thousands of liters wasted.", "Sector 12 Housing", "Ward 15", "Community Hall", "medium", 19.1254, 72.8524, 7, "SUBMITTED"),
    ("water", "No water supply for last 36 hours in Sector 12 Block B without prior notice.", "Sector 12 Housing", "Ward 15", "Block B", "high", 19.1249, 72.8519, 3, "RESOLVED"),

    # Cluster D: Nehru Park Streetlights (Electricity)
    ("electricity", "All streetlights dark on Nehru Park outer perimeter road, unsafe for women walking at night.", "Nehru Park Outer", "Ward 4", "Main Gate 1", "high", 19.1080, 72.8610, 4, "IN_PROGRESS"),
    ("electricity", "Street pole light sparking during evening rain near Nehru Park children play area.", "Nehru Park Outer", "Ward 4", "Play Area", "urgent", 19.1082, 72.8613, 2, "ASSIGNED"),
    ("electricity", "3 consecutive sodium streetlights flickering continuously on park perimeter.", "Nehru Park Outer", "Ward 4", "Pole #24", "low", 19.1081, 72.8611, 8, "RESOLVED"),
    ("electricity", "Open live wire hanging from electric junction box on Nehru Park footpath.", "Nehru Park Outer", "Ward 4", "Near Bus Stop", "urgent", 19.1079, 72.8608, 1, "IN_PROGRESS"),

    # Cluster E: Bandra West Drainage & Waterlogging
    ("drainage", "Stormwater drain completely blocked with plastic waste causing knee-deep waterlogging.", "Hill Road", "Ward 9", "Near St. Joseph Church", "urgent", 19.0558, 72.8340, 3, "IN_PROGRESS"),
    ("drainage", "Sewage backflow into residential ground floor compounds on Hill Road.", "Hill Road", "Ward 9", "Society Complex", "high", 19.0560, 72.8342, 5, "ASSIGNED"),
    ("drainage", "Broken manhole cover on Hill Road, high danger for pedestrians in evening darkness.", "Hill Road", "Ward 9", "Opposite Bakery", "urgent", 19.0556, 72.8338, 2, "RESOLVED"),
    ("drainage", "Foul sewer gas leaking from open drain near market crossing.", "Hill Road", "Ward 9", "Crossing #3", "medium", 19.0562, 72.8345, 9, "RESOLVED"),

    # Varied standalone grievances across other categories and areas
    ("property", "Broken boundary railing and damaged public bench at Sea Face Promenade.", "Worli Sea Face", "Ward 10", "Promenade Point 4", "low", 19.0166, 72.8150, 12, "RESOLVED"),
    ("property", "Bus shelter glass roof shattered by falling tree branch on SV Road.", "SV Road", "Ward 14", "Khar Bus Stop", "medium", 19.0700, 72.8360, 10, "ASSIGNED"),
    ("property", "Public toilet door broken and water tap missing near municipal garden.", "Shivaji Park", "Ward 7", "Garden Corner", "medium", 19.0270, 72.8380, 14, "RESOLVED"),
    ("animals", "Pack of aggressive stray dogs barking and chasing bikes near School Road.", "Parel Village", "Ward 6", "Municipal School #2", "high", 19.0010, 72.8420, 6, "IN_PROGRESS"),
    ("animals", "Stray cattle sitting in middle of busy 4-lane junction causing traffic snarls.", "Kurla Junction", "Ward 11", "CST Road Crossing", "medium", 19.0720, 72.8790, 8, "ASSIGNED"),
    ("animals", "Injured stray dog lying near railway ticket counter needing immediate medical care.", "Ghatkopar Station", "Ward 13", "East Ticket Window", "high", 19.0860, 72.9080, 3, "RESOLVED"),
    ("noise", "Loud construction work happening at 2:00 AM violating city noise pollution curfew.", "Lokhandwala Complex", "Ward 12", "Building 45 Site", "medium", 19.1410, 72.8280, 4, "RESOLVED"),
    ("noise", "Commercial generator running on open footpath with excessive diesel smoke and vibration.", "Linking Road", "Ward 9", "Shopping Plaza", "medium", 19.0620, 72.8340, 11, "ASSIGNED"),
    ("other", "Overgrown tree branches touching 11KV overhead power wires.", "Chembur Colony", "Ward 16", "Sindhi Society", "high", 19.0520, 72.8890, 7, "IN_PROGRESS"),
    ("other", "Illegal banners and posters obscuring traffic warning signs at junction.", "Andheri East", "Ward 12", "Western Express Highway Exit", "low", 19.1190, 72.8590, 15, "RESOLVED"),
    ("roads", "Deep asphalt depression on flyover descending ramp causing vehicles to jump.", "Link Road Flyover", "Ward 14", "South Ramp", "high", 19.1350, 72.8360, 6, "ASSIGNED"),
    ("roads", "Road excavation done by telecom company left unfilled with loose gravel.", "JVLR Crossing", "Ward 12", "Seepz Gate 1", "medium", 19.1290, 72.8750, 13, "RESOLVED"),
    ("garbage", "Illegal debris dumping on open mangrove land behind residential colony.", "Charkop Sector 8", "Ward 17", "Mangrove Border", "urgent", 19.2150, 72.8250, 5, "IN_PROGRESS"),
    ("water", "Burst water meter splashing water into building electrical substation.", "Borivali IC Colony", "Ward 18", "Holy Cross Road", "urgent", 19.2450, 72.8520, 1, "IN_PROGRESS"),
    ("electricity", "High mast lighting at central junction dead for 2 weeks.", "Vikhroli East", "Ward 13", "Station Road Circle", "medium", 19.1090, 72.9290, 18, "RESOLVED"),
    ("drainage", "Drainage cover collapsed under truck weight near wholesale market.", "APMC Market Area", "Ward 20", "Truck Gate 4", "high", 19.0750, 73.0020, 9, "ASSIGNED"),
    ("roads", "Continuous pothole stretch of 200 meters outside international school.", "Powai Hiranandani", "Ward 15", "School Lane", "high", 19.1210, 72.9120, 8, "IN_PROGRESS"),
    ("garbage", "Plastic garbage choked in nullah preventing smooth water discharge.", "Malad Marve Road", "Ward 14", "Mithila Bridge", "urgent", 19.1850, 72.8280, 4, "ASSIGNED"),
    ("water", "Low pressure during morning 6 AM to 8 AM window in entire chawl area.", "Kurla Nehru Nagar", "Ward 11", "Chawl #14", "medium", 19.0620, 72.8810, 16, "RESOLVED"),
    ("electricity", "Substation transformer making loud buzzing sound and emitting smoke.", "Mulund West", "Ward 19", "LBS Marg Crossing", "urgent", 19.1720, 72.9420, 2, "IN_PROGRESS"),
    ("property", "Children playground swing broken with exposed sharp rusted iron edge.", "Colaba Woods Garden", "Ward 1", "Kids Play Area", "medium", 18.9120, 72.8190, 20, "RESOLVED"),
    ("animals", "Stray monkey entered residential high-rise balcony biting clothes.", "Bhandup West", "Ward 16", "Jungle Border Society", "medium", 19.1480, 72.9320, 11, "RESOLVED"),
    ("noise", "Loudspeaker continuous broadcast from unauthorized festival tent without permit.", "Mahim West", "Ward 9", "Fishermen Colony", "low", 19.0410, 72.8410, 13, "RESOLVED"),
    ("roads", "Loose iron grating on road drain causing loud clanking noise and tire punctures.", "Dadar TT Circle", "Ward 8", "Southbound Lane", "medium", 19.0190, 72.8450, 10, "IN_PROGRESS"),
    ("garbage", "Garbage collection truck not arriving on scheduled morning route in ward.", "Goregaon East", "Ward 12", "Aarey Road", "medium", 19.1650, 72.8620, 7, "ASSIGNED"),
    ("water", "Drinking water smells strongly of chlorine and causes burning sensation.", "Prabhadevi", "Ward 10", "Old Compound", "high", 19.0150, 72.8280, 5, "IN_PROGRESS"),
    ("electricity", "Streetlight timer misconfigured - lights stay ON during day and OFF at night.", "Vile Parle East", "Ward 12", "Nehru Road", "low", 19.0980, 72.8520, 22, "RESOLVED"),
    ("drainage", "Drain cleaning silt left on pedestrian sidewalk drying up and turning to toxic dust.", "Santacruz West", "Ward 9", "Tagore Road", "medium", 19.0820, 72.8360, 12, "RESOLVED")
]

def seed_demo():
    print("==========================================================")
    print("   SEEDING SEVA SETU: 50 USERS & REALISTIC GRIEVANCES     ")
    print("==========================================================")
    
    init_db()
    SessionFactory = get_session_factory()
    db = SessionFactory()

    auth_svc = AuthService(db)
    complaint_svc = ComplaintService(db)

    # 1. Register 5 Authority accounts
    print("\n[1/3] Seeding 5 Official Authority Accounts...")
    for a in AUTHORITY_PROFILES:
        existing = db.query(UserModel).filter(UserModel.email == a["email"]).first()
        if not existing:
            auth_svc.register_authority(AuthorityRegisterRequest(**a))
            print(f"  + Authority: {a['name']} ({a['email']}) - {a['department']}")
        else:
            print(f"  . Authority already exists: {a['email']}")

    # 2. Register 45 Citizen accounts
    print("\n[2/3] Seeding 45 Citizen Accounts...")
    created_citizens = []
    for name, email, phone, locality in CITIZEN_PROFILES:
        existing = db.query(UserModel).filter(UserModel.email == email).first()
        if not existing:
            auth_svc.register_citizen(CitizenRegisterRequest(
                name=name,
                email=email,
                password="password123"
            ))
            # update phone
            u = db.query(UserModel).filter(UserModel.email == email).first()
            if u:
                u.phone = phone
                db.commit()
            created_citizens.append((name, email, phone, locality))
        else:
            created_citizens.append((name, email, phone, locality))

    print(f"  Total Citizens seeded: {len(created_citizens)}")

    # 3. Seed 50+ diverse complaints through AI Duplicate Pipeline
    print("\n[3/3] Filing 50+ Real Complaints with AI Duplicate Engine Clustering...")
    total_filed = 0
    duplicate_count = 0

    now = datetime.utcnow()
    for idx, (cat, desc_text, loc, ward, landmark, priority, lat, lng, days_ago, target_status) in enumerate(COMPLAINT_TEMPLATES):
        # Pick citizen
        citizen_idx = idx % len(created_citizens)
        c_name, c_email, c_phone, _ = created_citizens[citizen_idx]

        req = ComplaintCreateRequest(
            category=cat,
            description=desc_text,
            locality=loc,
            ward=ward,
            landmark=landmark,
            priority=priority,
            latitude=lat,
            longitude=lng,
            is_anonymous=(idx % 7 == 0),
            full_name=c_name if (idx % 7 != 0) else None,
            phone=c_phone if (idx % 7 != 0) else None
        )

        user = db.query(UserModel).filter(UserModel.email == c_email).first()
        res = complaint_svc.create_complaint(req, current_user=user)
        total_filed += 1
        if res["is_duplicate"]:
            duplicate_count += 1

        # Adjust created_at timestamp to match simulated date history
        cid = res["complaint_id"]
        record = db.query(ComplaintModel).filter(ComplaintModel.complaint_id == cid).first()
        if record:
            simulated_date = now - timedelta(days=days_ago, hours=random.randint(1, 18), minutes=random.randint(0, 59))
            record.created_at = simulated_date
            record.timestamp = simulated_date

            # Update status to target status with status history
            if target_status != "SUBMITTED":
                record.status = target_status
                hist = ComplaintStatusHistoryModel(
                    complaint_id=cid,
                    old_status="SUBMITTED",
                    new_status=target_status,
                    changed_by="Rajesh Verma (Ward Officer)",
                    comment=f"Status set to {target_status} as per field inspection report",
                    timestamp=simulated_date + timedelta(hours=4)
                )
                db.add(hist)
            db.commit()

        print(f"  [{idx+1:02d}] {cid} | {cat:11} | {target_status:11} | {loc:22} | AI Match: {res['is_duplicate']}")

    db.close()
    print("\n==========================================================")
    print(f"   SEED COMPLETE: {len(AUTHORITY_PROFILES) + len(created_citizens)} Users | {total_filed} Complaints ({duplicate_count} Duplicates Linked)")
    print("   Demo Logins:")
    print("     - Authority: authority@gov.in  /  password123")
    print("     - Citizen:   citizen@example.com / password123")
    print("==========================================================")

if __name__ == '__main__':
    seed_demo()
