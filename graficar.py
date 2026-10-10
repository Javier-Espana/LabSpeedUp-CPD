#!/usr/bin/env python3
"""
graficar.py - Procesa CSVs de Lab 12 (CC3069), calcula S, E, C y F,
guarda los archivos *_con_S_E.csv y genera las 7 gráficas correspondientes.

Métricas:
  S = Ts / Tp
  E = S / p
  C = p * Tp
  F = S / C = Ts / (p * Tp^2)
"""

import sys
import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

def procesar_csv(filepath):
    """Lee CSV, calcula métricas S, E, C, F y guarda *_con_S_E.csv"""
    df = pd.read_csv(filepath)
    # S = t_seq / t_par
    df['S'] = df['t_seq'] / df['t_par']
    # E = S / p
    df['E'] = df['S'] / df['p']
    # C = p * t_par
    df['C'] = df['p'] * df['t_par']
    # F = S / C
    df['F'] = df['S'] / df['C']
    
    base, ext = os.path.splitext(filepath)
    out_name = f"{base}_con_S_E{ext}"
    df.to_csv(out_name, index=False)
    print(f"Calculadas métricas S, E, C, F -> {out_name}")
    return df

def graficar_amdahl(dfs):
    """Genera gráfica 1 (Speedup) y gráfica 2 (Eficiencia) para Amdahl"""
    # Gráfica 1: Speedup vs p para varios fp
    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=300)
    colores = {'fp=1.00': '#1f77b4', 'fp=0.95': '#2ca02c', 'fp=0.90': '#ff7f0e',
               'fp=0.75': '#d62728', 'fp=0.50': '#9467bd'}
    
    max_p = 1
    for param, df in sorted(dfs.items(), reverse=True):
        df_sorted = df.sort_values('p')
        p = df_sorted['p']
        S = df_sorted['S']
        max_p = max(max_p, p.max())
        color = colores.get(param, None)
        ax.plot(p, S, marker='o', linewidth=2, label=f"{param} (medido)", color=color)
        
    p_ideal = np.linspace(1, max_p, 100)
    ax.plot(p_ideal, p_ideal, 'k--', alpha=0.6, label='Ideal lineal (S = p)')
    
    ax.set_title('Parte 1 — Speedup vs Número de Hilos (Ley de Amdahl)', fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel('Número de hilos (p)', fontsize=12)
    ax.set_ylabel('Speedup (S = Ts / Tp)', fontsize=12)
    ax.set_xticks(range(1, max_p + 1))
    ax.legend(frameon=True, facecolor='white', framealpha=0.9)
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig('grafica_amdahl_speedup.png')
    plt.close()
    print("Generada: grafica_amdahl_speedup.png")

    # Gráfica 2: Eficiencia vs p para varios fp
    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=300)
    for param, df in sorted(dfs.items(), reverse=True):
        df_sorted = df.sort_values('p')
        p = df_sorted['p']
        E = df_sorted['E']
        color = colores.get(param, None)
        ax.plot(p, E, marker='s', linewidth=2, label=f"{param}", color=color)
        
    ax.axhline(1.0, color='k', linestyle='--', alpha=0.6, label='Eficiencia 100% (E = 1.0)')
    ax.set_title('Parte 1 — Eficiencia vs Número de Hilos (E = S / p)', fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel('Número de hilos (p)', fontsize=12)
    ax.set_ylabel('Eficiencia (E)', fontsize=12)
    ax.set_xticks(range(1, max_p + 1))
    ax.set_ylim(0, 1.1)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9)
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig('grafica_amdahl_eficiencia.png')
    plt.close()
    print("Generada: grafica_amdahl_eficiencia.png")

def graficar_suma(df):
    """Genera gráfica 3 (Speedup vs p por tamaño N) y gráfica 4 (Speedup vs N para pmax)"""
    fig, ax = plt.subplots(figsize=(8.5, 5.5), dpi=300)
    tamanos = sorted(df['N'].unique())
    colores_n = plt.cm.viridis(np.linspace(0.1, 0.9, len(tamanos)))
    
    max_p = df['p'].max()
    for idx, N in enumerate(tamanos):
        sub = df[df['N'] == N].sort_values('p')
        ax.plot(sub['p'], sub['S'], marker='o', linewidth=2, label=f"N = {N:,}", color=colores_n[idx])
        
    p_ideal = np.sort(df['p'].unique())
    ax.plot(p_ideal, p_ideal, 'k--', alpha=0.6, label='Ideal lineal (S = p)')
    ax.axhline(1.0, color='red', linestyle=':', alpha=0.7, label='Límite ganancia (S = 1.0)')
    
    ax.set_title('Parte 2 — Speedup al Sumar N Números vs Hilos', fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel('Número de hilos (p)', fontsize=12)
    ax.set_ylabel('Speedup (S)', fontsize=12)
    ax.set_xticks(p_ideal)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9, title="Tamaño de entrada")
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig('grafica_suma_speedup.png')
    plt.close()
    print("Generada: grafica_suma_speedup.png")

    # Gráfica 4: Granularidad - Speedup vs N para p = pmax
    fig, ax = plt.subplots(figsize=(8.5, 5.5), dpi=300)
    sub_pmax = df[df['p'] == max_p].sort_values('N')
    ax.plot(sub_pmax['N'], sub_pmax['S'], marker='D', color='#e74c3c', linewidth=2.5, markersize=8, label=f"Speedup medido (p = {max_p})")
    ax.axhline(1.0, color='black', linestyle='--', alpha=0.8, label='Umbral de ganancia (S = 1.0)')
    
    ax.set_xscale('log')
    ax.set_title(f'Parte 2 — Granularidad: Speedup vs N (p = {max_p} hilos)', fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel('Tamaño del arreglo N (escala logarítmica)', fontsize=12)
    ax.set_ylabel('Speedup (S)', fontsize=12)
    ax.grid(True, which="both", linestyle='--', alpha=0.5)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9)
    plt.tight_layout()
    plt.savefig('grafica_suma_granularidad.png')
    plt.close()
    print("Generada: grafica_suma_granularidad.png")

def graficar_desbalance(dfs):
    """Genera gráfica 5 (Speedup) y gráfica 6 (Eficiencia) para Desbalance"""
    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=300)
    colores_sched = {'static': '#e74c3c', 'dynamic': '#2ecc71', 'guided': '#3498db'}
    
    max_p = 1
    for sched, df in dfs.items():
        sub = df.sort_values('p')
        max_p = max(max_p, sub['p'].max())
        ax.plot(sub['p'], sub['S'], marker='o', linewidth=2, label=f"schedule({sched})", color=colores_sched.get(sched))
        
    p_ideal = np.linspace(1, max_p, 100)
    ax.plot(p_ideal, p_ideal, 'k--', alpha=0.6, label='Ideal lineal (S = p)')
    
    ax.set_title('Parte 3 — Desbalance: Speedup según Estrategia de Schedule', fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel('Número de hilos (p)', fontsize=12)
    ax.set_ylabel('Speedup (S)', fontsize=12)
    ax.set_xticks(range(1, max_p + 1))
    ax.legend(frameon=True, facecolor='white', framealpha=0.9)
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig('grafica_desbalance_speedup.png')
    plt.close()
    print("Generada: grafica_desbalance_speedup.png")

    # Gráfica 6: Eficiencia vs p
    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=300)
    for sched, df in dfs.items():
        sub = df.sort_values('p')
        ax.plot(sub['p'], sub['E'], marker='s', linewidth=2, label=f"schedule({sched})", color=colores_sched.get(sched))
        
    ax.axhline(1.0, color='k', linestyle='--', alpha=0.6, label='Eficiencia 100% (E = 1.0)')
    ax.set_title('Parte 3 — Desbalance: Eficiencia (E = S / p)', fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel('Número de hilos (p)', fontsize=12)
    ax.set_ylabel('Eficiencia (E)', fontsize=12)
    ax.set_xticks(range(1, max_p + 1))
    ax.set_ylim(0, 1.1)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9)
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig('grafica_desbalance_eficiencia.png')
    plt.close()
    print("Generada: grafica_desbalance_eficiencia.png")

def graficar_gustafson(df):
    """Genera gráfica 7: Escalabilidad de Gustafson (Speedup medido vs Ideal y tiempos)"""
    fig, ax1 = plt.subplots(figsize=(8.5, 5.5), dpi=300)
    sub = df.sort_values('p')
    p = sub['p']
    S = sub['S']
    
    color_s = '#2980b9'
    ax1.plot(p, S, marker='o', linewidth=2.5, color=color_s, label='Speedup Gustafson medido')
    ax1.plot(p, p, 'k--', alpha=0.6, label='Ideal lineal (S = p)')
    
    # Amdahl predicción para fp = 0.83 (1/6 secuencial ~ 0.17)
    fp_amdahl = 100000.0 / 120000.0
    s_amdahl = 1.0 / ((1.0 - fp_amdahl) + (fp_amdahl / p))
    ax1.plot(p, s_amdahl, 'r:', linewidth=2, label=f'Amdahl fijando W (fp={fp_amdahl:.2f})')
    
    ax1.set_title('Parte 4 — Escalabilidad con Problema Creciente (Ley de Gustafson)', fontsize=14, fontweight='bold', pad=12)
    ax1.set_xlabel('Número de hilos (p)', fontsize=12)
    ax1.set_ylabel('Speedup (S)', fontsize=12, color=color_s)
    ax1.tick_params(axis='y', labelcolor=color_s)
    ax1.set_xticks(range(1, p.max() + 1))
    ax1.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.9)
    ax1.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig('grafica_gustafson_speedup.png')
    plt.close()
    print("Generada: grafica_gustafson_speedup.png")

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 graficar.py <archivos_csv...>")
        print("Ejemplos:")
        print("  python3 graficar.py amdahl_*.csv")
        print("  python3 graficar.py suma.csv")
        print("  python3 graficar.py desb_*.csv")
        print("  python3 graficar.py gustafson.csv")
        print("  python3 graficar.py *.csv")
        sys.exit(1)

    archivos = []
    for arg in sys.argv[1:]:
        # Expandir globs si la shell no lo hizo
        match = glob.glob(arg)
        if match:
            archivos.extend(match)
        elif os.path.exists(arg):
            archivos.append(arg)
            
    archivos = sorted(list(set([f for f in archivos if not f.endswith('_con_S_E.csv')])))
    
    amdahl_dfs = {}
    desbalance_dfs = {}
    suma_df = None
    gustafson_df = None
    
    for f in archivos:
        df = procesar_csv(f)
        modo = df['modo'].iloc[0] if 'modo' in df.columns else None
        
        if modo == 'amdahl':
            param = df['param'].iloc[0] if 'param' in df.columns else os.path.basename(f)
            amdahl_dfs[param] = df
        elif modo == 'suma':
            suma_df = df
        elif modo == 'desbalance':
            param = df['param'].iloc[0] if 'param' in df.columns else os.path.basename(f)
            desbalance_dfs[param] = df
        elif modo == 'gustafson':
            gustafson_df = df
            
    if amdahl_dfs:
        graficar_amdahl(amdahl_dfs)
    if suma_df is not None:
        graficar_suma(suma_df)
    if desbalance_dfs:
        graficar_desbalance(desbalance_dfs)
    if gustafson_df is not None:
        graficar_gustafson(gustafson_df)

if __name__ == '__main__':
    main()
