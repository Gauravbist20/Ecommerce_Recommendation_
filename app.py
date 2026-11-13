
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from database import (
    create_database,
    get_products,
    create_user,
    get_user_by_email,
    add_rating
)

from recommender import recommend_products

app = Flask(__name__)
app.secret_key = "smartshop-secret-key-change-later"

create_database()

PRODUCT_IMAGES = {
    1: "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600",
    2: "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600",
    3: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600",
    4: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600",
    5: "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600",
    6: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600",
    7: "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=600",
    8: "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=600",
    9: "https://images.unsplash.com/photo-1592078615290-033ee584e267?w=600",
    10: "https://images.unsplash.com/photo-1499933374294-4584851497cc?w=600"
}


@app.context_processor
def inject_global_data():
    cart = session.get("cart", {})

    return {
        "product_images": PRODUCT_IMAGES,
        "current_user": session.get("user_name"),
        "cart_count": sum(cart.values())
    }


@app.route("/")
def home():
    all_products = get_products()

    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    selected_id = request.args.get("product", type=int)

    categories = sorted(set(p[2] for p in all_products))
    products = all_products

    if search:
        products = [
            p for p in products
            if search.lower() in
            (p[1] + " " + p[2] + " " + p[4]).lower()
        ]

    if category:
        products = [p for p in products if p[2] == category]

    recommendations = []

    if selected_id:
        recommendations = recommend_products(all_products, selected_id)

    return render_template(
        "index.html",
        products=products,
        recommendations=recommendations,
        selected_id=selected_id,
        categories=categories,
        search=search,
        selected_category=category
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or len(password) < 8:
            flash("Enter all details. Password must be at least 8 characters.")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        user_id = create_user(name, email, hashed_password)

        if user_id:
            session["user_id"] = user_id
            session["user_name"] = name
            flash("Account created successfully!")
            return redirect(url_for("home"))

        flash("This email is already registered.")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = get_user_by_email(email)

        if user and check_password_hash(user[3], password):
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            flash("Welcome back!")
            return redirect(url_for("home"))

        flash("Invalid email or password.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("user_name", None)
    flash("You have logged out.")
    return redirect(url_for("home"))


@app.route("/add-to-cart/<int:product_id>")
def add_to_cart(product_id):
    products = get_products()

    if not any(p[0] == product_id for p in products):
        flash("Product not found.")
        return redirect(url_for("home"))

    cart = session.get("cart", {})
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    session["cart"] = cart

    flash("Product added to cart.")
    return redirect(url_for("home"))


@app.route("/cart")
def cart():
    products = get_products()
    cart_items = session.get("cart", {})
    cart_products = []
    total = 0

    for product in products:
        key = str(product[0])

        if key in cart_items:
            quantity = cart_items[key]
            subtotal = product[3] * quantity
            total += subtotal

            cart_products.append({
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal
            })

    return render_template(
        "cart.html",
        cart_products=cart_products,
        total=total
    )


@app.route("/update-cart", methods=["POST"])
def update_cart():
    cart = session.get("cart", {})

    for product_id, quantity in request.form.items():
        try:
            quantity = int(quantity)

            if quantity > 0:
                cart[product_id] = min(quantity, 99)
            else:
                cart.pop(product_id, None)
        except ValueError:
            continue

    session["cart"] = cart
    return redirect(url_for("cart"))


@app.route("/remove-from-cart/<int:product_id>")
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    cart.pop(str(product_id), None)
    session["cart"] = cart
    return redirect(url_for("cart"))


@app.route("/rate", methods=["POST"])
def rate():
    user_id = session.get("user_id")

    if not user_id:
        flash("Please login before rating a product.")
        return redirect(url_for("login"))

    product_id = request.form.get("product_id", type=int)
    rating = request.form.get("rating", type=float)

    valid_product = any(
        p[0] == product_id for p in get_products()
    )

    if product_id and valid_product and rating is not None and 1 <= rating <= 5:
        add_rating(user_id, product_id, rating)
        flash("Your rating has been saved.")
    else:
        flash("Please select a valid rating.")

    return redirect(url_for("home", product=product_id))


if __name__ == "__main__":
    app.run(debug=True)
