# 🛍️ Fashion Hub

Fashion Hub is a **Django-based e-commerce web application** designed for modern online shopping.  
It allows users to browse fashion items, view detailed product pages, manage their carts, and securely checkout using Razorpay integration.  

---

## 🚀 Features

### 👕 User-Facing Features
- **Homepage with Hero Banner:** A stylish and responsive homepage banner showcasing brand highlights.  
- **Product Categories:** Browse by Men, Women, or Accessories.  
- **Product Details Page:** Displays multiple images, sizes, and descriptions.  
- **Cart System:** Add, update, or remove items with real-time total updates.  
- **Checkout Page:** Choose a saved address or add a new one, then proceed to Razorpay payment.  
- **User Authentication:**
  - Register, Login, Logout
  - Profile management with image upload
  - Address management (add/edit/delete)
  - Password change and forgot password options  

---

## 🧩 Tech Stack

| Layer | Technology Used |
|-------|------------------|
| **Frontend** | HTML, CSS (Bootstrap 5), JavaScript |
| **Backend** | Django 5+ (Python Framework) |
| **Database** | SQLite3 (default) |
| **Payment Gateway** | Razorpay Integration |
| **Authentication** | Django session-based custom user model |
| **Media Handling** | Django Media Uploads (Profile pictures, Product images) |

---

## ⚙️ Installation and Setup

### 1️⃣ Clone this Repository
```bash
git clone https://github.com/yourusername/fashion-hub.git
cd fashion-hub
2️⃣ Create a Virtual Environment
bash
Copy code
python -m venv venv
venv\Scripts\activate      # For Windows
source venv/bin/activate   # For macOS/Linux
3️⃣ Install Required Dependencies
bash
Copy code
pip install -r requirements.txt
4️⃣ Apply Migrations
bash
Copy code
python manage.py makemigrations
python manage.py migrate
5️⃣ Create a Superuser
bash
Copy code
python manage.py createsuperuser
6️⃣ Run the Development Server
bash
Copy code
python manage.py runserver
Visit:
👉 http://127.0.0.1:8000/ for the main site
👉 http://127.0.0.1:8000/admin/ for the admin panel

🗂️ Project Structure
bash
Copy code
fashion-hub/
│
├── fashionhub/              # Main Django project folder
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── clothes/                 # App for products & categories
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/clothes/
│
├── user/                    # App for user accounts & profiles
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/user/
│
├── order/                   # App for cart, checkout, and payments
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/order/
│
├── static/                  # CSS, JS, Images
├── media/                   # Uploaded images
└── manage.py
🧾 Models Overview
🧍 User Model
Custom user model with profile picture, phone number, gender, and addresses.

🛒 Product Model
Supports multiple product images and size variants.

📦 Cart & Order Models
Session-based cart system.

STRIPE-ready checkout process.

💳 Payment Integration
The checkout process integrates with STRIPE, ensuring secure and fast payments.
You can configure your STRIPE API keys in .env or settings.py:

python
Copy code
STRIPE_KEY_ID = "your_key_here"
STRIPE_KEY_SECRET = "your_secret_here"
👨‍💻 Admin Panel
Access the admin panel to:

Manage products and categories

Manage users and orders

Upload product images

URL: /admin/

📸 Screenshots
🏠 Homepage

🛒 Product Page

👤 Profile Page

💰 Checkout

✨ Future Improvements
Add wishlist and order tracking features

Integrate email verification and password reset

Deploy using AWS or Render

📬 Contact
Developer: Anuj Thakur
📍 Jalandhar, India
📧 anujthakur2004@gmail.com
💼 LinkedIn

