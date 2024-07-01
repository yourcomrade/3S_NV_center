#include <Arduino.h>
#include <SPI.h>
#define ADF4351_LE 3 // or Chip select pin
#define LOCK 2
#define ADF4351_CE 7 // This pin is to turn on or off
uint32_t registers[6] =  {0x2C8018, 0x8008029, 0x4E42, 0x4B3,0xDC803C, 0x580005};
void WriteRegister32(const uint32_t value)
{
  digitalWrite(ADF4351_LE, LOW);
  for (int i = 3; i >= 0; i--)             // loop round 4 x 8 bits
    SPI.transfer((value >> 8 * i) & 0xFF); // offset, byte mask and send via SPI
  digitalWrite(ADF4351_LE, HIGH);
  digitalWrite(ADF4351_LE, LOW);
}
void SetADF4351()  // bung the data into the ADF4351
{ for (int i = 5; i >= 0; i--)
    WriteRegister32(registers[i]);
}
void disable(){
  digitalWrite(ADF4351_CE, LOW);
}
void enable(){
  digitalWrite(ADF4351_CE, HIGH);
}
void setup() 
{
  Serial.begin(9600);
  pinMode(LOCK,INPUT);
  pinMode(ADF4351_LE, OUTPUT);          // Setup pins
  pinMode(ADF4351_CE, OUTPUT);
  disable();
  digitalWrite(ADF4351_LE, HIGH);
  SPI.begin();                          // Init SPI bus
  SPI.setDataMode(SPI_MODE0);           
  SPI.setBitOrder(MSBFIRST);            
}
void loop() 
{ 
  Serial.println("Start");
  SetADF4351();
  enable();
  delay(2000);
}

/*!
   ADF4351 example program
*/
