import tkinter as tk
from tkinter import ttk, messagebox
import random

# =========================
# DATOS DEL JUEGO
# =========================
personajes = [
    "Dr. Valeria Cruz - Médica forense",
    "Ing. Mateo Ríos - Ingeniero en robótica",
    "Lic. Andrea Solís - Abogada",
    "Chef Bruno Salvatierra - Chef profesional",
    "Prof. Elena Vargas - Historiadora"
]

lugares = [
    "Mansión antigua",
    "Hotel de lujo",
    "Cocina industrial",
    "Laboratorio",
    "Biblioteca"
]

armas = [
    "Cuchillo",
    "Pistola",
    "Veneno",
    "Cable eléctrico",
    "Llave inglesa"
]

# =========================
# SELECCIÓN ALEATORIA
# =========================
culpable = random.choice(personajes)
lugar_crimen = random.choice(lugares)
arma_crimen = random.choice(armas)

# =========================
# HISTORIAS / FINALES
# =========================
def obtener_historia_final(culpable, lugar, arma):
    nombre = culpable.split(" - ")[0]

    if "Chef Bruno" in culpable:
        return f"{nombre} utilizó {arma.lower()} en {lugar.lower()} aprovechando que conocía cada rincón del lugar. Todo fue planeado como una venganza silenciosa."
    elif "Valeria" in culpable:
        return f"{nombre} manipuló la escena del crimen en {lugar.lower()} y usó {arma.lower()} con precisión, confiando en que sus conocimientos la harían parecer inocente."
    elif "Mateo" in culpable:
        return f"{nombre} preparó todo en {lugar.lower()} y empleó {arma.lower()} de manera calculada. Su mente lógica casi lo ayuda a salir libre."
    elif "Andrea" in culpable:
        return f"{nombre} pensó que nadie sospecharía de ella. En {lugar.lower()}, usó {arma.lower()} y creó una coartada casi perfecta."
    else:
        return f"{nombre} escondió la verdad entre libros, pistas falsas y engaños. El crimen ocurrió en {lugar.lower()} usando {arma.lower()}."

# =========================
# FUNCIONES
# =========================
def mostrar_personajes():
    area_texto.delete("1.0", tk.END)
    area_texto.insert(tk.END, "SOSPECHOSOS:\n\n")
    for p in personajes:
        area_texto.insert(tk.END, f"• {p}\n")

def mostrar_lugares():
    area_texto.delete("1.0", tk.END)
    area_texto.insert(tk.END, "LOCACIONES:\n\n")
    for l in lugares:
        area_texto.insert(tk.END, f"• {l}\n")

def mostrar_armas():
    area_texto.delete("1.0", tk.END)
    area_texto.insert(tk.END, "ARMAS:\n\n")
    for a in armas:
        area_texto.insert(tk.END, f"• {a}\n")

def dar_pista():
    pistas = [
        f"Una huella fue encontrada cerca de {lugar_crimen}.",
        f"Los investigadores creen que el arma pudo haber sido {arma_crimen}.",
        f"Un testigo vio a alguien relacionado con {culpable.split(' - ')[0]}.",
        f"El crimen ocurrió en un sitio importante: {lugar_crimen}.",
        f"La víctima tenía relación reciente con {culpable.split(' - ')[0]}."
    ]
    pista = random.choice(pistas)
    area_texto.delete("1.0", tk.END)
    area_texto.insert(tk.END, "PISTA ENCONTRADA:\n\n")
    area_texto.insert(tk.END, pista)

def acusar():
    sospechoso = combo_personaje.get()
    lugar = combo_lugar.get()
    arma = combo_arma.get()

    if not sospechoso or not lugar or not arma:
        messagebox.showwarning("Faltan datos", "Debes seleccionar sospechoso, lugar y arma.")
        return

    area_texto.delete("1.0", tk.END)

    # 5 casos/finales
    if sospechoso == culpable and lugar == lugar_crimen and arma == arma_crimen:
        area_texto.insert(tk.END, "FINAL 1 – CASO RESUELTO\n\n")
        area_texto.insert(tk.END, "¡Has encontrado al verdadero culpable!\n\n")
        area_texto.insert(tk.END, obtener_historia_final(culpable, lugar_crimen, arma_crimen))

    elif sospechoso == culpable and lugar == lugar_crimen and arma != arma_crimen:
        area_texto.insert(tk.END, "FINAL 2 – ARMA EQUIVOCADA\n\n")
        area_texto.insert(tk.END, "Descubriste al culpable y el lugar, pero te equivocaste en el arma.\n")
        area_texto.insert(tk.END, "El caso queda incompleto y el culpable casi escapa.")

    elif sospechoso == culpable and lugar != lugar_crimen and arma == arma_crimen:
        area_texto.insert(tk.END, "FINAL 3 – LUGAR EQUIVOCADO\n\n")
        area_texto.insert(tk.END, "Encontraste al culpable y el arma, pero fallaste en la locación.\n")
        area_texto.insert(tk.END, "Las pistas no fueron interpretadas correctamente.")

    elif sospechoso != culpable and lugar == lugar_crimen and arma == arma_crimen:
        area_texto.insert(tk.END, "FINAL 4 – SOSPECHOSO EQUIVOCADO\n\n")
        area_texto.insert(tk.END, "Identificaste bien el arma y la locación, pero acusaste a la persona incorrecta.\n")
        area_texto.insert(tk.END, "El verdadero culpable sigue libre.")

    else:
        area_texto.insert(tk.END, "FINAL 5 – MISTERIO SIN RESOLVER\n\n")
        area_texto.insert(tk.END, "La acusación fue incorrecta.\n")
        area_texto.insert(tk.END, "No lograste conectar bien las pistas y el caso quedó abierto.\n\n")

    area_texto.insert(tk.END, "\n\n--- SOLUCIÓN REAL ---\n")
    area_texto.insert(tk.END, f"Culpable: {culpable}\n")
    area_texto.insert(tk.END, f"Locación: {lugar_crimen}\n")
    area_texto.insert(tk.END, f"Arma: {arma_crimen}\n")

# =========================
# VENTANA PRINCIPAL
# =========================
ventana = tk.Tk()
ventana.title("CLUE - Simulador")
ventana.geometry("900x600")
ventana.configure(bg="#1e1e2f")

titulo = tk.Label(
    ventana,
    text="CLUE – Caso Misterioso",
    font=("Arial", 20, "bold"),
    bg="#1e1e2f",
    fg="white"
)
titulo.pack(pady=10)

subtitulo = tk.Label(
    ventana,
    text="Investiga, analiza las pistas y encuentra al culpable.",
    font=("Arial", 11),
    bg="#1e1e2f",
    fg="#d9d9d9"
)
subtitulo.pack()

frame_principal = tk.Frame(ventana, bg="#1e1e2f")
frame_principal.pack(fill="both", expand=True, padx=15, pady=15)

# Panel izquierdo
frame_izq = tk.Frame(frame_principal, bg="#2b2b40", padx=10, pady=10)
frame_izq.pack(side="left", fill="y", padx=10)

tk.Label(frame_izq, text="Investigar", font=("Arial", 14, "bold"), bg="#2b2b40", fg="white").pack(pady=5)

tk.Button(frame_izq, text="Ver personajes", width=20, command=mostrar_personajes).pack(pady=5)
tk.Button(frame_izq, text="Ver locaciones", width=20, command=mostrar_lugares).pack(pady=5)
tk.Button(frame_izq, text="Ver armas", width=20, command=mostrar_armas).pack(pady=5)
tk.Button(frame_izq, text="Buscar pista", width=20, command=dar_pista).pack(pady=5)

tk.Label(frame_izq, text="Acusación", font=("Arial", 14, "bold"), bg="#2b2b40", fg="white").pack(pady=15)

combo_personaje = ttk.Combobox(frame_izq, values=personajes, width=30, state="readonly")
combo_personaje.pack(pady=5)
combo_personaje.set("Selecciona sospechoso")

combo_lugar = ttk.Combobox(frame_izq, values=lugares, width=30, state="readonly")
combo_lugar.pack(pady=5)
combo_lugar.set("Selecciona lugar")

combo_arma = ttk.Combobox(frame_izq, values=armas, width=30, state="readonly")
combo_arma.pack(pady=5)
combo_arma.set("Selecciona arma")

tk.Button(frame_izq, text="Acusar", width=20, command=acusar).pack(pady=15)

# Panel derecho
frame_der = tk.Frame(frame_principal, bg="#2b2b40", padx=10, pady=10)
frame_der.pack(side="right", fill="both", expand=True)

tk.Label(frame_der, text="Narrativa / Resultados", font=("Arial", 14, "bold"), bg="#2b2b40", fg="white").pack(pady=5)

area_texto = tk.Text(frame_der, wrap="word", font=("Arial", 11), bg="#f4f4f4", fg="black")
area_texto.pack(fill="both", expand=True)

introduccion = (
    "Bienvenido al simulador del juego de mesa CLUE.\n\n"
    "Una muerte misteriosa ha ocurrido y tu misión es descubrir:\n"
    "• Quién fue el culpable\n"
    "• En qué lugar ocurrió el crimen\n"
    "• Qué arma se utilizó\n\n"
    "Usa los botones de investigación, reúne pistas y realiza tu acusación."
)

area_texto.insert(tk.END, introduccion)

ventana.mainloop()