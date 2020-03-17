import requests, json

api = ('http://api.openweathermap.org/data/2.5/weather?q=%s&appid=1947089d8ce1bcc3c318ca30b2aba583',)


def get_weather(city) -> json:
    response = requests.get(api[0] % city)
    city_weather = response.json()
    if city_weather["cod"] == "404":
        weather_ui = ('404',)
        return weather_ui
    temp = city_weather["main"]["temp"]
    weather_ui = list()
    weather_ui.append("--=====[Weather]=====--\n")
    weather_ui.append("City: %(cityName)s,%(country)s Weather: %(weather)s\n"
                      % {"cityName": city, "weather": city_weather["weather"][0]["description"],
                         "country": city_weather["sys"]["country"]})
    weather_ui.append("Temperature: %(t_fahr).01f F | %(t_celsius).01f C\n"
                      % {"t_fahr": ((float(temp) - 273.15) * 1.8 + 32), "t_celsius": (float(temp) - 273.15)})
    weather_ui.append("Wind speed: %(wind_speed)s\n" % {"wind_speed": city_weather["wind"]["speed"]})
    weather_ui.append("=======================")
    return weather_ui
