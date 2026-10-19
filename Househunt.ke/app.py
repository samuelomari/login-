"""
HouseHunt Kenya — Main Flask Application.
Your Real Estate Solution for the Kenyan Market.
"""

import json
import os
import re
from functools import wraps
from typing import Any, Dict, List, Optional
from datetime import datetime

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from database import execute_db, get_db_connection, query_db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "househunt_kenya_secret_key_2026_safe")


# ============================================================================
# Auth Decorators & Helpers
# ============================================================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for("auth", next=request.path))
        return f(*args, **kwargs)

    return decorated_function


def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                flash("Please sign in to continue.", "warning")
                return redirect(url_for("auth", next=request.path))
            if session.get("user_role") not in allowed_roles:
                flash("Access denied: You do not have permission for this section.", "danger")
                return redirect(url_for("index"))
            return f(*args, **kwargs)

        return decorated_function

    return decorator


@app.context_processor
def inject_global_context():
    """Inject current user, unread notification counts, and stats into all templates."""
    current_user = None
    unread_notifications = 0
    favorites_count = 0

    if "user_id" in session:
        current_user = query_db(
            "SELECT id, full_name, email, phone, role, is_verified, verification_type FROM users WHERE id = ?",
            (session["user_id"],),
            one=True,
        )
        notif_row = query_db(
            "SELECT COUNT(*) as count FROM notifications WHERE user_id = ? AND is_read = 0",
            (session["user_id"],),
            one=True,
        )
        unread_notifications = notif_row["count"] if notif_row else 0

        fav_row = query_db(
            "SELECT COUNT(*) as count FROM favorites WHERE user_id = ?",
            (session["user_id"],),
            one=True,
        )
        favorites_count = fav_row["count"] if fav_row else 0

    return {
        "current_user": current_user,
        "unread_notifications": unread_notifications,
        "favorites_count": favorites_count,
        "current_year": 2026,
    }


# ============================================================================
# Property Retrieval Utilities
# ============================================================================
def get_property_full_details(prop_id: int) -> Optional[Dict[str, Any]]:
    """Fetches single property with images, amenities, landlord info, and rating."""
    prop = query_db(
        """
        SELECT p.*,
               u.full_name as landlord_name,
               u.phone as landlord_phone,
               u.email as landlord_email,
               u.role as landlord_role,
               u.is_verified as landlord_is_verified,
               u.verification_type as landlord_verification_type,
               u.bio as landlord_bio
        FROM properties p
        JOIN users u ON p.landlord_id = u.id
        WHERE p.id = ?
        """,
        (prop_id,),
        one=True,
    )
    if not prop:
        return None

    # Fetch images
    images = query_db(
        "SELECT * FROM property_images WHERE property_id = ? ORDER BY is_featured DESC, id ASC",
        (prop_id,),
    )
    prop["images"] = images or []
    prop["featured_image"] = (
        images[0]["image_url"]
        if images
        else "https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=800&q=80"
    )

    # Fetch amenities
    amenities = query_db(
        """
        SELECT a.* FROM amenities a
        JOIN property_amenities pa ON a.id = pa.amenity_id
        WHERE pa.property_id = ?
        ORDER BY a.name ASC
        """,
        (prop_id,),
    )
    prop["amenities"] = amenities or []

    # Calculate total upfront moving cost
    # Rent + Security Deposit + Water Deposit + Electricity Deposit + Garbage Fee + Agent Fee
    prop["total_upfront_cost"] = (
        prop["monthly_rent"]
        + prop["security_deposit"]
        + prop["water_deposit"]
        + prop["electricity_deposit"]
        + prop["garbage_fee"]
        + prop["agent_fee"]
    )

    # Calculate review rating
    rating_row = query_db(
        "SELECT AVG(rating) as avg_rating, COUNT(*) as review_count FROM reviews WHERE property_id = ?",
        (prop_id,),
        one=True,
    )
    prop["avg_rating"] = round(rating_row["avg_rating"], 1) if rating_row and rating_row["avg_rating"] else 4.8
    prop["review_count"] = rating_row["review_count"] if rating_row else 0

    return prop


def build_whatsapp_link(phone: str, property_title: str, prop_id: int) -> str:
    """Creates a direct WhatsApp click-to-chat URL with Kenyan phone number formatting."""
    clean_phone = re.sub(r"[^0-9]", "", phone)
    if clean_phone.startswith("0"):
        clean_phone = "254" + clean_phone[1:]
    elif not clean_phone.startswith("254"):
        clean_phone = "254" + clean_phone

    message = (
        f"Habari! I am inquiring about '{property_title}' (Ref #{prop_id}) "
        f"listed on HouseHunt Kenya. Is it currently available for a viewing?"
    )
    from urllib.parse import quote

    return f"https://wa.me/{clean_phone}?text={quote(message)}"


# ============================================================================
# Main User Routes
# ============================================================================
@app.route("/")
def index():
    """Home page with search, verified featured properties, and transparency pitch."""
    featured_properties = query_db(
        """
        SELECT p.*,
               u.full_name as landlord_name,
               u.is_verified as landlord_is_verified,
               (SELECT image_url FROM property_images WHERE property_id = p.id ORDER BY is_featured DESC LIMIT 1) as featured_image,
               (p.monthly_rent + p.security_deposit + p.water_deposit + p.electricity_deposit + p.garbage_fee + p.agent_fee) as total_upfront_cost
        FROM properties p
        JOIN users u ON p.landlord_id = u.id
        WHERE p.status = 'available' AND p.moderation_status = 'approved'
        ORDER BY p.is_promoted DESC, p.is_property_verified DESC, p.created_at DESC
        LIMIT 6
        """
    )

    # Summary metrics for trust
    total_listings = query_db("SELECT COUNT(*) as count FROM properties WHERE moderation_status = 'approved'", one=True)["count"]
    verified_listings = query_db("SELECT COUNT(*) as count FROM properties WHERE is_property_verified = 1", one=True)["count"]
    resolved_reports = query_db("SELECT COUNT(*) as count FROM reports WHERE status = 'resolved'", one=True)["count"]

    estates = query_db("SELECT DISTINCT estate FROM properties WHERE moderation_status = 'approved' ORDER BY estate ASC")
    amenities = query_db("SELECT * FROM amenities ORDER BY name ASC")

    return render_template(
        "index.html",
        featured_properties=featured_properties,
        total_listings=total_listings,
        verified_listings=verified_listings,
        resolved_reports=resolved_reports,
        estates=estates,
        amenities=amenities,
    )


@app.route("/listings")
def listings():
    """Multi-criteria search & discovery with instant filters, grid/list view, and sorting."""
    q = request.args.get("q", "").strip()
    estate = request.args.get("estate", "").strip()
    town = request.args.get("town", "").strip()
    property_type = request.args.get("property_type", "").strip()
    min_rent = request.args.get("min_rent", type=float)
    max_rent = request.args.get("max_rent", type=float)
    max_upfront = request.args.get("max_upfront", type=float)
    verified_only = request.args.get("verified_only", type=int, default=0)
    sort_by = request.args.get("sort", "verified")
    selected_amenities = request.args.getlist("amenities")

    sql = """
        SELECT p.*,
               u.full_name as landlord_name,
               u.role as landlord_role,
               u.is_verified as landlord_is_verified,
               (SELECT image_url FROM property_images WHERE property_id = p.id ORDER BY is_featured DESC LIMIT 1) as featured_image,
               (p.monthly_rent + p.security_deposit + p.water_deposit + p.electricity_deposit + p.garbage_fee + p.agent_fee) as total_upfront_cost
        FROM properties p
        JOIN users u ON p.landlord_id = u.id
        WHERE p.status = 'available' AND p.moderation_status = 'approved'
    """
    params = []

    if q:
        sql += " AND (p.title LIKE ? OR p.estate LIKE ? OR p.town LIKE ? OR p.landmark LIKE ? OR p.description LIKE ?)"
        term = f"%{q}%"
        params.extend([term, term, term, term, term])

    if estate:
        sql += " AND p.estate = ?"
        params.append(estate)

    if town:
        sql += " AND p.town = ?"
        params.append(town)

    if property_type:
        sql += " AND p.property_type = ?"
        params.append(property_type)

    if min_rent is not None:
        sql += " AND p.monthly_rent >= ?"
        params.append(min_rent)

    if max_rent is not None:
        sql += " AND p.monthly_rent <= ?"
        params.append(max_rent)

    if verified_only:
        sql += " AND p.is_property_verified = 1"

    if selected_amenities:
        for amen_id in selected_amenities:
            sql += " AND p.id IN (SELECT property_id FROM property_amenities WHERE amenity_id = ?)"
            params.append(amen_id)

    # Sorting
    if sort_by == "price_asc":
        sql += " ORDER BY p.monthly_rent ASC"
    elif sort_by == "price_desc":
        sql += " ORDER BY p.monthly_rent DESC"
    elif sort_by == "newest":
        sql += " ORDER BY p.created_at DESC"
    else:  # verified first, then promoted
        sql += " ORDER BY p.is_promoted DESC, p.is_property_verified DESC, p.created_at DESC"

    properties = query_db(sql, tuple(params))

    # Optional filter by computed upfront move-in cost
    if max_upfront is not None:
        properties = [p for p in properties if p["total_upfront_cost"] <= max_upfront]

    # Collect user's favorite IDs for instant active heart state
    user_favorites = []
    if "user_id" in session:
        fav_rows = query_db("SELECT property_id FROM favorites WHERE user_id = ?", (session["user_id"],))
        user_favorites = [f["property_id"] for f in fav_rows]

    # Pagination (9 per page keeps cards readable on mobile + desktop)
    try:
        page = max(1, int(request.args.get("page", 1)))
    except (TypeError, ValueError):
        page = 1
    per_page = 9
    total_count = len(properties)
    total_pages = max(1, (total_count + per_page - 1) // per_page)
    if page > total_pages:
        page = total_pages
    start = (page - 1) * per_page
    paged_properties = properties[start:start + per_page]

    # Return JSON for AJAX dynamic filtering
    if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.args.get("format") == "json":
        return jsonify({
            "count": len(properties),
            "properties": properties,
            "user_favorites": user_favorites,
        })

    all_estates = query_db("SELECT DISTINCT estate FROM properties WHERE moderation_status = 'approved' ORDER BY estate ASC")
    all_amenities = query_db("SELECT * FROM amenities ORDER BY name ASC")

    return render_template(
        "listings.html",
        properties=paged_properties,
        total_count=total_count,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        estates=all_estates,
        amenities=all_amenities,
        selected_amenities=[int(x) for x in selected_amenities if x.isdigit()],
        current_filters={
            "q": q,
            "estate": estate,
            "town": town,
            "property_type": property_type,
            "min_rent": min_rent or "",
            "max_rent": max_rent or "",
            "max_upfront": max_upfront or "",
            "verified_only": verified_only,
            "sort": sort_by,
        },
        user_favorites=user_favorites,
    )


@app.route("/properties/<int:prop_id>")
def property_detail(prop_id: int):
    """Detailed property page with transparent cost breakdown, landlord verification, and booking."""
    prop = get_property_full_details(prop_id)
    if not prop:
        flash("Listing not found or has been removed.", "danger")
        return redirect(url_for("listings"))

    # Increment view count
    execute_db("UPDATE properties SET views_count = views_count + 1 WHERE id = ?", (prop_id,))

    # WhatsApp link
    whatsapp_url = build_whatsapp_link(prop["landlord_phone"], prop["title"], prop_id)

    # Reviews
    reviews = query_db(
        """
        SELECT r.*, u.full_name as author_name, u.role as author_role
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.property_id = ?
        ORDER BY r.created_at DESC
        """,
        (prop_id,),
    )

    # Similar houses in same estate or nearby price range
    similar_properties = query_db(
        """
        SELECT p.*,
               (SELECT image_url FROM property_images WHERE property_id = p.id ORDER BY is_featured DESC LIMIT 1) as featured_image,
               (p.monthly_rent + p.security_deposit + p.water_deposit + p.electricity_deposit + p.garbage_fee + p.agent_fee) as total_upfront_cost
        FROM properties p
        WHERE p.id != ? AND (p.estate = ? OR p.property_type = ?) AND p.status = 'available' AND p.moderation_status = 'approved'
        LIMIT 3
        """,
        (prop_id, prop["estate"], prop["property_type"]),
    )

    is_favorited = False
    if "user_id" in session:
        fav_check = query_db(
            "SELECT id FROM favorites WHERE user_id = ? AND property_id = ?",
            (session["user_id"], prop_id),
            one=True,
        )
        is_favorited = bool(fav_check)

    return render_template(
        "property_detail.html",
        prop=prop,
        whatsapp_url=whatsapp_url,
        reviews=reviews,
        similar_properties=similar_properties,
        is_favorited=is_favorited,
    )


# ============================================================================
# Upfront Moving Cost & Budget Affordability Calculator
# ============================================================================
@app.route("/calculator")
def calculator():
    """Interactive Rent and Moving-Cost Calculator for Kenyan House Hunters."""
    all_properties = query_db(
        """
        SELECT p.id, p.title, p.estate, p.property_type, p.monthly_rent,
               p.security_deposit, p.water_deposit, p.electricity_deposit,
               p.garbage_fee, p.agent_fee, p.is_property_verified
        FROM properties p
        WHERE p.status = 'available' AND p.moderation_status = 'approved'
        ORDER BY p.monthly_rent ASC
        """
    )
    return render_template("calculator.html", properties=all_properties)


# ============================================================================
# House Comparison Feature
# ============================================================================
@app.route("/compare")
def compare():
    """Side-by-side comparison matrix for up to 3 properties."""
    prop_ids_str = request.args.get("ids", "")
    prop_ids = [int(x) for x in prop_ids_str.split(",") if x.isdigit()]

    if not prop_ids:
        # Default to first 2 properties for demonstration
        default_props = query_db("SELECT id FROM properties WHERE moderation_status = 'approved' LIMIT 2")
        prop_ids = [p["id"] for p in default_props]

    properties = []
    for pid in prop_ids[:3]:
        p = get_property_full_details(pid)
        if p:
            properties.append(p)

    return render_template("compare.html", properties=properties, prop_ids=prop_ids)


# ============================================================================
# AI House-Hunting Assistant API
# ============================================================================
@app.route("/api/ai-search", methods=["POST"])
def ai_search():
    """
    Parses ordinary language house-hunting requests into structured filters:
    e.g. 'Find a 2-bedroom in Rongai under 25k with parking and borehole'
    """
    data = request.get_json() or {}
    user_prompt = data.get("prompt", "").lower().strip()

    if not user_prompt:
        return jsonify({"success": False, "error": "Prompt cannot be empty"}), 400

    extracted_filters = {
        "property_type": None,
        "estate": None,
        "max_rent": None,
        "detected_amenities": [],
        "explanation": []
    }

    # Extract Property Type
    if "bedsitter" in user_prompt or "bed-sitter" in user_prompt:
        extracted_filters["property_type"] = "Bedsitter"
        extracted_filters["explanation"].append("Identified property type: Bedsitter")
    elif "studio" in user_prompt:
        extracted_filters["property_type"] = "Studio"
        extracted_filters["explanation"].append("Identified property type: Studio")
    elif "1 bedroom" in user_prompt or "1-bedroom" in user_prompt or "1br" in user_prompt or "one bedroom" in user_prompt:
        extracted_filters["property_type"] = "1-Bedroom"
        extracted_filters["explanation"].append("Identified property type: 1-Bedroom")
    elif "2 bedroom" in user_prompt or "2-bedroom" in user_prompt or "2br" in user_prompt or "two bedroom" in user_prompt:
        extracted_filters["property_type"] = "2-Bedroom"
        extracted_filters["explanation"].append("Identified property type: 2-Bedroom")
    elif "3 bedroom" in user_prompt or "3-bedroom" in user_prompt or "3br" in user_prompt or "three bedroom" in user_prompt:
        extracted_filters["property_type"] = "3-Bedroom"
        extracted_filters["explanation"].append("Identified property type: 3-Bedroom")

    # Extract Kenyan Estates
    estates_map = {
        "kilimani": "Kilimani",
        "roysambu": "Roysambu",
        "trm": "Roysambu",
        "rongai": "Ongata Rongai",
        "ongata rongai": "Ongata Rongai",
        "ruaka": "Ruaka",
        "westlands": "Westlands",
        "kasarani": "Kasarani",
        "ngong road": "Ngong Road",
        "ngong": "Ngong Road",
        "south b": "South B",
        "south c": "South B"
    }
    for key, val in estates_map.items():
        if key in user_prompt:
            extracted_filters["estate"] = val
            extracted_filters["explanation"].append(f"Target location detected: {val}")
            break

    # Extract Budget / Rent
    # Match patterns like: under 25k, below 30,000, 20000, max 45k
    rent_match = re.search(r"(?:under|below|max|around|within|budget of)\s*(?:ksh|kes)?\s*(\d+)(?:k)?", user_prompt)
    if not rent_match:
        rent_match = re.search(r"(\d+)\s*(?:k|kes|ksh)", user_prompt)

    if rent_match:
        val = int(rent_match.group(1))
        # if number is small (e.g. 25, 30), it meant 25k = 25000
        if val < 500:
            val = val * 1000
        extracted_filters["max_rent"] = val
        extracted_filters["explanation"].append(f"Maximum rent budget set to: KSh {val:,}")

    # Extract Amenities
    if "borehole" in user_prompt or "water" in user_prompt:
        extracted_filters["detected_amenities"].append("Borehole Water (24/7)")
    if "parking" in user_prompt:
        extracted_filters["detected_amenities"].append("Dedicated Parking Bay")
    if "wifi" in user_prompt or "wi-fi" in user_prompt or "fiber" in user_prompt:
        extracted_filters["detected_amenities"].append("High-Speed Fiber Ready")
    if "security" in user_prompt or "cctv" in user_prompt or "guard" in user_prompt:
        extracted_filters["detected_amenities"].append("CCTV & 24/7 Security Guards")
    if "generator" in user_prompt or "backup" in user_prompt:
        extracted_filters["detected_amenities"].append("Backup Power Generator")

    if extracted_filters["detected_amenities"]:
        extracted_filters["explanation"].append(f"Prioritizing amenities: {', '.join(extracted_filters['detected_amenities'])}")

    # Execute database query matching these constraints
    query = """
        SELECT p.*,
               u.full_name as landlord_name,
               u.is_verified as landlord_is_verified,
               (SELECT image_url FROM property_images WHERE property_id = p.id ORDER BY is_featured DESC LIMIT 1) as featured_image,
               (p.monthly_rent + p.security_deposit + p.water_deposit + p.electricity_deposit + p.garbage_fee + p.agent_fee) as total_upfront_cost
        FROM properties p
        JOIN users u ON p.landlord_id = u.id
        WHERE p.status = 'available' AND p.moderation_status = 'approved'
    """
    params = []

    if extracted_filters["estate"]:
        query += " AND p.estate = ?"
        params.append(extracted_filters["estate"])

    if extracted_filters["property_type"]:
        query += " AND p.property_type = ?"
        params.append(extracted_filters["property_type"])

    if extracted_filters["max_rent"]:
        query += " AND p.monthly_rent <= ?"
        params.append(extracted_filters["max_rent"])

    query += " ORDER BY p.is_property_verified DESC, p.monthly_rent ASC"
    results = query_db(query, tuple(params))

    return jsonify({
        "success": True,
        "filters": extracted_filters,
        "results_count": len(results),
        "results": results
    })


# ============================================================================
# Inquiries, Viewings, Reports, Reviews & Notifications APIs
# ============================================================================
@app.route("/api/inquiries", methods=["POST"])
def submit_inquiry():
    """Allows house seekers to send an in-app inquiry to a landlord."""
    data = request.get_json() or {}
    prop_id = data.get("property_id")
    seeker_name = data.get("name", "").strip()
    seeker_phone = data.get("phone", "").strip()
    seeker_email = data.get("email", "").strip()
    message = data.get("message", "").strip()

    if not prop_id or not seeker_name or not seeker_phone or not message:
        return jsonify({"success": False, "error": "Please provide your name, phone number, and inquiry message."}), 400

    prop = query_db("SELECT id, landlord_id, title FROM properties WHERE id = ?", (prop_id,), one=True)
    if not prop:
        return jsonify({"success": False, "error": "Property not found."}), 404

    seeker_id = session.get("user_id")

    execute_db(
        """
        INSERT INTO inquiries (property_id, seeker_id, seeker_name, seeker_phone, seeker_email, message)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (prop_id, seeker_id, seeker_name, seeker_phone, seeker_email, message)
    )

    # Notify Landlord
    execute_db(
        """
        INSERT INTO notifications (user_id, title, message, link)
        VALUES (?, ?, ?, ?)
        """,
        (
            prop["landlord_id"],
            "New Property Inquiry",
            f"You received an inquiry from {seeker_name} ({seeker_phone}) for '{prop['title']}'.",
            "/dashboard/landlord"
        )
    )

    return jsonify({
        "success": True,
        "message": "Your inquiry has been submitted directly to the landlord! You will also be contacted via phone or WhatsApp."
    })


@app.route("/api/viewings", methods=["POST"])
def schedule_viewing():
    """Submits a requested viewing appointment with time preferences."""
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Please sign in to schedule a viewing appointment."}), 401

    data = request.get_json() or {}
    prop_id = data.get("property_id")
    preferred_date = data.get("date", "").strip()
    preferred_time = data.get("time", "").strip()
    notes = data.get("notes", "").strip()

    if not prop_id or not preferred_date or not preferred_time:
        return jsonify({"success": False, "error": "Please choose both a preferred date and time slot."}), 400

    prop = query_db("SELECT id, landlord_id, title FROM properties WHERE id = ?", (prop_id,), one=True)
    if not prop:
        return jsonify({"success": False, "error": "Property not found."}), 404

    execute_db(
        """
        INSERT INTO viewings (property_id, seeker_id, preferred_date, preferred_time, notes)
        VALUES (?, ?, ?, ?, ?)
        """,
        (prop_id, session["user_id"], preferred_date, preferred_time, notes)
    )

    # Notify landlord
    execute_db(
        """
        INSERT INTO notifications (user_id, title, message, link)
        VALUES (?, ?, ?, ?)
        """,
        (
            prop["landlord_id"],
            "New Viewing Request",
            f"{session.get('user_name', 'A house hunter')} requested a viewing for '{prop['title']}' on {preferred_date} ({preferred_time}).",
            "/dashboard/landlord"
        )
    )

    return jsonify({
        "success": True,
        "message": f"Viewing request sent! The landlord will confirm your appointment for {preferred_date}."
    })


@app.route("/api/reports", methods=["POST"])
def submit_report():
    """Reports suspicious listings, fake agents demanding viewing fees, or scam attempts."""
    data = request.get_json() or {}
    prop_id = data.get("property_id")
    reason = data.get("reason", "").strip()
    details = data.get("details", "").strip()

    if not prop_id or not reason or not details:
        return jsonify({"success": False, "error": "Please select a reason and provide details for the scam report."}), 400

    reporter_id = session.get("user_id")

    execute_db(
        """
        INSERT INTO reports (property_id, reporter_id, reason, details)
        VALUES (?, ?, ?, ?)
        """,
        (prop_id, reporter_id, reason, details)
    )

    # Auto-flag property for moderation review if multiple reports exist
    report_count = query_db("SELECT COUNT(*) as c FROM reports WHERE property_id = ?", (prop_id,), one=True)["c"]
    if report_count >= 2:
        execute_db("UPDATE properties SET moderation_status = 'flagged' WHERE id = ?", (prop_id,))

    return jsonify({
        "success": True,
        "message": "Thank you for protecting fellow house hunters! Your report has been submitted to HouseHunt compliance moderators."
    })


@app.route("/api/favorites/toggle", methods=["POST"])
def toggle_favorite():
    """Toggles property in user's saved favorites list."""
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Please sign in to save favorite houses."}), 401

    data = request.get_json() or {}
    prop_id = data.get("property_id")
    user_id = session["user_id"]

    existing = query_db(
        "SELECT id FROM favorites WHERE user_id = ? AND property_id = ?",
        (user_id, prop_id),
        one=True
    )

    if existing:
        execute_db("DELETE FROM favorites WHERE id = ?", (existing["id"],))
        favorited = False
    else:
        execute_db("INSERT INTO favorites (user_id, property_id) VALUES (?, ?)", (user_id, prop_id))
        favorited = True

    new_count = query_db("SELECT COUNT(*) as count FROM favorites WHERE user_id = ?", (user_id,), one=True)["count"]

    return jsonify({"success": True, "favorited": favorited, "favorites_count": new_count})


@app.route("/api/reviews", methods=["POST"])
def submit_review():
    """Lets signed-in seekers leave a star rating and comment on a property."""
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Please sign in to leave a review."}), 401

    data = request.get_json() or {}
    try:
        prop_id = int(data.get("property_id", 0))
        rating = int(data.get("rating", 0))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Invalid rating submitted."}), 400
    comment = (data.get("comment") or "").strip()

    if not prop_id or rating < 1 or rating > 5 or len(comment) < 3:
        return jsonify({"success": False, "error": "Please give 1-5 stars and a short comment."}), 400

    prop = query_db("SELECT id FROM properties WHERE id = ?", (prop_id,), one=True)
    if not prop:
        return jsonify({"success": False, "error": "Property not found."}), 404

    execute_db(
        "INSERT INTO reviews (property_id, user_id, rating, comment) VALUES (?, ?, ?, ?)",
        (prop_id, session["user_id"], rating, comment),
    )
    landlord = query_db("SELECT landlord_id FROM properties WHERE id = ?", (prop_id,), one=True)
    if landlord:
        execute_db(
            "INSERT INTO notifications (user_id, title, message, link) VALUES (?, ?, ?, ?)",
            (
                landlord["landlord_id"],
                "New Tenant Review",
                f"A house seeker rated your listing {rating}/5 stars.",
                f"/properties/{prop_id}",
            ),
        )
    return jsonify({"success": True, "message": "Thank you! Your review helps other house hunters."})


@app.route("/notifications")
@login_required
def notifications():
    """Inbox showing viewing confirmations, inquiries, reviews and admin updates."""
    notes = query_db(
        "SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 50",
        (session["user_id"],),
    )
    return render_template("notifications.html", notifications=notes)


@app.route("/notifications/<int:note_id>/read", methods=["POST"])
@login_required
def mark_notification_read(note_id: int):
    """Marks a single notification as read."""
    execute_db(
        "UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?",
        (note_id, session["user_id"]),
    )
    return jsonify({"success": True})


@app.route("/notifications/read-all", methods=["POST"])
@login_required
def mark_all_notifications_read():
    """Marks every notification for the user as read."""
    execute_db("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (session["user_id"],))
    return jsonify({"success": True})


@app.route("/dashboard/seeker")
@login_required
def dashboard_seeker():
    """Personal hub for seekers: favorites, viewings, inquiries and notifications."""
    user_id = session["user_id"]
    favs = query_db(
        """
        SELECT p.*,
               (SELECT image_url FROM property_images WHERE property_id = p.id ORDER BY is_featured DESC LIMIT 1) as featured_image,
               (p.monthly_rent + p.security_deposit + p.water_deposit + p.electricity_deposit + p.garbage_fee + p.agent_fee) as total_upfront_cost
        FROM favorites f
        JOIN properties p ON f.property_id = p.id
        WHERE f.user_id = ?
        ORDER BY f.created_at DESC LIMIT 6
        """,
        (user_id,),
    )
    viewings = query_db(
        """
        SELECT v.*, p.title as property_title, p.estate, p.town
        FROM viewings v JOIN properties p ON v.property_id = p.id
        WHERE v.seeker_id = ? ORDER BY v.preferred_date DESC LIMIT 10
        """,
        (user_id,),
    )
    inquiries = query_db(
        """
        SELECT i.*, p.title as property_title
        FROM inquiries i JOIN properties p ON i.property_id = p.id
        WHERE i.seeker_id = ? ORDER BY i.created_at DESC LIMIT 10
        """,
        (user_id,),
    )
    notes = query_db(
        "SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 8",
        (user_id,),
    )
    return render_template(
        "dashboard_seeker.html",
        favorites=favs,
        viewings=viewings,
        inquiries=inquiries,
        notifications=notes,
    )


@app.route("/favorites")
@login_required
def favorites():
    """Displays all houses favorited by the logged in user."""
    props = query_db(
        """
        SELECT p.*,
               u.full_name as landlord_name,
               u.is_verified as landlord_is_verified,
               (SELECT image_url FROM property_images WHERE property_id = p.id ORDER BY is_featured DESC LIMIT 1) as featured_image,
               (p.monthly_rent + p.security_deposit + p.water_deposit + p.electricity_deposit + p.garbage_fee + p.agent_fee) as total_upfront_cost
        FROM favorites f
        JOIN properties p ON f.property_id = p.id
        JOIN users u ON p.landlord_id = u.id
        WHERE f.user_id = ?
        ORDER BY f.created_at DESC
        """,
        (session["user_id"],)
    )
    return render_template("favorites.html", properties=props)


# ============================================================================
# Landlord & Agent Dashboard
# ============================================================================
@app.route("/dashboard/landlord")
@role_required("landlord", "agent", "admin")
def dashboard_landlord():
    """Portal for property owners and verified agents."""
    user_id = session["user_id"]

    # If admin viewing landlord dashboard, allow viewing their own or all
    my_properties = query_db(
        """
        SELECT p.*,
               (SELECT image_url FROM property_images WHERE property_id = p.id ORDER BY is_featured DESC LIMIT 1) as featured_image,
               (SELECT COUNT(*) FROM inquiries WHERE property_id = p.id) as inquiry_count,
               (SELECT COUNT(*) FROM viewings WHERE property_id = p.id) as viewing_count,
               (SELECT COUNT(*) FROM favorites WHERE property_id = p.id) as save_count
        FROM properties p
        WHERE p.landlord_id = ?
        ORDER BY p.created_at DESC
        """,
        (user_id,)
    )

    inquiries = query_db(
        """
        SELECT i.*, p.title as property_title
        FROM inquiries i
        JOIN properties p ON i.property_id = p.id
        WHERE p.landlord_id = ?
        ORDER BY i.created_at DESC
        LIMIT 10
        """,
        (user_id,)
    )

    viewings = query_db(
        """
        SELECT v.*, p.title as property_title, u.full_name as seeker_name, u.phone as seeker_phone
        FROM viewings v
        JOIN properties p ON v.property_id = p.id
        JOIN users u ON v.seeker_id = u.id
        WHERE p.landlord_id = ?
        ORDER BY v.preferred_date ASC
        """,
        (user_id,)
    )

    all_amenities = query_db("SELECT * FROM amenities ORDER BY name ASC")

    return render_template(
        "dashboard_landlord.html",
        properties=my_properties,
        inquiries=inquiries,
        viewings=viewings,
        amenities=all_amenities
    )


@app.route("/properties/new", methods=["POST"])
@role_required("landlord", "agent", "admin")
def create_property():
    """Landlord creates a new transparent property listing."""
    user_id = session["user_id"]

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    property_type = request.form.get("property_type", "").strip()
    town = request.form.get("town", "Nairobi").strip()
    estate = request.form.get("estate", "").strip()
    landmark = request.form.get("landmark", "").strip()

    monthly_rent = float(request.form.get("monthly_rent", 0))
    security_deposit = float(request.form.get("security_deposit", 0))
    water_deposit = float(request.form.get("water_deposit", 0))
    electricity_deposit = float(request.form.get("electricity_deposit", 0))
    garbage_fee = float(request.form.get("garbage_fee", 0))
    agent_fee = float(request.form.get("agent_fee", 0))
    service_charge = float(request.form.get("service_charge", 0))

    water_source = request.form.get("water_source", "Borehole + Nairobi City Council (24/7)").strip()
    electricity_type = request.form.get("electricity_type", "Individual Prepaid Token Meter").strip()

    image_urls = request.form.getlist("image_urls")
    selected_amenities = request.form.getlist("amenities")

    # Anti-Scam Duplicate Detection Check
    # Check if a listing with identical title and estate already exists
    duplicate_check = query_db(
        "SELECT id, title, landlord_id FROM properties WHERE title = ? AND estate = ?",
        (title, estate),
        one=True
    )
    if duplicate_check:
        flash("Warning: A property with this exact title already exists in this estate. Please ensure this is not a duplicate.", "warning")

    prop_id = execute_db(
        """
        INSERT INTO properties (
            landlord_id, title, description, property_type, county, town, estate, landmark,
            monthly_rent, security_deposit, water_deposit, electricity_deposit, agent_fee,
            service_charge, water_source, electricity_type, garbage_fee, status, moderation_status
        ) VALUES (?, ?, ?, ?, 'Nairobi', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'available', 'approved')
        """,
        (
            user_id, title, description, property_type, town, estate, landmark,
            monthly_rent, security_deposit, water_deposit, electricity_deposit, agent_fee,
            service_charge, water_source, electricity_type, garbage_fee
        )
    )

    # Insert images
    valid_images = [img.strip() for img in image_urls if img.strip()]
    if not valid_images:
        valid_images = ["https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=1200&q=80"]

    for i, img in enumerate(valid_images):
        execute_db(
            "INSERT INTO property_images (property_id, image_url, is_featured) VALUES (?, ?, ?)",
            (prop_id, img, 1 if i == 0 else 0)
        )

    # Insert amenities
    for amen_id in selected_amenities:
        execute_db(
            "INSERT INTO property_amenities (property_id, amenity_id) VALUES (?, ?)",
            (prop_id, int(amen_id))
        )

    flash(f"Property '{title}' has been successfully published with transparent move-in pricing!", "success")
    return redirect(url_for("dashboard_landlord"))


@app.route("/properties/<int:prop_id>/toggle-status", methods=["POST"])
@role_required("landlord", "agent", "admin")
def toggle_property_status(prop_id: int):
    """Allows landlord to mark a property as Available, Occupied, or Temporarily Unavailable."""
    new_status = request.form.get("status", "available")
    execute_db("UPDATE properties SET status = ?, last_confirmed_date = CURRENT_DATE WHERE id = ?", (new_status, prop_id))
    flash("Property status updated successfully.", "success")
    return redirect(url_for("dashboard_landlord"))


@app.route("/viewings/<int:viewing_id>/status", methods=["POST"])
@role_required("landlord", "agent", "admin")
def update_viewing_status(viewing_id: int):
    """Landlord confirms, reschedules, or cancels viewing request."""
    status = request.form.get("status", "confirmed")
    response_note = request.form.get("response", "").strip()

    execute_db(
        "UPDATE viewings SET status = ?, landlord_response = ? WHERE id = ?",
        (status, response_note, viewing_id)
    )

    viewing = query_db("SELECT * FROM viewings WHERE id = ?", (viewing_id,), one=True)
    if viewing:
        execute_db(
            "INSERT INTO notifications (user_id, title, message, link) VALUES (?, ?, ?, ?)",
            (
                viewing["seeker_id"],
                f"Viewing Request {status.capitalize()}",
                f"The landlord has {status} your viewing request for {viewing['preferred_date']}. Note: {response_note}",
                f"/properties/{viewing['property_id']}"
            )
        )

    flash("Viewing request updated and seeker notified.", "info")
    return redirect(url_for("dashboard_landlord"))


# ============================================================================
# Administrator Dashboard
# ============================================================================
@app.route("/dashboard/admin")
@role_required("admin")
def dashboard_admin():
    """Admin moderation console for verifications, duplicate detection, and scam reports."""
    stats = {
        "total_users": query_db("SELECT COUNT(*) as c FROM users", one=True)["c"],
        "total_properties": query_db("SELECT COUNT(*) as c FROM properties", one=True)["c"],
        "pending_verifications": query_db("SELECT COUNT(*) as c FROM verification_requests WHERE status = 'pending'", one=True)["c"],
        "pending_reports": query_db("SELECT COUNT(*) as c FROM reports WHERE status = 'pending'", one=True)["c"],
    }

    pending_reports = query_db(
        """
        SELECT r.*, p.title as property_title, u.full_name as reporter_name
        FROM reports r
        JOIN properties p ON r.property_id = p.id
        LEFT JOIN users u ON r.reporter_id = u.id
        ORDER BY r.created_at DESC
        """
    )

    verification_requests = query_db(
        """
        SELECT vr.*, u.full_name as user_name, u.role as user_role, u.phone as user_phone, p.title as property_title
        FROM verification_requests vr
        JOIN users u ON vr.user_id = u.id
        LEFT JOIN properties p ON vr.property_id = p.id
        ORDER BY vr.created_at DESC
        """
    )

    all_properties = query_db(
        """
        SELECT p.*, u.full_name as landlord_name
        FROM properties p
        JOIN users u ON p.landlord_id = u.id
        ORDER BY p.created_at DESC
        LIMIT 20
        """
    )

    # Duplicate Scanner: Identify potential duplicate listings by matching titles or estates
    potential_duplicates = query_db(
        """
        SELECT p1.id as id1, p1.title as title1, p1.estate as estate1, p1.monthly_rent as rent1,
               p2.id as id2, p2.title as title2, p2.estate as estate2, p2.monthly_rent as rent2
        FROM properties p1
        JOIN properties p2 ON p1.id < p2.id AND p1.estate = p2.estate AND p1.monthly_rent = p2.monthly_rent
        LIMIT 5
        """
    )

    return render_template(
        "dashboard_admin.html",
        stats=stats,
        pending_reports=pending_reports,
        verification_requests=verification_requests,
        all_properties=all_properties,
        potential_duplicates=potential_duplicates
    )


@app.route("/admin/verification/<int:vr_id>/action", methods=["POST"])
@role_required("admin")
def process_verification(vr_id: int):
    """Admin approves or rejects landlord/agent verification submission."""
    action = request.form.get("action")  # 'approved' or 'rejected'
    vr = query_db("SELECT * FROM verification_requests WHERE id = ?", (vr_id,), one=True)
    if not vr:
        flash("Verification request not found.", "danger")
        return redirect(url_for("dashboard_admin"))

    execute_db(
        "UPDATE verification_requests SET status = ?, reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP WHERE id = ?",
        (action, session["user_id"], vr_id)
    )

    if action == "approved":
        # Update user status to verified
        execute_db(
            "UPDATE users SET is_verified = 1, verification_type = ? WHERE id = ?",
            (vr["document_type"], vr["user_id"])
        )
        if vr["property_id"]:
            execute_db("UPDATE properties SET is_property_verified = 1 WHERE id = ?", (vr["property_id"],))

        # Notify user
        execute_db(
            "INSERT INTO notifications (user_id, title, message, link) VALUES (?, ?, ?, ?)",
            (
                vr["user_id"],
                "Verification Approved!",
                f"Your {vr['document_type']} verification has been verified. The verified badge is now active on your profile and properties.",
                "/dashboard/landlord"
            )
        )
        flash("Verification approved successfully.", "success")
    else:
        execute_db(
            "INSERT INTO notifications (user_id, title, message, link) VALUES (?, ?, ?, ?)",
            (
                vr["user_id"],
                "Verification Notice",
                f"Your verification request for {vr['document_type']} could not be approved. Please review provided details.",
                "/dashboard/landlord"
            )
        )
        flash("Verification request marked as rejected.", "info")

    return redirect(url_for("dashboard_admin"))


@app.route("/admin/reports/<int:rep_id>/resolve", methods=["POST"])
@role_required("admin")
def resolve_report(rep_id: int):
    """Admin resolves or dismisses a scam report."""
    action = request.form.get("status", "resolved")
    execute_db("UPDATE reports SET status = ? WHERE id = ?", (action, rep_id))
    flash("Report status updated.", "info")
    return redirect(url_for("dashboard_admin"))


@app.route("/admin/properties/<int:prop_id>/moderation", methods=["POST"])
@role_required("admin")
def moderate_property(prop_id: int):
    """Admin approves, flags, or suspends a listing."""
    status = request.form.get("moderation_status", "approved")
    execute_db("UPDATE properties SET moderation_status = ? WHERE id = ?", (status, prop_id))
    flash(f"Property moderation status changed to {status}.", "success")
    return redirect(url_for("dashboard_admin"))


# ============================================================================
# Authentication Routes
# ============================================================================
@app.route("/auth", methods=["GET", "POST"])
def auth():
    """Unified login and registration page."""
    tab = request.args.get("tab", "login")

    if request.method == "POST":
        action = request.form.get("action")

        if action == "login":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            user = query_db("SELECT * FROM users WHERE email = ?", (email,), one=True)
            if user and check_password_hash(user["password_hash"], password):
                session["user_id"] = user["id"]
                session["user_name"] = user["full_name"]
                session["user_role"] = user["role"]
                flash(f"Karibu tena, {user['full_name']}! Signed in successfully.", "success")

                next_page = request.args.get("next")
                if next_page and next_page.startswith("/"):
                    return redirect(next_page)
                if user["role"] == "admin":
                    return redirect(url_for("dashboard_admin"))
                if user["role"] in ("landlord", "agent"):
                    return redirect(url_for("dashboard_landlord"))
                return redirect(url_for("index"))
            else:
                flash("Invalid email or password. Please check your credentials.", "danger")
                tab = "login"

        elif action == "register":
            full_name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip().lower()
            phone = request.form.get("phone", "").strip()
            password = request.form.get("password", "")
            role = request.form.get("role", "seeker")

            if not full_name or not email or not phone or not password:
                flash("All fields are required to register.", "danger")
                tab = "register"
            elif query_db("SELECT id FROM users WHERE email = ?", (email,), one=True):
                flash("An account with this email already exists. Please sign in.", "warning")
                tab = "login"
            else:
                password_hash = generate_password_hash(password)
                new_user_id = execute_db(
                    """
                    INSERT INTO users (full_name, email, phone, password_hash, role)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (full_name, email, phone, password_hash, role)
                )
                session["user_id"] = new_user_id
                session["user_name"] = full_name
                session["user_role"] = role

                flash(f"Account created successfully! Welcome to HouseHunt Kenya, {full_name}.", "success")
                if role in ("landlord", "agent"):
                    return redirect(url_for("dashboard_landlord"))
                return redirect(url_for("index"))

    return render_template("auth.html", active_tab=tab)


@app.route("/logout")
def logout():
    """Signs out user and clears session."""
    session.clear()
    flash("You have been signed out safely.", "info")
    return redirect(url_for("index"))


# ============================================================================
# Entry Point
# ============================================================================
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

