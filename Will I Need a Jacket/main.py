from typing import List, Optional
import requests
import json
import datetime
import pickle
import os


class Controller:
    def __init__(self):
        self.API_KEY = "uCdHvxRv0HBt2yLxIVEBZqdvmAss4wZd"
        self.most_recent_data = {}
        self.postal_and_key = {}
        self.load()

    def save(self):
        with open('most_recent_data.pkl', 'wb') as f:
            pickle.dump(self.most_recent_data, f)
        with open('postal_and_key.pkl', 'wb') as f:
            pickle.dump(self.postal_and_key, f)
        print("Most Recent Data Saved")

    def load(self):
        # Weather Data
        if os.path.isfile('most_recent_data.pkl'):
            with open('most_recent_data.pkl', 'rb') as f:
                self.most_recent_data = pickle.load(f)
        else:
            print("Load failed, could not find most_recent_data.pkl")

        # Postal code and key pairings
        if os.path.isfile('postal_and_key.pkl'):
            with open('postal_and_key.pkl', 'rb') as f:
                self.postal_and_key = pickle.load(f)
        else:
            print("Load failed, could not find postal_and_key.pkl")
        print("Load Complete")

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

        if response_json:
            key = response_json[0]['Key']
            self.postal_and_key[key] = postal_code
            return key
        else:
            return None

    def get_current_conditions(self, api_key: str, location_key: str) -> dict[str, str]:
        """
        Get current weather conditions for a location key
        :param api_key:
        :param location_key:
        """
        url = f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}"
        params = {
            "apikey": api_key
        }
        if location_key in self.most_recent_data:
            if datetime.datetime.today() - self.get_date_of_query(location_key) < datetime.timedelta(hours=1):
                # Info was fetched within the past day so return early
                print("Reused data!")
                return self.most_recent_data[location_key]

        # Data doesn't exist or is outdated, fetch new
        print("Getting current weather conditions")
        response = requests.get(url, params=params)
        response_dict = response.json()[0]

        # Save Data
        response_dict['Key'] = location_key
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

    def what_clothing(self, location_key: str) -> str:
        if location_key not in self.most_recent_data:
            return "You live in the void, follow your wildest dreams."
        data = self.most_recent_data[location_key]
        temperature = data['Temperature']['Metric']['Value']
        if temperature >= 30:
            return "You can go outside shirtless."
        if 14 <= temperature < 30:
            return "Wear a t-shirt."
        if 7 <= temperature < 14:
            return "Put on a sweater."
        if 0 <= temperature < 7:
            return "You will need a jacket."
        if temperature < 0:
            return "Grab your parka!"


    def query(self):
        """
        Query weather conditions for a location key
        :return:
        """
        postal_code = input("Enter postal code: ")

        location_key = self.get_location_key(self.API_KEY, postal_code)
        current_conditions = self.get_current_conditions(self.API_KEY, location_key)
        print(f"It is currently {current_conditions['WeatherText']} out, with a temperature of {current_conditions['Temperature']['Metric']['Value']} Degrees Celsius.")
        clothing_recommendation = self.what_clothing(location_key)
        print(clothing_recommendation)


controller = Controller()
controller.query()
