#include <Arduino.h>
#line 1 "C:\\Users\\Andrej Scerbickis\\OneDrive - Vilniaus Gedimino technikos universitetas\\Dokumentai\\univer\\bakalauras\\4Cs4Vs_test_bench_app\\test_bench_fw\\test_bench_fw.ino"
#include <Arduino_PortentaBreakout.h>

breakoutPin spi_cs   = SPI1_CS; //Apibrėžiamas Breakout plokštės SPI sąsajos Chip Select kaištis
breakoutPin spi_ck   = SPI1_CK; //Apibrėžiamas Breakout plokštės SPI sąsajos Clock kaištis
breakoutPin spi_miso = SPI1_CIPO; //Apibrėžiamas Breakout plokštės SPI sąsajos Controller In Peripheral Out kaištis
breakoutPin spi_mosi = SPI1_COPI; //Apibrėžiamas Breakout plokštės SPI sąsajos Controller Out Peripheral In kaištis

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

const uint8_t SAK0_adresas = 0; // Pirmo SAK'o adresas
const uint8_t SAK1_adresas = 1; // Antro SAK'o adresas
const uint8_t SAK2_adresas = 2; // Trečio SAK'o adresas
const uint8_t SAK3_adresas = 3; // Ketvirto SAK'o adresas
const uint8_t SAK4_adresas = 4; // Penkto SAK'o adresas
const uint8_t SAK5_adresas = 5; // Šešto SAK'o adresas
const uint8_t SAK6_adresas = 6; // Septinto SAK'o adresas
const uint8_t SAK7_adresas = 7; // Aštunto SAK'o adresas

const uint16_t DIAPAZONAS_0_5   = 0x00; //Diapazono nuo 0V iki 5V nustatymo komandos duomenų dalis
const uint16_t DIAPAZONAS_0_10  = 0x01; //Diapazono nuo 0V iki 10V nustatymo komandos duomenų dalis
const uint16_t DIAPAZONAS_5_5   = 0x02; //Diapazono nuo -5V iki 5V nustatymo komandos duomenų dalis
const uint16_t DIAPAZONAS_10_10 = 0x03; //Diapazono nuo -10V iki 10V nustatymo komandos duomenų dalis
const uint16_t DIAPAZONAS_2_5_2_5 = 0x04; //Diapazono nuo -2.5V iki 2.5V nustatymo komandos duomenų dalis
const uint8_t DONTCARE = 0; // Nereikšmingo baito apibrėžimas, kuris naudojamas kai sudaromas 32 bitų paketas
uint16_t itamposIsejimoDiapazonas = DIAPAZONAS_2_5_2_5;

const float faze[] = {0, 2*PI/3, 4*PI/3}; //Kiekvienos fazės srovės signalų fazių poslinkių apibrėžimas (tarp kiekvienos 120 laipsnių)
uint16_t amplitude = 0xFFFF; //Maksimalios amplitudės vertės apibrėžimas 16 bitų SAK'o atveju
float f = 50.0; //Fundamentaliosios harmonikos dažnis
float fs = 5.0e4; //Diskretizavimo dažnis
float apkrova1[] = {1, 0, 0}; //Pirmos fazės nuosekliai prijungtos apkrovos RLC parametrų vertės
float apkrova2[] = {1, 0, 0}; //Antros fazės nuosekliai prijungtos apkrovos RLC parametrų vertės
float apkrova3[] = {1, 0, 0}; //Trečios fazės nuosekliai prijungtos apkrovos RLC parametrų vertės
uint8_t kiekvienosFazesHarmonikuSkaicius[] = {0, 0, 0}; //Kiekvienos fazės harmonikų skaičius
char kiekvienosFazesHarmonikuLyginumas[] = {'N', 'N', 'N'}; /*Kiekvienos fazės harmonikų lyginumas (variantai: 'E' - lyginės,
                                                  'O' - nelyginės, 'B' - lyginės ir nelyginės,
                                                  'N' - bet koks kitas simbolis kai nėra harmonikų)*/
double t = 0.0; //Laiko kintamojo apibrėžimas

#line 51 "C:\\Users\\Andrej Scerbickis\\OneDrive - Vilniaus Gedimino technikos universitetas\\Dokumentai\\univer\\bakalauras\\4Cs4Vs_test_bench_app\\test_bench_fw\\test_bench_fw.ino"
void setup();
#line 60 "C:\\Users\\Andrej Scerbickis\\OneDrive - Vilniaus Gedimino technikos universitetas\\Dokumentai\\univer\\bakalauras\\4Cs4Vs_test_bench_app\\test_bench_fw\\test_bench_fw.ino"
void loop();
#line 130 "C:\\Users\\Andrej Scerbickis\\OneDrive - Vilniaus Gedimino technikos universitetas\\Dokumentai\\univer\\bakalauras\\4Cs4Vs_test_bench_app\\test_bench_fw\\test_bench_fw.ino"
uint16_t generuotiHarmonikas(uint16_t amplitude, float f, float t, float faze, int aukstesniuHarmonikuSkaicius, char lyginumas);
#line 160 "C:\\Users\\Andrej Scerbickis\\OneDrive - Vilniaus Gedimino technikos universitetas\\Dokumentai\\univer\\bakalauras\\4Cs4Vs_test_bench_app\\test_bench_fw\\test_bench_fw.ino"
uint16_t gautiApkrovosImpedansa(float apkrova[], float f);
#line 169 "C:\\Users\\Andrej Scerbickis\\OneDrive - Vilniaus Gedimino technikos universitetas\\Dokumentai\\univer\\bakalauras\\4Cs4Vs_test_bench_app\\test_bench_fw\\test_bench_fw.ino"
float gautiApkrovosFazesPoslinki(float apkrova[], float f);
#line 178 "C:\\Users\\Andrej Scerbickis\\OneDrive - Vilniaus Gedimino technikos universitetas\\Dokumentai\\univer\\bakalauras\\4Cs4Vs_test_bench_app\\test_bench_fw\\test_bench_fw.ino"
void valdytiSAK(uint8_t komanda, uint8_t adresas, uint16_t duomenys);
#line 51 "C:\\Users\\Andrej Scerbickis\\OneDrive - Vilniaus Gedimino technikos universitetas\\Dokumentai\\univer\\bakalauras\\4Cs4Vs_test_bench_app\\test_bench_fw\\test_bench_fw.ino"
void setup() {
  Serial.begin(115200);
  while (!Serial);
  Breakout.SPI_0.begin(); //Inicializuojama SPI magistralė
  Breakout.SPI_0.beginTransaction(SPISettings(35e6, MSBFIRST, SPI_MODE0)); //SPI komunikacijos parametrų nustatymas
  pinMode(spi_cs, OUTPUT); //Lusto išrinkimo kaištis nustatomas į išvesties režimą
  valdytiSAK(RASYTI_DIAPAZONA_I_VISUS,DONTCARE,itamposIsejimoDiapazonas); //Visų SAK išėjimų diapazonų nustatymo komanda
}

void loop() {

  float phi1 = gautiApkrovosFazesPoslinki(apkrova1,f); // Pirmos fazės įtampos fazės poslinkis
  float phi2 = gautiApkrovosFazesPoslinki(apkrova2,f); // Antros fazės įtampos fazės poslinkis
  float phi3 = gautiApkrovosFazesPoslinki(apkrova3,f); // Trečios fazės įtampos fazės poslinkis

  // Pirmos fazės įtampos taškų generavimas
  uint16_t u1 = generuotiHarmonikas(amplitude,f,t,faze[0]+phi1,kiekvienosFazesHarmonikuSkaicius[0],kiekvienosFazesHarmonikuLyginumas[0]);
  // Antros fazės įtampos taškų generavimas
  uint16_t u2 = generuotiHarmonikas(amplitude,f,t,faze[1]+phi2,kiekvienosFazesHarmonikuSkaicius[1],kiekvienosFazesHarmonikuLyginumas[1]); 
  // Trečios fazės įtampos taškų generavimas
  uint16_t u3 = generuotiHarmonikas(amplitude,f,t,faze[2]+phi3,kiekvienosFazesHarmonikuSkaicius[2],kiekvienosFazesHarmonikuLyginumas[2]);
  uint16_t uN = u1+u2+u3; // Nulinio laido įtampos taškų apskaičiavimas

  // Pirmos fazės srovės signalaso taškų generavimas
  uint16_t i1 = generuotiHarmonikas(amplitude/gautiApkrovosImpedansa(apkrova1,f),f,t,faze[0],
                                                                      kiekvienosFazesHarmonikuSkaicius[0],kiekvienosFazesHarmonikuLyginumas[0]);
  // Antros fazės srovės signalaso taškų generavimas
  uint16_t i2 = generuotiHarmonikas(amplitude/gautiApkrovosImpedansa(apkrova2,f),f,t,faze[1],
                                                                      kiekvienosFazesHarmonikuSkaicius[1],kiekvienosFazesHarmonikuLyginumas[1]);
  // Trečios fazės srovės signalaso taškų generavimas
  uint16_t i3 = generuotiHarmonikas(amplitude/gautiApkrovosImpedansa(apkrova3,f),f,t,faze[2],
                                                                      kiekvienosFazesHarmonikuSkaicius[2],kiekvienosFazesHarmonikuLyginumas[2]);
  uint16_t iN = i1+i2+i3; // Nulinio laido srovės signalaso taškų apskaičiavimas

  /*Galio parametrų apskaičiavimas*/
  uint16_t S1 = u1*i1; // Pirmos fazės pilnutinės galios apskaičiavimas
  uint16_t S2 = u2*i2; // Antros fazės pilnutinės galios apskaičiavimas
  uint16_t S3 = u3*i3; // Trečios fazės pilnutinės galios apskaičiavimas

  float galiosKoeficientas1 = cos(phi1); // Pirmos fazės galios koeficientas
  float galiosKoeficientas2 = cos(phi2); // Antros fazės galios koeficientas
  float galiosKoeficientas3 = cos(phi3); // Trečios fazės galios koeficientas

  float P1 = u1*i1*galiosKoeficientas1; // Pirmos fazės pilnutinės galios apskaičiavimas
  float P2 = u2*i2*galiosKoeficientas2; // Antros fazės pilnutinės galios apskaičiavimas
  float P3 = u3*i3*galiosKoeficientas3; // Trečios fazės pilnutinės galios apskaičiavimas

  float Q1 = u1*i1*sin(phi1); // Pirmos fazės pilnutinės galios apskaičiavimas
  float Q2 = u2*i2*sin(phi2); // Pirmos fazės pilnutinės galios apskaičiavimas
  float Q3 = u3*i3*sin(phi3); // Pirmos fazės pilnutinės galios apskaičiavimas
  
  valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N,SAK0_adresas,u1); /*Pirmojo SAK išėjimo įėjimo registro užpildymas pirmos fazės įtampos signalaso momentine verte
                                                              ir SAK registro vertės atnaujinimo komandos siuntimas*/
  valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N,SAK1_adresas,u2); /*Antrojo SAK išėjimo įėjimo registro užpildymas antros fazės įtampos signalaso momentine verte
                                                                                                                          ir SAK registro vertės atnaujinimo komandos siuntimas*/
  valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N,SAK2_adresas,u3); /*Trečiojo SAK išėjimo įėjimo registro užpildymas trečios fazės įtampos signalaso momentine verte
                                                                                                                          ir SAK registro vertės atnaujinimo komandos siuntimas*/
  valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N,SAK3_adresas,uN); /*Ketvirtojo SAK išėjimo įėjimo registro užpildymas nulinio laido įtampos signalaso momentine verte
                                                                                                                          ir SAK registro vertės atnaujinimo komandos siuntimas*/
  valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N,SAK4_adresas,i1); /*Penktojo SAK išėjimo įėjimo registro užpildymas pirmos fazės srovės signalaso momentine verte
                                                                                                                          ir SAK registro vertės atnaujinimo komandos siuntimas*/
  valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N,SAK5_adresas,i2); /*Šeštojo SAK išėjimo įėjimo registro užpildymas antros fazės srovės signalaso momentine verte
                                                                                                                          ir SAK registro vertės atnaujinimo komandos siuntimas*/
  valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N,SAK6_adresas,i3); /*Septintojo SAK išėjimo įėjimo registro užpildymas trečios fazės srovės signalaso momentine verte
                                                                                                                          ir SAK registro vertės atnaujinimo komandos siuntimas*/
  valdytiSAK(RASYTI_KODA_I_N_ATNAUJINTI_N,SAK7_adresas,iN); /*Aštuntojo SAK išėjimo įėjimo registro užpildymas nulinio laido srovės signalaso momentine verte
                                                                                                                          ir SAK registro vertės atnaujinimo komandos siuntimas*/
  Serial.print("{{u1}}:"); Serial.print(u1); Serial.print(", ");
  Serial.print("{{u2}}:"); Serial.print(u2); Serial.print(", ");
  Serial.print("{{u3}}:"); Serial.print(u3); Serial.print(", ");
  Serial.print("{{uN}}:"); Serial.print(uN); Serial.print(", ");
  Serial.print("{{i1}}:"); Serial.print(i1); Serial.print(", ");
  Serial.print("{{i2}}:"); Serial.print(i2); Serial.print(", ");
  Serial.print("{{i3}}:"); Serial.print(i3); Serial.print(", ");
  Serial.print("{{iN}}:"); Serial.println(iN);

  t += 1.0/fs; // Laiko kintamojo inkremintavimas
}

uint16_t generuotiHarmonikas(uint16_t amplitude, float f, float t, float faze, int aukstesniuHarmonikuSkaicius, char lyginumas){
  float signalas = amplitude * (sin(2*PI*f*t + faze) + 1)/2; /*Pagrindinės įtampos signalo harmonikos apibrėžimas.
                                                              Sinusoidė yra pakelta ir normuota, taip kad jos verčių diapazonas yra
                                                              tarp 0 ir 1 imtinai.*/
  // Toliau pridedamos tam tikro lyginumo tam tikras harmonikų skaičius
  switch(lyginumas){ 
    case 'E': //E  reiškia 'Even' (lyginis)
      for(int h = 1; h<=aukstesniuHarmonikuSkaicius; h++){
        signalas += amplitude/(2*h) * (sin(2*h*(2*PI*f*t + faze)))/2; /*Kiekvienos harmonikos amplitudė mažėja, o dažnis didėja du kart
                                                                        harmonikos indekso skaičiumi*/
      }
      break;
    case 'O': //O  reiškia 'Odd' (nelyginis)
      for(int h = 1; h<=aukstesniuHarmonikuSkaicius; h++){
        signalas += amplitude/(2*h+1) * (sin((2*h+1)*(2*PI*f*t + faze)))/2;
        // Kiekvienos harmonikos amplitudė mažėja, o dažnis didėja 2*i+1 skaičiumi, kur i yra harmonikos indeksas.
      }
      break;
    case 'B': //B  reiškia 'Both' (abu)
      for(int h = 1; h<=aukstesniuHarmonikuSkaicius; h++){
        signalas += amplitude/(h+1) * (sin((h+1)*(2*PI*f*t + faze)))/2;
        // Kiekvienos harmonikos amplitudė mažėja, o dažnis didėja i+1 kartu, kur i yra harmonikos indeksas
      }
      break;
    default: // Jei įvestas bet koks kitoks simbolis tai šitoje dalyje nieko nedaroma
      break;    
  }
  return word(signalas); // Grąžinamas signalas, konvertuotas į uint16_t tipą.
}

uint16_t gautiApkrovosImpedansa(float apkrova[], float f){
  uint16_t Z; // Impedanso kintamojo apibrėžimas
  // Jeigu talpos vertė lygi nuliui, talpinė varža neapskaičiuojama, taip išvengiant dalybos iš nulio.
  if(apkrova[2]==0) Z = word(sqrt(sq(apkrova[0])+sq(2*PI*f*apkrova[1]))); // Z=sqrt(R^2+XL^2)
  // Kitu atveju impedansas apskaičiuojamas pagal pilną formulę Z=sqrt(R^2+(XL-XC)^2)
  else Z = word(sqrt(sq(apkrova[0])+sq(2*PI*f*apkrova[1]-1/(2*PI*f*apkrova[2]))));
  return Z;
}

float gautiApkrovosFazesPoslinki(float apkrova[], float f){
  float phi; // Reaktyviąja apkrovos dalimi sukurtas įtampos signalo fazės poslinkio apibrėžimas
  // Jeigu talpos vertė lygi nuliui, talpinė varža neapskaičiuojama, taip išvengiant dalybos iš nulio.
  if(apkrova[2]==0) phi = float(atan((2*PI*f*apkrova[1])/apkrova[0])); // atan(XL/R)
  // Kitu atveju fazes poslinkis apskaičiuojamas pagal pilną formulę atan((XL-XC)/R)
  else phi = float(atan((2*PI*f*apkrova[1]-1/(2*PI*f*apkrova[2]))/apkrova[0]));
  return phi;
}

void valdytiSAK(uint8_t komanda, uint8_t adresas, uint16_t duomenys) {
  /*Šį funkciją naudojama SAK valdymui per SPI sąsają*/

  uint8_t antraste = (komanda << 4) | adresas; /*Atliekant komandinio baito loginį poslinkį keturiais bitais į kaire
                                                ir atliekant loginį sumavimą su adreso baitu, sukuriamas paketo antraštės baitas*/
  Breakout.digitalWrite(spi_cs, LOW); /*Pradedamas duomenų perdavimas su SAK'u, nustatant Lusto Pasirinkimo kaiščio
                                        išėjimo įtampos lygį į žemą*/
  Breakout.SPI_0.transfer(antraste); // Antraštės baito siuntimas   
  Breakout.SPI_0.transfer16(duomenys); // Dviejų baitų duomenų siuntimas 

  Breakout.digitalWrite(spi_cs, HIGH); /*Baigiamas duomenų perdavimas su SAK'u, nustatant Lusto Pasirinkimo kaiščio
                                        išėjimo įtampos lygį į aukštą*/

}

