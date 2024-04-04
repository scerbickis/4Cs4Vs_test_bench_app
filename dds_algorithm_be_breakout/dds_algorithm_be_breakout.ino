#include <SPI.h> //Įtraukiamas SPI biblioteka

const uint16_t L = 1 << 12 - *21; // Number of entries in the lookup table
const float step = 2 * PI / L; // Step size for calculating sine values 

const uint8_t RASYTI_DIAPAZONA_I_VISUS = 14; //Apibrėžiamas visų SAK išėjimų įtampos diapazonų nustatymo komandos kodas
const uint8_t RASYTI_KODA_I_N_ATNAUJINTI_N = 3; /*Apibrėžiamas rašymo į tam tikro SAK išėjimo (n) įėjimo registrą
                                                  bei šio išėjimo SAK registro atnaujinimo komandos kodas*/

const uint8_t DIAPAZONAS_10_10 = 0x03; //Diapazono nuo -10V iki 10V nustatymo komandos duomenų dalis

const uint8_t DONTCARE = 0; // Nereikšmingo baito apibrėžimas, kuris naudojamas kai sudaromas 32 bitų paketas
// unsigned long int currentTime = 0;

uint8_t parameter_id = 0x46; // Parameter value for the sine wave

uint16_t M = 1; // Step size for the lookup table
uint16_t amplitude = 1; // Amplitude of the sine wave

float phaseFactor1 = 0.0;
float phaseFactor2 = 2.0 / 3.0;
float phaseFactor3 = 1.0 / 3.0;
uint16_t phase1 = (uint16_t) L * phaseFactor1;
uint16_t phase2 = (uint16_t) L * phaseFactor2;
uint16_t phase3 = (uint16_t) L * phaseFactor3;
float apkrova = 100.0;
uint8_t harmonic_order = 0;
char harmonic_parity = 'E';
bool signal_statuses[8] = {true, true, true, true, true, true, true, true};

uint16_t u[L]; // Lookup table to store wave values
uint16_t un[L]; // Lookup table to store wave values 

inline uint8_t evenOrder(uint8_t h) { return 2*h; }
inline uint8_t oddOrder(uint8_t h) { return 2*h + 1}
inline uint8_t tripleOrder(uint8_t h) { return 3*(2*h-1); }
inline uint8_t positiveOrder(uint8_t h) { return 3*h+1; }
inline uint8_t negativeOrder(uint8_t h) { return 3*h-1; }
inline uint8_t zeroOrder(uint8_t h) { return 3*h; }
inline uint8_t nonTripleOrder(uint8_t h) { return pow(-1,h)*(6*h*pow(-1,h)+3*pow(-1,h)-1)/2; }

uint16_t calculateSineTable(){

  uint8_t (*orderFunction)(uint8_t);

  if (harmonic_parity == 'E') orderFunction = evenOrder;
  else if (harmonic_parity == 'O') orderFunction = oddOrder;
  else if (harmonic_parity == 'T') orderFunction = tripleOrder;
  else if (harmonic_parity == 'P') orderFunction = positiveOrder;
  else if (harmonic_parity == 'N') orderFunction = negativeOrder;
  else if (harmonic_parity == 'Z') orderFunction = zeroOrder;
  else orderFunction = nonTripleOrder;

  for (uint8_t h = 1; h <= harmonic_number; orderFunction(h)){
      
      for (uint16_t j = 0; j < L; j++) {
        // Scale sine values to the range of 0-65535
        u[j] += (uint16_t)(amplitude/h * sin(h * j * step));
      }
    }
}


void setupParameters() {
  
  parameter_id = Serial.read(); // Read the parameter id from the serial port

  switch(parameter_id){
    
    case 0x46: // 0x46 is Ascii for 'F'. If the parameter id is 0x46, read the step size from the serial port
      M = (Serial.read() << 8) | Serial.read(); // Shift the byte by 8 bits
      break;
    
    case 0x41: // 0x41 is Ascii for 'A'. If the parameter id is 0x41, read the amplitude from the serial port
      amplitude = (Serial.read() << 8) | Serial.read(); // Shift the byte by 8 bits
      break;

    case 0x48: // 0x48 is Ascii for 'H'. If the parameter id is 0x48, read the harmonic value from the serial port
      harmonic_parity = Serial.read(); // Read the harmonic parity from the serial port
      harmonic_order = Serial.read(); // Read the harmonic number from the serial port
      break;

    case 0x4F: // 0x4F is Ascii for 'O'.
      signal_statuses[Serial.read()] = Serial.read(); // Read the signal status from the serial port
      break;

    case 0x50: // 0x50 is Ascii for 'P'.
      apkrova = (Serial.read() << 8) | Serial.read(); // Read the load value from the serial port
      break;

    case 0x52:
      break;  

    default: // If the parameter id is not 0x46 or 0x41, break the switch statement
      break;
  }

  for (uint16_t j = 0; j < L; j++) {
    // Scale sine values to the range of 0-65535
    u[j] = (uint16_t)(amplitude * (sin(j * step) + 1)/2);
    un[j] = (uint16_t)(amplitude * (sin(j * step) + sin(j * step + 2*PI/3) + sin(j * step + 4*PI/3))/2);
  }
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
  valdytiSAK(RASYTI_DIAPAZONA_I_VISUS, DONTCARE, DIAPAZONAS_10_10); //Visų SAK išėjimų diapazonų nustatymo komanda

  setupParameters(); // Call the setup function

}

void loop() {

  for (uint16_t t = 0; t < L; t += M){

    if (Serial.available() > 0) { // if there is data available on the serial port
      if (Serial.read() == 0x53) setupParameters(); // if the received byte is 0x53, call the setup function
    }

  valdytiSAK(RASYTI_DIAPAZONA_I_VISUS, DONTCARE, DIAPAZONAS_10_10); // Set the range for all SAK outputs

  if (signal_statuses[0]) valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N, 0, u[t]);
  if (signal_statuses[1]) valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N, 1, u[t + 43690]);
  if (signal_statuses[2]) valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N, 2, u[t + 21844]);
  if (signal_statuses[3]) valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N, 3, un[t]);

  if (signal_statuses[4]) valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N, 4, u[t]);
  if (signal_statuses[5]) valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N, 5, u[t + 43690]);
  if (signal_statuses[6]) valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N, 6, u[t + 21844]);
  if (signal_statuses[7]) valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N, 7, un[t]);

  }
  
}
