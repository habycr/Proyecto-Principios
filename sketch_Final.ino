#include <WiFi.h>
#include <WebServer.h>

#include <DHT.h>

#define DHTPIN 23
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);


const char* ssid = "Xiaomi 13T";
const char* password = "12345678";

const int pinBomba = 27;
const int pinVentilador = 26;
const int pinLuzUV = 15;
const int IN1 = 16, IN2 = 17, IN3 = 18, IN4 = 19;
const int pinSensorDrenaje = 35;
const int pinSensorRiego = 34;
const int pinSensorLuz = 33;
const int pinSensorHumedad = 32;

bool bombaEncendida = false;
bool ventiladorEncendido = false;
bool luzUVEncendida = false;

WebServer server(80);

int leerNivel(int pin) {
  int valor = analogRead(pin);
  if (pin == pinSensorDrenaje) {
    int nivel = map(valor, 0, 4000, 1, 10);
    return constrain(nivel, 1, 10);
  } else {
    int nivel = map(valor, 0, 1152, 1, 10);
    return constrain(nivel, 1, 10);
  }
}

int leerIntensidadLuz() {
  int valor = analogRead(pinSensorLuz);  // 930 oscuro, 0 luz directa
  int intensidad = map(valor, 930, 0, 1, 10);
  return constrain(intensidad, 1, 10);
}

int leerHumedadTierra() {
  int valor = analogRead(pinSensorHumedad);  // 4095 = seco, 2440 = mojado
  int humedad = map(valor, 4095, 2240, 1, 10);  // Invertido: más seco = más alto
  return constrain(humedad, 1, 10);
}



String generarPagina() {
  String html = "<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Control</title>";
  html += "<style>body{font-family:sans-serif;} .bajo{color:red; font-weight:bold;}</style>";
  html += "<script>setInterval(() => {fetch('/niveles').then(r => r.text()).then(t => {document.getElementById('niveles').innerHTML = t;});}, 1000);</script></head><body>";

  html += "<h2>Bomba de Agua</h2>";
  html += bombaEncendida ? "<a href='/bomba/apagar'><button>Apagar</button></a>" : "<a href='/bomba/encender'><button>Encender</button></a>";

  html += "<h2>Ventilador</h2>";
  html += ventiladorEncendido ? "<a href='/ventilador/apagar'><button>Apagar</button></a>" : "<a href='/ventilador/encender'><button>Encender</button></a>";

  html += "<h2>Luz Ultravioleta</h2>";
  html += luzUVEncendida ? "<a href='/uv/apagar'><button>Apagar</button></a>" : "<a href='/uv/encender'><button>Encender</button></a>";

  html += "<h2>Motores </h2>";
  html += "<a href='/motores/adelante'><button>Adelante</button></a> ";
  html += "<a href='/motores/atras'><button>Atrás</button></a> ";
  html += "<a href='/motores/stop'><button>Detener</button></a>";

  

  html += "<h2>Sensores</h2>";
  html += "<div id='niveles'></div>";

  html += "</body></html>";
  return html;
}

void setup() {
  Serial.begin(115200);
  dht.begin();


  pinMode(pinBomba, OUTPUT);
  pinMode(pinVentilador, OUTPUT);
  pinMode(pinLuzUV, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  digitalWrite(pinBomba, LOW);
  digitalWrite(pinVentilador, LOW);
  digitalWrite(pinLuzUV, LOW);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConectado. IP: " + WiFi.localIP().toString());

  server.on("/", []() { server.send(200, "text/html", generarPagina()); });

  server.on("/niveles", []() {
    int drenaje = leerNivel(pinSensorDrenaje);
    int riego = leerNivel(pinSensorRiego);
    int luz = leerIntensidadLuz();
    int humedad = leerHumedadTierra();

    String claseDrenaje = (drenaje <= 3) ? "bajo" : "";
    String claseRiego = (riego <= 3) ? "bajo" : "";

    String datos = "<div class='" + claseDrenaje + "'>Nivel Drenaje: " + String(drenaje) + " / 10</div>";
    datos += "<div class='" + claseRiego + "'>Nivel Riego: " + String(riego) + " / 10</div>";
    datos += "<div>Intensidad de Luz: " + String(luz) + " / 10</div>";
    datos += "<div>Nivel Humedad del Suelo: " + String(humedad) + " / 10</div>";


    float temp = dht.readTemperature();
    float humAmb = dht.readHumidity();

    if (isnan(temp) || isnan(humAmb)) {
      datos += "<div style='color:red;'>⚠️ Error leyendo DHT11</div>";
    } else {
      datos += "<div>Temperatura Ambiente: " + String(temp, 1) + " °C</div>";
      datos += "<div>Humedad Ambiente: " + String(humAmb, 1) + " %</div>";
    }


    server.send(200, "text/plain", datos);
  });

  server.on("/bomba/encender", []() { digitalWrite(pinBomba, HIGH); bombaEncendida = true; server.send(200, "text/html", generarPagina()); });
  server.on("/bomba/apagar", []() { digitalWrite(pinBomba, LOW); bombaEncendida = false; server.send(200, "text/html", generarPagina()); });

  server.on("/ventilador/encender", []() { digitalWrite(pinVentilador, HIGH); ventiladorEncendido = true; server.send(200, "text/html", generarPagina()); });
  server.on("/ventilador/apagar", []() { digitalWrite(pinVentilador, LOW); ventiladorEncendido = false; server.send(200, "text/html", generarPagina()); });

  server.on("/uv/encender", []() { digitalWrite(pinLuzUV, HIGH); luzUVEncendida = true; server.send(200, "text/html", generarPagina()); });
  server.on("/uv/apagar", []() { digitalWrite(pinLuzUV, LOW); luzUVEncendida = false; server.send(200, "text/html", generarPagina()); });

  server.on("/motores/adelante", []() { digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW); digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW); server.send(200, "text/html", generarPagina()); });
  server.on("/motores/atras", []() { digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH); digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH); server.send(200, "text/html", generarPagina()); });
  server.on("/motores/stop", []() { digitalWrite(IN1, LOW); digitalWrite(IN2, LOW); digitalWrite(IN3, LOW); digitalWrite(IN4, LOW); server.send(200, "text/html", generarPagina()); });


  server.begin();
  Serial.println("Servidor web iniciado.");
}

void loop() {
  server.handleClient();
}
