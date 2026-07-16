#!/usr/bin/env python
"""
Initialize Database and Create Admin User
Run this script once to set up the database
"""

import os
import sys
from datetime import datetime, timedelta
import secrets
from app import create_app, db
from models import User, SiteSettings, Service, BlogPost, Comment, Newsletter, NewsletterCampaign, Subscriber
from dotenv import load_dotenv

load_dotenv()


def init_database():
    """Create all database tables"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully")


def create_admin_user(username='je_consultancy', email='admin@johneniolaltd.com', password='admin123'):
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
            is_admin=True,
            is_active=True
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


def create_sample_blog_posts():
    """Create sample blog posts / insights"""
    app = create_app()

    with app.app_context():
        if BlogPost.query.first():
            print("Blog posts already exist in database")
            return

        posts = [
            BlogPost(
                title="Understanding Nigeria's New Tax Reforms: What Businesses Need to Know",
                slug="nigerian-tax-reforms-2026",
                excerpt="A comprehensive breakdown of the latest tax policy changes in Nigeria and how they impact businesses of all sizes.",
                content="""
<h2>Overview of the 2026 Tax Reforms</h2>
<p>The Nigerian government has introduced sweeping tax reforms aimed at simplifying the tax landscape, broadening the tax base, and improving compliance across all sectors. These changes present both challenges and opportunities for businesses operating in Nigeria.</p>

<h3>Key Changes to Be Aware Of</h3>
<p>Among the most significant changes are the restructuring of Value Added Tax (VAT) rates, revised thresholds for small and medium enterprises (SMEs), and enhanced digital tax filing requirements. The reforms also introduce new incentives for companies investing in critical infrastructure and technology.</p>

<h3>Impact on SMEs</h3>
<p>Small and medium enterprises stand to benefit from reduced compliance burdens and new tax credits. The government has set a higher revenue threshold below which businesses are exempt from certain corporate income tax obligations. This is expected to ease the financial pressure on emerging businesses and encourage formalization.</p>

<h3>Compliance Tips</h3>
<ul>
    <li>Review your current tax structure with a qualified advisor to identify new opportunities for savings.</li>
    <li>Ensure your digital records are up to date, as the new e-filing system will be mandatory from Q3 2026.</li>
    <li>Take advantage of the transitional relief period, which allows businesses to adjust their processes before full enforcement begins.</li>
</ul>

<h3>How We Can Help</h3>
<p>At John & Eniola Consultancy, we guide businesses through every stage of tax compliance. From initial assessment to filing and dispute resolution, our team ensures you stay ahead of regulatory changes while optimizing your tax position.</p>
""",
                author_name="John Adebayo",
                category="Tax",
                tags=["tax", "nigeria", "reforms", "compliance", "SME"],
                meta_description="Learn about Nigeria's 2026 tax reforms and what they mean for your business.",
                is_featured=True,
                reading_time=6,
                is_published=True,
                view_count=245,
                created_at=datetime(2026, 6, 10, 9, 0),
                published_at=datetime(2026, 6, 12, 10, 0),
                updated_at=datetime(2026, 6, 12, 10, 0),
            ),
            BlogPost(
                title="5 Financial Strategies Every Startup in Lagos Should Adopt",
                slug="financial-strategies-lagos-startups",
                excerpt="Starting a business in Lagos? These five financial strategies will set you up for sustainable growth.",
                content="""
<h2>Why Financial Planning Matters for Startups</h2>
<p>Lagos is one of Africa's most dynamic business hubs, but the competition is fierce. Without a solid financial foundation, even the most promising startups can quickly run into trouble. Proper financial planning is not just about survival — it's about building a scalable, investable business.</p>

<h3>1. Separate Personal and Business Finances</h3>
<p>One of the most common mistakes founders make is mixing personal and business funds. Opening a dedicated business bank account and using proper accounting software from day one establishes credibility with investors and simplifies tax compliance.</p>

<h3>2. Build a Cash Reserve</h3>
<p>Cash flow challenges are the number one killer of startups. Aim to maintain at least three to six months of operating expenses in a reserve. This buffer gives you breathing room during slow periods and positions you to seize unexpected opportunities.</p>

<h3>3. Understand Your Unit Economics</h3>
<p>Know exactly how much it costs to acquire a customer and how much revenue each customer generates over their lifetime. This fundamental understanding guides pricing decisions, marketing spend, and growth strategy.</p>

<h3>4. Leverage Government Incentives</h3>
<p>Nigeria offers several incentive programs for startups, including pioneer status, investment tax credits, and export-oriented incentives. Many founders leave money on the table simply because they are unaware of these programs.</p>

<h3>5. Plan for Tax from Day One</h3>
<p>Tax planning should not be an afterthought. Structuring your business tax-efficiently from the start can save you significant amounts as you grow. This includes choosing the right entity structure, understanding withholding tax obligations, and planning for VAT.</p>

<h3>Partner With Experts</h3>
<p>At John & Eniola Consultancy, we specialize in helping startups navigate the financial landscape. From incorporation to fundraising and beyond, we provide the strategic guidance you need to build a resilient business.</p>
""",
                author_name="Eniola Okafor",
                category="Business",
                tags=["startups", "lagos", "financial planning", "entrepreneurship"],
                meta_description="Essential financial strategies for startups in Lagos, Nigeria.",
                is_featured=False,
                reading_time=5,
                is_published=True,
                view_count=189,
                created_at=datetime(2026, 6, 18, 14, 0),
                published_at=datetime(2026, 6, 20, 9, 0),
                updated_at=datetime(2026, 6, 20, 9, 0),
            ),
            BlogPost(
                title="The Role of Internal Audit in Preventing Corporate Fraud",
                slug="internal-audit-preventing-fraud",
                excerpt="How a robust internal audit function can protect your organization from financial misconduct and fraud.",
                content="""
<h2>Why Internal Audit Is Critical</h2>
<p>Corporate fraud costs organizations billions of naira every year. Beyond the direct financial losses, fraud erodes stakeholder trust, damages reputations, and can lead to severe regulatory penalties. A well-structured internal audit function is your first line of defense.</p>

<h3>Common Types of Corporate Fraud</h3>
<ul>
    <li><strong>Asset misappropriation:</strong> Theft or misuse of company resources, including cash, inventory, and intellectual property.</li>
    <li><strong>Financial statement fraud:</strong> Deliberate misstatement or misrepresentation of financial information to deceive stakeholders.</li>
    <li><strong>Corruption:</strong> Bribery, kickbacks, and conflicts of interest that compromise decision-making integrity.</li>
</ul>

<h3>Building an Effective Internal Audit Function</h3>
<p>An effective internal audit goes beyond checking boxes. It requires a risk-based approach that focuses on the areas of greatest vulnerability. This includes regular assessment of internal controls, surprise audits, and data analytics to detect anomalies.</p>

<h3>The Human Factor</h3>
<p>Technology is important, but the human element remains central to fraud prevention. A strong ethical culture, clear codes of conduct, whistleblower mechanisms, and regular training significantly reduce the risk of fraud.</p>

<h3>Regulatory Compliance</h3>
<p>Nigerian regulatory frameworks, including the Companies and Allied Matters Act (CAMA) and various CBN guidelines, require companies to maintain adequate internal controls. Non-compliance can result in fines, sanctions, and reputational damage.</p>

<h3>Our Approach</h3>
<p>John & Eniola Consultancy provides comprehensive internal audit services tailored to your organization's size, industry, and risk profile. We help you design, implement, and monitor audit programs that protect your assets and ensure regulatory compliance.</p>
""",
                author_name="John Adebayo",
                category="Assurance",
                tags=["internal audit", "fraud prevention", "compliance", "governance"],
                meta_description="Learn how internal audit prevents corporate fraud in Nigerian organizations.",
                is_featured=True,
                reading_time=7,
                is_published=True,
                view_count=312,
                created_at=datetime(2026, 6, 25, 11, 0),
                published_at=datetime(2026, 6, 27, 8, 0),
                updated_at=datetime(2026, 6, 27, 8, 0),
            ),
            BlogPost(
                title="Managing Financial Risk in Nigeria's Unpredictable Economy",
                slug="managing-financial-risk-nigeria",
                excerpt="Practical strategies for mitigating financial risk in a volatile economic environment.",
                content="""
<h2>The Reality of Economic Volatility</h2>
<p>Nigeria's economic landscape is shaped by fluctuating oil prices, currency instability, inflation, and evolving regulatory policies. For businesses, this uncertainty makes financial risk management not just important, but essential for survival.</p>

<h3>Key Financial Risks Facing Nigerian Businesses</h3>
<ul>
    <li><strong>Currency risk:</strong> The naira's volatility directly impacts import-dependent businesses and those with foreign currency obligations.</li>
    <li><strong>Inflation risk:</strong> Rising costs erode margins and purchasing power, requiring constant pricing adjustments.</li>
    <li><strong>Liquidity risk:</strong> Cash flow disruptions from delayed payments, seasonal fluctuations, or economic downturns.</li>
    <li><strong>Regulatory risk:</strong> Policy changes can suddenly alter the business environment, affecting everything from taxation to trade.</li>
</ul>

<h3>Practical Mitigation Strategies</h3>
<p>Effective risk management does not require eliminating all risk — it requires understanding, quantifying, and managing risk to acceptable levels. Key strategies include diversifying revenue streams, maintaining adequate reserves, using hedging instruments where appropriate, and building flexible cost structures.</p>

<h3>The Importance of Scenario Planning</h3>
<p>Businesses that thrive in volatile environments are those that plan for multiple scenarios. Stress-testing your financial model against various economic conditions helps you identify vulnerabilities and prepare contingency plans before crises hit.</p>

<h3>Professional Guidance</h3>
<p>Navigating financial risk requires expertise and experience. Our team at John & Eniola Consultancy helps businesses develop comprehensive risk management frameworks tailored to the Nigerian market.</p>
""",
                author_name="Eniola Okafor",
                category="Advisory",
                tags=["risk management", "financial planning", "nigeria economy", "currency risk"],
                meta_description="Strategies for managing financial risk in Nigeria's volatile economy.",
                is_featured=False,
                reading_time=6,
                is_published=True,
                view_count=156,
                created_at=datetime(2026, 7, 1, 10, 0),
                published_at=datetime(2026, 7, 3, 9, 0),
                updated_at=datetime(2026, 7, 3, 9, 0),
            ),
            BlogPost(
                title="Why Your Business Needs a Strategic Financial Plan in 2026",
                slug="strategic-financial-plan-2026",
                excerpt="A strategic financial plan is the backbone of sustainable growth. Here is why your business needs one now.",
                content="""
<h2>Beyond Budgeting: What Strategic Financial Planning Means</h2>
<p>A strategic financial plan goes far beyond annual budgeting. It is a living document that aligns your financial resources with your long-term business objectives. It provides a roadmap for growth, helps secure funding, and ensures you are prepared for both opportunities and challenges.</p>

<h3>Components of a Strong Financial Plan</h3>
<ul>
    <li><strong>Revenue projections:</strong> Data-driven forecasts based on market analysis, sales pipelines, and historical trends.</li>
    <li><strong>Cost structure analysis:</strong> A clear understanding of fixed and variable costs, and how they scale with growth.</li>
    <li><strong>Cash flow management:</strong> Detailed projections that account for seasonal variations and payment cycles.</li>
    <li><strong>Capital requirements:</strong> Identifying when and how much funding you will need, and the best sources for it.</li>
    <li><strong>Risk assessment:</strong> Identifying potential threats and building contingency plans.</li>
</ul>

<h3>The Cost of Not Planning</h3>
<p>Businesses without a strategic financial plan are reactive rather than proactive. They miss growth opportunities, struggle with cash flow crises, and often find themselves unable to respond effectively to market changes. The cost of poor planning far exceeds the investment required to do it properly.</p>

<h3>When to Engage a Financial Advisor</h3>
<p>The best time to develop a strategic financial plan is before you need it. Whether you are a startup seeking investment, an SME planning expansion, or an established company navigating change, professional financial advisory services provide the expertise and objectivity you need.</p>

<h3>Start Today</h3>
<p>John & Eniola Consultancy works with businesses across Nigeria to develop strategic financial plans that drive growth and create value. Contact us to schedule a consultation and take the first step toward a more secure financial future.</p>
""",
                author_name="John Adebayo",
                category="Advisory",
                tags=["strategic planning", "financial planning", "business growth", "2026"],
                meta_description="Why every business in Nigeria needs a strategic financial plan in 2026.",
                is_featured=False,
                reading_time=5,
                is_published=True,
                view_count=98,
                created_at=datetime(2026, 7, 8, 13, 0),
                published_at=datetime(2026, 7, 10, 10, 0),
                updated_at=datetime(2026, 7, 10, 10, 0),
            ),
        ]

        for post in posts:
            db.session.add(post)
        db.session.commit()
        print(f"Created {len(posts)} blog posts")

        # Add comments to the first blog post
        post1 = BlogPost.query.filter_by(slug="nigerian-tax-reforms-2026").first()
        post3 = BlogPost.query.filter_by(slug="internal-audit-preventing-fraud").first()

        if post1:
            comments = [
                Comment(
                    blog_post_id=post1.id,
                    author_name="Chukwuemeka D.",
                    author_email="chukwuemeka@example.com",
                    content="This is a very timely article. The new e-filing requirements will be a game changer for many SMEs. Would love to see a follow-up piece on the specific software platforms that will be supported.",
                    edit_token=secrets.token_urlsafe(32),
                    is_approved=True,
                    created_at=datetime(2026, 6, 14, 11, 30),
                ),
                Comment(
                    blog_post_id=post1.id,
                    author_name="Fatima Bello",
                    author_email="fatima.bello@example.com",
                    content="Very informative. We have been struggling to understand how the revised SME thresholds apply to our consulting firm. This article helped clarify things. Thank you!",
                    edit_token=secrets.token_urlsafe(32),
                    is_approved=True,
                    created_at=datetime(2026, 6, 15, 9, 15),
                ),
            ]

            # Add a reply to the first comment
            reply = Comment(
                blog_post_id=post1.id,
                parent_id=None,  # will set after first comment is added
                author_name="John Adebayo",
                author_email="admin@johneniolaltd.com",
                content="Thank you, Chukwuemeka! We are working on a detailed guide about the e-filing platforms. Stay tuned for that.",
                edit_token=secrets.token_urlsafe(32),
                is_approved=True,
                created_at=datetime(2026, 6, 14, 15, 0),
            )

            for c in comments:
                db.session.add(c)
            db.session.flush()
            reply.parent_id = comments[0].id
            db.session.add(reply)

        if post3:
            comments3 = [
                Comment(
                    blog_post_id=post3.id,
                    author_name="Amina Yusuf",
                    author_email="amina.yusuf@example.com",
                    content="The section on the human factor really resonates with our experience. We implemented a whistleblower policy last year and it has already helped us catch two issues early. Every company should have one.",
                    edit_token=secrets.token_urlsafe(32),
                    is_approved=True,
                    created_at=datetime(2026, 6, 29, 14, 20),
                ),
                Comment(
                    blog_post_id=post3.id,
                    author_name="Oluwaseun Adeyemi",
                    author_email="oluwaseun@example.com",
                    content="Great read. Do you offer training programs for internal audit teams? Our finance department could benefit from a refresher on fraud detection techniques.",
                    edit_token=secrets.token_urlsafe(32),
                    is_approved=True,
                    created_at=datetime(2026, 6, 30, 10, 45),
                ),
            ]
            for c in comments3:
                db.session.add(c)

        db.session.commit()
        total = Comment.query.count()
        print(f"Created {total} comments")


def create_sample_newsletters():
    """Create sample newsletters"""
    app = create_app()

    with app.app_context():
        if Newsletter.query.first():
            print("Newsletters already exist in database")
            return

        newsletters = [
            Newsletter(
                title="JE Tax Insight - June 2026",
                slug="je-tax-insight-june-2026",
                excerpt="Your monthly roundup of tax updates, compliance deadlines, and planning opportunities for Nigerian businesses.",
                google_drive_link="https://drive.google.com/example/june-2026",
                featured_image="/static/images/highlight.jpg",
                is_published=True,
                published_at=datetime(2026, 6, 28, 9, 0),
                created_at=datetime(2026, 6, 28, 9, 0),
                updated_at=datetime(2026, 6, 28, 9, 0),
            ),
            Newsletter(
                title="JE Tax Insight - May 2026",
                slug="je-tax-insight-may-2026",
                excerpt="In this edition: new FIRS guidelines on VAT, company income tax filing reminders, and tips for maximizing your tax credits.",
                google_drive_link="https://drive.google.com/example/may-2026",
                featured_image="/static/images/highlight.jpg",
                is_published=True,
                published_at=datetime(2026, 5, 30, 9, 0),
                created_at=datetime(2026, 5, 30, 9, 0),
                updated_at=datetime(2026, 5, 30, 9, 0),
            ),
            Newsletter(
                title="JE Tax Insight - April 2026",
                slug="je-tax-insight-april-2026",
                excerpt="Quarterly review of Nigeria's fiscal landscape, including updates on the Finance Act, investment incentives, and SME tax relief measures.",
                google_drive_link="https://drive.google.com/example/april-2026",
                featured_image="/static/images/highlight.jpg",
                is_published=True,
                published_at=datetime(2026, 4, 30, 9, 0),
                created_at=datetime(2026, 4, 30, 9, 0),
                updated_at=datetime(2026, 4, 30, 9, 0),
            ),
            Newsletter(
                title="JE Business Advisory Digest - Q1 2026",
                slug="je-advisory-digest-q1-2026",
                excerpt="Strategic insights for Q1: economic outlook, business growth strategies, and risk management considerations for the year ahead.",
                google_drive_link="https://drive.google.com/example/q1-2026",
                featured_image="/static/images/highlight.jpg",
                is_published=True,
                published_at=datetime(2026, 3, 31, 9, 0),
                created_at=datetime(2026, 3, 31, 9, 0),
                updated_at=datetime(2026, 3, 31, 9, 0),
            ),
        ]

        for nl in newsletters:
            db.session.add(nl)
        db.session.commit()
        print(f"Created {len(newsletters)} newsletters")


def create_sample_subscribers():
    """Create sample newsletter subscribers"""
    app = create_app()

    with app.app_context():
        if Subscriber.query.first():
            print("Subscribers already exist in database")
            return

        subscribers = [
            Subscriber(email="chukwuemeka@example.com", name="Chukwuemeka D.", is_active=True),
            Subscriber(email="fatima.bello@example.com", name="Fatima Bello", is_active=True),
            Subscriber(email="oluwaseun@example.com", name="Oluwaseun Adeyemi", is_active=True),
            Subscriber(email="amina.yusuf@example.com", name="Amina Yusuf", is_active=True),
            Subscriber(email="tunde.olawale@example.com", name="Tunde Olawale", is_active=True),
        ]

        for sub in subscribers:
            db.session.add(sub)
        db.session.commit()
        print(f"Created {len(subscribers)} subscribers")


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

        # Create blog posts, comments, newsletters, subscribers
        create_sample_blog_posts()
        print()

        create_sample_comments_reply_note = "(Replies created within comments above)"
        print(create_sample_comments_reply_note)
        print()

        create_sample_newsletters()
        print()

        create_sample_subscribers()
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
