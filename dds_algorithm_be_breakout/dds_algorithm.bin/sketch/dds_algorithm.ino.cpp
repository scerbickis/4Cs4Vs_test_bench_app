#include <Arduino.h>
#line 1 "C:\\Users\\Andrej Scerbickis\\OneDrive - Vilniaus Gedimino technikos universitetas\\Dokumentai\\univer\\bakalauras\\4Cs4Vs_test_bench_app\\dds_algorithm\\dds_algorithm.ino"
#include <Arduino_PortentaBreakout.h>

breakoutPin spi_cs   = SPI1_CS; //Apibrėžiamas Breakout plokštės SPI sąsajos Chip Select kaištis
breakoutPin spi_ck   = SPI1_CK; //Apibrėžiamas Breakout plokštės SPI sąsajos Clock kaištis
breakoutPin spi_miso = SPI1_CIPO; //Apibrėžiamas Breakout plokštės SPI sąsajos Controller In Peripheral Out kaištis
breakoutPin spi_mosi = SPI1_COPI; //Apibrėžiamas Breakout plokštės SPI sąsajos Controller Out Peripheral In kaištis

const uint16_t L = 65535; // Number of entries in the lookup table
const float step = 2 * PI / L; // Step size for calculating sine values 

uint16_t t1 = 0; // Index for the lookup table
uint16_t t2 = 43690; // Index for the lookup table
uint16_t t3 = 21844; // Index for the lookup table
uint16_t i; // Index for loops

uint8_t parameter_id = 0x46; // Parameter value for the sine wave

uint16_t M = 65000; // Step size for the lookup table
uint16_t amplitude = 1; // Amplitude of the sine wave

uint16_t u1 = 0; // Sine wave value
uint16_t u2 = 0; // Sine wave value
uint16_t u3 = 0; // Sine wave value
uint16_t un = 0; // Sine wave value

uint16_t i1 = 0; // Sine wave value
uint16_t i2 = 0; // Sine wave value
uint16_t i3 = 0; // Sine wave value
uint16_t in = 0; // Sine wave value

uint16_t voltageLookupTable[L]; // Lookup table to store sine wave values
uint16_t currentLookupTable[L]; // Lookup table to store sine wave values

const uint8_t RASYTI_KODA_I_N = 0; //Apibrėžiamas rašymo į tam tikro SAK išėjimo (n) įėjimo registrą komandos kodas  
const uint8_t RASYTI_KODA_I_VISUS = 8; //Apibrėžiamas rašymo į visų SAK išėjimų įėjimų registrus komandos kodas
const uint8_t RASYTI_DIAPAZONA_I_N = 6; //Apibrėžiamas tam tikro SAK išėjimo (n) įtampos diapazono nustatymo komandos kodas
const uint8_t RASYTI_DIAPAZONA_I_VISUS = 14; //Apibrėžiamas visų SAK išėjimų įtampos diapazonų nustatymo komandos kodas
const uint8_t ATNAUJINTI_N = 1; //Apibrėžiamas tam tikro SAK išėjimo (n) SAK registro atnaujinimo komandos kodas
const uint8_t ATNAUJINTI_VISUS = 9; //Apibrėžiamas visų SAK išėjimų SAK registrų atnaujinimo komandos kodas
const uint8_t RASYTI_KODA_I_N_ATNAUJINTI_N = 3; /*Apibrėžiamas rašymo į tam tikro SAK išėjimo (n) įėjimo registrą
                                                  bei šio išėjimo SAK registro atnaujinimo komandos kodas*/
const uint8_t RASYTI_KODA_I_N_ATNAUJINTI_VISUS = 2; /*Apibrėžiamas rašymo į tam tikro SAK išėjimo (n) įėjimo registrą
                                                      bei visų išėjimų SAK registrų atnaujinimo komandos kodas*/
const uint8_t RASYTI_KODA_I_VISUS_ATNAUJINTI_VISUS = 10; /*Apibrėžiamas rašymo į visų SAK išėjimų įėjimų registrus
                                                          bei visų išėjimų SAK registrų atnaujinimo komandos kodas*/

const uint16_t DIAPAZONAS_0_5   = 0x00; //Diapazono nuo 0V iki 5V nustatymo komandos duomenų dalis
const uint16_t DIAPAZONAS_0_10  = 0x01; //Diapazono nuo 0V iki 10V nustatymo komandos duomenų dalis
const uint16_t DIAPAZONAS_5_5   = 0x02; //Diapazono nuo -5V iki 5V nustatymo komandos duomenų dalis
const uint16_t DIAPAZONAS_10_10 = 0x03; //Diapazono nuo -10V iki 10V nustatymo komandos duomenų dalis
const uint16_t DIAPAZONAS_2_5_2_5 = 0x04; //Diapazono nuo -2.5V iki 2.5V nustatymo komandos duomenų dalis

const uint8_t DONTCARE = 0; // Nereikšmingo baito apibrėžimas, kuris naudojamas kai sudaromas 32 bitų paketas
// unsigned long int currentTime = 0;



#line 58 "C:\\Users\\Andrej Scerbickis\\OneDrive - Vilniaus Gedimino technikos universitetas\\Dokumentai\\univer\\bakalauras\\4Cs4Vs_test_bench_app\\dds_algorithm\\dds_algorithm.ino"
void setupParameters();
#line 87 "C:\\Users\\Andrej Scerbickis\\OneDrive - Vilniaus Gedimino technikos universitetas\\Dokumentai\\univer\\bakalauras\\4Cs4Vs_test_bench_app\\dds_algorithm\\dds_algorithm.ino"
void valdytiSAK(uint8_t komanda, uint8_t adresas, uint16_t duomenys);
#line 102 "C:\\Users\\Andrej Scerbickis\\OneDrive - Vilniaus Gedimino technikos universitetas\\Dokumentai\\univer\\bakalauras\\4Cs4Vs_test_bench_app\\dds_algorithm\\dds_algorithm.ino"
void setup();
#line 115 "C:\\Users\\Andrej Scerbickis\\OneDrive - Vilniaus Gedimino technikos universitetas\\Dokumentai\\univer\\bakalauras\\4Cs4Vs_test_bench_app\\dds_algorithm\\dds_algorithm.ino"
void loop();
#line 58 "C:\\Users\\Andrej Scerbickis\\OneDrive - Vilniaus Gedimino technikos universitetas\\Dokumentai\\univer\\bakalauras\\4Cs4Vs_test_bench_app\\dds_algorithm\\dds_algorithm.ino"
void setupParameters() {
  
  parameter_id = Serial.read(); // Read the parameter id from the serial port

  switch(parameter_id){
    
    case 0x46: // 0x46 is Ascii for 'F'. If the parameter id is 0x46, read the step size from the serial port
      M = (Serial.read() << 8) | Serial.read(); // Shift the byte by 8 bits
      break;
    
    case 0x41: // 0x41 is Ascii for 'A'. If the parameter id is 0x41, read the amplitude from the serial port
      amplitude = (Serial.read() << 8) | Serial.read(); // Shift the byte by 8 bits
      break;  
    
    default: // If the parameter id is not 0x46 or 0x41, break the switch statement
      break;
  }

  for (i = 0; i < L; i++) {
    float angle = i * step;
    voltageLookupTable[i] = (uint16_t)(amplitude * (sin(angle) + 1)/2); // Scale sine values to the range of 0-65535
  }

  for (i = 0; i < L; i++) {
    float angle = i * step;
    currentLookupTable[i] = (uint16_t)(amplitude * (sin(angle) + 1)/2); // Scale sine values to the range of 0-65535
  }
}

void valdytiSAK(uint8_t komanda, uint8_t adresas, uint16_t duomenys) {
  /*Šį funkciją naudojama SAK valdymui per SPI sąsają*/

   /*Atliekant komandinio baito loginį poslinkį keturiais bitais į kaire
                                                ir atliekant loginį sumavimą su adreso baitu, sukuriamas paketo antraštės baitas*/
  Breakout.digitalWrite(spi_cs, LOW); /*Pradedamas duomenų perdavimas su SAK'u, nustatant Lusto Pasirinkimo kaiščio
                                        išėjimo įtampos lygį į žemą*/
  Breakout.SPI_0.transfer((komanda << 4) | adresas); // Antraštės baito siuntimas   
  Breakout.SPI_0.transfer16(duomenys); // Dviejų baitų duomenų siuntimas 

  Breakout.digitalWrite(spi_cs, HIGH); /*Baigiamas duomenų perdavimas su SAK'u, nustatant Lusto Pasirinkimo kaiščio
                                        išėjimo įtampos lygį į aukštą*/

}

void setup() {

  Serial.begin(115200);
  
  Breakout.SPI_0.begin(); //Inicializuojama SPI magistralė
  Breakout.SPI_0.beginTransaction(SPISettings(30e6, MSBFIRST, SPI_MODE0)); //SPI komunikacijos parametrų nustatymas
  pinMode(spi_cs, OUTPUT); //Lusto išrinkimo kaištis nustatomas į išvesties režimą
  valdytiSAK(RASYTI_DIAPAZONA_I_VISUS, DONTCARE, DIAPAZONAS_0_5); //Visų SAK išėjimų diapazonų nustatymo komanda

  setupParameters(); // Call the setup function

}

void loop() {

  if (Serial.available() > 0) { // if there is data available on the serial port
      if (Serial.read() == 0x53) setupParameters(); // if the received byte is 0x53, call the setup function
    }

    valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N, 0, voltageLookupTable[t1]); 
    valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N, 1, voltageLookupTable[t2]); 
    valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N, 2, voltageLookupTable[t3]); 

    valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N, 4, currentLookupTable[t1]);
    valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N, 5, currentLookupTable[t2]); 
    valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N, 6, currentLookupTable[t3]); 

    t1 = t1 + M;
    t2 = t2 + M;
    t3 = t3 + M;
}

