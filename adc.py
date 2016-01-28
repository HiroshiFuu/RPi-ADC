import fcntl
import time
import struct

I2C_SLAVE = 0x0703
address = 0b0101000
buf = [0, 0]

#Open I2C bus and acquire access
try:
	f = open("/dev/i2c-1", 'r+b')
	fcntl.ioctl(f, I2C_SLAVE, address)
except Exception as e:
	print e
	exit()

if True:
	cmd = [0b11110100]			# D7 to D4 : CH3 to CH0
								# D3 : REF_SEL (default 0)
								# D2 : FLTR (default 1)
								# D1 : Bit trial delay (default 0)
								# D0 : Sample delay (default 0)
	cmd = bytearray(cmd)
	f.write(cmd)

for i in range(4):
	rb = f.read(2)
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
	data = (float)((buf[0] & 0x0F) << 8) + buf[1]
	#data = data / 4096;
	print "Channel %02d Data: %.2f\n" % (channel + 1, data);
	time.sleep(0.1)
