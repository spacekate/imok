
extern "C" {
	#include "enc28j60.h"
}
#include "Polymer.h"

Polymer::Polymer(){	
}

void Polymer::init(uint8_t* mac){
	Serial.println("Polymer::init...");
	enc28j60Init(mac);
	enc28j60clkout(2);
	delay (10);

	blinkEthernetLeds();
	initEthernetLeds();
}

void Polymer::loop(){
}

// Private methods below

void Polymer::initEthernetLeds()
{
  // 0x476 is PHLCON LEDA=links status, LEDB=receive/transmit
  // enc28j60PhyWrite (PHLCON,0b0000 0100 0111 01 10);
  enc28j60PhyWrite (PHLCON,0x476);
  delay (100);  
}
void Polymer::blinkEthernetLeds()
{
  /* Magjack leds configuration, see enc28j60 datasheet, page 11 */
  // LEDA=greed LEDB=yellow
  // 0x880 is PHLCON LEDB=on, LEDA=on
  // 0x990 is PHLCON LEDB=off, LEDA=off

  enc28j60PhyWrite (PHLCON,0x880);
  delay (200);

  enc28j60PhyWrite (PHLCON,0x990);
  delay (200);

  enc28j60PhyWrite (PHLCON,0x880);
  delay (200);

  enc28j60PhyWrite (PHLCON,0x990);
  delay (200);  

  enc28j60PhyWrite (PHLCON,0x880);
  delay (200);

  enc28j60PhyWrite (PHLCON,0x990);
  delay (500);  
}
