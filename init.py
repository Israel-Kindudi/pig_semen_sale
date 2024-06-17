# Initialize the database and add initial data (run this once)
from app import app, db
from models import PigType

with app.app_context():
    db.create_all()
    if not PigType.query.all():
        pig_types = [
            PigType(name="Piétrain", description="A popular pig breed", price=38.0),
            PigType(name="Valens", description="Known for large litters", price=54.0),
            PigType(name="Duroc", description="Great growth rate", price=54.0),
            PigType(name="Landracs", description="High-quality meat", price=82.0),
            PigType(name="Large White", description="Robust and healthy", price=82.0),
            PigType(name="Thor", description="Muscular build", price=38.0)
        ]
        db.session.bulk_save_objects(pig_types)
        db.session.commit()
