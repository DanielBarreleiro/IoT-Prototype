import os
from time import sleep
from machine import RTC, Pin
from libs.iot_app import IoTApp
from libs.bme680 import BME680, OS_2X, OS_4X, OS_8X, FILTER_SIZE_3, DISABLE_GAS_MEAS

access_period = False

class MainApp(IoTApp):

    def init(self):
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

    def loop(self):
        self.oled_clear()

        if access_period == True:
            if self.sensor_bme680.get_sensor_data():
                tm_reading = self.sensor_bme680.data.temperature  # In degrees Celsius 
                rh_reading = self.sensor_bme680.data.humidity     # As a percentage (ie. relative humidity))
                        
                output = "{0:.2f}C | {1:.2f}%rh".format(tm_reading, rh_reading)
                data_str = "{0}\n".format(output)
                self.file.write(data_str)
            
        sleep(1)
    
    def deinit(self):
        if self.file:
            self.file.close()

    def file_exists(self, file_name):
        file_names = os.listdir()
        return file_name in file_names

#print access twice??
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

# Program entrance function
def main():
    app = MainApp(name="IoT Prot Sys", has_oled_board=True, finish_button="C", start_verbose=True)
    
    # Run the app
    app.run()

# Invoke main() program entrance
if __name__ == "__main__":
    # execute only if run as a script
    main()