const int ledPin = 6;
const int buzzerPin = 9;
const int buttonPin = 7;

bool alarmActive = false;

void setup() {
  pinMode(ledPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP);

  Serial.begin(115200);
  while (!Serial);   // Espera a que el puerto serie esté listo (USB)

  Serial.println("ARDUINO_READY");
}

void loop() {
  // Recibir comandos desde Raspberry Pi por USB (Serial)
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "DROWSY") {
      alarmActive = true;
      Serial.println("ALARM_ON");
    }
  }

  if (alarmActive) {
    digitalWrite(ledPin, HIGH);
    tone(buzzerPin, 1000);  // Sonido de alarma

    // Botón pulsado (LOW porque usamos INPUT_PULLUP)
    if (digitalRead(buttonPin) == LOW) {
      alarmActive = false;
      noTone(buzzerPin);
      digitalWrite(ledPin, LOW);
      Serial.println("ACK");
      delay(300); // Antirrebote básico
    }
  } else {
    noTone(buzzerPin);
    digitalWrite(ledPin, LOW);
  }
}
