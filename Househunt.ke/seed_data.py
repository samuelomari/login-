"""
Seed data script for HouseHunt Kenya.
Populates realistic Kenyan rental properties, verified landlords/agents,
amenities, upfront moving cost items, inquiries, reviews, and anti-scam reports.
"""

import sqlite3
from werkzeug.security import generate_password_hash
from database import DB_FILE, get_db_connection, init_db


def seed():
    init_db(force=True)
    conn = get_db_connection()
    cur = conn.cursor()

    print("Seeding Users...")
    users = [
        # (full_name, email, phone, password_hash, role, is_verified, verification_type, bio)
        (
            "Admin Moderator",
            "admin@househunt.ke",
            "+254769323786",
            generate_password_hash("Admin@123"),
            "admin",
            1,
            "system_admin",
            "HouseHunt Kenya System Administrator & Compliance Officer."
        ),
        (
            "David Mwangi",
            "david.mwangi@gmail.com",
            "+254722123456",
            generate_password_hash("Mwangi@2026"),
            "landlord",
            1,
            "National ID & Title Deed",
            "Verified private property owner with residential apartments in Kilimani, Ngong Road, and Westlands."
        ),
        (
            "Faith Kamau",
            "faith.kamau@primehaven.co.ke",
            "+254733987654",
            generate_password_hash("Faith@2026"),
            "agent",
            1,
            "Estate Agents Registration Board (EARB #2940)",
            "Licensed property manager at PrimeHaven Realtors Kenya. Specializing in secure, water-guaranteed rentals along Thika Road and Ruaka."
        ),
        (
            "Peter Otieno",
            "peter.otieno@yahoo.com",
            "+254701234567",
            generate_password_hash("Otieno@2026"),
            "landlord",
            1,
            "National ID",
            "Owner of residential flats in Kasarani Clay City and South B Plainsview."
        ),
        (
            "Brian Kiprono",
            "brian.kiprono@gmail.com",
            "+254712345678",
            generate_password_hash("Brian@2026"),
            "seeker",
            0,
            None,
            "Software engineer searching for a peaceful 1-bedroom or studio apartment near Westlands or Kilimani."
        ),
        (
            "Amina Hassan",
            "amina.hassan@gmail.com",
            "+254790112233",
            generate_password_hash("Amina@2026"),
            "seeker",
            0,
            None,
            "Young professional looking for a safe 2-bedroom in Rongai or Ngong Road."
        ),
    ]

    cur.executemany(
        """
        INSERT INTO users (full_name, email, phone, password_hash, role, is_verified, verification_type, bio)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        users
    )

    print("Seeding Amenities...")
    amenities = [
        ("Borehole Water (24/7)", "fa-water", "utilities"),
        ("Prepaid KPLC Token Meter", "fa-bolt", "utilities"),
        ("Backup Power Generator", "fa-charging-station", "utilities"),
        ("CCTV & 24/7 Security Guards", "fa-shield-halved", "security"),
        ("Perimeter Electric Fence", "fa-border-all", "security"),
        ("Biometric Gate Access", "fa-fingerprint", "security"),
        ("Dedicated Parking Bay", "fa-square-parking", "convenience"),
        ("High-Speed Fiber Ready", "fa-wifi", "convenience"),
        ("Balcony with Scenic View", "fa-sun", "features"),
        ("Instant Hot Shower Installed", "fa-shower", "features"),
        ("Modern Ceramic Tiles", "fa-th-large", "features"),
        ("Built-in Kitchen Cabinets", "fa-kitchen-set", "features"),
        ("High-Speed Elevator / Lift", "fa-elevator", "convenience"),
        ("Garbage Collection Included", "fa-trash-can", "convenience"),
        ("Pet-Friendly Compound", "fa-paw", "convenience")
    ]

    cur.executemany(
        "INSERT INTO amenities (name, icon, category) VALUES (?, ?, ?)",
        amenities
    )

    print("Seeding Properties...")
    properties = [
        # 1. Kilimani Modern 1-Bedroom
        {
            "landlord_id": 2, # David Mwangi
            "title": "Sunlit 1-Bedroom Executive Haven — Kilimani (Wood Avenue)",
            "description": "Luxurious, brightly lit 1-bedroom apartment located along Wood Avenue in Kilimani. Features a spacious American open-plan kitchen with granite counters, built-in wardrobes, private balcony, instant shower, and reliable borehole water backed by Nairobi City Water supply. Silent backup generator for common areas and elevator. Safe neighbourhood walking distance to Yaya Centre, Adlife Plaza, and major transport routes.",
            "property_type": "1-Bedroom",
            "county": "Nairobi",
            "town": "Nairobi",
            "estate": "Kilimani",
            "landmark": "Near Yaya Centre & Wood Avenue",
            "latitude": -1.2921,
            "longitude": 36.7865,
            "monthly_rent": 45000.0,
            "security_deposit": 45000.0,
            "water_deposit": 2500.0,
            "electricity_deposit": 2000.0,
            "agent_fee": 0.0,
            "service_charge": 3000.0,
            "water_source": "Borehole + Nairobi City Council (24/7)",
            "electricity_type": "Individual Prepaid Token Meter",
            "garbage_fee": 500.0,
            "status": "available",
            "moderation_status": "approved",
            "is_promoted": 1,
            "is_property_verified": 1,
            "last_confirmed_date": "2026-10-15",
            "amenities": [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13],
            "images": [
                "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1200&q=80"
            ]
        },
        # 2. Roysambu Executive Bedsitter
        {
            "landlord_id": 3, # Faith Kamau
            "title": "Spacious Self-Contained Bedsitter — Roysambu (TRM Drive)",
            "description": "Well-finished, spacious bedsitter situated along TRM Drive in Roysambu, barely 3 minutes walk to Thika Road Mall (TRM) and the stage. Comes with tiled floor, modern ceiling, dedicated kitchen sink with lower cabinets, instant hot shower, and individual token meter. Safe gated community with CCTV, 24/7 guard, and steady borehole water so you never face water rationing.",
            "property_type": "Bedsitter",
            "county": "Nairobi",
            "town": "Nairobi",
            "estate": "Roysambu",
            "landmark": "Near TRM Drive, 200m from Thika Road Mall",
            "latitude": -1.2185,
            "longitude": 36.8887,
            "monthly_rent": 12500.0,
            "security_deposit": 12500.0,
            "water_deposit": 1000.0,
            "electricity_deposit": 1000.0,
            "agent_fee": 0.0,
            "service_charge": 0.0,
            "water_source": "Dedicated Clean Borehole (24/7)",
            "electricity_type": "Individual Prepaid Token Meter",
            "garbage_fee": 300.0,
            "status": "available",
            "moderation_status": "approved",
            "is_promoted": 1,
            "is_property_verified": 1,
            "last_confirmed_date": "2026-10-14",
            "amenities": [1, 2, 4, 8, 10, 11, 12],
            "images": [
                "https://images.unsplash.com/photo-1598928506311-c55ded91a20c?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1536376072261-38c75010e6c9?auto=format&fit=crop&w=1200&q=80"
            ]
        },
        # 3. Ongata Rongai 2-Bedroom Master Ensuite
        {
            "landlord_id": 2, # David Mwangi
            "title": "Serene 2-Bedroom Ensuite with Garden View — Ongata Rongai",
            "description": "Escape the city rush in this peaceful, newly built 2-bedroom master ensuite apartment in Ongata Rongai near Rimpa stage. Features large panoramic windows, spacious sitting area, modern ceramic finish, built-in closets, perimeter electric fencing, and unlimited solar-powered borehole water. Ample parking for 2 cars and child-safe compound.",
            "property_type": "2-Bedroom",
            "county": "Kajiado",
            "town": "Ongata Rongai",
            "estate": "Ongata Rongai",
            "landmark": "Near Rimpa Junction & QuickMart Rongai",
            "latitude": -1.3967,
            "longitude": 36.7589,
            "monthly_rent": 24000.0,
            "security_deposit": 24000.0,
            "water_deposit": 1500.0,
            "electricity_deposit": 1500.0,
            "agent_fee": 0.0,
            "service_charge": 1200.0,
            "water_source": "Solar Powered Borehole (Continuous 24/7)",
            "electricity_type": "Individual Prepaid Token Meter",
            "garbage_fee": 350.0,
            "status": "available",
            "moderation_status": "approved",
            "is_promoted": 0,
            "is_property_verified": 1,
            "last_confirmed_date": "2026-10-16",
            "amenities": [1, 2, 4, 5, 7, 8, 9, 10, 11, 12, 14, 15],
            "images": [
                "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1200&q=80"
            ]
        },
        # 4. Ruaka Modern Studio
        {
            "landlord_id": 3, # Faith Kamau
            "title": "Chic Studio Apartment with High-Speed Fiber — Ruaka (Limuru Road)",
            "description": "Contemporary studio apartment located in prime Ruaka, just 5 minutes drive from Two Rivers Mall and Rosslyn Riviera. Ideal for young corporate professionals or remote workers. Enjoy high-speed fiber internet infrastructure, modern kitchenette with cooker space, rooftop relaxation lounge with Nairobi skyline view, biometric access, and 24/7 CCTV surveillance.",
            "property_type": "Studio",
            "county": "Kiambu",
            "town": "Ruaka",
            "estate": "Ruaka",
            "landmark": "Near Two Rivers Mall & Joyland Supermarket",
            "latitude": -1.2062,
            "longitude": 36.7772,
            "monthly_rent": 22000.0,
            "security_deposit": 22000.0,
            "water_deposit": 1500.0,
            "electricity_deposit": 1000.0,
            "agent_fee": 0.0,
            "service_charge": 1500.0,
            "water_source": "Borehole & City Supply",
            "electricity_type": "Individual Prepaid Token Meter",
            "garbage_fee": 400.0,
            "status": "available",
            "moderation_status": "approved",
            "is_promoted": 1,
            "is_property_verified": 1,
            "last_confirmed_date": "2026-10-13",
            "amenities": [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
            "images": [
                "https://images.unsplash.com/photo-1502005229762-ee1b4f494543?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1200&q=80"
            ]
        },
        # 5. Westlands Luxury 2-Bedroom with DSQ
        {
            "landlord_id": 2, # David Mwangi
            "title": "Prime 2-Bedroom with DSQ, Pool & Full Generator — Westlands (Rhapta Road)",
            "description": "Executive residence on Rhapta Road in Westlands. Boasts expansive living and dining space, all bedrooms ensuite plus detached servant quarters (DSQ). State-of-the-art amenities including heated swimming pool, fully fitted gym, full backup generator powering inside units, high-speed elevators, 2 designated basement parking spots, and round-the-clock armed security.",
            "property_type": "2-Bedroom",
            "county": "Nairobi",
            "town": "Nairobi",
            "estate": "Westlands",
            "landmark": "Rhapta Road, 5 mins from Sarit Centre",
            "latitude": -1.2644,
            "longitude": 36.7923,
            "monthly_rent": 75000.0,
            "security_deposit": 75000.0,
            "water_deposit": 3000.0,
            "electricity_deposit": 3000.0,
            "agent_fee": 0.0,
            "service_charge": 5000.0,
            "water_source": "Borehole + Commercial Purified Supply",
            "electricity_type": "Individual Prepaid Token Meter + Full Generator Backup",
            "garbage_fee": 600.0,
            "status": "available",
            "moderation_status": "approved",
            "is_promoted": 1,
            "is_property_verified": 1,
            "last_confirmed_date": "2026-10-16",
            "amenities": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
            "images": [
                "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1200&q=80"
            ]
        },
        # 6. Kasarani 1-Bedroom Apartment
        {
            "landlord_id": 4, # Peter Otieno
            "title": "Cozy 1-Bedroom Apartment with Balcony — Kasarani (Clay City)",
            "description": "Neat and well-maintained 1-bedroom flat in Kasarani Clay City near Seasons. Tiled floors, well-ventilated rooms, private washing balcony, separate bathroom and toilet, and instant shower. 24/7 borehole water with separate storage tanks. Easy access to Thika Superhighway via Clay City feeder road.",
            "property_type": "1-Bedroom",
            "county": "Nairobi",
            "town": "Nairobi",
            "estate": "Kasarani",
            "landmark": "Clay City near Seasons & Kasarani Police",
            "latitude": -1.2154,
            "longitude": 36.9022,
            "monthly_rent": 16000.0,
            "security_deposit": 16000.0,
            "water_deposit": 1500.0,
            "electricity_deposit": 1000.0,
            "agent_fee": 0.0,
            "service_charge": 800.0,
            "water_source": "Borehole + Nairobi Water",
            "electricity_type": "Individual Prepaid Token Meter",
            "garbage_fee": 300.0,
            "status": "available",
            "moderation_status": "approved",
            "is_promoted": 0,
            "is_property_verified": 1,
            "last_confirmed_date": "2026-10-12",
            "amenities": [1, 2, 4, 8, 9, 10, 11, 12],
            "images": [
                "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1560185007-c5ca9d2c014d?auto=format&fit=crop&w=1200&q=80"
            ]
        },
        # 7. Ngong Road Bright 2-Bedroom
        {
            "landlord_id": 2, # David Mwangi
            "title": "Modern 2-Bedroom Apartment near The Junction — Ngong Road",
            "description": "Bright 2-bedroom home situated off Ngong Road, walking distance to The Junction Mall and Makindi Road. Features wooden parquet finishing in bedrooms, spacious kitchen with pantry, master ensuite, secure parking, CCTV surveillance, and dedicated borehole connection.",
            "property_type": "2-Bedroom",
            "county": "Nairobi",
            "town": "Nairobi",
            "estate": "Ngong Road",
            "landmark": "Opposite Junction Mall, off Makindi Road",
            "latitude": -1.2985,
            "longitude": 36.7621,
            "monthly_rent": 48000.0,
            "security_deposit": 48000.0,
            "water_deposit": 2500.0,
            "electricity_deposit": 2000.0,
            "agent_fee": 0.0,
            "service_charge": 2500.0,
            "water_source": "Borehole + City Council",
            "electricity_type": "Individual Prepaid Token Meter",
            "garbage_fee": 500.0,
            "status": "available",
            "moderation_status": "approved",
            "is_promoted": 1,
            "is_property_verified": 1,
            "last_confirmed_date": "2026-10-15",
            "amenities": [1, 2, 4, 5, 7, 8, 9, 10, 11, 12, 14],
            "images": [
                "https://images.unsplash.com/photo-1512918728675-ed5a9ecdebfd?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=1200&q=80"
            ]
        },
        # 8. South B 3-Bedroom Townhouse
        {
            "landlord_id": 4, # Peter Otieno
            "title": "Spacious 3-Bedroom Maisonette in Gated Court — South B (Plainsview)",
            "description": "Family-friendly 3-bedroom maisonette located inside a peaceful gated court in South B Plainsview. Ground floor comprises a large sitting room, guest cloakroom, and fitted kitchen leading to backyard dhobi area. First floor has 3 bedrooms (master ensuite) with inbuilt wardrobes. Secure 2-car parking bay and perimeter electric fence.",
            "property_type": "3-Bedroom",
            "county": "Nairobi",
            "town": "Nairobi",
            "estate": "South B",
            "landmark": "Plainsview Estate near Mater Hospital",
            "latitude": -1.3135,
            "longitude": 36.8378,
            "monthly_rent": 60000.0,
            "security_deposit": 60000.0,
            "water_deposit": 3000.0,
            "electricity_deposit": 2500.0,
            "agent_fee": 0.0,
            "service_charge": 2000.0,
            "water_source": "Nairobi Water + Underground 10,000L Storage Tank",
            "electricity_type": "Individual Prepaid Token Meter",
            "garbage_fee": 500.0,
            "status": "available",
            "moderation_status": "approved",
            "is_promoted": 0,
            "is_property_verified": 1,
            "last_confirmed_date": "2026-10-14",
            "amenities": [1, 2, 4, 5, 7, 8, 9, 10, 11, 12, 14, 15],
            "images": [
                "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1600565193348-f74bd3c7ccdf?auto=format&fit=crop&w=1200&q=80"
            ]
        }
    ]

    for prop in properties:
        cur.execute(
            """
            INSERT INTO properties (
                landlord_id, title, description, property_type, county, town, estate, landmark,
                latitude, longitude, monthly_rent, security_deposit, water_deposit, electricity_deposit,
                agent_fee, service_charge, water_source, electricity_type, garbage_fee, status,
                moderation_status, is_promoted, is_property_verified, last_confirmed_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                prop["landlord_id"], prop["title"], prop["description"], prop["property_type"],
                prop["county"], prop["town"], prop["estate"], prop["landmark"], prop["latitude"],
                prop["longitude"], prop["monthly_rent"], prop["security_deposit"], prop["water_deposit"],
                prop["electricity_deposit"], prop["agent_fee"], prop["service_charge"], prop["water_source"],
                prop["electricity_type"], prop["garbage_fee"], prop["status"], prop["moderation_status"],
                prop["is_promoted"], prop["is_property_verified"], prop["last_confirmed_date"]
            )
        )
        prop_id = cur.lastrowid

        # Insert images
        for i, img_url in enumerate(prop["images"]):
            cur.execute(
                "INSERT INTO property_images (property_id, image_url, is_featured, caption) VALUES (?, ?, ?, ?)",
                (prop_id, img_url, 1 if i == 0 else 0, f"View {i+1} of {prop['title']}")
            )

        # Insert amenities
        for amen_id in prop["amenities"]:
            cur.execute(
                "INSERT INTO property_amenities (property_id, amenity_id) VALUES (?, ?)",
                (prop_id, amen_id)
            )

    print("Seeding Favorites...")
    cur.execute("INSERT INTO favorites (user_id, property_id) VALUES (?, ?)", (5, 1)) # Brian favorited Kilimani
    cur.execute("INSERT INTO favorites (user_id, property_id) VALUES (?, ?)", (5, 4)) # Brian favorited Ruaka
    cur.execute("INSERT INTO favorites (user_id, property_id) VALUES (?, ?)", (6, 3)) # Amina favorited Rongai

    print("Seeding Inquiries...")
    cur.execute(
        """
        INSERT INTO inquiries (property_id, seeker_id, seeker_name, seeker_phone, seeker_email, message, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            1, 5, "Brian Kiprono", "+254712345678", "brian.kiprono@gmail.com",
            "Jambo David, I am interested in this 1-bedroom flat on Wood Avenue. Is there safe underground parking for 1 car, and what is the internet service provider available?",
            "responded"
        )
    )
    cur.execute(
        """
        UPDATE inquiries SET response_message = 'Habari Brian! Yes, there is 1 assigned parking slot with 24/7 CCTV, and Safaricom Fiber + Zuku Fiber are already connected in the building.'
        WHERE property_id = 1 AND seeker_id = 5
        """
    )

    print("Seeding Viewings...")
    cur.execute(
        """
        INSERT INTO viewings (property_id, seeker_id, preferred_date, preferred_time, notes, status, landlord_response)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            1, 5, "2026-10-18", "Morning (10:00 AM - 11:30 AM)",
            "I would like to inspect the water pressure and parking bay in person.",
            "confirmed",
            "Appointment confirmed. Call the caretaker Mr. John on 0722000111 upon arrival at the gate."
        )
    )

    print("Seeding Reviews...")
    reviews = [
        (1, 5, 5, "Clean building, genuine landlord! The rent and deposits matched the listing exactly with no surprise agent fees. Water is truly available 24/7.", 1),
        (2, 6, 4, "Great bedsitter for someone working along Thika Road or TRM. The token meter is separate so you control your own power costs.", 1),
        (4, 5, 5, "Fast fiber, very secure compound with biometric gate. Highly recommend Faith Kamau as an agent.", 1),
    ]
    cur.executemany(
        "INSERT INTO reviews (property_id, user_id, rating, comment, is_verified_tenant) VALUES (?, ?, ?, ?, ?)",
        reviews
    )

    print("Seeding Verification Requests...")
    cur.execute(
        """
        INSERT INTO verification_requests (user_id, property_id, document_type, document_reference, notes, status, reviewed_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            2, 1, "Title Deed", "NAIROBI/BLOCK102/4482",
            "Proof of ownership for Kilimani Wood Avenue apartments.",
            "approved", 1
        )
    )
    cur.execute(
        """
        INSERT INTO verification_requests (user_id, property_id, document_type, document_reference, notes, status, reviewed_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            3, 2, "Agent License", "EARB-REG-2940-2024",
            "Estate Agents Registration Board practicing certificate.",
            "approved", 1
        )
    )

    print("Seeding Sample Anti-Scam Reports...")
    cur.execute(
        """
        INSERT INTO reports (property_id, reporter_id, reason, details, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            2, 6, "agent_demands_viewing_fee",
            "A third-party claiming to represent this building requested KSh 1,500 viewing fee over M-Pesa before showing the house. (Reporting to ensure official contact is clear).",
            "resolved"
        )
    )

    print("Seeding Notifications...")
    notifications = [
        (5, "Viewing Confirmed", "Your viewing appointment for 'Sunlit 1-Bedroom Executive Haven — Kilimani' on 2026-10-18 has been confirmed by David Mwangi.", "/properties/1"),
        (2, "New Inquiry Received", "Brian Kiprono sent an inquiry regarding your Kilimani Wood Avenue property.", "/dashboard/landlord"),
        (3, "Agent Verification Approved", "Your Estate Agent license (EARB #2940) has been verified. Verified badge is now active on your listings.", "/dashboard/landlord")
    ]
    cur.executemany(
        "INSERT INTO notifications (user_id, title, message, link) VALUES (?, ?, ?, ?)",
        notifications
    )

    conn.commit()
    conn.close()
    print("Database seeding completed successfully!")


if __name__ == "__main__":
    seed()

