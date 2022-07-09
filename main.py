import threading
import gi

gi.require_version("Gtk", "3.0")

import os
import json
import time
import requests
from queue import Queue
from gi.repository import Gtk


class Weather:
    def __init__(self) -> None:
        self.service_url: str = "http://api.weatherapi.com/v1/current.json"
        self.response: requests.Response

        try:
            self.apiKey = open("weather_api.txt", "r").readline()
        except FileExistsError:
            print("file does not exist")
            exit(0)

    def getWeatherData(self, city: str) -> tuple:
        url = self.service_url + "?key=" + self.apiKey.strip() + "&q=" + city

        self.response = requests.get(url)

        if "current" in self.response.json():
            feelslike_c = self.response.json()["current"]["feelslike_c"]
            feelslike_f = self.response.json()["current"]["feelslike_f"]
            humidity = self.response.json()["current"]["humidity"]
            cloud = self.response.json()["current"]["cloud"]
            temp_c = self.response.json()["current"]["temp_c"]
            temp_f = self.response.json()["current"]["temp_f"]

            return (feelslike_c, feelslike_f, humidity, cloud, temp_c, temp_f)
        else:
            raise Exception("Please Enter Proper City Name")

    def main(self, **args):

        print(
            json.dumps(
                self.response.json(),
            )
        )

    def getReadableWeatherData(self, weather_data: tuple[int, ...]) -> tuple[str, ...]:
        if 0 <= weather_data[3] < 20:
            cloudiness = "Clear"
        elif 20 <= weather_data[3] < 40:
            cloudiness = "Slightly Cloudy"
        elif 40 <= weather_data[3] < 60:
            cloudiness = "Partly Cloudy"
        elif 60 <= weather_data[3] < 80:
            cloudiness = "Cloudy"
        elif 80 <= weather_data[3] <= 100:
            cloudiness = "Extremely Cloudy"

        return (
            f"Temperature is: {weather_data[4]}°C",
            f"Feels like: {weather_data[0]}°C",
            f"Humidity: {weather_data[2]}%",
            # f"Feels like: {weather_data[1]}°F",
            # f"Temperature is: {weather_data[4]}°F",
            "Sky:" + str(cloudiness),
        )


class Window:
    def __init__(self) -> None:
        self.builder = Gtk.Builder()
        self.builder.add_from_file(
            os.path.abspath(os.path.expanduser(os.path.expandvars("Glade/GUI.glade")))
        )

        self.window = self.builder.get_object("window1")
        self.window.connect("destroy", Gtk.main_quit)

        self.weather: Weather = Weather()

        self.search = self.builder.get_object("search")
        self.label = self.builder.get_object("label")

    def setWeatherLabels(self, weather_data: tuple[int, ...]) -> str:
        text = ""
        labels = [
            self.builder.get_object("label1"),
            self.builder.get_object("label2"),
            self.builder.get_object("label3"),
            self.builder.get_object("label4"),
        ]
        for i, i1 in zip(self.weather.getReadableWeatherData(weather_data), labels):
            i1.set_text(i)

        return text

    def updateFields(self):
        def update(*args):
            text = self.search.get_text()

            def weather_what(q):
                weather_data = self.weather.getWeatherData(text)
                q.put(weather_data)

            q = Queue()
            th = threading.Thread(target=weather_what, args=(q,))

            th.start()
            th.join()
            # self.label.set_text(self.getWeatherLabel(weather_data))
            self.setWeatherLabels(q.get())

        self.search.connect("activate", update)

    def main(self):
        self.updateFields()
        self.window.show_all()
        Gtk.main()


if __name__ == "__main__":
    window = Window()
    window.main()
