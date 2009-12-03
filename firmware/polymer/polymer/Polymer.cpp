
extern "C" {
	#include "enc28j60.h"
}
#include "Polymer.h"
#include "net.h"

#define BUFFER_SIZE 500
static uint8_t buf[BUFFER_SIZE+1];

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
    uint16_t plen;
    uint8_t i;
    plen = enc28j60PacketReceive(BUFFER_SIZE, buf);
    if ( plen != 0 )
    {
        handlePacket(plen);
    }	
}

// Private methods below

void Polymer::handlePacket(uint16_t plen){
	if (packetTypeIsARP(plen)){
		handleArpPacket(plen);
	} else {
		Serial.println("Ignored Packet");
	}
}
uint8_t Polymer::packetTypeIsARP(uint16_t plen){
	if (plen<41){
		return(0);
	}
	if(buf[ETH_TYPE_H_P] != ETHTYPE_ARP_H_V || 
	   buf[ETH_TYPE_L_P] != ETHTYPE_ARP_L_V){
		return(0);
	}	
	return (1);
}

void Polymer::handleArpPacket(uint16_t plen){
}

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
