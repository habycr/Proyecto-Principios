import pygame
from invernadero_inteligente.frontend.config import config
from components.usuarios.registro.elementos.boton import Boton
from invernadero_inteligente.backend.services.google_sheets import GoogleSheetsDB


class GestionTicketsAdmin:
    def __init__(self, ancho_ventana, alto_ventana):
        self.ancho = ancho_ventana
        self.alto = alto_ventana
        self.fuente_titulo = pygame.font.Font(None, 36)
        self.fuente_normal = pygame.font.Font(None, 24)
        self.fuente_pequena = pygame.font.Font(None, 20)

        # Conexión con Google Sheets
        self.gsheets = GoogleSheetsDB()

        # Historial de cambios
        self.historial = []
        self.max_historial = 10  # Máximo de entradas en el historial
        self.scroll_historial = 0
        self.area_historial = pygame.Rect(370, 400, self.ancho - 390, 150)  # Ajusta según tu diseño

        # Datos de tickets
        self.tickets = []
        self.ticket_seleccionado = None
        self.datos_ticket = {}

        # Configuración de scroll
        self.scroll_y = 0
        self.scroll_offset = 0
        self.altura_item = 40
        self.area_scroll = pygame.Rect(50, 120, 300, 300)
        self.item_rects = []

        # Configuración para el campo de descripción
        self.tamano_linea_descripcion = 23  # Caracteres por línea (corregido de 'camano' a 'tamano')
        self.max_lineas_descripcion = 4  # Líneas visibles

        # Campos editables y no editables
        self.campos_editables = {
            'ticket_id': '',
            'Dispositivo': '',
            'Email': '',
            'Asunto': '',
            'Descripcion': '',
            'Status': 'Activo'
        }
        self.campos_no_editables = ['ticket_id', 'Dispositivo', 'Email']
        self.espacio_entre_campos = 35
        self.altura_campo = 30
        self.altura_campo_descripcion = 100  # Altura para 4 líneas

        # Estado de los campos activos
        self.campos_activos = {campo: False for campo in self.campos_editables.keys()}
        self.campo_rects = {}  # Diccionario para almacenar los rectángulos de los campos
        self.posicion_cursor_descripcion = 0  # Posición del cursor en la descripción

        # Control del cursor
        self.cursor_visible = True
        self.tiempo_cursor = pygame.time.get_ticks()
        self.intervalo_cursor = 500  # ms para parpadeo del cursor

        # Mensajes de estado
        self.mensaje_estado = ''
        self.mostrar_mensaje = False
        self.tipo_mensaje = 'info'
        self.tiempo_mensaje = 0

        # Botones principales
        self.boton_volver = Boton(
            x=20, y=20,
            ancho=100, alto=40,
            texto="← Volver",
            color=config.COLOR_BUTTON_SECONDARY
        )

        self.boton_refrescar = Boton(
            x=self.ancho - 280, y=20,
            ancho=120, alto=40,
            texto="Actualizar",
            color=config.COLOR_BUTTON
        )

        self.boton_guardar = Boton(
            x=self.ancho - 140, y=20,
            ancho=120, alto=40,
            texto="Guardar",
            color=(34, 139, 34)
        )

        # Áreas de visualización
        self.area_tickets = pygame.Rect(50, 80, 300, self.alto - 100)
        self.area_datos = pygame.Rect(370, 80, self.ancho - 390, self.alto - 120)

        # Cargar tickets al inicializar
        self.cargar_tickets()

    def cargar_tickets(self):
        """Carga la lista de tickets desde Google Sheets"""
        try:
            self.tickets = self.gsheets.get_tickets()
            self.mostrar_mensaje_temporal("Tickets cargados correctamente", "success")
        except Exception as e:
            self.mostrar_mensaje_temporal(f"Error al cargar tickets: {str(e)}", "error")

    def cargar_datos_ticket(self, ticket_id):
        """Carga los datos de un ticket específico"""
        try:
            self.ticket_seleccionado = next(
                (t for t in self.tickets if str(t['ticket_id']) == str(ticket_id)), None)

            if self.ticket_seleccionado:
                for campo in self.campos_editables.keys():
                    self.campos_editables[campo] = str(self.ticket_seleccionado.get(campo, ''))
                self.mostrar_mensaje_temporal("Datos del ticket cargados", "success")
                self.posicion_cursor_descripcion = len(self.campos_editables['Descripcion'])
            else:
                self.mostrar_mensaje_temporal("Ticket no encontrado", "error")
        except Exception as e:
            self.mostrar_mensaje_temporal(f"Error al cargar datos: {str(e)}", "error")

    def guardar_cambios(self):
        """Guarda los cambios del ticket en Google Sheets"""
        if not self.ticket_seleccionado:
            self.mostrar_mensaje_temporal("Seleccione un ticket primero", "error")
            return

        try:
            updates = {}
            for k, v in self.campos_editables.items():
                if k not in self.campos_no_editables:
                    valor_anterior = str(self.ticket_seleccionado.get(k, ''))
                    if valor_anterior != v:
                        updates[k] = v
                        self.registrar_cambio(k, valor_anterior, v)

            if updates:
                self.gsheets.update_ticket(self.ticket_seleccionado['ticket_id'], updates)

                # Actualizar localmente
                for key, value in updates.items():
                    self.ticket_seleccionado[key] = value

                self.mostrar_mensaje_temporal("Cambios guardados correctamente", "success")
                self.cargar_tickets()
            else:
                self.mostrar_mensaje_temporal("No hay cambios para guardar", "info")

        except Exception as e:
            self.mostrar_mensaje_temporal(f"Error al guardar: {str(e)}", "error")

    def mostrar_mensaje_temporal(self, mensaje, tipo):
        """Muestra un mensaje temporal en la interfaz"""
        self.mensaje_estado = mensaje
        self.tipo_mensaje = tipo
        self.mostrar_mensaje = True
        self.tiempo_mensaje = pygame.time.get_ticks()

    def registrar_cambio(self, campo, valor_anterior, valor_nuevo):
        """Registra un cambio en el historial"""
        if not self.ticket_seleccionado:
            return

        if valor_anterior == valor_nuevo:
            return

        entrada = {
            'fecha': pygame.time.get_ticks(),  # Usamos ticks como timestamp
            'ticket_id': self.ticket_seleccionado['ticket_id'],
            'dispositivo': self.ticket_seleccionado['Dispositivo'],
            'campo': campo,
            'anterior': valor_anterior,
            'nuevo': valor_nuevo
        }

        self.historial.insert(0, entrada)  # Añadir al principio

        # Limitar el tamaño del historial
        if len(self.historial) > self.max_historial:
            self.historial = self.historial[:self.max_historial]


    def manejar_evento(self, evento):
        """Maneja los eventos de la interfaz"""
        if evento.type == pygame.MOUSEBUTTONDOWN:
            pos = evento.pos

            if self.boton_volver.rect.collidepoint(pos):
                return "volver"
            elif self.boton_refrescar.rect.collidepoint(pos):
                self.cargar_tickets()
                if self.ticket_seleccionado:
                    self.cargar_datos_ticket(self.ticket_seleccionado['ticket_id'])
            elif self.boton_guardar.rect.collidepoint(pos):
                self.guardar_cambios()

            # Click en tickets de la lista
            for i, rect in enumerate(self.item_rects):
                if rect.collidepoint(pos) and i < len(self.tickets):
                    self.cargar_datos_ticket(self.tickets[i]['ticket_id'])
                    break

            # Click en campos editables con mayor precisión
            self.manejar_click_campos(pos)

        elif evento.type == pygame.MOUSEWHEEL:
            if self.area_scroll.collidepoint(pygame.mouse.get_pos()):
                max_scroll = max(0, len(self.tickets) * self.altura_item - self.area_scroll.height)
                self.scroll_offset -= evento.y * 20
                self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

        elif evento.type == pygame.KEYDOWN:
            self.manejar_entrada_texto(evento)
        elif evento.type == pygame.MOUSEWHEEL:
            if self.area_scroll.collidepoint(pygame.mouse.get_pos()):
                # Scroll para la lista de tickets (existente)
                max_scroll = max(0, len(self.tickets) * self.altura_item - self.area_scroll.height)
                self.scroll_offset -= evento.y * 20
                self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))
            elif self.area_historial.collidepoint(pygame.mouse.get_pos()):
                # Scroll para el historial
                max_scroll_hist = max(0, len(self.historial) * 20 - self.area_historial.height)
                self.scroll_historial -= evento.y * 20
                self.scroll_historial = max(0, min(self.scroll_historial, max_scroll_hist))

    def manejar_click_campos(self, pos):
        """Maneja los clicks en los campos editables con mayor precisión"""
        # Desactivar todos los campos primero
        self.campos_activos = {k: False for k in self.campos_activos}

        if not self.ticket_seleccionado:
            return

        # Verificar clic en los rectángulos de los campos guardados
        for campo, rect in self.campo_rects.items():
            if campo not in self.campos_no_editables and rect.collidepoint(pos):
                self.campos_activos[campo] = True
                # Reiniciar cursor al hacer clic
                self.cursor_visible = True
                self.tiempo_cursor = pygame.time.get_ticks()

                # Para el campo de descripción, establecer posición del cursor al final
                if campo == 'Descripcion':
                    self.posicion_cursor_descripcion = len(self.campos_editables['Descripcion'])
                break

    def dibujar_historial(self, superficie):
        """Dibuja el historial de cambios"""
        titulo = self.fuente_normal.render("Historial de Cambios:", True, (0, 0, 0))
        superficie.blit(titulo, (self.area_historial.x, self.area_historial.y - 25))

        pygame.draw.rect(superficie, (255, 230, 230), self.area_historial)  # Fondo rojo claro
        pygame.draw.rect(superficie, (200, 0, 0), self.area_historial, 2)  # Borde rojo

        if not self.historial:
            texto = self.fuente_pequena.render("No hay cambios registrados", True, (100, 100, 100))
            superficie.blit(texto, (self.area_historial.x + 10, self.area_historial.y + 10))
            return

        # Área de contenido con scroll
        area_contenido = pygame.Rect(
            self.area_historial.x + 5,
            self.area_historial.y + 5,
            self.area_historial.width - 10,
            self.area_historial.height - 10
        )

        # Crear una superficie para el contenido (para el scroll)
        contenido_surface = pygame.Surface((area_contenido.width, len(self.historial) * 20))
        contenido_surface.fill((255, 240, 240))  # Fondo rojo muy claro

        for i, cambio in enumerate(self.historial):
            y_pos = i * 20 - self.scroll_historial

            if y_pos + 20 < 0 or y_pos > area_contenido.height:
                continue  # No dibujar elementos fuera de vista

            # Formatear la entrada del historial
            texto_base = f"{cambio['dispositivo']} - {cambio['campo']}: "
            texto_anterior = f"de '{cambio['anterior']}' "
            texto_nuevo = f"a '{cambio['nuevo']}'"

            # Renderizar cada parte con diferente color
            base = self.fuente_pequena.render(texto_base, True, (0, 0, 0))
            anterior = self.fuente_pequena.render(texto_anterior, True, (100, 100, 100))
            nuevo = self.fuente_pequena.render(texto_nuevo, True, (200, 150, 0))  # Amarillo/naranja

            contenido_surface.blit(base, (5, y_pos))
            contenido_surface.blit(anterior, (5 + base.get_width(), y_pos))
            contenido_surface.blit(nuevo, (5 + base.get_width() + anterior.get_width(), y_pos))

        # Recortar y dibujar solo la parte visible
        superficie.blit(contenido_surface, area_contenido,
                        (0, self.scroll_historial, area_contenido.width, area_contenido.height))

    def manejar_entrada_texto(self, evento):
        """Maneja la entrada de texto en los campos activos con mayor precisión"""
        for campo, activo in self.campos_activos.items():
            if activo and campo not in self.campos_no_editables:
                # Reiniciar temporizador del cursor
                self.tiempo_cursor = pygame.time.get_ticks()
                self.cursor_visible = True

                if campo == 'Descripcion':
                    self.manejar_entrada_descripcion(evento)
                else:
                    if evento.key == pygame.K_BACKSPACE:
                        self.campos_editables[campo] = self.campos_editables[campo][:-1]
                    elif evento.key == pygame.K_RETURN:
                        self.campos_activos[campo] = False
                    elif evento.key == pygame.K_ESCAPE:
                        self.campos_activos[campo] = False
                    elif evento.key == pygame.K_TAB:
                        self.manejar_cambio_campo_tab()
                    elif len(self.campos_editables[campo]) < 100:  # Límite para otros campos
                        if evento.unicode.isprintable():
                            self.campos_editables[campo] += evento.unicode
                break

    def manejar_entrada_descripcion(self, evento):
        """Maneja la entrada de texto específicamente para el campo de descripción"""
        descripcion = self.campos_editables['Descripcion']

        if evento.key == pygame.K_BACKSPACE:
            if self.posicion_cursor_descripcion > 0:
                # Eliminar caracter en la posición del cursor
                descripcion = descripcion[:self.posicion_cursor_descripcion - 1] + descripcion[
                                                                                   self.posicion_cursor_descripcion:]
                self.posicion_cursor_descripcion -= 1
                self.campos_editables['Descripcion'] = descripcion
        elif evento.key == pygame.K_DELETE:
            if self.posicion_cursor_descripcion < len(descripcion):
                # Eliminar caracter después del cursor
                descripcion = descripcion[:self.posicion_cursor_descripcion] + descripcion[
                                                                               self.posicion_cursor_descripcion + 1:]
                self.campos_editables['Descripcion'] = descripcion
        elif evento.key == pygame.K_LEFT:
            if self.posicion_cursor_descripcion > 0:
                self.posicion_cursor_descripcion -= 1
        elif evento.key == pygame.K_RIGHT:
            if self.posicion_cursor_descripcion < len(descripcion):
                self.posicion_cursor_descripcion += 1
        elif evento.key == pygame.K_HOME:
            self.posicion_cursor_descripcion = 0
        elif evento.key == pygame.K_END:
            self.posicion_cursor_descripcion = len(descripcion)
        elif evento.key == pygame.K_RETURN:
            # Insertar salto de línea (si no excede el máximo de líneas)
            lineas = self.obtener_lineas_descripcion()
            if len(lineas) < self.max_lineas_descripcion:
                descripcion = descripcion[:self.posicion_cursor_descripcion] + '\n' + descripcion[
                                                                                      self.posicion_cursor_descripcion:]
                self.posicion_cursor_descripcion += 1
                self.campos_editables['Descripcion'] = descripcion
        elif evento.key == pygame.K_ESCAPE:
            self.campos_activos['Descripcion'] = False
        elif evento.key == pygame.K_TAB:
            self.manejar_cambio_campo_tab()
        elif len(descripcion) < 500 and evento.unicode and evento.unicode.isprintable():
            # Insertar caracter en la posición del cursor
            descripcion = descripcion[:self.posicion_cursor_descripcion] + evento.unicode + descripcion[
                                                                                            self.posicion_cursor_descripcion:]
            self.posicion_cursor_descripcion += 1
            self.campos_editables['Descripcion'] = descripcion

    def obtener_lineas_descripcion(self):
        """Divide el texto de la descripción en líneas de máximo 23 caracteres"""
        texto = self.campos_editables['Descripcion']
        lineas = []
        linea_actual = ""

        for caracter in texto:
            if caracter == '\n' or len(linea_actual) >= self.tamano_linea_descripcion:
                lineas.append(linea_actual)
                linea_actual = ""
                if caracter != '\n':
                    linea_actual += caracter
            else:
                linea_actual += caracter

        if linea_actual:
            lineas.append(linea_actual)

        return lineas

    def manejar_cambio_campo_tab(self):
        """Cambia entre campos editables al presionar TAB"""
        campos_editables = [c for c in self.campos_editables.keys() if c not in self.campos_no_editables]
        if not campos_editables:
            return

        # Encontrar el campo actualmente activo
        campo_actual = None
        for campo, activo in self.campos_activos.items():
            if activo:
                campo_actual = campo
                break

        if campo_actual:
            # Desactivar el campo actual
            self.campos_activos[campo_actual] = False

            # Encontrar el índice del campo actual
            try:
                indice_actual = campos_editables.index(campo_actual)
                siguiente_indice = (indice_actual + 1) % len(campos_editables)
                self.campos_activos[campos_editables[siguiente_indice]] = True
                # Reiniciar cursor al cambiar campo
                self.cursor_visible = True
                self.tiempo_cursor = pygame.time.get_ticks()
            except ValueError:
                # Si no se encuentra, activar el primero
                self.campos_activos[campos_editables[0]] = True
        else:
            # Si no hay campo activo, activar el primero
            self.campos_activos[campos_editables[0]] = True

    def actualizar(self):
        """Actualiza el estado de la interfaz"""
        # Ocultar mensaje después de 3 segundos
        if self.mostrar_mensaje and pygame.time.get_ticks() - self.tiempo_mensaje > 3000:
            self.mostrar_mensaje = False

        # Actualizar parpadeo del cursor
        if any(self.campos_activos.values()):
            tiempo_actual = pygame.time.get_ticks()
            if tiempo_actual - self.tiempo_cursor > self.intervalo_cursor:
                self.cursor_visible = not self.cursor_visible
                self.tiempo_cursor = tiempo_actual
        else:
            self.cursor_visible = False

    def dibujar(self, superficie):
        """Dibuja toda la interfaz"""
        superficie.fill(config.BACKGROUND_COLOR)

        # Título
        titulo = self.fuente_titulo.render("Gestión de Tickets", True, (0, 0, 0))
        superficie.blit(titulo, (self.ancho // 2 - titulo.get_width() // 2, 30))

        # Botones
        self.boton_volver.dibujar(superficie)
        self.boton_refrescar.dibujar(superficie)
        self.boton_guardar.dibujar(superficie)

        # Lista de tickets
        self.dibujar_lista_tickets(superficie)

        # Detalles del ticket
        self.dibujar_datos_ticket(superficie)


        #Añadir el hisotrial
        self.dibujar_historial(superficie)

        # Mensaje de estado
        if self.mostrar_mensaje:
            self.dibujar_mensaje_estado(superficie)

        # Instrucciones
        instrucciones = "Seleccione un ticket para ver y editar sus datos • Click en los campos para editarlos"
        inst_surface = self.fuente_pequena.render(instrucciones, True, (120, 120, 120))
        superficie.blit(inst_surface, (20, self.alto - 40))

    def dibujar_lista_tickets(self, superficie):
        """Dibuja la lista scrolleable de tickets"""
        etiqueta = self.fuente_normal.render("Tickets:", True, (0, 0, 0))
        superficie.blit(etiqueta, (self.area_scroll.x, self.area_scroll.y - 25))

        pygame.draw.rect(superficie, (230, 230, 230), self.area_scroll)
        pygame.draw.rect(superficie, (0, 0, 0), self.area_scroll, 2)

        self.item_rects = []
        for i, ticket in enumerate(self.tickets):
            item_y = self.area_scroll.y + i * self.altura_item - self.scroll_offset

            if item_y + self.altura_item >= self.area_scroll.top and item_y <= self.area_scroll.bottom:
                item_rect = pygame.Rect(self.area_scroll.x, item_y, self.area_scroll.width, self.altura_item)

                color = (180, 230, 180) if (self.ticket_seleccionado and
                                            ticket['ticket_id'] == self.ticket_seleccionado['ticket_id']) else (255,
                                                                                                                255,
                                                                                                                255)

                pygame.draw.rect(superficie, color, item_rect)
                pygame.draw.rect(superficie, (0, 0, 0), item_rect, 1)

                texto = f"{ticket.get('ticket_id', '')} - {ticket.get('Dispositivo', '')}"
                if len(texto) > 30:
                    texto = texto[:30] + "..."

                texto_surface = self.fuente_normal.render(texto, True, (0, 0, 0))
                superficie.blit(texto_surface, (item_rect.x + 10, item_rect.y + 10))

                self.item_rects.append(item_rect)

    def dibujar_datos_ticket(self, superficie):
        """Dibuja los datos del ticket con campo de descripción multilínea"""
        titulo_datos = self.fuente_normal.render("Detalles del Ticket:", True, (0, 0, 0))
        superficie.blit(titulo_datos, (self.area_datos.x, self.area_datos.y - 25))

        if not self.ticket_seleccionado:
            mensaje = self.fuente_normal.render("Seleccione un ticket para ver sus datos", True, (100, 100, 100))
            superficie.blit(mensaje, (self.area_datos.x + 20, self.area_datos.y + 50))
            return

        etiquetas = {
            'ticket_id': 'Ticket ID:',
            'Dispositivo': 'Dispositivo:',
            'Email': 'Email:',
            'Asunto': 'Asunto:',
            'Descripcion': 'Descripción:',
            'Status': 'Estado:'
        }

        y_pos = self.area_datos.y + 20
        mouse_pos = pygame.mouse.get_pos()

        # Limpiar los rectángulos de campos antes de volver a dibujar
        self.campo_rects = {}

        for i, (campo, etiqueta) in enumerate(etiquetas.items()):
            y_actual = y_pos + i * self.espacio_entre_campos

            # Ajustar posición vertical para el campo de descripción
            if campo == 'Descripcion':
                etiqueta_y = y_actual - 10
            else:
                etiqueta_y = y_actual

            # Etiqueta del campo
            etiqueta_surface = self.fuente_normal.render(etiqueta, True, (0, 0, 0))
            superficie.blit(etiqueta_surface, (self.area_datos.x, etiqueta_y))

            # Rectángulo para el campo (todos los campos tendrán rectángulo)
            if campo == 'Descripcion':
                # Campo de descripción más grande
                campo_rect = pygame.Rect(
                    self.area_datos.x + 150,
                    y_actual - 10,
                    self.area_datos.width - 160,
                    self.altura_campo_descripcion
                )
                # Ajustar posición del siguiente campo para que no choque
                y_pos += self.altura_campo_descripcion - self.altura_campo
            else:
                # Campos normales
                campo_rect = pygame.Rect(
                    self.area_datos.x + 150,
                    y_actual,
                    self.area_datos.width - 160,
                    self.altura_campo
                )

            # Guardar el rectángulo para detección de clics
            self.campo_rects[campo] = campo_rect

            # Campos no editables (fondo gris)
            if campo in self.campos_no_editables:
                pygame.draw.rect(superficie, (230, 230, 230), campo_rect)
                pygame.draw.rect(superficie, (180, 180, 180), campo_rect, 1)

                texto_campo = self.campos_editables[campo]
                if len(texto_campo) > 50:
                    texto_campo = texto_campo[:50] + "..."

                texto_surface = self.fuente_normal.render(texto_campo, True, (100, 100, 100))

                # Centrar texto verticalmente
                text_y = campo_rect.y + (campo_rect.height - texto_surface.get_height()) // 2
                superficie.blit(texto_surface, (campo_rect.x + 5, text_y))

            # Campos editables
            else:
                # Color de fondo (activo, hover o normal)
                if self.campos_activos[campo]:
                    color_fondo = (255, 255, 200)  # Amarillo claro para campo activo
                elif campo_rect.collidepoint(mouse_pos):
                    color_fondo = (245, 245, 245)  # Gris muy claro para hover
                else:
                    color_fondo = (255, 255, 255)  # Blanco normal

                pygame.draw.rect(superficie, color_fondo, campo_rect)
                pygame.draw.rect(superficie, (0, 0, 0), campo_rect, 1)

                # Texto del campo
                if campo == 'Descripcion':
                    self.dibujar_descripcion_multilinea(superficie, campo_rect)
                else:
                    texto_campo = self.campos_editables[campo]
                    texto_mostrar = texto_campo
                    if not self.campos_activos[campo] and len(texto_campo) > 50:
                        texto_mostrar = texto_campo[:47] + "..."

                    texto_surface = self.fuente_normal.render(texto_mostrar, True, (0, 0, 0))
                    text_y = campo_rect.y + (campo_rect.height - texto_surface.get_height()) // 2
                    superficie.blit(texto_surface, (campo_rect.x + 5, text_y))

                    # Cursor para campos normales
                    if self.campos_activos[campo] and self.cursor_visible:
                        cursor_x = campo_rect.x + 5 + texto_surface.get_width()
                        pygame.draw.line(superficie, (0, 0, 0),
                                         (cursor_x, campo_rect.y + 5),
                                         (cursor_x, campo_rect.y + 25), 2)

    def dibujar_descripcion_multilinea(self, superficie, campo_rect):
        """Dibuja el campo de descripción con múltiples líneas"""
        descripcion = self.campos_editables['Descripcion']
        lineas = self.obtener_lineas_descripcion()

        # Mostrar solo las primeras 4 líneas
        lineas_visibles = lineas[:self.max_lineas_descripcion]

        # Dibujar cada línea
        for i, linea in enumerate(lineas_visibles):
            texto_surface = self.fuente_normal.render(linea, True, (0, 0, 0))
            superficie.blit(texto_surface, (campo_rect.x + 5, campo_rect.y + 5 + i * 25))

        # Cursor para el campo de descripción
        if self.campos_activos['Descripcion'] and self.cursor_visible:
            # Calcular posición del cursor
            cursor_x, cursor_y = self.calcular_posicion_cursor_descripcion(campo_rect, lineas)
            pygame.draw.line(superficie, (0, 0, 0),
                             (cursor_x, cursor_y),
                             (cursor_x, cursor_y + 20), 2)

    def calcular_posicion_cursor_descripcion(self, campo_rect, lineas):
        """Calcula la posición (x,y) del cursor en el campo de descripción"""
        # Calcular en qué línea está el cursor
        pos = self.posicion_cursor_descripcion
        linea_actual = 0
        pos_en_linea = 0
        caracteres_recorridos = 0

        for i, linea in enumerate(lineas):
            if pos <= caracteres_recorridos + len(linea):
                linea_actual = i
                pos_en_linea = pos - caracteres_recorridos
                break
            caracteres_recorridos += len(linea)

        # Si el cursor está después del último caracter
        if pos >= len(self.campos_editables['Descripcion']):
            if lineas:
                linea_actual = len(lineas) - 1
                pos_en_linea = len(lineas[linea_actual])
            else:
                linea_actual = 0
                pos_en_linea = 0

        # Asegurarse que no exceda las líneas visibles
        if linea_actual >= self.max_lineas_descripcion:
            linea_actual = self.max_lineas_descripcion - 1
            pos_en_linea = len(lineas[linea_actual]) if linea_actual < len(lineas) else 0

        # Calcular posición x del cursor
        texto_hasta_cursor = lineas[linea_actual][:pos_en_linea] if linea_actual < len(lineas) else ""
        ancho_texto = self.fuente_normal.size(texto_hasta_cursor)[0]

        cursor_x = campo_rect.x + 5 + ancho_texto
        cursor_y = campo_rect.y + 5 + linea_actual * 25

        return cursor_x, cursor_y

    def dibujar_mensaje_estado(self, superficie):
        """Dibuja el mensaje de estado temporal"""
        colores = {
            'info': (70, 130, 180),
            'success': (34, 139, 34),
            'error': (220, 20, 60)
        }

        color = colores.get(self.tipo_mensaje, colores['info'])
        mensaje_surface = self.fuente_normal.render(self.mensaje_estado, True, color)

        fondo_rect = pygame.Rect(
            self.ancho // 2 - mensaje_surface.get_width() // 2 - 10,
            self.alto - 90,
            mensaje_surface.get_width() + 20,
            30
        )
        pygame.draw.rect(superficie, (240, 240, 240), fondo_rect)
        pygame.draw.rect(superficie, color, fondo_rect, 2)
        superficie.blit(mensaje_surface, (fondo_rect.x + 10, fondo_rect.y + 5))