# Initialize the database and add initial data (run this once)
from app import app, db
from models import PigType

with app.app_context():
    db.create_all()
    if not PigType.query.all():
        pig_types = [
            PigType(name="Piétrain", description="éfficacité Alimentaire", price=38.0),
            PigType(name="Valens", description="Rentabilité", price=54.0),
            PigType(name="Duroc", description="Croissance", price=54.0),
            PigType(name="Landracs", description="Capacité à sevrer", price=82.0),
            PigType(name="Large White", description="qualité du porcelet", price=82.0),
            PigType(name="Thor", description="Vigueur à la naissance", price=38.0)
        ]
        db.session.bulk_save_objects(pig_types)
        db.session.commit()
