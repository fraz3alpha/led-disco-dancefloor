      
//############################################################################################################################################################
//Externe Bibliotheken einbinden                                                                                                                             #
//############################################################################################################################################################

#include <avr/pgmspace.h>

//############################################################################################################################################################
//Programmspeicher beschreiben                                                                                                                               #
//############################################################################################################################################################

//Exponentialfunktion für Gamma-Korrektur
PROGMEM prog_uint16_t exp_table[] =
{ 
0,15,15,16,16,16,17,17,17,18,18,19,19,20,20,20,21,21,22,22,23,23,24,24,25,25,26,27,27,28,28,29,30,30,31,32,32,33,34,35,35,36,37,38,39,39,40,41,42,43,44,45,46,
47,48,49,50,51,53,54,55,56,57,59,60,61,63,64,65,67,68,70,72,73,75,76,78,80,82,83,85,87,89,91,93,95,97,99,102,104,106,109,111,114,116,119,121,124,127,130,132,
135,138,141,145,148,151,154,158,161,165,169,172,176,180,184,188,192,197,201,206,210,215,220,225,230,235,240,245,251,256,262,268,274,280,286,292,299,305,312,319,
326,334,341,349,356,364,372,381,389,398,407,416,425,434,444,454,464,474,485,496,507,518,529,541,553,566,578,591,604,618,631,645,660,674,689,705,720,736,753,770,
787,804,822,840,859,878,898,918,938,959,980,1002,1024,1047,1070,1094,1119,1143,1169,1195,1221,1249,1276,1305,1334,1364,1394,1425,1457,1489,1522,1556,1591,1626,
1662,1699,1737,1775,1815,1855,1897,1939,1982,2026,2071,2117,2164,2212,2262,2312,2363,2416,2470,2524,2581,2638,2697,2757,2818,2881,2945,3010,3077,3146,3216,3287,
3360,3435,3511,3590,3669,3751,3834,3920,4007,4095
};

//############################################################################################################################################################
//Definitionen und Variablen                                                                                                                                 #
//############################################################################################################################################################

//Gray Scale Depth for the PWM on TLC5940
#define Gray_Scale_Depth 4095

//GSCLK an PD6 (Arduino Pin 6)
#define GSCLK_Low       PORTD &=  ~(1 << 6)
#define GSCLK_High      PORTD |=   (1 << 6)

//XLAT an PD4 (Arduino Pin 4)
#define XLAT_Low       PORTD &=  ~(1 << 4)
#define XLAT_High      PORTD |=   (1 << 4)

//GSCK an PD5 (Arduino Pin 5)
#define GSCK_Low       PORTD &=  ~(1 << 5)
#define GSCK_High      PORTD |=   (1 << 5)

//VPRG an PD3 (Arduino Pin 3)
#define VPRG_Low       PORTD &=  ~(1 << 3)
#define VPRG_High      PORTD |=   (1 << 3)

//BLANK an PB1 (Arduino Pin 9)
#define BLANK_Low       PORTB &=  ~(1 << 1)
#define BLANK_High      PORTB |=   (1 << 1)

//SCLK an PB5 (Arduino Pin 13)
#define SCLK_Low       PORTB &=  ~(1 << 5)
#define SCLK_High      PORTB |=   (1 << 5)

//MOSI an PB3 (Arduino Pin 11)
#define MOSI_Low       PORTB &=  ~(1 << 3)
#define MOSI_High      PORTB |=   (1 << 3)

//Debug an PD7 (Arduino Pin 7)
#define Debug_Low       PORTD &=  ~(1 << 7)
#define Debug_High      PORTD |=   (1 << 7)

# define CMD_NEW_DATA 1

#define MODULE_WIDTH 6
#define MODULE_HEIGHT 8
#define RGB_LEDS MODULE_HEIGHT * MODULE_WIDTH
#define BUFFER_SIZE MODULE_WIDTH*MODULE_HEIGHT*3

unsigned char display_buffer_1[BUFFER_SIZE];
unsigned char display_buffer_2[BUFFER_SIZE];
static unsigned char *display_buffer = display_buffer_1;

volatile byte display_buffer_live = 1;

volatile byte new_row = 0;
volatile byte need_xlat = 0;

static unsigned char *ptr;
static unsigned int pos = 0;

byte row = 0;

unsigned long tickcounter = 0;
unsigned long lastdata_tickcounter = 0;
// 40000 = 20 seconds
unsigned long timeout = 40000;

volatile boolean cycling = false;
// 1000 ~ 1/2 second
unsigned long cycle_period = 1000;
unsigned long cycle_tickcounter = 0;

unsigned long colours[] = {0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0x00FFFF, 0xFF00FF, 0xFFFFFF};

void set_initial_pattern(void) {
  set_random_colours();
}

void set_random_colours() {
  int colours_length = 7;
  for (int pixel=0; pixel < RGB_LEDS; pixel++) {
    unsigned long colour = colours[random(colours_length)];
    display_buffer[pixel * 3 + 0] = colour & 0xFF;
    display_buffer[pixel * 3 + 1] = (colour >> 8 ) & 0xFF;
    display_buffer[pixel * 3 + 2] = (colour >> 16) & 0xFF;   
  }
  
}

//############################################################################################################################################################
//Setup - Prozedur                                                                                                                                           #
//############################################################################################################################################################

void setup()   
{               
  // Pins auf Ein- oder Ausgang stellen und einen Startwert zuweisen 
  DDRB |= (1<<1)  | (1<<2)  | (1<<3) | (1<<5) ; // BLANK, SS, MOSI, SCLK as OUTPUTS
  DDRD |= (1<<3)  | (1<<4) |  (1<<6) | (1<<7) ; // VPRG, XLAT, GSCLK, Debug as OUTPUTS
  DDRC = 255;
  
  XLAT_Low;
  BLANK_High;
  VPRG_Low;
  Debug_Low;
  
  set_initial_pattern();
       
  //Timer 1 (16bit)
  TCCR1A  = (1<<WGM11) | (0<<WGM10);            // Fast PWM with ICR1 as top
  TCCR1B  = (1<<WGM13) | (1<<WGM12);            // Fast PWM with ICR1 as top
  TCCR1B |= (1<<CS12)  | (1<<CS11) | (1<<CS10); // external clock (T1) on rising egde
  TIMSK1 |= (1<<TOIE1);                         // enable overflow interupt
  ICR1    = Gray_Scale_Depth;                   // Grey scale depth for TLC-PW

  //Timer 0 (8bit)
  TCCR0A  = (1<<WGM01) | (0<<WGM00);            // CTC
  TCCR0A |= (0<<COM0A1) | (1<<COM0A0);          // Toggle on Compare Match
  TCCR0B  = (0<<CS02) | (0<<CS01) | (1<<CS00);  // No Prescaler
  OCR0A   = 0;                                  // f(OCR) = F_CPU/2/Prescaler
  
  //UART Initialisation
  UCSR0A |= (1<<U2X0);                                 // Double up UART
  UCSR0B |= (1<<RXEN0)  | (1<<TXEN0) | (1<<RXCIE0);    // UART RX, TX und RX Interrupt enable
  UCSR0C |= (1<<UCSZ01) | (1<<UCSZ00)             ;    // Asynchrous 8N1 
  UBRR0H = 0;
  UBRR0L = 1; //Baud Rate 1 MBit   --> 0% Error at 16MHz :-)
  
  //Enable global interrupts
  sei();
   
  //Configure SPI  
  SPCR = (1<<SPE)|(1<<MSTR);  
  SPSR = B00000000;   
  
  /*ptr=display_buffer_2;
  display_buffer = display_buffer_1;
  display_buffer_live = 1;
    */
  ptr = display_buffer;
}

void flip_buffers() {
  if (display_buffer_live == 1) {
    display_buffer_live = 2;
    display_buffer = display_buffer_2;
    ptr = display_buffer_1;
  } else {
    display_buffer_live = 1;
    display_buffer = display_buffer_1;
    ptr = display_buffer_2;
  }
  lastdata_tickcounter = tickcounter;
  cycling = false;
  
}

//############################################################################################################################################################
//Hauptprogramm                                                                                                                                              #
//############################################################################################################################################################

void loop()        
{     
  if (new_row)
  {    
    shift_out_data(row);
            
    need_xlat = 1;
                                              
    new_row = 0;   
    tickcounter++;

   
    // If we are cycling, then see if we need to cycle again
    if (cycling == true) {
      if (tickcounter - cycle_tickcounter > cycle_period) {
        set_random_colours();
        cycle_tickcounter = tickcounter;
      }
    } else {
      // If we aren't cycling, then see if we need to start
      if (tickcounter - lastdata_tickcounter > timeout) {
        cycling = true;
      }
    }

  }
}

//############################################################################################################################################################
// Timer-Interrupt-Prozedur                                                                                                                                  #
//############################################################################################################################################################

ISR( TIMER1_OVF_vect )
{  
    
  if (need_xlat)
  {
    XLAT_High;
    XLAT_Low;
    need_xlat = 0;
  }
  
  PORTC = ~(1<<row);
  
  BLANK_High; 
  BLANK_Low;
  
  row++;
  if (row == 3) {row = 0;}
  new_row = 1;
  
  TCNT1 = 0;
}

//############################################################################################################################################################
// UART-Interrupt-Prozedur (called every time one byte is compeltely received)                                                                               #
//############################################################################################################################################################

ISR(USART_RX_vect) 
{
  unsigned char b;
  
  b=UDR0;
  
  if (b == CMD_NEW_DATA)  {
    UDR0=b; 
    pos=0; 
    ptr=display_buffer;
    // Flip buffers to make the live one the one we have just populated, 
    //  and the temporary one containing incoming data, the other one
    //flip_buffers();
    lastdata_tickcounter = tickcounter;
    cycling = false;
    return;
  }    
  if (pos == BUFFER_SIZE) {
    UDR0=b; 
    return;
  } else {
    *ptr=b; 
    ptr++; 
    pos++;
  }  
}

//############################################################################################################################################################
// Shift out Data                                                                                                                                            #
//############################################################################################################################################################

void shift_out_data(byte row)
{
  
//    unsigned int index_offset = (row) * 48; 
  
    //Shift Out Data
    for(byte i = 0; i<24; i++)
    {
      unsigned int index = 6*(i) + row;
      unsigned int t1 = pgm_read_word_near(exp_table + display_buffer[index + 3]);
      unsigned int t2 = pgm_read_word_near(exp_table + display_buffer[index]);
     
      byte d1 = (highByte(t2) << 4) | (lowByte(t2) >> 4);
      spi_transfer(d1);
      
      byte d2 = (lowByte(t2) << 4) | (highByte(t1));
      spi_transfer(d2);
     
      byte d3 = (lowByte(t1)); 
      spi_transfer(d3);      
    }
  
/*
    unsigned int index_offset = (row) * 48; 
  
    //Shift Out Blue Data
    for(byte i = 0; i<8; i++)
    {
      unsigned int index = index_offset + 6*(i) + 2;
      unsigned int t1 = pgm_read_word_near(exp_table + display_buffer[index + 3]);
      unsigned int t2 = pgm_read_word_near(exp_table + display_buffer[index]);
     
      byte d1 = (highByte(t2) << 4) | (lowByte(t2) >> 4);
      spi_transfer(d1);
      
      byte d2 = (lowByte(t2) << 4) | (highByte(t1));
      spi_transfer(d2);
     
      byte d3 = (lowByte(t1)); 
      spi_transfer(d3);      
    }
    
    //Shift Out Green Data
    for(byte i = 0; i<8; i++)
    {
      unsigned int index = index_offset + 6*(i) + 1;
      unsigned int t1 = pgm_read_word_near(exp_table + display_buffer[index + 3]);
      unsigned int t2 = pgm_read_word_near(exp_table + display_buffer[index]);
     
      byte d1 = (highByte(t2) << 4) | (lowByte(t2) >> 4);
      spi_transfer(d1);
      
      byte d2 = (lowByte(t2) << 4) | (highByte(t1));
      spi_transfer(d2);
     
      byte d3 = (lowByte(t1)); 
      spi_transfer(d3);      
    }
           
    //Shift Out Red Data
    for(byte i = 0; i<8; i++)
    {
      unsigned int index = index_offset + 6*(i);
      unsigned int t1 = pgm_read_word_near(exp_table + display_buffer[index + 3]);
      unsigned int t2 = pgm_read_word_near(exp_table + display_buffer[index]);
     
      byte d1 = (highByte(t2) << 4) | (lowByte(t2) >> 4);
      spi_transfer(d1);
      
      byte d2 = (lowByte(t2) << 4) | (highByte(t1));
      spi_transfer(d2);
     
      byte d3 = (lowByte(t1)); 
      spi_transfer(d3);      
    }
*/
  
}
//############################################################################################################################################################
// SPI-Prozedur                                                                                                                                              #
//############################################################################################################################################################

void spi_transfer(byte data)
{
  SPDR = data;	  // Start the transmission
  while (!(SPSR & (1<<SPIF)))     // Wait the end of the transmission
  {
  };
}




//############################################################################################################################################################
//############################################################################################################################################################
//############################################################################################################################################################

