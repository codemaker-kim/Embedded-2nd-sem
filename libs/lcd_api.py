class LcdApi:
    # Constants
    LCD_CLR = 0x01  # Clear display command
    LCD_ENTRY_MODE = 0x04  # Set entry mode
    LCD_ENTRY_INC = 0x02  # Increment cursor
    LCD_ENTRY_SHIFT = 0x01  # Shift display
    LCD_ON_CTRL = 0x08  # Display on/off control
    LCD_ON_DISPLAY = 0x04  # Turn display on
    LCD_ON_CURSOR = 0x02  # Turn cursor on
    LCD_ON_BLINK = 0x01  # Turn blinking on
    LCD_MOVE = 0x10  # Cursor or display move
    LCD_MOVE_DISP = 0x08  # Display move
    LCD_MOVE_RIGHT = 0x04  # Move right
    LCD_FUNCTION = 0x20  # Function set
    LCD_FUNCTION_8BIT = 0x10  # 8-bit mode
    LCD_FUNCTION_2LINES = 0x08  # 2 lines
    LCD_FUNCTION_5X10 = 0x04  # 5x10 font
    LCD_CGRAM = 0x40  # Set CGRAM address
    LCD_DDRAM = 0x80  # Set DDRAM address
    LCD_RS_CMD = 0
    LCD_RS_DATA = 1
    LCD_RW_WRITE = 0
    LCD_RW_READ = 1

    def __init__(self, num_lines, num_columns):
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.cursor_x = 0
        self.cursor_y = 0

    def clear(self):
        """Clears the LCD screen and resets the cursor position."""
        self.hal_write_command(self.LCD_CLR)
        self.cursor_x = 0
        self.cursor_y = 0

    def putstr(self, string):
        """Writes a string to the LCD."""
        for char in string:
            if char == '\n':
                self.cursor_x = 0
                self.cursor_y += 1
                if self.cursor_y >= self.num_lines:
                    self.cursor_y = 0
            else:
                self.hal_write_data(ord(char))
                self.cursor_x += 1
                if self.cursor_x >= self.num_columns:
                    self.cursor_x = 0
                    self.cursor_y += 1
                    if self.cursor_y >= self.num_lines:
                        self.cursor_y = 0

    def hal_write_command(self, command):
        """Write a command to the LCD. Must be implemented in a subclass."""
        raise NotImplementedError

    def hal_write_data(self, data):
        """Write data to the LCD. Must be implemented in a subclass."""
        raise NotImplementedError

