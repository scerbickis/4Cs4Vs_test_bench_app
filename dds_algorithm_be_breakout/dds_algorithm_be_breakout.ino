#include <SPI.h> //Įtraukiamas SPI biblioteka

const uint16_t L = 65535; // Number of entries in the lookup table
const float step = 2 * PI / L; // Step size for calculating sine values 

const uint8_t RASYTI_DIAPAZONA_I_VISUS = 14; //Apibrėžiamas visų SAK išėjimų įtampos diapazonų nustatymo komandos kodas
const uint8_t RASYTI_KODA_I_N_ATNAUJINTI_N = 3; /*Apibrėžiamas rašymo į tam tikro SAK išėjimo (n) įėjimo registrą
                                                  bei šio išėjimo SAK registro atnaujinimo komandos kodas*/

const uint8_t DIAPAZONAS_10_10 = 0x03; //Diapazono nuo -10V iki 10V nustatymo komandos duomenų dalis

const uint8_t DONTCARE = 0; // Nereikšmingo baito apibrėžimas, kuris naudojamas kai sudaromas 32 bitų paketas
// unsigned long int currentTime = 0;

uint16_t t1 = 0; // Index for the lookup table
uint16_t t2 = 43690; // Index for the lookup table
uint16_t t3 = 21844; // Index for the lookup table
uint16_t j; // Index for loops

uint8_t parameter_id = 0x46; // Parameter value for the sine wave

uint16_t M = 65000; // Step size for the lookup table
uint16_t amplitude = 1; // Amplitude of the sine wave
float apkrova = 100.0;

uint16_t u[L]; // Lookup table to store wave values
uint16_t un[L]; // Lookup table to store wave values

void setupParameters() {
  
  parameter_id = Serial.read(); // Read the parameter id from the serial port

  switch(parameter_id){
    
    case 0x46: // 0x46 is Ascii for 'F'. If the parameter id is 0x46, read the step size from the serial port
      M = (Serial.read() << 8) | Serial.read(); // Shift the byte by 8 bits
      break;
    
    case 0x41: // 0x41 is Ascii for 'A'. If the parameter id is 0x41, read the amplitude from the serial port
      amplitude = (Serial.read() << 8) | Serial.read(); // Shift the byte by 8 bits
      break;

    case 
    
    default: // If the parameter id is not 0x46 or 0x41, break the switch statement
      break;
  }

  for (j = 0; j < L; j++) {
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

  if (Serial.available() > 0) { // if there is data available on the serial port
      if (Serial.read() == 0x53) setupParameters(); // if the received byte is 0x53, call the setup function
    }

  valdytiSAK(RASYTI_DIAPAZONA_I_VISUS, DONTCARE, DIAPAZONAS_10_10); // Set the range for all SAK outputs

  valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N, 0, u[t1]); 
  valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N, 1, u[t2]); 
  valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N, 2, u[t3]); 
  valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N, 3, un[t1]); 

  valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N, 4, i[t1]);
  valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N, 5, i[t2]); 
  valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N, 6, i[t3]); 
  valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N, 7, in[t1]); 

  t1 = t1 + M; // Increment the index for the lookup table
  t2 = t2 + M; // Increment the index for the lookup table
  t3 = t3 + M; // Increment the index for the lookup table
}
