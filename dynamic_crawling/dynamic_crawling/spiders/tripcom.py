import scrapy
import json
import re
import random
import os
from datetime import datetime, timedelta
from ..items import PropertyItem


class TripcomSpider(scrapy.Spider):
    name = 'tripcom'
    allowed_domains = ['uk.trip.com', 'tripcdn.com']
    start_urls = ['https://uk.trip.com/hotels/?locale=en-GB&curr=GBP']

    def parse(self, response):
        script = response.xpath(
            '//script[contains(., "window.IBU_HOTEL")]/text()').get()

        if script:
            match = re.search(
                r'window\.IBU_HOTEL\s*=\s*(\{.*?\});', script, re.DOTALL)

            if match:
                json_data = match.group(1)

                try:
                    data = json.loads(json_data)
                    htls_data = data.get('initData', {}).get('htlsData', {})
                    
                    tag1_data = data.get('translate', {}).get('key.hotel.homepage.hotelrecommendation.hotdomestichotels')   #Popular Hotels in %1$s",
                    tag2_data = data.get('translate', {}).get('key.hotel.homepage.hotelrecommendation.hotdomesticcities')
                    tag3_data = data.get('translate', {}).get('key.hotel.homepage.hotelrecommendation.hot5starhotels')
                    tag4_data = data.get('translate', {}).get('key.hotel.homepage.hotelrecommendation.hotcheaphotels')
                    tag5_data = data.get('translate', {}).get('key.hotel.homepage.hotelrecommendation.hotostels')
                    
                    tag1_data = tag1_data.replace("%1$s", "%s")  # Replace %1$s with %s
                    tag2_data = tag2_data.replace("%1$s", "%s")  # Replace %1$s with %s 
                    
                    
                    all_cities = []

                    # Extract data from inboundCities
                    uk='United Kingdom'
                    inbound_cities = htls_data.get('inboundCities', [])
                    for index, city in enumerate(inbound_cities):
                        hotels = city.get('recommendHotels', [])

                        if hotels:  # Check if the list is not empty
                            country_name = hotels[0].get('countryName')
                        else:
                            country_name = None  # Handle the case where `country` is empty

                        city_name = city.get('name')
                        city_id = city.get('id')

                        if index < 3:
                            h3_tag = tag1_data % uk
                        else:
                            h3_tag = tag2_data % uk

                        all_cities.append({
                            'country': country_name,
                            'city_name': city_name,
                            'city_id': city_id,
                            'h3_tag': h3_tag
                        })

                    # Extract data from outboundCities
                    world='Worldwide'
                    outbound_cities = htls_data.get('outboundCities', [])
                    for index, city in enumerate(outbound_cities):
                        country = city.get('recommendHotels', [])

                        if country:  # Check if the list is not empty
                            country_name = country[0].get('countryName')
                        else:
                            country_name = None  # Handle the case where `country` is empty
                        city_name = city.get('name')
                        city_id = city.get('id')

                        # Use the same h3 tag logic for outbound cities
                        if index < 3:
                            h3_tag = tag1_data % world
                        else:
                            h3_tag = tag2_data % world

                        all_cities.append({
                            'country': country_name,
                            'city_name': city_name,
                            'city_id': city_id,
                            'h3_tag': h3_tag
                        })

                    all_cities.append({
                        'city_name': "fiveStarHotels",
                        'city_id': "-1",
                        'h3_tag': tag3_data
                    })

                    all_cities.append({
                        'city_name': "cheapHotels",
                        'city_id': "-2",
                        'h3_tag': tag4_data
                    })

                    all_cities.append({
                        'city_name': "hostelHotels",
                        'city_id': "-3",
                        'h3_tag': tag5_data
                    })

                    # Randomly select one city or the 3 types of hotels
                    random_city = random.choice(all_cities)
                    selected_city_id = random_city['city_id']
                    selected_city_name = random_city['city_name']

                    if selected_city_id in ["-1", "-2", "-3"]:
                        hotel_list = htls_data[selected_city_name]

                        for index, city in enumerate(hotel_list):
                            hotel_name = city.get('hotelName')
                            img = city.get('imgUrl')
                            hotel_img_url = f"https://ak-d.tripcdn.com/images{img}" if img else None
                            address = city.get('address')
                            price = city.get('displayPrice', {}).get('price')
                            hotel_star = city.get('star')
                            rating = city.get('rating')
                            room_name = city.get('room', None)
                            latitude = city.get('lat')
                            longitude = city.get('lon')
                            city_name = city.get('cityName')
                            hotel_url = city.get('hotelJumpUrl')
                            country_name = city.get('countryName')

                            item = PropertyItem(
                                h3_tag=random_city['h3_tag'],
                                title=hotel_name,
                                country_name=country_name,
                                city_name=city_name,
                                star=hotel_star,
                                rating=rating,
                                location=address,
                                latitude=latitude,
                                longitude=longitude,
                                room_type=room_name,
                                price=price,
                                image_paths=''  # We'll update this in the save_image method
                            )

                            yield scrapy.Request(
                                url=hotel_url,
                                callback=self.parse_hotel_detail,
                                meta={
                                    'item': item,
                                    'url': hotel_img_url
                                }
                            )

                    else:

                        today = datetime.today()
                        # Format dates as 'YYYY/MM/DD'
                        checkin_date = today.strftime('%Y/%m/%d')
                        checkout_date = (
                            today + timedelta(days=1)).strftime('%Y/%m/%d')

                        # Construct a new URL using the selected city_id
                        new_url = f"https://uk.trip.com/hotels/list?city={selected_city_id}&checkin={checkin_date}&checkout={checkout_date}"

                        # Make a new request to the URL
                        yield scrapy.Request(
                            url=new_url,
                            callback=self.parse_city_data,
                            meta={
                                'h3_tag': random_city['h3_tag'],
                                'city_name': random_city['city_name'],
                                'country_name': random_city['country']
                            }
                        )

                except json.JSONDecodeError:
                    self.logger.error("Failed to parse JSON data")
            else:
                self.logger.error("JSON data not found in the script")
        else:
            self.logger.error("Script containing window.IBU_HOTEL not found")

    def parse_city_data(self, response):
        tag = response.meta['h3_tag']
        city_name = response.meta['city_name']
        country_name = response.meta['country_name']

        script = response.xpath(
            '//script[contains(., "window.IBU_HOTEL")]/text()').get()

        if script:
            match = re.search(
                r'window\.IBU_HOTEL\s*=\s*(\{.*?\});', script, re.DOTALL)
            if match:
                json_data = match.group(1)

                try:
                    data = json.loads(json_data)

                    # Navigate to the firstPageList -> hotelList section in the JSON structure
                    first_page_list = data.get(
                        'initData', {}).get('firstPageList', [])
                    hotel_list = first_page_list.get('hotelList', [])

                    for hotel in hotel_list:
                        hotel_name = hotel.get(
                            'hotelBasicInfo', {}).get('hotelName')
                        hotel_img_url = hotel.get(
                            'hotelBasicInfo', {}).get('hotelImg')
                        address = hotel.get(
                            'hotelBasicInfo', {}).get('hotelAddress')
                        price = hotel.get('hotelBasicInfo', {}).get('price')
                        hotel_star = hotel.get('hotelStarInfo', {}).get('star')
                        rating = hotel.get(
                            'commentInfo', {}).get('commentScore')
                        latitude = hotel.get('positionInfo', {}).get(
                            'coordinate', {}).get('lat')
                        longitude = hotel.get('positionInfo', {}).get(
                            'coordinate', {}).get('lng')
                        hotel_id = hotel.get(
                            'hotelBasicInfo', {}).get('hotelId')
                        hotel_ename = hotel.get(
                            'hotelBasicInfo', {}).get('hotelEnName')
                        hotel_url = f"https://uk.trip.com/hotels/{city_name}-hotel-detail-{hotel_id}/{hotel_ename}/"

                        if hotel_name and hotel_img_url:
                            # Create a PropertyItem
                            item = PropertyItem(
                                h3_tag=tag,
                                title=hotel_name,
                                country_name=country_name,
                                city_name=city_name,
                                star=hotel_star,
                                rating=rating,
                                location=address,
                                latitude=latitude,
                                longitude=longitude,
                                room_type=None,
                                price=price,
                                image_paths=''  # We'll update this in the save_image method
                            )

                            yield scrapy.Request(
                                url=hotel_url,
                                callback=self.parse_hotel_detail,
                                meta={
                                    'item': item,
                                    'url': hotel_img_url
                                }
                            )

                except json.JSONDecodeError:
                    self.logger.error(
                        "Failed to parse JSON data for selected city")
            else:
                self.logger.error(
                    "JSON data not found in the script for selected city")
        else:
            self.logger.error(
                "Script containing window.IBU_HOTEL not found for selected city")

    def parse_hotel_detail(self, response):
        try:
            item = response.meta['item']
            link = response.meta['url']

            page_content = response.text

            pattern = r'"roomTypeName\\":\\"(.*?)\\"'
            room_type_names = re.findall(pattern, page_content)

            if not room_type_names:
                self.logger.error("No roomTypeName found on the page")

            # Remove duplicates by converting the list to a set and back to a list
            unique_room_type_names = list(set(room_type_names))

            item['room_type'] = list(set(unique_room_type_names))

            yield scrapy.Request(
                url=link,
                callback=self.save_image,
                meta={'item': item}
            )
        except Exception as e:
            self.logger.error(f"Error in parse_hotel_detail: {str(e)}")

    def save_image(self, response):
        try:
            # Extract hotel name from the response meta
            item = response.meta['item']
            hotel_name = item['title']

            # Create a folder to save images if it doesn't exist
            try:
                if not os.path.exists('hotel_images'):
                    os.makedirs('hotel_images')
            except OSError as e:
                self.logger.error(
                    f"Failed to create directory 'hotel_images': {e}")
                return  # Exit the function if we can't create the directory

            image_path = f'hotel_images/{hotel_name}.jpg'
            try:
                with open(image_path, 'wb') as file:
                    file.write(response.body)
            except IOError as e:
                self.logger.error(f"Failed to save image for {hotel_name}: {e}")
                return  # Exit the function if we can't save the image

            self.logger.info(f"Saved image for {hotel_name} at {image_path}")

            item['image_paths'] = image_path
            yield item

        except Exception as e:
            self.logger.error(f"Unexpected error in save_image for { hotel_name}: {e}")
