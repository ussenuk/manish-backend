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
            product_title='Hamburger',
            product_category='Fast-Food',
            product_summary='Un hamburger, ou par aphérèse burger, est un sandwich d\'origine allemande, composé de deux pains de forme ronde1 (bun) généralement garnis d\'une galette de steak haché (généralement du bœuf) et de crudités, salade, tomate, oignon, cornichon (pickles) ainsi que de sauce.',
            pricing=5,
            quantity=10,
            image=save_image_for_product('Hamburger'),
            slug=generate_slug('Hamburger')
        )
        product2 = Product(
            product_title='Shawarma',
            product_category='Local-Food',
            product_summary='Nous vous offrons du Shawarma que vous pouvez manger avec nos frites. Tout à très bon prix',
            pricing=2,
            quantity=5,
            image=save_image_for_product('Shawarma'),
            slug=generate_slug('Shawarma')
        )
        product3 = Product(
            product_title='Frites',
            product_category='Local-Food',
            product_summary='Des Frites simples disponibles chez nous à très bas prix',
            pricing=1,
            quantity=20,
            image=save_image_for_product('Frites'),
            slug=generate_slug('Frites')
        )
        product4 = Product(
            product_title='Pizza Boeuf',
            product_category='Fast-Food',
            product_summary='Les carnivores sont fans de cette pizza qui mise sur les saveurs bien marquées du bœuf français et de la merguez, poivron, oignon rouge et sauce salsa pour régaler les amateurs de sensations fortes. Il y a tout le tempérament du Mexique dans cette pizza.',
            pricing=12,
            quantity=20,
            image=save_image_for_product('Boeuf'),
            slug=generate_slug('Boeuf')
        )
        product5 = Product(
            product_title='Pizza au poulet tikka',
            product_category='Fast-Food',
            product_summary='La pizza au poulet tikka est une pizza délicieuse et savoureuse qui allie les saveurs de la cuisine indienne au goût classique de la pizza. La garniture au poulet tikka est faite de poulet grillé ou rôti mariné dans un mélange d\'épices, notamment du garam masala, du gingembre, de l\'ail et du yaourt. Le poulet est ensuite cuit jusqu\'à ce qu\'il soit tendre et juteux. La pizza est garnie de poulet tikka, d\'une sauce tomate, de fromage mozzarella et d\'autres garnitures de votre choix, comme de l\'oignon rouge, de la tomate ou du poivron. ',
            pricing=12,
            quantity=20,
            image=save_image_for_product('Poulet'),
            slug=generate_slug('Poulet')
        )
        product6 = Product(
            product_title='Pizza hawaïenne',
            product_category='Fast-Food',
            product_summary='La pizza hawaïenne est une variété de pizza qui se compose généralement de fromage et d\'une base de tomate avec des morceaux de jambon et d\'ananas',
            pricing=15,
            quantity=20,
            image=save_image_for_product('Hawain'),
            slug=generate_slug('Hawain')
        )
        product7 = Product(
            product_title='Pepperoni',
            product_category='Fast-Food',
            product_summary='La pizza Pepperoni est garnie d\'une sauce tomate tomates d\'Italie, de mozzarella française et de fromage cheddar puis :- des tranches de Pepperoni il est important de savoir que le Pepperoni est une variété américaine de salami, fabriqué à partir de porc et de bœuf séchés mélangés et assaisonnés de paprika ou d\'un autre piment.',
            pricing=15,
            quantity=20,
            image=save_image_for_product('Pepperoni'),
            slug=generate_slug('Pepperoni')
        )
        product8 = Product(
            product_title='Salad',
            product_category='Local-Food',
            product_summary='Une salade gratuite offerte à chaque paiement de frites faite chez nous',
            pricing=1,
            quantity=20,
            image=save_image_for_product('Salad'),
            slug=generate_slug('Salad')
        )
        product9 = Product(
            product_title='Poulet griller',
            product_category='Local-Food',
            product_summary='Nous vous offrons des morceaux de poulet grillé que vous pouvez manger avec nos frites. Tout à très bon prix',
            pricing=5,
            quantity=20,
            image=save_image_for_product('Pouletgriller'),
            slug=generate_slug('Pouletgriller')
        )
        product10 = Product(
            product_title='Jus',
            product_category='Boisson',
            product_summary='Jus locale',
            pricing=1,
            quantity=20,
            image=save_image_for_product('Jus'),
            slug=generate_slug('Jus')
        )

        # Add products to the session and commit to the database
        db.session.add_all([product1, product2, product3, product4, product5, product6, product7, product8, product9, product10 ])
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
