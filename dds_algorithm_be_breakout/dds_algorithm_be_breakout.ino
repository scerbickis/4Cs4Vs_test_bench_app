#include <SPI.h> //Įtraukiamas SPI biblioteka

const uint8_t resolution = 16;
const uint16_t tableLength = (1 << resolution) - 1; // Number of entries in the lookup table

const uint8_t WRITE_ALL = 14; //Apibrėžiamas visų SAK išėjimų įtampos diapazonų nustatymo komandos kodas
const uint8_t WRITE_N_UPDATE_N = 3; /*Apibrėžiamas rašymo į tam tikro SAK išėjimo (n) įėjimo registrą
                                                  bei šio išėjimo SAK registro atnaujinimo komandos kodas*/
const uint8_t SCOPE_10_10 = 0x03; //Diapazono nuo -10V iki 10V nustatymo komandos duomenų dalis

uint8_t phase_id = 1;// Phase id

uint16_t amplitudeU[3] = {0x7FFF, 0x7FFF, 0x7FFF};
uint16_t amplitudeI[3] = {0x7FFF, 0x7FFF, 0x7FFF};
uint16_t tableStep[3] = {266, 266, 266};
// Amplitude, frequency and phase of the each phase
uint16_t phaseU[3] = {0, (uint16_t) 2 * tableLength/3, (uint16_t) tableLength/3}; 
uint16_t phaseI[3] = {0, (uint16_t) 2 * tableLength/3, (uint16_t) tableLength/3}; 
uint8_t harmonicOrder = 1; // Harmonic order of the each phase
char harmonicParity = 'A'; // Harmonic parity of the each phase

float R = 100.0; // Resistance
bool signal_statuses[8] = {true, true, true, true, true, true, true, true};

uint16_t index1 = phaseU[0];
uint16_t index2 = phaseU[1];
uint16_t index3 = phaseU[2];

float sineTable[tableLength] = {0.0}; // Lookup sine table 

void calculateSineTable(){

  for (uint16_t i = 0; i < tableLength; i++) {

    uint8_t h;
    sineTable[i] = 0.0;

    for (uint8_t k = 1; k <= 50; k++){

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
  
  uint8_t phaseBuffer[4];
  float phaseFactor;
  uint8_t outputStatus;
  uint8_t outputType;

  uint8_t parameter_id = Serial.read(); // Read the parameter id from the serial port
  phase_id = Serial.read(); // Read the phase id from the serial port01

  // Read the output type from the serial port
  if (parameter_id == 0x41 || parameter_id == 0x50) outputType = Serial.read(); 

  switch(parameter_id){
    
    case 0x41: // 0x41 is Ascii for 'A'. If the parameter id is 0x41, read the amplitude from the serial port
      if (outputType == 0x55) amplitudeU[phase_id - 1] = (Serial.read() << 8) | Serial.read(); // Shift the byte by 8 bits
      else if (outputType == 0x49) amplitudeI[phase_id - 1] = (Serial.read() << 8) | Serial.read(); // Shift the byte by 8 bits
      break;

    case 0x46: // 0x46 is Ascii for 'F'. If the parameter id is 0x46, read the step size from the serial port
      tableStep[phase_id - 1] = (Serial.read() << 8) | Serial.read(); // Shift the byte by 8 bits
      break;

    case 0x50: // 0x50 is Ascii for 'P'.

      for (uint8_t i = 0; i < 4; i++) phaseBuffer[i] = Serial.read();
      memcpy(&phaseFactor, phaseBuffer, sizeof(float));
      if (outputType == 0x55) phaseU[phase_id - 1] = (uint16_t) (phaseFactor * tableLength);
      else if (outputType == 0x49) phaseI[phase_id - 1] = (uint16_t) (phaseFactor * tableLength);
      break;

    case 0x48: // 0x48 is Ascii for 'H'. If the parameter id is 0x48, read the harmonic value from the serial port
      harmonicParity = Serial.read(); // Read the harmonic parity from the serial port
      harmonicOrder = Serial.read(); // Read the harmonic order from the serial port
      if (harmonicOrder == 0) harmonicOrder = 1;
      calculateSineTable();
      break;

    case 0x4F: // 0x4F is Ascii for 'O'.
      outputStatus = Serial.read(); // Read the output status and address from the serial port
      signal_statuses[outputStatus & 0x0F] = (outputStatus & 0xF0) >> 4; // Read the signal status from the serial port
      break;

    case 0x52: // 0x52 is Ascii for 'R'.
      break;  

    default: // If the parameter id is not 0x46 or 0x41, break the switch statement
      break;
  }

}

void valdytiSAK(uint8_t komanda, uint8_t adresas, uint16_t duomenys) {
  /*Ši funkcija naudojama SAK valdymui per SPI sąsają*/
  SPI.beginTransaction(SPISettings(30e6, MSBFIRST, SPI_MODE0));

  digitalWrite(PIN_SPI_SS, LOW); /*Pradedamas duomenų perdavimas su SAK'u, nustatant Lusto Pasirinkimo kaiščio
                                        išėjimo įtampos lygį į žemą*/

  /*Atliekant komandinio baito loginį poslinkį keturiais bitais į kaire
  ir atliekant loginį sumavimą su adreso baitu, sukuriamas paketo antraštės baitas*/
  SPI.transfer((komanda << 4) | adresas); // Antraštės baito siuntimas   
  SPI.transfer16(duomenys); // Dviejų baitų duomenų siuntimas 

  digitalWrite(PIN_SPI_SS, HIGH); /*Baigiamas duomenų perdavimas su SAK'u, nustatant Lusto Pasirinkimo kaiščio
                                        išėjimo įtampos lygį į aukštą*/

  SPI.endTransaction(); //Baigiamas SPI perdavimas

}

void setup() {
  
  Serial.begin(115200);
  while (!Serial);
  
  calculateSineTable();
  
  pinMode(PIN_SPI_SS, OUTPUT); //Lusto išrinkimo kaištis nustatomas į išvesties režimą
  digitalWrite(PIN_SPI_SS, HIGH);

  SPI.begin(); //Inicializuojama SPI magistralė
  
  valdytiSAK(WRITE_ALL, 0, SCOPE_10_10); //Visų SAK išėjimų diapazonų nustatymo komanda

}

void loop() {


  if (Serial.available() > 0) { // if there is data available on the serial port
    if (Serial.read() == 0x53) setParameters(); // if the received byte is 0x53, call the setup function
  }

  if (index1 > tableLength) index1 -= tableLength;
  if (index2 > tableLength) index2 -= tableLength;
  if (index3 > tableLength) index3 -= tableLength;

  uint16_t u1 = (uint16_t) (amplitudeU[0] * (sineTable[index1] + 1)/2);
  signal_statuses[0] ? valdytiSAK(WRITE_N_UPDATE_N, 0, u1) : valdytiSAK(WRITE_N_UPDATE_N, 0, 32767);

  uint16_t u2 = (uint16_t) (amplitudeU[1] * (sineTable[index2] + 1)/2);
  signal_statuses[1] ? valdytiSAK(WRITE_N_UPDATE_N, 1, u2) : valdytiSAK(WRITE_N_UPDATE_N, 1, 32767);

  uint16_t u3 = (uint16_t) (amplitudeU[2] * (sineTable[index3] + 1)/2);
  signal_statuses[2] ? valdytiSAK(WRITE_N_UPDATE_N, 2, u3) : valdytiSAK(WRITE_N_UPDATE_N, 2, 32767);

  uint16_t uN = u1 + u2 + u3 - (amplitudeU[0] + amplitudeU[1] + amplitudeU[2])/3;
  signal_statuses[3] ? valdytiSAK(WRITE_N_UPDATE_N, 3, uN) : valdytiSAK(WRITE_N_UPDATE_N, 3, 32767);

  uint16_t i1 = (uint16_t) (amplitudeI[0] * (sineTable[index1] + 1)/2);
  signal_statuses[4] ? valdytiSAK(WRITE_N_UPDATE_N, 4, i1) : valdytiSAK(WRITE_N_UPDATE_N, 4, 32767);

  uint16_t i2 = (uint16_t) (amplitudeI[1] * (sineTable[index2] + 1)/2);
  signal_statuses[5] ? valdytiSAK(WRITE_N_UPDATE_N, 5, i2) : valdytiSAK(WRITE_N_UPDATE_N, 5, 32767);

  uint16_t i3 = (uint16_t) (amplitudeI[2] * (sineTable[index3] + 1)/2);
  signal_statuses[6] ? valdytiSAK(WRITE_N_UPDATE_N, 6, i3) : valdytiSAK(WRITE_N_UPDATE_N, 6, 32767);

  uint16_t iN = i1 + i2 + i3 - (amplitudeI[0] + amplitudeI[1] + amplitudeI[2])/3;
  signal_statuses[7] ? valdytiSAK(WRITE_N_UPDATE_N, 7, iN) : valdytiSAK(WRITE_N_UPDATE_N, 7, 32767);


  index1 += tableStep[0];
  index2 += tableStep[1];
  index3 += tableStep[2];

}
