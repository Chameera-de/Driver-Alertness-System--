int pulsePin = A0;
const int AOUTpin=1; //alcohol sensor analog o/p //change this
const int DOUTpin=9; //digital output of alcohol sensor //change this
const int blinkPin=13;
const int interface=11;
const int trigPin = 7;
const int echoPin = 4;
int limit;
int value;
int inp1=0;  
int co2=0; 
int i=0;
volatile int BPM;                  
volatile int Signal;
const int buzzer = 8;
volatile int IBI = 600;             
volatile boolean Pulse = false;   
volatile boolean QS = false; 
long duration;
float currdistance;
float speedometer=32;//kmh-1
float decel=6.56;//ms-2
float spd; 
float truedist;
float temp=27;

static boolean serialVisual = true;

volatile int rate[10];                      
volatile unsigned long sampleCounter = 0;        
volatile unsigned long lastBeatTime = 0;        
volatile int P = 512;                      
volatile int T = 512;                     
volatile int thresh = 525;             
volatile int amp = 100;       
volatile boolean firstBeat = true;   
volatile boolean secondBeat = false; 

void setup() 
{
  Serial.begin(9600);
  pinMode(DOUTpin, INPUT);
  pinMode(blinkPin, OUTPUT);
  pinMode(interface, OUTPUT);
  pinMode(buzzer,OUTPUT);
  pinMode(AOUTpin, INPUT);
  interruptSetup();  
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(13, OUTPUT);
}

void loop()
{
  
  if (Serial.available()>0)
  {
    while(!Serial.available());
   // Serial.println("Got input");
    inp1=Serial.read();
    co2=inp1-48;
    delay(200);

  }
  //Serial.println(co2);

  if(co2==1)      //Simulating the breath of the user
                  // If CO2 is 1, it means the driver has  breathed into the sensor

  {
  value= analogRead(AOUTpin);
  limit= digitalRead(DOUTpin);
  Serial.print("Alcohol value: ");
  Serial.println(value);

//  delay(1000);

 
    if (value > 200)  //check alcohol content in the breath
    {
      digitalWrite(blinkPin, HIGH);
      i=1;
      delay(2000);
      digitalWrite(blinkPin,LOW);
      Serial.println("Your alcohol level is higher than the permissible limit.\nThe program will exit.");
      exit(0);
      

    }
    else
    {
      while(analogRead(AOUTpin) <= 200){
      digitalWrite(blinkPin, LOW);
      i=0;
      Serial.println("Ignition has been enabled");

      serialOutput();  
   
  if (QS == true) // A Heartbeat Was Found
    {     
      serialOutputWhenBeatHappens(); // A Beat Happened, Output that to serial.     
      QS = false;   
    }
     
  delay(20); 
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH);
  Serial.print("duration ");
  Serial.println(duration);
  currdistance= ((duration*0.000001)/2)*(331+0.6*temp);
  Serial.print("currdistance "); // distance calculated by US sensor
  Serial.println(currdistance);
  spd=speedometer*5/18;
  Serial.print("spd ");//Speed in m/s
  Serial.println(spd);
  truedist=(spd*spd)/(2*decel);//Distance calculated by equation for the car to dead stop with the average decelaration
  Serial.print("truedist ");
  Serial.println(truedist);
  if (currdistance < truedist){
    Serial.println("Collision is imminent"); 
    digitalWrite(13,HIGH);}
  delay(1000);      
      
    }
    }
    if(analogRead(AOUTpin) > 200)
    {
      Serial.print("Exit");
      delay(500);
      exit(0);
      }
  }//else ends
}
 
void interruptSetup() // Set an interrupt every 2ms
{     
 
  TCCR2A = 0x02;    
  TCCR2B = 0x06;   
  OCR2A = 0X7C;      
  TIMSK2 = 0x02;     
  sei();             
} 

void serialOutput()
{  
 if (serialVisual == true)
  {  
     arduinoSerialMonitorVisual('-', Signal); 
  } 
 else
  {
      sendDataToSerial('S', Signal);
   }        
}

void serialOutputWhenBeatHappens()
{    
 if (serialVisual == true)
   {            
     Serial.print(" Heart-Beat Found ");  
     Serial.print("BPM: ");
     Serial.println(BPM);
   }
 if (BPM > 100)
  {
    digitalWrite(buzzer,HIGH);
    delay(2000);
    digitalWrite(buzzer,LOW);
  }
 else
   {
     sendDataToSerial('B',BPM);  
     sendDataToSerial('Q',IBI); 
   }   
}



void arduinoSerialMonitorVisual(char symbol, int data )
{    
  const int sensorMin = 0;      
  const int sensorMax = 1024;  
  int sensorReading = data;
  int range = map(sensorReading, sensorMin, sensorMax, 0, 11);


}


ISR(TIMER2_COMPA_vect) // Triggered when Timer2 counts to 124 
{  
  cli();                                      
  Signal = analogRead(pulsePin);              
  sampleCounter += 2;                        
  int N = sampleCounter - lastBeatTime;     
                                              
  if(Signal < thresh && N > (IBI/5)*3)
    {      
      if (Signal < T)
      {                        
        T = Signal;
      }
    }

  if(Signal > thresh && Signal > P)
    {      
      P = Signal;                           
    }                                      
//Look for heart beat
  if (N > 250)
  {                                 
    if ( (Signal > thresh) && (Pulse == false) && (N > (IBI/5)*3) )
      {        
        Pulse = true;                               
        digitalWrite(blinkPin,HIGH);            
        IBI = sampleCounter - lastBeatTime;       
        lastBeatTime = sampleCounter;          
  
        if(secondBeat)
        {                   
          secondBeat = false;         
          for(int i=0; i<=9; i++)
          {             
            rate[i] = IBI;                      
          }
        }
  
        if(firstBeat)
        {                         
          firstBeat = false;                   
          secondBeat = true;              
          sei();                              
          return;                          
        }   
  
      word runningTotal = 0;                  

      for(int i=0; i<=8; i++)
        {               
          rate[i] = rate[i+1];                 
          runningTotal += rate[i];             
        }

      rate[9] = IBI;                         
      runningTotal += rate[9];         
      runningTotal /= 10;                
      BPM = 60000/runningTotal;           
      QS = true;                             
    }                       
  }

  if (Signal < thresh && Pulse == true)
    {   
      digitalWrite(blinkPin,LOW);            
      Pulse = false;                       
      amp = P - T;                
      thresh = amp/2 + T;                
      P = thresh;                           
      T = thresh;
    }

  if (N > 2500)
    {                         
      thresh = 512;                          
      P = 512;                             
      T = 512;                               
      lastBeatTime = sampleCounter;           
      firstBeat = true;                     
      secondBeat = false;                   
    }

  sei();                                  
}
void sendDataToSerial(char symbol, int data )
{
   //Serial.print(symbol);
   //Serial.println(data);                
}
