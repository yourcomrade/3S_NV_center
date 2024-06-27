#include <Arduino.h>
#include <SPI.h>

#define ADF4351_LE 5 // or Chip select pin
#define LOCK 2
#define ADF4351_CE 4 // This pin is to turn on or off
#define SCK 18
#define MOSI 23
#define MISO 19
#define SS 5 
class simple_adf4351{
  public:
    uint64_t RFout;
    uint32_t PFDFreq;
    uint16_t ChannelSpacing;
    uint32_t registers[6] = {0,0,0,0,0};
    uint16_t divider;
    double N ;
    uint64_t INTVal ;
    uint64_t MODVal ;
    uint64_t FRACVal;
    uint64_t GCDVal;
    simple_adf4351 (uint64_t RFout, uint32_t PFDFreq, uint16_t ChannelSpacing):RFout(RFout),
    PFDFreq(PFDFreq), ChannelSpacing(ChannelSpacing){
      pinMode(ADF4351_LE, OUTPUT);          // Setup pins
      pinMode(ADF4351_CE, OUTPUT);
      digitalWrite(ADF4351_LE, HIGH);
      SPI.begin(SCK, MISO, MOSI, SS);                         // Init SPI bus
      SPI.setDataMode(SPI_MODE0);           
      SPI.setBitOrder(MSBFIRST);   
  }
  void disable(){
    digitalWrite(ADF4351_CE, LOW);
  }
  void enable(){
    digitalWrite(ADF4351_CE, HIGH);
  }
  void setADF4351(){
    for (int i = 5; i >= 0; i--)
    WriteRegister32(registers[i]);
  }
  void set_freq(int desired_freq){
    RFout = desired_freq;
    divider = SelectDivider(RFout);
    N = CalcN(RFout, PFDFreq);
    INTVal = CalcINT(N);
    MODVal = CalcMOD(PFDFreq, ChannelSpacing);
    FRACVal = CalcFRAC(N, INTVal, MODVal);
    GCDVal = CalcGCD(FRACVal, MODVal);
    if(GCDVal > 1){
      MODVal /= GCDVal;
      FRACVal /= GCDVal;
    }
    // Set Reg values
    // Reg0
    registers[0] = setbf(0, 16, INTVal, 15, 0x00000000) ;
    registers[0] = setbf(0, 12, FRACVal, 3, registers[0]);
    // Reg1
    registers[1] = setbf(0, 16, MODVal, 3, 0x00008001);
    // Reg2
    registers[2] = 0x4E42;
    // Reg3
    registers[3] = 0x4B3;
    // Reg4
    registers[4] = SelectReg4(RFout);
    // Reg5
    registers[5] = 0x580005;
  }
  private:
  
  void WriteRegister32(const uint32_t value)
  {
    digitalWrite(ADF4351_LE, LOW);
    for (int i = 3; i >= 0; i--)             // loop round 4 x 8 bits
      SPI.transfer((value >> 8 * i) & 0xFF); // offset, byte mask and send via SPI
    digitalWrite(ADF4351_LE, HIGH);
    digitalWrite(ADF4351_LE, LOW);
  }
  int SelectDivider(uint32_t RFout) {
    int Divider;
    if (RFout >= 2200000) Divider = 1;      // 2200 MHz * 1000 = 2200000 kHz
    if (RFout < 2200000) Divider = 2;       // 2200 MHz * 1000 = 2200000 kHz
    if (RFout < 1100000) Divider = 4;       // 1100 MHz * 1000 = 1100000 kHz
    if (RFout < 550000) Divider = 8;        // 550 MHz * 1000 = 550000 kHz
    if (RFout < 275000) Divider = 16;       // 275 MHz * 1000 = 275000 kHz  
    if (RFout < 137500) Divider = 32;       // 137.5 MHz * 1000 = 137500 kHz
    if (RFout < 68750) Divider = 64;        // 68.75 MHz * 1000 = 68750 kHz
    return Divider;
  }
  long SelectReg4(int RFout) {
    long Reg4;
    if (RFout >= 2200000) Reg4 = 0x8503FC;      // 2200 MHz * 1000 = 2200000 kHz
    if (RFout < 2200000) Reg4 = 0x9503FC;       // 2200 MHz * 1000 = 2200000 kHz
    if (RFout < 1100000) Reg4 = 0xA503FC;       // 1100 MHz * 1000 = 1100000 kHz
    if (RFout < 550000) Reg4 = 0xB503FC;        // 550 MHz * 1000 = 550000 kHz
    if (RFout < 275000) Reg4 = 0xC503FC;        // 275 MHz * 1000 = 275000 kHz
    if (RFout < 137500) Reg4 = 0xD503FC;        // 137.5 MHz * 1000 = 137500 kHz
    if (RFout < 68750) Reg4 = 0xE503FC;         // 68.75 MHz * 1000 = 68750 kHz  
    return Reg4;
  }
  double CalcN(int RFout, int PFDFreq) {
    return (double(RFout) / (double)PFDFreq) * SelectDivider(RFout);  
  }
  uint64_t CalcINT(double N) {
    return int(N);
  }
  uint64_t CalcMOD(int PFDFreq, int ChannelSpacing) {
    return int(1000.0 * (PFDFreq/1000) / ChannelSpacing);
  }
  uint64_t CalcFRAC(double N, double INTVal, double MODVal) {
    return uint64_t((N - INTVal) * MODVal);
  }
  uint64_t CalcGCD(uint64_t A, uint64_t B) {
    uint64_t T;
    while (B != 0) {
      T = B;
      B = A % B;
      A = T;
    }
    return A;
  }
  uint8_t get_bit(uint32_t val, uint8_t pos){
    return (val >> pos) & 0x01;
  }
  uint32_t set_bit(uint32_t val, uint8_t pos, uint8_t bit){
    uint32_t mask = 1UL << (pos);
    if(bit){
      val |= mask; 
    }
    else{
      val &= ~mask;
    }
    return val;
  }
  uint32_t setbf(uint8_t st_putb, uint8_t en_putb, uint32_t val_putb, uint8_t st_whole,uint32_t whole){
    uint8_t j = st_whole;
    uint32_t temp = 0x0;
    for(uint8_t i = st_putb; i < en_putb; i++){
      uint8_t bit = get_bit(val_putb, i);
      temp |= set_bit(whole, j, bit);
      j++;
    }
    return temp;
  }

};
uint64_t freq = 2860000; //khz
simple_adf4351 dev(freq, 25000, 100);
void setup() 
{
 
  pinMode(LOCK,INPUT);
  // put your setup code here, to run once:
  Serial.begin(115200);
 
           
}

void loop() 
{
  dev.set_freq(freq);
  dev.setADF4351();
  dev.enable();
  Serial.print("Frequency: ");
  Serial.print(freq);
  Serial.println("khz");
 
  delay(200);
  if(freq < 2890000){
    freq += 100;
  }
  else{
    freq = 2840000;
  }
 

  
}

/*!
   ADF4351 example program
*/