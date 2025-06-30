from invernadero_inteligente.backend.services.google_sheets import GoogleSheetsDB

class DataPoint:
    def __init__(self, fecha, hora, dispositivo, tipo_dato, valor, estado_techo):
        self.fecha = fecha
        self.hora = hora
        self.dispositivo = dispositivo
        self.tipo_dato = tipo_dato
        self.valor = valor
        self.estado_techo = estado_techo

    def to_dict(self):
        return {
            "fecha": self.fecha,
            "hora": self.hora,
            "dispositivo": self.dispositivo,
            "tipo_dato": self.tipo_dato,
            "valor": self.valor,
            "estado_techo": self.estado_techo
        }

    @staticmethod
    def get_by_device_and_type(dispositivo, tipo_dato, limit=100, fecha_inicio=None, fecha_fin=None):
        db = GoogleSheetsDB()
        worksheet = db.get_worksheet("Datos")
        registros = worksheet.get_all_records()

        # Mapeo de tipos de dato del sistema → hoja de cálculo
        tipo_mapeo = {
            "temperatura": "Temperatura",
            "humedad_suelo": "Humedad",  # Si "Humedad" representa suelo
            "humedad_ambiente": "Humedad Ambiente",  # Si existe otra columna futura
            "nivel_drenaje": "Nivel Drenaje",
            "nivel_bomba": "Nivel Bomba"
        }

        tipo_en_hoja = tipo_mapeo.get(tipo_dato, tipo_dato)

        # Filtrado por dispositivo y tipo de dato (case insensitive)
        registros_filtrados = [
            r for r in registros
            if str(r.get("Dispositivo")).strip().upper() == str(dispositivo).strip().upper()
            and str(r.get("TipoDato")).strip().lower() == str(tipo_en_hoja).strip().lower()
        ]

        # Opcional: filtrado por fecha si se provee
        if fecha_inicio:
            registros_filtrados = [r for r in registros_filtrados if r.get("Fecha") >= fecha_inicio]
        if fecha_fin:
            registros_filtrados = [r for r in registros_filtrados if r.get("Fecha") <= fecha_fin]

        # Tomar los últimos `limit` registros
        registros_ordenados = registros_filtrados[-limit:]

        # Convertir a DataPoint
        return [
            DataPoint(
                r.get("Fecha"),
                r.get("Hora"),
                r.get("Dispositivo"),
                r.get("TipoDato"),
                r.get("Valor"),
                r.get("EstadoTecho", 0)
            )
            for r in registros_ordenados
        ]

    @staticmethod
    def get_filtered_data(dispositivo=None, tipo_dato=None, fecha_inicio=None, fecha_fin=None, limit=1000):
        db = GoogleSheetsDB()
        worksheet = db.get_worksheet("Datos")
        registros = worksheet.get_all_records()

        # Mapeo de nombres para lectura
        tipo_mapeo = {
            "temperatura": "Temperatura",
            "humedad_suelo": "Humedad",
            "humedad_ambiente": "Humedad Ambiente",
            "nivel_drenaje": "Nivel Drenaje",
            "nivel_bomba": "Nivel Bomba"
        }

        tipo_en_hoja = tipo_mapeo.get(tipo_dato, tipo_dato) if tipo_dato else None

        # Filtro completo
        registros_filtrados = []
        for r in registros:
            cumple = True

            if dispositivo:
                cumple &= str(r.get("Dispositivo", "")).strip().upper() == dispositivo.strip().upper()

            if tipo_en_hoja:
                cumple &= str(r.get("TipoDato", "")).strip().lower() == tipo_en_hoja.strip().lower()

            if fecha_inicio:
                cumple &= r.get("Fecha") >= fecha_inicio
            if fecha_fin:
                cumple &= r.get("Fecha") <= fecha_fin

            if cumple:
                registros_filtrados.append(r)

        registros_ordenados = registros_filtrados[-limit:]

        return [
            DataPoint(
                r.get("Fecha"),
                r.get("Hora"),
                r.get("Dispositivo"),
                r.get("TipoDato"),
                r.get("Valor"),
                r.get("EstadoTecho", 0)
            )
            for r in registros_ordenados
        ]
