"""
books/management/commands/faker.py

Custom Django management command to seed CommunityBook data.

Usage:
    python manage.py faker            # seed (skips existing)
    python manage.py faker --clear    # wipe all CommunityBooks first, then seed
"""

import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from books.models import BorrowRequest, CommunityBook


BARANGAYS = [
    "Brgy. San Jose, Puerto Princesa City, Palawan",
    "Brgy. Bancao-Bancao, Puerto Princesa City, Palawan",
    "Brgy. Tiniguiban, Puerto Princesa City, Palawan",
    "Brgy. Mandaragat, Puerto Princesa City, Palawan",
    "Brgy. Sicsican, Puerto Princesa City, Palawan",
    "Brgy. Bagong Sikat, Puerto Princesa City, Palawan",
    "Brgy. Sta. Monica, Puerto Princesa City, Palawan",
    "Brgy. Masipag, Puerto Princesa City, Palawan",
    "Brgy. Irawan, Puerto Princesa City, Palawan",
    "Brgy. Tagburos, Puerto Princesa City, Palawan",
    "Brgy. Bacungan, Puerto Princesa City, Palawan",
    "Brgy. Mangingisda, Puerto Princesa City, Palawan",
    "Brgy. Mabuhay, Puerto Princesa City, Palawan",
    "Brgy. Kalipay, Puerto Princesa City, Palawan",
    "Brgy. Macarascas, Puerto Princesa City, Palawan",
    "Brgy. Sta. Lourdes, Puerto Princesa City, Palawan",
    "Brgy. Abo-Abo, Puerto Princesa City, Palawan",
    "Brgy. Binduyan, Puerto Princesa City, Palawan",
    "Brgy. Kamuning, Puerto Princesa City, Palawan",
    "Brgy. Princesa, Puerto Princesa City, Palawan",
]

OWNER_NAMES = [
    "Maria Santos", "Juan dela Cruz", "Ana Reyes", "Carlo Villanueva",
    "Liza Fernandez", "Ramon Aguilar", "Cristina Bautista", "Diego Ramos",
    "Jasmine Lim", "Eduardo Torres", "Patricia Cruz", "Miguel Hernandez",
    "Sofia Garcia", "Antonio Flores", "Marisol Aquino", "Benedict Tan",
    "Camille Navarro", "Jose Mercado", "Isabel Domingo", "Marco Soriano",
]

OWNER_CONTACTS = [
    "09171234567", "09281234568", "09391234569", "09501234570",
    "09171234571", "09281234572", "09391234573", "09501234574",
    "09171234575", "09281234576", "09391234577", "09501234578",
    "09171234579", "09281234580", "09391234581", "09501234582",
    "09171234583", "09281234584", "09391234585", "09501234586",
]

CONDITION_NOTES = [
    "Slight yellowing on pages, still very readable.",
    "Barely used, kept in protective cover.",
    "Good shape with minor wear on spine.",
    "Some pencil annotations inside, easily erasable.",
    "Cover has minor scratches but pages are intact.",
    "Read once, excellent condition.",
    "Has a small coffee ring on the back cover.",
    "Pristine condition, received as a gift.",
    "Well-loved copy with creased spine.",
    "Nearly new, purchased but never fully read.",
    "Former library copy, stamped but otherwise clean.",
    "Minor fading on cover, text pages perfect.",
    "Stored carefully, no damage.",
    "Light fold on one corner, rest is fine.",
    "Paperback edition, slight curling on edges.",
    "Hardcover, dust jacket has small tear.",
    "Pages slightly tanned from age, still sturdy.",
    "Came in a book set, individual copy in good shape.",
    "Read multiple times but well cared for.",
    "Brand new, never opened.",
]

BOOKS_DATA = [
    {
        "title": "Harry Potter and the Sorcerer's Stone",
        "authors": "J.K. Rowling",
        "description": (
            "Harry Potter has never even heard of Hogwarts when the letters start dropping on "
            "the doormat at number four, Privet Drive. On Harry's eleventh birthday, a great "
            "beetle-eyed giant called Rubeus Hagrid bursts in with astonishing news: Harry "
            "Potter is a wizard, and he has a place at Hogwarts School of Witchcraft and Wizardry."
        ),
        "published_date": "1997",
        "categories": "Fiction / Fantasy",
        "google_books_id": "wrOQLV6xB-wC",
        "thumbnail": "https://books.google.com/books/content?id=wrOQLV6xB-wC&printsec=frontcover&img=1&zoom=1&edge=curl",
        "condition": "good",
        "listing_type": "borrow",
    },
    {
        "title": "To Kill a Mockingbird",
        "authors": "Harper Lee",
        "description": (
            "The unforgettable novel of a childhood in a sleepy Southern town and the crisis of "
            "conscience that rocked it. Told through the eyes of Scout Finch, whose father, "
            "attorney Atticus Finch, defends a Black man unjustly accused of a terrible crime."
        ),
        "published_date": "1960",
        "categories": "Fiction / Classic Literature",
        "google_books_id": "PGR2AwAAQBAJ",
        "thumbnail": "https://books.google.com/books/content?id=PGR2AwAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl",
        "condition": "like_new",
        "listing_type": "both",
    },
    {
        "title": "The Alchemist",
        "authors": "Paulo Coelho",
        "description": (
            "Paulo Coelho's masterpiece tells the mystical story of Santiago, an Andalusian "
            "shepherd boy who yearns to travel in search of a worldly treasure. Along the way "
            "he learns about listening to his heart and following his dreams."
        ),
        "published_date": "1988",
        "categories": "Fiction / Inspirational",
        "google_books_id": "FzVjBgAAQBAJ",
        "thumbnail": "https://books.google.com/books/content?id=FzVjBgAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl",
        "condition": "good",
        "listing_type": "borrow",
    },
    {
        "title": "1984",
        "authors": "George Orwell",
        "description": (
            "George Orwell's nightmarish vision of a totalitarian, bureaucratic world and one "
            "man's attempt to find individuality in it. A seminal text of the 20th century that "
            "grows more haunting as its futuristic purgatory becomes more real."
        ),
        "published_date": "1949",
        "categories": "Fiction / Dystopian",
        "google_books_id": "kotPYEqx7kMC",
        "thumbnail": "https://books.google.com/books/content?id=kotPYEqx7kMC&printsec=frontcover&img=1&zoom=1&edge=curl",
        "condition": "fair",
        "listing_type": "swap",
    },
    {
        "title": "The Great Gatsby",
        "authors": "F. Scott Fitzgerald",
        "description": (
            "The story of the fabulously wealthy Jay Gatsby and his love for the beautiful Daisy "
            "Buchanan, set against lavish Long Island parties in the 1920s. An exquisitely crafted "
            "tale of the American Dream, love, and loss."
        ),
        "published_date": "1925",
        "categories": "Fiction / Classic Literature",
        "google_books_id": "iXn5U2IzoBkC",
        "thumbnail": "https://books.google.com/books/content?id=iXn5U2IzoBkC&printsec=frontcover&img=1&zoom=1&edge=curl",
        "condition": "good",
        "listing_type": "borrow",
    },
    {
        "title": "Atomic Habits",
        "authors": "James Clear",
        "description": (
            "James Clear reveals practical strategies for forming good habits, breaking bad ones, "
            "and mastering the tiny behaviors that lead to remarkable results. A proven framework "
            "for getting 1% better every day."
        ),
        "published_date": "2018",
        "categories": "Self-Help / Productivity",
        "google_books_id": "XfFvDwAAQBAJ",
        "thumbnail": "https://books.google.com/books/content?id=XfFvDwAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl",
        "condition": "like_new",
        "listing_type": "both",
    },
    {
        "title": "The Hunger Games",
        "authors": "Suzanne Collins",
        "description": (
            "In the ruins of North America lies Panem, where the Capitol forces each district to "
            "send one boy and one girl to participate in the annual Hunger Games — a fight to the "
            "death on live TV. Sixteen-year-old Katniss volunteers to save her sister."
        ),
        "published_date": "2008",
        "categories": "Fiction / Young Adult / Dystopian",
        "google_books_id": "sazytgAACAAJ",
        "thumbnail": "https://books.google.com/books/content?id=sazytgAACAAJ&printsec=frontcover&img=1&zoom=1&edge=curl",
        "condition": "good",
        "listing_type": "borrow",
    },
    {
        "title": "Rich Dad Poor Dad",
        "authors": "Robert T. Kiyosaki",
        "description": (
            "Robert Kiyosaki's story of growing up with two dads — his real father and the father "
            "of his best friend — and the ways both men shaped his thoughts about money. It "
            "explodes the myth that you need a high income to be rich."
        ),
        "published_date": "1997",
        "categories": "Non-Fiction / Personal Finance",
        "google_books_id": "MIjhAAAAMAAJ",
        "thumbnail": "https://books.google.com/books/content?id=MIjhAAAAMAAJ&printsec=frontcover&img=1&zoom=1&edge=curl",
        "condition": "good",
        "listing_type": "both",
    },
    {
        "title": "The Midnight Library",
        "authors": "Matt Haig",
        "description": (
            "Between life and death there is a library where every book provides a chance to try "
            "another life you could have lived. Nora Seed discovers this library and must decide "
            "what makes a life worth living."
        ),
        "published_date": "2020",
        "categories": "Fiction / Fantasy / Contemporary",
        "google_books_id": "dVDLDwAAQBAJ",
        "thumbnail": "https://books.google.com/books/content?id=dVDLDwAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl",
        "condition": "like_new",
        "listing_type": "borrow",
    },
    {
        "title": "Pride and Prejudice",
        "authors": "Jane Austen",
        "description": (
            "One of the most popular novels in the English language. Jane Austen's brilliant "
            "social comedy follows the Bennet family, particularly the witty and independent "
            "Elizabeth Bennet and the proud Mr. Darcy."
        ),
        "published_date": "1813",
        "categories": "Fiction / Classic / Romance",
        "google_books_id": "vnmWoAEACAAJ",
        "thumbnail": "https://books.google.com/books/content?id=vnmWoAEACAAJ&printsec=frontcover&img=1&zoom=1&edge=curl",
        "condition": "fair",
        "listing_type": "swap",
    },
    {
        "title": "The Da Vinci Code",
        "authors": "Dan Brown",
        "description": (
            "Harvard symbologist Robert Langdon is drawn into a breathless chase through Paris "
            "after a murder at the Louvre. He and a French cryptologist must crack a code that "
            "leads to a trail blazed by a mysterious ancient society."
        ),
        "published_date": "2003",
        "categories": "Fiction / Thriller / Mystery",
        "google_books_id": "jgzMDgAAQBAJ",
        "thumbnail": "https://books.google.com/books/content?id=jgzMDgAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl",
        "condition": "good",
        "listing_type": "borrow",
    },
    {
        "title": "Sapiens: A Brief History of Humankind",
        "authors": "Yuval Noah Harari",
        "description": (
            "Dr. Yuval Noah Harari spans the whole of human history, from the very first humans "
            "to the radical breakthroughs of the Cognitive, Agricultural, and Scientific "
            "Revolutions. A sweeping look at how history has shaped our societies and ourselves."
        ),
        "published_date": "2011",
        "categories": "Non-Fiction / History / Science",
        "google_books_id": "1EiJAwAAQBAJ",
        "thumbnail": "https://books.google.com/books/content?id=1EiJAwAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl",
        "condition": "like_new",
        "listing_type": "both",
    },
    {
        "title": "The Fault in Our Stars",
        "authors": "John Green",
        "description": (
            "Despite the tumor-shrinking miracle that has bought her a few years, Hazel has "
            "never been anything but terminal. But when a gorgeous twist named Augustus Waters "
            "appears at Cancer Kid Support Group, Hazel's story is completely rewritten."
        ),
        "published_date": "2012",
        "categories": "Fiction / Young Adult / Romance",
        "google_books_id": "tE0-AQAAQBAJ",
        "thumbnail": "https://books.google.com/books/content?id=tE0-AQAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl",
        "condition": "good",
        "listing_type": "borrow",
    },
    {
        "title": "Thinking, Fast and Slow",
        "authors": "Daniel Kahneman",
        "description": (
            "Nobel Prize winner Daniel Kahneman takes us on a groundbreaking tour of the mind, "
            "explaining the two systems that drive the way we think: System 1 (fast, intuitive, "
            "emotional) and System 2 (slow, deliberate, logical)."
        ),
        "published_date": "2011",
        "categories": "Non-Fiction / Psychology",
        "google_books_id": "ZuKTvERuPG8C",
        "thumbnail": "https://books.google.com/books/content?id=ZuKTvERuPG8C&printsec=frontcover&img=1&zoom=1&edge=curl",
        "condition": "good",
        "listing_type": "both",
    },
    {
        "title": "The Little Prince",
        "authors": "Antoine de Saint-Exupéry",
        "description": (
            "A pilot stranded in the desert meets a remarkable little fellow who teaches him "
            "life's most important lessons. One of the most translated and beloved books in "
            "history, cherished by children and adults alike."
        ),
        "published_date": "1943",
        "categories": "Fiction / Classic / Children's",
        "google_books_id": "y3vXCgAAQBAJ",
        "thumbnail": "https://books.google.com/books/content?id=y3vXCgAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl",
        "condition": "like_new",
        "listing_type": "borrow",
    },
    {
        "title": "Educated",
        "authors": "Tara Westover",
        "description": (
            "An unforgettable memoir about a young girl who, kept out of school, leaves her "
            "survivalist family and goes on to earn a PhD from Cambridge University. A story "
            "about the struggle for self-invention and the price of family loyalty."
        ),
        "published_date": "2018",
        "categories": "Non-Fiction / Memoir / Biography",
        "google_books_id": "2ObWDgAAQBAJ",
        "thumbnail": "https://books.google.com/books/content?id=2ObWDgAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl",
        "condition": "like_new",
        "listing_type": "both",
    },
    {
        "title": "The Hobbit",
        "authors": "J.R.R. Tolkien",
        "description": (
            "Bilbo Baggins, a hobbit who enjoys a comfortable life, is whisked away by the "
            "wizard Gandalf and a company of dwarves on an unexpected adventure to reclaim a "
            "mountain treasure guarded by the dragon Smaug."
        ),
        "published_date": "1937",
        "categories": "Fiction / Fantasy / Adventure",
        "google_books_id": "pD6arNyKyi8C",
        "thumbnail": "https://books.google.com/books/content?id=pD6arNyKyi8C&printsec=frontcover&img=1&zoom=1&edge=curl",
        "condition": "good",
        "listing_type": "borrow",
    },
    {
        "title": "Gone Girl",
        "authors": "Gillian Flynn",
        "description": (
            "On their fifth wedding anniversary, Nick Dunne's wife Amy disappears. Under mounting "
            "pressure from police and the public, Nick's secrets and lies begin to unravel in this "
            "masterfully plotted psychological thriller."
        ),
        "published_date": "2012",
        "categories": "Fiction / Thriller / Mystery",
        "google_books_id": "7SJcxgPKhhEC",
        "thumbnail": "https://books.google.com/books/content?id=7SJcxgPKhhEC&printsec=frontcover&img=1&zoom=1&edge=curl",
        "condition": "fair",
        "listing_type": "swap",
    },
    {
        "title": "The Power of Now",
        "authors": "Eckhart Tolle",
        "description": (
            "A guide to spiritual enlightenment, The Power of Now has transformed millions of "
            "lives. Eckhart Tolle shows readers how to free themselves from enslavement to the "
            "mind and how to find peace and happiness in the present moment."
        ),
        "published_date": "1997",
        "categories": "Non-Fiction / Self-Help / Spirituality",
        "google_books_id": "4EhpBgAAQBAJ",
        "thumbnail": "https://books.google.com/books/content?id=4EhpBgAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl",
        "condition": "good",
        "listing_type": "borrow",
    },
    {
        "title": "It Ends with Us",
        "authors": "Colleen Hoover",
        "description": (
            "Lily has come a long way from the small town in Maine where she grew up. When she "
            "feels a spark with a gorgeous neurosurgeon named Ryle Kincaid, everything seems too "
            "good to be true — and then her first love re-enters her life."
        ),
        "published_date": "2016",
        "categories": "Fiction / Romance / Contemporary",
        "google_books_id": "HVpZDwAAQBAJ",
        "thumbnail": "https://books.google.com/books/content?id=HVpZDwAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl",
        "condition": "like_new",
        "listing_type": "both",
    },
]


REQUESTER_NAMES = [
    "Alicia Mendoza", "Bryan Castillo", "Carla Delos Santos", "Dennis Macaraeg",
    "Elena Quirino", "Francis Galapon", "Grace Palacio", "Harold Sison",
    "Iris Tanedo", "Jason Abad", "Karen Morales", "Leo Briones",
    "Mila Custodio", "Noel Pineda", "Olivia Resurreccion", "Paolo Zulueta",
    "Queenie Macalinao", "Renz Buenaventura", "Sheila Corpuz", "Tomas Ilagan",
]

REQUESTER_CONTACTS = [
    "09171110001", "09282220002", "09393330003", "09504440004",
    "09175550005", "09286660006", "09397770007", "09508880008",
    "09179990009", "09281110010", "09392220011", "09503330012",
    "09174440013", "09285550014", "09396660015", "09507770016",
    "09178880017", "09289990018", "09391110019", "09502220020",
]

REQUEST_MESSAGES = [
    "Hi! I'd love to borrow this book. I'll take good care of it.",
    "I've been looking for this title for a while. Can we arrange a meetup?",
    "Interested to read this. Please let me know your available schedule.",
    "This is on my reading list! Hope we can arrange something soon.",
    "I'm a careful reader — I'll return it in the same condition.",
    "Would love to swap if that works for you. I have some good titles.",
    "Been wanting to read this. Available most weekends for pickup.",
    "Excited to get my hands on this one! Let me know when and where.",
    "I'm a fast reader so I'll return it quickly. Thanks in advance!",
    "I live nearby, happy to pick up at your convenience.",
]

MEETUP_LOCATIONS_NOTES = [
    "Robinsons Place Palawan",
    "Puerto Princesa City Hall",
    "SM City Puerto Princesa",
    "National Book Store, Puerto Princesa",
    "Barangay Hall, San Jose",
    "Rizal Avenue, Puerto Princesa",
]


class Command(BaseCommand):
    help = "Seed CommunityBook with 20 popular books in Puerto Princesa City barangays"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing CommunityBook records before seeding",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            count = CommunityBook.objects.count()
            CommunityBook.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Cleared {count} existing CommunityBook(s)."))

        self.stdout.write("Seeding CommunityBook data for Puerto Princesa City, Palawan...")
        self.stdout.write("-" * 65)

        created_count = 0
        skipped_count = 0

        for i, book in enumerate(BOOKS_DATA):
            exists = CommunityBook.objects.filter(
                title=book["title"],
                owner_name=OWNER_NAMES[i],
            ).exists()

            if exists:
                self.stdout.write(f"  ⚠  Skipping (already exists): {book['title']}")
                skipped_count += 1
                continue

            CommunityBook.objects.create(
                title=book["title"],
                authors=book["authors"],
                description=book["description"],
                thumbnail=book["thumbnail"],
                published_date=book["published_date"],
                categories=book["categories"],
                google_books_id=book["google_books_id"],
                owner_name=OWNER_NAMES[i],
                owner_contact=OWNER_CONTACTS[i],
                location=BARANGAYS[i],
                condition=book["condition"],
                listing_type=book["listing_type"],
                notes=CONDITION_NOTES[i],
                is_available=True,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✓  [{i+1:02d}] {book['title'][:45]:<45} "
                    f"— {OWNER_NAMES[i]} @ {BARANGAYS[i].split(',')[0]}"
                )
            )
            created_count += 1

        self.stdout.write("-" * 65)
        self.stdout.write(
            self.style.SUCCESS(
                f"Done!  Created: {created_count}  |  Skipped (duplicates): {skipped_count}"
            )
        )
        self.stdout.write(
            f"Total CommunityBooks in DB: {CommunityBook.objects.count()}"
        )

        # ── Seed BorrowRequests ──────────────────────────────────────────────
        self.stdout.write("")
        self.stdout.write("Seeding BorrowRequest data for Puerto Princesa City, Palawan...")
        self.stdout.write("-" * 65)

        if options["clear"]:
            req_count = BorrowRequest.objects.count()
            BorrowRequest.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Cleared {req_count} existing BorrowRequest(s)."))

        community_books = list(CommunityBook.objects.all())
        if not community_books:
            self.stdout.write(self.style.WARNING("No CommunityBooks found — skipping BorrowRequest seeding."))
            return

        req_created = 0
        req_skipped = 0

        for i, (name, contact) in enumerate(zip(REQUESTER_NAMES, REQUESTER_CONTACTS)):
            book = community_books[i % len(community_books)]

            exists = BorrowRequest.objects.filter(
                requester_name=name,
                book=book,
            ).exists()

            if exists:
                self.stdout.write(f"  ⚠  Skipping (already exists): {name} → {book.title}")
                req_skipped += 1
                continue

            # Spread meetup datetimes across the next 14 days
            days_ahead = (i % 14) + 1
            hour = 9 + (i % 8)  # 9 AM – 4 PM
            meetup_dt = timezone.now().replace(
                hour=hour, minute=0, second=0, microsecond=0
            ) + timedelta(days=days_ahead)

            request_type = "swap" if i % 5 == 0 else "borrow"
            status_choices = ["pending", "pending", "approved", "declined", "returned"]
            status = status_choices[i % len(status_choices)]

            BorrowRequest.objects.create(
                book=book,
                requester_name=name,
                requester_contact=contact,
                message=REQUEST_MESSAGES[i % len(REQUEST_MESSAGES)],
                meetup_datetime=meetup_dt,
                request_type=request_type,
                status=status,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✓  [{i+1:02d}] {name:<25} → {book.title[:35]:<35} [{request_type}/{status}]"
                )
            )
            req_created += 1

        self.stdout.write("-" * 65)
        self.stdout.write(
            self.style.SUCCESS(
                f"Done!  Created: {req_created}  |  Skipped (duplicates): {req_skipped}"
            )
        )
        self.stdout.write(
            f"Total BorrowRequests in DB: {BorrowRequest.objects.count()}"
        )
