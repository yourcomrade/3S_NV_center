#include <Arduino.h>
#include <SPI.h>

#define ADF4351_LE 3 // or Chip select pin
#define LOCK 2
#define ADF4351_CE 7 // This pin is to turn on or off


class simple_adf4351{
  public:
    uint16_t RFout;
    uint16_t PFDFreq;
    uint16_t ChannelSpacing;
    uint32_t registers[6] = {0,0,0,0,0};
    int divider;
    double N ;
    int INTVal ;
    int MODVal ;
    int FRACVal;
    int GCDVal;
    simple_adf4351 (uint16_t RFout, uint16_t PFDFreq, uint16_t ChannelSpacing):RFout(RFout),
    PFDFreq(PFDFreq), ChannelSpacing(ChannelSpacing){
      pinMode(ADF4351_LE, OUTPUT);          // Setup pins
      pinMode(ADF4351_CE, OUTPUT);
      digitalWrite(ADF4351_LE, HIGH);
      SPI.begin();                          // Init SPI bus
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
    // Set Reg values
    // Reg0
    registers[0] = setbf(0, 16, INTVal, 15, 0x00000000) ;
    
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
  int SelectDivider(int RFout) {
    int Divider;
  
    if (RFout >= 2200) Divider = 1;
    if (RFout < 2200) Divider = 2;
    if (RFout < 1100) Divider = 4;
    if (RFout < 550) Divider = 8;
    if (RFout < 275) Divider = 16;
    if (RFout < 137.5) Divider = 32;
    if (RFout < 68.75) Divider = 64;
  
    return Divider;
  }
  long SelectReg4(int RFout) {
    long Reg4;
  
    if (RFout >= 2200) Reg4 = 0x8503FC;
    if (RFout < 2200) Reg4 = 0x9503FC;
    if (RFout < 1100) Reg4 = 0xA503FC;
    if (RFout < 550) Reg4 = 0xB503FC;
    if (RFout < 275) Reg4 = 0xC503FC;
    if (RFout < 137.5) Reg4 = 0xD503FC;
    if (RFout < 68.75) Reg4 = 0xE503FC;
  
    return Reg4;
  }
  double CalcN(int RFout, int PFDFreq) {
    return (double(RFout) / PFDFreq) * SelectDivider(RFout);  
  }

  int CalcINT(double N) {
    return int(N);
  }

  int CalcMOD(int PFDFreq, int ChannelSpacing) {
    return int(1000.0 * PFDFreq / ChannelSpacing);
  }

  int CalcFRAC(double N, int INTVal, int MODVal) {
    return int((N - INTVal) * MODVal);
  }

  int CalcGCD(int A, int B) {
    int T;

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
uint16_t freq = 2500;
simple_adf4351 dev(freq, 25, 100);
void setup() 
{
  Serial.begin(9600);
  pinMode(LOCK,INPUT);

           
}

void loop() 
{
  
  
  Serial.print("Frequency: ");
  Serial.print(freq);
  Serial.println(" Mhz");
  dev.set_freq(freq);
  dev.setADF4351();
  dev.enable();
 
  delay(200);
  if(freq < 3000){
    
    freq+=10;
  }
  else{
    freq = 2500;
  }

  
}

/*!
   ADF4351 example program
*/
