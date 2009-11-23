#include "WProgram.h"
#include <enc28j60.h>
#include "Polymer.h"

//Config params- to be revisited
static uint8_t mac[6] = {0x54,0x55,0x58,0x10,0x00,0x24}; 


Polymer polymer = Polymer();


//http://zedcode.blogspot.com/2007/02/gcc-c-link-problems-on-small-embedded.html
//to keep from needing to link to c++ std lib, maybe? not totally sure
// solves this error:
//../../libarduino/libarduinocore.a(Print.o):(.data+0x6): undefined reference to `__cxa_pure_virtual'
extern "C" void __cxa_pure_virtual(void)
{
	// call to a pure virtual function happened ... wow, should never happen ... stop
	for(;;)
	{

	}
}

int main()
{
	init(); // This is the arduino init code
    setup();
    
	for(;;)
	{
        loop();
	}
	return 0;
}


void setup() 
{
	Serial.begin(9600);
	Serial.println("Setup..");
	polymer.init(mac);
	Serial.println("Setup Complete");
}

void loop()
{
	polymer.loop();
}
