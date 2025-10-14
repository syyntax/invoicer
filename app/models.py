from datetime import datetime
from app import db # `db` object initialized in `app/__init__.py`

class CompanySettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default="StormKeep Inc.")
    address_line1 = db.Column(db.String(100))
    address_line2 = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(20))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(50))

    def __repr__(self):
        return f"<CompanySettings {self.name}>"

class Recipient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False, unique=True)
    address_line1 = db.Column(db.String(100))
    address_line2 = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(20))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(50))

    invoices = db.relationship('Invoice', backref='recipient', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Recipient {self.client_name}>"

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('recipient.id'), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_due = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="OUTSTANDING", nullable=False) # "PAID" or "OUTSTANDING"
    total_due = db.Column(db.Float, default=0.00)

    line_items = db.relationship('LineItem', backref='invoice', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Invoice {self.invoice_number}>"

class LineItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False) # calculated as quantity * unit_price

    def __repr__(self):
        return f"<LineItem {self.description}>"