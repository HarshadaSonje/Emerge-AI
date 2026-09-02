from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.utils.security import hash_password

db = SessionLocal()

try:
    # Check if admin already exists
    existing_admin = (
        db.query(User)
        .filter(User.email == "admin@emergeai.com")
        .first()
    )

    if existing_admin:
        print("✅ Admin user already exists.")
    else:
        admin = User(
            full_name="System Admin",
            email="admin@emergeai.com",
            phone="9999999999",
            password_hash=hash_password("Admin@123"),
            role=UserRole.ADMIN,
            is_active=True,
        )

        db.add(admin)
        db.commit()

        print("✅ Admin user created successfully!")

finally:
    db.close()