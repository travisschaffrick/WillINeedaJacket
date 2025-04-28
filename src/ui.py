from PyQt6 import uic
import controller as c


class MyApp:
    def __init__(self):
        # Load the file
        self.ui = uic.loadUi('ui/main.ui')

        # Search functionality
        self.ui.submitButton.clicked.connect(self.search)

        # Display UI
        self.ui.show()
        self.controller = c.Controller()

    def search(self):
        # Get postal code from text box
        postal_code = self.ui.textEdit.toPlainText()

        location_key = self.controller.get_location_key(self.controller.API_KEY, postal_code)
        current_conditions = self.controller.get_current_conditions(self.controller.API_KEY, location_key)

        if current_conditions:
            clothing_recommendation = self.controller.what_clothing(location_key)
            date = self.controller.get_date_of_query(location_key)
            uv_index = self.controller.most_recent_data[location_key]['UVIndex']
            uv_index_phrase = self.controller.most_recent_data[location_key]['UVIndexText']
            wind_speed = self.controller.most_recent_data[location_key]['Wind']['Speed']['Metric']['Value']
            wind_direction = self.controller.most_recent_data[location_key]['Wind']['Direction']['English']
            wind_gusts = self.controller.most_recent_data[location_key]['WindGust']['Speed']['Metric']['Value']
            wind_phrase = self.controller.get_wind_phrase(wind_speed)
            output = (
                f"Recommendation: {clothing_recommendation}\n\n"
                f"Weather Report:\n"
                f"----------------\n"
                f"Condition: {current_conditions['WeatherText']}\n"
                f"Temperature (True): {current_conditions['Temperature']['Metric']['Value']}°C\n"
                f"Temperature (Feels Like): It feels {current_conditions['RealFeelTemperature']['Metric']['Phrase']} \
out with a temperature of {current_conditions['RealFeelTemperature']['Metric']['Value']}°C\n"
                f'{f"Wind: Wind is blowing {wind_direction} at {wind_speed}km/h with gusts of {wind_gusts}km/h \
({wind_phrase})\n" if wind_phrase != "Insignificant" else ""}'
                f"UV Index: The UV Index is {uv_index} ({uv_index_phrase}). {"Wear sunscreen." if uv_index >= 3 else ""}\n"
                f"Last Updated: {date.ctime()}"
            )
            self.ui.responseField.setText(output)
