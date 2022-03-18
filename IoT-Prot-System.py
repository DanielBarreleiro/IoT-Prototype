import os
from time import sleep
from machine import RTC, Pin
from neopixel import NeoPixel
from libs.iot_app import IoTApp
from libs.bme680 import BME680, OS_2X, OS_4X, OS_8X, FILTER_SIZE_3, DISABLE_GAS_MEAS

access_period = False

neopixel_pin = Pin(21)
neopixel_pin.init(mode=Pin.OUT, pull=Pin.PULL_DOWN)
npm = NeoPixel(neopixel_pin, 32, bpp=3, timing=1)

class MainApp(IoTApp):

    def init(self):
        self.rtc.datetime((2022, 3, 18, 5, 10, 00, 00, 0))
        self.day_names = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

        self.sensor_bme680 = BME680(i2c=self.rig.i2c_adapter, i2c_addr = 0x76)
        
        self.sensor_bme680.set_humidity_oversample(OS_2X)
        self.sensor_bme680.set_pressure_oversample(OS_4X)
        self.sensor_bme680.set_temperature_oversample(OS_8X)
        self.sensor_bme680.set_filter(FILTER_SIZE_3)
        self.sensor_bme680.set_gas_status(DISABLE_GAS_MEAS)

        self.file_name = "a.csv"
        if self.file_exists(self.file_name):
            os.remove(self.file_name)
        self.file = open(self.file_name, "w+") 
        self.acess = False

        self.count = 0

    def loop(self):
        now = self.rtc.datetime()
        year = now[0]
        month = now[1]
        day = now[2]
        hour = now[4]
        minute = now[5]
        second = now[6]

        # Format strings to hold the current date and the current time
        date_str = "{0}/{1}/{2}".format(day, month, year)
        time_str = "{0}:{1}:{2}".format(hour, minute, second)

        self.oled_clear()
        self.oled_text(date_str, 0, 4)
        self.oled_text(time_str, 0, 14)
        self.oled_display()

        if access_period == True:
            self.oled_text("Access: {0}s".format(self.count), 0, 24)
            self.oled_display()
            if self.sensor_bme680.get_sensor_data():
                if self.count > 10:
                    npm.fill((5, 0, 0))
                    npm.write()
                if self.count <= 10:
                    npm.fill((0, 5, 0))
                    npm.write()
                    
                # Current date and time taken from the real-time clock
                now = self.rtc.datetime()
                year = now[0]
                month = now[1]
                day = now[2]
                hour = now[4]
                minute = now[5]
                second = now[6]

                 # Format timestamp
                timestamp = "{0}-{1}-{2}|{3}:{4}:{5}".format(year, month, day, hour, minute, second)

                tm_reading = self.sensor_bme680.data.temperature  # In degrees Celsius 
                rh_reading = self.sensor_bme680.data.humidity     # As a percentage (ie. relative humidity))
                        
                output = "{0} | {1:.2f}C | {2:.2f}%rh".format(timestamp, tm_reading, rh_reading)
                data_str = "{0}\n".format(output)
                self.file.write(data_str)
                self.count += 1
            
        sleep(1)
    
    def deinit(self):
        if self.file:
            self.file.close()

    def file_exists(self, file_name):
        file_names = os.listdir()
        return file_name in file_names

#prints access twice why??
    def btnA_handler(self, pin, pull=Pin.PULL_DOWN):
        global access_period
        access_period = True
        access_start = "{0}\n".format("Access Period Started")
        self.file.write(access_start)
        
    def btnB_handler(self, pin):
        global access_period
        access_period = False
        access_end = "{0}\n".format("Access Period Ended")
        self.file.write(access_end)
        npm.fill((0, 0, 0))
        npm.write()
        self.count = 0

# Program entrance function
def main():

    app = MainApp(name="IoT Prot Sys", has_oled_board=True, finish_button="C", start_verbose=True)
    
    # Run the app
    app.run()

# Invoke main() program entrance
if __name__ == "__main__":
    # execute only if run as a script
    main()