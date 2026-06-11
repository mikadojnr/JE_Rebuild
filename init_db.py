#!/usr/bin/env python
"""
Initialize Database and Create Admin User
Run this script once to set up the database
"""

import os
import sys
from app import create_app, db
from models import User, SiteSettings, Service
from dotenv import load_dotenv

load_dotenv()


def init_database():
    """Create all database tables"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully")


def create_admin_user(username='admin', email='admin@johneniola.com', password='admin123'):
    """Create an admin user"""
    app = create_app()
    
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"✗ User '{username}' already exists")
            return False
        
        # Create new admin user
        user = User(
            username=username,
            email=email,
            is_admin=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        print(f"✓ Admin user created successfully")
        print(f"  Username: {username}")
        print(f"  Email: {email}")
        print(f"  Password: {password}")
        print("\n⚠️  IMPORTANT: Change this password immediately after first login!")
        
        return True


def create_sample_data():
    """Create sample services for demonstration"""
    app = create_app()
    
    with app.app_context():
        # Check if services already exist
        if Service.query.first():
            print("Services already exist in database")
            return
        
        services = [
            Service(
                title="Fiscal Incentive Management",
                slug="fiscal-incentive-management",
                description="Maximize government incentives and tax benefits available in Nigeria and across West Africa. We help businesses navigate the complex landscape of government incentives, tax credits, and financial benefits available in Nigeria and across West Africa. We conduct eligibility assessments, identify applicable benefits, and manage the application process to ensure compliance with all requirements.",
                excerpt="Maximize government incentives and tax benefits",
                icon="📊",
                key_features=[
                    "Incentive identification & eligibility assessment",
                    "Application preparation & submission",
                    "Compliance monitoring & reporting",
                    "ROI analysis & benefit optimization"
                ],
                order=1,
                is_active=True
            ),
            Service(
                title="Tax Planning",
                slug="tax-planning",
                description="Strategic tax optimization and compliance management",
                excerpt="Strategic tax optimization and compliance management",
                icon="💰",
                key_features=[
                    "Tax strategy development",
                    "Year-round tax planning",
                    "Deduction optimization",
                    "Structure planning"
                ],
                order=2,
                is_active=True
            ),
            Service(
                title="Assurance Services",
                slug="assurance-services",
                description="Independent verification and stakeholder confidence",
                excerpt="Independent verification and stakeholder confidence",
                icon="✓",
                key_features=[
                    "Financial statement audits",
                    "Internal audits",
                    "Compliance audits",
                    "Fraud investigations"
                ],
                order=3,
                is_active=True
            ),
            Service(
                title="Advisory Services",
                slug="advisory-services",
                description="Strategic business guidance and financial consulting",
                excerpt="Strategic business guidance and financial consulting",
                icon="🎯",
                key_features=[
                    "Business advisory",
                    "Financial consulting",
                    "Risk management",
                    "Process improvement"
                ],
                order=4,
                is_active=True
            ),
            Service(
                title="Risk Management",
                slug="risk-management",
                description="Comprehensive risk assessment and mitigation",
                excerpt="Comprehensive risk assessment and mitigation",
                icon="🛡️",
                key_features=[
                    "Risk assessment",
                    "Risk mitigation",
                    "Insurance advisory",
                    "Business continuity planning"
                ],
                order=5,
                is_active=True
            ),
            Service(
                title="Strategic Planning",
                slug="strategic-planning",
                description="Long-term financial strategy and growth planning",
                excerpt="Long-term financial strategy and growth planning",
                icon="📈",
                key_features=[
                    "5-year planning",
                    "Growth strategy",
                    "Expansion planning",
                    "Market analysis"
                ],
                order=6,
                is_active=True
            )
        ]
        
        for service in services:
            db.session.add(service)
        
        db.session.commit()
        print(f"✓ Created {len(services)} sample services")


if __name__ == '__main__':
    print("=" * 50)
    print("John & Eniola Consultancy - Database Initialization")
    print("=" * 50)
    print()
    
    try:
        # Create database tables
        init_database()
        print()
        
        # Create admin user
        create_admin_user()
        print()
        
        # Create sample data
        create_sample_data()
        print()
        
        print("=" * 50)
        print("✓ Database initialization complete!")
        print("=" * 50)
        print()
        print("Next steps:")
        print("1. Update .env file with your email settings")
        print("2. Run: python app.py")
        print("3. Navigate to http://localhost:5000/admin")
        print()
        
    except Exception as e:
        print(f"✗ Error during initialization: {str(e)}")
        sys.exit(1)
