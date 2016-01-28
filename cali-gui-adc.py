import fcntl
import time
import struct
import pygame
from pygame.locals import *
import sys
import Buttons
from math import ceil
import datetime

I2C_SLAVE = 0x0703		# I2C slave address
address = 0b0101000		# I2C device address
f_handler = None		# file handler
buf = [0, 0]			# read buffer

WINDOWWIDTH = 680 # width of the program's window, in pixels
WINDOWHEIGHT = 320 + 20 # height in pixels

#                 R    G    B
WHITE		= 	(255, 255, 255)
BLACK		= 	(  0,   0,   0)
GREEN		= 	(  0, 255,   0)
RED			=	(255, 	0,	 0)

SCREENCOLOR = BLACK
TEXTCOLOR = WHITE
PROMTEXTCOLOR = GREEN
WEIGHTCOLOR = RED

FONT_SIZE_NORMAL = 0
FONT_SIZE_MEDIUM = 1
FONT_SIZE_LARGE = 2

current_step = 0

#Initialize pygame
pygame.init()

class PModAD2:
	
	def __init__(self):
		self.main()
			
	def display(self):
		self.screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
		pygame.display.set_caption('PModAD2 ADC Calibration')
		pygame.font.init()
		
		self.font = pygame.font.Font('freesansbold.ttf', 16)
		self.font_medium = pygame.font.Font('freesansbold.ttf', 24)
		self.font_large = pygame.font.Font('freesansbold.ttf', 32)
		self.ButtonStart = Buttons.Button()
		self.ButtonPrevious = Buttons.Button()
		self.ButtonNext = Buttons.Button()
		self.Exit = Buttons.Button()
		self.data = None
		self.sum_data = 0
		self.measure_count = 0
		self.overall_data = [[None, None], [None, None], [None, None], [None, None]]
		
	def update_display(self):
		global selected_mode, voltage_range, resistance_range
		global current_step
		
		self.screen.fill(SCREENCOLOR)
		
		if current_step == 0:
			self.ButtonStart.create_button(self.screen, (212,154,0), 20, 300, 80, 30, 18, "Start", (255,255,255))
		else:
			self.ButtonStart.create_button(self.screen, (212,154,0), 20, 300, 80, 30, 18, "Re-Start", (255,255,255))
			if current_step != 8:
				self.ButtonNext.create_button(self.screen, (87,160,70), 120, 300, 80, 30, 18, "Next", (255,255,255))
			else:
				self.ButtonNext.create_button(self.screen, (87,160,70), 120, 300, 80, 30, 18, "Finish", (255,255,255))
			if current_step > 1:
				self.ButtonPrevious.create_button(self.screen, (30,30,254), 220, 300, 80, 30, 18, "Previous", (255,255,255))
		self.Exit.create_button(self.screen, (254,63,30), 600, 300, 60, 30, 20, "Exit", (255,255,255))
		
		self.drawText("ADC Calibration", 240, 10, FONT_SIZE_LARGE)
				
		if current_step != 0:
			self.drawText("501g Cali Point : ", 10, 130)
			self.drawText("900g Cali Point : ", 10, 150)
		# Channel 1
		if current_step >= 1:
			self.drawText("Channel 1", 140, 110)
		if current_step == 1:
			self.drawText("Please place the ", 20, 50, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.drawText("501g", 220, 50, FONT_SIZE_MEDIUM, WEIGHTCOLOR)
			self.drawText("weight on the 1st loadcell", 280, 50, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.drawText("Then press Next button to get data sensor 1", 20, 80, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.drawText("501g", 540, 80, FONT_SIZE_MEDIUM, WEIGHTCOLOR)
			self.drawText("point", 600, 80, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.readI2C()
			self.sum_data += self.data
			self.measure_count += 1
			self.overall_data[0][0] = self.sum_data / self.measure_count
		if current_step >= 1:
			self.drawText(str(self.overall_data[0][0]), 160, 130)
		if current_step == 2:
			self.drawText("Please place the ", 20, 50, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.drawText("900g", 220, 50, FONT_SIZE_MEDIUM, WEIGHTCOLOR)
			self.drawText("weight on the 1st loadcell", 280, 50, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.drawText("Then press Next button to get data sensor 1", 20, 80, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.drawText("900g", 540, 80, FONT_SIZE_MEDIUM, WEIGHTCOLOR)
			self.drawText("point", 600, 80, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.readI2C()
			self.sum_data += self.data
			self.measure_count += 1
			self.overall_data[0][1] = self.sum_data / self.measure_count
		if current_step >= 2:
			self.drawText(str(self.overall_data[0][1]), 160, 150)
		# Channel 2
		if current_step >= 3:
			self.drawText("Channel 2", 240, 110)
		if current_step == 3:
			self.drawText("Please place the ", 20, 50, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.drawText("501g", 220, 50, FONT_SIZE_MEDIUM, WEIGHTCOLOR)
			self.drawText("weight on the 2nd loadcell", 280, 50, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.drawText("Then press Next button to get data sensor 2", 20, 80, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.drawText("501g", 540, 80, FONT_SIZE_MEDIUM, WEIGHTCOLOR)
			self.drawText("point", 600, 80, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.readI2C()
			self.sum_data += self.data
			self.measure_count += 1
			self.overall_data[1][0] = self.sum_data / self.measure_count
		if current_step >= 3:
			self.drawText(str(self.overall_data[1][0]), 260, 130)
		if current_step == 4:
			self.drawText("Please place the ", 20, 50, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.drawText("900g", 220, 50, FONT_SIZE_MEDIUM, WEIGHTCOLOR)
			self.drawText("weight on the 2nd loadcell", 280, 50, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.drawText("Then press Next button to get data sensor 2", 20, 80, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.drawText("900g", 540, 80, FONT_SIZE_MEDIUM, WEIGHTCOLOR)
			self.drawText("point", 600, 80, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.readI2C()
			self.sum_data += self.data
			self.measure_count += 1
			self.overall_data[1][1] = self.sum_data / self.measure_count
		if current_step >= 4:
			self.drawText(str(self.overall_data[1][1]), 260, 150)
		# Channel 3
		if current_step >= 5:
			self.drawText("Channel 3", 340, 110)
		if current_step == 5:
			self.drawText("Please place the ", 20, 50, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.drawText("501g", 220, 50, FONT_SIZE_MEDIUM, WEIGHTCOLOR)
			self.drawText("weight on the 3rd loadcell", 280, 50, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.drawText("Then press Next button to get data sensor 3", 20, 80, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.drawText("501g", 540, 80, FONT_SIZE_MEDIUM, WEIGHTCOLOR)
			self.drawText("point", 600, 80, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.readI2C()
			self.sum_data += self.data
			self.measure_count += 1
			self.overall_data[2][0] = self.sum_data / self.measure_count
		if current_step >= 5:
			self.drawText(str(self.overall_data[2][0]), 360, 130)
		if current_step == 6:
			self.drawText("Please place the ", 20, 50, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.drawText("900g", 220, 50, FONT_SIZE_MEDIUM, WEIGHTCOLOR)
			self.drawText("weight on the 3rd loadcell", 280, 50, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.drawText("Then press Next button to get data sensor 3", 20, 80, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.drawText("900g", 540, 80, FONT_SIZE_MEDIUM, WEIGHTCOLOR)
			self.drawText("point", 600, 80, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.readI2C()
			self.sum_data += self.data
			self.measure_count += 1
			self.overall_data[2][1] = self.sum_data / self.measure_count
		if current_step >= 6:
			self.drawText(str(self.overall_data[2][1]), 360, 150)
		# Channel 4
		if current_step >= 7:
			self.drawText("Channel 4", 440, 110)
		if current_step == 7:
			self.drawText("Please place the ", 20, 50, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.drawText("501g", 220, 50, FONT_SIZE_MEDIUM, WEIGHTCOLOR)
			self.drawText("weight on the 4th loadcell", 280, 50, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.drawText("Then press Next button to get data sensor 4", 20, 80, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.drawText("501g", 540, 80, FONT_SIZE_MEDIUM, WEIGHTCOLOR)
			self.drawText("point", 600, 80, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.readI2C()
			self.sum_data += self.data
			self.measure_count += 1
			self.overall_data[3][0] = self.sum_data / self.measure_count
		if current_step >= 7:
			self.drawText(str(self.overall_data[3][0]), 460, 130)
		if current_step == 8:
			self.drawText("Please place the ", 20, 50, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.drawText("900g", 220, 50, FONT_SIZE_MEDIUM, WEIGHTCOLOR)
			self.drawText("weight on the 4th loadcell", 280, 50, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.drawText("Then press Next button to get data sensor 4", 20, 80, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.drawText("900g", 540, 80, FONT_SIZE_MEDIUM, WEIGHTCOLOR)
			self.drawText("point", 600, 80, FONT_SIZE_MEDIUM, PROMTEXTCOLOR)
			self.readI2C()
			self.sum_data += self.data
			self.measure_count += 1
			self.overall_data[3][1] = self.sum_data / self.measure_count
		if current_step >= 8:
			self.drawText(str(self.overall_data[3][1]), 460, 150)
					
		pygame.display.update()
		
	def drawText(self, text, x, y, size=FONT_SIZE_NORMAL, color=TEXTCOLOR):
		if size == FONT_SIZE_NORMAL:
			text = self.font.render(text, 1, color)
		if size == FONT_SIZE_MEDIUM:
			text = self.font_medium.render(text, 1, color)
		if size == FONT_SIZE_LARGE:
			text = self.font_large.render(text, 1, color)
		self.screen.blit(text, (x, y))
			
	def checkForEvent(self):
		global selected_mode, current_step
		
		for event in pygame.event.get(): # event handling loop
			if event.type == pygame.QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEBUTTONDOWN:
				if self.Exit.pressed(pygame.mouse.get_pos()):
					pygame.quit()
					sys.exit()
				elif self.ButtonStart.pressed(pygame.mouse.get_pos()):
					self.sum_data = 0
					self.measure_count = 0
					current_step = 1
					self.setChannelRead(1)
				elif current_step != 0:
					if current_step > 1:
						if self.ButtonPrevious.pressed(pygame.mouse.get_pos()):
							self.sum_data = 0
							self.measure_count = 0
							current_step -= 1
							self.setChannelRead(int(ceil(current_step / 2.0)))
					if self.ButtonNext.pressed(pygame.mouse.get_pos()):
						self.sum_data = 0
						self.measure_count = 0
						current_step += 1
						if current_step == 9:
							current_step = 0
							self.writeConfig()
						else:
							self.setChannelRead(int(ceil(current_step / 2.0)))
	
	def openI2C(self):
		global f_handler, I2C_SLAVE, address
		
		#Open I2C bus and acquire access
		try:
			f_handler = open("/dev/i2c-1", 'r+b')
			fcntl.ioctl(f_handler, I2C_SLAVE, address)
		except Exception as e:
			print e
			pygame.quit()
			sys.exit()
			
	# channel : 1 to 4 for channel 1 to 4
	# channel : 0 for all channels
	def setChannelRead(self, channel):
		global f_handler
		
		self.openI2C()
				
		# D7 to D4 : CH3 to CH0
		# D3 : REF_SEL (default 0)
		# D2 : FLTR (default 1)
		# D1 : Bit trial delay (default 0)
		# D0 : Sample delay (default 0)
		cmd = [0b00000100]	
		
		if channel == 0:
			mask = 0b11110000;
		else:
			mask = 0b00001000 << channel
		cmd[0] |= mask
		cmd = bytearray(cmd)
		f_handler.write(cmd)
		time.sleep(0.1)
		
	def readI2C(self):
		global f_handler, buf
		
		self.openI2C()
		
		#Open I2C bus and acquire access
		try:
			f_handler = open("/dev/i2c-1", 'r')
			fcntl.ioctl(f_handler, I2C_SLAVE, address)
		except Exception as e:
			print e
			pygame.quit()
			sys.exit()
		
		rb = f_handler.read(2)
		if len(rb) != 2:
			return
		#unpack the binary stream, 'H' for unsigned short
		res = struct.unpack('H', rb)
		res = int(res[0])
		buf[0] = res & 0x00FF
		buf[1] = res >> 8
		
		#Frame 1 
		#bit 6 - CH id 1
		#bit 5 - CH id 0
		#bit 2:1 - Data bit 10:9
		#channel = (buf[0] & 0b00110000) >> 4
		#Frame 12
		#bit 8:1 - Data bit 8:1
		self.data = ((buf[0] & 0x0F) << 8) + buf[1]
			
	def writeConfig(self):
		cali_file = open(datetime.datetime.now().strftime("Cali %Y-%m-%d %H-%M-%S.txt"), 'w')
		for i in range(4):
			cali_file.write("[Channel " + str(i + 1) + "]\n")
			cali_file.write("RawVal501Pt=" + str(self.overall_data[i][0]) + "\n")
			cali_file.write("RawVal900Pt=" + str(self.overall_data[i][1]) + "\n")
			cali_file.write("\n")
		cali_file.close()
		self.updateConfig()
		
	def updateConfig(self):
		config_file = open("./config.txt", 'rw+')
		lines = []
		for i in range(7):
			lines.append(config_file.next())
		config_file.seek(0)
		for i in range(7):
			if i == 1:
				config_file.write("DateCali=" + datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + "\n")
			else:
				config_file.write(lines[i])
		config_file.close()
			
		
	def main(self):
		self.display()
		clock = pygame.time.Clock()
		while True:
			clock.tick(6)
			self.update_display()
			self.checkForEvent()

if __name__ == '__main__':
	obj = PModAD2()

