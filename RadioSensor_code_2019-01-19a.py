# T201 Radio Sensor
import time
import board
import busio as io
import adafruit_bme680
import digitalio
import adafruit_rfm69
from digitalio import DigitalInOut
import adafruit_ssd1306
import neopixel

i2c = io.I2C(board.SCL, board.SDA)
spi = io.SPI(board.SCK, board.MOSI, board.MISO)
sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c, 0x76)
led = neopixel.NeoPixel(board.NEOPIXEL, 1)
cs = digitalio.DigitalInOut(board.D9)
reset = digitalio.DigitalInOut(board.D11)
# Create the I2C interface.

# A reset line may be required if there is no auto-reset circuitry
# reset_pin = DigitalInOut(board.D5)
# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
# The I2C address for these displays is 0x3d or 0x3c, change to match
# A reset line may be required if there is no auto-reset circuitry
# display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
#oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, 0x3d)  #, addr=0x3d)

RADIO_FREQ_MHZ = 434.0
# Initialze RFM radio
rfm69 = adafruit_rfm69.RFM69(spi, cs, reset, RADIO_FREQ_MHZ)
# ino: uint8_t key[] ="VillaAstrid_2003"
e_key = b'\x56\x69\x6c\x6c\x61\x41\x73\x74\x72\x69\x64\x5f\x32\x30\x30\x33'
rfm69.encryption_key = e_key
rec_msg = {'Zone': '', 'Sensor': '', 'Value': '', 'Remark': ''}
sensor_4char = {'T_bmp180': 'TMP2', 'P_bmp180': 'ILMP', 
                'H_dht22': 'HUM ', 'T_dht22': 'TMP1',
                'T_Water': 'LAKE', 'Light1': 'LDR1', 'Light2': 'LDR2',
                'Temp2': 'TMP2'}

def json_fix(s):
    n = s.find(':')
    s = s[n+1:]
    if s[0] == '"':
        s = s[1:-1]
    return s
def sensor_fix4(s):
    if s in sensor_4char:
        s = sensor_4char[s]
    return s
def json_attr(s):
    jattr = ''
    if s[0] == '"' and s[2] == '"':
        if s[1] == 'Z': 
            jattr = 'Zone'
        elif s[1] == 'S': 
            jattr = 'Sensor'
        elif s[1] == 'V': 
            jattr = 'Value'
        elif s[1] == 'R': 
            jattr = 'Remark'
    return jattr

def parse_json(radio_str):
    # radio_str = '{"Z":"OD_1","S":"Hum","V":99.90,"R":""}'
    if radio_str.endswith('}') and radio_str.startswith('{'):
        print('JSON is OK')
        rs = radio_str[1:-1].split(',')
        # print(rs)
        for i in range(len(rec_msg)):
            attr = json_attr(rs[i])
            # print(attr)
            if attr in rec_msg:
                # print(json_fix(rs[i]))
                s1 = json_fix(rs[i])
                if attr == 'Sensor':
                    s1 = sensor_fix4(s1)
                rec_msg[attr] = s1   
        # print(rec_msg)
# display1 = adafruit_ht16k33.segments.Seg14x4(i2c)

def float_to_json(zone, sensor, value, float_format, remark):
    JsonString = '{\"Z\":\"'
    JsonString += zone + '\",'
    JsonString += '\"S\":\"'
    JsonString += sensor + '\",'
    JsonString += '\"V\":'
    JsonString += float_format.format(value)
    JsonString += ',\"R\":\"'
    JsonString += remark
    JsonString += '\"}'
    return(JsonString)
    
led[0] = (255, 0, 0)
# print('Temperature: {:.1f} degrees C'.format(sensor.temperature))
# print('Gas: {} ohms'.format(sensor.gas))
# print('Humidity: {}%'.format(sensor.humidity))
# print('Pressure: {}hPa'.format(sensor.pressure))
# display1.fill(0)
# display1.print('{:.1f}'.format(sensor.temperature))

print('Waiting for packets...')
  
radio_str = '{"Z":"OD_1","S":"Hum","V":99.90,"R":""}'
parse_json(radio_str)
saved_time = time.monotonic()
meas_indx = 0
while True:
    if time.monotonic() - saved_time > 10:
        saved_time = time.monotonic()    
        # oled.fill(0)
        # oled.text('{:.1f}'.format(sensor.temperature),0,0,1)
        # oled.show()

        meas_indx += 1
        if meas_indx == 1:
            # s = float_to_json('TEST', 'TEMP', sensor.temperature, 'C')
            rfm69.send(bytes(float_to_json('TEST', 'TEMP', 
                             sensor.temperature, '{:.1f}', 'C'), 'utf-8'))
        elif meas_indx == 2:                      
            rfm69.send(bytes(float_to_json('TEST', 'HUM ', 
                             sensor.humidity/100, '{:.0%}',''), 'utf-8'))
        elif meas_indx == 3:                      
            rfm69.send(bytes(float_to_json('TEST', 'GAS ', 
                             sensor.gas/1000, '{:.0f}', 'kOhm'), 'utf-8'))
        elif meas_indx == 4:                      
            rfm69.send(bytes(float_to_json('TEST', 'hPa ', 
                             sensor.pressure,  '{:.0f}',''), 'utf-8'))
        else:
            meas_indx = 0
            # rfm69.send(bytes('Temperature: {:.1f} degrees C'.format(sensor.temperature),'utf-8'))
        # time.sleep(2)
        # packet = rfm69.receive()
        # Optionally change the receive timeout from its default of 0.5 seconds:
        # packet = rfm69.receive(timeout=5.0)
        # If no packet was received during the timeout then None is returned.
        #if packet is None:
            # pass
            # print('Received nothing! Listening again...')
    else:
        pass 
      