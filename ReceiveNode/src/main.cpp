
#include <RHReliableDatagram.h>
//#include <RHDatagram.h>
#include <RH_RF95.h>
#include <SPI.h>

#define PORTABLE_ADDRESS 1 //Portable node
#define NODEA 2            //esp1 (self)
#define NODEB 3            //esp2 (self)
#define NODEC 4            //raspberry pi

#define NSS 5
#define DIO0 26
RH_RF95 driver(NSS, DIO0);

RHReliableDatagram manager(driver, NODEA); //change this on upload


void setup()
{
  Serial.begin(115200);
  while (!Serial)
    ; // Wait for serial port to be available
  if (!manager.init())
    Serial.println("init failed");
  //    if (!manager2.init())
  //        Serial.println("init 2 failed");
  driver.setFrequency(900);
  driver.setTxPower(23, false);
}

uint8_t data[] = "Loc Node";
uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];

void loop()
{
  // Serial.println("working");
  uint8_t len = sizeof(buf);
  uint8_t from;

  if (manager.available())
  {
    // Wait for a message addressed to us from the client
    uint8_t len = sizeof(buf);
    uint8_t from;
    if (manager.recvfromAck(buf, &len, &from))
    {
      Serial.print("got request from : 0x");
      Serial.print(from, HEX);
      Serial.print(": ");
      Serial.println((char *)buf);

      // Send a reply back to the originator client
      if (!manager.sendtoWait(data, sizeof(data), from))
        Serial.println("sendtoWait failed");
    }
  }
  // uint8_t to;
  // uint8_t id;
  // uint8_t flags;

  //  if (manager.available())
  //  {
  //    Serial.println("available");
  //    if(driver.recv(buf,&len)){
  //      Serial.println((char*)buf);
  //    }
  // if(manager.recvfrom(buf, &len, &from)){
  //   Serial.print("got reply from : 0x");
  //   Serial.print(from, HEX);
  //   Serial.print(": ");
  //   Serial.println((char*)buf);
  // }
  // delay(500);
  //  }
}