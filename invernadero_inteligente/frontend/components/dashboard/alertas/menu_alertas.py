# frontend/components/dashboard/menu_alertas.py
import pygame
import json
import os
from invernadero_inteligente.frontend.config import config
from invernadero_inteligente.frontend.components.usuarios.registro.elementos.boton import Boton
from invernadero_inteligente.frontend.components.usuarios.registro.elementos.textbox import TextBox


class MenuAlertas:
    def __init__(self, ancho_ventana, alto_ventana):
        self.ancho = ancho_ventana
        self.alto = alto_ventana
        self.fuente_titulo = pygame.font.Font(None, 36)
        self.fuente_normal = pygame.font.Font(None, 24)
        self.fuente_pequena = pygame.font.Font(None, 20)

        # Archivo de configuración
        self.archivo_config = "data/alertas_config.json"

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

        # Crear directorio si no existe
        os.makedirs(os.path.dirname(self.archivo_config), exist_ok=True)

        # Cargar configuración guardada
        self.configuracion_guardada = self.cargar_configuracion()

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

    def cargar_configuracion(self):
        """Carga la configuración desde el archivo JSON"""
        try:
            if os.path.exists(self.archivo_config):
                with open(self.archivo_config, 'r', encoding='utf-8') as archivo:
                    return json.load(archivo)
        except Exception as e:
            print(f"Error al cargar configuración: {e}")
        return None

    def guardar_configuracion(self):
        """Guarda la configuración actual en el archivo JSON"""
        try:
            valores = self.obtener_valores()
            # Convertir valores numéricos a strings para consistencia con textboxes
            valores_str = {key: str(valor) for key, valor in valores.items()}

            with open(self.archivo_config, 'w', encoding='utf-8') as archivo:
                json.dump(valores_str, archivo, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al guardar configuración: {e}")
            return False

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
                    # Si hay errores, podrías mostrar un mensaje (aquí solo imprimimos)
                    print("Errores de validación:")
                    for error in errores:
                        print(f"- {error}")
                    return "error_validacion"
                else:
                    # Guardar configuración
                    if self.guardar_configuracion():
                        print("Configuración guardada exitosamente")
                        return "guardado_exitoso"
                    else:
                        print("Error al guardar la configuración")
                        return "error_guardado"

        # Manejar eventos de los textboxes - IMPORTANTE: manejar todos
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

        # Dibujar botones
        self.boton_volver.dibujar(superficie)
        self.boton_predeterminados.dibujar(superficie)
        self.boton_guardar.dibujar(superficie)

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

        # Dibujar etiquetas y textboxes
        for etiqueta, y_pos, textbox_keys in parametros_info:
            # Dibujar etiqueta
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
            "Valores recomendados:",
            "• Temperatura: 18-25°C para crecimiento óptimo",
            "• Humedad ambiental: 50-90% para evitar hongos",
            "• Humedad del suelo: 20-80% para hidratación adecuada",
            "• Nivel de bombeo: 0 para alerta de tanque vacío",
            "• Nivel de drenaje: 5 para evitar desbordamiento",
            "",
            "💡 Presiona 'Guardar' para mantener la configuración entre sesiones"
        ]

        y_info = 450
        for linea in info_text:
            if linea.startswith("•"):
                texto = self.fuente_pequena.render(linea, True, (100, 100, 100))
            elif linea == "Valores recomendados:":
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

        return errores