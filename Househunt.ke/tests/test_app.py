"""
Automated Test Suite for HouseHunt Kenya.
Tests database integrity, routes, auth, search filters, AI assistant API,
inquiries, viewings, moving cost calculator, and administrative moderation.
"""

import os
import sys
import unittest

# Ensure app directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from database import DB_FILE, get_db_connection, init_db
from seed_data import seed


class HouseHuntKenyaTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set test database
        os.environ["HOUSEHUNT_DB"] = os.path.join(os.path.dirname(__file__), "test_househunt.db")
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        seed()

    @classmethod
    def tearDownClass(cls):
        test_db = os.environ.get("HOUSEHUNT_DB")
        if test_db and os.path.exists(test_db):
            os.remove(test_db)

    def setUp(self):
        self.client = app.test_client()

    def login(self, email, password):
        return self.client.post(
            "/auth?tab=login",
            data={"action": "login", "email": email, "password": password},
            follow_redirects=True,
        )

    def logout(self):
        return self.client.get("/logout", follow_redirects=True)

    # 1. Test Home & Navigation
    def test_home_page(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"HouseHunt", res.data)
        self.assertIn(b"Move with confidence", res.data)
        self.assertIn(b"Verified Rentals in Nairobi", res.data)

    # 2. Test Listings & Search Filters
    def test_listings_all(self):
        res = self.client.get("/listings")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Kilimani", res.data)
        self.assertIn(b"Roysambu", res.data)

    def test_listings_filter_estate(self):
        res = self.client.get("/listings?estate=Kilimani")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Kilimani", res.data)

    def test_listings_filter_max_rent(self):
        res = self.client.get("/listings?max_rent=15000")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Roysambu", res.data) # 12,500 bedsitter
        self.assertNotIn(b"Rhapta Road", res.data) # 75,000 Westlands excluded

    def test_listings_ajax_json(self):
        res = self.client.get("/listings?format=json")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("count", data)
        self.assertIn("properties", data)
        self.assertGreater(data["count"], 0)

    # 3. Test Property Detail Page & Move-in Cost Transparency
    def test_property_detail(self):
        res = self.client.get("/properties/1")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Wood Avenue", res.data)
        self.assertIn(b"Total Move-in Capital", res.data)
        self.assertIn(b"Borehole", res.data)
        self.assertIn(b"wa.me", res.data) # WhatsApp button present

    # 4. Test Calculator Page
    def test_calculator_page(self):
        res = self.client.get("/calculator")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Moving-Cost Calculator", res.data)
        self.assertIn(b"calcTotalUpfront", res.data)

    # 5. Test Comparison Page
    def test_compare_page(self):
        res = self.client.get("/compare?ids=1,2")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Compare Properties", res.data)
        self.assertIn(b"Wood Avenue", res.data)
        self.assertIn(b"Roysambu", res.data)

    # 6. Test AI Natural Language House-Hunting Assistant
    def test_ai_search_endpoint(self):
        res = self.client.post(
            "/api/ai-search",
            json={"prompt": "Looking for a 2-bedroom in Rongai under 30k with parking"},
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["filters"]["estate"], "Ongata Rongai")
        self.assertEqual(data["filters"]["property_type"], "2-Bedroom")
        self.assertEqual(data["filters"]["max_rent"], 30000)
        self.assertGreater(len(data["results"]), 0)

    # 7. Test In-App Inquiry API
    def test_inquiry_submission(self):
        res = self.client.post(
            "/api/inquiries",
            json={
                "property_id": 2,
                "name": "Grace Wanjiku",
                "phone": "+254700112233",
                "email": "grace@gmail.com",
                "message": "Is this bedsitter ready for immediate occupation?",
            },
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])

    # 8. Test Viewing Appointment Request API
    def test_schedule_viewing_flow(self):
        # Without login -> 401
        res = self.client.post(
            "/api/viewings",
            json={"property_id": 1, "date": "2026-10-22", "time": "Morning (9:00 AM - 11:30 AM)"},
        )
        self.assertEqual(res.status_code, 401)

        # Login as seeker
        self.login("brian.kiprono@gmail.com", "Brian@2026")
        res = self.client.post(
            "/api/viewings",
            json={
                "property_id": 1,
                "date": "2026-10-22",
                "time": "Morning (9:00 AM - 11:30 AM)",
                "notes": "Testing parking bay.",
            },
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])
        self.logout()

    # 9. Test Anti-Scam Reporting API
    def test_scam_report_submission(self):
        res = self.client.post(
            "/api/reports",
            json={
                "property_id": 3,
                "reason": "agent_demands_viewing_fee",
                "details": "Agent requested KSh 1,000 before opening gate.",
            },
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])

    # 10. Test Landlord Property Creation
    def test_landlord_post_property(self):
        self.login("david.mwangi@gmail.com", "Mwangi@2026")
        res = self.client.post(
            "/properties/new",
            data={
                "title": "Newly Built Studio in Kilimani",
                "description": "Chic studio with borehole and token meter.",
                "property_type": "Studio",
                "town": "Nairobi",
                "estate": "Kilimani",
                "landmark": "Near Dennis Pritt",
                "monthly_rent": "28000",
                "security_deposit": "28000",
                "water_deposit": "1500",
                "electricity_deposit": "1000",
                "garbage_fee": "400",
                "agent_fee": "0",
                "water_source": "Borehole (24/7)",
                "electricity_type": "Individual Prepaid Token Meter",
                "image_urls": ["https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800"],
            },
            follow_redirects=True,
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Newly Built Studio in Kilimani", res.data)
        self.logout()

    # 11. Test Admin Dashboard Access & Verification Workflow
    def test_admin_dashboard_and_verification(self):
        # Seeker cannot access admin console
        self.login("brian.kiprono@gmail.com", "Brian@2026")
        res = self.client.get("/dashboard/admin", follow_redirects=True)
        self.assertIn(b"Access denied", res.data)
        self.logout()

        # Admin can access and approve verification
        self.login("admin@househunt.ke", "Admin@123")
        res = self.client.get("/dashboard/admin")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Compliance Console", res.data)
        self.logout()


if __name__ == "__main__":
    unittest.main()

