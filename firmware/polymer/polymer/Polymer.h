#ifndef Polymer_H
#define Polymer_H

#include "WProgram.h"
#include "enc28j60.h"


class Polymer
{
	public:
		Polymer();
		
		void init(uint8_t* mac);
		void loop();
	private:
		void blinkEthernetLeds();
		void initEthernetLeds();
};
#endif
