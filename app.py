# server/server.py

from flask import Flask, render_template, request, redirect, url_for, flash, make_response, jsonify, session, send_from_directory
from config import app, db, CORS, api
from models import Buyer, Product, Payment, Review,Command
from flask_restful import Resource, reqparse
from werkzeug.utils import secure_filename
import os
import stripe
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from validators import validate_file, validate_business_description
from datetime import datetime
from portalsdk import APIContext, APIMethodType, APIRequest
from time import sleep

# from flask_cors import CORS

#Sending an email using Flask-Mail

from sqlalchemy import func
import random
from helpers import save_image

# Stripe API Key (test key for now, use environment variables for security in production)
stripe.api_key = "sk_test_51Q9ME4HHE78HQruKFYrOTNBUzv3RrHpmkKIJidWHxOKi8ykG3ah25uToNKXknazoZJ6yvefBx1Vk8launjQjYr3000UmxV0o7A"


# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login_user_route'  # specify the login view

@login_manager.user_loader
def load_user(buyer_id):
    
    return Buyer.query.get(int(buyer_id))

@login_manager.unauthorized_handler
def handle_unauthorized():
    # This handler will redirect to appropriate login route based on the session
    if 'buyer_id' in session:
        return redirect(url_for('login_user_route'))



@app.route('/images/<filename>')
def images(filename):
    return send_from_directory('public/images', filename)


# M-Pesa Payment Integration for Congo (DRC)
def initiate_mpesa_payment(buyer_id, amount, phone_number, service_provider_code):
    try:
        # Prepare the API context for the M-Pesa payment
        api_context = APIContext()
        api_context.api_key = "3MC43mJzfxlPl3EAGFDmFL0zcg5xSKWq"  # Sandbox API Key
        api_context.ssl = True
        api_context.method_type = APIMethodType.POST
        api_context.address = "openapi.m-pesa.com"
        api_context.port = 443
        api_context.path = "/sandbox/ipg/v2/vodacomDRC/c2bPayment/singleStage/"  # Market: vodacomDRC

        # Add headers
        api_context.add_header("Origin", "*")

        # Add parameters
        api_context.add_parameter("input_Amount", str(amount))
        api_context.add_parameter("input_CustomerMSISDN", phone_number)
        api_context.add_parameter("input_Country", "DRC")
        api_context.add_parameter("input_Currency", "USD")  # Currency: USD for Congo
        api_context.add_parameter("input_ServiceProviderCode", service_provider_code)
        api_context.add_parameter("input_ThirdPartyConversationID", "unique-conversation-id")
        api_context.add_parameter("input_TransactionReference", "T1234C")
        api_context.add_parameter("input_PurchasedItemsDesc", "Food order")

        # Make the API request
        api_request = APIRequest(api_context)
        result = api_request.execute()

        # Handle response
        if result.status_code == 200:
            return result.body  # Response body from M-Pesa
        else:
            return {"error": "Failed to process M-Pesa payment"}, 500

    except Exception as e:
        return {"error": str(e)}, 500

# Home route
class Home(Resource):
    def get(self):
        if 'buyer_id' in session:
            return jsonify({
                "message": "Welcome to the Home Page",
                "status": "logged_in",
                "buyer_id": session['buyer_id']
            })
        else:
            return jsonify({
                "message": "Welcome to the Home Page",
                "status": "logged_out"
            })

api.add_resource(Home, '/')

#/api/test
@app.route("/api/test", methods=['GET'])
def return_home():
    return jsonify({
        'message':"Hello world"
    })
# User Registration
@app.route('/userregister', methods=['POST'])
def register_user():
    data = request.get_json()
    phonenumber = data.get('phonenumber')
    password = data.get('password')
    address = data.get('address')

    # Validate compulsory fields
    if not all([phonenumber, address, password]):
        return jsonify({'error': 'Please fill all the required fields.'}), 400

    # Check for unique phone number
    if Buyer.query.filter_by(phonenumber=phonenumber).first():
        return jsonify({'error': 'Phone number already in use'}), 409

    new_user = Buyer(phonenumber=phonenumber, address=address)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


# User Login
@app.route('/userlogin', methods=['POST'])
def login_user_route():
    data = request.get_json()
    phonenumber = data.get('phonenumber')
    password = data.get('password')

    user = Buyer.query.filter_by(phonenumber=phonenumber).first()
    if user and user.check_password(password):
        session['buyer_id'] = user.id
        return jsonify({'message': 'Logged in successfully', 'buyer_id': user.id, 'phonenumber': user.phonenumber}), 200
    return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/get_user_name', methods=['GET'])
def get_user_name():
    # Check if user is logged in
    if 'buyer_id' in session:
        buyer_id = session['buyer_id']
        # Fetch the user from the database
        user = Buyer.query.get(buyer_id)
        if user:
            # Return the user's full name
            return jsonify({'user_name': user.phonenumber}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    else:
        return jsonify({'error': 'User not logged in'}), 401



# User Logout
@app.route('/logout', methods=['GET'])
def logout_user_route():
    if 'buyer_id' in session:
        session.pop('buyer_id')
    
    return jsonify({'message': 'You have been logged out'}), 200

# Route to get all products
@app.route('/products', methods=['GET'])
def get_products():
    try:
        products = Product.query.all()
        return jsonify([product.as_dict() for product in products]), 200
    except Exception as e:
        return jsonify({"error":str(e)}), 500
    

# GET a single product by slug
@app.route('/products/<slug>', methods=['GET'])
def get_product(slug):
    product = Product.query.filter_by(slug=slug).first()
    if product:
        return jsonify({
            "product_title": product.product_title,
            "product_category": product.product_category,
            "product_summary": product.product_summary,
            "pricing": product.pricing,
            "quantity": product.quantity,
            "image": product.image,
            "slug": product.slug
        }), 200
    else:
        return jsonify({"error": "Meal not found"}), 404
    
# Route to save a new product to the database
@app.route('/products', methods=['POST'])
def save_product():
    try:
        #Validate the form data
        product_title = request.form.get('product_title')
        product_category = request.form.get('product_category')
        product_summary = request.form.get('product_summary')
        pricing = request.form.get('pricing')
        quantity = request.form.get('quantity')
        image = request.files.get('image')

        if not all([product_title, product_category, product_summary, pricing, quantity, image]):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Customize filename based on product_title



        
        #save the image and get the filename

        file_name = save_image(image, product_title)

        #create the product object
        product = Product(
            product_title = product_title,
            product_category = product_category,
            product_summary = product_summary,
            pricing = pricing,
            quantity = quantity,
            image = file_name,
            slug=product_title.lower().replace(' ', '-')
        )

        #insert the product into the database
         # Insert the meal into the database
        db.session.add(product)
        db.session.commit()

        return jsonify({"message": "Product saved successfully!"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Get all unique product categories
@app.route('/categories', methods=['GET'])
def get_all_categories():
    try:
        categories = db.session.query(Product.product_category).distinct().all()
        categories_list = [category[0] for category in categories]  # Extracting category names from query result
        return jsonify(categories_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get products by category
@app.route('/categories/<category_name>', methods=['GET'])
def get_category(category_name):
    try:
        products = Product.query.filter_by(product_category=category_name).all()
        if products:
            return jsonify([product.as_dict() for product in products]), 200
        else:
            return jsonify({"error": "Category not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/allproducts', methods=['GET'])
def get_allproducts():
    search_term = request.args.get('query')
    category = request.args.get('category')
    
    query = Product.query

    # Search by title (assuming 'title' is the correct attribute in the Product model)
    if search_term:
        query = query.filter(Product.product_title.contains(search_term))

    # Filter by category
    if category:
        query = query.filter(Product.product_category == category)

    # Fetch the filtered products
    products = query.all()

    # Convert product objects to dicts for JSON response
    return jsonify([product.to_dict() for product in products]), 200

@app.route('/products/multiple', methods=['POST'])
def get_multiple_products():
    try:
        data = request.get_json()  # Expect a JSON body with the list of product IDs
        product_ids = data.get('product_ids', [])
        
        # Fetch the products by their IDs
        products = Product.query.filter(Product.id.in_(product_ids)).all()

        # Return the product details as a JSON response
        return jsonify([product.as_dict() for product in products]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/orders', methods=['POST'])
def create_order():
    try:
        data = request.get_json()

        buyer_id = data.get('buyer_id')
        product_ids = data.get('products', [])  # Now it's just a flat list of product IDs
        payment_mode = data.get('paymentMode')  # "stripe", "mpesa", or "cash-on-delivery"
        price = data.get('price')
        phone_number = data.get('phone_number')  # Only required for M-Pesa payment

        if not product_ids or not buyer_id:
            return jsonify({'error': 'Invalid order data. Missing products or buyer info.'}), 400

        # Create a new order associated with the buyer
        new_order = Command(buyer_id=buyer_id, created_at=datetime.now())
        db.session.add(new_order)
        db.session.commit()

        # Create Command entries for each product ordered
        for product_id in product_ids:
            order_item = Command(buyer_id=buyer_id, product_id=product_id, created_at=datetime.now())
            db.session.add(order_item)

        db.session.commit()

        # Payment handling based on the payment mode
        if payment_mode == 'stripe':
            return handle_stripe_payment(price, new_order.id)
        elif payment_mode == 'mpesa':
            return handle_mpesa_payment(buyer_id, price, phone_number, "service-provider-code", new_order.id)
        elif payment_mode == 'cash-on-delivery':
            return handle_cash_on_delivery(new_order.id)

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# Handle Stripe Payment
def handle_stripe_payment(price, order_id):
    try:
        payment_data = stripe.PaymentIntent.create(
            amount=int(price * 100),  # Convert to cents
            currency='usd',
            automatic_payment_methods={'enabled': True}
        )
        payment_intent = payment_data['id']
        client_secret = payment_data['client_secret']

        # Create the payment record in the database
        new_payment = Payment(
            payment_status=False,
            payment_option='stripe',
            payment_intent=payment_intent,
            command_id=order_id,
        )
        db.session.add(new_payment)
        db.session.commit()

        return jsonify({
            "message": "Stripe order created successfully",
            "client_secret": client_secret,
            "payment_intent": payment_intent
        }), 201

    except Exception as e:
        return jsonify({"error": "Failed to process Stripe payment", "details": str(e)}), 500


# Handle M-Pesa Payment
def handle_mpesa_payment(buyer_id, price, phone_number, service_provider_code, order_id):
    try:
        mpesa_response = initiate_mpesa_payment(buyer_id, price, phone_number, service_provider_code)
        
        # If there's an error in the response
        if isinstance(mpesa_response, dict) and "error" in mpesa_response:
            return jsonify({"error": mpesa_response.get("error")}), 500

        # Assuming the M-Pesa response has a transaction ID
        transaction_id = mpesa_response.get("output_TransactionID")  # Change this according to your M-Pesa response

        if not transaction_id:
            return jsonify({"error": "No transaction ID received from M-Pesa"}), 500

        # Create the payment record in the database
        new_payment = Payment(
            payment_status=False,
            payment_option='mpesa',
            payment_intent=transaction_id,  # You could rename this to transaction_id in the database too
            command_id=order_id,
        )
        db.session.add(new_payment)
        db.session.commit()

        return jsonify({
            "message": "M-Pesa order created successfully",
            "transaction_id": transaction_id
        }), 201

    except Exception as e:
        return jsonify({"error": "Failed to process M-Pesa payment", "details": str(e)}), 500


# Handle Cash on Delivery
def handle_cash_on_delivery(order_id):
    try:
        # Create the payment record in the database
        new_payment = Payment(
            payment_status=False,
            payment_option='cash-on-delivery',
            payment_intent=None,  # No payment intent for COD
            command_id=order_id,
        )
        db.session.add(new_payment)
        db.session.commit()

        return jsonify({
            "message": "Cash on delivery order created successfully"
        }), 201

    except Exception as e:
        return jsonify({"error": "Failed to create COD order", "details": str(e)}), 500



    
# Get all orders for a user
@app.route('/orders/user/<int:buyer_id>', methods=['GET'])
def get_user_orders(buyer_id):
    try:
        orders = Command.query.filter_by(buyer_id=buyer_id).all()
        return jsonify([order.to_dict() for order in orders]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get a single order by ID
@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Command.query.get(order_id)
    if order:
        return jsonify(order.to_dict()), 200
    else:
        return jsonify({"error": "Order not found"}), 404
    
@app.route('/orders/<int:order_id>/payment-status', methods=['PATCH'])
def update_order_payment_status(order_id):
    try:
        data = request.get_json()
        payment_status = data.get('paymentStatus')

        payment = Payment.query.filter_by(command_id=order_id).first()
        if not payment:
            return jsonify({"error": "Payment not found"}), 404

        payment.payment_status = payment_status
        db.session.commit()

        return jsonify({"message": "Payment status updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    

@app.route('/success')
def payment_success():
    return render_template('success.html', message="Payment was successful!")

@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        # Invalid payload
        return jsonify({"error": str(e)}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify({"error": str(e)}), 400

    # Handle successful payment_intent.succeeded event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        # Update payment status in database
        payment = Payment.query.filter_by(payment_intent=payment_intent['id']).first()
        if payment:
            payment.payment_status = True
            db.session.commit()
        return jsonify({"status": "success"}), 200

    return jsonify({"status": "unhandled event"}), 200




     

if __name__ == '__main__':
    app.run(port=5555, debug=True)