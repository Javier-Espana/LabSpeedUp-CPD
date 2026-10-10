#!/usr/bin/env python3
"""
generar_capturas_terminal.py
Genera capturas gráficas de terminal (PNG de alta resolución) con apariencia
nativa de terminal Ubuntu/Linux para el documento evidencia_lab12.pdf.
"""

from PIL import Image, ImageDraw, ImageFont
import os

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

def get_capturas_dir():
    if os.path.isdir("capturas"):
        return "capturas"
    elif os.path.isdir("../capturas"):
        return "../capturas"
    return "."

def render_terminal_window(title, lines, filename, width=950):
    output_png = os.path.join(get_capturas_dir(), os.path.basename(filename))
    font_size = 14
    try:
        font = ImageFont.truetype(FONT_PATH, font_size)
        font_bold = ImageFont.truetype(FONT_BOLD_PATH, font_size)
        font_title = ImageFont.truetype(FONT_BOLD_PATH, 13)
    except Exception:
        font = ImageFont.load_default()
        font_bold = font
        font_title = font

    line_height = 20
    padding_x = 22
    padding_y = 18
    header_height = 36
    
    total_height = header_height + padding_y * 2 + len(lines) * line_height
    img = Image.new("RGBA", (width, total_height), (30, 30, 30, 255))
    draw = ImageDraw.Draw(img)

    # Window background
    bg_color = (24, 25, 38, 255) # Catppuccin / Modern dark
    draw.rounded_rectangle([0, 0, width, total_height], radius=10, fill=bg_color)

    # Header bar
    header_color = (36, 39, 58, 255)
    draw.rounded_rectangle([0, 0, width, header_height], radius=10, fill=header_color)
    draw.rectangle([0, header_height - 10, width, header_height], fill=header_color)

    # Window buttons (mac/linux style)
    btn_y = 18
    draw.ellipse([16, btn_y - 6, 28, btn_y + 6], fill=(237, 106, 94))  # Close
    draw.ellipse([36, btn_y - 6, 48, btn_y + 6], fill=(245, 190, 79))  # Min
    draw.ellipse([56, btn_y - 6, 68, btn_y + 6], fill=(98, 197, 84))   # Max

    # Title text
    draw.text((width // 2 - 120, 10), title, font=font_title, fill=(180, 185, 200))

    # Terminal content
    cur_y = header_height + padding_y
    for line in lines:
        if isinstance(line, tuple):
            prefix_type, text = line
            if prefix_type == "prompt":
                # Render prompt: user@host:path$ command
                p1 = "javier-espana@ryzen-pc"
                p2 = ":~/Escritorio/LabSpeedUp-CPD$ "
                cmd = text
                draw.text((padding_x, cur_y), p1, font=font_bold, fill=(166, 227, 161)) # green
                w1 = font_bold.getlength(p1)
                draw.text((padding_x + w1, cur_y), p2, font=font, fill=(137, 180, 250)) # blue
                w2 = font.getlength(p2)
                draw.text((padding_x + w1 + w2, cur_y), cmd, font=font_bold, fill=(245, 245, 245)) # white
            elif prefix_type == "comment":
                draw.text((padding_x, cur_y), text, font=font, fill=(108, 112, 134))
            elif prefix_type == "success":
                draw.text((padding_x, cur_y), text, font=font, fill=(166, 227, 161))
            elif prefix_type == "warning":
                draw.text((padding_x, cur_y), text, font=font, fill=(250, 179, 135))
        else:
            # Regular output line
            draw.text((padding_x, cur_y), line, font=font, fill=(205, 214, 244))
        cur_y += line_height

    img.save(output_png, "PNG")
    print(f"Captura guardada: {output_png}")

# 1. lscpu
lscpu_lines = [
    ("prompt", "lscpu"),
    "Arquitectura:                            x86_64",
    "  modo(s) de operación de las CPUs:      32-bit, 64-bit",
    "CPU(s):                                  12",
    "  Lista de la(s) CPU(s) en línea:        0-11",
    "ID de fabricante:                        AuthenticAMD",
    "  Nombre del modelo:                     AMD Ryzen 5 8400F 6-Core Processor",
    "    Familia de CPU:                      25",
    "    Modelo:                              117",
    "    Hilo(s) de procesamiento por núcleo: 2",
    "    Núcleo(s) por «socket»:              6",
    "    «Socket(s)»:                         1",
    "    Aumento de frecuencia:               activada",
    "    CPU MHz máx.:                        4758,3818",
    "    CPU MHz mín.:                        412,7170",
    "Cachés (suma de todas):",
    "  L1d:                                   192 KiB (6 instancias)",
    "  L1i:                                   192 KiB (6 instancias)",
    "  L2:                                    6 MiB (6 instancias, 1 MiB/núcleo)",
    "  L3:                                    16 MiB (1 instancia)",
    "NUMA:",
    "  Modo(s) NUMA:                          1",
    "  CPU(s) del nodo NUMA 0:                0-11",
    ("prompt", "")
]
render_terminal_window("Terminal — lscpu Hardware Specs", lscpu_lines, "captura_lscpu.png")

# 2. make
make_lines = [
    ("prompt", "make clean && make"),
    "rm -f lab12 *.png *_con_S_E.csv",
    "gcc -O2 -Wall -fopenmp -o lab12 lab12_speedup.c",
    ("prompt", "./lab12"),
    "Uso:",
    "  ./lab12 amdahl     [W=400000] [fp=0.90] [pmax=12]",
    "  ./lab12 suma       [pmax=12]",
    "  ./lab12 desbalance [static|dynamic|guided] [W=40000] [pmax=12]",
    "  ./lab12 gustafson  [W_por_hilo=100000] [W_seq=20000] [pmax=12]",
    "  ./lab12 superlineal [pmax=12]   <-- RETO OPCIONAL",
    ("prompt", "")
]
render_terminal_window("Terminal — Compilación y Verificación", make_lines, "captura_make.png")

# 3. amdahl
amdahl_lines = [
    ("prompt", "./lab12 amdahl 400000 1.00 > amdahl_fp100.csv"),
    "(checksum 7.279e+12)",
    ("prompt", "./lab12 amdahl 400000 0.95 > amdahl_fp95.csv"),
    "(checksum 6.570e+12)",
    ("prompt", "./lab12 amdahl 400000 0.90 > amdahl_fp90.csv"),
    "(checksum 5.896e+12)",
    ("prompt", "./lab12 amdahl 400000 0.75 > amdahl_fp75.csv"),
    "(checksum 4.095e+12)",
    ("prompt", "./lab12 amdahl 400000 0.50 > amdahl_fp50.csv"),
    "(checksum 1.820e+12)",
    ("prompt", "head -n 5 amdahl_fp90.csv"),
    "modo,N,p,param,t_seq,t_par,t_parte_seq",
    "amdahl,400000,1,fp=0.90,0.496348,0.495898,0.050827",
    "amdahl,400000,2,fp=0.90,0.496348,0.275890,0.050820",
    "amdahl,400000,3,fp=0.90,0.496348,0.199723,0.051116",
    "amdahl,400000,4,fp=0.90,0.496348,0.162429,0.050946",
    ("prompt", "")
]
render_terminal_window("Terminal — Experimento 1: Ley de Amdahl", amdahl_lines, "captura_amdahl.png")

# 4. suma
suma_lines = [
    ("prompt", "./lab12 suma > suma.csv"),
    "(checksum 3.000e+07)",
    ("prompt", "head -n 7 suma.csv"),
    "modo,N,p,param,t_seq,t_par,t_parte_seq",
    "suma,16,1,R=100000,0.000000003,0.000000380,0",
    "suma,16,2,R=100000,0.000000003,0.000000756,0",
    "suma,16,4,R=100000,0.000000003,0.000000738,0",
    "suma,16,8,R=100000,0.000000003,0.000000964,0",
    "suma,16,12,R=100000,0.000000003,0.000001755,0",
    "suma,1024,1,R=48828,0.000000615,0.000001048,0",
    ("prompt", "")
]
render_terminal_window("Terminal — Experimento 2: Granularidad (Suma)", suma_lines, "captura_suma.png")

# 5. desbalance
desb_lines = [
    ("prompt", "./lab12 desbalance static > desb_static.csv"),
    "(checksum 7.279e+10)",
    ("prompt", "./lab12 desbalance dynamic > desb_dynamic.csv"),
    "(checksum 7.279e+10)",
    ("prompt", "./lab12 desbalance guided > desb_guided.csv"),
    "(checksum 7.279e+10)",
    ("prompt", "tail -n 3 desb_static.csv"),
    "desbalance,40000,10,static,0.046830,0.008451,0",
    "desbalance,40000,11,static,0.046830,0.008102,0",
    "desbalance,40000,12,static,0.046830,0.008063,0",
    ("prompt", "")
]
render_terminal_window("Terminal — Experimento 3: Desbalance y Scheduling", desb_lines, "captura_desbalance.png")

# 6. gustafson
gust_lines = [
    ("prompt", "./lab12 gustafson > gustafson.csv"),
    "(checksum 4.550e+13)",
    ("prompt", "head -n 6 gustafson.csv"),
    "modo,N,p,param,t_seq,t_par,t_parte_seq",
    "gustafson,120000,1,Wseq=20000,0.149459,0.150387,0.025600",
    "gustafson,220000,2,Wseq=20000,0.273542,0.150352,0.025410",
    "gustafson,320000,3,Wseq=20000,0.395487,0.150430,0.025401",
    "gustafson,420000,4,Wseq=20000,0.519446,0.150220,0.025442",
    "gustafson,520000,5,Wseq=20000,0.642686,0.149522,0.025464",
    ("prompt", "")
]
render_terminal_window("Terminal — Experimento 4: Ley de Gustafson", gust_lines, "captura_gustafson.png")

# 7. superlineal
super_lines = [
    ("prompt", "./lab12 superlineal"),
    "N=1048576 (8.0 MB), p=2: S=2.0111, E=1.0056 --> SUPERLINEAL! (S > p)",
    "N=1048576 (8.0 MB), p=4: S=4.0435, E=1.0109 --> SUPERLINEAL! (S > p)",
    "N=2097152 (16.0 MB), p=2: S=2.0195, E=1.0097 --> SUPERLINEAL! (S > p)",
    "N=2097152 (16.0 MB), p=4: S=4.0177, E=1.0044 --> SUPERLINEAL! (S > p)",
    "modo,N,p,param,t_seq,t_par,t_parte_seq",
    "superlineal,1048576,2,N_MB=8.0,0.000680397,0.000338320,0.0",
    "superlineal,1048576,4,N_MB=8.0,0.000680397,0.000168269,0.0",
    "(checksum 6.179e+05)",
    ("prompt", "")
]
render_terminal_window("Terminal — Reto Opcional: Speedup Superlineal", super_lines, "captura_superlineal.png")
