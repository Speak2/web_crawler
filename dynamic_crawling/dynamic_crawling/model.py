from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.dialects.postgresql import ARRAY
from .config import db_url

engine = create_engine(db_url)
Base = declarative_base()

class Property(Base):
    __tablename__ = 'properties'

    id = Column(Integer, primary_key=True)
    h3_tag = Column(String)
    country_name = Column(String)
    city_name = Column(String)
    title = Column(String)
    star = Column(Integer)
    rating = Column(Float)
    location = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    room_type = Column(ARRAY(String)) 
    price = Column(Float)
    image_paths = Column(String)
