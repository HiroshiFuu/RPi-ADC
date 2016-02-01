import fcntl
import time
import struct
import pygame
from pygame.locals import *
import sys
import Buttons
import PygButton
import PygInputBox

I2C_SLAVE = 0x0703		# I2C slave address
address = 0b0101000		# I2C device address
f_handler = None		# file handler
buf = [0, 0]			# read buffer

WINDOWWIDTH = 480 # width of the program's window, in pixels
WINDOWHEIGHT = 320 + 40 # height in pixels

#                 R    G    B
WHITE		= 	(255, 255, 255)
BLACK		= 	(  0,   0,   0)
GREEN		= 	(  0, 255,   0)
RED			=	(255, 	0,	 0)

SCREENCOLOR = BLACK
TEXTCOLOR = WHITE

selected_mode = 0
voltage_range = 5
resistance_range = 50000

#Initialize pygame
pygame.init()

class PModAD2:
	
	def __init__(self):
		self.main()
			
	def display(self):
		self.screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
		pygame.display.set_caption('PModAD2 ADC')
		pygame.font.init()
		
		self.font = pygame.font.Font('freesansbold.ttf', 16)
		self.ButtonRaw = Buttons.Button()
		self.ButtonPercentage = Buttons.Button()
		self.ButtonVoltage = Buttons.Button()
		self.ButtonResistance = Buttons.Button()
		self.Exit = Buttons.Button()
		self.data = [None, None, None, None]
		
		self.CaliDate = None
		self.VeriDate = None
		self.MaxErr = None
		
		self.ButtonSetErr = PygButton.PygButton((230, 210, 45, 25), 'Set', WHITE)
		self.ErrInputBox = PygInputBox.PygInputBox((160, 208, 50, 30), 'Error', WHITE)
		
	def update_display(self):
		global selected_mode, voltage_range, resistance_range
		
		self.screen.fill(SCREENCOLOR)
		
		self.ButtonRaw.create_button(self.screen, (65,65,65), 10, 300, 80, 30, 18, "Raw Value", (255,255,255))
		self.ButtonPercentage.create_button(self.screen, (87,160,70), 100, 300, 80, 30, 18, "Percentage", (255,255,255))
		self.ButtonVoltage.create_button(self.screen, (30,30,254), 190, 300, 80, 30, 18, "Voltage", (255,255,255))
		self.ButtonResistance.create_button(self.screen, (212,154,0), 280, 300, 80, 30, 18, "Resistance", (255,255,255))
		self.Exit.create_button(self.screen, (254,63,30), 400, 300, 60, 30, 20, "Exit", (255,255,255))
		
		self.drawText("Last Calibration Date  :  " + self.CaliDate, 10, 160)
		self.drawText("Last Verification Date :  " + self.VeriDate, 10, 180)
		self.drawText("Max Error Allow :  ", 10, 212)
		self.ButtonSetErr.draw(self.screen)
		self.ErrInputBox.draw(self.screen)
		
		self.readI2C();
		for i in range(4):
			self.drawText("Channel " + str(i + 1) + " : ", 10, 20 + 30 * i)
			if selected_mode == 0:
				self.drawText(str(self.data[i]), 100, 20 + 30 * i)
				self.drawText('', 150, 20 + 30 * i)
			elif selected_mode == 1:
				data = self.data[i] / 4095.0 * 100
				text = "{0:.3f}".format(round(data, 3))
				self.drawText(text, 100, 20 + 30 * i)
				if data > 10:
					self.drawText('%', 150, 20 + 30 * i)
				else:
					self.drawText('%', 140, 20 + 30 * i)
			elif selected_mode == 2:
				text = "{0:.4f}".format(round(self.data[i] / 4095.0 * voltage_range, 4))
				self.drawText(text, 100, 20 + 30 * i)
				self.drawText('V', 150, 20 + 30 * i)
			elif selected_mode == 3:
				data = self.data[i] / 4095.0 * resistance_range
				if data < 10000:
					text = "{0:.1f}".format(round(data, 1))
					self.drawText(text, 100, 20 + 30 * i)
					if data == 0:
						self.drawText(u'\u03A9', 125, 20 + 30 * i)
					else:
						self.drawText(u'\u03A9', 150, 20 + 30 * i)
				else:
					text = "{0:.4f}".format(round(data / 1000, 4))
					self.drawText(text, 100, 20 + 30 * i)
					self.drawText('k' + u'\u03A9', 160, 20 + 30 * i)
					
		pygame.display.update()
		
	def drawText(self, text, x, y, color=TEXTCOLOR):
		text = self.font.render(text, 1, color)
		self.screen.blit(text, (x, y))
			
	def checkForEvent(self):
		global selected_mode
		
		for event in pygame.event.get(): # event handling loop
			if event.type == pygame.QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEBUTTONDOWN:
				if self.Exit.pressed(pygame.mouse.get_pos()):
					pygame.quit()
					sys.exit()
				elif self.ButtonRaw.pressed(pygame.mouse.get_pos()):
					selected_mode = 0
				elif self.ButtonPercentage.pressed(pygame.mouse.get_pos()):
					selected_mode = 1
				elif self.ButtonVoltage.pressed(pygame.mouse.get_pos()):
					selected_mode = 2
				elif self.ButtonResistance.pressed(pygame.mouse.get_pos()):
					selected_mode = 3
			elif event.type == MOUSEBUTTONUP:	
				if 'click' in self.ErrInputBox.handleMouseEvent(event):
					pass
			elif event.type == KEYUP:
				self.ErrInputBox.handleKeyEvent(event)
	
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
		
		for i in range(4):
			rb = f_handler.read(2)
			if len(rb) != 2:
				continue
			#unpack the binary stream, 'H' for unsigned short
			res = struct.unpack('H', rb)
			res = int(res[0])
			buf[0] = res & 0x00FF
			buf[1] = res >> 8
			
			#Frame 1 
			#bit 6 - CH id 1
			#bit 5 - CH id 0
			#bit 2:1 - Data bit 10:9
			channel = (buf[0] & 0b00110000) >> 4
			#Frame 12
			#bit 8:1 - Data bit 8:1
			self.data[channel] = ((buf[0] & 0x0F) << 8) + buf[1]
			#data = data / 4095;
			#print "Channel %02d Data: %.2f\n" % (channel + 1, data);
				
	def loadConfig(self):			
		config_file = open("./config.txt", 'r')
		lines = []
		for i in range(7):
			lines.append(config_file.next())
		self.CaliDate = lines[1].replace("DateCali=", "").replace("\n", "")
		self.VeriDate = lines[2].replace("DateVeri=", "").replace("\n", "")
		config_file.close()
	
	def main(self):
		self.display()
		clock = pygame.time.Clock()
		self.setChannelRead(0)
		self.loadConfig()
		while True:
			clock.tick(3)
			self.update_display()
			self.checkForEvent()

if __name__ == '__main__':
	obj = PModAD2()

