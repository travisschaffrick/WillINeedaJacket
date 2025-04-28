from typing import List, Optional
import requests
import datetime
import pickle
import os
import random


class Controller:
    def __init__(self):
        self.API_KEY = "" # PUT YOUR OWN API_KEY HERE IF MODIFYING CODE
        self.most_recent_data = {}
        self.postal_and_key = {}
        self.output = []
        self.load()

    def save(self):
        with open('saves/most_recent_data.pkl', 'wb') as f:
            pickle.dump(self.most_recent_data, f)
        with open('saves/postal_and_key.pkl', 'wb') as f:
            pickle.dump(self.postal_and_key, f)
        self.output.append("Most Recent Data Saved\n")

    def load(self):
        # Weather Data
        if os.path.isfile('saves/most_recent_data.pkl'):
            with open('saves/most_recent_data.pkl', 'rb') as f:
                self.most_recent_data = pickle.load(f)
        else:
            self.output.append("Load failed, could not find most_recent_data.pkl\n")

        # Postal code and key pairings
        if os.path.isfile('saves/postal_and_key.pkl'):
            with open('saves/postal_and_key.pkl', 'rb') as f:
                self.postal_and_key = pickle.load(f)
                self.output.append(str(self.postal_and_key))
                self.output.append("\n")
        else:
            self.output.append("Load failed, could not find postal_and_key.pkl\n")
        self.output.append("Load Complete\n")

    def get_output(self):
        return self.output

    def get_location_key(self, api_key: str, postal_code: str) -> Optional[str]:
        """
        :param api_key:
        :param postal_code:
        """
        postal_code = postal_code.lower().replace(" ", "")  #A0A 0A0 -> a0a0a0
        if postal_code in self.postal_and_key:
            return self.postal_and_key[postal_code]

        url = f'http://dataservice.accuweather.com/locations/v1/postalcodes/search'
        params = {
            "apikey": api_key,
            "q": postal_code
        }

        response = requests.get(url, params=params)
        response_json = response.json()
        print(response_json)
        if response_json and 'Message' not in response_json[0]: # Message being in response means API used up
            key = response_json[0]['Key']
            self.postal_and_key[postal_code] = key
            return key
        else:
            self.output.append("Empty response_json, failed to get request\n")
            return None

    def get_current_conditions(self, api_key: str, location_key: str) -> dict[str, str]:
        """
        Get current weather conditions for a location key
        :param api_key:
        :param location_key:
        """
        url = f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}"
        params = {
            "apikey": api_key,
            "details": True
        }
        if location_key in self.most_recent_data:
            if False == True and datetime.datetime.today() - self.get_date_of_query(location_key) < datetime.timedelta(hours=1):
                # Info was fetched within the past day so return early
                self.output.append(f"Reused data! ({location_key})\n")
                return self.most_recent_data[location_key]

        # Data doesn't exist or is outdated, fetch new
        self.output.append(f"Getting current weather conditions ({location_key})\n")
        response = requests.get(url, params=params)
        response_json = response.json()
        if response_json and 'Message' not in response_json: # Message means error
            response_dict = response_json[0]
        else:
            self.output.append("Empty response_json, failed to get request\n")
            return None

        # Save Data
        if response_dict:
            self.most_recent_data[location_key] = response_dict
        self.save()

        return response.json()[0]

    def get_date_of_query(self, key: str) -> Optional[datetime.date]:
        """Takes in a location key and returns the date of the query in datetime format"""
        if key in self.most_recent_data:
            iso_date = self.most_recent_data[key]['LocalObservationDateTime']  # Stored in ISO Format
            date_of_query = datetime.datetime.fromisoformat(iso_date)
            naive = date_of_query.replace(tzinfo=None)
            return naive

    def get_wind_phrase(self, wind_speed):
        if 30 <= wind_speed <= 39:
            strength = "Fresh Breeze"
        elif 40 <= wind_speed <= 49:
            strength = "Strong Breeze"
        elif 50 <= wind_speed <= 61:
            strength = "Near Gale"
        elif 62 <= wind_speed <= 74:
            strength = "Gale"
        elif 75 <= wind_speed <= 88:
            strength = "Strong Gale"
        elif 89 <= wind_speed <= 102:
            strength = "Storm"
        elif wind_speed > 102:
            strength = "Hurricane Force"
        else:  # wind_speed < 30
            strength = "Insignificant"

        return strength

    def what_clothing(self, location_key: str) -> str:
        if location_key not in self.most_recent_data:
            self.output.append("what_clothing function failed, location_key not in most recent data\n")
            return "You live in the void, follow your wildest dreams."
        if random.random() <= 0.01:
            return "NAKED!!!"
        data = self.most_recent_data[location_key]
        temperature = data['RealFeelTemperature']['Metric']['Value']
        has_precipitation = data['HasPrecipitation']
        precipitation_type = data['PrecipitationType']
        weather_text = data['WeatherText']
        # Recommendation made from temperature alone

        if "rain" in weather_text.lower():
            temperature -= 5 # Adjust for poor conditions because i couldn't think of any other way lol


        if temperature >= 30:
            recommendation = "You can go outside shirtless."
        elif 17 <= temperature < 30:
            recommendation = "Wear a t-shirt."
        elif 7 <= temperature < 17:
            recommendation = "Put on a sweater."
        elif 0 <= temperature < 7:
            recommendation = "You will need a jacket."
        else:  # temperature < 0
            recommendation = "Grab your parka!"

        # Add precipitation advice
        if has_precipitation:
            if weather_text in ["Rain", "Heavy rain"]:
                recommendation += " Don't forget an umbrella or raincoat."
            elif weather_text in ["Snow", "Flurries"]:
                recommendation += " Make sure to wear waterproof boots."

        return recommendation
