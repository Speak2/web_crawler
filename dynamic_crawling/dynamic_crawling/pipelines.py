from sqlalchemy.orm import sessionmaker
from .items import PropertyItem
from .model import Property, Base, engine
from sqlalchemy_utils import database_exists,create_database

class ScrapyProjectPipeline:
    def __init__(self):
        self.Session = sessionmaker(bind=engine)

    def open_spider(self, spider):
        # Create the database and tables if they don't exist
        if not database_exists(engine.url):
            create_database(engine.url)
        Base.metadata.create_all(engine)

    def process_item(self, item, spider):
        session = self.Session()
        property_item = Property(
            title=item['title'],
            rating=item['rating'],
            location=item['location'],
            latitude=item['latitude'],
            longitude=item['longitude'],
            room_type=item['room_type'],
            price=item['price'],
            image_paths=item['image_paths']
        )
        session.add(property_item)
        session.commit()
        session.close()
        return item