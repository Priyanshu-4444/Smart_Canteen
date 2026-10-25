
from flask import Flask, render_template, request, session, redirect, g
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Secret key for login sessions
app.secret_key = "smart_canteen_secret_key"


# =========================
# MYSQL DATABASE CONNECTION
# =========================

import os
import pymysql

import os
import pymysql

def get_db_connection():
    db_host = os.environ.get("DB_HOST", "127.0.0.1")

    db_config = {
        "host": db_host,
        "port": int(os.environ.get("DB_PORT", 3307)),
        "user": os.environ.get("DB_USER", "root"),
        "password": os.environ.get("DB_PASSWORD", ""),
        "database": os.environ.get("DB_NAME", "canteen_db"),
        "connect_timeout": 10,
        "cursorclass": pymysql.cursors.Cursor
    }

    # Enable SSL when connecting to the online Aiven database
    if db_host != "127.0.0.1" and db_host != "localhost":
        db_config["ssl"] = {"ssl": {}}

    return pymysql.connect(**db_config)

# =========================
# SHARED DATABASE CONNECTION
# =========================

class DatabaseProxy:
    def get_connection(self):
        if "db_connection" not in g:
            g.db_connection = get_db_connection()
        return g.db_connection

    def __getattr__(self, name):
        return getattr(self.get_connection(), name)


# Existing routes can continue using db.cursor(), db.commit(), etc.
db = DatabaseProxy()


@app.teardown_appcontext
def close_db_connection(exception=None):
    connection = g.pop("db_connection", None)

    if connection is not None:
        connection.close()


# =========================
# HOME PAGE
# =========================


@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Smart Canteen | Fresh Food, Fast Service</title>

        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: Arial, sans-serif;
            }

            :root {
                --orange: #f97316;
                --dark: #25251f;
                --cream: #fffaf2;
                --muted: #716d65;
            }

            body {
                background: var(--cream);
                color: var(--dark);
                line-height: 1.6;
            }

            a {
                text-decoration: none;
            }

            .navbar {
                min-height: 76px;
                padding: 15px 7%;
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 20px;
                background: rgba(255, 255, 255, .96);
                border-bottom: 1px solid #f0e8dc;
            }

            .brand {
                color: var(--dark);
                font-size: 23px;
                font-weight: 800;
            }

            .brand span {
                color: var(--orange);
            }

            .nav-links {
                display: flex;
                align-items: center;
                gap: 24px;
                flex-wrap: wrap;
            }

            .nav-links a {
                color: #45423d;
                font-weight: 600;
                font-size: 14px;
            }

            .nav-links a:hover {
                color: var(--orange);
            }

            .nav-button, .primary-btn {
                background: var(--orange);
                color: white !important;
                padding: 12px 20px;
                border-radius: 10px;
                display: inline-block;
                font-weight: 700;
                transition: .2s;
            }

            .nav-button:hover, .primary-btn:hover {
                background: #ea580c;
                transform: translateY(-2px);
            }

            .hero {
                padding: 65px 7% 75px;
                display: grid;
                grid-template-columns: 1.1fr .9fr;
                align-items: center;
                gap: 45px;
                overflow: hidden;
                background:
                    radial-gradient(circle at 90% 10%, #ffe0bd 0, transparent 30%),
                    linear-gradient(135deg, #fffaf2, #fff0db);
            }

            .eyebrow {
                display: inline-block;
                background: #ffead5;
                color: #b94b08;
                border-radius: 30px;
                padding: 8px 14px;
                font-size: 13px;
                font-weight: 700;
                margin-bottom: 20px;
            }

            h1 {
                font-size: clamp(38px, 5vw, 62px);
                line-height: 1.12;
                letter-spacing: -2px;
                margin-bottom: 22px;
            }

            h1 span {
                color: var(--orange);
            }

            .hero p {
                color: var(--muted);
                max-width: 490px;
                margin-bottom: 28px;
                font-size: 17px;
            }

            .hero-actions {
                display: flex;
                gap: 13px;
                flex-wrap: wrap;
            }

            .secondary-btn {
                display: inline-block;
                padding: 11px 20px;
                border: 1px solid #e3d6c5;
                border-radius: 10px;
                color: var(--dark);
                font-weight: 700;
                background: white;
            }

            .food-art {
                min-height: 340px;
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .food-circle {
                width: min(320px, 75vw);
                height: min(320px, 75vw);
                border-radius: 50%;
                background: linear-gradient(145deg, #ffb65e, #f97316);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: clamp(100px, 17vw, 165px);
                box-shadow: 0 25px 60px #e88a4a35;
                transform: rotate(-7deg);
            }

            .floating-card {
                position: absolute;
                background: white;
                border: 1px solid #f2e9dd;
                padding: 13px 17px;
                border-radius: 15px;
                box-shadow: 0 12px 30px #47301b12;
                font-size: 14px;
                font-weight: 700;
            }

            .floating-card small {
                display: block;
                color: var(--muted);
                font-weight: 400;
            }

            .card-top {
                top: 25px;
                right: 0;
            }

            .card-bottom {
                bottom: 25px;
                left: 0;
            }

            .section {
                padding: 65px 7%;
            }

            .section-heading {
                text-align: center;
                margin-bottom: 35px;
            }

            .section-heading h2 {
                font-size: clamp(27px, 4vw, 36px);
                margin-bottom: 8px;
            }

            .section-heading p {
                color: var(--muted);
            }

            .categories {
                display: grid;
                grid-template-columns: repeat(6, minmax(0, 1fr));
                gap: 15px;
            }

            .category {
                text-align: center;
                background: white;
                border: 1px solid #f0e8dc;
                border-radius: 17px;
                padding: 22px 8px;
                transition: .2s;
            }

            .category:hover {
                transform: translateY(-5px);
                border-color: #fdba74;
                box-shadow: 0 10px 25px #70451b0c;
            }

            .category .emoji {
                font-size: 34px;
                display: block;
                margin-bottom: 8px;
            }

            .category h3 {
                font-size: 13px;
            }

            .features {
                background: white;
            }

            .feature-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 20px;
            }

            .feature {
                padding: 27px;
                border: 1px solid #f0e8dc;
                border-radius: 18px;
                background: #fffdf9;
            }

            .feature-icon {
                font-size: 32px;
                margin-bottom: 12px;
            }

            .feature h3 {
                margin-bottom: 7px;
            }

            .feature p {
                color: var(--muted);
                font-size: 14px;
            }

            .steps {
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 15px;
            }

            .step {
                text-align: center;
                padding: 20px 10px;
            }

            .step-number {
                width: 46px;
                height: 46px;
                border-radius: 50%;
                margin: 0 auto 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: #ffead5;
                color: #c4510b;
                font-weight: 800;
            }

            .step p {
                color: var(--muted);
                font-size: 14px;
            }

            .cta {
                margin: 0 7% 65px;
                padding: 40px 25px;
                text-align: center;
                border-radius: 22px;
                color: white;
                background: linear-gradient(120deg, #f97316, #c2410c);
            }

            .cta h2 {
                font-size: clamp(26px, 4vw, 35px);
                margin-bottom: 8px;
            }

            .cta p {
                margin-bottom: 20px;
                color: #fff1e7;
            }

            .cta .primary-btn {
                background: white;
                color: #c2410c !important;
            }

            footer {
                padding: 25px 7%;
                background: #25251f;
                color: #d6d3cd;
                text-align: center;
                font-size: 13px;
            }

            @media (max-width: 900px) {
                .hero {
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                }

                .categories {
                    grid-template-columns: repeat(3, minmax(0, 1fr));
                }

                .feature-grid {
                    grid-template-columns: 1fr;
                }
            }

            @media (max-width: 600px) {
                .navbar {
                    padding: 15px 5%;
                    align-items: flex-start;
                    flex-direction: column;
                }

                .nav-links {
                    gap: 14px;
                }

                .hero {
                    grid-template-columns: 1fr;
                    padding: 45px 6%;
                }

                .food-art {
                    min-height: 300px;
                }

                .section {
                    padding: 45px 6%;
                }

                .categories {
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                }

                .steps {
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                }

                .cta {
                    margin: 0 5% 45px;
                }
            }
        </style>
    </head>

    <body>

        <nav class="navbar">
            <a class="brand" href="/">🍴 Smart<span>Canteen</span></a>

            <div class="nav-links">
                <a href="/">Home</a>
                <a href="/login">Menu</a>
                <a href="/login">Track Orders</a>
                <a href="/login">Login</a>
                <a href="/register" class="nav-button">Get Started →</a>
            </div>
        </nav>

        <section class="hero">
            <div>
                <div class="eyebrow">🍊 Your campus food, made easier</div>

                <h1>Good food.<br>
                    Great mood.<br>
                    <span>Zero hassle.</span>
                </h1>

                <p>
                    Order your favourite canteen meals online,
                    manage your cart and track your order.
                    More convenience, less waiting.
                </p>

                <div class="hero-actions">
                    <a href="/register" class="primary-btn">
                        🍔 Order Your Food
                    </a>

                    <a href="/login" class="secondary-btn">
                        Sign In →
                    </a>
                </div>
            </div>

            <div class="food-art">
                <div class="food-circle">🍔</div>

                <div class="floating-card card-top">
                    🍟 Fresh favourites
                    <small>Your campus food stop</small>
                </div>

                <div class="floating-card card-bottom">
                    🎟️ Digital order tokens
                    <small>Follow your order status</small>
                </div>
            </div>
        </section>

        <section class="section">
            <div class="section-heading">
                <h2>Something for every craving</h2>
                <p>Explore popular canteen food categories.</p>
            </div>

            <div class="categories">
                <div class="category">
                    <span class="emoji">🥞</span>
                    <h3>South Indian</h3>
                </div>

                <div class="category">
                    <span class="emoji">🥪</span>
                    <h3>Snacks</h3>
                </div>

                <div class="category">
                    <span class="emoji">☕</span>
                    <h3>Beverages</h3>
                </div>

                <div class="category">
                    <span class="emoji">🍱</span>
                    <h3>Lunch & Thali</h3>
                </div>

                <div class="category">
                    <span class="emoji">🍕</span>
                    <h3>Fast Food</h3>
                </div>

                <div class="category">
                    <span class="emoji">🍰</span>
                    <h3>Desserts</h3>
                </div>
            </div>
        </section>

        <section class="section features">
            <div class="section-heading">
                <h2>Your canteen, upgraded</h2>
                <p>Simple features for a smoother food-ordering experience.</p>
            </div>

            <div class="feature-grid">
                <div class="feature">
                    <div class="feature-icon">🛒</div>
                    <h3>Easy Online Ordering</h3>
                    <p>Browse available dishes, add items to your cart
                    and place your order in a few simple steps.</p>
                </div>

                <div class="feature">
                    <div class="feature-icon">🎟️</div>
                    <h3>Digital Order Tokens</h3>
                    <p>Get a token when your order is placed and use it
                    to identify your order.</p>
                </div>

                <div class="feature">
                    <div class="feature-icon">📦</div>
                    <h3>Order Tracking</h3>
                    <p>Check your order status and see when your food
                    is being prepared or is ready.</p>
                </div>
            </div>
        </section>

        <section class="section">
            <div class="section-heading">
                <h2>How it works</h2>
                <p>Your next meal is just a few steps away.</p>
            </div>

            <div class="steps">
                <div class="step">
                    <div class="step-number">1</div>
                    <h3>Browse</h3>
                    <p>Explore the available food menu.</p>
                </div>

                <div class="step">
                    <div class="step-number">2</div>
                    <h3>Add to Cart</h3>
                    <p>Select dishes and quantities.</p>
                </div>

                <div class="step">
                    <div class="step-number">3</div>
                    <h3>Place Order</h3>
                    <p>Confirm your order and get a token.</p>
                </div>

                <div class="step">
                    <div class="step-number">4</div>
                    <h3>Collect</h3>
                    <p>Track the status and collect your food.</p>
                </div>
            </div>
        </section>

        <section class="cta">
            <h2>Ready for your next favourite meal?</h2>
            <p>Create your account and start exploring the canteen menu.</p>
            <a href="/register" class="primary-btn">Create Free Account →</a>
        </section>

        <footer>
            © Smart Canteen Management System | Made for campus convenience 🍴
        </footer>

    </body>
    </html>
    """
# =========================
# REGISTER
# =========================


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        hashed_password = generate_password_hash(password)

        db = get_db_connection()
        cursor = db.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO users
                (name, email, password, role)
                VALUES (%s, %s, %s, %s)
                """,
                (name, email, hashed_password, role)
            )

            db.commit()

        except pymysql.err.IntegrityError:
            db.rollback()
            return """
                <h2>Email already registered!</h2>
                <a href="/register">Try Again</a>
            """

        finally:
            cursor.close()
            db.close()

        return """
            <h2>Registration successful! 🎉</h2>
            <a href="/login">Go to Login</a>
        """

    return render_template("register.html")

# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        db = get_db_connection()
        cursor = db.cursor()

        try:
            cursor.execute(
                """
                SELECT *
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

            user = cursor.fetchone()

        finally:
            cursor.close()
            db.close()

        if user and check_password_hash(user[3], password):

            # Save user information in session
            session["user_id"] = user[0]
            session["name"] = user[1]
            session["email"] = user[2]
            session["role"] = user[4]

            # Redirect admin to admin dashboard
            if user[4].lower() == "admin":
                return redirect("/admin")

            # Redirect student to dashboard
            return redirect("/dashboard")

        else:
            return """
                <h2>❌ Invalid email or password</h2>
                <a href="/login">Try Again</a>
            """

    return render_template("login.html")

# =========================
# STUDENT DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    # Check login
    if "email" not in session:

        return redirect("/login")

    cursor = db.cursor()

    # Count student's orders
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM orders
        WHERE student_email = %s
        """,
        (session["email"],)
    )

    total_orders = cursor.fetchone()[0]

    cursor.close()

    return render_template(
        "dashboard.html",
        name=session["name"],
        email=session["email"],
        role=session["role"],
        total_orders=total_orders
    )


# =========================
# CANTEEN MENU
# =========================

@app.route("/menu")
def menu():

    if "email" not in session:

        return redirect("/login")

    search = request.args.get("search", "")
    category = request.args.get("category", "")

    cursor = db.cursor()

    query = """
        SELECT *
        FROM menu
        WHERE availability = 'Available'
    """

    values = []

    if search:

        query += """
            AND item_name LIKE %s
        """

        values.append("%" + search + "%")


    if category:

        query += """
            AND category = %s
        """

        values.append(category)


    query += """
        ORDER BY id DESC
    """


    cursor.execute(
        query,
        values
    )

    items = cursor.fetchall()


    # Get categories
    cursor.execute(
        """
        SELECT DISTINCT category
        FROM menu
        WHERE availability = 'Available'
        ORDER BY category
        """
    )

    categories = cursor.fetchall()

    cursor.close()


    return render_template(
        "menu.html",
        items=items,
        categories=categories,
        search=search,
        selected_category=category
    )
# =========================
# CREATE ORDERS TABLE
# =========================

@app.route("/create_orders_table")
def create_orders_table():

    cursor = db.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (

            id INT AUTO_INCREMENT PRIMARY KEY,

            student_email VARCHAR(100) NOT NULL,

            item_name VARCHAR(100) NOT NULL,

            price DECIMAL(10,2) NOT NULL,

            quantity INT NOT NULL,

            total DECIMAL(10,2) NOT NULL,

            order_status VARCHAR(30)
            DEFAULT 'Pending',

            order_date TIMESTAMP
            DEFAULT CURRENT_TIMESTAMP

        )
        """
    )

    db.commit()

    cursor.close()

    return """
        <h2>Orders table created successfully! 🎉</h2>

        <a href="/menu">Go to Menu</a>
    """
@app.route("/cart")
def cart():
    if "email" not in session:
        return redirect("/login")

    student_email = session["email"]

    cursor = db.cursor()

    cursor.execute(
        """
        SELECT *
        FROM cart
        WHERE student_email = %s
        ORDER BY id DESC
        """,
        (student_email,)
    )

    cart_items = cursor.fetchall()

    grand_total = 0

    for item in cart_items:
        grand_total += float(item[5])

    cursor.close()

    return render_template(
        "cart.html",
        cart_items=cart_items,
        grand_total=grand_total
    )

@app.route("/remove_from_cart/<int:cart_id>", methods=["POST"])
def remove_from_cart(cart_id):
    if "email" not in session:
        return redirect("/login")

    cursor = db.cursor()

    cursor.execute(
        """
        DELETE FROM cart
        WHERE id = %s
        AND student_email = %s
        """,
        (cart_id, session["email"])
    )

    db.commit()
    cursor.close()

    return redirect("/cart")

@app.route("/update_cart/<int:cart_id>", methods=["POST"])
def update_cart(cart_id):
    if "email" not in session:
        return redirect("/login")

    quantity = int(request.form["quantity"])

    if quantity < 1:
        quantity = 1

    if quantity > 10:
        quantity = 10

    cursor = db.cursor()

    # Get the cart item
    cursor.execute(
        """
        SELECT price
        FROM cart
        WHERE id = %s
        AND student_email = %s
        """,
        (cart_id, session["email"])
    )

    item = cursor.fetchone()

    if item:
        price = float(item[0])
        total = price * quantity

        cursor.execute(
            """
            UPDATE cart
            SET quantity = %s,
                total = %s
            WHERE id = %s
            AND student_email = %s
            """,
            (
                quantity,
                total,
                cart_id,
                session["email"]
            )
        )

        db.commit()

    cursor.close()

    return redirect("/cart")

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if "email" not in session:
        return redirect("/login")

    student_email = session["email"]

    cursor = db.cursor()

    # Get cart items
    cursor.execute(
        """
        SELECT *
        FROM cart
        WHERE student_email = %s
        """,
        (student_email,)
    )

    cart_items = cursor.fetchall()

    if not cart_items:
        cursor.close()
        return """
            <h2>🛒 Your cart is empty!</h2>
            <a href="/menu">Go to Menu</a>
        """

        # Generate a unique token for today's order
    cursor.execute(
        """
        SELECT COUNT(DISTINCT token)
        FROM orders
        WHERE DATE(order_date) = CURDATE()
        AND token IS NOT NULL
        """
    )

    today_tokens = cursor.fetchone()[0]
    token_number = today_tokens + 1
    token = f"A{token_number:03d}"

    # Add every cart item to orders using the same token
    for item in cart_items:
        cursor.execute(
            """
            INSERT INTO orders
            (
                token,
                student_email,
                item_name,
                price,
                quantity,
                total,
                order_status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                token,
                student_email,
                item[2],
                item[3],
                item[4],
                item[5],
                "Pending"
            )
        )
    # Empty the cart
    cursor.execute(
        """
        DELETE FROM cart
        WHERE student_email = %s
        """,
        (student_email,)
    )

    db.commit()
    cursor.close()

    return f"""
        <!DOCTYPE html>
        <html lang="en">

        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">

            <title>Order Successful - Smart Canteen</title>

            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    font-family: Arial, sans-serif;
                }}

                body {{
                    min-height: 100vh;
                    background: linear-gradient(135deg, #fff3e0, #ffcc80);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 20px;
                }}

                .container {{
                    width: 100%;
                    max-width: 500px;
                    background: white;
                    padding: 40px 30px;
                    border-radius: 20px;
                    text-align: center;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
                }}

                .success {{
                    font-size: 55px;
                    margin-bottom: 10px;
                }}

                h1 {{
                    color: #2e7d32;
                    margin-bottom: 10px;
                }}

                .message {{
                    color: #555;
                    margin-bottom: 25px;
                }}

                .token-box {{
                    background: #fff3e0;
                    border: 2px dashed #ff6f00;
                    border-radius: 15px;
                    padding: 20px;
                    margin: 20px 0;
                }}

                .token-label {{
                    color: #777;
                    font-size: 14px;
                    margin-bottom: 5px;
                }}

                .token {{
                    color: #e65100;
                    font-size: 42px;
                    font-weight: bold;
                    letter-spacing: 4px;
                }}

                .status {{
                    display: inline-block;
                    background: #fff8e1;
                    color: #f57c00;
                    padding: 8px 18px;
                    border-radius: 20px;
                    font-weight: bold;
                    margin-bottom: 25px;
                }}

                .btn {{
                    display: block;
                    text-decoration: none;
                    padding: 13px;
                    border-radius: 10px;
                    margin-top: 12px;
                    font-weight: bold;
                }}

                .orders {{
                    background: #ff6f00;
                    color: white;
                }}

                .menu {{
                    border: 2px solid #ff6f00;
                    color: #e65100;
                }}

                .dashboard {{
                    color: #666;
                }}
            </style>
        </head>

        <body>

            <div class="container">

                <div class="success">🎉</div>

                <h1>Order Placed Successfully!</h1>

                <p class="message">
                    Your order has been sent to the canteen.
                </p>

                <div class="token-box">

                    <div class="token-label">
                        Your Digital Token
                    </div>

                    <div class="token">
                        {token}
                    </div>

                </div>

                <div class="status">
                    🕐 Pending
                </div>

                <a href="/my_orders" class="btn orders">
                    📋 View My Orders
                </a>

                <a href="/menu" class="btn menu">
                    🍔 Back to Menu
                </a>

                <a href="/dashboard" class="btn dashboard">
                    🏠 Dashboard
                </a>

            </div>

        </body>
        </html>
    """

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    if "email" not in session:
        return redirect("/login")

    student_email = session["email"]
    item_name = request.form["item_name"]
    price = float(request.form["price"])
    quantity = int(request.form["quantity"])

    total = price * quantity

    cursor = db.cursor()

    # Check if item is already in cart
    cursor.execute(
        """
        SELECT id, quantity
        FROM cart
        WHERE student_email = %s
        AND item_name = %s
        """,
        (student_email, item_name)
    )

    existing_item = cursor.fetchone()

    if existing_item:
        new_quantity = existing_item[1] + quantity
        new_total = price * new_quantity

        cursor.execute(
            """
            UPDATE cart
            SET quantity = %s,
                total = %s
            WHERE id = %s
            """,
            (new_quantity, new_total, existing_item[0])
        )

    else:
        cursor.execute(
            """
            INSERT INTO cart
            (
                student_email,
                item_name,
                price,
                quantity,
                total
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                student_email,
                item_name,
                price,
                quantity,
                total
            )
        )

    db.commit()
    cursor.close()

    return redirect("/cart")

# =========================
# PLACE ORDER
# =========================

@app.route("/order", methods=["POST"])
def order():

    if "email" not in session:

        return redirect("/login")

    # Get actual logged-in student's email
    student_email = session["email"]

    item_name = request.form["item_name"]

    price = float(request.form["price"])

    quantity = int(request.form["quantity"])

    # Calculate total
    total = price * quantity

    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO orders
        (
            student_email,
            item_name,
            price,
            quantity,
            total,
            order_status
        )

        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """,
        (
            student_email,
            item_name,
            price,
            quantity,
            total,
            "Pending"
        )
    )

    db.commit()

    cursor.close()

    return f"""
        <html>

        <head>

            <title>Order Successful</title>

        </head>

        <body>

            <h1>🎉 Order placed successfully!</h1>

            <hr>

            <p>
                <strong>Student:</strong>
                {student_email}
            </p>

            <p>
                <strong>Item:</strong>
                {item_name}
            </p>

            <p>
                <strong>Quantity:</strong>
                {quantity}
            </p>

            <p>
                <strong>Price:</strong>
                ₹{price:.2f}
            </p>

            <p>
                <strong>Total:</strong>
                ₹{total:.2f}
            </p>

            <p>
                <strong>Status:</strong>
                Pending
            </p>

            <br>

            <a href="/menu">
                🍔 Back to Menu
            </a>

            <br><br>

            <a href="/my_orders">
                📋 View My Orders
            </a>

        </body>

        </html>
    """


# =========================
# MY ORDERS
# =========================

@app.route("/my_orders")
def my_orders():

    if "email" not in session:

        return redirect("/login")

    # Get actual logged-in student's email
    student_email = session["email"]

    cursor = db.cursor()

    cursor.execute(
        """
        SELECT *
        FROM orders
        WHERE student_email = %s
        ORDER BY order_date DESC
        """,
        (student_email,)
    )

    orders = cursor.fetchall()

    cursor.close()

    return render_template(
        "my_orders.html",
        orders=orders
    )


# =========================
# ADMIN DASHBOARD
# =========================

@app.route("/admin")
def admin():

    # Check login
    if "email" not in session:
        return redirect("/login")

    # Check admin role
    if session["role"].lower() != "admin":
        return """
            <h2>❌ Access Denied</h2>

            <p>Only administrators can access this page.</p>

            <a href="/dashboard">
                Go to Dashboard
            </a>
        """

    # Get search and status filter
    search = request.args.get("search", "")
    status = request.args.get("status", "")

    cursor = db.cursor()

    # Get orders
    query = """
        SELECT *
        FROM orders
        WHERE 1=1
    """

    values = []

    # Search student email or food item
    if search:
        query += """
            AND (
                student_email LIKE %s
                OR item_name LIKE %s
            )
        """

        values.append("%" + search + "%")
        values.append("%" + search + "%")

    # Filter by status
    if status:
        query += """
            AND order_status = %s
        """

        values.append(status)

    query += """
        ORDER BY order_date DESC
    """

    cursor.execute(query, values)

    orders = cursor.fetchall()


    # Total orders
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM orders
        """
    )

    total_orders = cursor.fetchone()[0]


    # Pending orders
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM orders
        WHERE order_status = 'Pending'
        """
    )

    pending_orders = cursor.fetchone()[0]


    # Total students
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM users
        WHERE role = 'student'
        """
    )

    total_students = cursor.fetchone()[0]


    # Total menu items
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM menu
        """
    )

    total_menu_items = cursor.fetchone()[0]


    # Today's orders
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM orders
        WHERE DATE(order_date) = CURDATE()
        """
    )

    todays_orders = cursor.fetchone()[0]


    # Today's revenue
    cursor.execute(
        """
        SELECT COALESCE(SUM(total), 0)
        FROM orders
        WHERE DATE(order_date) = CURDATE()
        """
    )

    todays_revenue = cursor.fetchone()[0]


    cursor.close()


    return render_template(
        "admin_dashboard.html",
        name=session["name"],
        email=session["email"],
        orders=orders,
        total_orders=total_orders,
        pending_orders=pending_orders,
        total_students=total_students,
        total_menu_items=total_menu_items,
        todays_orders=todays_orders,
        todays_revenue=todays_revenue,
        search=search,
        selected_status=status
    )

# =========================
# UPDATE ORDER STATUS
# =========================

@app.route("/update_order", methods=["POST"])
def update_order():

    # Check login
    if "email" not in session:

        return redirect("/login")

    # Check admin role
    if session["role"].lower() != "admin":

        return """
            <h2>❌ Access Denied</h2>

            <a href="/dashboard">Go to Dashboard</a>
        """

    order_id = request.form["order_id"]

    status = request.form["status"]

    cursor = db.cursor()

    cursor.execute(
        """
        UPDATE orders

        SET order_status = %s

        WHERE id = %s
        """,
        (status, order_id)
    )

    db.commit()

    cursor.close()

    return redirect("/admin")

# =========================
# ADD MENU ITEM
# =========================

@app.route("/add_menu", methods=["GET", "POST"])
def add_menu():

    # Check login
    if "email" not in session:
        return redirect("/login")

    # Check admin role
    if session["role"].lower() != "admin":
        return """
            <h2>❌ Access Denied</h2>
            <a href="/dashboard">Go to Dashboard</a>
        """

    if request.method == "POST":

        item_name = request.form["item_name"]
        price = request.form["price"]
        category = request.form["category"]
        prep_time = request.form["prep_time"]
        availability = request.form["availability"]

        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO menu
            (item_name, price, category, prep_time, availability)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                item_name,
                price,
                category,
                prep_time,
                availability
            )
        )

        db.commit()
        cursor.close()

        return redirect("/admin/menu")

    return render_template("add_menu.html")

# =========================
# ADMIN MENU MANAGEMENT
# =========================

@app.route("/admin/menu")
def admin_menu():

    # Check login
    if "email" not in session:
        return redirect("/login")

    # Check admin role
    if session["role"].lower() != "admin":
        return """
            <h2>❌ Access Denied</h2>
            <a href="/dashboard">Go to Dashboard</a>
        """

    cursor = db.cursor()

    cursor.execute(
        """
        SELECT *
        FROM menu
        ORDER BY id DESC
        """
    )

    items = cursor.fetchall()

    cursor.close()

    return render_template(
        "admin_menu.html",
        items=items
    )
# =========================
# EDIT MENU ITEM
# =========================

@app.route("/edit_menu/<int:item_id>", methods=["GET", "POST"])
def edit_menu(item_id):

    # Check login
    if "email" not in session:
        return redirect("/login")

    # Check admin role
    if session["role"].lower() != "admin":
        return """
            <h2>❌ Access Denied</h2>
            <a href="/dashboard">Go to Dashboard</a>
        """

    cursor = db.cursor()

    # Update item
    if request.method == "POST":

        item_name = request.form["item_name"]
        price = request.form["price"]
        category = request.form["category"]
        availability = request.form["availability"]

        cursor.execute(
            """
            UPDATE menu

            SET item_name = %s,
                price = %s,
                category = %s,
                availability = %s

            WHERE id = %s
            """,
            (
                item_name,
                price,
                category,
                availability,
                item_id
            )
        )

        db.commit()

        cursor.close()

        return redirect("/admin/menu")

    # Get item information
    cursor.execute(
        """
        SELECT *
        FROM menu
        WHERE id = %s
        """,
        (item_id,)
    )

    item = cursor.fetchone()

    cursor.close()

    if not item:
        return """
            <h2>❌ Menu item not found</h2>
            <a href="/admin/menu">Back to Menu Management</a>
        """

    return render_template(
        "edit_menu.html",
        item=item
    )
# =========================
# DELETE MENU ITEM
# =========================

@app.route("/delete_menu/<int:item_id>", methods=["POST"])
def delete_menu(item_id):

    # Check login
    if "email" not in session:
        return redirect("/login")

    # Check admin role
    if session["role"].lower() != "admin":
        return """
            <h2>❌ Access Denied</h2>
            <a href="/dashboard">Go to Dashboard</a>
        """

    cursor = db.cursor()

    cursor.execute(
        """
        DELETE FROM menu
        WHERE id = %s
        """,
        (item_id,)
    )

    db.commit()

    cursor.close()

    return redirect("/admin/menu")
# =========================
# TOGGLE MENU AVAILABILITY
# =========================

@app.route("/toggle_menu/<int:item_id>", methods=["POST"])
def toggle_menu(item_id):

    # Check login
    if "email" not in session:
        return redirect("/login")

    # Check admin role
    if session["role"].lower() != "admin":
        return """
            <h2>❌ Access Denied</h2>
            <a href="/dashboard">Go to Dashboard</a>
        """

    cursor = db.cursor()

    # Get current availability
    cursor.execute(
        """
        SELECT availability
        FROM menu
        WHERE id = %s
        """,
        (item_id,)
    )

    item = cursor.fetchone()

    if item:

        current_status = item[0]

        if current_status == "Available":
            new_status = "Unavailable"
        else:
            new_status = "Available"

        cursor.execute(
            """
            UPDATE menu
            SET availability = %s
            WHERE id = %s
            """,
            (new_status, item_id)
        )

        db.commit()

    cursor.close()

    return redirect("/admin/menu")
# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

@app.route("/create_cart_table")
def create_cart_table():
    cursor = db.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS cart (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_email VARCHAR(100) NOT NULL,
            item_name VARCHAR(100) NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            quantity INT NOT NULL,
            total DECIMAL(10,2) NOT NULL
        )
        """
    )

    db.commit()
    cursor.close()

    return """
        <h2>Cart table created successfully! 🛒</h2>
        <a href="/menu">Go to Menu</a>
    """
@app.route("/receipt/<int:order_id>")
def receipt(order_id):

    if "email" not in session:
        return redirect("/login")

    cursor = db.cursor()

    cursor.execute(
        """
        SELECT *
        FROM orders
        WHERE id = %s
        AND student_email = %s
        """,
        (order_id, session["email"])
    )

    order = cursor.fetchone()

    cursor.close()

    if not order:
        return """
            <h2>❌ Order not found</h2>
            <a href="/my_orders">Back to My Orders</a>
        """

    return render_template(
        "receipt.html",
        order=order
    )

@app.route("/cancel_order/<int:order_id>", methods=["POST"])
def cancel_order(order_id):

    if "email" not in session:
        return redirect("/login")

    cursor = db.cursor()

    cursor.execute(
        """
        UPDATE orders
        SET order_status = 'Cancelled'
        WHERE id = %s
        AND student_email = %s
        AND order_status = 'Pending'
        """,
        (order_id, session["email"])
    )

    db.commit()
    cursor.close()

    return redirect("/my_orders")

@app.route("/sales_report")
def sales_report():

    if "email" not in session:
        return redirect("/login")

    if session["role"].lower() != "admin":
        return """
            <h2>❌ Access Denied</h2>
            <p>Only administrators can access the Sales Report.</p>
            <a href="/dashboard">Go to Dashboard</a>
        """

    cursor = db.cursor()

    # Total revenue
    cursor.execute(
        """
        SELECT COALESCE(SUM(total), 0)
        FROM orders
        WHERE order_status != 'Cancelled'
        """
    )
    total_revenue = cursor.fetchone()[0]

    # Total orders
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM orders
        WHERE order_status != 'Cancelled'
        """
    )
    total_orders = cursor.fetchone()[0]

    # Today's revenue
    cursor.execute(
        """
        SELECT COALESCE(SUM(total), 0)
        FROM orders
        WHERE DATE(order_date) = CURDATE()
        AND order_status != 'Cancelled'
        """
    )
    todays_revenue = cursor.fetchone()[0]

    # Today's orders
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM orders
        WHERE DATE(order_date) = CURDATE()
        AND order_status != 'Cancelled'
        """
    )
    todays_orders = cursor.fetchone()[0]

    cursor.close()

    return render_template(
        "sales_report.html",
        total_revenue=total_revenue,
        total_orders=total_orders,
        todays_revenue=todays_revenue,
        todays_orders=todays_orders
    )


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

