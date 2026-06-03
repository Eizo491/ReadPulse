# ReadPulse

**ReadPulse** is a web-based reading companion built with Django. It lets users search for books and audiobooks, read previews inline, save favorites, and connect with a community to borrow or swap physical books.

---

## Features

- **Book Search** — Search millions of books via the Google Books API with cover images, ratings, and metadata.
- **Inline Book Reader** — Preview books directly inside the app using the Google Books Embedded Viewer — no new tab needed.
- **Audiobook Search & Player** — Search free public domain audiobooks from LibriVox and listen to them inline with a chapter-by-chapter audio player.
- **Favorites** — Save books to your personal favorites list for quick access later.
- **Community Board** — List your physical books as available to borrow or swap. Other users can browse and send requests.
- **Book Requests** — Send borrow or swap requests to other users, propose meetup times and locations, and track request status (pending, accepted, declined, completed, cancelled).
- **My Listings** — Manage your own community listings and respond to incoming requests.
- **Authentication** — Sign up and log in with username/email, or via Google and GitHub (OAuth) using django-allauth.
- **PWA Support** — Installable as a Progressive Web App on mobile and desktop.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 6.0.5 |
| Auth | django-allauth 65.x (local + Google + GitHub OAuth) |
| Database | SQLite (development) |
| Frontend | Vanilla JS, CSS custom properties |
| Book Data | Google Books API |
| Audiobook Data | LibriVox API |
| PWA | django-pwa |
| Hosting | PythonAnywhere |

---

## Getting Started

### Prerequisites

- Python 3.13+
- pip

### Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd ReadPulse/ReadPulse

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply migrations
python manage.py migrate

# 4. (Optional) Seed community data
python manage.py seed_community

# 5. Run the development server
python manage.py runserver
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## Environment & Configuration

All configuration lives in `ReadPulse/settings.py`. Key settings to review before deploying:

| Setting | Description |
|---|---|
| `SECRET_KEY` | Replace with a secure random key in production |
| `DEBUG` | Set to `False` in production |
| `GOOGLE_BOOKS_API_KEY` | Your Google Books API key |
| `EMAIL_BACKEND` | Set to console backend locally (see below) |
| `SITE_ID` | Auto-switches between local (`2`) and PythonAnywhere (`3`) |

### Local Email Setup

Django-allauth sends a confirmation email on signup. To avoid connection errors locally, add this to `settings.py`:

```python
if "pythonanywhere" in socket.gethostname():
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

---

## Project Structure

```
ReadPulse/
├── ReadPulse/              # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── books/                  # Main app
│   ├── models.py           # FavoriteBook, CommunityBook, BookRequest
│   ├── views.py            # Page views + REST API endpoints
│   ├── urls.py             # URL routing
│   ├── admin.py
│   └── management/
│       └── commands/
│           └── seed_community.py
├── templates/
│   └── books/              # HTML templates
├── static/
│   ├── css/main.css
│   ├── js/
│   │   ├── main.js         # Search, book reader, audio player
│   │   ├── community.js
│   │   ├── my_listings.js
│   │   └── requests.js
│   └── img/
├── db.sqlite3
├── manage.py
└── requirements.txt
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/search/` | Search books via Google Books |
| GET | `/api/search-audiobooks/` | Search audiobooks via LibriVox |
| GET | `/api/audiobook-rss/` | Proxy LibriVox RSS for inline playback |
| GET | `/api/books/<id>/` | Get book detail |
| GET/POST | `/api/favorites/` | List / add favorites |
| DELETE | `/api/favorites/<id>/remove/` | Remove a favorite |
| GET | `/api/community/` | Browse community listings |
| POST | `/api/community/add/` | Add a listing |
| GET | `/api/community/my-listings/` | Your listings |
| POST | `/api/requests/create/` | Send a borrow/swap request |
| GET | `/api/requests/mine/` | Requests you made |
| GET | `/api/requests/for-me/` | Requests on your listings |
| PATCH | `/api/requests/<id>/` | Update request status |

---

## Deployment (PythonAnywhere)

1. Upload the project files to PythonAnywhere.
2. Set `DEBUG = False` and update `ALLOWED_HOSTS`.
3. Configure a WSGI file pointing to `ReadPulse.wsgi`.
4. Run `python manage.py collectstatic`.
5. Set up your email backend for production SMTP.
6. Ensure `SITE_ID = 3` is active (handled automatically via `socket.gethostname()`).

---

## License

This project was built for educational purposes.
