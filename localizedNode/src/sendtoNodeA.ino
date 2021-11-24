
#include <RHReliableDatagram.h>
#include <RH_RF95.h>
#include <SPI.h>

#define PORTABLE_ADDRESS 1 //self
#define NODEA 2            //esp1
#define NODEB 3            //esp2
#define NODEC 4            //raspberry pi

#define NSS 5
#define DIO0 26
#define TIMEOUT 80
RH_RF95 driver(NSS, DIO0);

RHReliableDatagram manager(driver, PORTABLE_ADDRESS);

void setup()
{
  Serial.begin(115200);
    // Serial.println("here");

  if (!driver.init())
  {
    Serial.println("LoRa init failed. Check your connections.");
    // while (true)
    //   ;
  } else {
    Serial.println("LoRa init success");
  }
  // while (!Serial)
  //   ; // Wait for serial port to be available
  if (!manager.init())
    Serial.println("init failed");
  driver.setFrequency(900);
  driver.setTxPower(23, false);
  manager.setRetries(1);
  manager.setTimeout(TIMEOUT);
}

uint8_t data[] = "Ping";
uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
uint8_t len = sizeof(buf);
uint8_t from;

String getNodeAPacket(){
  String nodeAPacket = "";
  //populate nodeA packet
  nodeAPacket += ",NodeA,";
  for (int i = 0; i < 10; i++)
  {
    if (manager.sendtoWait(data, sizeof(data), NODEA))
    {
      if (manager.recvfromAckTimeout(buf, &len, 500, &from))
      {
        nodeAPacket += String(driver.lastRssi());

        if (i < 9)
        {
          nodeAPacket += ",";
        }
        // else
        // {
        //   nodeAPacket += "EOD,";
        // }

        // delay(50);
      }
    }
    else
    {
      Serial.println("Packet loss A!");
    }
  }
  return nodeAPacket;
}

String getNodeBPacket(){
  String nodeBPacket = "";
  //populate nodeB packet
  nodeBPacket += ",NodeB,";

  for (int i = 0; i < 10; i++)
  {
    if (manager.sendtoWait(data, sizeof(data), NODEB))
    {
      if (manager.recvfromAckTimeout(buf, &len, 500, &from))
      {
        nodeBPacket += String(driver.lastRssi());

        if (i < 9)
        {
          nodeBPacket += ",";
        }
        // else
        // {
        //   nodeBPacket += "EOD,";
        // }
        // delay(50);
      }
    }
    else
    {
      Serial.println("Packet loss B!");
    }
  }
  return nodeBPacket;
}

String getNodeCPacket(){
  String nodeCPacket = "";
  nodeCPacket += ",NodeC,";

  //populate nodeC packet
  for (int i = 0; i < 10; i++)
  {
    Serial.println("send to c");
    if (manager.sendtoWait(data, sizeof(data), NODEC))
    {
      if (manager.recvfromAckTimeout(buf, &len, 500, &from))
      {
        nodeCPacket += String(driver.lastRssi());

        if (i < 9)
        {
          nodeCPacket += ",";
        }
        // else
        // {
        //   nodeCPacket += "EOD,";
        // }

        // delay(50);
      }
    }
    else
    {
      Serial.println("Packet loss C!");
    }
  }
  return nodeCPacket;
}

//TODO: implement sensor reads/processing
String getSensorData(){
  String sensorData = "";

  return sensorData;
}

void loop()
{

  String nodeAPacket = "";
  String nodeBPacket = "";
  String nodeCPacket = "";
  String eofStr = "EOF,";
  String packetString = "";

  // ping anchor nodes for RSSI values and populate data strings
  nodeAPacket = getNodeAPacket();
  nodeBPacket = getNodeBPacket();
  nodeCPacket = getNodeCPacket();  

  packetString = nodeAPacket + nodeBPacket + nodeCPacket + eofStr;

  uint8_t *packetData = (uint8_t*)packetString.c_str();

  //send packets to data server
  for(int i = 0; i < packetString.length(); i++){
    Serial.print((char)packetData[i]);
  }

  manager.setTimeout(200);
  delay(50);
  if(manager.sendtoWait(packetData, packetString.length(), NODEC)){
    // delay(10);
    if (manager.recvfromAckTimeout(buf, &len, 4000, &from))
    {
      Serial.println("Transmission successful. Dumping data.");
      // delay(50);
      manager.setTimeout(TIMEOUT);

    }

  }
  
  // free(packetData);

}
