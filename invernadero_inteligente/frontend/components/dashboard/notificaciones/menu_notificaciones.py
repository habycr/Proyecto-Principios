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

        # Si es una lista, tomar el primer elemento
        if isinstance(numero_serie, list):
            numero_serie = numero_serie[0]

        # Obtener configuración de alertas del dispositivo
        alertas_resp = APIService.obtener_alertas_dispositivo(numero_serie)
        if alertas_resp.get("status") != "success":
            print("❌ Error obteniendo alertas:", alertas_resp.get("message"))
            return

        alertas = alertas_resp.get("alertas", {})
        print(f"🔍 Alertas configuradas: {alertas}")

        # Mapeo de tipo_sistema (lógica) a nombre mostrado (para mensajes)
        tipos_dato_mapeo = {
            "temperatura": "Temperatura",
            "humedad_suelo": "Humedad",
            "humedad_ambiente": "Humedad Ambiente",
            "nivel_drenaje": "Nivel Drenaje",
            "nivel_bomba": "Nivel Bomba"
        }

        nombres_hoja_datos = {
            "temperatura": "Temperatura",
            "humedad_suelo": "Humedad Suelo",
            "humedad_ambiente": "Humedad",
            "nivel_drenaje": "Nivel Drenaje",
            "nivel_bomba": "Nivel Riego"
        }

        for tipo_sistema, tipo_hoja in tipos_dato_mapeo.items():
            print(f"\n🔍 Verificando {tipo_sistema} ({tipo_hoja})...")

            # Obtener configuración de alerta para este tipo
            config_alerta = alertas.get(tipo_sistema)
            if config_alerta is None:
                print(f"⚠ No hay configuración de alerta para '{tipo_sistema}'")
                continue

            # Usar nombre real según hoja de datos
            nombre_real = nombres_hoja_datos.get(tipo_sistema, tipo_sistema)
            datos_resp = APIService.obtener_datos_raw(numero_serie, nombre_real, limit=10)
            if datos_resp.get("status") != "success" or not datos_resp.get("data"):
                print(f"❌ No se encontraron datos para '{tipo_sistema}'")
                continue

            # Tomar el último dato (más reciente)
            ultimo_dato = datos_resp["data"][-1]
            try:
                valor_actual = float(ultimo_dato["valor"])
                print(f"📊 Valor actual de {tipo_sistema}: {valor_actual}")
            except (KeyError, ValueError, TypeError) as e:
                print(f"❌ Error procesando valor para '{tipo_sistema}': {e}")
                continue

            # Verificar según el tipo de alerta
            if tipo_sistema in ["temperatura", "humedad_suelo", "humedad_ambiente"]:
                self._verificar_rango_min_max(tipo_sistema, valor_actual, config_alerta)
            elif tipo_sistema == "nivel_drenaje":
                self._verificar_nivel_drenaje(tipo_sistema, valor_actual, config_alerta)
            elif tipo_sistema == "nivel_bomba":
                self._verificar_nivel_bomba(tipo_sistema, valor_actual, config_alerta)

    def _verificar_rango_min_max(self, tipo, valor, config_alerta):
        """Verifica si un valor está dentro del rango min-max configurado"""
        if not isinstance(config_alerta, dict):
            print(f"⚠ Configuración de alerta inválida para {tipo}: {config_alerta}")
            return

        try:
            # Obtener valores min y max, usar valores por defecto si no están configurados
            min_val = float(config_alerta.get("min", float("-inf"))) if config_alerta.get("min") not in [None, "",
                                                                                                         "0"] else float(
                "-inf")
            max_val = float(config_alerta.get("max", float("inf"))) if config_alerta.get("max") not in [None, "",
                                                                                                        "0"] else float(
                "inf")

            print(f"🎯 Rango configurado para {tipo}: {min_val} - {max_val}")

            # Verificar si está fuera del rango
            if valor < min_val or valor > max_val:
                mensaje = f"{tipo.replace('_', ' ').title()}: {valor}"
                if min_val != float("-inf") and max_val != float("inf"):
                    mensaje += f" (rango: {min_val} - {max_val})"
                elif min_val != float("-inf"):
                    mensaje += f" (mínimo: {min_val})"
                elif max_val != float("inf"):
                    mensaje += f" (máximo: {max_val})"

                self.alertas_fuera_de_rango.append({
                    "tipo": tipo,
                    "valor": valor,
                    "mensaje": mensaje,
                    "criticidad": "alta" if valor < min_val * 0.8 or valor > max_val * 1.2 else "media"
                })
                print(f"⚠ ALERTA: {mensaje}")
            else:
                print(f"✅ {tipo} dentro del rango")

        except (ValueError, TypeError) as e:
            print(f"❌ Error procesando rango para {tipo}: {e}")

    def _verificar_nivel_drenaje(self, tipo, valor, config_alerta):
        """Verifica el nivel de drenaje - alerta si es menor al configurado"""
        try:
            nivel_minimo = float(config_alerta) if config_alerta not in [None, "", "0"] else 0
            print(f"🎯 Nivel mínimo de drenaje configurado: {nivel_minimo}")

            if valor < nivel_minimo:
                mensaje = f"Nivel de Drenaje Bajo: {valor} (mínimo: {nivel_minimo})"
                self.alertas_fuera_de_rango.append({
                    "tipo": tipo,
                    "valor": valor,
                    "mensaje": mensaje,
                    "criticidad": "alta"
                })
                print(f"⚠ ALERTA: {mensaje}")
            else:
                print(f"✅ Nivel de drenaje OK: {valor} >= {nivel_minimo}")

        except (ValueError, TypeError) as e:
            print(f"❌ Error procesando nivel de drenaje: {e}")

    def _verificar_nivel_bomba(self, tipo, valor, config_alerta):
        """Verifica el nivel de bomba - alerta si es mayor al configurado"""
        try:
            nivel_maximo = float(config_alerta) if config_alerta not in [None, "", "0"] else float("inf")
            print(f"🎯 Nivel máximo de bomba configurado: {nivel_maximo}")

            if valor > nivel_maximo:
                mensaje = f"Nivel de Bomba Alto: {valor} (máximo: {nivel_maximo})"
                self.alertas_fuera_de_rango.append({
                    "tipo": tipo,
                    "valor": valor,
                    "mensaje": mensaje,
                    "criticidad": "alta"
                })
                print(f"⚠ ALERTA: {mensaje}")
            else:
                print(f"✅ Nivel de bomba OK: {valor} <= {nivel_maximo}")

        except (ValueError, TypeError) as e:
            print(f"❌ Error procesando nivel de bomba: {e}")

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            return "volver_dashboard"
        if evento.type == pygame.MOUSEBUTTONDOWN:
            return "volver_dashboard"
        return None

    def dibujar(self, superficie):
        superficie.fill(config.BACKGROUND_COLOR)

        # Título
        titulo = self.fuente_titulo.render("🔔 Notificaciones del Dispositivo", True, (0, 0, 0))
        superficie.blit(titulo, (50, 30))

        # Información del dispositivo
        numero_serie = self.usuario_actual.get("numero_serie")
        if isinstance(numero_serie, list):
            numero_serie = numero_serie[0]

        info_dispositivo = self.fuente_texto.render(f"Dispositivo: {numero_serie}", True, (100, 100, 100))
        superficie.blit(info_dispositivo, (50, 80))

        y = 130

        if not self.alertas_fuera_de_rango:
            # Todo está bien
            texto_ok = self.fuente_texto.render("✅ Todos los parámetros están dentro del rango normal", True,
                                                (0, 150, 0))
            superficie.blit(texto_ok, (50, y))
            y += 40

            instrucciones = self.fuente_texto.render("Presiona ESC o haz clic para volver al dashboard", True,
                                                     (100, 100, 100))
            superficie.blit(instrucciones, (50, y))
        else:
            # Hay alertas
            encabezado = self.fuente_texto.render("⚠ Se detectaron los siguientes problemas:", True, (200, 50, 50))
            superficie.blit(encabezado, (50, y))
            y += 50

            for i, alerta in enumerate(self.alertas_fuera_de_rango):
                # Color según criticidad
                color = (255, 0, 0) if alerta["criticidad"] == "alta" else (255, 150, 0)

                # Texto de la alerta
                texto_alerta = self.fuente_texto.render(f"• {alerta['mensaje']}", True, color)
                superficie.blit(texto_alerta, (70, y))
                y += 35

                # Evitar que se salga de la pantalla
                if y > self.alto - 100:
                    texto_mas = self.fuente_texto.render("... y más alertas", True, (150, 150, 150))
                    superficie.blit(texto_mas, (70, y))
                    break

            # Instrucciones
            y += 30
            instrucciones = self.fuente_texto.render("Presiona ESC o haz clic para volver al dashboard", True,
                                                     (100, 100, 100))
            superficie.blit(instrucciones, (50, y))

        # Mostrar total de alertas en la esquina
        if self.alertas_fuera_de_rango:
            total_alertas = self.fuente_texto.render(f"Total de alertas: {len(self.alertas_fuera_de_rango)}", True,
                                                     (150, 150, 150))
            superficie.blit(total_alertas, (self.ancho - 250, 30))