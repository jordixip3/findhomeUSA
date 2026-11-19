"""
Database layer for FindHome USA
Supports MySQL (MariaDB) with graceful SQLite fallback
"""
import os
import json
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

DB_TYPE_ENV = os.getenv("DB_TYPE", "").strip().lower()
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "lookingforhome")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "LookingForHome2026!")
MYSQL_DB = os.getenv("MYSQL_DB", "findhome_usa")

SQLITE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "findhome.db")
_ACTIVE_ENGINE = None

INITIAL_PROPERTIES = [
    {
        "title": "Modern 4-Bedroom Loft with Skyline Views in Lower East Side",
        "subdivision": "New York",
        "subdivision_code": "NY",
        "city": "New York City",
        "address": "142 Ludlow St, New York, NY 10002",
        "neighborhood": "Lower East Side",
        "latitude": 40.7208,
        "longitude": -73.9882,
        "total_rent": 4400,
        "bedrooms": 4,
        "bathrooms": 2,
        "surface": 1450,
        "portal": "Zillow Premier",
        "url": "https://www.zillow.com/homedetails/142-Ludlow-St-New-York-NY/prop1",
        "desc": "Stunning loft featuring exposed brick walls, modern kitchen island, central AC, and oversized windows overlooking Manhattan.",
        "contact_name": "Manhattan Living Group",
        "contact_phone": "+1 (212) 555-0192",
        "contact_agency": "NYC Premier Properties"
    },
    {
        "title": "Creative 3-Bedroom Flat near Williamsburg Waterfront",
        "subdivision": "New York",
        "subdivision_code": "NY",
        "city": "Brooklyn",
        "address": "88 North 6th St, Brooklyn, NY 11249",
        "neighborhood": "Williamsburg",
        "latitude": 40.7185,
        "longitude": -73.9615,
        "total_rent": 3600,
        "bedrooms": 3,
        "bathrooms": 2,
        "surface": 1280,
        "portal": "StreetEasy",
        "url": "https://streeteasy.com/rental/williamsburg-loft-88",
        "desc": "Bright and spacious Brooklyn flat steps from Bedford Ave subway, rooftop access with skyline panorama.",
        "contact_name": "Brooklyn Co-Living",
        "contact_phone": "+1 (718) 555-0144",
        "contact_agency": "King's County Realty"
    },
    {
        "title": "Sunlit 4-Bedroom Craftsman Home in Silver Lake",
        "subdivision": "California",
        "subdivision_code": "CA",
        "city": "Los Angeles",
        "address": "2810 Sunset Blvd, Los Angeles, CA 90026",
        "neighborhood": "Silver Lake",
        "latitude": 34.0811,
        "longitude": -118.2721,
        "total_rent": 4200,
        "bedrooms": 4,
        "bathrooms": 2,
        "surface": 1850,
        "portal": "Redfin Verified MLS",
        "url": "https://www.redfin.com/CA/Los-Angeles/2810-Sunset-Blvd/home/prop2",
        "desc": "Charming California bungalow with open patio, hardwood floors, high-speed fiber internet, and dedicated workspace.",
        "contact_name": "West Coast Living",
        "contact_phone": "+1 (213) 555-0188",
        "contact_agency": "Angeleno Homes"
    },
    {
        "title": "Tech-Savvy 3-Bedroom Apartment in Mission District",
        "subdivision": "California",
        "subdivision_code": "CA",
        "city": "San Francisco",
        "address": "820 Valencia St, San Francisco, CA 94110",
        "neighborhood": "Mission District",
        "latitude": 37.7599,
        "longitude": -122.4215,
        "total_rent": 4500,
        "bedrooms": 3,
        "bathrooms": 2,
        "surface": 1350,
        "portal": "Zillow Premier",
        "url": "https://www.zillow.com/homedetails/820-Valencia-St-San-Francisco-CA/prop3",
        "desc": "High-ceiling Victorian renovated with smart thermostat, in-unit laundry, and designer quartz countertops.",
        "contact_name": "Bay Area Hub",
        "contact_phone": "+1 (415) 555-0112",
        "contact_agency": "Golden Gate Realty"
    },
    {
        "title": "Silicon Hills 4-Bedroom Co-Living House in Rainey St District",
        "subdivision": "Texas",
        "subdivision_code": "TX",
        "city": "Austin",
        "address": "74 Rainey St, Austin, TX 78701",
        "neighborhood": "Downtown / Rainey",
        "latitude": 30.2588,
        "longitude": -97.7392,
        "total_rent": 2800,
        "bedrooms": 4,
        "bathrooms": 3,
        "surface": 2100,
        "portal": "Apartments.com Network",
        "url": "https://www.apartments.com/rainey-street-austin-tx/prop4",
        "desc": "Spacious Austin home with private backyard pool, barbecue lounge, EV charger, and minutes from Lady Bird Lake.",
        "contact_name": "Austin Tech Pods",
        "contact_phone": "+1 (512) 555-0177",
        "contact_agency": "Lone Star Living"
    },
    {
        "title": "Chic 3-Bedroom Flat with Balcony in South Beach",
        "subdivision": "Florida",
        "subdivision_code": "FL",
        "city": "Miami",
        "address": "1120 Ocean Dr, Miami Beach, FL 33139",
        "neighborhood": "South Beach",
        "latitude": 25.7825,
        "longitude": -80.1305,
        "total_rent": 3300,
        "bedrooms": 3,
        "bathrooms": 2,
        "surface": 1400,
        "portal": "Zillow Premier",
        "url": "https://www.zillow.com/homedetails/1120-Ocean-Dr-Miami-Beach-FL/prop5",
        "desc": "Art Deco oceanview residence with central air, marble finishes, designer lighting, and heated community pool.",
        "contact_name": "Biscayne Bay Living",
        "contact_phone": "+1 (305) 555-0133",
        "contact_agency": "Sunshine State Realty"
    },
    {
        "title": "Cozy 4-Bedroom Craftsman in Capitol Hill",
        "subdivision": "Washington",
        "subdivision_code": "WA",
        "city": "Seattle",
        "address": "415 E Pine St, Seattle, WA 98122",
        "neighborhood": "Capitol Hill",
        "latitude": 47.6152,
        "longitude": -122.3242,
        "total_rent": 3400,
        "bedrooms": 4,
        "bathrooms": 2,
        "surface": 1720,
        "portal": "Redfin Verified MLS",
        "url": "https://www.redfin.com/WA/Seattle/415-E-Pine-St/home/prop6",
        "desc": "Lush Seattle retreat with cedar deck, wood-burning stove, chef kitchen, and quick transit to Amazon and Microsoft campuses.",
        "contact_name": "Emerald City Homes",
        "contact_phone": "+1 (206) 555-0165",
        "contact_agency": "Pacific Northwest Realty"
    },
    {
        "title": "Loft-Style 3-Bedroom Apartment in Lincoln Park",
        "subdivision": "Illinois",
        "subdivision_code": "IL",
        "city": "Chicago",
        "address": "2210 N Clark St, Chicago, IL 60614",
        "neighborhood": "Lincoln Park",
        "latitude": 41.9224,
        "longitude": -87.6385,
        "total_rent": 2900,
        "bedrooms": 3,
        "bathrooms": 2,
        "surface": 1550,
        "portal": "Apartments.com Network",
        "url": "https://www.apartments.com/lincoln-park-chicago-il/prop7",
        "desc": "Timeless timber loft with 14ft ceilings, exposed ductwork, fitness center in building, and steps from the lakefront trail.",
        "contact_name": "Windy City Co-Op",
        "contact_phone": "+1 (312) 555-0199",
        "contact_agency": "Midwest Metro Realty"
    },
    {
        "title": "Historic Brownstone 4-Bed Flat in Back Bay",
        "subdivision": "Massachusetts",
        "subdivision_code": "MA",
        "city": "Boston",
        "address": "180 Commonwealth Ave, Boston, MA 02116",
        "neighborhood": "Back Bay",
        "latitude": 42.3518,
        "longitude": -71.0792,
        "total_rent": 4200,
        "bedrooms": 4,
        "bathrooms": 2,
        "surface": 1680,
        "portal": "Realtor.com Direct",
        "url": "https://www.realtor.com/realestateandhomes-detail/180-Commonwealth-Ave-Boston-MA/prop8",
        "desc": "Classic Boston architectural gem with ornamental fireplaces, bay windows, modern stainless appliances, near MIT and Harvard.",
        "contact_name": "New England Co-Living",
        "contact_phone": "+1 (617) 555-0121",
        "contact_agency": "Beacon Hill Partners"
    },
    {
        "title": "Rocky Mountain RiNo Arts District 3-Bedroom Loft",
        "subdivision": "Colorado",
        "subdivision_code": "CO",
        "city": "Denver",
        "address": "2901 Blake St, Denver, CO 80205",
        "neighborhood": "RiNo Arts District",
        "latitude": 39.7635,
        "longitude": -104.9818,
        "total_rent": 2700,
        "bedrooms": 3,
        "bathrooms": 2,
        "surface": 1490,
        "portal": "HotPads Co-Living",
        "url": "https://hotpads.com/2901-blake-st-denver-co/prop9",
        "desc": "Industrial chic living space surrounded by breweries, art murals, bike paths, and stunning mountain view balcony.",
        "contact_name": "Mile High Living",
        "contact_phone": "+1 (303) 555-0145",
        "contact_agency": "Rockies Real Estate"
    }
]
SUBDIVISIONS = [
    [
        "Alabama",
        "AL"
    ],
    [
        "Alaska",
        "AK"
    ],
    [
        "Arizona",
        "AZ"
    ],
    [
        "Arkansas",
        "AR"
    ],
    [
        "California",
        "CA"
    ],
    [
        "Colorado",
        "CO"
    ],
    [
        "Connecticut",
        "CT"
    ],
    [
        "Delaware",
        "DE"
    ],
    [
        "District of Columbia",
        "DC"
    ],
    [
        "Florida",
        "FL"
    ],
    [
        "Georgia",
        "GA"
    ],
    [
        "Hawaii",
        "HI"
    ],
    [
        "Idaho",
        "ID"
    ],
    [
        "Illinois",
        "IL"
    ],
    [
        "Indiana",
        "IN"
    ],
    [
        "Iowa",
        "IA"
    ],
    [
        "Kansas",
        "KS"
    ],
    [
        "Kentucky",
        "KY"
    ],
    [
        "Louisiana",
        "LA"
    ],
    [
        "Maine",
        "ME"
    ],
    [
        "Maryland",
        "MD"
    ],
    [
        "Massachusetts",
        "MA"
    ],
    [
        "Michigan",
        "MI"
    ],
    [
        "Minnesota",
        "MN"
    ],
    [
        "Mississippi",
        "MS"
    ],
    [
        "Missouri",
        "MO"
    ],
    [
        "Montana",
        "MT"
    ],
    [
        "Nebraska",
        "NE"
    ],
    [
        "Nevada",
        "NV"
    ],
    [
        "New Hampshire",
        "NH"
    ],
    [
        "New Jersey",
        "NJ"
    ],
    [
        "New Mexico",
        "NM"
    ],
    [
        "New York",
        "NY"
    ],
    [
        "North Carolina",
        "NC"
    ],
    [
        "North Dakota",
        "ND"
    ],
    [
        "Ohio",
        "OH"
    ],
    [
        "Oklahoma",
        "OK"
    ],
    [
        "Oregon",
        "OR"
    ],
    [
        "Pennsylvania",
        "PA"
    ],
    [
        "Rhode Island",
        "RI"
    ],
    [
        "South Carolina",
        "SC"
    ],
    [
        "South Dakota",
        "SD"
    ],
    [
        "Tennessee",
        "TN"
    ],
    [
        "Texas",
        "TX"
    ],
    [
        "Utah",
        "UT"
    ],
    [
        "Vermont",
        "VT"
    ],
    [
        "Virginia",
        "VA"
    ],
    [
        "Washington",
        "WA"
    ],
    [
        "West Virginia",
        "WV"
    ],
    [
        "Wisconsin",
        "WI"
    ],
    [
        "Wyoming",
        "WY"
    ]
]

def detect_engine() -> str:
    global _ACTIVE_ENGINE
    if _ACTIVE_ENGINE is not None:
        return _ACTIVE_ENGINE
    if DB_TYPE_ENV == "sqlite":
        _ACTIVE_ENGINE = "sqlite"
        return _ACTIVE_ENGINE
    try:
        import pymysql
        conn = pymysql.connect(
            host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER,
            password=MYSQL_PASSWORD, database=MYSQL_DB, connect_timeout=3
        )
        conn.close()
        _ACTIVE_ENGINE = "mysql"
        return _ACTIVE_ENGINE
    except Exception:
        _ACTIVE_ENGINE = "sqlite"
        return _ACTIVE_ENGINE

def get_raw_connection():
    engine = detect_engine()
    if engine == "mysql":
        import pymysql
        import pymysql.cursors
        return pymysql.connect(
            host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER,
            password=MYSQL_PASSWORD, database=MYSQL_DB, charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor, autocommit=False
        )
    else:
        import sqlite3
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    engine = detect_engine()
    conn = get_raw_connection()
    cursor = conn.cursor()

    if engine == "mysql":
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS properties (
            id VARCHAR(64) PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            city VARCHAR(100) NOT NULL,
            subdivision VARCHAR(100) NOT NULL,
            subdivision_code VARCHAR(10),
            address VARCHAR(255),
            neighborhood VARCHAR(100),
            latitude DOUBLE PRECISION,
            longitude DOUBLE PRECISION,
            total_rent DOUBLE PRECISION NOT NULL,
            ideal_roommates INT DEFAULT 4,
            bedrooms INT NOT NULL,
            bathrooms INT NOT NULL,
            surface INT NOT NULL,
            has_elevator TINYINT(1) DEFAULT 1,
            is_exterior TINYINT(1) DEFAULT 1,
            is_furnished TINYINT(1) DEFAULT 1,
            has_terrace TINYINT(1) DEFAULT 0,
            has_air_con TINYINT(1) DEFAULT 0,
            source_portal VARCHAR(100) DEFAULT 'Direct Portal',
            source_url VARCHAR(500),
            property_type VARCHAR(50) DEFAULT 'apartment',
            images JSON,
            contact_name VARCHAR(150),
            contact_phone VARCHAR(50),
            contact_agency VARCHAR(150),
            status VARCHAR(30) DEFAULT 'available',
            created_at VARCHAR(50)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS access_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ip VARCHAR(64) NOT NULL,
            country VARCHAR(100),
            country_code VARCHAR(10),
            region VARCHAR(100),
            city VARCHAR(100),
            latitude DOUBLE PRECISION,
            longitude DOUBLE PRECISION,
            path VARCHAR(255),
            method VARCHAR(10),
            status_code INT,
            user_agent TEXT,
            device_type VARCHAR(30),
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS whatsapp_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sender_phone VARCHAR(50),
            sender_name VARCHAR(100),
            message_body TEXT,
            response_body TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        conn.commit()

        # Check if properties exist
        cursor.execute("SELECT COUNT(*) AS cnt FROM properties")
        row = cursor.fetchone()
        cnt = row["cnt"] if isinstance(row, dict) else row[0]
        if cnt == 0:
            seed_data(cursor, engine)
            conn.commit()

    else:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS properties (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            city TEXT NOT NULL,
            subdivision TEXT NOT NULL,
            subdivision_code TEXT,
            address TEXT,
            neighborhood TEXT,
            latitude REAL,
            longitude REAL,
            total_rent REAL NOT NULL,
            ideal_roommates INTEGER DEFAULT 4,
            bedrooms INTEGER NOT NULL,
            bathrooms INTEGER NOT NULL,
            surface INTEGER NOT NULL,
            has_elevator INTEGER DEFAULT 1,
            is_exterior INTEGER DEFAULT 1,
            is_furnished INTEGER DEFAULT 1,
            has_terrace INTEGER DEFAULT 0,
            has_air_con INTEGER DEFAULT 0,
            source_portal TEXT,
            source_url TEXT,
            property_type TEXT,
            images TEXT,
            contact_name TEXT,
            contact_phone TEXT,
            contact_agency TEXT,
            status TEXT DEFAULT 'available',
            created_at TEXT
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL,
            country TEXT,
            country_code TEXT,
            region TEXT,
            city TEXT,
            latitude REAL,
            longitude REAL,
            path TEXT,
            method TEXT,
            status_code INTEGER,
            user_agent TEXT,
            device_type TEXT,
            timestamp TEXT
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS whatsapp_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_phone TEXT,
            sender_name TEXT,
            message_body TEXT,
            response_body TEXT,
            timestamp TEXT
        );
        """)
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM properties")
        if cursor.fetchone()[0] == 0:
            seed_data(cursor, engine)
            conn.commit()

    conn.close()

def seed_data(cursor, engine):
    img_list = [
        "static/images/prop-mad-01-1.jpg", "static/images/prop-mad-01-2.jpg",
        "static/images/prop-bcn-01-1.jpg", "static/images/prop-par-01-1.jpg",
        "static/images/prop-ber-01-1.jpg", "static/images/prop-lis-01-1.jpg"
    ]
    for idx, p in enumerate(INITIAL_PROPERTIES):
        pid = f"usa-prop-{idx+1:02d}"
        imgs = json.dumps([img_list[idx % len(img_list)]])
        now = datetime.now(timezone.utc).isoformat()
        if engine == "mysql":
            cursor.execute("""
            INSERT INTO properties (
                id, title, description, city, subdivision, subdivision_code, address, neighborhood,
                latitude, longitude, total_rent, ideal_roommates, bedrooms, bathrooms, surface,
                has_elevator, is_exterior, is_furnished, has_terrace, has_air_con,
                source_portal, source_url, property_type, images, contact_name, contact_phone, contact_agency, status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                pid, p["title"], p["desc"], p["city"], p["subdivision"], p.get("subdivision_code", ""),
                p["address"], p["neighborhood"], p["latitude"], p["longitude"], p["total_rent"],
                p.get("ideal_roommates", p["bedrooms"]), p["bedrooms"], p["bathrooms"], p["surface"],
                1, 1, 1, 1, 1, p["portal"], p["url"], "apartment", imgs,
                p["contact_name"], p["contact_phone"], p["contact_agency"], "available", now
            ))
        else:
            cursor.execute("""
            INSERT INTO properties (
                id, title, description, city, subdivision, subdivision_code, address, neighborhood,
                latitude, longitude, total_rent, ideal_roommates, bedrooms, bathrooms, surface,
                has_elevator, is_exterior, is_furnished, has_terrace, has_air_con,
                source_portal, source_url, property_type, images, contact_name, contact_phone, contact_agency, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pid, p["title"], p["desc"], p["city"], p["subdivision"], p.get("subdivision_code", ""),
                p["address"], p["neighborhood"], p["latitude"], p["longitude"], p["total_rent"],
                p.get("ideal_roommates", p["bedrooms"]), p["bedrooms"], p["bathrooms"], p["surface"],
                1, 1, 1, 1, 1, p["portal"], p["url"], "apartment", imgs,
                p["contact_name"], p["contact_phone"], p["contact_agency"], "available", now
            ))

def get_properties(city=None, subdivision=None, portal=None, min_bedrooms=None, max_total_rent=None) -> List[Dict[str, Any]]:
    conn = get_raw_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM properties WHERE 1=1"
    params = []

    if city:
        query += " AND LOWER(city) LIKE %s" if detect_engine() == "mysql" else " AND LOWER(city) LIKE ?"
        params.append(f"%{city.lower()}%")
    if subdivision:
        query += " AND (LOWER(subdivision) LIKE %s OR LOWER(subdivision_code) LIKE %s)" if detect_engine() == "mysql" else " AND (LOWER(subdivision) LIKE ? OR LOWER(subdivision_code) LIKE ?)"
        params.extend([f"%{subdivision.lower()}%", f"%{subdivision.lower()}%"])
    if portal:
        query += " AND LOWER(source_portal) LIKE %s" if detect_engine() == "mysql" else " AND LOWER(source_portal) LIKE ?"
        params.append(f"%{portal.lower()}%")
    if min_bedrooms:
        query += " AND bedrooms >= %s" if detect_engine() == "mysql" else " AND bedrooms >= ?"
        params.append(int(min_bedrooms))
    if max_total_rent:
        query += " AND total_rent <= %s" if detect_engine() == "mysql" else " AND total_rent <= ?"
        params.append(float(max_total_rent))

    query += " ORDER BY total_rent ASC"
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()

    results = []
    for r in rows:
        d = dict(r)
        if isinstance(d.get("images"), str):
            try:
                d["images"] = json.loads(d["images"])
            except Exception:
                d["images"] = []
        d["rent_per_person"] = round(d["total_rent"] / max(1, d.get("ideal_roommates", d.get("bedrooms", 4))))
        results.append(d)

    conn.close()
    return results

def get_property(prop_id: str) -> Optional[Dict[str, Any]]:
    conn = get_raw_connection()
    cursor = conn.cursor()
    q = "SELECT * FROM properties WHERE id = %s" if detect_engine() == "mysql" else "SELECT * FROM properties WHERE id = ?"
    cursor.execute(q, (prop_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    if isinstance(d.get("images"), str):
        try:
            d["images"] = json.loads(d["images"])
        except Exception:
            d["images"] = []
    d["rent_per_person"] = round(d["total_rent"] / max(1, d.get("ideal_roommates", d.get("bedrooms", 4))))
    return d

def record_access_log(ip, country, country_code, region, city, latitude, longitude, path, method, status_code, user_agent, device_type):
    try:
        conn = get_raw_connection()
        cursor = conn.cursor()
        engine = detect_engine()
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        if engine == "mysql":
            cursor.execute("""
            INSERT INTO access_logs (ip, country, country_code, region, city, latitude, longitude, path, method, status_code, user_agent, device_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (ip, country, country_code, region, city, latitude, longitude, path, method, status_code, user_agent, device_type))
        else:
            cursor.execute("""
            INSERT INTO access_logs (ip, country, country_code, region, city, latitude, longitude, path, method, status_code, user_agent, device_type, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (ip, country, country_code, region, city, latitude, longitude, path, method, status_code, user_agent, device_type, now))
        conn.commit()
        conn.close()
    except Exception:
        pass

def get_access_logs(limit: int = 100) -> List[Dict[str, Any]]:
    conn = get_raw_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM access_logs ORDER BY id DESC LIMIT {int(limit)}")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def record_whatsapp_log(sender_phone, sender_name, message_body, response_body):
    try:
        conn = get_raw_connection()
        cursor = conn.cursor()
        engine = detect_engine()
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        if engine == "mysql":
            cursor.execute("""
            INSERT INTO whatsapp_logs (sender_phone, sender_name, message_body, response_body)
            VALUES (%s, %s, %s, %s)
            """, (sender_phone, sender_name, message_body, response_body))
        else:
            cursor.execute("""
            INSERT INTO whatsapp_logs (sender_phone, sender_name, message_body, response_body, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """, (sender_phone, sender_name, message_body, response_body, now))
        conn.commit()
        conn.close()
    except Exception:
        pass

def get_whatsapp_logs(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_raw_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM whatsapp_logs ORDER BY id DESC LIMIT {int(limit)}")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
