/*
  Autor: MSc. Ing. Fabian Palacios Pereira
  Fecha: 8 de Mayo 2025
  Descripcion: Codigo para realizar comunicacion INBOUND y OUTBOUND, de Notehub a Nodo LoRa (Notecard)
  envia un comando desde el notehub y el notecard lo recibe, se actualiza a un muestreo determinado,
  lee el comando enviado desde notehub en formato {"exmpl": "exmpl"} y realiza una accion de acuerdo al comando
  resetpi: cierra y abre rele 1
  resetjet: cierra y abre rele 2

  Tambien envia el valor del conteo desde el notecard a notehub

  Placa DOIT ESP32 KIT V1

*/

//---------------------------------------------------------------------------------------

const int analogPin = 34; // Usa un pin ADC del ESP32 (34 a 39 suelen ser seguros)
const float vRef = 3.3;   // Voltaje de referencia del ESP32
const int adcMax = 4095;  // Resolución del ADC de 12 bits

int adcValue = 0;
float voltage = 0;

// Escala del divisor resistivo: si está calibrado para 25V -> 5V, el factor es 5
const float voltageDividerFactor = 5.0;

//---------------------------------------------------------------------------------------

unsigned long previousMillis = 0;  // debe ser unsigned long
const unsigned long interval = 3UL * 60UL * 1000UL;  // 10 o 15 minutos en milisegundos

//---------------------------------------------------------------------------------------

#include <Notecard.h>

#define usbSerial Serial2
#define txRxPinsSerial Serial1

// This is the unique Product Identifier for your device
#ifndef PRODUCT_UID
#define PRODUCT_UID "com.gmail.fabianpalacios0902:test"   // nombre del proyecto en notehub
#pragma message "PRODUCT_UID is not defined in this example. Please ensure your Notecard has a product identifier set before running this example or define it in code here. More details at https://dev.blues.io/tools-and-sdks/samples/product-uid"
#endif

#define myProductID PRODUCT_UID
Notecard notecard;

String string_entrada= "";  
bool fin_string= false;
int value = 0;

//----------------------------------------------------------------------------------------

void setup() {
  analogReadResolution(12); // Asegura resolución de 12 bits (0-4095)

  string_entrada.reserve(64);               //Reserva un espacio de hasta 64bytes
  usbSerial.begin(115200);
  Serial.begin(115200);

  pinMode(12, OUTPUT);
  digitalWrite(12, LOW);

  pinMode(14, OUTPUT);
  pinMode(27, OUTPUT);
  digitalWrite(14, HIGH);
  digitalWrite(27, HIGH);

  points();
  points();

  notecard.setDebugOutputStream(usbSerial);
  #ifdef txRxPinsSerial
    notecard.begin(txRxPinsSerial, 9600);
  #else
    notecard.begin();
  #endif

  //solicitud para restaurar notecard
  J *req = notecard.newRequest("card.restore");
  JAddBoolToObject(req, "delete", true);
  notecard.sendRequest(req);

  points();
  points();

  //solicitud para verificar version notecard
  J *req0 = notecard.newRequest("card.version");
  notecard.sendRequest(req0);

  points();

  //solicitud para conectar con el proyecto de notehub
  J *req1 = notecard.newRequest("hub.set");
  if (myProductID[0])
  {
      JAddStringToObject(req1, "product", myProductID);
  }
  notecard.sendRequestWithRetry(req1, 5); // 5 seconds

  points60();

  //solicitud para sincronizar con el proyecto de notehub
  J *req2 = notecard.newRequest("hub.sync");
  notecard.sendRequest(req2);

  points60();

  // Solicitud para crear template para recibir datos tipo string desde Notehub
  J *req3 = notecard.newRequest("note.template");
  JAddStringToObject(req3, "file", "datain.qi");
  JAddStringToObject(req3, "format", "compact");
  JAddNumberToObject(req3, "port", 1);
  J *body1 = JAddObjectToObject(req3, "body");
  if (body1) {
    JAddStringToObject(body1, "command", "example");
    JAddStringToObject(body1, "hash", "example");  // Valor por defecto o de ejemplo
  }
  notecard.sendRequest(req3);

  points();
  points();
  points();

  //solicitud para crear template para enviar datos al proyecto de notehub
  J *req4 = notecard.newRequest("note.template");
  JAddStringToObject(req4, "file", "count.qo");
  JAddStringToObject(req4, "format", "compact");
  JAddNumberToObject(req4, "port", 2);
  J *body2 = JAddObjectToObject(req4, "body");
  if (body2){
    JAddNumberToObject(body2, "counting", 14.1);
    JAddNumberToObject(body2, "voltage", 14.1);
  }
  notecard.sendRequest(req4);

  points();
  points();
  points();

  //solicitud para sincronizar con el proyecto de notehub
  J *req5 = notecard.newRequest("hub.sync");
  notecard.sendRequest(req5);

  points60();
  digitalWrite(12, HIGH);
  usbSerial.println("Ready");
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    // Aquí va tu código de muestreo
    
    J *req0 = notecard.newRequest("hub.sync");
    notecard.sendRequest(req0);

    points();
    points();
    points();
    points();

    // Solicitar cambios en el archivo y los verifica solo si hay cambios, si no, no
    J *req1 = notecard.newRequest("file.changes");
    if (req1 != NULL) {
      J *files = JCreateArray();
      if (files != NULL) {
        JAddItemToArray(files, JCreateString("datain.qi"));
        JAddItemToObject(req1, "files", files);
        J *rsp = notecard.requestAndResponse(req1);
        
        if (rsp != NULL) {
          J *info = JGetObject(rsp, "info");
          if (info != NULL) {
            J *datain = JGetObject(info, "datain.qi");
            if (datain != NULL) {
              // Hay cambios en datain.qi, hacer note.get
              J *req2 = notecard.newRequest("note.get");
              if (req2 != NULL) {
                JAddStringToObject(req2, "file", "datain.qi");
                JAddBoolToObject(req2, "delete", true);
                J *rsp2 = notecard.requestAndResponse(req2);
                
                if (rsp2 != NULL) {
                  J *body1 = JGetObject(rsp2, "body");
                  if (body1 != NULL) {
                    const char* command = JGetString(body1, "command");
                    if (command != NULL) {
                      usbSerial.print("Comando recibido: ");
                      usbSerial.println(command);
                      if (strcmp(command, "resetpi") == 0) {
                        // Acción para "resetpi"
                        digitalWrite(14, LOW);
                        delay(3000);
                        digitalWrite(14, HIGH);
                      }
                      if (strcmp(command, "resetjet") == 0) {
                        // Acción para "resetjet"
                        digitalWrite(27, LOW);
                        delay(3000);
                        digitalWrite(27, HIGH);
                      }

                      // Detectar el valor de 'hash'
                      const char* hash = JGetString(body1, "hash");
                      if (hash != NULL && strcmp(hash, "-") != 0) {
                        usbSerial.print("hash ");
                        usbSerial.println(hash);
                      } else {
                        usbSerial.println("Sin hash");
                      }
                    }
                  }
                  JDelete(rsp2);  // Liberar respuesta
                }
              }
            }
          }
          JDelete(rsp);  // Liberar memoria
        }

      }
    }

    //verifica de nuevo si hay algo en cola
    J *req3 = notecard.newRequest("file.changes");
    if (req3 != NULL) {
      J *files3 = JCreateArray();
      if (files3 != NULL) {
        JAddItemToArray(files3, JCreateString("datain.qi"));
        JAddItemToObject(req3, "files", files3);
        notecard.sendRequest(req3);
      }
    }

  }

  if(fin_string){                            //Si se confirma como terminado el string realiza las sgtes funciones
    string_entrada.trim();                   // trim() impide que se imprima el valor en ascii del espacio y del salto de linea
    fin_string=false;                        //Vuelve a setear como false el fin string
    value = string_entrada.toInt();
    //Serial.println(string_entrada);            //imprime lo que se ha escrito en el string_entrada
    usbSerial.print("vehicles counting: ");
    usbSerial.println(value);

    adcValue = analogRead(analogPin);
    voltage = (adcValue * vRef / adcMax) * voltageDividerFactor;
    
    J *req4 = notecard.newRequest("note.add");
    if (req4 != NULL){
      JAddStringToObject(req4, "file", "count.qo");
      JAddBoolToObject(req4, "sync", true);
      J *body2 = JAddObjectToObject(req4, "body");
      if (body2){
        JAddNumberToObject(body2, "counting", value);
        JAddNumberToObject(body2, "voltage", voltage);
      }
      notecard.sendRequest(req4);
    }

    string_entrada= "";                      //Vacia el buffer de entrada 
  }

}

void points(){
  usbSerial.println(".");
  delay(1000);
  usbSerial.println(".");
  delay(1000);
  usbSerial.println(".");
  delay(1000);
  usbSerial.println(".");
  delay(1000);
}

void points60(){
  for(int i=0; i<60; i++){
    usbSerial.println(".");
    delay(1000);
  }
}

void serialEvent(){
  while(Serial.available()){
    char char_entrada=(char)Serial.read();   //Lee lo que se introduce y lo convierte a char
    string_entrada+=char_entrada;            //Agrega el char que se leyo al string
    
    if(char_entrada=='\n'){                  //Si se aprieta enter lo toma como un salto de linea y determina que se completo el string 
      fin_string=true;    
    } 
  }
}