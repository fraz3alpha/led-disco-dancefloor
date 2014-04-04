
/*
Andy Taylor's highly inefficient SNES gamepad parsing code.
29/10/2012
The gamepads contain two shift registers, parallel-in-serial-out.
To latch the inputs into the registers, pulse the latch.
To read the data, strobe the clock 16 times and read the data on 
the high to low transition. Once the latch is clocked, bit 0 
will be immediately available.

SNES controller connector (looking into the end of the cable) :

/---------\
|1234 567 )
\---------/

1  5V
2  CLOCK
3  LATCH
4  DATA

5  NC
6  NC
7  Ground

*/

#define CLOCK 3
#define LATCH 2  // Strobe / Latch
#define DATA  4

void setup() {
  // put your setup code here, to run once:
  pinMode(CLOCK, OUTPUT);
  pinMode(LATCH, OUTPUT);
  pinMode(DATA,  INPUT);

  digitalWrite(CLOCK, LOW);
  digitalWrite(LATCH, LOW);
  
  Serial.begin(57600);

}

// Self explanatory except Shoulder L&R buttons are O&P,
//  and sElect & sTart.
char* pressed  = "BYETUDLRAXOP    ";
char* released = "byetudlraxop    ";

void pad_callback(byte controller, unsigned int previous_data, unsigned int new_data) {
  
  unsigned int changed = previous_data ^ new_data;
  
  for (int i=0; i<16; i++) {
    if (changed & 1<<i) {
      // A '0' in the new data indicates that it has been pressed
      if (1<<i & new_data) {
        // Released
        Serial.println(released[i]);
      } else {
        // Pressed
        Serial.println(pressed[i]);
      }
    } 
  }
}

unsigned int previous_data = 0x0;

void loop() {
 
  // Latch the inputs into the shift register
  digitalWrite(LATCH, HIGH);
  digitalWrite(LATCH, LOW);
  delay(1);
  
  unsigned int this_data = 0x0;
  
  // Read in all the data. First bit is immediately available
  for (int i=0; i<16; i++) {
    this_data |= (digitalRead(DATA) << i);
    digitalWrite(CLOCK, HIGH); 
    digitalWrite(CLOCK, LOW);
    
  }
  // Only if the data changes, do anything about it.
  if (this_data != previous_data) {
    pad_callback(1, previous_data, this_data);
    previous_data = this_data;
  }
  
}
