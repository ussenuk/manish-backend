from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_serializer import SerializerMixin
from config import db
from sqlalchemy import UniqueConstraint
from flask_login import UserMixin


class Buyer(db.Model, SerializerMixin, UserMixin):
    __tablename__ = 'buyers'
    id = db.Column(db.Integer, primary_key=True)
    phonenumber = db.Column(db.String(255), unique=True)
    address = db.Column(db.String(255))
    password_hash = db.Column(db.String(128))

    # Exclude sensitive data and prevent recursion
    serialize_rules = ('-password_hash', '-commands.buyer')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_name(self):
        return self.phonenumber

class Command(db.Model, SerializerMixin):
    __tablename__ = 'commands'
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyers.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    created_at = db.Column(db.DateTime)

    product = db.relationship('Product', backref='commands')  # Add relationship with products

    payments = db.relationship('Payment', backref='command', lazy=True)

    # Prevent recursion by excluding backreferences
    serialize_rules = ('-buyer.commands', '-product.commands')

    def to_dict(self):
        return {
            'id': self.id,
            'buyer_id': self.buyer_id,
            'product_id': self.product_id,
            'created_at': self.created_at.isoformat(),
        }

class Review(db.Model, SerializerMixin):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    stars_given = db.Column(db.Integer)
    comments = db.Column(db.String(255))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyers.id'))
    average_rating = db.Column(db.Integer)

    # Exclude relationships that may cause recursion
    serialize_rules = ('-buyer.reviews', '-product.reviews')

class Payment(db.Model, SerializerMixin):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    payment_status = db.Column(db.String(255))
    payment_option = db.Column(db.String(255))
    payment_intent = db.Column(db.String(255))  # Add paymentIntent here
    command_id = db.Column(db.Integer, db.ForeignKey('commands.id'))
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyers.id'))

    # Exclude circular references
    serialize_rules = ('-command.payments', '-buyer.payments')

class Product(db.Model, SerializerMixin):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    product_title = db.Column(db.String(255))
    product_category = db.Column(db.String(255))
    product_summary = db.Column(db.String(255))
    pricing = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    image = db.Column(db.String(255))
    slug = db.Column(db.String(255))

    # Relationships (e.g., reviews and commands)
    reviews = db.relationship('Review', backref='product', lazy=True)

    # Exclude relationships to prevent recursion
    serialize_rules = ('-reviews.product',)

    def as_dict(self):
        return {
            "id": self.id,
            "product_title": self.product_title,
            "product_category": self.product_category,
            "product_summary": self.product_summary,
            "pricing": self.pricing,
            "quantity": self.quantity,
            "image": self.image,
            "slug": self.slug
        }
