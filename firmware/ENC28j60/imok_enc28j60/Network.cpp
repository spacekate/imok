/*
  Network.cpp - Network Functions
*/

#include "WProgram.h"
#include "Network.h"
#include "etherShield.h"

Morse::Morse(Ethershield shield)
{
  _shield = shield;
}
void blinkLeds()
{
    /* Magjack leds configuration, see enc28j60 datasheet, page 11 */
    // LEDA=greed LEDB=yellow

    // 0x880 is PHLCON LEDB=on, LEDA=on
    // enc28j60PhyWrite (PHLCON,0b0000 1000 1000 00 00);
    _shield.ES_enc28j60PhyWrite (PHLCON,0x880);
    delay (500);

    // 0x990 is PHLCON LEDB=off, LEDA=off
    // enc28j60PhyWrite (PHLCON,0b0000 1001 1001 00 00);
    _shield.ES_enc28j60PhyWrite (PHLCON,0x990);
    delay (500);

    // 0x880 is PHLCON LEDB=on, LEDA=on
    // enc28j60PhyWrite (PHLCON,0b0000 1000 1000 00 00);
    _shield.ES_enc28j60PhyWrite (PHLCON,0x880);
    delay (500);

    // 0x990 is PHLCON LEDB=off, LEDA=off
    // enc28j60PhyWrite (PHLCON,0b0000 1001 1001 00 00);
    _shield.ES_enc28j60PhyWrite (PHLCON,0x990);
    delay (500);
}

