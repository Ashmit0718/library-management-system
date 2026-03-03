"""
seed.py — Populate library_db with realistic sample data.

Usage:
    python seed.py                    # uses .env DB credentials
    python seed.py --password secret  # override MySQL root password

What it creates:
  • 1 admin account
  • 2 librarian accounts
  • 9 member accounts
  • 40 real books across 8 genres
  • ~70 borrow records (mix of returned, active, overdue)
"""

import argparse
import os
import sys
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# ── Parse optional password override ─────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("--password", default=None, help="MySQL root password (overrides .env)")
args = parser.parse_args()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1").strip()
DB_PORT = int(os.getenv("DB_PORT", "3306").strip())
DB_USER = os.getenv("DB_USER", "root").strip()
DB_PASS = args.password if args.password is not None else os.getenv("DB_PASSWORD", "").strip()
DB_NAME = os.getenv("DB_NAME", "library_db").strip()

# ── Bootstrap — ensure DB exists, then set up Flask app ──────────────────────
import pymysql
try:
    bootstrap = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS)
    bootstrap.cursor().execute(
        f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    bootstrap.commit()
    bootstrap.close()
    print(f"✓ Database `{DB_NAME}` ready")
except pymysql.err.OperationalError as e:
    print(f"\n✗ Cannot connect to MySQL: {e}")
    print("  → Pass your password with:  python seed.py --password YOUR_PASSWORD")
    sys.exit(1)

# Update env so Flask picks up the right password
os.environ["DB_PASSWORD"] = DB_PASS
os.environ["DB_HOST"]     = DB_HOST

from app import create_app
from app.extensions import db, bcrypt
from app.models.user    import User
from app.models.book    import Book
from app.models.borrow  import BorrowRecord
from app.models.activity import ActivityLog

app = create_app()

# ── Data ─────────────────────────────────────────────────────────────────────

USERS = [
    # (name, email, password, role)
    ("Ashmit Desai",     "24104139@apsit.edu.in",  "Admin@123",   "admin"),
    ("Priya Sharma",    "priya@library.com",       "Priya123",   "librarian"),
    ("Ravi Kumar",      "ravi@library.com",        "Ravi123",    "librarian"),
    ("Ananya Iyer",     "ananya@library.com",      "Ananya123",  "member"),
    ("Rohan Mehta",     "rohan@library.com",       "Rohan123",   "member"),
    ("Sneha Patil",     "sneha@library.com",       "Sneha123",   "member"),
    ("Vikram Singh",    "vikram@library.com",      "Vikram123",  "member"),
    ("Kavya Nair",      "kavya@library.com",       "Kavya123",   "member"),
    ("Aditya Rao",      "aditya@library.com",      "Aditya123",  "member"),
    ("Meera Joshi",     "meera@library.com",       "Meera123",   "member"),
    ("Kiran Bhat",      "kiran@library.com",       "Kiran123",   "member"),
    ("Pooja Vishwakarma", "pooja@library.com",     "Pooja123",   "member"),
]

BOOKS = [
    # Fiction
    ("The Great Gatsby",            "F. Scott Fitzgerald",  "9780743273565", "Fiction",     "A story of the mysteriously wealthy Jay Gatsby and his love for Daisy Buchanan.", 4),
    ("To Kill a Mockingbird",       "Harper Lee",           "9780061935466", "Fiction",     "A gripping tale of racial injustice and moral growth in the American South.", 3),
    ("1984",                        "George Orwell",        "9780451524935", "Fiction",     "A dystopian novel about totalitarianism and surveillance society.", 5),
    ("The Catcher in the Rye",      "J.D. Salinger",        "9780316769174", "Fiction",     "A story of teenage angst and alienation through Holden Caulfield's eyes.", 2),
    ("Pride and Prejudice",         "Jane Austen",          "9780141439518", "Fiction",     "A romantic novel about the Bennet sisters navigating love and society.", 3),
    ("The Alchemist",               "Paulo Coelho",         "9780062315007", "Fiction",     "An inspiring fable about following one's dreams and the soul of the world.", 5),
    ("One Hundred Years of Solitude","Gabriel García Márquez","9780060883287","Fiction",   "A multi-generational saga of the Buendía family in the fictional town of Macondo.", 2),
    ("Brave New World",             "Aldous Huxley",        "9780060850524", "Fiction",     "A futuristic society where happiness is manufactured and freedom is extinct.", 3),

    # Non-fiction
    ("Sapiens",                     "Yuval Noah Harari",    "9780062316097", "Non-fiction", "A brief history of humankind from ancient times to the present.", 5),
    ("Educated",                    "Tara Westover",        "9780399590504", "Non-fiction", "A memoir of a woman who grew up in a survivalist family and educated herself.", 4),
    ("Becoming",                    "Michelle Obama",       "9781524763138", "Non-fiction", "An intimate and inspiring memoir by the former First Lady of the United States.", 3),
    ("The Power of Habit",          "Charles Duhigg",       "9780812981605", "Non-fiction", "A fascinating exploration of the science behind habit formation.", 4),
    ("Atomic Habits",               "James Clear",          "9780735211292", "Non-fiction", "Practical strategies for building good habits and breaking bad ones.", 6),
    ("Thinking, Fast and Slow",     "Daniel Kahneman",      "9780374533557", "Non-fiction", "A groundbreaking tour of the mind and how we make decisions.", 3),

    # Science
    ("A Brief History of Time",     "Stephen Hawking",      "9780553380163", "Science",     "From the big bang to black holes, a landmark guide to the cosmos.", 4),
    ("The Selfish Gene",            "Richard Dawkins",      "9780198788607", "Science",     "A revolutionary view of evolution through the lens of the gene.", 3),
    ("Cosmos",                      "Carl Sagan",           "9780345539434", "Science",     "A journey through the universe and humanity's place in it.", 3),
    ("The Origin of Species",       "Charles Darwin",       "9780140432053", "Science",     "Darwin's groundbreaking work on the theory of evolution by natural selection.", 2),
    ("Astrophysics for People in a Hurry","Neil deGrasse Tyson","9780393609394","Science", "Essential knowledge about the universe, from the big bang to dark matter.", 5),

    # Technology
    ("Clean Code",                  "Robert C. Martin",     "9780132350884", "Technology",  "A handbook of agile software craftsmanship and best practices.", 4),
    ("The Pragmatic Programmer",    "Andrew Hunt",          "9780135957059", "Technology",  "Your journey to mastery as a software developer.", 3),
    ("You Don't Know JS",           "Kyle Simpson",         "9781491924464", "Technology",  "A deep dive into the JavaScript language mechanisms.", 4),
    ("Design Patterns",             "Gang of Four",         "9780201633610", "Technology",  "Classic patterns for object-oriented software design.", 2),
    ("Deep Learning",               "Ian Goodfellow",       "9780262035613", "Technology",  "The definitive textbook on deep learning and neural networks.", 3),
    ("The Lean Startup",            "Eric Ries",            "9780307887894", "Technology",  "How today's entrepreneurs use continuous innovation to create successful businesses.", 4),

    # History
    ("Guns, Germs, and Steel",      "Jared Diamond",        "9780393354323", "History",     "Why some civilizations came to dominate others.", 3),
    ("A People's History of the US","Howard Zinn",          "9780060838652", "History",     "History told from the perspective of ordinary Americans.", 3),
    ("The Silk Roads",              "Peter Frankopan",      "9781101912379", "History",     "A new history of the world through the ancient trade routes.", 2),
    ("Genghis Khan",                "Jack Weatherford",     "9780609809648", "History",     "The story of the man who conquered more land than any other in history.", 2),

    # Philosophy
    ("Meditations",                 "Marcus Aurelius",      "9780140449334", "Philosophy",  "Personal writings of the Roman Emperor — a stoic guide to life.", 3),
    ("Thus Spoke Zarathustra",      "Friedrich Nietzsche",  "9780140441185", "Philosophy",  "Nietzsche's magnum opus presenting his philosophical vision.", 2),
    ("The Republic",                "Plato",                "9780872201361", "Philosophy",  "Plato's dialogues on justice, beauty, equality, politics, and the soul.", 3),
    ("Man's Search for Meaning",    "Viktor E. Frankl",     "9780807014271", "Philosophy",  "A psychiatrist's memoir of surviving the Holocaust and finding purpose.", 5),

    # Biography
    ("Steve Jobs",                  "Walter Isaacson",      "9781451648539", "Biography",   "The exclusive biography of Apple's visionary co-founder.", 4),
    ("Elon Musk",                   "Ashlee Vance",         "9780062301239", "Biography",   "The story of the entrepreneur reshaping multiple industries.", 5),
    ("Leonardo da Vinci",           "Walter Isaacson",      "9781501139154", "Biography",   "A fascinating portrait of the ultimate Renaissance man.", 3),
    ("Long Walk to Freedom",        "Nelson Mandela",       "9780316548182", "Biography",   "Nelson Mandela's autobiography and struggle against apartheid.", 3),

    # Other
    ("The Art of War",              "Sun Tzu",              "9781599869773", "Other",       "Ancient Chinese military treatise with timeless strategic wisdom.", 4),
    ("Rich Dad Poor Dad",           "Robert T. Kiyosaki",   "9781612680194", "Other",       "What the rich teach their kids about money that the poor and middle class do not.", 5),
]

# How many days ago borrow happened, and how many days the loan was
BORROW_SCENARIOS = [
    # (borrowed_days_ago, loan_duration_days, returned_after_days_or_None)
    # RETURNED borrows
    (60, 14, 12),   (55, 14, 10),  (50, 14, 14),  (45, 14, 7),
    (40, 14, 13),   (35, 14, 14),  (30, 14, 5),   (25, 14, 9),
    (20, 14, 12),   (18, 14, 14),  (15, 14, 6),   (12, 14, 11),
    (10, 14, 4),    (8,  14, 7),

    # ACTIVE (still borrowed, not overdue)
    (5,  14, None), (4,  14, None), (3,  14, None), (2,  14, None),
    (1,  14, None), (6,  14, None), (7,  14, None), (3,  14, None),

    # OVERDUE (borrowed long ago, never returned)
    (30, 14, None), (25, 14, None), (20, 14, None),
    (22, 14, None), (28, 14, None), (35, 14, None),
]


def run_seed():
    with app.app_context():
        # Drop & recreate all tables
        db.drop_all()
        db.create_all()
        print("✓ Tables created")

        # ── Users ────────────────────────────────────────────────────────────
        created_users = []
        for name, email, password, role in USERS:
            pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
            user = User(name=name, email=email, password_hash=pw_hash, role=role)
            db.session.add(user)
            created_users.append(user)
        db.session.commit()
        print(f"✓ {len(created_users)} users created")

        # ── Books ─────────────────────────────────────────────────────────────
        created_books = []
        for title, author, isbn, genre, desc, copies in BOOKS:
            book = Book(
                title=title, author=author, isbn=isbn, genre=genre,
                description=desc, total_copies=copies, available_copies=copies,
            )
            db.session.add(book)
            created_books.append(book)
        db.session.commit()
        print(f"✓ {len(created_books)} books created")

        # ── Borrow Records ────────────────────────────────────────────────────
        members = [u for u in created_users if u.role == "member"]
        now = datetime.utcnow()
        borrow_count = 0

        for i, (days_ago, loan_days, returned_after) in enumerate(BORROW_SCENARIOS):
            member  = members[i % len(members)]
            book    = created_books[i % len(created_books)]

            borrowed_at = now - timedelta(days=days_ago)
            due_date    = borrowed_at + timedelta(days=loan_days)

            if returned_after is not None:
                returned_at = borrowed_at + timedelta(days=returned_after)
                status      = "returned"
            else:
                returned_at = None
                # Keep status as 'borrowed' — the analytics query detects overdue
                # by checking due_date < NOW() AND status = 'borrowed'
                status = "borrowed"
                if book.available_copies > 0:
                    book.available_copies -= 1

            record = BorrowRecord(
                user_id=member.id, book_id=book.id,
                borrowed_at=borrowed_at, due_date=due_date,
                returned_at=returned_at, status=status,
            )
            db.session.add(record)

            # Activity log
            log = ActivityLog(user_id=member.id, action="borrow", entity="book", entity_id=book.id, timestamp=borrowed_at)
            db.session.add(log)
            if returned_at:
                log2 = ActivityLog(user_id=member.id, action="return", entity="book", entity_id=book.id, timestamp=returned_at)
                db.session.add(log2)

            borrow_count += 1

        db.session.commit()
        print(f"✓ {borrow_count} borrow records created")

        # ── Summary ───────────────────────────────────────────────────────────
        returned = sum(1 for s in BORROW_SCENARIOS if s[2] is not None)
        overdue  = sum(1 for days_ago, loan_days, ret in BORROW_SCENARIOS
                       if ret is None and (now - timedelta(days=days_ago) + timedelta(days=loan_days)) < now)
        active   = borrow_count - returned - overdue

        print()
        print("=" * 52)
        print("  🎉  Seed complete!")
        print("=" * 52)
        print(f"  Users   : {len(created_users)}  (1 admin · 2 librarians · 9 members)")
        print(f"  Books   : {len(created_books)}  (Fiction · Sci · Tech · History · …)")
        print(f"  Borrows : {borrow_count}  ({returned} returned · {active} active · {overdue} overdue)")
        print()
        print("  Login credentials:")
        print("  ┌─────────────────────────────────────────────────┐")
        print("  │  admin@library.com     /  admin123   (admin)    │")
        print("  │  priya@library.com     /  priya123   (librarian)│")
        print("  │  ananya@library.com    /  ananya123  (member)   │")
        print("  └─────────────────────────────────────────────────┘")
        print()
        print("  Run the server:  python run.py")


if __name__ == "__main__":
    run_seed()
