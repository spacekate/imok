#include <Ethernet.h>
#include "Dhcp.h"
#include <string.h>
#include <Wire.h>

#define EPROM_ADDRESS (0x50)
#define MAC_LOCATION (0xFA)

const int buttonPin = 2;     // the number of the pushbutton pin

// Variables will change:
int buttonState;             // the current reading from the input pin
int lastButtonState = LOW;   // the previous reading from the input pin
int sending=0;

// the following variables are long's because the time, measured in miliseconds,
// will quickly become a bigger number than can be stored in an int.
long lastconnectionTime = 0;  // the last time the output pin was toggled
long connectionTimeout = 5000;    // the debounce time; increase if the output flickers


byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
byte serverIp[] = { 10, 1, 1, 2 };
char serverName[] = "localhost";

boolean ipAcquired = false;

Client client(serverIp, 8080);

void setup()
{
  Serial.begin(9600);
  Serial.println("getting mac...");
  setMac();
  Serial.println("getting ip...");
  int result = Dhcp.beginWithDHCP(mac);

  pinMode(buttonPin, INPUT); 
  
  if(result == 1)
  {
    ipAcquired = true;
    printDhcpResults();
    delay(3000);
    doGet();
  }
  else
    Serial.println("unable to acquire ip address...");
}

void printArray(Print *output, char* delimeter, byte* data, int len, int base)
{
  char buf[10] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
  
  for(int i = 0; i < len; i++)
  {
    if(i != 0)
      output->print(delimeter);
      
    output->print(itoa(data[i], buf, base));
  }
  
  output->println();
}

void loop()
{
  if(ipAcquired && sending)
  {
    if (client.available()) {
      char c = client.read();
      Serial.print(c);
    }

    if (!client.connected()) {
      Serial.println();
      Serial.println("disconnecting.");
      client.stop();
      sending=0;
    }
  }
  // read the state of the switch into a local variable:
  int reading = digitalRead(buttonPin);
  //Serial.print("reading=");
  //Serial.println(reading);
  
  if (reading != lastButtonState) {
      lastButtonState = reading;
      if (millis() - lastconnectionTime > connectionTimeout){
        doGet();
      }
      lastconnectionTime = millis();
  } //else{
    //Serial.println("same");
  //}
  //delay(300);
}

void doGet(){
    byte buffer[6];
    Dhcp.getMacAddress(buffer);
    Serial.println("connecting...");

    if (client.connect()) {
      sending=1;
      Serial.println("connected");
      client.print("GET /notification/?vendorId=button&deviceId=");
      printArray(&client, ":", buffer, 6, 16);
      client.println(" HTTP/1.1");
      client.print("Host: ");
      client.println(serverName);
      client.println();
    } else {
      sending=0;
      Serial.println("connection failed");
    }
}

void setMac(){
  Wire.begin();        // join i2c bus (address optional for master)
  //Serial.println("Setting Mac..");

  
  //  Send input register address
  Wire.beginTransmission(EPROM_ADDRESS);
  Wire.send(MAC_LOCATION);
  Wire.endTransmission();
  
  Wire.requestFrom(EPROM_ADDRESS, 6);    // request 6 bytes from slave device 
  

  for(int i = 0; i < 6; i++)
  {
    if(i != 0){
      Serial.print(":");
    }
    byte b = 0;
    if (Wire.available()){
      b = Wire.receive(); // receive a byte as character
    }
    mac[i] = b;
    //Serial.print(b, HEX);
         
  }  
  //Serial.println("");
  //Serial.println("MAC set..");
  
}

void printDhcpResults()
{
    byte buffer[6];
    Serial.println("ip acquired...");
    
    Dhcp.getMacAddress(buffer);
    Serial.print("mac address: ");
    printArray(&Serial, ":", buffer, 6, 16);
    
    Dhcp.getLocalIp(buffer);
    Serial.print("ip address: ");
    printArray(&Serial, ".", buffer, 4, 10);
    
    Dhcp.getSubnetMask(buffer);
    Serial.print("subnet mask: ");
    printArray(&Serial, ".", buffer, 4, 10);
    
    Dhcp.getGatewayIp(buffer);
    Serial.print("gateway ip: ");
    printArray(&Serial, ".", buffer, 4, 10);
    
    Dhcp.getDhcpServerIp(buffer);
    Serial.print("dhcp server ip: ");
    printArray(&Serial, ".", buffer, 4, 10);
    
    Dhcp.getDnsServerIp(buffer);
    Serial.print("dns server ip: ");
    printArray(&Serial, ".", buffer, 4, 10);  
}
