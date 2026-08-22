import os
import pandas as pd

# -----------------------------------------------------------------------------
# 1. DEFINICIÓN DE CONFIGURACIÓN Y RUTAS DE TRABAJO
# -----------------------------------------------------------------------------
# Definimos la ruta base del proyecto para centralizar el acceso a los archivos.
# Esto permite que el script sea modular y solo requiera cambiar esta variable 
# si se traslada de computadora o directorio (cumpliendo con la directriz de inputs).
ruta_datos = "C:/Users/YENNY/Desktop/PROYECTOS INEI/problem-sets-fcd/"

# Establecemos el rango de años analizados (del 2019 al 2025 inclusive).
anios = range(2019, 2026)

# Inicializamos una lista vacía para almacenar de forma temporal los dataframes 
# procesados de cada año antes de unirlos en un cuadro consolidado final.
lista_porcentajes = []

# -----------------------------------------------------------------------------
# 2. BUCLE ITERATIVO DE LECTURA Y ANÁLISIS TEMPORAL
# -----------------------------------------------------------------------------
# Recorremos cada año de la secuencia establecida para automatizar la carga de microdatos.
for anio in anios:
    # Construimos dinámicamente la ruta absoluta de cada archivo CSV del Módulo 1 (Enaho01).
    archivo = os.path.join(ruta_datos, f"Enaho01-{anio}-100.csv")
    
    # Verificamos mediante un condicional si el archivo físico realmente existe en la PC,
    # evitando que el programa se detenga abruptamente por archivos faltantes.
    if os.path.exists(archivo):
        try:
            # -----------------------------------------------------------------
            # 3. LECTURA ROBUSTA DE MICRODATOS
            # -----------------------------------------------------------------
            # Se utiliza pd.read_csv con los siguientes parámetros clave:
            # - encoding='latin-1': Necesario para interpretar correctamente tildes 
            #   y caracteres especiales del español propios de las bases del INEI.
            # - sep=None y engine='python': Permiten detectar automáticamente el 
            #   delimitador del archivo (coma ',' o punto y coma ';'), asegurando 
            #   compatibilidad entre las diferentes versiones de años de la ENAHO.
            df = pd.read_csv(archivo, encoding='latin-1', sep=None, engine='python')
            
            # Estandarizamos los nombres de las columnas a minúsculas (.str.lower())
            # para evitar errores de coincidencia por mayúsculas en los nombres de variables.
            df.columns = df.columns.str.lower()
            
            # -----------------------------------------------------------------
            # 4. PROCESAMIENTO Y CÁLCULO ESTADÍSTICO
            # -----------------------------------------------------------------
            # Comprobamos que la variable objetivo 'result' (resultado de entrevista) exista.
            if 'result' in df.columns:
                # value_counts(normalize=True) calcula la proporción (frecuencia relativa)
                # de cada categoría dentro de la variable 'result'.
                # .reset_index() convierte la serie estadística resultante en una tabla limpia.
                tabla = df['result'].value_counts(normalize=True).reset_index()
                
                # Renombramos las columnas de la tabla resultante para mayor claridad.
                tabla.columns = ['result', 'porcentaje']
                
                # Transformamos la proporción decimal a un formato porcentual (0 a 100%).
                tabla['porcentaje'] = tabla['porcentaje'] * 100
                
                # Creamos una columna adicional con el año analizado para mantener 
                # la trazabilidad temporal en el cuadro final consolidado.
                tabla['anio'] = anio
                
                # Almacenamos la tabla calculada del año en nuestra lista acumuladora.
                lista_porcentajes.append(tabla)
                
        except Exception as e:
            # Capturamos cualquier excepción imprevista durante la lectura del archivo de ese año.
            print(f"Advertencia: No se pudo procesar correctamente el año {anio}: {e}")

# -----------------------------------------------------------------------------
# 5. CONSOLIDACIÓN Y EXPORTACIÓN DEL ENTREGABLE FINAL
# -----------------------------------------------------------------------------
# Validamos si la lista contiene datos procesados exitosamente.
if lista_porcentajes:
    # pd.concat une verticalmente todas las tablas individuales de los años analizados 
    # en un único gran DataFrame consolidado.
    df_cuadro_final = pd.concat(lista_porcentajes, ignore_index=True)
    
    # Definimos la ruta de salida exacta requerida dentro de la estructura del Problem Set.
    ruta_salida_csv = os.path.join(ruta_datos, "problem-set-1", "p2", "porcentaje_no_respuesta_por_anio.csv")
    
    # Exportamos el DataFrame final a formato CSV excluyendo el índice numérico automático (index=False).
    df_cuadro_final.to_csv(ruta_salida_csv, index=False)
    
    print("¡Cuadro de porcentajes guardado exitosamente en la carpeta p2!")
else:
    print("Error crítico: No se procesó ningún archivo. Verifique la ubicación de los CSV.")