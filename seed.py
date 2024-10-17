from app import app, db
from datetime import datetime
from models import Buyer, Command, Review, Payment, Product
import re

# Helper function to create a slug from a product title
def generate_slug(title):
    return re.sub(r'[^a-zA-Z0-9]+', '-', title).strip('-').lower()

# Helper function to simulate saving an image
def save_image_for_product(product_title):
    # Assuming we're storing images in a 'static/images' directory
    image_name = f"{generate_slug(product_title)}.jpg"
    return image_name  # This is a placeholder; you would save/upload the actual image in a real scenario.

# Create an application context
with app.app_context():
    try:
        # Clear existing data from the tables
        Buyer.query.delete()
        Command.query.delete()
        Review.query.delete()
        Payment.query.delete()
        Product.query.delete()

        # Create sample buyers
        buyer1 = Buyer(phonenumber='1234567890', address='New York')
        buyer2 = Buyer(phonenumber='0987654321', address='Los Angeles')
        buyer3 = Buyer(phonenumber='1122334455', address='San Francisco')

        # Set passwords for buyers
        buyer1.set_password('password123')
        buyer2.set_password('password456')
        buyer3.set_password('password789')

        # Add buyers to the session and commit to the database
        db.session.add_all([buyer1, buyer2, buyer3])
        db.session.commit()

        # Create sample products with summaries, images, and slugs
        product1 = Product(
            product_title='Camera',
            product_category='Electronics',
            product_summary='A high-quality digital camera',
            pricing=500,
            quantity=10,
            image=save_image_for_product('Camera'),
            slug=generate_slug('Camera')
        )
        product2 = Product(
            product_title='Laptop',
            product_category='Electronics',
            product_summary='A powerful laptop for work and gaming',
            pricing=1000,
            quantity=5,
            image=save_image_for_product('Laptop'),
            slug=generate_slug('Laptop')
        )
        product3 = Product(
            product_title='Smartphone',
            product_category='Electronics',
            product_summary='A smartphone with excellent battery life',
            pricing=800,
            quantity=20,
            image=save_image_for_product('Smartphone'),
            slug=generate_slug('Smartphone')
        )

        # Add products to the session and commit to the database
        db.session.add_all([product1, product2, product3])
        db.session.commit()

        # Create sample commands linked to buyers and products
        command1 = Command(buyer_id=buyer1.id, product_id=product1.id, created_at=datetime.strptime('2024-04-20 10:00:00', '%Y-%m-%d %H:%M:%S'))
        command2 = Command(buyer_id=buyer2.id, product_id=product2.id, created_at=datetime.strptime('2024-04-21 11:00:00', '%Y-%m-%d %H:%M:%S'))
        command3 = Command(buyer_id=buyer3.id, product_id=product3.id, created_at=datetime.strptime('2024-04-22 12:00:00', '%Y-%m-%d %H:%M:%S'))

        # Add commands to the session and commit to the database
        db.session.add_all([command1, command2, command3])
        db.session.commit()

        # Create sample reviews for the products
        review1 = Review(stars_given=4, comments="Great camera!", product_id=product1.id, buyer_id=buyer1.id, average_rating=4)
        review2 = Review(stars_given=5, comments="Excellent laptop!", product_id=product2.id, buyer_id=buyer2.id, average_rating=5)
        review3 = Review(stars_given=3, comments="Good smartphone.", product_id=product3.id, buyer_id=buyer3.id, average_rating=3)

        # Add reviews to the session and commit to the database
        db.session.add_all([review1, review2, review3])
        db.session.commit()

        # Create sample payments associated with the commands
        payment1 = Payment(payment_status='Paid', payment_option='Credit Card', payment_intent='pi_1GqIC8Lxqz0fQJ04L8XtSAhS', command_id=command1.id, buyer_id=buyer1.id)
        payment2 = Payment(payment_status='Paid', payment_option='PayPal', payment_intent='pi_1GqIC9Lxqz0fQJ04M8XtSBvT', command_id=command2.id, buyer_id=buyer2.id)
        payment3 = Payment(payment_status='Paid', payment_option='Bank Transfer', payment_intent='pi_1GqICAqz0fQJ04N9XtSCrwB', command_id=command3.id, buyer_id=buyer3.id)

        # Add payments to the session and commit to the database
        db.session.add_all([payment1, payment2, payment3])
        db.session.commit()

        print("Database seeded successfully.")

    except Exception as e:
        db.session.rollback()
        print(f"Error during seeding: {str(e)}")
