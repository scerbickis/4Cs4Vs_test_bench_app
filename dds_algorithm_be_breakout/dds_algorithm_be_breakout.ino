#include <SPI.h> //Įtraukiamas SPI biblioteka

const byte resolution = 16;
const word tableLength = (1 << resolution) - 1; // Number of entries in the lookup table

const byte WRITE_ALL = 14; //Apibrėžiamas visų SAK išėjimų įtampos diapazonų nustatymo komandos kodas
const byte WRITE_N_UPDATE_N = 3; /*Apibrėžiamas rašymo į tam tikro SAK išėjimo (n) įėjimo registrą
                                                  bei šio išėjimo SAK registro atnaujinimo komandos kodas*/
const byte SCOPE_10_10 = 0x03; //Diapazono nuo -10V iki 10V nustatymo komandos duomenų dalis

byte phase_id = 1;// Phase id

word amplitudeU[3] = { 0x3FFF, 0x3FFF, 0x3FFF };
word amplitudeI[3] = { 0x3FFF, 0x3FFF, 0x3FFF };
word DCComponentU[3] = { 0x7FFF, 0x7FFF, 0x7FFF };
word DCComponentI[3] = { 0x7FFF, 0x7FFF, 0x7FFF };
word tableStep[3] = { 266, 266, 266 };
// Amplitude, frequency and phase of the each phase
word phaseU[3] = {0, (word) 2 * tableLength/3, (word) tableLength/3}; 
word phaseI[3] = {0, (word) 2 * tableLength/3, (word) tableLength/3}; 
byte harmonicOrder = 1; // Harmonic order of the each phase
char harmonicParity = 'A'; // Harmonic parity of the each phase

bool signal_statuses[8] = { true };

// Index of the sine table for each phase
word indexU[3] = {phaseU[0], phaseU[1], phaseU[2]}; 
word indexI[3] = {phaseI[0], phaseI[1], phaseI[2]}; 

float sineTable[tableLength] = {0.0}; // Lookup sine table 

void calculateSineTable(){

  for (word i = 0; i < tableLength; i++) {

    byte h;
    sineTable[i] = 0.0;

    for (byte k = 1; k <= 50; k++){

      if (harmonicParity == 'E') h = 2 * k;
      else if (harmonicParity == 'O') h = 2 * k - 1;
      else if (harmonicParity == 'T') h = 3 * (2 * k - 1);
      else if (harmonicParity == 'R') h = (6 * k + pow(-1, k) - 3) / 2;
      else if (harmonicParity == 'P') h = 3 * k - 2;
      else if (harmonicParity == 'N') h = 3 * k - 1;
      else if (harmonicParity == 'Z') h = 3 * k;
      else h = k;

      if (h > harmonicOrder) break;

      sineTable[i] += sin(h * i * TWO_PI / tableLength) / (float) h;

    }

  }

}

void setParameters() {
  
  byte outputStatus;
  byte outputType;

  // Read the parameter id from the serial port
  byte parameter_id = Serial.read(); 
  // Read the phase id from the serial port01
  if (parameter_id != 0x48) phase_id = Serial.read(); 

  // Read the output type from the serial port
  if (parameter_id == 0x41 || parameter_id == 0x50) {
    outputType = Serial.read(); 
  }

  switch(parameter_id){
    
    // 0x41 is Ascii for 'A'. 
    // If the parameter id is 0x41, read the amplitude from the serial port
    case 0x41: 
      // Shift the byte by 8 bits
      if (outputType == 0x55) {
        amplitudeU[phase_id - 1] = (Serial.read() << 8) | Serial.read();
      } 
      // Shift the byte by 8 bits
      else if (outputType == 0x49) {
        amplitudeI[phase_id - 1] = (Serial.read() << 8) | Serial.read(); 
      }
      break;

    // 0x46 is Ascii for 'F'.
    // If the parameter id is 0x46, read the step size from the serial port
    case 0x46: 
      // Shift the byte by 8 bits
      tableStep[phase_id - 1] = (Serial.read() << 8) | Serial.read(); 
      break;

    // 0x50 is Ascii for 'P'.
    case 0x50: 
      
      word angle = (Serial.read() << 8) | Serial.read();

      if (outputType == 0x55) {
        phaseU[phase_id - 1] = (word) angle * tableLength / 360;
        for (byte i = 0; i < 3; i++) indexU[i] = phaseU[i];
      }
      
      else if (outputType == 0x49) {
        phaseI[phase_id - 1] = (word) angle * tableLength / 360;
        for (byte i = 0; i < 3; i++) indexI[i] = phaseI[i];
      }
      
      break;

    // 0x48 is Ascii for 'H'.
    // If the parameter id is 0x48, read the harmonic value from the serial port
    case 0x48: 
      
      // Read the harmonic parity from the serial port
      harmonicParity = Serial.read(); 
      // Read the harmonic order from the serial port
      harmonicOrder = Serial.read(); 
      if (harmonicOrder == 0) harmonicOrder = 1;
      calculateSineTable();
      
      break;

    // 0x4F is Ascii for 'O'.
    case 0x4F: 
      
      // Read the output status and address from the serial port
      outputStatus = Serial.read(); 
      // Read the signal status from the serial port
      signal_statuses[outputStatus & 0x0F] = (outputStatus & 0xF0) >> 4; 
      
      break;

    // If the parameter id is not 0x46 or 0x41, break the switch statement
    default: 
      break;
  }

}

void valdytiSAK(byte komanda, byte adresas, word duomenys) {
  
  /*Ši funkcija naudojama SAK valdymui per SPI sąsają*/
  SPI.beginTransaction(SPISettings(30e6, MSBFIRST, SPI_MODE0));
  /*Pradedamas duomenų perdavimas su SAK'u, 
  nustatant Lusto Pasirinkimo kaiščio
  išėjimo įtampos lygį į žemą*/
  digitalWrite(PIN_SPI_SS, LOW); 

  /*Atliekant komandinio baito loginį poslinkį keturiais bitais į kaire
  ir atliekant loginį sumavimą su adreso baitu, 
  sukuriamas paketo antraštės baitas*/
  // Antraštės baito siuntimas   
  SPI.transfer((komanda << 4) | adresas); 
  // Dviejų baitų duomenų siuntimas 
  SPI.transfer16(duomenys); 

  /*Baigiamas duomenų perdavimas su SAK'u, 
  nustatant Lusto Pasirinkimo kaiščio
  išėjimo įtampos lygį į aukštą*/
  digitalWrite(PIN_SPI_SS, HIGH); 

  SPI.endTransaction(); //Baigiamas SPI perdavimas

}

void setup() {
  
  Serial.begin(115200);
  while (!Serial);
  
  calculateSineTable();
  
  //Lusto išrinkimo kaištis nustatomas į išvesties režimą
  pinMode(PIN_SPI_SS, OUTPUT); 
  digitalWrite(PIN_SPI_SS, HIGH);

  SPI.begin(); //Inicializuojama SPI magistralė
  
  //Visų SAK išėjimų diapazonų nustatymo komanda
  valdytiSAK(WRITE_ALL, 0, SCOPE_10_10); 

}

void loop() {

  // if there is data available in the serial input buffer
  // if the received byte is 0x53, call the setup function
  if (Serial.available() > 0 && Serial.read() == 0x53) setParameters();

  for (byte i = 0; i < 3; i++) {
    indexU[i] += tableStep[i];
    if (indexU[i] > tableLength) indexU[i] -= tableLength;
    indexI[i] += tableStep[i];
    if (indexI[i] > tableLength) indexI[i] -= tableLength;
  }

  word u1 = (word) amplitudeU[0] * sineTable[indexU[0]] + DCComponentU[0];
  valdytiSAK(WRITE_N_UPDATE_N, 0, u1);

  word u2 = (word) amplitudeU[1] * sineTable[indexU[1]] + DCComponentU[1];
  valdytiSAK(WRITE_N_UPDATE_N, 1, u2);

  word u3 = (word) amplitudeU[2] * sineTable[indexU[2]] + DCComponentU[2];
  valdytiSAK(WRITE_N_UPDATE_N, 2, u3);

  word uN = 0x7FFF + (u1 - DCComponentU[0]) + (u2 - DCComponentU[1]) + (u3 - DCComponentU[2]);
  valdytiSAK(WRITE_N_UPDATE_N, 3, uN);

  word i1 = (word) amplitudeI[0] * sineTable[indexI[0]] + DCComponentI[0];
  valdytiSAK(WRITE_N_UPDATE_N, 4, i1);

  word i2 = (word) amplitudeI[1] * sineTable[indexI[1]] + DCComponentI[1];
  valdytiSAK(WRITE_N_UPDATE_N, 5, i2);

  word i3 = (word) amplitudeI[2] * sineTable[indexI[2]] + DCComponentI[2];
  valdytiSAK(WRITE_N_UPDATE_N, 6, i3);

  word iN = 0x7FFF + (i1 - DCComponentI[0]) + (i2 - DCComponentI[1]) + (i3 - DCComponentI[2]);
  valdytiSAK(WRITE_N_UPDATE_N, 7, iN);

}
