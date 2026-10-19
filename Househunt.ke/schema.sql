-- HouseHunt Kenya Database Schema (SQLite)
-- Designed for complete trust, transparency, and Kenyan rental market workflows

PRAGMA foreign_keys = ON;

-- 1. Users Table (House Seekers, Landlords, Verified Agents, Admins)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'seeker' CHECK (role IN ('seeker', 'landlord', 'agent', 'admin')),
    is_verified INTEGER NOT NULL DEFAULT 0,
    verification_type TEXT,
    avatar_url TEXT DEFAULT '/static/images/default_avatar.png',
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Properties Table with transparent costs & utility details
CREATE TABLE IF NOT EXISTS properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    landlord_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    property_type TEXT NOT NULL CHECK (property_type IN ('Bedsitter', 'Single Room', 'Studio', '1-Bedroom', '2-Bedroom', '3-Bedroom', 'Maisonette', 'Villa')),
    county TEXT DEFAULT 'Nairobi',
    town TEXT NOT NULL,
    estate TEXT NOT NULL,
    landmark TEXT,
    latitude REAL,
    longitude REAL,
    monthly_rent REAL NOT NULL CHECK (monthly_rent > 0),
    security_deposit REAL NOT NULL DEFAULT 0,
    water_deposit REAL NOT NULL DEFAULT 0,
    electricity_deposit REAL NOT NULL DEFAULT 0,
    agent_fee REAL NOT NULL DEFAULT 0,
    service_charge REAL NOT NULL DEFAULT 0,
    water_source TEXT NOT NULL DEFAULT 'Borehole + City Council (24/7)',
    electricity_type TEXT NOT NULL DEFAULT 'Individual Prepaid Token Meter',
    garbage_fee REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'available' CHECK (status IN ('available', 'occupied', 'temporarily_unavailable')),
    moderation_status TEXT NOT NULL DEFAULT 'approved' CHECK (moderation_status IN ('pending', 'approved', 'rejected', 'flagged')),
    is_promoted INTEGER NOT NULL DEFAULT 0,
    is_property_verified INTEGER NOT NULL DEFAULT 0,
    last_confirmed_date DATE DEFAULT CURRENT_DATE,
    views_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (landlord_id) REFERENCES users (id) ON DELETE CASCADE
);

-- 3. Property Images
CREATE TABLE IF NOT EXISTS property_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    image_url TEXT NOT NULL,
    is_featured INTEGER NOT NULL DEFAULT 0,
    caption TEXT,
    FOREIGN KEY (property_id) REFERENCES properties (id) ON DELETE CASCADE
);

-- 4. Amenities Catalog
CREATE TABLE IF NOT EXISTS amenities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    icon TEXT NOT NULL,
    category TEXT DEFAULT 'convenience'
);

-- 5. Property Amenities Junction Table
CREATE TABLE IF NOT EXISTS property_amenities (
    property_id INTEGER NOT NULL,
    amenity_id INTEGER NOT NULL,
    PRIMARY KEY (property_id, amenity_id),
    FOREIGN KEY (property_id) REFERENCES properties (id) ON DELETE CASCADE,
    FOREIGN KEY (amenity_id) REFERENCES amenities (id) ON DELETE CASCADE
);

-- 6. Favorites
CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    property_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, property_id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (property_id) REFERENCES properties (id) ON DELETE CASCADE
);

-- 7. Inquiries
CREATE TABLE IF NOT EXISTS inquiries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    seeker_id INTEGER,
    seeker_name TEXT NOT NULL,
    seeker_phone TEXT NOT NULL,
    seeker_email TEXT,
    message TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'read', 'responded')),
    response_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties (id) ON DELETE CASCADE,
    FOREIGN KEY (seeker_id) REFERENCES users (id) ON DELETE SET NULL
);

-- 8. Viewing Appointments
CREATE TABLE IF NOT EXISTS viewings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    seeker_id INTEGER NOT NULL,
    preferred_date DATE NOT NULL,
    preferred_time TEXT NOT NULL,
    notes TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'rescheduled', 'cancelled', 'completed')),
    landlord_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties (id) ON DELETE CASCADE,
    FOREIGN KEY (seeker_id) REFERENCES users (id) ON DELETE CASCADE
);

-- 9. Reviews
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT NOT NULL,
    is_verified_tenant INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- 10. Reports (Anti-scam & fake listing reporting)
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    reporter_id INTEGER,
    reason TEXT NOT NULL CHECK (reason IN (
        'fake_listing',
        'agent_demands_viewing_fee',
        'duplicate_listing',
        'incorrect_rent',
        'property_occupied',
        'unreachable_contact',
        'other'
    )),
    details TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'investigating', 'resolved', 'dismissed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties (id) ON DELETE CASCADE,
    FOREIGN KEY (reporter_id) REFERENCES users (id) ON DELETE SET NULL
);

-- 11. Verification Requests (Landlord ID, agent registration, title deeds)
CREATE TABLE IF NOT EXISTS verification_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    property_id INTEGER,
    document_type TEXT NOT NULL CHECK (document_type IN ('National ID', 'Title Deed', 'Utility Bill', 'Agent License', 'Power of Attorney')),
    document_reference TEXT,
    notes TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    reviewed_by INTEGER,
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (property_id) REFERENCES properties (id) ON DELETE SET NULL,
    FOREIGN KEY (reviewed_by) REFERENCES users (id) ON DELETE SET NULL
);

-- 12. Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    link TEXT,
    is_read INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Create helpful indexes for fast search performance
CREATE INDEX IF NOT EXISTS idx_properties_estate ON properties(estate);
CREATE INDEX IF NOT EXISTS idx_properties_town ON properties(town);
CREATE INDEX IF NOT EXISTS idx_properties_rent ON properties(monthly_rent);
CREATE INDEX IF NOT EXISTS idx_properties_type ON properties(property_type);
CREATE INDEX IF NOT EXISTS idx_properties_status ON properties(status);
CREATE INDEX IF NOT EXISTS idx_properties_moderation ON properties(moderation_status);

