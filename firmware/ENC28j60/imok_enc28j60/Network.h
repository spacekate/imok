/*
  Network.h - Class for network functions
*/
#ifndef Network_h
#define Network_h

#include "WProgram.h"
#include "etherShield.h"

class Network
{
  public:
    Network(Ethershield shield);
    void blinkLeds();
  private:
    Ethershield _shield;
};

#endif
