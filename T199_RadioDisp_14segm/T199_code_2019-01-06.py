import board
import busio as io
import adafruit_ht16k33.segments
import adafruit_bme680
import digitalio
import adafruit_rfm69
# import adafruit_sdcard
# import storage
import neopixel

i2c = io.I2C(board.SCL, board.SDA)
spi = io.SPI(board.SCK, board.MOSI, board.MISO)
sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c,0x76)
led = neopixel.NeoPixel(board.NEOPIXEL, 1)
cs = digitalio.DigitalInOut(board.D9)
reset = digitalio.DigitalInOut(board.D11)
display1 = adafruit_ht16k33.segments.Seg14x4(i2c, address=0x70)
display2 = adafruit_ht16k33.segments.Seg14x4(i2c, address=0x71)

display3 = adafruit_ht16k33.segments.Seg14x4(i2c, address=0x72)

RADIO_FREQ_MHZ = 434.0
# Initialze RFM radio
rfm69 = adafruit_rfm69.RFM69(spi, cs, reset, RADIO_FREQ_MHZ)
# ino: uint8_t key[] ="VillaAstrid_2003"
e_key = b'\x56\x69\x6c\x6c\x61\x41\x73\x74\x72\x69\x64\x5f\x32\x30\x30\x33'
rfm69.encryption_key = e_key
rec_msg = {'Zone': '', 'Sensor': '', 'Value': '', 'Remark': ''}
sensor_4char = {'T_bmp180': 'TMP2', 'P_bmp180': 'ILMP', 
                'H_dht22':'HUM ','T_dht22':'TMP1',
                'T_Water': 'LAKE', 'Light1': 'LDR1', 'Light2': 'LDR2',
                'Temp2','TMP2'}

def json_fix(s):
    n = s.find(':')
    s= s[n+1:]
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
    #radio_str = '{"Z":"OD_1","S":"Hum","V":99.90,"R":""}'
    if radio_str.endswith('}') and radio_str.startswith('{'):
        print('JSON is OK')
        rs = radio_str[1:-1].split(',')
        #print(rs)
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

display1.fill(0)
display1.show()
display2.fill(0)
display2.show()
display3.fill(0)
display3.show()
# display1[0] = 'M'
 
display1.print('-21.2')
display1.show()

display2.fill(0)
display2.print('XYZ_')
display2.brightness = 15
display2.show()


display3.fill(0)
display3.print('T196')
display3.brightness = 15
display3.show()

led[0] = (255, 0, 0)
print('Temperature: {:.1f} degrees C'.format(sensor.temperature))
print('Gas: {} ohms'.format(sensor.gas))
print('Humidity: {}%'.format(sensor.humidity))
print('Pressure: {}hPa'.format(sensor.pressure))
display1.fill(0)
display1.print('{:.1f}'.format(sensor.temperature))
print('Waiting for packets...')
  
radio_str = '{"Z":"OD_1","S":"Hum","V":99.90,"R":""}'
parse_json(radio_str)
  
while True:
    packet = rfm69.receive()
    # Optionally change the receive timeout from its default of 0.5 seconds:
    # packet = rfm69.receive(timeout=5.0)
    # If no packet was received during the timeout then None is returned.
    if packet is None:
        pass
        # print('Received nothing! Listening again...')
    else:
        # Received a packet!
        # Print out the raw bytes of the packet:
        print('Received (raw bytes): {0}'.format(packet))
        # And decode to ASCII text and print it too.  Note that you always
        # receive raw bytes and need to convert to a text format like ASCII
        # if you intend to do string processing on your data.  Make sure the
        # sending side is sending ASCII data before you try to decode!
        packet_text = str(packet, 'ascii')
        print('Received (ASCII): {0}'.format(packet_text))
        rec = '{0}'.format(packet_text)
        parse_json(rec)
        print(rec_msg)
        display1.fill(0)
        display1.print(rec_msg['Zone'])
        display2.fill(0)
        display2.print(rec_msg['Sensor'])
        display3.fill(0)
        display3.print(rec_msg['Value'])