# frontend/components/dashboard/menu_alertas.py
import pygame
import json
import os
from invernadero_inteligente.frontend.config import config
from invernadero_inteligente.frontend.components.usuarios.registro.elementos.boton import Boton
from invernadero_inteligente.frontend.components.usuarios.registro.elementos.textbox import TextBox
from invernadero_inteligente.frontend.services.api_service import APIService


class MenuAlertas:
    def __init__(self, ancho_ventana, alto_ventana, usuario_actual=None):
        self.ancho = ancho_ventana
        self.alto = alto_ventana
        self.usuario_actual = usuario_actual  # Necesario para identificar el dispositivo
        self.fuente_titulo = pygame.font.Font(None, 36)
        self.fuente_normal = pygame.font.Font(None, 24)
        self.fuente_pequena = pygame.font.Font(None, 20)

        # Estado de mensajes
        self.mensaje = ""
        self.color_mensaje = (0, 0, 0)
        self.tiempo_mensaje = 0

        # Valores predeterminados
        self.valores_predeterminados = {
            'temp_min': '18',
            'temp_max': '25',
            'hum_ambiental_min': '50',
            'hum_ambiental_max': '90',
            'hum_suelo_min': '20',
            'hum_suelo_max': '80',
            'nivel_bombeo': '0',
            'nivel_drenaje': '5'
        }

        # Cargar configuración desde Google Sheets
        self.configuracion_guardada = self.cargar_configuracion_desde_sheets()

        self.crear_componentes()

    def crear_componentes(self):
        # Botón de volver
        self.boton_volver = Boton(
            x=30,
            y=30,
            ancho=120,
            alto=40,
            texto="← Volver",
            color=config.COLOR_BUTTON_SECONDARY
        )

        # Botón de parámetros predeterminados
        self.boton_predeterminados = Boton(
            x=self.ancho - 450,
            y=30,
            ancho=200,
            alto=40,
            texto="Parámetros Predeterminados",
            color=(100, 150, 255)  # Azul claro
        )

        # Botón de guardar
        self.boton_guardar = Boton(
            x=self.ancho - 220,
            y=30,
            ancho=150,
            alto=40,
            texto="💾 Guardar",
            color=(50, 150, 50)  # Verde
        )

        # Posiciones base para los elementos
        x_etiqueta = 50
        x_min = 300
        x_max = 450
        ancho_textbox = 100
        alto_textbox = 30
        espacio_vertical = 60
        y_inicial = 120

        # Crear TextBoxes para cada parámetro con valores guardados o predeterminados
        self.textboxes = {}
        valores_iniciales = self.configuracion_guardada if self.configuracion_guardada else self.valores_predeterminados

        # Temperatura
        self.textboxes['temp_min'] = TextBox(
            x=x_min, y=y_inicial,
            ancho=ancho_textbox, alto=alto_textbox,
            texto_inicial=str(valores_iniciales.get('temp_min', '18'))
        )
        self.textboxes['temp_max'] = TextBox(
            x=x_max, y=y_inicial,
            ancho=ancho_textbox, alto=alto_textbox,
            texto_inicial=str(valores_iniciales.get('temp_max', '25'))
        )

        # Humedad ambiental
        self.textboxes['hum_ambiental_min'] = TextBox(
            x=x_min, y=y_inicial + espacio_vertical,
            ancho=ancho_textbox, alto=alto_textbox,
            texto_inicial=str(valores_iniciales.get('hum_ambiental_min', '50'))
        )
        self.textboxes['hum_ambiental_max'] = TextBox(
            x=x_max, y=y_inicial + espacio_vertical,
            ancho=ancho_textbox, alto=alto_textbox,
            texto_inicial=str(valores_iniciales.get('hum_ambiental_max', '90'))
        )

        # Humedad del suelo
        self.textboxes['hum_suelo_min'] = TextBox(
            x=x_min, y=y_inicial + espacio_vertical * 2,
            ancho=ancho_textbox, alto=alto_textbox,
            texto_inicial=str(valores_iniciales.get('hum_suelo_min', '20'))
        )
        self.textboxes['hum_suelo_max'] = TextBox(
            x=x_max, y=y_inicial + espacio_vertical * 2,
            ancho=ancho_textbox, alto=alto_textbox,
            texto_inicial=str(valores_iniciales.get('hum_suelo_max', '80'))
        )

        # Nivel de agua del tanque de bombeo (solo columna min)
        self.textboxes['nivel_bombeo'] = TextBox(
            x=x_min, y=y_inicial + espacio_vertical * 3,
            ancho=ancho_textbox, alto=alto_textbox,
            texto_inicial=str(valores_iniciales.get('nivel_bombeo', '0'))
        )

        # Nivel de agua del tanque de drenaje (solo columna min)
        self.textboxes['nivel_drenaje'] = TextBox(
            x=x_min, y=y_inicial + espacio_vertical * 4,
            ancho=ancho_textbox, alto=alto_textbox,
            texto_inicial=str(valores_iniciales.get('nivel_drenaje', '5'))
        )

    def cargar_configuracion_desde_sheets(self):
        """Carga la configuración de alertas desde Google Sheets"""
        if not self.usuario_actual:
            print("Usuario actual no definido")
            return None

        # Obtener el número de serie del usuario
        numero_serie = self.obtener_numero_serie_usuario()
        if not numero_serie:
            print(f"Usuario no tiene número de serie asociado: {self.usuario_actual}")
            return None

        try:
            print(f"Intentando cargar alertas para dispositivo: {numero_serie}")  # Debug
            response = APIService.obtener_alertas_dispositivo(numero_serie)

            if response.get('status') != 'success':
                print(f"No se pudo cargar alertas: {response.get('message', 'Error desconocido')}")
                return None

            alertas = response.get('alertas', {})
            return self.mapear_alertas_a_configuracion(alertas)

        except Exception as e:
            print(f"Error al cargar configuración desde Sheets: {e}")
            return None

    def obtener_numero_serie_usuario(self):
        """Obtiene el número de serie del dispositivo del usuario"""
        if not self.usuario_actual or 'numero_serie' not in self.usuario_actual:
            return None

        numero_serie = self.usuario_actual['numero_serie']

        # Si es una lista, tomar el primer elemento
        if isinstance(numero_serie, list):
            return numero_serie[0] if numero_serie else None
        return str(numero_serie) if numero_serie else None

    def mapear_alertas_a_configuracion(self, alertas):
        """Mapea las alertas al formato interno"""
        configuracion = {
            'temp_min': alertas.get('temperatura', {}).get('min', self.valores_predeterminados['temp_min']),
            'temp_max': alertas.get('temperatura', {}).get('max', self.valores_predeterminados['temp_max']),
            'hum_ambiental_min': alertas.get('humedad_ambiente', {}).get('min', self.valores_predeterminados[
                'hum_ambiental_min']),
            'hum_ambiental_max': alertas.get('humedad_ambiente', {}).get('max', self.valores_predeterminados[
                'hum_ambiental_max']),
            'hum_suelo_min': alertas.get('humedad_suelo', {}).get('min', self.valores_predeterminados['hum_suelo_min']),
            'hum_suelo_max': alertas.get('humedad_suelo', {}).get('max', self.valores_predeterminados['hum_suelo_max']),
            'nivel_bombeo': alertas.get('nivel_bomba', self.valores_predeterminados['nivel_bombeo']),
            'nivel_drenaje': alertas.get('nivel_drenaje', self.valores_predeterminados['nivel_drenaje'])
        }
        print(f"Configuración cargada: {configuracion}")  # Debug
        return configuracion

    def guardar_configuracion_en_sheets(self):
        """Guarda la configuración de alertas en Google Sheets"""
        numero_serie = self.obtener_numero_serie_usuario()
        if not numero_serie:
            self.mostrar_mensaje("Error: Dispositivo no configurado para este usuario", (255, 0, 0))
            return False

        try:
            valores = self.obtener_valores()

            # Preparar los datos para enviar al backend
            datos_alertas = {
                'numero_serie': numero_serie,
                'alertas': {
                    'temperatura': {
                        'min': valores['temp_min'],
                        'max': valores['temp_max']
                    },
                    'humedad_ambiente': {
                        'min': valores['hum_ambiental_min'],
                        'max': valores['hum_ambiental_max']
                    },
                    'humedad_suelo': {
                        'min': valores['hum_suelo_min'],
                        'max': valores['hum_suelo_max']
                    },
                    'nivel_bomba': valores['nivel_bombeo'],
                    'nivel_drenaje': valores['nivel_drenaje']
                }
            }

            print(f"Intentando guardar alertas para dispositivo: {numero_serie}")
            response = APIService.guardar_alertas_dispositivo(datos_alertas)

            if response.get('status') == 'success':
                self.mostrar_mensaje("✅ Configuración guardada exitosamente", (0, 150, 0))
                return True
            else:
                error_msg = response.get('message', 'Error desconocido')
                self.mostrar_mensaje(f"❌ Error al guardar: {error_msg}", (255, 0, 0))
                return False

        except Exception as e:
            print(f"Error al guardar configuración en Sheets: {e}")
            self.mostrar_mensaje("❌ Error interno al guardar", (255, 0, 0))
            return False
    def mostrar_mensaje(self, texto, color):
        """Muestra un mensaje temporal en la interfaz"""
        self.mensaje = texto
        self.color_mensaje = color
        self.tiempo_mensaje = pygame.time.get_ticks()

    def aplicar_valores_predeterminados(self):
        """Aplica los valores predeterminados a todos los textboxes"""
        for key, textbox in self.textboxes.items():
            if key in self.valores_predeterminados:
                textbox.texto = self.valores_predeterminados[key]
                textbox.cursor_pos = len(textbox.texto)

    def manejar_evento(self, evento):
        # Manejar eventos de los botones
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.boton_volver.rect.collidepoint(evento.pos):
                return "volver_dashboard"
            elif self.boton_predeterminados.rect.collidepoint(evento.pos):
                self.aplicar_valores_predeterminados()
                return "redraw"
            elif self.boton_guardar.rect.collidepoint(evento.pos):
                # Validar antes de guardar
                errores = self.validar_valores()
                if errores:
                    error_mensaje = "Errores: " + "; ".join(errores)
                    self.mostrar_mensaje(error_mensaje, (255, 0, 0))
                    return "error_validacion"
                else:
                    # Guardar configuración en Google Sheets
                    if self.guardar_configuracion_en_sheets():
                        return "guardado_exitoso"
                    else:
                        return "error_guardado"

        # Manejar eventos de los textboxes
        resultado = None
        for textbox in self.textboxes.values():
            resultado_textbox = textbox.manejar_evento(evento)
            if resultado_textbox == "redraw":
                resultado = "redraw"

        return resultado

    def dibujar(self, superficie):
        # Fondo
        superficie.fill(config.BACKGROUND_COLOR)

        # Título
        titulo = self.fuente_titulo.render("Configuración de Alertas", True, (0, 0, 0))
        superficie.blit(titulo, (50, 50))

        # Mostrar información del dispositivo
        if self.usuario_actual and self.usuario_actual.get('numero_serie'):
            numero_serie = self.usuario_actual['numero_serie']
            if isinstance(numero_serie, list):
                numero_serie = numero_serie[0]

            info_dispositivo = self.fuente_pequena.render(
                f"Dispositivo: {numero_serie}", True, (100, 100, 100)
            )
            superficie.blit(info_dispositivo, (50, 85))

        # Dibujar botones
        self.boton_volver.dibujar(superficie)
        self.boton_predeterminados.dibujar(superficie)
        self.boton_guardar.dibujar(superficie)

        # Mostrar mensaje temporal si existe
        if self.mensaje and pygame.time.get_ticks() - self.tiempo_mensaje < 3000:  # 3 segundos
            mensaje_surface = self.fuente_normal.render(self.mensaje, True, self.color_mensaje)
            superficie.blit(mensaje_surface, (50, 90))

        # Posiciones para las etiquetas
        x_etiqueta = 50
        x_min_label = 300
        x_max_label = 450
        y_inicial = 120
        espacio_vertical = 60

        # Encabezados de columnas
        encabezado_min = self.fuente_normal.render("Mínimo", True, (0, 0, 0))
        encabezado_max = self.fuente_normal.render("Máximo", True, (0, 0, 0))
        superficie.blit(encabezado_min, (x_min_label + 25, y_inicial - 25))
        superficie.blit(encabezado_max, (x_max_label + 25, y_inicial - 25))

        # Definir parámetros y sus textboxes correspondientes
        parametros_info = [
            ("Temperatura (°C):", y_inicial, ['temp_min', 'temp_max']),
            ("Humedad Ambiental (%):", y_inicial + espacio_vertical, ['hum_ambiental_min', 'hum_ambiental_max']),
            ("Humedad del Suelo (%):", y_inicial + espacio_vertical * 2, ['hum_suelo_min', 'hum_suelo_max']),
            ("Nivel Tanque Bombeo:", y_inicial + espacio_vertical * 3, ['nivel_bombeo']),
            ("Nivel Tanque Drenaje:", y_inicial + espacio_vertical * 4, ['nivel_drenaje'])
        ]

        # Dibujar etiquetas
        for etiqueta, y_pos, textbox_keys in parametros_info:
            texto_etiqueta = self.fuente_normal.render(etiqueta, True, (0, 0, 0))
            superficie.blit(texto_etiqueta, (x_etiqueta, y_pos + 5))

        # Dibujar todos los textboxes
        for textbox in self.textboxes.values():
            textbox.dibujar(superficie)

        # Información adicional
        info_text = [
            "Configure los rangos de valores para recibir alertas cuando",
            "los sensores detecten valores fuera de estos parámetros.",
            "",
            "Los cambios se guardan automáticamente en Google Sheets.",
            "",
            "Valores recomendados:",
            "• Temperatura: 18-25°C para crecimiento óptimo",
            "• Humedad ambiental: 50-90% para evitar hongos",
            "• Humedad del suelo: 20-80% para hidratación adecuada",
            "• Nivel de bombeo: 0 para alerta de tanque vacío",
            "• Nivel de drenaje: 5 para evitar desbordamiento"
        ]

        y_info = 450
        for linea in info_text:
            if linea.startswith("•"):
                texto = self.fuente_pequena.render(linea, True, (100, 100, 100))
            elif linea == "Valores recomendados:" or linea == "Los cambios se guardan automáticamente en Google Sheets.":
                texto = self.fuente_normal.render(linea, True, (0, 0, 0))
            else:
                texto = self.fuente_pequena.render(linea, True, (80, 80, 80))

            superficie.blit(texto, (50, y_info))
            y_info += 20

    def obtener_valores(self):
        """Retorna un diccionario con todos los valores configurados"""
        valores = {}
        for key, textbox in self.textboxes.items():
            try:
                # Intentar convertir a número
                valor = float(textbox.texto) if textbox.texto else 0
                valores[key] = valor
            except ValueError:
                # Si no se puede convertir, usar valor predeterminado
                valores[key] = float(self.valores_predeterminados.get(key, '0'))

        return valores

    def validar_valores(self):
        """Valida que los valores mínimos sean menores que los máximos"""
        valores = self.obtener_valores()
        errores = []

        # Validar temperatura
        if valores['temp_min'] >= valores['temp_max']:
            errores.append("La temperatura mínima debe ser menor que la máxima")

        # Validar humedad ambiental
        if valores['hum_ambiental_min'] >= valores['hum_ambiental_max']:
            errores.append("La humedad ambiental mínima debe ser menor que la máxima")

        # Validar humedad del suelo
        if valores['hum_suelo_min'] >= valores['hum_suelo_max']:
            errores.append("La humedad del suelo mínima debe ser menor que la máxima")

        # Validar rangos de porcentaje para humedades
        if not (0 <= valores['hum_ambiental_min'] <= 100) or not (0 <= valores['hum_ambiental_max'] <= 100):
            errores.append("Los valores de humedad ambiental deben estar entre 0 y 100")

        if not (0 <= valores['hum_suelo_min'] <= 100) or not (0 <= valores['hum_suelo_max'] <= 100):
            errores.append("Los valores de humedad del suelo deben estar entre 0 y 100")

        return errores