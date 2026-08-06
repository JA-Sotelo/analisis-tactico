# Análisis Táctico · Fútbol de Salón

App de análisis táctico deportivo con visión artificial (YOLOv8) y estadísticas en tiempo real.

## Stack
- Python · Streamlit · YOLOv8 · OpenCV · pandas · matplotlib · plotly

## Estructura
```
datos/
  equipos.json              ← índice de equipos
  olimpia/
    equipo.json             ← info del equipo
    OLIMPIA.png             ← escudo
    partidos/
      2026-06-14_vs_marmoleria/
        partido.json        ← metadata del partido
        partido_completo.csv
        partido_Marmoleria_REAL_2026-06-14.json
        MARMOLERIA.png
```

## Agregar un nuevo partido
1. Crear carpeta en `datos/{equipo}/partidos/{fecha}_vs_{rival}/`
2. Copiar `partido.json`, CSV y escudo del rival
3. Actualizar `datos/equipos.json` si es un equipo nuevo
4. Push a GitHub → Streamlit Cloud se actualiza solo

## Desarrollado con
YOLOv8 · Python · OpenCV · Streamlit
