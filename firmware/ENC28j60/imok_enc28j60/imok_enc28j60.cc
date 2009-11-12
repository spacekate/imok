#include "WProgram.h"
#include <etherShield.h>


static uint8_t myMac[6] = {0x54,0x55,0x58,0x10,0x00,0x24}; 
static uint8_t myIp[4] = {10,1,1,55};

// server settings - modify the service ip to your own server
static uint8_t destIp[4] = {10,1,1,3};
static uint8_t destMac[6];
static uint16_t destPort = 8080;

#define BUFFER_SIZE 500
static uint8_t buf[BUFFER_SIZE+1];

enum CLIENT_STATE
{
  IDLE, ARP_SENT, ARP_REPLY, SYNC_SENT, SYNC_REPLY, DATA_SENT
};
static CLIENT_STATE client_state;
static uint8_t syn_ack_timeout = 0;
static unsigned long actionPump = 0;

EtherShield es = EtherShield();
static uint8_t makeConection;



//after build -- to flash
//avr-objcopy -O ihex -R .eeprom blink.out blink.hex
//sudo avrdude -V -c dragon_isp -p m168 -b 19200 -P usb -U flash:w:cmaketest.hex

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
	init();
    setup();
    
	for(;;)
	{
        loop();
	}
	return 0;
}


void closeConnection()
{
    uint16_t plen;
      plen = es.ES_tcp_get_dlength ( (uint8_t*)&buf );

      // send ACK to answer PSHACK from server
      es.ES_tcp_client_send_packet (
        buf,
        destPort,                 // destination port
        1200,               // source port
        TCP_FLAG_ACK_V,     // flag
        0,                  // (bool)maximum segment size
        0,                  // (bool)clear sequence ack number
        plen,               // 0=use old seq, seqack : 1=new seq,seqack no data : >1 new seq,seqack with data
        0,                  // tcp data length
        destMac,
        destIp
      );

      // send finack to disconnect from web server
      es.ES_tcp_client_send_packet (
        buf,
        destPort,                               // destination port
        1200,                             // source port
        TCP_FLAG_FIN_V|TCP_FLAG_ACK_V,    // flag
        0,                                // (bool)maximum segment size
        0,                                // (bool)clear sequence ack number
        0,                                // 0=use old seq, seqack : 1=new seq,seqack no data : >1 new seq,seqack with data
        0,
        destMac,
        destIp
      );
}

uint16_t gen_client_request (uint8_t *buf )

{
  uint16_t plen;
  byte i;

  plen = es.ES_fill_tcp_data_p (buf, 0, PSTR ( "GET /device/" ) );
/*  plen = es.ES_fill_tcp_data_p (buf, 0, PSTR ( "GET /ethershield_log/save.php?pwd=secret&client=" ) );
  for (i = 0; client_ip[i] != '\0'; i++) {
    buf[TCP_DATA_P+plen] = client_ip[i];
    plen++;
  }
  plen = es.ES_fill_tcp_data_p (buf, plen, PSTR ( "&status=temperature-" ) );
  for (i = 0; sensorData[i] != '\0'; i++) {
    buf[TCP_DATA_P+plen]=sensorData[i];
    plen++;
  }*/

  plen = es.ES_fill_tcp_data_p (buf, plen, PSTR ( " HTTP/1.0\r\n" ));
  plen = es.ES_fill_tcp_data_p (buf, plen, PSTR ( "Host: 10.1.1.3\r\n" ));
  plen = es.ES_fill_tcp_data_p (buf, plen, PSTR ( "User-Agent: AVR ethernet\r\n" ));
  plen = es.ES_fill_tcp_data_p (buf, plen, PSTR ( "Accept: text/html\r\n" ));
  plen = es.ES_fill_tcp_data_p (buf, plen, PSTR ( "Keep-Alive: 300\r\n" ));
  plen = es.ES_fill_tcp_data_p (buf, plen, PSTR ( "Connection: keep-alive\r\n\r\n" ));

  return plen;
}

void sendData()
{
    uint16_t plen;

    Serial.println("Send Data");
    // check SYNACK flag, after AVR send SYN server response by send SYNACK to AVR
    if (buf[TCP_FLAGS_P] == (TCP_FLAG_SYN_V | TCP_FLAG_ACK_V))
    {
      // send ACK to answer SYNACK
      es.ES_tcp_client_send_packet (
        buf,
        destPort,
        1200,
        TCP_FLAG_ACK_V,      // flag
        0,                   // (bool)maximum segment size
        0,                   // (bool)clear sequence ack number
        1,                   // 0=use old seq, seqack : 1=new seq,seqack no data : new seq,seqack with data
        0,                   // tcp data length
        destMac,
        destIp
      );

      // setup http request to server
      plen = gen_client_request (buf);
      // send http request packet
      // send packet with PSHACK

      es.ES_tcp_client_send_packet (
        buf,
        destPort,                                 // destination port
        1200,                               // source port
        TCP_FLAG_ACK_V | TCP_FLAG_PUSH_V,   // flag
        0,                                  // (bool)maximum segment size
        0,                                  // (bool)clear sequence ack number
        0,                                  // 0=use old seq, seqack : 1=new seq,seqack no data : >1 new seq,seqack with data
        plen,                               // tcp data length
        destMac,
        destIp
      );
    }
}
void sendSync()
{
    Serial.println("Send Sync");
    es.ES_tcp_client_send_packet (
        buf,
        destPort,
        1200,
        TCP_FLAG_SYN_V,     // flag
        1,                  // (bool)maximum segment size
        1,                  // (bool)clear sequence ack number
        0,                  // 0=use old seq, seqack : 1=new seq,seqack no data : new seq,seqack with data
        0,                  // tcp data length
        destMac,
        destIp
    );  
}
void startConnection()
{
  if (client_state == IDLE) {   // initialize ARP
    Serial.println("Start Connection");
    es.ES_make_arp_request (buf, destIp);
    client_state = ARP_SENT;
    return;
  }
} 

void printState()
{
  // IDLE, ARP_SENT, ARP_REPLY, SYNC_SENT, SYNC_REPLY, DATA_SENT
  if (client_state==IDLE) {
    Serial.print("IDLE");
  } else if (client_state==ARP_SENT) {
    Serial.print("ARP_SENT");
  } else if (client_state==ARP_REPLY) {
    Serial.print("ARP_REPLY");
  } else if (client_state==SYNC_SENT) {
    Serial.print("SYNC_SENT");
  } else if (client_state==SYNC_REPLY) {
    Serial.print("SYNC_REPLY");
  } else if (client_state==DATA_SENT) {
    Serial.print("DATA_SENT");
  } else {
    Serial.print("unknown");
  }
  Serial.println("");
}
void printSequence(uint8_t *buf, char* label, uint8_t start, uint8_t printMode, uint8_t seqLen)
{
    uint8_t i=0;
    Serial.print(label);
    Serial.print(": ");
    i=0;
    while(i<seqLen){
       Serial.print(buf[start+i], printMode);
       Serial.print(", ");
       i++;
   }
   Serial.println("");
}
void printPacket(uint8_t *buf,uint16_t len)
{
    uint8_t i=0;
    Serial.println("Packet:");

    if (len<41){
        Serial.println("--> Shorter than 41");
        return;
    }  

    //printSequence(buf, "----> Destination Mac", ETH_DST_MAC, HEX, 6);
    //printSequence(buf, "----> Source Mac", ETH_SRC_MAC, HEX, 6);

    Serial.print("--> Type: ");
    if(buf[ETH_TYPE_H_P] == ETHTYPE_ARP_H_V  &&
      buf[ETH_TYPE_L_P] == ETHTYPE_ARP_L_V){
        Serial.println("ARP");
        printSequence(buf, "----> Src Mac", ETH_ARP_SRC_MAC_P, HEX, 6);
        printSequence(buf, "----> Src IP", ETH_ARP_SRC_IP_P, DEC, 4);
        printSequence(buf, "----> Dst Mac", ETH_ARP_DST_MAC_P, HEX, 6);
        printSequence(buf, "----> Dst IP", ETH_ARP_DST_IP_P, DEC, 4);

    } else if(buf[ETH_TYPE_H_P] == ETHTYPE_IP_H_V  &&
      buf[ETH_TYPE_L_P] == ETHTYPE_IP_L_V){
        Serial.println("IP");
        //printSequence(buf, "----> Src IP", IP_SRC_P, DEC, 4);  
        //printSequence(buf, "----> Dst IP", IP_DST_P, DEC, 4); 
        Serial.print("TCP Flags: "); Serial.println(buf[TCP_FLAGS_P], HEX);
    } else {
        Serial.print("--> Unknown (");
        Serial.print(buf[ETH_TYPE_H_P], HEX);
        Serial.print(", ");
        Serial.print(buf[ETH_TYPE_L_P], HEX);
        Serial.println(")");
    }
    
    
    
    Serial.println("------------------");
}

void initEthernetLeds()
{
  // 0x476 is PHLCON LEDA=links status, LEDB=receive/transmit
  // enc28j60PhyWrite (PHLCON,0b0000 0100 0111 01 10);
  es.ES_enc28j60PhyWrite (PHLCON,0x476);
  delay (100);  
}
void blinkEthernetLeds()
{
  /* Magjack leds configuration, see enc28j60 datasheet, page 11 */
  // LEDA=greed LEDB=yellow

  // 0x880 is PHLCON LEDB=on, LEDA=on
  // enc28j60PhyWrite (PHLCON,0b0000 1000 1000 00 00);
  es.ES_enc28j60PhyWrite (PHLCON,0x880);
  delay (500);

  // 0x990 is PHLCON LEDB=off, LEDA=off
  // enc28j60PhyWrite (PHLCON,0b0000 1001 1001 00 00);
  es.ES_enc28j60PhyWrite (PHLCON,0x990);
  delay (500);

  // 0x880 is PHLCON LEDB=on, LEDA=on
  // enc28j60PhyWrite (PHLCON,0b0000 1000 1000 00 00);
  es.ES_enc28j60PhyWrite (PHLCON,0x880);
  delay (500);

  // 0x990 is PHLCON LEDB=off, LEDA=off
  // enc28j60PhyWrite (PHLCON,0b0000 1001 1001 00 00);
  es.ES_enc28j60PhyWrite (PHLCON,0x990);
  delay (500);  
}

void handlePacket(uint16_t plen)
{
    uint8_t i;
    if (es.ES_arp_packet_is_myreply_arp (buf)) 
    {
        Serial.println("ARP Reply");
        printSequence(buf, "Server Mac", ETH_SRC_MAC, HEX, 6);
        for (i = 0; i < 6; i++) {
          destMac[i] = buf[ETH_SRC_MAC+i];
        }
        client_state = ARP_REPLY;
        syn_ack_timeout=0;
        return;
    }
    // Other ARP request.
    if(es.ES_eth_type_is_arp_and_my_ip(buf,plen))
    {
        Serial.println("ARP Request");
        //printPacket(buf, plen);        
        es.ES_make_arp_answer_from_request(buf);
        Serial.println("ARP Response sent");
        return;
    }
    if (client_state == SYNC_SENT && es.ES_eth_type_is_ip_and_my_ip(buf,plen) != 0)
    { 
        if (buf[TCP_FLAGS_P] == (TCP_FLAG_RST_V | TCP_FLAG_ACK_V))
        {
          Serial.println("Syn RST - setting state back to idle ");
          client_state=IDLE;
          return;
        }
        if (buf[TCP_FLAGS_P] == (TCP_FLAG_SYN_V | TCP_FLAG_ACK_V))
        {
          Serial.println("Syn AcK ");
          client_state=SYNC_REPLY;
          return;
        }
        // Fall through to ignore packet
    }
    if (client_state == DATA_SENT) 
    {
        // after AVR send http request to server, server response by send data with PSHACK to AVR
        // AVR answer by send ACK and FINACK to server
        if (buf [ TCP_FLAGS_P ] == (TCP_FLAG_ACK_V|TCP_FLAG_PUSH_V))
        {
          Serial.println("Closing Conenction");
          closeConnection();
          client_state=IDLE;
          return;
        }
        // Fall through to Ignore Packet
    }
    Serial.print("Packet Ignored.. State: "); 
    printState();
    printPacket(buf, plen);
}

void setup() 
{
  Serial.begin(9600);
  es.ES_enc28j60Init (myMac);
  es.ES_enc28j60clkout (2); // change clkout from 6.25MHz to 12.5MHz
  delay (10);

  blinkEthernetLeds();
  initEthernetLeds();
  
  //init the ethernet/ip layer:
  es.ES_init_ip_arp_udp_tcp (myMac,myIp,8080);
  client_state=IDLE;
  makeConection=1;
  actionPump=millis();
  Serial.println("Setup Complete");

}

void loop()
{
    uint16_t plen;
    uint8_t i;
    plen = es.ES_enc28j60PacketReceive (BUFFER_SIZE, buf);
    if ( plen != 0 )
    {
        handlePacket(plen);
    }
    if (makeConection != 0 && client_state==IDLE)
    {
      startConnection();
      makeConection=0;
    } 
    if (client_state==ARP_REPLY)
    {
        Serial.println("Sending Sync");
        sendSync();
        client_state = SYNC_SENT;
        return;
    } 
    if (client_state==SYNC_REPLY)
    {
      sendData();
      client_state = DATA_SENT;
    }

    unsigned long now = millis();
    if ((now - actionPump) >= 20000)
    {
        Serial.println("ActionPump");
        makeConection=1;
        actionPump = now;
        client_state = IDLE;
      
    }
}
