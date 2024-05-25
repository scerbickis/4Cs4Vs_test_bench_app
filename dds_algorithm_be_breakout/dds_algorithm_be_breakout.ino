#include <SPI.h> //Įtraukiamas SPI biblioteka

const byte resolution = 16;
// Number of entries in the lookup table
const word tableLength = (1 << resolution) - 1; 

//Apibrėžiamas visų SAK išėjimų įtampos diapazonų nustatymo komandos kodas
const byte WRITE_ALL = 14; 
/*Apibrėžiamas rašymo į tam tikro SAK išėjimo (n) įėjimo registrą
bei šio išėjimo SAK registro atnaujinimo komandos kodas*/
const byte WRITE_N_UPDATE_N = 3; 
//Diapazono nuo -10V iki 10V nustatymo komandos duomenų dalis
const byte SCOPE_10_10 = 0x03; 

byte phase_id = 1;// Phase id

word amplitudeU[3] = { 0x3FFF, 0x3FFF, 0x3FFF };
word amplitudeI[3] = { 0x3FFF, 0x3FFF, 0x3FFF };
word DCComponentU[3] = { 0x7FFF, 0x7FFF, 0x7FFF };
word DCComponentI[3] = { 0x7FFF, 0x7FFF, 0x7FFF };
word tableStepU[3] = { 266, 266, 266 };
word tableStepI[3] = { 266, 266, 266 };
word u[3] = {0, 0, 0};
word i[3] = {0, 0, 0};
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

  for (word index = 0; index < tableLength; index++) {

    byte h;
    sineTable[index] = 0.0;

    for (byte k = 1; k <= harmonicOrder; k++){

      if (harmonicParity == 'E') h = 2 * k;
      else if (harmonicParity == 'O') h = 2 * k - 1;
      else if (harmonicParity == 'T') h = 3 * (2 * k - 1);
      else if (harmonicParity == 'R') h = (6 * k + pow(-1, k) - 3) / 2;
      else if (harmonicParity == 'P') h = 3 * k - 2;
      else if (harmonicParity == 'N') h = 3 * k - 1;
      else if (harmonicParity == 'Z') h = 3 * k;
      else h = k;
      
      sineTable[index] += sin(h * index * TWO_PI / tableLength) / (float) h;

    }

  }

}

void setParameters() {
  
  // Read the parameter id from the serial port
  byte parameter_id = Serial.read(); 

  if (parameter_id == 0x48) {
    // Read the harmonic parity from the serial port
    harmonicParity = Serial.read(); 
    // Read the harmonic order from the serial port
    harmonicOrder = Serial.read(); 
    if (harmonicOrder == 0) harmonicOrder = 1;
    calculateSineTable();
  }

  else if (parameter_id == 0x46 || parameter_id == 0x41 || parameter_id == 0x50) {
    // Read the phase id from the serial port01
    phase_id = Serial.read(); 
    // Read the output type from the serial port
    byte outputType = Serial.read();
    // Read 2 bytes of data from the serial port
    word dataBytes = (Serial.read() << 8) | Serial.read();

    switch(parameter_id){
      
      // 0x41 is Ascii for 'A'. 
      case 0x41: 
        if (outputType == 0x55) amplitudeU[phase_id - 1] = dataBytes;
        else if (outputType == 0x49) amplitudeI[phase_id - 1] = dataBytes; 
        break;

      // 0x46 is Ascii for 'F'.
      case 0x46: 
        if (outputType == 0x55) tableStepU[phase_id - 1] = dataBytes;
        else if (outputType == 0x49) tableStepI[phase_id - 1] = dataBytes;
        break;

      // 0x50 is Ascii for 'P'.
      case 0x50: {
        if (outputType == 0x55) {
          phaseU[phase_id - 1] = (word) dataBytes * tableLength / 360;
          for (byte line = 0; line < 3; line++) indexU[line] = phaseU[line];
        }
        else if (outputType == 0x49) {
          phaseI[phase_id - 1] = (word) dataBytes * tableLength / 360;
          for (byte line = 0; line < 3; line++) indexI[line] = phaseI[line];
        }
        break;
      }

      default: 
        break;
    }
  }
}

void valdytiSAK(byte komanda, byte adresas, word duomenys) {
  
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

    //Baigiamas SPI perdavimas
    SPI.endTransaction(); 

}

void setup() {
  
    Serial.begin(115200);
    while (!Serial);
    
    //Lusto išrinkimo kaištis nustatomas į išvesties režimą
    pinMode(PIN_SPI_SS, OUTPUT); 
    digitalWrite(PIN_SPI_SS, HIGH);

    SPI.begin(); //Inicializuojama SPI magistralė
    
    //Visų SAK išėjimų diapazonų nustatymo komanda
    valdytiSAK(WRITE_ALL, 0, SCOPE_10_10); 

    calculateSineTable();

}

void loop() {

  // if there is data available in the serial input buffer
  // if the received byte is 0x53, call the setup function
  if (Serial.available() > 0 && Serial.read() == 0x53) setParameters();

  word uN = 0x7FFF;
  word iN = 0x7FFF;

  for (byte line = 0; line < 3; line++) {
    
    indexU[line] += tableStepU[line];
    if (indexU[line] > tableLength) indexU[line] -= tableLength;
    indexI[line] += tableStepI[line];
    if (indexI[line] > tableLength) indexI[line] -= tableLength;

    u[line] = (word) amplitudeU[line] * sineTable[indexU[line]] + DCComponentU[line];
    valdytiSAK(WRITE_N_UPDATE_N, line, u[line]);
    i[line] = (word) amplitudeI[line] * sineTable[indexI[line]] + DCComponentI[line];
    valdytiSAK(WRITE_N_UPDATE_N, line + 4, i[line]);

    uN += (u[line] - DCComponentU[line]);
    iN += (i[line] - DCComponentI[line]);
  }

  valdytiSAK(WRITE_N_UPDATE_N, 3, uN);
  valdytiSAK(WRITE_N_UPDATE_N, 7, iN);

}
