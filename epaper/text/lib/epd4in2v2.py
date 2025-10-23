from machine import Pin, SPI
import framebuf
import utime

# Display resolution
EPD_WIDTH       = 400
EPD_HEIGHT      = 300

SCK_PIN         = 18
DIN_PIN         = 23
RST_PIN         = 22
DC_PIN          = 32
CS_PIN          = 33
BUSY_PIN        = 21

LUT_ALL=[   0x01,	0x0A,	0x1B,	0x0F,	0x03,	0x01,	0x01,	
            0x05,	0x0A,	0x01,	0x0A,	0x01,	0x01,	0x01,	
            0x05,	0x08,	0x03,	0x02,	0x04,	0x01,	0x01,	
            0x01,	0x04,	0x04,	0x02,	0x00,	0x01,	0x01,	
            0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
            0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
            0x01,	0x0A,	0x1B,	0x0F,	0x03,	0x01,	0x01,	
            0x05,	0x4A,	0x01,	0x8A,	0x01,	0x01,	0x01,	
            0x05,	0x48,	0x03,	0x82,	0x84,	0x01,	0x01,	
            0x01,	0x84,	0x84,	0x82,	0x00,	0x01,	0x01,	
            0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
            0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
            0x01,	0x0A,	0x1B,	0x8F,	0x03,	0x01,	0x01,	
            0x05,	0x4A,	0x01,	0x8A,	0x01,	0x01,	0x01,	
            0x05,	0x48,	0x83,	0x82,	0x04,	0x01,	0x01,	
            0x01,	0x04,	0x04,	0x02,	0x00,	0x01,	0x01,	
            0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
            0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
            0x01,	0x8A,	0x1B,	0x8F,	0x03,	0x01,	0x01,	
            0x05,	0x4A,	0x01,	0x8A,	0x01,	0x01,	0x01,	
            0x05,	0x48,	0x83,	0x02,	0x04,	0x01,	0x01,	
            0x01,	0x04,	0x04,	0x02,	0x00,	0x01,	0x01,	
            0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
            0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
            0x01,	0x8A,	0x9B,	0x8F,	0x03,	0x01,	0x01,	
            0x05,	0x4A,	0x01,	0x8A,	0x01,	0x01,	0x01,	
            0x05,	0x48,	0x03,	0x42,	0x04,	0x01,	0x01,	
            0x01,	0x04,	0x04,	0x42,	0x00,	0x01,	0x01,	
            0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
            0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
            0x00,	0x00,	0x00,	0x00,	0x00,	0x00,	0x00,	
            0x00,	0x00,	0x00,	0x00,	0x00,	0x00,	0x00,	
            0x02,	0x00,	0x00,	0x07,	0x17,	0x41,	0xA8,	
            0x32,	0x30 ]

class EPD_4in2:
    def __init__(self):
        self.reset_pin = Pin(RST_PIN, Pin.OUT)
        
        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        self.Seconds_1_5S = 0
        self.Seconds_1S = 1
        self.LUT_ALL = LUT_ALL
        
        self.black = 0x00
        self.white = 0xff
        self.darkgray = 0xaa
        self.grayish = 0x55
        
        self.spi = SPI(1)
        self.spi.init(baudrate=4000_000, sck=Pin(SCK_PIN), mosi=Pin(DIN_PIN))
        self.dc_pin = Pin(DC_PIN, Pin.OUT)

        self.buffer_1Gray = bytearray(self.height * self.width // 8)
        self.buffer_4Gray = bytearray(self.height * self.width // 4)
        self.image1Gray = framebuf.FrameBuffer(self.buffer_1Gray, self.width, self.height, framebuf.MONO_HLSB)
        self.image4Gray = framebuf.FrameBuffer(self.buffer_4Gray, self.width, self.height, framebuf.GS2_HMSB)
        
        self.EPD_4IN2_V2_Init()
        self.EPD_4IN2_V2_Clear()
        utime.sleep_ms(500)

    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def delay_ms(self, delaytime):
        utime.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    def module_exit(self):
        self.digital_write(self.reset_pin, 0)

    # Hardware reset
    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(20) 
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(20)
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(20)
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(20)  

    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([command])
        self.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([data])
        self.digital_write(self.cs_pin, 1)
        
    def send_data1(self, buf):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi.write(bytearray(buf))
        self.digital_write(self.cs_pin, 1)
        
    def ReadBusy(self):
        #print("e-Paper busy")
        while(self.digital_read(self.busy_pin) == 1):      #  LOW: idle, HIGH: busy
            self.delay_ms(100) 
        #print("e-Paper busy release")
        
        
    def TurnOnDisplay(self):
        self.send_command(0x22) #Display Update Control
        self.send_data(0xF7)
        self.send_command(0x20) #Activate Display Update Sequence
        self.ReadBusy()
        
    def TurnOnDisplay_Fast(self):
        self.send_command(0x22) #Display Update Control
        self.send_data(0xC7)
        self.send_command(0x20) #Activate Display Update Sequence
        self.ReadBusy()
        
    def TurnOnDisplay_Partial(self):
        self.send_command(0x22) #Display Update Control
        self.send_data(0xFF)
        self.send_command(0x20) #Activate Display Update Sequence
        self.ReadBusy()
        
    def TurnOnDisplay_4GRAY(self):
        self.send_command(0x22) #Display Update Control
        self.send_data(0xCF)
        self.send_command(0x20) #Activate Display Update Sequence
        self.ReadBusy()
            
    def EPD_4IN2_V2_Init(self):
        # EPD hardware init start
        self.reset()
        self.ReadBusy()

        self.send_command(0x12) #SWRESET
        self.ReadBusy()

        self.send_command(0x21)  # Display update control
        self.send_data(0x40)
        self.send_data(0x00)

        self.send_command(0x3C)  # BorderWavefrom
        self.send_data(0x05)

        self.send_command(0x11)  # data  entry  mode
        self.send_data(0x03)  # X-mode

        self.send_command(0x44) 
        self.send_data(0x00)
        self.send_data(0x31)  
        
        self.send_command(0x45) 
        self.send_data(0x00)
        self.send_data(0x00)  
        self.send_data(0x2B)
        self.send_data(0x01)

        self.send_command(0x4E) 
        self.send_data(0x00)

        self.send_command(0x4F) 
        self.send_data(0x00)
        self.send_data(0x00)  
        self.ReadBusy()

    def EPD_4IN2_V2_Init_Fast(self, mode):
        self.reset()
        self.ReadBusy()

        self.send_command(0x12) #SWRESET
        self.ReadBusy()

        self.send_command(0x21)  # Display update control
        self.send_data(0x40)
        self.send_data(0x00)

        self.send_command(0x3C)  # BorderWavefrom
        self.send_data(0x05)

        if mode == self.Seconds_1_5S:
            self.send_command(0x1A)
            self.send_data(0x6E)  
        else :
            self.send_command(0x1A)
            self.send_data(0x5A)  

        self.send_command(0x22)  # Load temperature value
        self.send_data(0x91)  
        self.send_command(0x20)  
        self.ReadBusy()

        self.send_command(0x11)  # data  entry  mode
        self.send_data(0x03)  # X-mode

        self.send_command(0x44) 
        self.send_data(0x00)
        self.send_data(0x31)  
        
        self.send_command(0x45) 
        self.send_data(0x00)
        self.send_data(0x00)  
        self.send_data(0x2B)
        self.send_data(0x01)

        self.send_command(0x4E) 
        self.send_data(0x00)

        self.send_command(0x4F) 
        self.send_data(0x00)
        self.send_data(0x00)  
        self.ReadBusy()

    def Lut(self):
        self.send_command(0x32)
        for i in range(227):
            self.send_data(self.LUT_ALL[i])

        self.send_command(0x3F)
        self.send_data(self.LUT_ALL[227])

        self.send_command(0x03)
        self.send_data(self.LUT_ALL[228])

        self.send_command(0x04)
        self.send_data(self.LUT_ALL[229])
        self.send_data(self.LUT_ALL[230])
        self.send_data(self.LUT_ALL[231])

        self.send_command(0x2c)
        self.send_data(self.LUT_ALL[232])
        
    def EPD_4IN2_V2_Init_4Gray(self):
        # EPD hardware init start
        self.reset()
        self.ReadBusy()

        self.send_command(0x12) #SWRESET
        self.ReadBusy()

        self.send_command(0x21)  # Display update control
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x3C)  # BorderWavefrom
        self.send_data(0x03)

        self.send_command(0x0C)  # BTST
        self.send_data(0x8B) # 8B
        self.send_data(0x9C) # 9C 
        self.send_data(0xA4) # 96 A4
        self.send_data(0x0F) # 0F

        self.Lut()

        self.send_command(0x11)  # data  entry  mode
        self.send_data(0x03)  # X-mode

        self.send_command(0x44) 
        self.send_data(0x00)
        self.send_data(0x31)  
        
        self.send_command(0x45) 
        self.send_data(0x00)
        self.send_data(0x00)  
        self.send_data(0x2B)
        self.send_data(0x01)

        self.send_command(0x4E) 
        self.send_data(0x00)

        self.send_command(0x4F) 
        self.send_data(0x00)
        self.send_data(0x00)  
        self.ReadBusy()
            
    def EPD_4IN2_V2_Clear(self):
        high = self.height
        if( self.width % 8 == 0) :
            wide =  self.width // 8
        else :
            wide =  self.width // 8 + 1

        self.send_command(0x24)
        for i in range(0, wide):
            self.send_data1([0xff] * high)
                
        self.send_command(0x26)
        for i in range(0, wide):
            self.send_data1([0xff] * high)

        self.TurnOnDisplay()
        
    def EPD_4IN2_V2_Display(self,Image):                
        self.send_command(0x24)
        self.send_data1(Image)

        self.send_command(0x26)
        self.send_data1(Image)

        self.TurnOnDisplay()

    def EPD_4IN2_V2_Display_Fast(self, image):
        self.send_command(0x24)
        self.send_data1(image)

        self.send_command(0x26)
        self.send_data1(image)

        self.TurnOnDisplay_Fast()
        
    def EPD_4IN2_V2_PartialDisplay(self, Image):
        self.send_command(0x3C)  # BorderWavefrom
        self.send_data(0x80)

        self.send_command(0x21)  # Display update control
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x3C)  # BorderWavefrom
        self.send_data(0x80)

        self.send_command(0x44) 
        self.send_data(0x00)
        self.send_data(0x31)  
        
        self.send_command(0x45) 
        self.send_data(0x00)
        self.send_data(0x00)  
        self.send_data(0x2B)
        self.send_data(0x01)

        self.send_command(0x4E) 
        self.send_data(0x00)

        self.send_command(0x4F) 
        self.send_data(0x00)
        self.send_data(0x00) 

        self.send_command(0x24) # WRITE_RAM
        self.send_data1(Image)  
        self.TurnOnDisplay_Partial()

        
    def EPD_4IN2_V2_4GrayDisplay(self,Image):
        self.send_command(0x24)
        for i in range(0, 15000):
            temp3=0
            for j in range(0, 2):
                temp1 = Image[i*2+j]
                for k in range(0, 2):
                    temp2 = temp1&0x03 
                    if(temp2 == 0x03):
                        temp3 |= 0x01   # white
                    elif(temp2 == 0x00):
                        temp3 |= 0x00   # black
                    elif(temp2 == 0x02):
                        temp3 |= 0x01   # gray1
                    else:   # 0x01
                        temp3 |= 0x00   # gray2
                    temp3 <<= 1

                    temp1 >>= 2
                    temp2 = temp1&0x03 
                    if(temp2 == 0x03):   # white
                        temp3 |= 0x01
                    elif(temp2 == 0x00):   # black
                        temp3 |= 0x00
                    elif(temp2 == 0x02):
                        temp3 |= 0x01   # gray1
                    else:   # 0x01
                        temp3 |= 0x00   # gray2
                    
                    if (( j!=1 ) | ( k!=1 )):
                        temp3 <<= 1

                    temp1 >>= 2
            self.send_data(temp3)

        self.send_command(0x26)
        for i in range(0, 15000):
            temp3=0
            for j in range(0, 2):
                temp1 = Image[i*2+j]
                for k in range(0, 2):
                    temp2 = temp1&0x03 
                    if(temp2 == 0x03):
                        temp3 |= 0x01   # white
                    elif(temp2 == 0x00):
                        temp3 |= 0x00   # black
                    elif(temp2 == 0x02):
                        temp3 |= 0x00   # gray1
                    else:   # 0x01
                        temp3 |= 0x01   # gray2
                    temp3 <<= 1

                    temp1 >>= 2
                    temp2 = temp1&0x03
                    if(temp2 == 0x03):   # white
                        temp3 |= 0x01
                    elif(temp2 == 0x00):   # black
                        temp3 |= 0x00
                    elif(temp2 == 0x02):
                        temp3 |= 0x00   # gray1
                    else:   # 0x01
                        temp3 |= 0x01   # gray2
                    
                    if (( j!=1 ) | ( k!=1 )):
                        temp3 <<= 1

                    temp1 >>= 2
            self.send_data(temp3)
        self.TurnOnDisplay_4GRAY()
        
    def Sleep(self):
        self.send_command(0x10)  # DEEP_SLEEP
        self.send_data(0x01)
