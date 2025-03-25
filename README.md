# Coderr Backend

Dies ist das Backend für die Coderr-Webanwendung, eine Plattform zur Vermittlung zwischen Selbstständigen und Kunden. Die Anwendung ermöglicht die Erstellung, Verwaltung und Bewertung von Angeboten sowie das Erteilen von Aufträgen.

---

## 🚀 Features

- 🔐 Authentifizierung via Token (Registrierung, Login, Profilverwaltung)
- 🧑‍💼 Zwei Benutzertypen: `business` & `customer`
- 🧾 Angebotserstellung mit gestaffelten Angeboten (`basic`, `standard`, `premium`)
- 🛒 Auftragsvergabe und Statusverfolgung
- ⭐ Kundenbewertungen für Business-Nutzer
- 🔍 Filter- und Suchfunktion für Angebote
- 📊 Dashboard-Infos (z. B. durchschnittliche Bewertungen, Anzahl Business-Profile)

---

## 🛠️ Tech Stack

- **Backend Framework**: Django & Django REST Framework
- **Auth**: Token Authentication (`rest_framework.authtoken`)
- **Datenbank**: SQLite (Default, für Entwicklung)
- **Filter & Search**: `django-filter`, `SearchFilter`
- **File Uploads**: Über `ImageField` (z. B. für Profilbilder)

---

## 📂 Projektstruktur (Apps)

| App | Zweck |
|-----|-------|
| `auth_user` | Registrierung, Login, Profilverwaltung |
| `offers` | Angebote & Angebotsdetails |
| `orders` | Auftragserteilung und Verwaltung |
| `reviews` | Kundenbewertungen |
| `baseinfo` | Dashboard-Metriken (z. B. Anzahl Business-Profile) |

---

## 🔧 Setup

### 1. Repository klonen

```bash
git clone https://github.com/UriOriKay/Coderr-Backend
cd coderr-backend
```

### 2. Virtuelles Environment erstellen

```bash
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
```

### 3. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### 4. Migrationen anwenden & Starten

```bash
python manage.py migrate
python manage.py runserver
```

---

## 🔐 API Endpoints

Hier ein Auszug der wichtigsten Endpunkte:

### Authentifizierung
- `POST /api/register/`
- `POST /api/login/`
- `GET /api/profile/<pk>/`
- `PATCH /api/profile/<pk>/`

### Angebote
- `GET /api/offers/`
- `POST /api/offers/`
- `GET /api/offers/<id>/`
- `PATCH /api/offers/<id>/`
- `DELETE /api/offers/<id>/`

### Aufträge
- `POST /api/orders/`
- `GET /api/orders/`
- `PATCH /api/orders/<id>/`
- `DELETE /api/orders/<id>/`

### Bewertungen
- `GET /api/reviews/`
- `POST /api/reviews/`
- `PATCH /api/reviews/<id>/`
- `DELETE /api/reviews/<id>/`


## ✅ Rollen & Berechtigungen

| Rolle | Rechte |
|-------|--------|
| **Customer** | Angebote sehen, Aufträge erteilen, Bewertungen abgeben |
| **Business** | Angebote erstellen/bearbeiten, Aufträge bearbeiten |
| **Admin** | Vollzugriff, inkl. Löschen von Angeboten, Bewertungen etc. |

---

## ✍️ Autor

Kay Schumacher  
📬 **Kay@uriori.de*



