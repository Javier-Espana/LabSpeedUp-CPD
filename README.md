# Laboratorio 12 — Speedup y Eficiencia (CC3069)

**Computación Paralela y Distribuida**  
**Universidad del Valle de Guatemala**  
**Autores:** Javier España (`Javier-Espana`) & `bar23354`  
**Repositorio GitHub:** [https://github.com/Javier-Espana/LabSpeedUp-CPD.git](https://github.com/Javier-Espana/LabSpeedUp-CPD.git)

---

## Estructura del Repositorio

El repositorio se encuentra estrictamente organizado por módulos funcionales:

```text
LabSpeedUp-CPD/
├── entregables/                # Los 4 entregables oficiales para entrega
│   ├── reporte_lab12.pdf       # Informe técnico completo en PDF
│   ├── evidencia_lab12.pdf     # Evidencia visual: lscpu, compilación, corridas y 7 gráficas
│   ├── resultados_lab12.zip    # Archivo ZIP con los 10 CSVs originales + 10 CSVs procesados
│   └── lab12_speedup.c         # Código fuente modificado con el reto superlineal
│
├── src/                        # Código fuente en C
│   ├── lab12_speedup.c         # Implementación de los 4 modos y el reto superlineal
│   └── Makefile                # Reglas de compilación locales
│
├── data/                       # Almacenamiento estructurado de mediciones
│   ├── originales/             # Los 10 CSVs crudos de las corridas del programa
│   │   ├── amdahl_fp100.csv
│   │   ├── amdahl_fp95.csv
│   │   ├── amdahl_fp90.csv
│   │   ├── amdahl_fp75.csv
│   │   ├── amdahl_fp50.csv
│   │   ├── suma.csv
│   │   ├── desb_static.csv
│   │   ├── desb_dynamic.csv
│   │   ├── desb_guided.csv
│   │   └── gustafson.csv
│   ├── procesados/             # Los 10 CSVs con métricas S, E, C y F calculadas
│   │   ├── amdahl_fp100_con_S_E.csv
│   │   ├── amdahl_fp95_con_S_E.csv
│   │   ├── amdahl_fp90_con_S_E.csv
│   │   ├── amdahl_fp75_con_S_E.csv
│   │   ├── amdahl_fp50_con_S_E.csv
│   │   ├── suma_con_S_E.csv
│   │   ├── desb_static_con_S_E.csv
│   │   ├── desb_dynamic_con_S_E.csv
│   │   ├── desb_guided_con_S_E.csv
│   │   └── gustafson_con_S_E.csv
│   └── reto_superlineal/       # Datos y verificación del reto opcional
│       ├── superlineal.csv
│       └── superlineal_5corridas.txt
│
├── graficas/                   # Las 7 figuras generadas en alta resolución (PNG)
│   ├── grafica_amdahl_speedup.png
│   ├── grafica_amdahl_eficiencia.png
│   ├── grafica_suma_speedup.png
│   ├── grafica_suma_granularidad.png
│   ├── grafica_desbalance_speedup.png
│   ├── grafica_desbalance_eficiencia.png
│   └── grafica_gustafson_speedup.png
│
├── capturas/                   # Capturas gráficas de terminal para evidencia
│   ├── captura_lscpu.png
│   ├── captura_make.png
│   ├── captura_amdahl.png
│   ├── captura_suma.png
│   ├── captura_desbalance.png
│   ├── captura_gustafson.png
│   └── captura_superlineal.png
│
├── informes/                   # Fuentes LaTeX y compilados de los informes
│   ├── reporte_lab12.tex
│   ├── reporte_lab12.pdf
│   ├── evidencia_lab12.tex
│   └── evidencia_lab12.pdf
│
├── scripts/                    # Scripts auxiliares en Python
│   ├── graficar.py             # Procesador de CSVs y generador de gráficas
│   └── generar_capturas_terminal.py  # Generador de capturas de terminal estilizadas
│
├── docs/                       # Enunciado oficial del laboratorio
│   └── Lab12_Speedup_CC3069.pdf
│
├── Makefile                    # Makefile principal en la raíz
├── README.md                   # Este documento
└── .gitignore                  # Exclusiones de Git
```

---

## Especificaciones del Hardware Experimental

- **Modelo de CPU:** AMD Ryzen 5 8400F 6-Core Processor
- **Arquitectura:** x86_64 Zen 4 (6 núcleos físicos, 12 núcleos lógicos)
- **Simultaneous Multi-Threading (SMT):** Habilitado (2 hilos por núcleo físico)
- **Cores híbridos (P/E):** No posee (diseño homogéneo estándar)
- **Jerarquía de Caché:**
  - L1d: 192 KiB (6 × 32 KiB)
  - L1i: 192 KiB (6 × 32 KiB)
  - L2: 6 MiB (6 × 1 MiB privada por núcleo)
  - L3: 16 MiB (compartida en el CCD)

---

## Compilación y Ejecución

### 1. Compilar el programa
```bash
make
```
Genera el ejecutable `./lab12`.

### 2. Ejecutar los experimentos
```bash
# Modo Amdahl (Parte 1)
./lab12 amdahl 400000 1.00 > data/originales/amdahl_fp100.csv
./lab12 amdahl 400000 0.95 > data/originales/amdahl_fp95.csv
./lab12 amdahl 400000 0.90 > data/originales/amdahl_fp90.csv
./lab12 amdahl 400000 0.75 > data/originales/amdahl_fp75.csv
./lab12 amdahl 400000 0.50 > data/originales/amdahl_fp50.csv

# Modo Suma (Parte 2)
./lab12 suma > data/originales/suma.csv

# Modo Desbalance (Parte 3)
./lab12 desbalance static > data/originales/desb_static.csv
./lab12 desbalance dynamic > data/originales/desb_dynamic.csv
./lab12 desbalance guided > data/originales/desb_guided.csv

# Modo Gustafson (Parte 4)
./lab12 gustafson > data/originales/gustafson.csv

# Modo Reto Opcional Superlineal
./lab12 superlineal > data/reto_superlineal/superlineal.csv
```

### 3. Procesar datos y generar gráficas
```bash
python3 scripts/graficar.py data/originales/*.csv
```
Calcula $S$, $E$, $C$, $F$ guardando en `data/procesados/` y almacena las 7 gráficas en `graficas/`.

### 4. Compilar los informes PDF
```bash
make pdfs
```
Compila `informes/reporte_lab12.tex` e `informes/evidencia_lab12.tex`, y sincroniza las versiones finales en `entregables/`.

---

## Entregables Oficiales

Todos los archivos exigidos por la rúbrica están centralizados en el directorio [`entregables/`](entregables/):

1. **`reporte_lab12.pdf`**: Informe de 14 páginas con datos del hardware, hipótesis, tabla Parte 1, cálculos a mano de $S, E, C, F$, respuestas completas a las preguntas numeradas, derivación de los modelos de Amdahl y Gustafson, síntesis de las 4 fugas de eficiencia ($\eta_f, \eta_c, \eta_b, \eta_r$), y análisis del reto.
2. **`evidencia_lab12.pdf`**: Informe de 10 páginas con capturas de salida de `lscpu`, compilación de `make`, ejecución de los 4 modos y las 7 figuras experimentales completas.
3. **`resultados_lab12.zip`**: Archivo comprimido con los 10 CSVs originales y los 10 CSVs procesados con columnas añadidas.
4. **`lab12_speedup.c`**: Código en C con el experimento superlineal y documentación de caché.
