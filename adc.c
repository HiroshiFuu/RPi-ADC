#include <stdio.h>
#include <fcntl.h>			// O_RDWR
#include <stdlib.h>			// exit()
#include <sys/ioctl.h>		// ioctl()
#include <linux/i2c-dev.h>	// I2C_SLAVE
#include <unistd.h>			// read()
#include <errno.h>			// errno

int main(int argc, char **argv)
{	
	int file;
	char *filename = "/dev/i2c-1";
	if ((file = open(filename, O_RDWR)) < 0)
	{
		perror("Failed to open i2c bus");
		exit(-1);
	}
	
	int addr = 0b0101000;
	if (ioctl(file, I2C_SLAVE, addr) < 0)
	{
		perror("Failed to access i2c bus");
		exit(-1);
	}
	
	char cmd[1] = {0};
	cmd[0] = 0b11110100;		// D7 to D4 : CH3 to CH0
								// D3 : REF_SEL (default 0)
								// D2 : FLTR (default 1)
								// D1 : Bit trial delay (default 0)
								// D0 : Sample delay (default 0)
								
	short debug_write = 0;
	if (debug_write == 1)
	{
		if (write(file, cmd, 1) != 1)
		{
			printf("Failed to write to i2c bus\n\n");
		}
	}
	
	char buf[10] = {0};
	float data;
	char channel;
	int i;
	for (i = 0; i < 4; i++)
	{
		if (read(file, buf, 2) != 2)
		{
			printf("Failed to read from i2c bus\n\n");
		}
		else {
			channel = ((buf[0] & 0b00110000) >> 4);
			data = (float)((buf[0] & 0x0F) << 8) + buf[1];
			//10-bit range for AD7991
			//data = data / 4096;
			printf("Channel %02d Data: %04f\n", channel + 1, data);
		}
	}
	
	return 0;
}

