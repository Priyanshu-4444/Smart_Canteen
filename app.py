
from flask import Flask, render_template, request, session, redirect
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

db = pymysql.connect(
    host=os.environ.get("DB_HOST"),
    port=int(os.environ.get("DB_PORT", 12855)),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD"),
    database=os.environ.get("DB_NAME", "defaultdb"),
    connect_timeout=10,
    ssl={"ssl": {}}
)

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

        <title>Smart Canteen - Home</title>

        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: Arial, sans-serif;
            }

            body {
                min-height: 100vh;
                background: linear-gradient(135deg, #fff3e0, #ffcc80);
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }

            .container {
                width: 100%;
                max-width: 500px;
                background: white;
                padding: 45px 35px;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
                text-align: center;
            }

            .logo {
                font-size: 70px;
                margin-bottom: 10px;
            }

            h1 {
                color: #e65100;
                font-size: 30px;
                margin-bottom: 12px;
            }

            .subtitle {
                color: #555;
                font-size: 16px;
                margin-bottom: 25px;
                line-height: 1.5;
            }

            .status {
                display: inline-block;
                background: #e8f5e9;
                color: #2e7d32;
                padding: 8px 15px;
                border-radius: 20px;
                font-size: 14px;
                margin-bottom: 30px;
                font-weight: bold;
            }

            .buttons {
                display: flex;
                flex-direction: column;
                gap: 15px;
            }

            .btn {
                display: block;
                width: 100%;
                padding: 14px;
                border-radius: 10px;
                text-decoration: none;
                font-size: 17px;
                font-weight: bold;
                transition: 0.3s;
            }

            .register {
                background: #ff6f00;
                color: white;
            }

            .register:hover {
                background: #e65100;
                transform: translateY(-2px);
            }

            .login {
                background: white;
                color: #e65100;
                border: 2px solid #ff6f00;
            }

            .login:hover {
                background: #fff3e0;
                transform: translateY(-2px);
            }

            .features {
                margin-top: 30px;
                padding-top: 25px;
                border-top: 1px solid #eee;
                color: #666;
                font-size: 14px;
                line-height: 1.8;
            }

            .footer {
                margin-top: 25px;
                color: #999;
                font-size: 12px;
            }

            @media (max-width: 480px) {
                .container {
                    padding: 35px 25px;
                }

                h1 {
                    font-size: 26px;
                }

                .logo {
                    font-size: 60px;
                }
            }
        </style>
    </head>

    <body>

        <div class="container">

            <div class="logo">🍔</div>

            <h1>Smart Canteen</h1>

            <p class="subtitle">
                Food Ordering & Management System
            </p>

            <div class="status">
                ✓ Database Connected Successfully!
            </div>

            <div class="buttons">

                <a href="/register" class="btn register">
                    📝 Create Account
                </a>

                <a href="/login" class="btn login">
                    🔐 Login
                </a>

            </div>

            <div class="features">
                🍔 Easy Food Ordering<br>
                🛒 Simple Cart Management<br>
                📋 Track Your Orders<br>
                ⚡ Fast & Convenient
            </div>

            <div class="footer">
                Smart Canteen Management System
            </div>

        </div>

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

            cursor.close()

            return """
                <h2>Email already registered!</h2>

                <a href="/register">Try Again</a>
            """

        cursor.close()

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

        cursor = db.cursor()

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()

        if user and check_password_hash(user[3], password):

            # Save user information in session
            session["user_id"] = user[0]
            session["name"] = user[1]
            session["email"] = user[2]
            session["role"] = user[4]

            # If admin, go to admin dashboard
            if user[4].lower() == "admin":

                return redirect("/admin")

            # Otherwise student dashboard
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
        availability = request.form["availability"]

        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO menu
            (item_name, price, category, availability)
            VALUES (%s, %s, %s, %s)
            """,
            (
                item_name,
                price,
                category,
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

