#!/usr/bin/env python3
"""
LookingForHome — Standalone Open Portals Feeder CLI
Populates or refreshes properties from open real estate portals into the database (MySQL/MariaDB or SQLite).
"""
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.database import DBContext, init_db, get_properties
from app.services.portal_feeder import feed_open_portal_properties

def main():
    print("=" * 65)
    print("🏠 LOOKINGFORHOME — OPEN PORTALS PROPERTY FEEDER")
    print("=" * 65)
    
    # Ensure database schema is initialized
    init_db()

    with DBContext() as db:
        print(f"• Database Engine: {db.engine.upper()}")
        count = feed_open_portal_properties(db)
        print(f"• Open portal properties fed: {count}")

    props = get_properties()
    print(f"• Total active properties in database now: {len(props)}")
    cities = sorted(list(set(p['city'] for p in props)))
    print(f"• Active cities ({len(cities)}): {', '.join(cities)}")
    print("=" * 65)
    print("✅ Open portal synchronization complete!")

if __name__ == "__main__":
    main()
