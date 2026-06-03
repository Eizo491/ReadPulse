"""
Management command to seed the database with 20 community books.

Usage:
    python manage.py seed_community
    python manage.py seed_community --clear   # wipe existing community books first
    python manage.py seed_community --user admin  # assign all books to one user

Books are split across 3 dummy users (created if they don't exist).
Every book has a real Google Books cover thumbnail URL.
Listing types are spread: borrow / swap / both.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from books.models import CommunityBook


SEED_USERS = [
    {"username": "alice_reads",   "first_name": "Alice",   "last_name": "Reyes",    "email": "alice@example.com",   "password": "readpulse123"},
    {"username": "bookworm_ben",  "first_name": "Ben",     "last_name": "Santos",   "email": "ben@example.com",     "password": "readpulse123"},
    {"username": "mia_pages",     "first_name": "Mia",     "last_name": "Cruz",     "email": "mia@example.com",     "password": "readpulse123"},
]

# 20 popular books with working Google Books thumbnail URLs
SEED_BOOKS = [
    {
        "title": "Atomic Habits",
        "authors": "James Clear",
        "published_date": "2018",
        "isbn": "9780735211292",
        "publisher": "Avery",
        "language": "en",
        "page_count": 320,
        "categories": "Self-Help",
        "google_books_id": "XfFvDwAAQBAJ",
        "thumbnail": "https://books.google.com/books/content?id=XfFvDwAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
        "description": "Tiny changes, remarkable results. An easy and proven way to build good habits and break bad ones.",
        "listing_type": "borrow",
        "condition": "Like New",
        "notes": "Barely read, great condition!",
        "user_index": 0,
    },
    {
        "title": "The Alchemist",
        "authors": "Paulo Coelho",
        "published_date": "1988",
        "isbn": "9780062315007",
        "publisher": "HarperOne",
        "language": "en",
        "page_count": 208,
        "categories": "Fiction",
        "google_books_id": "FzVjBgAAQBAJ",
        "thumbnail": "https://books.google.com/books/content?id=FzVjBgAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
        "description": "A magical story about following your dreams and listening to your heart.",
        "listing_type": "swap",
        "condition": "Good",
        "notes": "Looking to swap for another fiction novel.",
        "user_index": 0,
    },
    {
        "title": "Sapiens: A Brief History of Humankind",
        "authors": "Yuval Noah Harari",
        "published_date": "2011",
        "isbn": "9780062316097",
        "publisher": "Harper",
        "language": "en",
        "page_count": 443,
        "categories": "History",
        "google_books_id": "1EiJAwAAQBAJ",
        "thumbnail": "https://books.google.com/books/content?id=1EiJAwAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
        "description": "A groundbreaking narrative of humanity's creation and evolution.",
        "listing_type": "both",
        "condition": "Good",
        "notes": "A must-read. Happy to lend or swap.",
        "user_index": 0,
    },
    {
        "title": "The Great Gatsby",
        "authors": "F. Scott Fitzgerald",
        "published_date": "1925",
        "isbn": "9780743273565",
        "publisher": "Scribner",
        "language": "en",
        "page_count": 180,
        "categories": "Classic Fiction",
        "google_books_id": "iXn5U2IzVH0C",
        "thumbnail": "https://books.google.com/books/content?id=iXn5U2IzVH0C&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
        "description": "A story of wealth, obsession, and the American Dream set in the Roaring Twenties.",
        "listing_type": "borrow",
        "condition": "Fair",
        "notes": "Classic copy, some wear on the spine.",
        "user_index": 0,
    },
    {
        "title": "Thinking, Fast and Slow",
        "authors": "Daniel Kahneman",
        "published_date": "2011",
        "isbn": "9780374533557",
        "publisher": "Farrar, Straus and Giroux",
        "language": "en",
        "page_count": 499,
        "categories": "Psychology",
        "google_books_id": "ZuKTvERuPG8C",
        "thumbnail": "https://books.google.com/books/content?id=ZuKTvERuPG8C&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
        "description": "Nobel laureate Kahneman reveals the two systems that drive the way we think.",
        "listing_type": "borrow",
        "condition": "Good",
        "notes": "Lots of highlights — hope that's okay!",
        "user_index": 0,
    },
    {
        "title": "To Kill a Mockingbird",
        "authors": "Harper Lee",
        "published_date": "1960",
        "isbn": "9780061935466",
        "publisher": "HarperCollins",
        "language": "en",
        "page_count": 336,
        "categories": "Classic Fiction",
        "google_books_id": "PGR2AwAAQBAJ",
        "thumbnail": "https://books.google.com/books/content?id=PGR2AwAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
        "description": "A timeless story of racial injustice and childhood innocence in the American South.",
        "listing_type": "swap",
        "condition": "Good",
        "notes": "Willing to swap for any classic.",
        "user_index": 1,
    },
    {
        "title": "Deep Work",
        "authors": "Cal Newport",
        "published_date": "2016",
        "isbn": "9781455586691",
        "publisher": "Grand Central Publishing",
        "language": "en",
        "page_count": 304,
        "categories": "Self-Help",
        "google_books_id": "lZpFCgAAQBAJ",
        "thumbnail": "https://books.google.com/books/content?id=lZpFCgAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
        "description": "Rules for focused success in a distracted world.",
        "listing_type": "both",
        "condition": "Like New",
        "notes": "Read once. Perfect condition.",
        "user_index": 1,
    },
    {
        "title": "1984",
        "authors": "George Orwell",
        "published_date": "1949",
        "isbn": "9780451524935",
        "publisher": "Signet Classic",
        "language": "en",
        "page_count": 328,
        "categories": "Dystopian Fiction",
        "google_books_id": "kotPYEqx7kMC",
        "thumbnail": "https://books.google.com/books/content?id=kotPYEqx7kMC&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
        "description": "Orwell's chilling dystopia about totalitarianism and surveillance.",
        "listing_type": "borrow",
        "condition": "Acceptable",
        "notes": "Old paperback but fully readable.",
        "user_index": 1,
    },
    {
        "title": "The Power of Now",
        "authors": "Eckhart Tolle",
        "published_date": "1997",
        "isbn": "9781577314806",
        "publisher": "New World Library",
        "language": "en",
        "page_count": 236,
        "categories": "Spirituality",
        "google_books_id": "4lZeT2ZFgPYC",
        "thumbnail": "https://books.google.com/books/content?id=4lZeT2ZFgPYC&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
        "description": "A guide to spiritual enlightenment through living in the present moment.",
        "listing_type": "swap",
        "condition": "Good",
        "notes": "Would love to swap for another mindfulness book.",
        "user_index": 1,
    },
    {
        "title": "Harry Potter and the Sorcerer's Stone",
        "authors": "J.K. Rowling",
        "published_date": "1997",
        "isbn": "9780439708180",
        "publisher": "Scholastic",
        "language": "en",
        "page_count": 309,
        "categories": "Fantasy",
        "google_books_id": "wrOQLV6xB-wC",
        "thumbnail": "https://books.google.com/books/content?id=wrOQLV6xB-wC&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
        "description": "The beloved story of a young wizard discovering his destiny at Hogwarts.",
        "listing_type": "both",
        "condition": "Good",
        "notes": "Great for kids or first-time readers!",
        "user_index": 1,
    },
    {
        "title": "Educated",
        "authors": "Tara Westover",
        "published_date": "2018",
        "isbn": "9780399590504",
        "publisher": "Random House",
        "language": "en",
        "page_count": 352,
        "categories": "Memoir",
        "google_books_id": "2ObWDgAAQBAJ",
        "thumbnail": "https://books.google.com/books/content?id=2ObWDgAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
        "description": "A memoir about a woman who leaves her survivalist family and pursues education.",
        "listing_type": "borrow",
        "condition": "Like New",
        "notes": "Amazing read. Please take care of it!",
        "user_index": 1,
    },
    {
        "title": "The Subtle Art of Not Giving a F*ck",
        "authors": "Mark Manson",
        "published_date": "2016",
        "isbn": "9780062457714",
        "publisher": "HarperOne",
        "language": "en",
        "page_count": 224,
        "categories": "Self-Help",
        "google_books_id": "yng_CwAAQBAJ",
        "thumbnail": "https://books.google.com/books/content?id=yng_CwAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
        "description": "A counterintuitive approach to living a good life.",
        "listing_type": "swap",
        "condition": "Good",
        "notes": "Swap for any self-help or psychology book.",
        "user_index": 2,
    },
    {
        "title": "Dune",
        "authors": "Frank Herbert",
        "published_date": "1965",
        "isbn": "9780441013593",
        "publisher": "Ace Books",
        "language": "en",
        "page_count": 688,
        "categories": "Science Fiction",
        "google_books_id": "B1hSG45JCX4C",
        "thumbnail": "https://books.google.com/books/content?id=B1hSG45JCX4C&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
        "description": "An epic science-fiction saga set on the desert planet Arrakis.",
        "listing_type": "both",
        "condition": "Good",
        "notes": "Epic book. A bit thick but worth every page.",
        "user_index": 2,
    },
    {
        "title": "The 7 Habits of Highly Effective People",
        "authors": "Stephen R. Covey",
        "published_date": "1989",
        "isbn": "9781982137274",
        "publisher": "Simon & Schuster",
        "language": "en",
        "page_count": 381,
        "categories": "Self-Help",
        "google_books_id": "upUxaNWSaREC",
        "thumbnail": "https://books.google.com/books/content?id=upUxaNWSaREC&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
        "description": "Powerful lessons in personal change and leadership.",
        "listing_type": "borrow",
        "condition": "Fair",
        "notes": "Some notes in margins but great content.",
        "user_index": 2,
    },
    {
        "title": "Rich Dad Poor Dad",
        "authors": "Robert T. Kiyosaki",
        "published_date": "1997",
        "isbn": "9781612680194",
        "publisher": "Plata Publishing",
        "language": "en",
        "page_count": 336,
        "categories": "Finance",
        "google_books_id": "5bFZDwAAQBAJ",
        "thumbnail": "https://books.google.com/books/content?id=5bFZDwAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
        "description": "What the rich teach their kids about money that the poor and middle class do not.",
        "listing_type": "swap",
        "condition": "Good",
        "notes": "Swap for another finance or investment book.",
        "user_index": 2,
    },
    {
        "title": "The Hunger Games",
        "authors": "Suzanne Collins",
        "published_date": "2008",
        "isbn": "9780439023481",
        "publisher": "Scholastic Press",
        "language": "en",
        "page_count": 374,
        "categories": "Young Adult Fiction",
        "google_books_id": "sazytgAACAAJ",
        "thumbnail": "https://books.google.com/books/content?id=sazytgAACAAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
        "description": "In a dystopian future, Katniss Everdeen volunteers to take her sister's place in a deadly televised competition.",
        "listing_type": "both",
        "condition": "Good",
        "notes": "Great page-turner! Return in same condition please.",
        "user_index": 2,
    },
    {
        "title": "Becoming",
        "authors": "Michelle Obama",
        "published_date": "2018",
        "isbn": "9781524763138",
        "publisher": "Crown",
        "language": "en",
        "page_count": 448,
        "categories": "Biography",
        "google_books_id": "G4x7DwAAQBAJ",
        "thumbnail": "https://books.google.com/books/content?id=G4x7DwAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
        "description": "An intimate memoir by the former First Lady of the United States.",
        "listing_type": "borrow",
        "condition": "Like New",
        "notes": "Inspirational read. Handle with care.",
        "user_index": 0,
    },
    {
        "title": "Zero to One",
        "authors": "Peter Thiel, Blake Masters",
        "published_date": "2014",
        "isbn": "9780804139021",
        "publisher": "Crown Business",
        "language": "en",
        "page_count": 224,
        "categories": "Business",
        "google_books_id": "xnMKBgAAQBAJ",
        "thumbnail": "https://books.google.com/books/content?id=xnMKBgAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
        "description": "Notes on startups, or how to build the future.",
        "listing_type": "swap",
        "condition": "Like New",
        "notes": "Swap for another startup or tech book.",
        "user_index": 1,
    },
    {
        "title": "The Midnight Library",
        "authors": "Matt Haig",
        "published_date": "2020",
        "isbn": "9780525559474",
        "publisher": "Viking",
        "language": "en",
        "page_count": 304,
        "categories": "Fiction",
        "google_books_id": "ByTODwAAQBAJ",
        "thumbnail": "https://books.google.com/books/content?id=ByTODwAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
        "description": "Between life and death there is a library with books of every life you could have lived.",
        "listing_type": "both",
        "condition": "Good",
        "notes": "Beautiful story. You'll love it.",
        "user_index": 2,
    },
    {
        "title": "The Four Agreements",
        "authors": "Don Miguel Ruiz",
        "published_date": "1997",
        "isbn": "9781878424310",
        "publisher": "Amber-Allen Publishing",
        "language": "en",
        "page_count": 160,
        "categories": "Spirituality",
        "google_books_id": "zGFJBAAAQBAJ",
        "thumbnail": "https://books.google.com/books/content?id=zGFJBAAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
        "description": "A practical guide to personal freedom based on ancient Toltec wisdom.",
        "listing_type": "borrow",
        "condition": "Good",
        "notes": "Quick read, very impactful.",
        "user_index": 0,
    },
]


class Command(BaseCommand):
    help = "Seed the database with 20 community books across 3 dummy users."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing CommunityBook records before seeding.",
        )
        parser.add_argument(
            "--user",
            type=str,
            default=None,
            help="Assign all seeded books to this username instead of dummy users.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            deleted, _ = CommunityBook.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Cleared {deleted} existing community book(s)."))

        # Resolve owners
        if options["user"]:
            try:
                owner = User.objects.get(username=options["user"])
                owners = [owner, owner, owner]
                self.stdout.write(f"Using existing user '{owner.username}' for all books.")
            except User.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"User '{options['user']}' not found."))
                return
        else:
            owners = []
            for u in SEED_USERS:
                user, created = User.objects.get_or_create(
                    username=u["username"],
                    defaults={
                        "first_name": u["first_name"],
                        "last_name":  u["last_name"],
                        "email":      u["email"],
                    },
                )
                if created:
                    user.set_password(u["password"])
                    user.save()
                    self.stdout.write(f"  Created user: {user.username} (password: {u['password']})")
                else:
                    self.stdout.write(f"  Using existing user: {user.username}")
                owners.append(user)

        # Create books
        created_count = 0
        skipped_count = 0
        for book_data in SEED_BOOKS:
            user_index = book_data.pop("user_index")
            owner = owners[user_index]

            # Skip if this exact book already exists for this owner
            if CommunityBook.objects.filter(
                owner=owner,
                google_books_id=book_data.get("google_books_id", ""),
            ).exists():
                skipped_count += 1
                book_data["user_index"] = user_index  # restore for safety
                continue

            CommunityBook.objects.create(owner=owner, **book_data)
            created_count += 1
            book_data["user_index"] = user_index  # restore

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅  Done! Created {created_count} book(s), skipped {skipped_count} duplicate(s)."
            )
        )
        if not options["user"]:
            self.stdout.write(
                "\nDummy user credentials (all use password: readpulse123):\n"
                "  alice_reads / bookworm_ben / mia_pages"
            )
