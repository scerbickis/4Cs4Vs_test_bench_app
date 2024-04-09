#include <SPI.h> //Įtraukiamas SPI biblioteka

const uint16_t L = 1 << 12 - 1; // Number of entries in the lookup table

const uint8_t WRITE_ALL = 14; //Apibrėžiamas visų SAK išėjimų įtampos diapazonų nustatymo komandos kodas
const uint8_t WRITE_N_UPDATE_N = 3; /*Apibrėžiamas rašymo į tam tikro SAK išėjimo (n) įėjimo registrą
                                                  bei šio išėjimo SAK registro atnaujinimo komandos kodas*/
const uint8_t SCOPE_10_10 = 0x03; //Diapazono nuo -10V iki 10V nustatymo komandos duomenų dalis
// unsigned long int currentTime = 0;

uint16_t table_step = 1; // Step size for the lookup table
uint8_t phase_id = 1; // Phase id

uint16_t amplitude[3] = {1, 1, 1}; // Amplitude of the each phase
uint16_t frequency[3] = {50, 50, 50}; // Frequency of the each phase
float phaseFactor[3] = {0.0, 2.0 / 3.0, 1.0 / 3.0}; // Phase factor of the each phase
uint8_t harmonicOrder[3] = {1, 1, 1}; // Harmonic order of the each phase
char harmonicParity[3] = {'E', 'E', 'E'}; // Harmonic parity of the each phase

// uint16_t phase1 = (uint16_t) L * phaseFactor1;
// uint16_t phase2 = (uint16_t) L * phaseFactor2;
// uint16_t phase3 = (uint16_t) L * phaseFactor3;
float apkrova = 100.0;
bool signal_statuses[8] = {true, true, true, true, true, true, true, true};

uint16_t sineTable[L]; // Lookup sine table 

inline uint8_t evenOrder(uint8_t h) { return 2*h; }
inline uint8_t oddOrder(uint8_t h) { return 2*h + 1}
inline uint8_t tripleOrder(uint8_t h) { return 3*(2*h-1); }
inline uint8_t positiveOrder(uint8_t h) { return 3*h+1; }
inline uint8_t negativeOrder(uint8_t h) { return 3*h-1; }
inline uint8_t zeroOrder(uint8_t h) { return 3*h; }
inline uint8_t nonTripleOrder(uint8_t h) { return pow(-1,h)*(6*h*pow(-1,h)+3*pow(-1,h)-1)/2; }

uint16_t calculateSineTable(){

  uint8_t (*orderFunction)(uint8_t);
  if (harmonicParity[phase_id - 1] == 'E') orderFunction = evenOrder;
  else if (harmonicParity[phase_id - 1] == 'O') orderFunction = oddOrder;
  else if (harmonicParity[phase_id - 1] == 'T') orderFunction = tripleOrder;
  else if (harmonicParity[phase_id - 1] == 'P') orderFunction = positiveOrder;
  else if (harmonicParity[phase_id - 1] == 'N') orderFunction = negativeOrder;
  else if (harmonicParity[phase_id - 1] == 'Z') orderFunction = zeroOrder;
  else orderFunction = nonTripleOrder;

  for (uint16_t j = 0; j < L; j++) {

    for (uint8_t h = 1; h <= harmonicOrder[phase_id - 1]; orderFunction(h)){
      // Scale sine values to the range of 0-65535
        sineTable[j] += sin(h * j * 2 * PI / L) / h;
    }
  }

}

void setupParameters() {
  
  uint8_t parameter_id = Serial.read(); // Read the parameter id from the serial port
  phase_id = Serial.read(); // Read the phase id from the serial port01

  switch(parameter_id){
    
    case 0x41: // 0x41 is Ascii for 'A'. If the parameter id is 0x41, read the amplitude from the serial port
      amplitude[phase_id - 1] = (Serial.read() << 8) | Serial.read(); // Shift the byte by 8 bits
      break;

    case 0x46: // 0x46 is Ascii for 'F'. If the parameter id is 0x46, read the step size from the serial port
      frequency[phase_id - 1] = (Serial.read() << 8) | Serial.read(); // Shift the byte by 8 bits
      break;

    case 0x50: // 0x50 is Ascii for 'P'.
      uint8_t phaseBuffer[4];
      for (uint8_t i = 0; i < 4; i++) phaseBuffer[i] = Serial.read();
      memcpy(&phaseFactor[phase_id - 1], phaseBuffer, sizeof(float));
      break;

    case 0x48: // 0x48 is Ascii for 'H'. If the parameter id is 0x48, read the harmonic value from the serial port
      harmonicParity[phase_id - 1] = Serial.read(); // Read the harmonic parity from the serial port
      harmonicOrder[phase_id - 1] = Serial.read(); // Read the harmonic order from the serial port
      break;

    case 0x4F: // 0x4F is Ascii for 'O'.
      uint8_t outputStatus = Serial.read(); // Read the output status and address from the serial port
      signal_statuses[outputStatus & 0x0F] = (outputStatus & 0xF0) >> 4; // Read the signal status from the serial port
      break;

    case 0x52: // 0x52 is Ascii for 'R'.
      break;  

    default: // If the parameter id is not 0x46 or 0x41, break the switch statement
      break;
  }
  
  calculateSineTable(); // Calculate the sine table
  // for (uint16_t j = 0; j < L; j++) {
  //   // Scale sine values to the range of 0-65535
  //   u[j] = (uint16_t)(amplitude * (sin(j * step) + 1)/2);
  //   un[j] = (uint16_t)(amplitude * (sin(j * step) + sin(j * step + 2*PI/3) + sin(j * step + 4*PI/3))/2);
  // }
}

void valdytiSAK(uint8_t komanda, uint8_t adresas, uint16_t duomenys) {
  /*Šį funkciją naudojama SAK valdymui per SPI sąsają*/

   /*Atliekant komandinio baito loginį poslinkį keturiais bitais į kaire
                                                ir atliekant loginį sumavimą su adreso baitu, sukuriamas paketo antraštės baitas*/
  digitalWrite(PIN_SPI_SS, LOW); /*Pradedamas duomenų perdavimas su SAK'u, nustatant Lusto Pasirinkimo kaiščio
                                        išėjimo įtampos lygį į žemą*/
  SPI.transfer((komanda << 4) | adresas); // Antraštės baito siuntimas   
  SPI.transfer16(duomenys); // Dviejų baitų duomenų siuntimas 

  digitalWrite(PIN_SPI_SS, HIGH); /*Baigiamas duomenų perdavimas su SAK'u, nustatant Lusto Pasirinkimo kaiščio
                                        išėjimo įtampos lygį į aukštą*/

}

void setup() {

  Serial.begin(115200);
  SPI.begin(); //Inicializuojama SPI magistralė
  SPI.beginTransaction(SPISettings(30e6, MSBFIRST, SPI_MODE0)); //SPI komunikacijos parametrų nustatymas
  pinMode(PIN_SPI_SS, OUTPUT); //Lusto išrinkimo kaištis nustatomas į išvesties režimą
  valdytiSAK(WRITE_ALL, 0, SCOPE_10_10); //Visų SAK išėjimų diapazonų nustatymo komanda

  calculateSineTable(); // Call the setup function

}

void loop() {

  for (uint16_t t = 0; t < L; t += table_step){

    if (Serial.available() > 0) { // if there is data available on the serial port
      if (Serial.read() == 0x53) setupParameters(); // if the received byte is 0x53, call the setup function
    }

    uint16_t u1 = (uint16_t) (amplitude[0] * (sineTable[t] + 1)/2);
    signal_statuses[0] ? valdytiSAK(WRITE_N_UPDATE_N, 0, u1) : valdytiSAK(WRITE_N_UPDATE_N, 0, 32767);
    if (signal_statuses[0]) valdytiSAK(WRITE_N_UPDATE_N, 0, u1);

    uint16_t u2 = (uint16_t) (amplitude[1] * (sineTable[t] + 1)/2);
    if (signal_statuses[1]) valdytiSAK(WRITE_N_UPDATE_N, 1, u2);

    uint16_t u3 = (uint16_t) (amplitude[2] * (sineTable[t] + 1)/2);
    if (signal_statuses[2]) valdytiSAK(WRITE_N_UPDATE_N, 2, u3);

    uint16_t uN = u1 + u2 + u3 - (amplitude[0] + amplitude[1] + amplitude[2])/3;
    if (signal_statuses[3]) valdytiSAK(WRITE_N_UPDATE_N, 3, uN);

    uint16_t i1 = (uint16_t) (amplitude[0] * (sineTable[t] + 1)/2);
    uint16_t i2 = (uint16_t) (amplitude[1] * (sineTable[t] + 1)/2);
    uint16_t i3 = (uint16_t) (amplitude[2] * (sineTable[t] + 1)/2);
    uint16_t iN = i1 + i2 + i3 - (amplitude[0] + amplitude[1] + amplitude[2])/3;

    if (signal_statuses[4]) valdytiSAK(WRITE_N_UPDATE_N, 4, u[t]);
    if (signal_statuses[5]) valdytiSAK(WRITE_N_UPDATE_N, 5, u[t + 43690]);
    if (signal_statuses[6]) valdytiSAK(WRITE_N_UPDATE_N, 6, u[t + 21844]);
    if (signal_statuses[7]) valdytiSAK(WRITE_N_UPDATE_N, 7, un[t]);

  }
  
}
