from lcd_api import LcdApi
from machine import I2C
import time

class I2cLcd(LcdApi):
    # LCD Command constants
    LCD_BACKLIGHT = 0x08  # Backlight ON
    LCD_NOBACKLIGHT = 0x00  # Backlight OFF
    ENABLE_BIT = 0x04  # Enable bit

    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.backlight = self.LCD_BACKLIGHT
        super().__init__(num_lines, num_columns)

        # Initialize LCD
        self.hal_write_command(0x33)  # Initialize
        self.hal_write_command(0x32)  # Set to 4-bit mode
        self.hal_write_command(0x28)  # 2-line mode
        self.hal_write_command(0x0C)  # Display ON, cursor OFF
        self.hal_write_command(0x06)  # Increment cursor
        self.clear()

    def hal_write_command(self, command):
        """Write a command to the LCD."""
        self.hal_write_byte(command & 0xF0)  # 상위 비트 전송
        time.sleep(0.1)  # 지연 추가
        self.hal_write_byte((command << 4) & 0xF0)  # 하위 비트 전송
        time.sleep(0.1)  # 지연 추가

    def hal_write_data(self, data):
        """Write data to the LCD."""
        self.hal_write_byte(data & 0xF0, rs=True)  # 상위 비트 전송
        time.sleep(0.1)  # 지연 추가
        self.hal_write_byte((data << 4) & 0xF0, rs=True)  # 하위 비트 전송
        time.sleep(0.1)  # 지연 추가


    def hal_write_byte(self, nibble, rs=False):
        """Send a nibble to the LCD."""
        data = nibble | self.backlight
        if rs:
            data |= 0x01  # Set RS bit for data
        self.i2c.writeto(self.i2c_addr, bytearray([data | self.ENABLE_BIT]))
        time.sleep_us(50)
        self.i2c.writeto(self.i2c_addr, bytearray([data & ~self.ENABLE_BIT]))
        time.sleep_us(50)
