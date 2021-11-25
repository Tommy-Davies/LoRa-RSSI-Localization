
#include <RHReliableDatagram.h>
#include <RH_RF95.h>
#include <SPI.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <math.h> 

Adafruit_MPU6050 mpu;


int sound_digital = 4;
int sound_analog = 0;


#define PORTABLE_ADDRESS 1 //self
#define NODEC 2            //esp1
#define NODEB 3            //esp2
#define NODEA 4            //raspberry pi

#define NSS 5
#define DIO0 26
#define TIMEOUT 100
RH_RF95 driver(NSS, DIO0);

RHReliableDatagram manager(driver, PORTABLE_ADDRESS);

bool setup_mpu() {
  while (!Serial)
    delay(10); // will pause Zero, Leonardo, etc until serial console opens

  Serial.println("Adafruit MPU6050 test!");

  // Try to initialize!
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    delay(100);
    return false;
  }
  Serial.println("MPU6050 Found!");

  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  Serial.print("Accelerometer range set to: ");
  switch (mpu.getAccelerometerRange()) {
  case MPU6050_RANGE_2_G:
    Serial.println("+-2G");
    break;
  case MPU6050_RANGE_4_G:
    Serial.println("+-4G");
    break;
  case MPU6050_RANGE_8_G:
    Serial.println("+-8G");
    break;
  case MPU6050_RANGE_16_G:
    Serial.println("+-16G");
    break;
  }
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  Serial.print("Gyro range set to: ");
  switch (mpu.getGyroRange()) {
  case MPU6050_RANGE_250_DEG:
    Serial.println("+- 250 deg/s");
    break;
  case MPU6050_RANGE_500_DEG:
    Serial.println("+- 500 deg/s");
    break;
  case MPU6050_RANGE_1000_DEG:
    Serial.println("+- 1000 deg/s");
    break;
  case MPU6050_RANGE_2000_DEG:
    Serial.println("+- 2000 deg/s");
    break;
  }

  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  Serial.print("Filter bandwidth set to: ");
  switch (mpu.getFilterBandwidth()) {
  case MPU6050_BAND_260_HZ:
    Serial.println("260 Hz");
    break;
  case MPU6050_BAND_184_HZ:
    Serial.println("184 Hz");
    break;
  case MPU6050_BAND_94_HZ:
    Serial.println("94 Hz");
    break;
  case MPU6050_BAND_44_HZ:
    Serial.println("44 Hz");
    break;
  case MPU6050_BAND_21_HZ:
    Serial.println("21 Hz");
    break;
  case MPU6050_BAND_10_HZ:
    Serial.println("10 Hz");
    break;
  case MPU6050_BAND_5_HZ:
    Serial.println("5 Hz");
    break;
  }

  Serial.println("");
  return true;
}

void setup()
{
  Serial.begin(115200);
  // setup_mpu(); //TODO: put this back

  // Initialize pins for sound sensor
  pinMode(sound_digital, INPUT);

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

bool noiseDetect() {
  int val_digital = digitalRead(sound_digital);
  int val_analog = analogRead(sound_analog);
  // Serial.print(val_analog);
  // Serial.print("\t");
  // Serial.println(val_digital);

  if (val_digital == HIGH)
  {
    Serial.println("Noise level high");
    return true;
  }
  Serial.println(val_analog);
  return false;
}
bool compareFloats (float a, float b, float EPSILON) {
  return fabs(a - b) < EPSILON;
}
/**
 * Checks temperature against upper and lower limits.
 *
 * @param temp current temperature reading
 * @return integer, 0 for normal temperature, 1 for low temperature, 2 for high temperature
 */
int tempDetect(float temp) {
  float lowerLimit = 18;  // https://www.labour.gov.on.ca/english/hs/faqs/workplace.php#temperature
  float upperLimit = 35;  // https://www.ccohs.ca/oshanswers/phys_agents/heat_health.html
  float init_val = 36.53;
  Serial.print("Temperature: ");
  Serial.print(temp);
  Serial.println(" degC");

  if (temp <= lowerLimit) {
    Serial.println("Temperature too cold");
    return 1;
  }
  else if (compareFloats(temp, init_val, 0.001)) { //  if nothing is read from MPU6050
    return 3;
  }
  else if (temp >= upperLimit) {
    Serial.println("Temperature too hot");
    return 2;
  }


  return 0;
}

/**
 * Detects falls using x, y and z accelerations and gyro data.
 *
 * @param event struct holding sensor readings
 * @return boolean, true if a fall has been detected.
 */
bool fallDetect(sensors_event_t  *event_a, sensors_event_t  *event_g) {
  float acc_magnitude, g_magnitude = 0;
  float acc_lastReading, g_lastReading = 0;
  float high_threshhold = 6; // change in acc threshold
  float changeAcc = 0;
  // change in acceleration, hold one reading and compare or look at mulitple readings for trend
  // accelerometer gives around 11m/s^2 for sitting down
  acc_magnitude = sqrt(sq(event_a->acceleration.x) +sq(event_a->acceleration.y) + sq(event_a->acceleration.z));
  g_magnitude = sqrt(sq(event_g->gyro.x) +sq(event_g->gyro.y) + sq(event_g->gyro.z));
  changeAcc = abs(acc_magnitude - acc_lastReading);

  if (changeAcc > high_threshhold) {
    Serial.println("Fall Detected");
    Serial.println("Change in Acceleration");
    Serial.print(changeAcc);
    return true;
  }

  Serial.print("Magnitude of Acceleration: ");
  Serial.println(acc_magnitude);
  acc_lastReading = acc_magnitude;

  Serial.print("Magnitude of Angular Velocity: ");
  Serial.println(g_magnitude);
  g_lastReading = g_magnitude;
  return false;
}

void checkSensors() {
  /* Get new sensor events with the readings */
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  fallDetect(&a, &g);

  if (tempDetect(temp.temperature) == 3) {
    while(!setup_mpu());
  }

  // noiseDetect();
}

uint8_t data[] = "Ping";
uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
uint8_t len = sizeof(buf);
uint8_t from;

String getNodeAPacket(){
  String nodeAPacket = "";
  manager.setTimeout(200);
  manager.setRetries(2);
  
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
  
      }
    }
    else
    {
      Serial.println("Packet loss A!");
    }
  }
  manager.setTimeout(TIMEOUT);
  manager.setRetries(1);

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
    // Serial.println("send to c");
    if (manager.sendtoWait(data, sizeof(data), NODEC))
    {
      if (manager.recvfromAckTimeout(buf, &len, 500, &from))
      {
        nodeCPacket += String(driver.lastRssi());

        if (i < 9)
        {
          nodeCPacket += ",";
        }
  
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
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  String sensorData = "";
  if(fallDetect(&a, &g)){
    Serial.println("uhhh");
    sensorData += ",Fall,";
  }
  if (tempDetect(temp.temperature) == 1){
    sensorData += ",Undertemp,";
  } else if (tempDetect(temp.temperature) == 2){
    sensorData += ",Overtemp,";
  } else if(tempDetect(temp.temperature) == 3){
    while(!setup_mpu());
  }

  return sensorData;
}

void loop()
{

  String nodeAPacket = "";
  String nodeBPacket = "";
  String nodeCPacket = "";
  String sensorPacket = "";
  String eofStr = "EOF,";
  String packetString = "";

  // ping anchor nodes for RSSI values and populate data strings
  nodeAPacket = getNodeAPacket();
  nodeBPacket = getNodeBPacket();
  nodeCPacket = getNodeCPacket();
  // sensorPacket = getSensorData();  //TODO: put this back

  packetString = nodeAPacket + nodeBPacket + nodeCPacket + sensorPacket + eofStr;

  uint8_t *packetData = (uint8_t*)packetString.c_str();

  //send packets to data server
  for(int i = 0; i < packetString.length(); i++){
    Serial.print((char)packetData[i]);
  }

  manager.setTimeout(200);
  delay(50);
  if(manager.sendtoWait(packetData, packetString.length(), NODEA)){
    if (manager.recvfromAckTimeout(buf, &len, 4000, &from))
    {
      Serial.println("Transmission successful. Dumping data.");
      manager.setTimeout(TIMEOUT);
      // int startTime = millis()
      if(manager.recvfromAckTimeout(buf, &len, 10000, &from)){
        manager.sendtoWait(data, sizeof(data), NODEA);
        Serial.println("pathloss done");
        // delay(1000);
      }

    }

  }
  
  // free(packetData);

}
