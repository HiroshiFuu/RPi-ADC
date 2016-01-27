import fcntl
import time
import struct

I2C_SLAVE = 0x0703
address = 0b0101000
buf = [0, 0]

#Open I2C bus and acquire access
try:
	f = open("/dev/i2c-1", 'r')
	fcntl.ioctl(f, I2C_SLAVE, address)
except Exception as e:
	print e
	exit()

for i in range(4):
	rb = f.read(2)
	if len(rb) != 2:
		continue
	res = struct.unpack('H', rb)
	res = int(res[0])
	buf[0] = res & 0x00FF
	buf[1] = res >> 8
	channel = (buf[0] & 0b00110000) >> 4
	data = (float)((buf[0] & 0x0F) << 8) + buf[1]
	print "Channel %02d Data: %04f\n" % (channel + 1, data);
	time.sleep(0.1)
