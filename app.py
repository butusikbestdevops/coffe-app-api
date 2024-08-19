import os
import uuid
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from prometheus_flask_exporter import PrometheusMetrics
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.dialects.postgresql import UUID

app = Flask(__name__)

DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_HOST = os.environ['DB_HOST']
DB_NAME = os.environ['DB_NAME']

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
metrics = PrometheusMetrics(app)

class Transaction(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    coffee_type = db.Column(db.String(50))

    def __init__(self, amount, coffee_type):
        self.amount = amount
        self.coffee_type = coffee_type

@app.route('/api/coffee', methods=['POST'])
def buy_coffee():
    try:
        data = request.get_json()
        amount = data['amount']

        if amount <= 0:
            return jsonify({'message': 'The amount cannot be zero or negative, please enter the correct amount'}), 400

        if amount > 10:
            return jsonify({'message': 'Do you really want such expensive coffee?'}), 200

        if amount < 2.00:
            coffee_type = 'Espresso'
        elif 2.00 <= amount < 3.00:
            coffee_type = 'Latte'
        else:
            coffee_type = 'Cappuccino'

        transaction = Transaction(amount=amount, coffee_type=coffee_type)
        db.session.add(transaction)
        db.session.commit()

        return jsonify({'coffee_type': coffee_type})
    
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': 'A transaction with the same ID already exists'}), 409
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
