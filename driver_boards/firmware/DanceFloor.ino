// AndyT's Dance Floor controller code. 
// Adapted from the original by solderlab.de

// One AVR drives 3 TLC5940 constant current LED drivers, for a total of 48 LEDs.
// LEDs are common cathode, with the TLC5940 connected to the cathode, and high side 
//  P-channel FETs providing the drive. 
// The FETs cycle RED/GREEN/BLUE along with changing TLC5940 data to give the illusion of
//  constant RGB colour when in fact only one is on at any given time.

// Data can be received from a PC through the serial port at 1000000 baud (1Mbps)

// If no data is received in several seconds then the module starts to set the LEDs to random
//  pure colours, changing 2 times a second

// Include the pgmspace header for storing the gamma correction tables
#include <avr/pgmspace.h>

// LEDs do not have a linear response curve, and particularly when they are driven by PWM.
// Here we have three curves to adjust the brightness to match human vision. 
// (Currently these are all identical, and follow an exponential curve, and need to be tuned)
PROGMEM prog_uint16_t exp_table_red[] =
{ 
  0,15,15,16,16,16,17,17,17,18,18,19,19,20,20,20,21,21,22,22,23,23,24,24,25,25,26,27,27,28,28,29,30,30,31,32,32,33,34,35,35,36,37,38,39,39,40,41,42,43,44,45,46,
  47,48,49,50,51,53,54,55,56,57,59,60,61,63,64,65,67,68,70,72,73,75,76,78,80,82,83,85,87,89,91,93,95,97,99,102,104,106,109,111,114,116,119,121,124,127,130,132,
  135,138,141,145,148,151,154,158,161,165,169,172,176,180,184,188,192,197,201,206,210,215,220,225,230,235,240,245,251,256,262,268,274,280,286,292,299,305,312,319,
  326,334,341,349,356,364,372,381,389,398,407,416,425,434,444,454,464,474,485,496,507,518,529,541,553,566,578,591,604,618,631,645,660,674,689,705,720,736,753,770,
  787,804,822,840,859,878,898,918,938,959,980,1002,1024,1047,1070,1094,1119,1143,1169,1195,1221,1249,1276,1305,1334,1364,1394,1425,1457,1489,1522,1556,1591,1626,
  1662,1699,1737,1775,1815,1855,1897,1939,1982,2026,2071,2117,2164,2212,2262,2312,2363,2416,2470,2524,2581,2638,2697,2757,2818,2881,2945,3010,3077,3146,3216,3287,
  3360,3435,3511,3590,3669,3751,3834,3920,4007,4095
};

PROGMEM prog_uint16_t exp_table_green[] =
{ 
  0,15,15,16,16,16,17,17,17,18,18,19,19,20,20,20,21,21,22,22,23,23,24,24,25,25,26,27,27,28,28,29,30,30,31,32,32,33,34,35,35,36,37,38,39,39,40,41,42,43,44,45,46,
  47,48,49,50,51,53,54,55,56,57,59,60,61,63,64,65,67,68,70,72,73,75,76,78,80,82,83,85,87,89,91,93,95,97,99,102,104,106,109,111,114,116,119,121,124,127,130,132,
  135,138,141,145,148,151,154,158,161,165,169,172,176,180,184,188,192,197,201,206,210,215,220,225,230,235,240,245,251,256,262,268,274,280,286,292,299,305,312,319,
  326,334,341,349,356,364,372,381,389,398,407,416,425,434,444,454,464,474,485,496,507,518,529,541,553,566,578,591,604,618,631,645,660,674,689,705,720,736,753,770,
  787,804,822,840,859,878,898,918,938,959,980,1002,1024,1047,1070,1094,1119,1143,1169,1195,1221,1249,1276,1305,1334,1364,1394,1425,1457,1489,1522,1556,1591,1626,
  1662,1699,1737,1775,1815,1855,1897,1939,1982,2026,2071,2117,2164,2212,2262,2312,2363,2416,2470,2524,2581,2638,2697,2757,2818,2881,2945,3010,3077,3146,3216,3287,
  3360,3435,3511,3590,3669,3751,3834,3920,4007,4095
};

PROGMEM prog_uint16_t exp_table_blue[] =
{ 
  0,15,15,16,16,16,17,17,17,18,18,19,19,20,20,20,21,21,22,22,23,23,24,24,25,25,26,27,27,28,28,29,30,30,31,32,32,33,34,35,35,36,37,38,39,39,40,41,42,43,44,45,46,
  47,48,49,50,51,53,54,55,56,57,59,60,61,63,64,65,67,68,70,72,73,75,76,78,80,82,83,85,87,89,91,93,95,97,99,102,104,106,109,111,114,116,119,121,124,127,130,132,
  135,138,141,145,148,151,154,158,161,165,169,172,176,180,184,188,192,197,201,206,210,215,220,225,230,235,240,245,251,256,262,268,274,280,286,292,299,305,312,319,
  326,334,341,349,356,364,372,381,389,398,407,416,425,434,444,454,464,474,485,496,507,518,529,541,553,566,578,591,604,618,631,645,660,674,689,705,720,736,753,770,
  787,804,822,840,859,878,898,918,938,959,980,1002,1024,1047,1070,1094,1119,1143,1169,1195,1221,1249,1276,1305,1334,1364,1394,1425,1457,1489,1522,1556,1591,1626,
  1662,1699,1737,1775,1815,1855,1897,1939,1982,2026,2071,2117,2164,2212,2262,2312,2363,2416,2470,2524,2581,2638,2697,2757,2818,2881,2945,3010,3077,3146,3216,3287,
  3360,3435,3511,3590,3669,3751,3834,3920,4007,4095
};

// Port and constant definitions for driving the TLC5940 ICs

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

// The character that indicates new data has been received.
//  (This is effectively a 'sync' pulse)
# define CMD_NEW_DATA 1

// Module size constants

#define MODULE_WIDTH 6
#define MODULE_HEIGHT 8
#define RGB_LEDS MODULE_HEIGHT * MODULE_WIDTH
#define BUFFER_SIZE MODULE_WIDTH*MODULE_HEIGHT*3

// temporary and live display buffers
unsigned char display_buffer_1[BUFFER_SIZE];
unsigned char display_buffer_2[BUFFER_SIZE];

static unsigned char *offscreen_display_buffer = display_buffer_1;
static unsigned char *display_buffer = display_buffer_2;

// Variables used in the UART ISR
static unsigned char *ptr;
static unsigned int pos = 0;

// Temporary buffer to store the next set of random colours
//  (These are calculated in advance over a period of cycles
//   so that they do not take too much processing time)
unsigned char random_colours_buffer[BUFFER_SIZE];
unsigned int random_colours_buffer_pixel = 0;


volatile byte display_buffer_live = 1;

// Variables that keep track of state in the ISR and main loop
volatile byte new_row = 0;
volatile byte need_xlat = 0;
byte row = 0;

// Variables used to decide when we should switch to the backup
//  random pattern
unsigned long tickcounter = 0;
unsigned long lastdata_tickcounter = 0;
// 40000 = 20 seconds
unsigned long timeout = 4000;

volatile boolean cycling = false;
// 1000 ~ 1/2 second
unsigned long cycle_period = 500;
unsigned long cycle_tickcounter = 0;

// The 'pure' colours that are used during random cycling
unsigned long colours[] = {
  0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0x00FFFF, 0xFF00FF, 0xFFFFFF};
int colours_length = 7;

void set_initial_pattern(void) {
  set_random_colours();
}

void set_random_colours() {

  for (int pixel=0; pixel < RGB_LEDS; pixel++) {
    unsigned long colour = colours[random(colours_length)];
    display_buffer[pixel * 3 + 0] = colour & 0xFF;
    display_buffer[pixel * 3 + 1] = (colour >> 8 ) & 0xFF;
    display_buffer[pixel * 3 + 2] = (colour >> 16) & 0xFF;   
  }

}

// Configuration of the AVR registers for communication with external
//  peripherals
void setup()   
{               
  // Set pins as inputs or outputs
  // Setup the SPI connection pins and the TLC5940 BLANK signal on PORTB
  DDRB |= (1<<1)  | (1<<2)  | (1<<3) | (1<<5) ; // BLANK, SS, MOSI, SCLK as OUTPUTS
  // Setup the remainder of the TLC5940 signal pins on PORTD
  DDRD |= (1<<3)  | (1<<4) |  (1<<6) | (1<<7) ; // VPRG, XLAT, GSCLK, Debug as OUTPUTS
  // PORTC is used to cycle the row high-side MOSFETS, and although only 
  //  pins 0, 1 & 2 are used, set them all as outputs
  DDRC = 255;

  // Configure the initial state of the TLC5940 control lines
  XLAT_Low;
  BLANK_High;
  VPRG_Low;
  Debug_Low;

  // Set an initial random patter in the display buffer
  set_initial_pattern();

  // Set Timer 1 (16bit) in count (capture) mode to count the number of output pulses up to the 
  //  greyscale depth. This then triggers an ISR to say that this LED has completed it's 
  //  cycle and to move on to the next row
  TCCR1A  = (1<<WGM11) | (0<<WGM10);            // Fast PWM with ICR1 as top
  TCCR1B  = (1<<WGM13) | (1<<WGM12);            // Fast PWM with ICR1 as top
  TCCR1B |= (1<<CS12)  | (1<<CS11) | (1<<CS10); // external clock (T1) on rising egde
  TIMSK1 |= (1<<TOIE1);                         // enable overflow interupt
  ICR1    = Gray_Scale_Depth;                   // Grey scale depth for TLC-PW

  // Set Timer 0 (8bit) to output a PWM pulse (which is then externally routed into Timer 1),
  //  which provides the clock source for the TLC5940 ICs.
  // It is not set as fast as possible because that leaves too much processing for the AVR
  //  to do, instead it is set a notch back (half speed)
  TCCR0A  = (1<<WGM01) | (0<<WGM00);            // CTC
  TCCR0A |= (0<<COM0A1) | (1<<COM0A0);          // Toggle on Compare Match
  TCCR0B  = (0<<CS02) | (0<<CS01) | (1<<CS00);  // No Prescaler
  // 0x00 is a bit too quick if you want to do any other processing,
  //  such as put in random pixels as well as receive data from the
  //  serial port, so put it up to 0x01. This makes the on time of 
  //  each colour 1ms, so a complete cycle in 3ms, which is still 
  //  strobing all colours at > 300Hz, so lots of time to play with
  OCR0A   = 0x01;                                  // f(OCR) = F_CPU/2/Prescaler

  // Configure the UART to receive data at 1 Mb/s
  UCSR0A |= (1<<U2X0);                                 // Double up UART
  UCSR0B |= (1<<RXEN0)  | (1<<TXEN0) | (1<<RXCIE0);    // UART RX, TX und RX Interrupt enable
  UCSR0C |= (1<<UCSZ01) | (1<<UCSZ00)             ;    // Asynchrous 8N1 
  UBRR0H = 0;
  UBRR0L = 1; //Baud Rate 1 MBit   --> 0% Error at 16MHz :-)

  // Enable global interrupts
  sei();

  // Configure and enable SPI  
  SPCR = (1<<SPE)|(1<<MSTR);  
  SPSR = B00000000;   

  // Double buffering doesn't work yet
  /*ptr=display_buffer_2;
   display_buffer = display_buffer_1;
   display_buffer_live = 1;
   */
  //  ptr = display_buffer;
  // Set the incoming data pointer to the start of the main display buffer
  ptr = display_buffer;

  // Prepopulate the random colour buffer
  if (random_colours_buffer_pixel < RGB_LEDS) {
    unsigned long colour = colours[random(colours_length)];
    random_colours_buffer[random_colours_buffer_pixel * 3 + 0] = colour & 0xFF;
    random_colours_buffer[random_colours_buffer_pixel * 3 + 1] = (colour >> 8 ) & 0xFF;
    random_colours_buffer[random_colours_buffer_pixel * 3 + 2] = (colour >> 16) & 0xFF; 
    random_colours_buffer_pixel++;
  } 

}

// If double buffering worked, we might use this, but it doesn't at the moment
void flip_buffers() {
  if (display_buffer_live == 1) {
    display_buffer_live = 2;
    display_buffer = display_buffer_2;
    ptr = display_buffer_1;
  } 
  else {
    display_buffer_live = 1;
    display_buffer = display_buffer_1;
    ptr = display_buffer_2;
  }
  lastdata_tickcounter = tickcounter;
  cycling = false;

}

// Main loop
void loop()        
{     
  // The loop does nothing until a new set of data needs to be shifted out for the next LED.
  // Everything else is handled by interrupts.
  if (new_row)
  {    
    shift_out_data(row);

    need_xlat = 1;

    new_row = 0;   
    
    // Every time there is a new row we increment our tick counter, which is our way of keeping
    //  track of time periods of the order of seconds, and we use this to cycle random colours
    //  at 1-4Hz. 2Hz is a pleasing cycling pattern.
        tickcounter++;

    // When we are cycling it can take a while to call random(), so lets do this once per loop.
    // If this is called many times in succession (e.g. 48), then you get a blip on the LED
    //  where it presumably should be sending more data (e.g. the xlat thing), but it isn't, so
    //  it does nothing, or something it shouldn't. either way, it's noticeable
    if (random_colours_buffer_pixel < RGB_LEDS) {
      unsigned long colour = colours[random(colours_length)];
      random_colours_buffer[random_colours_buffer_pixel * 3 + 0] = colour & 0xFF;
      random_colours_buffer[random_colours_buffer_pixel * 3 + 1] = (colour >> 8 ) & 0xFF;
      random_colours_buffer[random_colours_buffer_pixel * 3 + 2] = (colour >> 16) & 0xFF; 
      random_colours_buffer_pixel++;
    } 

    // If we are cycling, then see if we need to cycle again
    if (cycling == true) {

      if (tickcounter - cycle_tickcounter > cycle_period) {
        // Copy the current random colour buffer into the live display buffer
        // (TODO: If we had double buffering, we could just switch a pointer)
        memcpy(display_buffer, random_colours_buffer, BUFFER_SIZE);
        random_colours_buffer_pixel = 0;
        cycle_tickcounter = tickcounter;
      }
    } 
    else {
      // If we aren't cycling, then see if we need to start
      if (tickcounter - lastdata_tickcounter > timeout) {
        cycling = true;
      }
    }

  }
}

// Timer interupt for the TLC5940 clock input signal. Once this overflows we have 
//  completed the PWM cycle for the LEDs, and we should move onto the next row.
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

  // Move through the rows
  row++;
  if (row == 3) {
    row = 0;
  }
  new_row = 1;

  // Confirm we have handled the interrupt, clear the flag.
  TCNT1 = 0;
}

// UART interrupt for receiving data from a controlling computer.
ISR(USART_RX_vect) 
{
  // Read the data out of the UART RX memory location
  unsigned char b;
  b=UDR0;

  // If it is a frame sync pulse...
  if (b == CMD_NEW_DATA)  {
    // ... retransmit the pulse to subsequent modules
    UDR0=b; 
    //pos=0; 
    // Reset our counter
    pos=BUFFER_SIZE; 

    /*  
     if (offscreen_display_buffer == display_buffer_1) {
     offscreen_display_buffer = display_buffer_2;
     display_buffer = display_buffer_1;
     } else {
     offscreen_display_buffer = display_buffer_2;
     display_buffer = display_buffer_1;     
     }
     
     ptr=offscreen_display_buffer;
     */
    // And reset out buffer pointer location back to the start
    ptr=display_buffer;
    // Flip buffers to make the live one the one we have just populated, 
    //  and the temporary one containing incoming data, the other one
    //flip_buffers();

    // Make a note of when we last had a new frame - we use this to start
    //  the counter going to see if we should switch to random cycling
    lastdata_tickcounter = tickcounter;
    cycling = false;
    return;
  }    
  //  if (pos == BUFFER_SIZE) {
  // If we have received all the data we need (and have not yet received a new frame pulse),
  //  then relay the data to the next module by re-transmitting it.
  // This is a good way to keep signal integrity as each module is only receiving data from 
  //  the adjacent module in the chain, not from miles away where signal attenuation might be
  //  a problem
  if (pos == 0) {
    UDR0=b; 
    return;
  }
  // If we are still filling up our buffer, then store the data and keep track of how many
  //  piece of data we have had (so that we know when to stop)
  else {
    *ptr=b; 
    ptr++; 
    pos--;
  }  
}

// Shift out data to the TLC5940 ICs via the most efficient way possible: high speed SPI
void shift_out_data(byte row)
{

  // Get the appropriate gamma correction curve for this colour/row
  prog_uint16_t * exp_table;
  switch (row){ 
  case 2:
    exp_table = exp_table_blue;
    break;
  case 1:
    exp_table = exp_table_green;
    break;
  case 0:
  default:
    exp_table = exp_table_red;
    break;        
  }

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
  
}

// SPI transmission function
void spi_transfer(byte data)
{
  SPDR = data;	  // Start the transmission
  while (!(SPSR & (1<<SPIF)))     // Wait the end of the transmission
  {
  };
}


