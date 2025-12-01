from app.core.database import SessionLocal
from sqlalchemy import text
from datetime import datetime, date
from app.models.hostel import Hostel


def seed_sample_data():
    db = SessionLocal()
    try:
        print("🌱 Seeding sample data...\n")

        # ================================
        # 1. LOCATIONS
        # ================================
        db.execute(text("""
            INSERT INTO locations (city) VALUES
            ('Hyderabad'),
            ('Bangalore'),
            ('Chennai'),
            ('Pune'),
            ('Mumbai')
            ON CONFLICT DO NOTHING;
        """))
        db.commit()
        print("📍 Inserted locations")

        # ================================
        # 2. HOSTELS
        # ================================
        db.execute(text("""
            INSERT INTO hostels (hostel_name, description, full_address, hostel_type,
                                 contact_email, contact_phone, amenities, rules,
                                 check_in, check_out, total_beds, current_occupancy,
                                 monthly_revenue, visibility, is_featured, location_id)
            VALUES
            ('Elite Hostel', 'Modern hostel in Hyderabad', '12 Road St, Hyderabad', 'Men',
             'elite@example.com', '9876543210', 'WiFi, AC, Laundry', 'No smoking',
             '09:00', '21:00', 60, 55, 35000.50, 'public', TRUE, (SELECT id FROM locations WHERE city='Hyderabad' LIMIT 1)),

            ('Sunrise Hostel', 'Comfort stay near city center', '45 Park Ave, Bangalore', 'Women',
             'sunrise@example.com', '9876543211', 'WiFi, Gym, Breakfast', 'No loud music',
             '09:00', '22:00', 50, 44, 31000.00, 'public', TRUE, (SELECT id FROM locations WHERE city='Bangalore' LIMIT 1)),

            ('GreenStay Hostel', 'Eco-friendly hostel', '88 Green Rd, Chennai', 'Co-ed',
             'greenstay@example.com', '9876543212', 'WiFi, Garden, Hot Water', 'No smoking',
             '08:00', '20:00', 40, 34, 28000.30, 'public', FALSE, (SELECT id FROM locations WHERE city='Chennai' LIMIT 1)),

            ('BlueMoon Hostel', 'Quiet and peaceful stay', '5 Beach Rd, Pune', 'Men',
             'bluemoon@example.com', '9876543213', 'WiFi, Laundry, TV Lounge', 'No alcohol',
             '10:00', '21:00', 45, 35, 21000.00, 'public', FALSE, (SELECT id FROM locations WHERE city='Pune' LIMIT 1)),

            ('CozyNest Hostel', 'Budget stay for students', '10 Hill St, Mumbai', 'Co-ed',
             'cozynest@example.com', '9876543214', 'WiFi, Breakfast', 'No parties',
             '09:00', '22:00', 55, 40, 20000.00, 'public', FALSE, (SELECT id FROM locations WHERE city='Mumbai' LIMIT 1)),

            ('Sample Hostel', 'A sample hostel for testing.', '123 Test Street', 'public',
             'test@example.com', '1234567890', 'WiFi, Parking', 'No smoking',
             '14:00:00', '10:00:00', 100, 50, 10000, 'public', FALSE, (SELECT id FROM locations WHERE city='Hyderabad' LIMIT 1))
            ON CONFLICT DO NOTHING;
        """))
        db.commit()
        print("🏨 Inserted hostels\n")

        # ================================
        # 3. ADMINS
        # ================================
        db.execute(text("""
            INSERT INTO admins (admin_name, email, is_active)
            VALUES
            ('Admin User 1', 'admin1@example.com', TRUE),
            ('Admin User 2', 'admin2@example.com', TRUE)
            ON CONFLICT DO NOTHING;
        """))
        db.commit()
        print("👨‍💼 Inserted admins\n")

        # ================================
        # 4. REVENUE
        # ================================
        db.execute(text("""
            INSERT INTO revenues (hostel_id, month, revenue)
            SELECT id, date_trunc('month', current_date)::date, COALESCE(monthly_revenue, 0)
            FROM hostels
            ON CONFLICT DO NOTHING;
        """))
        db.commit()
        print("💰 Inserted revenue entries\n")

        # ================================
        # 5. OCCUPANCY
        # ================================
        db.execute(text("""
            INSERT INTO occupancies (hostel_id, month, occupancy_rate)
            SELECT id, date_trunc('month', current_date)::date,
                   ROUND((current_occupancy::numeric / total_beds) * 100, 2)
            FROM hostels
            ON CONFLICT DO NOTHING;
        """))
        db.commit()
        print("📊 Inserted occupancy entries\n")

        # ================================
        # 6. ACTIVITIES
        # ================================
        db.execute(text("""
            INSERT INTO activities (entity_name, entity_type, action)
            VALUES
            ('Elite Hostel', 'hostel', 'Created new hostel record'),
            ('Sunrise Hostel', 'hostel', 'Updated monthly revenue'),
            ('GreenStay Hostel', 'hostel', 'Occupancy data synced'),
            ('Admin User 1', 'admin', 'Activated account'),
            ('Admin User 2', 'admin', 'Added new hostel')
            ON CONFLICT DO NOTHING;
        """))
        db.commit()
        print("📝 Inserted activity logs\n")

        # ================================
        # SHOW PREVIEW OF SEEDED DATA
        # ================================
        print("\n📌 Preview of inserted data:\n")

        hostels = db.execute(text("SELECT id, hostel_name, monthly_revenue FROM hostels ORDER BY id")).fetchall()
        print("🏨 Hostels:")
        for h in hostels:
            print(f" → {h}")

        occupancies = db.execute(text("SELECT * FROM occupancies ORDER BY id")).fetchall()
        print("\n📊 Occupancies:")
        for o in occupancies:
            print(f" → {o}")

        revenues = db.execute(text("SELECT * FROM revenues ORDER BY id")).fetchall()
        print("\n💰 Revenues:")
        for r in revenues:
            print(f" → {r}")

        print("\n✅ Sample data inserted successfully!")

    except Exception as e:
        print("\n❌ Error during seeding:", e)
        db.rollback()
    finally:
        db.close()


def seed_hostel():
    db = SessionLocal()
    try:
        # Ensure hostel with id=6 exists
        if not db.query(Hostel).filter(Hostel.id == 6).first():
            hostel = Hostel(
                id=6,
                hostel_name="Sample Hostel",
                description="A sample hostel for testing.",
                full_address="123 Test Street",
                hostel_type="public",
                contact_email="test@example.com",
                contact_phone="1234567890",
                amenities="WiFi, Parking",
                rules="No smoking",
                check_in="14:00:00",
                check_out="10:00:00",
                total_beds=100,
                current_occupancy=50,
                monthly_revenue=10000,
                visibility="public",
                is_featured=False,
                location_id=1
            )
            db.add(hostel)
            db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_sample_data()
    seed_hostel()
