
# Coderr Backend

This is the backend for the **Coderr** web application – a platform connecting freelancers and clients. The app enables users to create, manage, and evaluate offers, as well as assign and track orders.

---

## 🚀 Features

- 🔐 Token-based authentication (registration, login, profile management)
- 🧑‍💼 Two user types: `business` & `customer`
- 🧾 Offer creation with tiered packages (`basic`, `standard`, `premium`)
- 🛒 Order assignment and status tracking
- ⭐ Customer reviews for business users
- 🔍 Offer filtering and search functionality
- 📊 Dashboard info (e.g. average rating, business profile count)

---

## 🛠️ Tech Stack

- **Backend Framework**: Django & Django REST Framework
- **Authentication**: Token Authentication (`rest_framework.authtoken`)
- **Database**: SQLite (default for development)
- **Filtering & Search**: `django-filter`, `SearchFilter`
- **File Uploads**: via `ImageField` (e.g. for profile pictures)

---

## 📂 Project Structure (Apps)

| App         | Purpose                                 |
|-------------|-----------------------------------------|
| `auth_user` | Registration, login, profile management |
| `offers`    | Offer listings and details              |
| `orders`    | Order creation and management           |
| `reviews`   | Customer reviews                        |
| `baseinfo`  | Dashboard metrics                       |

---

## 🔧 Setup

### 1. Clone the repository

```bash
git clone https://github.com/UriOriKay/Coderr-Backend
cd coderr-backend
```

### 2. Create a virtual environment

```bash
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env` file

Create a `.env` file in the project root and add the following line:

```env
SECRET_KEY=your-secret-key-here
```

> 🔑 You will receive the required `SECRET_KEY` via email.  
> Please contact [Kay@uriori.de](mailto:Kay@uriori.de) to request access.

### 5. Apply migrations and start the server

```bash
python manage.py migrate
python manage.py runserver
```

---

## 🔐 API Endpoints (Overview)

### Authentication
- `POST /api/register/`
- `POST /api/login/`
- `GET /api/profile/<pk>/`
- `PATCH /api/profile/<pk>/`

### Offers
- `GET /api/offers/`
- `POST /api/offers/`
- `GET /api/offers/<id>/`
- `PATCH /api/offers/<id>/`
- `DELETE /api/offers/<id>/`

### Orders
- `POST /api/orders/`
- `GET /api/orders/`
- `PATCH /api/orders/<id>/`
- `DELETE /api/orders/<id>/`

### Reviews
- `GET /api/reviews/`
- `POST /api/reviews/`
- `PATCH /api/reviews/<id>/`
- `DELETE /api/reviews/<id>/`

---

## ✅ Roles & Permissions

| Role       | Permissions                                         |
|------------|-----------------------------------------------------|
| **Customer** | View offers, place orders, leave reviews          |
| **Business** | Create/edit offers, manage orders                 |
| **Admin**    | Full access, including deletion of all resources  |

---

## ✍️ Author

**Kay Schumacher**  
📬 [Kay@uriori.de](mailto:Kay@uriori.de)
