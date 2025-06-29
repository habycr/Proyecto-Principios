import pygame
from invernadero_inteligente.frontend.services.api_service import APIService
from invernadero_inteligente.frontend.config import config

class MenuNotificaciones:
    def __init__(self, ancho, alto, usuario_actual):
        self.ancho = ancho
        self.alto = alto
        self.usuario_actual = usuario_actual
        self.alertas_fuera_de_rango = []
        self.fuente_titulo = pygame.font.Font(None, 36)
        self.fuente_texto = pygame.font.Font(None, 28)

        self.verificar_alertas()

    def verificar_alertas(self):
        numero_serie = self.usuario_actual.get("numero_serie")
        if not numero_serie:
            print("⚠ Usuario sin dispositivo.")
            return
        if isinstance(numero_serie, list):
            numero_serie = numero_serie[0]

        alertas_resp = APIService.obtener_alertas_dispositivo(numero_serie)
        if alertas_resp.get("status") != "success":
            print("❌ Error obteniendo alertas:", alertas_resp.get("message"))
            return

        alertas = alertas_resp.get("alertas", {})

        tipos_dato = {
            "temperatura": alertas.get("temperatura"),
            "humedad_suelo": alertas.get("humedad_suelo"),
            "humedad_ambiente": alertas.get("humedad_ambiente"),
            "nivel_drenaje": alertas.get("nivel_drenaje"),
            "nivel_bomba": alertas.get("nivel_bomba"),
        }

        for tipo, rango in tipos_dato.items():
            if rango is None:
                print(f"⚠ Rango de alerta no definido para '{tipo}'.")
                continue

            datos = APIService.obtener_datos_raw(numero_serie, tipo, limit=1)
            if datos.get("status") == "success" and datos["data"]:
                try:
                    valor = float(datos["data"][0]["valor"])
                except (KeyError, ValueError, TypeError):
                    print(f"❌ Valor inválido para '{tipo}'")
                    continue

                # Determinar si es tipo con min-max o fijo
                if isinstance(rango, dict):
                    try:
                        minimo = float(rango.get("min")) if rango.get("min") is not None else float("-inf")
                        maximo = float(rango.get("max")) if rango.get("max") is not None else float("inf")
                    except (ValueError, TypeError):
                        minimo, maximo = float("-inf"), float("inf")
                else:
                    try:
                        minimo = maximo = float(rango)
                    except (ValueError, TypeError):
                        minimo, maximo = float("-inf"), float("inf")

                if valor < minimo or valor > maximo:
                    self.alertas_fuera_de_rango.append((tipo, valor, minimo, maximo))
            else:
                print(f"❌ No se encontraron datos para '{tipo}'.")

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            return "volver_dashboard"
        if evento.type == pygame.MOUSEBUTTONDOWN:
            return "volver_dashboard"
        return None

    def dibujar(self, superficie):
        superficie.fill(config.BACKGROUND_COLOR)
        titulo = self.fuente_titulo.render("Notificaciones de Dispositivo", True, (0, 0, 0))
        superficie.blit(titulo, (50, 30))

        y = 100
        if not self.alertas_fuera_de_rango:
            texto = self.fuente_texto.render("✅ Todos los parámetros están dentro del rango.", True, (0, 128, 0))
            superficie.blit(texto, (50, y))
        else:
            alerta = self.fuente_texto.render("⚠ Parámetros fuera de rango detectados:", True, (255, 0, 0))
            superficie.blit(alerta, (50, y))
            y += 40
            for tipo, valor, minimo, maximo in self.alertas_fuera_de_rango:
                linea = f"{tipo.capitalize()}: {valor} (esperado entre {minimo} y {maximo})"
                texto = self.fuente_texto.render(linea, True, (255, 0, 0))
                superficie.blit(texto, (50, y))
                y += 35
