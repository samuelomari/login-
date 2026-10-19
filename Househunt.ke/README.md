# HouseHunt Kenya — Your Real Estate Solution

> **Tagline:** Find a home. Verify the listing. Move with confidence.  
> **Aesthetic:** Premium Real Estate — Elegant Dark Navy (`#090e1a`, `#162032`) with Gold (`#f59e0b`, `#d4af37`) & Emerald Verified Accents.

HouseHunt Kenya is a specialized web application tailored for the Kenyan rental ecosystem. It eliminates the rampant challenges of fake listings, fraudulent viewing fee demands over M-Pesa, hidden move-in deposits, and "water problems" by providing verified listings and 100% upfront move-in financial transparency.

---

## Key Features

### 1. House Search & Discovery
- **Location & Estates:** Search by estate, town, or landmark (Kilimani, Westlands, Roysambu / TRM Drive, Ruaka, Ongata Rongai, Kasarani Clay City, Ngong Road, South B Plainsview).
- **House Types:** Bedsitters, Single Rooms, Studios, 1-Bedroom, 2-Bedroom, and 3-Bedroom+ apartments.
- **Kenyan Utility Guarantees:** Filter by reliable borehole water (24/7), individual prepaid KPLC token meters, CCTV & guards, high-speed fiber, and dedicated parking.
- **Views:** Instant toggle between Grid and List formats, plus dynamic sorting (Verified first, Rent Low-High, Rent High-Low, Newest).
- **Persistent Favorites:** Save shortlisted houses with live badge counters.

### 2. Move-in & Upfront Cost Calculator
- Computes the exact liquid cash required before getting the key:  
  $$\text{Total Move-in} = \text{1st Month Rent} + \text{Security Deposit} + \text{Water Deposit} + \text{Token Deposit} + \text{Garbage Fee} + \text{Moving Truck Estimate}$$
- **Budget Matching:** Alerts renters when upfront costs exceed their available moving savings.
- **Preset Auto-fill:** Pick any verified listing from a dropdown to instantly populate its disclosed fees.

### 3. Side-by-Side House Comparison
- Compare up to 3 properties side-by-side on monthly rent, total upfront move-in capital, utility terms, and verification badges.

### 4. AI House-Hunting Natural Language Assistant
- Parse natural language queries like:  
  *"Looking for a 2-bedroom in Rongai under 25k with parking and borehole water"* or *"Cheap bedsitter in Roysambu near TRM"*
- Automatically extracts location, budget ceiling, house type, and amenities, presenting instant matches.

### 5. Trust & Anti-Scam Protection
- **Multi-Level Verification:** Independent verification badges for Landlords (National ID/Title Deeds) and Licensed Agents (Estate Agents Registration Board — EARB).
- **Zero Viewing Fee Guarantee:** Prominent alerts against paying any advance fees over M-Pesa prior to in-person inspection.
- **Community Scam Reporting:** In-app reporting for viewing fee extortion, fake photos, or occupied units with automatic moderation flagging.
- **Automated Duplicate Detection:** Scans for broker duplicates with matching rents and estates.

### 6. Landlord & Agent Portal
- Transparent listing creator requiring full upfront charge itemization.
- In-app inquiry manager and viewing appointment confirmation.
- One-click status toggling (Available, Occupied, Maintenance).

### 7. Administrator Compliance Console
- Moderate listings, inspect potential duplicates, approve/reject landlord ID/License submissions, and resolve scam complaints.

### 8. Seeker Dashboard, Notifications & Tenant Reviews (New)
- Personal seeker hub (`/dashboard/seeker`) tracking saved houses, viewing appointments, inquiries and latest alerts.
- Notifications inbox (`/notifications`) with unread badge in the navbar and mark-as-read actions.
- In-page tenant review form with interactive star rating (`POST /api/reviews`), plus Similar Houses Nearby on every property page.
- Listings pagination (9 per page) with filter-preserving page links for faster browsing.

---

## Technology Stack

- **Frontend:** HTML5, CSS3 (Custom responsive Premium Dark Navy & Gold design system), Vanilla JavaScript (ES6+), FontAwesome 6.
- **Backend:** Python 3 with Flask, Werkzeug security password hashing.
- **Database:** SQLite with full foreign key constraints, indexing, and 12 relational tables.

---

## Quickstart & How to Run

### 1. Run the Application
From the project folder:
```bash
/home/samuel-omari/.gemini/antigravity/scratch/venv/bin/python app.py
```
Open your browser at: `http://127.0.0.1:5000`

### 2. Pre-seeded Demo Accounts
| Role | Email | Password | Access / Capabilities |
| :--- | :--- | :--- | :--- |
| **System Admin** | `admin@househunt.ke` | `Admin@123` | Compliance Console, Verifications, Scam Reports |
| **Verified Landlord** | `david.mwangi@gmail.com` | `Mwangi@2026` | Landlord Portal, Kilimani & Ngong Rd listings |
| **Verified Agent** | `faith.kamau@primehaven.co.ke` | `Faith@2026` | Licensed Agent (EARB #2940), Roysambu & Ruaka |
| **House Seeker** | `brian.kiprono@gmail.com` | `Brian@2026` | Shortlists, Saved Favorites, Viewing requests |

### 3. Running the Test Suite
```bash
/home/samuel-omari/.gemini/antigravity/scratch/venv/bin/python -m unittest tests/test_app.py
```
All 14 unit and integration tests will execute against an isolated test database.

