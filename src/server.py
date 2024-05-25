from time import sleep
from flask import Flask
from seleniumwire import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from seleniumwire.utils import decode
from geopy import geocoders
import datetime
import requests


app = Flask(__name__)

@app.route('/')
def hello_world(query="hotel in boston from 2024-06-04 to 2024-06-20"):
    origin = 'seoul'
    destination = 'boston'
    start_day = '2024-06-04'
    end_day = '2024-06-20'
    driver = webdriver.Chrome()
    hotel_result = None
    flight_result = None
    weather_result = None
    todo_result = None
    try:
        # Hotel
        driver.get('https://www.google.com/search?q=hotel+in+%s+from+%s+to+%s' % (destination, start_day, end_day))
        go_to_hotel_detail = WebDriverWait(driver, 5, poll_frequency=0.1).until(
            EC.presence_of_element_located((By.CLASS_NAME, "S8ee5.CwbYXd.wHYlTd"))
        )
        go_to_hotel_detail.click()
        for i, request in enumerate(driver.requests):
            if request.response:
                try:
                    response_str = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity')).decode('utf-8')
                    if response_str.find('<div ng-non-bindable=""><div class="gb_m">Google 앱</div><div class="gb_Qc">') != -1:
                    #if response_str.find('Four Points by') != -1:
                        #print(response_str)
                        hotel_result = response_str
                        print(request.url)
                        print(i)
                        print(response_str)
                        file = open('read.txt', 'w')
                        file.write(response_str)
                        file.close()
                except:
                    continue
        print('hotel done')

        '''
        #Flight
        driver.get(f'https://www.google.com/travel/flights?tfs=CBwQARocagwIAhIIL20vMGhzcWZyDAgDEggvbS8wMWN4XxocagwIAxIIL20vMDFjeF9yDAgCEggvbS8waHNxZkABSAFwAYIBCwj___________8BmAEB&tfu=KgIIAw')
        start_date = datetime.datetime.strptime(start_day, "%Y-%m-%d")
        start_date_str = f'{start_date.strftime("%b")} {start_date.day}'
        end_date = datetime.datetime.strptime(end_day, "%Y-%m-%d")
        end_date_str = f'{end_date.strftime("%b")} {end_date.day}'
        day_inputs = WebDriverWait(driver, 5, poll_frequency=0.1).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME,"TP4Lpb.eoY5cb.j0Ppje"))
        )
        day_inputs[0].send_keys(start_date_str)
        day_inputs[1].send_keys(end_date_str)
        origin_input = WebDriverWait(driver, 5, poll_frequency=0.1).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[1]/div/div/div[1]/div/div/input"))
        )
        origin_input.clear()
        origin_input.send_keys(origin)
        #origin_input.send_keys(Keys.RETURN)
        destination_input = WebDriverWait(driver, 5, poll_frequency=0.1).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[4]/div/div/div[1]/div/div/input"))
        )
        destination_input.clear()
        destination_input.send_keys(destination)
        destination_input.send_keys(Keys.ENTER)
        for i, request in enumerate(driver.requests):
            if request.response:
                try:
                    response_str = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity')).decode('utf-8')
                    if response_str.find('</script><div ng-non-bindable=""><div class="gb_m">Google apps</div><div class="gb_Qc">Main menu</div></div>') != -1:
                        flight_result = response_str
                        print(request.url)
                        print(i)
                except:
                    continue
        print('flight done')
        #todo
        todo_result = ''
        for keyword in ['news', 'things-to-do','food-drink','culture','travel','hotels','time-out-market']:
            driver.get(f'https://www.timeout.com/{destination}/{keyword}')
            html = driver.page_source
            todo_result += html
        print('todo done')

        #weather
        gn = geocoders.GeoNames(username='sugsugsug')
        loc = gn.geocode(destination)
        r = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={loc.latitude}&longitude={loc.longitude}&current=relative_humidity_2m,rain,cloud_cover&hourly=temperature_2m,relative_humidity_2m,dew_point_2m,apparent_temperature,precipitation_probability,precipitation,rain,showers,snowfall,snow_depth,weather_code,pressure_msl,cloud_cover_high,visibility,evapotranspiration,wind_direction_80m,temperature_80m,temperature_120m,soil_temperature_54cm&daily=temperature_2m_max,apparent_temperature_max,daylight_duration,uv_index_max,snowfall_sum,wind_gusts_10m_max,shortwave_radiation_sum&forecast_days=16')
        weather_result = r.json()
        print('weather done')

        result = [hotel_result, flight_result, todo_result, weather_result]
        '''
    finally:
        driver.quit()
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True, port=5000)
