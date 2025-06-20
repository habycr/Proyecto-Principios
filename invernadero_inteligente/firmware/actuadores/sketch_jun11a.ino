#include <WiFi.h>
#include <WebServer.h>

// Configura tus datos Wi-Fi
const char* ssid = "Casa Invu 2.4";
const char* password = "Invu5400";

// Pines asignados
const int pinBomba = 27;
const int pinVentilador = 32;
const int pinLuzUV = 15;
bool luzUVEncendida = false;

const int IN1 = 16;  // Motor A
const int IN2 = 17;
const int IN3 = 18;  // Motor B
const int IN4 = 19;

// Estados
bool bombaEncendida = false;
bool ventiladorEncendido = false;

WebServer server(80);

void pararMotores() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

String generarPagina() {
  String html = "<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Control</title></head><body>";
  html += "<h2>Bomba de Agua</h2>";
  html += bombaEncendida ?
    "<a href='/bomba/apagar'><button>Apagar Bomba</button></a>" :
    "<a href='/bomba/encender'><button>Encender Bomba</button></a>";

  html += "<h2>Ventilador</h2>";
  html += ventiladorEncendido ?
    "<a href='/ventilador/apagar'><button>Apagar Ventilador</button></a>" :
    "<a href='/ventilador/encender'><button>Encender Ventilador</button></a>";

  html += "<h3>Luz Ultravioleta</h3>";
  html += luzUVEncendida ?
    "<a href=\"/uv/apagar\"><button>Apagar UV</button></a>" :
    "<a href=\"/uv/encender\"><button>Encender UV</button></a>";

  html += "<h2>Motor A</h2>";
  html += "<a href='/motorA/adelante'><button>Adelante</button></a> ";
  html += "<a href='/motorA/atras'><button>Atrás</button></a> ";
  html += "<a href='/motorA/stop'><button>Detener</button></a>";

  html += "<h2>Motor B</h2>";
  html += "<a href='/motorB/adelante'><button>Adelante</button></a> ";
  html += "<a href='/motorB/atras'><button>Atrás</button></a> ";
  html += "<a href='/motorB/stop'><button>Detener</button></a>";

  html += "</body></html>";
  return html;
}

void setup() {
  Serial.begin(115200);

  // Pines de salida
  pinMode(pinBomba, OUTPUT);
  pinMode(pinVentilador, OUTPUT);
  pinMode(pinLuzUV, OUTPUT);


  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  // Estados iniciales
  digitalWrite(pinBomba, LOW);
  digitalWrite(pinVentilador, LOW);
  digitalWrite(pinLuzUV, LOW);
  pararMotores();

  // Conexión Wi-Fi
  WiFi.begin(ssid, password);
  Serial.println("Conectando a Wi-Fi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500); Serial.print(".");
  }
  Serial.println("\n✅ Conectado. IP: " + WiFi.localIP().toString());

  // Rutas de la web
  server.on("/", []() {
    server.send(200, "text/html", generarPagina());
  });

  // Bomba
  server.on("/bomba/encender", []() {
    digitalWrite(pinBomba, HIGH);
    bombaEncendida = true;
    server.send(200, "text/html", generarPagina());
  });

  server.on("/bomba/apagar", []() {
    digitalWrite(pinBomba, LOW);
    bombaEncendida = false;
    server.send(200, "text/html", generarPagina());
  });

  // Ventilador
  server.on("/ventilador/encender", []() {
    digitalWrite(pinVentilador, HIGH);
    ventiladorEncendido = true;
    server.send(200, "text/html", generarPagina());
  });

  server.on("/ventilador/apagar", []() {
    digitalWrite(pinVentilador, LOW);
    ventiladorEncendido = false;
    server.send(200, "text/html", generarPagina());
  });

  server.on("/uv/encender", []() {
    digitalWrite(pinLuzUV, HIGH);
    luzUVEncendida = true;
    server.send(200, "text/html", generarPagina());
  });

  server.on("/uv/apagar", []() {
    digitalWrite(pinLuzUV, LOW);
    luzUVEncendida = false;
    server.send(200, "text/html", generarPagina());
  });


  // Motor A
  server.on("/motorA/adelante", []() {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    server.send(200, "text/html", generarPagina());
  });

  server.on("/motorA/atras", []() {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    server.send(200, "text/html", generarPagina());
  });

  server.on("/motorA/stop", []() {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    server.send(200, "text/html", generarPagina());
  });

  // Motor B
  server.on("/motorB/adelante", []() {
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
    server.send(200, "text/html", generarPagina());
  });

  server.on("/motorB/atras", []() {
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
    server.send(200, "text/html", generarPagina());
  });

  server.on("/motorB/stop", []() {
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, LOW);
    server.send(200, "text/html", generarPagina());
  });

  server.begin();
  Serial.println("🌐 Servidor web iniciado.");
}

void loop() {
  server.handleClient();
}
