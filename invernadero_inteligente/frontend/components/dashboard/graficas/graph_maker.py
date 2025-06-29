import io
import matplotlib.pyplot as plt
import pygame
from datetime import datetime
from invernadero_inteligente.frontend.services.api_service import APIService


def generar_grafica(tipo_dato: str, dispositivo: str, limit: int = 1000, ancho_px: int = 900,
                    alto_px: int = 500, fecha_inicio: str = None, fecha_fin: str = None) -> pygame.Surface:
    """
    Genera una gráfica con líneas continuas diferenciando techo abierto/cerrado

    Args:
        tipo_dato: Tipo de sensor (Temperatura, Humedad, etc.)
        dispositivo: Número de serie del dispositivo
        limit: Límite de registros a obtener
        ancho_px: Ancho de la gráfica en píxeles
        alto_px: Alto de la gráfica en píxeles
        fecha_inicio: Fecha de inicio en formato "DD/MM/YYYY" (opcional)
        fecha_fin: Fecha de fin en formato "DD/MM/YYYY" (opcional)
    """
    try:
        # Debug: Mostrar parámetros recibidos
        print(f"graph_maker: Generando gráfica con parámetros:")
        print(f"  - dispositivo: {dispositivo}")
        print(f"  - tipo_dato: {tipo_dato}")
        print(f"  - limit: {limit}")
        print(f"  - fecha_inicio: {fecha_inicio}")
        print(f"  - fecha_fin: {fecha_fin}")

        # Obtener datos del backend con filtro de fechas
        response = APIService.obtener_datos_raw(
            dispositivo=dispositivo,
            tipo_dato=tipo_dato,
            limit=limit,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

        print(f"graph_maker: Respuesta del API: {response.get('status')}")

        if response.get("status") != "success" or not response.get("data"):
            mensaje_error = response.get("message", "No se encontraron datos")
            print(f"graph_maker: Error - {mensaje_error}")
            return APIService._crear_superficie_error(mensaje_error)

        datos_raw = response["data"]
        print(f"graph_maker: Datos recibidos: {len(datos_raw)} registros")

        # Procesar datos
        datos = []
        for r in datos_raw:
            try:
                fecha_hora = f"{r.get('fecha', '')} {r.get('hora', '')}"
                dt = datetime.strptime(fecha_hora, "%d/%m/%Y %H:%M:%S")
                datos.append({
                    "timestamp": dt,
                    "valor": float(r.get("valor", 0)),
                    "estado_techo": int(r.get("estado_techo", 0))
                })
            except (ValueError, KeyError) as e:
                print(f"graph_maker: Error procesando dato: {e} - Dato: {r}")
                continue

        print(f"graph_maker: Datos procesados: {len(datos)} registros válidos")

        if len(datos) < 2:
            mensaje_error = "Datos insuficientes para generar gráfica"
            if fecha_inicio or fecha_fin:
                mensaje_error += " en el rango seleccionado"
            print(f"graph_maker: {mensaje_error}")
            return APIService._crear_superficie_error(mensaje_error)

        # Ordenar por fecha
        datos.sort(key=lambda x: x["timestamp"])

        # Debug: Mostrar rango de fechas en los datos
        if datos:
            print(f"graph_maker: Rango de fechas en datos: {datos[0]['timestamp']} a {datos[-1]['timestamp']}")

        # Preparar datos para gráfica
        fechas = [d["timestamp"] for d in datos]
        valores = [d["valor"] for d in datos]
        estados_techo = [d["estado_techo"] for d in datos]
        indices = list(range(len(datos)))

        # Configurar gráfica
        fig, ax = plt.subplots(figsize=(ancho_px / 100, alto_px / 100))

        # Separar datos por estado del techo
        indices_abierto = []
        valores_abierto = []
        indices_cerrado = []
        valores_cerrado = []

        for i, (indice, valor, estado) in enumerate(zip(indices, valores, estados_techo)):
            if estado == 1:  # Techo abierto
                indices_abierto.append(indice)
                valores_abierto.append(valor)
            else:  # Techo cerrado
                indices_cerrado.append(indice)
                valores_cerrado.append(valor)

        print(f"graph_maker: Puntos techo abierto: {len(indices_abierto)}")
        print(f"graph_maker: Puntos techo cerrado: {len(indices_cerrado)}")

        # Dibujar línea de tendencia para techo abierto (azul)
        if indices_abierto:
            ax.plot(indices_abierto, valores_abierto,
                    marker='o', linestyle='-',
                    color='#66b3ff',  # Azul claro
                    markersize=6,
                    linewidth=2.5,
                    markeredgecolor='#0066cc',
                    markeredgewidth=1,
                    label='Techo abierto')

        # Dibujar línea de tendencia para techo cerrado (verde)
        if indices_cerrado:
            ax.plot(indices_cerrado, valores_cerrado,
                    marker='s', linestyle='-',
                    color='#2e8b57',  # Verde marino
                    markersize=6,
                    linewidth=2.5,
                    markeredgecolor='#1a5d3a',
                    markeredgewidth=1,
                    label='Techo cerrado')

        # Configuración del título (incluye información de rango si aplica)
        titulo = f"{tipo_dato} - {dispositivo}"
        info_adicional = []

        if fecha_inicio or fecha_fin:
            if fecha_inicio and fecha_fin:
                info_adicional.append(f"{fecha_inicio} - {fecha_fin}")
            elif fecha_inicio:
                info_adicional.append(f"Desde {fecha_inicio}")
            elif fecha_fin:
                info_adicional.append(f"Hasta {fecha_fin}")

        # Agregar información del número de registros
        info_adicional.append(f"{len(datos)} registros")

        if info_adicional:
            titulo += f"\n({', '.join(info_adicional)})"

        ax.set_title(titulo, fontsize=14, fontweight='bold')
        ax.set_xlabel("Tiempo", fontsize=12)
        ax.set_ylabel(f"{tipo_dato}", fontsize=12)
        ax.grid(True, alpha=0.3)

        # Crear leyenda personalizada solo si hay datos para cada estado
        from matplotlib.lines import Line2D
        legend_elements = []

        if indices_abierto:
            legend_elements.append(
                Line2D([0], [0], marker='o', color='#66b3ff', linewidth=2.5,
                       markeredgecolor='#0066cc', markeredgewidth=1,
                       label=f'Techo abierto ({len(indices_abierto)} pts)', markersize=8)
            )

        if indices_cerrado:
            legend_elements.append(
                Line2D([0], [0], marker='s', color='#2e8b57', linewidth=2.5,
                       markeredgecolor='#1a5d3a', markeredgewidth=1,
                       label=f'Techo cerrado ({len(indices_cerrado)} pts)', markersize=8)
            )

        if legend_elements:
            ax.legend(handles=legend_elements, loc='upper right', framealpha=0.9)

        # Configurar etiquetas de fechas en el eje X
        # Seleccionar fechas representativas para evitar saturación
        num_etiquetas = min(8, len(fechas))  # Máximo 8 etiquetas
        step = max(1, len(fechas) // num_etiquetas)

        fechas_mostrar = []
        posiciones_mostrar = []

        for i in range(0, len(fechas), step):
            # Formato de fecha más detallado si el rango es pequeño
            if len(fechas) <= 50:  # Si hay pocos datos, mostrar fecha y hora
                fecha_str = fechas[i].strftime("%d/%m\n%H:%M")
            else:  # Si hay muchos datos, mostrar solo fecha
                fecha_str = fechas[i].strftime("%d/%m/%y")

            fechas_mostrar.append(fecha_str)
            posiciones_mostrar.append(i)

        # Asegurar que incluimos el último punto
        if posiciones_mostrar[-1] != len(fechas) - 1:
            if len(fechas) <= 50:
                fecha_str = fechas[-1].strftime("%d/%m\n%H:%M")
            else:
                fecha_str = fechas[-1].strftime("%d/%m/%y")

            fechas_mostrar.append(fecha_str)
            posiciones_mostrar.append(len(fechas) - 1)

        ax.set_xticks(posiciones_mostrar)
        ax.set_xticklabels(fechas_mostrar, rotation=45, ha='right', fontsize=10)

        # Ajustar diseño para evitar que se corten las etiquetas
        plt.tight_layout()

        # Convertir a superficie Pygame
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close(fig)
        buf.seek(0)

        print("graph_maker: Gráfica generada exitosamente")
        return pygame.image.load(buf).convert_alpha()

    except Exception as e:
        print(f"graph_maker: Error generando gráfica: {e}")
        import traceback
        traceback.print_exc()

        mensaje_error = "Error al generar gráfica"
        if fecha_inicio or fecha_fin:
            mensaje_error += " con el rango de fechas especificado"
        return APIService._crear_superficie_error(mensaje_error)