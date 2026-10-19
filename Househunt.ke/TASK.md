# HouseHunt Kenya — Implementation Roadmap & Task Tracker

**Tagline:** Find a home. Verify the listing. Move with confidence.  
**Visual Style:** Premium Real Estate (Dark Navy `#0c1322` & Lustrous Gold `#f59e0b` / `#d4af37`)

---

## 1. Plan & Milestones

- [x] **Milestone 1: Database Architecture & Models (SQLite)**
  - [x] Create `schema.sql` with 12 relational tables: `users`, `properties`, `property_images`, `amenities`, `property_amenities`, `favorites`, `inquiries`, `viewings`, `reviews`, `reports`, `verification_requests`, `notifications`.
  - [x] Implement database initialization and query helpers in `database.py`.
  - [x] Create realistic Kenyan seed dataset in `seed_data.py` (Kilimani, Westlands, Roysambu, Ruaka, Rongai, Kasarani, Ngong Road, South B) with transparent deposits, utility terms, and verification badges.

- [x] **Milestone 2: Flask Backend Application Core**
  - [x] Setup `app.py` with session-based authentication (Seeker, Landlord, Agent, Admin).
  - [x] Password hashing using Werkzeug / hashlib.
  - [x] REST API & SSR endpoints for search, filtering, property CRUD, enquiries, viewings, favorites, and scam reporting.
  - [x] Anti-scam duplicate detection algorithm and scam-risk indicator scoring.
  - [x] AI House-Hunting Assistant endpoint (Natural Language Query parsing).

- [x] **Milestone 3: Premium Real Estate Frontend UI (HTML5 & CSS3)**
  - [x] Responsive navigation bar with search bar, role-based dashboard links, favorites counter, and compare pill.
  - [x] Color palette: Dark Navy (`#0c1322`, `#162032`, `#1e293b`), Gold accents (`#f59e0b`, `#d4af37`), crisp typography, glassmorphism card styling.
  - [x] Templates: `base.html`, `index.html`, `listings.html`, `property_detail.html`, `calculator.html`, `compare.html`, `dashboard_landlord.html`, `dashboard_admin.html`, `auth.html`.
  - [x] Mobile-first responsive layout with collapsible filter drawers and quick-action bottom bars.

- [x] **Milestone 4: Interactive Client-Side JavaScript Features**
  - [x] Real-time multi-criteria filter & sort (rent range slider, estate dropdown, bedrooms, verified only, amenities).
  - [x] Grid vs. List view switcher.
  - [x] Interactive Upfront Move-in Cost Calculator with visual breakdown (rent, deposit, water deposit, token meter deposit, agent fees, moving truck).
  - [x] Property Comparison Drawer & matrix comparing up to 3 listings side-by-side.
  - [x] In-App Viewing Scheduler modal & instant WhatsApp click-to-chat generator with pre-filled message.
  - [x] Report Suspicious Listing modal with scam flags (unrealistic price, duplicate photos, upfront viewing fee demand).
  - [x] Natural Language Search assistant widget ("Find a 2BR in Kilimani under 45k with borehole and parking").

- [x] **Milestone 5: Dashboards & Anti-Scam Protection Features**
  - [x] Landlord / Agent Dashboard: Post listing with transparent cost items, manage photos, view enquiries & schedule viewings, toggle occupancy.
  - [x] Admin Dashboard: Verification requests review, approve/reject listings, review scam reports, monitor platform metrics.
  - [x] Verified Landlord & Property Authorization Badges.

- [x] **Milestone 6: Verification, Testing & Polish**
  - [x] Write unit and integration test suite (`tests/test_app.py`).
  - [x] Verify all routes, auth flows, calculator formulas, and search filters (14/14 tests passing).
  - [x] Verify responsive design and low-data accessibility.
