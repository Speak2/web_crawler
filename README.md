# Trip.com Hotel Scraper

This project is a Scrapy-based web scraper designed to extract hotel information from Trip.com. It collects data such as hotel names, locations, prices, ratings, and room types, and stores this information in a PostgreSQL database.

## Table of Contents
1. [Features](#features)
2. [Technologies Used](#technologies-used)
3. [Project Structure](#project-structure) 
5. [Setup](#setup)
6. [Usage](#usage)
7. [Data Storage](#data-storage)
8. [Customization](#customization)
9. [Note](#note)
10. [Contributing](#contributing)
11. [License](#license)



## Features

- Scrapes hotel data from Trip.com
- Extracts information including hotel name, location, price, star rating, user rating, room types, and more
- Saves hotel images locally
- Stores scraped data in a PostgreSQL database
- Supports random selection of cities or hotel types for diverse data collection
- scraped all the h3 headers of the main page
- scraped 3 different pages to handle data collection
- created a list of all the cities and 3 different types of hotels and choose one randomly from them. This handles all possible scenarios.It ensures random hading selection

## Technologies Used

- Python 3.x
- Scrapy
- SQLAlchemy
- PostgreSQL
- psycopg2
- sqlalchemy-utils

 

## Project Structure

The project structure is as follows:

```
web_crawler/
├──dynamic_crawling/
│   ├── dynamic_crawling/
│   │   ├── __pycache__/                  
│   │   ├── spiders/                   
│   │   │   ├── __pycache__/            
│   │   │   ├── __init__.py             
│   │   │   ├── tripcomp.py   
│   │   ├── __init__.py       
│   │   ├── items.py                  
│   │   ├── middlewares.py            
│   │   ├── model.py                  
│   │   ├── pipelines.py              
│   │   ├── settings.py  
│   │             
│   ├── scrapy.cfg                    
│                     
├── .gitignore                       
├── README.md                        
└── requirements.txt  
```

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Speak2/web_crawler
   cd web_crawler/
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```bash
     source venv/bin/activate
     ```


4. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

5. Connection with PostgreSQL database:
   - Create a new `config.py` file using the `config-sample.txt` inside- `web_crawler/dynamic_crawling/dynamic_crawling`
   - use appropriate username,password and port address to connect with the database.example-
     ```python
     db_url = "postgresql://username:password@localhost:port_number/database_name"
     ```

6. Set up the PostgreSQL database:

   6.1. Automatic Setup
   
   The project is configured to automatically create the database and tables if they don't exist. This is handled in the `open_spider` method of the `ScrapyProjectPipeline` class in `pipelines.py`.

   6.2. Manual Setup
   
   If you prefer to set up the database and table manually, follow these steps:

   a. Connect to PostgreSQL:
      ```sql
      psql -U postgres
      ```

   b. Create the database:
      ```sql
      CREATE DATABASE scrapy_db;
      ```

   c. Connect to the new database:
      ```sql
      \c scrapy_db
      ```

   d. Create the properties table:
      ```sql
      CREATE TABLE properties (
          id SERIAL PRIMARY KEY,
          h3_tag VARCHAR,
          country_name VARCHAR,
          city_name VARCHAR,
          title VARCHAR,
          star INTEGER,
          rating FLOAT,
          location VARCHAR,
          latitude FLOAT,
          longitude FLOAT,
          room_type VARCHAR[],
          price FLOAT,
          image_paths VARCHAR
      );
      ```

## Usage

To run the spider, use the following command:

```bash
cd WEB_CRAWLER/dynamic_crawling
scrapy crawl tripcom
```

This will start the scraping process. The spider will randomly select cities or hotel types to scrape, ensuring a diverse dataset.

## Data Storage

- Scraped data is stored in the PostgreSQL database in the `properties` table.
- Hotel images are saved in the `hotel_images` directory.
- The scraped data is also stored in `output.json` file in the project directory for convinience
- ths is the sample extracted data-
```json
{
   "h3_tag": "Popular Hotels in United Kingdom",
   "country_name": "United Kingdom",
   "city_name": "Liverpool",
   "title": "Heeton Concept Hotel City Centre Liverpool",
   "star": 3,
   "rating": 4.1,
   "location": "James St",
   "latitude": 40.7505,
   "longitude": -73.9864,
   "room_type": ["Accessible King Room","King Room","Twin Room"],
   "price": 179.99,
   "image_paths": "hotel_images/Heeton Concept Hotel City Centre Liverpool.jpg"
}
```

## Customization

- To modify the scraping behavior, edit the `TripcomSpider` class in `spiders/tripcom.py`.
- To change the structure of the scraped data, update the `PropertyItem` class in `items.py` and the `Property` model in `model.py`.
- Adjust the database settings in `model.py` and `pipelines.py` if needed.

## Note

This scraper is designed for educational purposes. Make sure to comply with Trip.com's terms of service and robots.txt file when using this scraper.

## Contributing

Contributions to improve the scraper are welcome. Please feel free to submit a Pull Request.

## License

[Specify your license here]
