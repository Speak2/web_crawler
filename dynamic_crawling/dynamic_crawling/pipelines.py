from sqlalchemy.orm import sessionmaker
from .model import Property, Base, engine
from sqlalchemy_utils import database_exists, create_database
import os
import requests
import re
from urllib.parse import urlparse


class ScrapyProjectPipeline:
    def __init__(self):
        self.Session = sessionmaker(bind=engine)

    def open_spider(self, spider):
        # Create the database and tables if they don't exist
        if not database_exists(engine.url):
            create_database(engine.url)
        Base.metadata.create_all(engine)

    def sanitize_filename(self, filename):
        # Remove special characters and replace spaces with underscores
        sanitized = re.sub(r'[^\w\s-]', '', filename.lower())
        sanitized = re.sub(r'[-\s]+', '_', sanitized).strip('-_')
        return sanitized

    def save_image(self, item):
        hotel_name = item['title']
        image_url = item['image_url']

        # Create a folder to save images if it doesn't exist
        try:
            if not os.path.exists('hotel_images'):
                os.makedirs('hotel_images')
        except OSError as e:
            self.logger.error(
                f"Failed to create directory 'hotel_images': {e}")
            return None

        # Sanitize the hotel name for use as a filename
        safe_hotel_name = self.sanitize_filename(hotel_name)

        # Get the file extension from the URL
        parsed_url = urlparse(image_url)
        file_extension = os.path.splitext(parsed_url.path)[1].lower()
        if not file_extension:
            file_extension = '.jpg'  # Default to .jpg if no extension is found

        # Create the full image path
        image_filename = f'{safe_hotel_name}{file_extension}'
        image_path = os.path.join('hotel_images', image_filename)

        try:
            response = requests.get(image_url)
            if response.status_code == 200:
                with open(image_path, 'wb') as file:
                    file.write(response.content)
                return image_path  # Return just the filename, not the full path
        except Exception as e:
            self.logger.error(f"Failed to save image for {hotel_name}: {e}")

        return None

    def process_item(self, item, spider):
        session = self.Session()
        image_path = self.save_image(item)
        print(image_path)
        property_item = Property(
            h3_tag=item['h3_tag'],
            country_name=item['country_name'],
            city_name=item['city_name'],
            title=item['title'],
            star=item['star'],
            rating=item['rating'],
            location=item['location'],
            latitude=item['latitude'],
            longitude=item['longitude'],
            room_type=item['room_type'],
            price=item['price'],
            image_paths=image_path
        )
        session.add(property_item)
        session.commit()
        session.close()
        return item
