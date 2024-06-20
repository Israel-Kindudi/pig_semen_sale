import random
from models import OrderItem

def generate_unique_order_id():
    while True:
        # Generate a random six-digit number
        order_id = random.randint(100000, 999999)
        # Check if this order_id already exists in the database
        existing_order = OrderItem.query.filter_by(order_id=order_id).first()
        if not existing_order:
            return order_id
