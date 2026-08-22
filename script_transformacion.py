"""
=============================================================================
SCRIPT DE TRANSFORMACIÓN DE DATOS - ENAHO (2024 - 2025)
=============================================================================
"""

import os
import pandas as pd

# Ruta base del proyecto
ruta_datos = "C:/Users/YENNY/Desktop/PROYECTOS INEI/problem-sets-fcd/"
ruta_salida = os.path.join(ruta_datos, "problem-set-1", "p2")
os.makedirs(ruta_salida, exist_ok=True)

anios_transformar = [2024, 2025]
proceso_exitoso = False

for anio in anios_transformar:
    archivo = os.path.join(ruta_datos, f"Enaho01-{anio}-100.csv")
    
    if os.path.exists(archivo):
        print(f"--> Leyendo y transformando archivo del año {anio}...")
        try:
            df = pd.read_csv(archivo, encoding='latin-1', sep=None, engine='python')
        except:
            df = pd.read_csv(archivo, encoding='latin-1', sep=';', low_memory=False)
            
        df.columns = df.columns.str.lower()
        
        # 1. Variable dicotómica 'target' (No respuesta si result no es 1 ni 2)
        if 'result' in df.columns:
            df['target'] = df['result'].apply(lambda x: 0 if x in [1, 2] else 1)
        
        # 2. Departamento y Provincia a partir de 'ubigeo'
        if 'ubigeo' in df.columns:
            df['ubigeo'] = df['ubigeo'].astype(str).str.zfill(6)
            df['departamento'] = df['ubigeo'].str.slice(0, 2)
            df['provincia'] = df['ubigeo'].str.slice(0, 4)
            
        # 3. Urbano y Rural a partir de 'estrato' (<=5 urbano, >=6 rural)
        if 'estrato' in df.columns:
            df['estrato_num'] = pd.to_numeric(df['estrato'], errors='coerce')
            df['urbano'] = df['estrato_num'].apply(lambda x: 1 if x <= 5 else (0 if pd.notnull(x) else None))
            df['rural'] = df['estrato_num'].apply(lambda x: 1 if x >= 6 else (0 if pd.notnull(x) else None))
            
        # 4. Región natural a partir de 'dominio'
        if 'dominio' in df.columns:
            dominio_num = pd.to_numeric(df['dominio'], errors='coerce')
            def clasificar_region(d):
                if d == 8: return 'Lima Metropolitana'
                elif d in [1, 2, 3]: return 'Costa'
                elif d in [4, 5, 6]: return 'Sierra'
                elif d == 7: return 'Selva'
                else: return 'No especificado'
            df['region_natural'] = dominio_num.apply(clasificar_region)
            
        # 5. Variables discretas (mes, trimestre, etc.)
        if 'mes' in df.columns:
            df['mes_num'] = pd.to_numeric(df['mes'], errors='coerce')
            df['trimestre'] = (df['mes_num'] - 1) // 3 + 1
            
        cols_a_categorizar = ['departamento', 'provincia', 'urbano', 'rural', 'region_natural', 'dominio']
        for col in cols_a_categorizar:
            if col in df.columns:
                df[col] = df[col].astype('category')
                
        # 6. Estadísticas agregadas cruzadas con la variable target
        if 'region_natural' in df.columns and 'target' in df.columns:
            resumen = df.groupby('region_natural')['target'].agg(
                total_hogares='count',
                no_respuestas='sum',
                tasa_media='mean'
            ).reset_index()
            resumen['porcentaje_no_respuesta'] = resumen['tasa_media'] * 100
            print(f"\n--- Estadísticas Agregadas {anio} ---")
            print(resumen)
            
            ruta_resumen = os.path.join(ruta_salida, f"resumen_no_respuesta_{anio}.csv")
            resumen.to_csv(ruta_resumen, index=False)

        # 7. Guardar el dataframe transformado completo
        archivo_salida = os.path.join(ruta_salida, f"enaho_transformado_{anio}.csv")
        df.to_csv(archivo_salida, index=False)
        print(f"¡Éxito! Archivo transformado guardado en: {archivo_salida}\n")
        proceso_exitoso = True
    else:
        print(f"No se encontró el archivo para el año {anio}.")

if proceso_exitoso:
    print("=========================================================")
    print("¡TODAS LAS TRANSFORMACIONES FUERON COMPLETADAS CON ÉXITO!")
    print("=========================================================")
else:
    print("No se procesó ningún archivo. Verifica las rutas.")