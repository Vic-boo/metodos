import numpy as np
import matplotlib.pyplot as plt

# ─────────────────────────────────────────────
#  COLORES PARA CONSOLA
# ─────────────────────────────────────────────
C_TITLE  = "\033[1;36m"   # Cyan negrita
C_OK     = "\033[1;32m"   # Verde negrita
C_WARN   = "\033[1;33m"   # Amarillo negrita
C_ERR    = "\033[1;31m"   # Rojo negrita
C_INFO   = "\033[0;37m"   # Gris claro
C_RESET  = "\033[0m"

def banner():
    print(f"""
{C_TITLE}╔══════════════════════════════════════════╗
║       MÉTODO DE SPLINES CÚBICOS          ║
║     Interpolación por tramos (grado 3)   ║
╚══════════════════════════════════════════╝{C_RESET}
""")

# ─────────────────────────────────────────────
#  INGRESO Y VALIDACIÓN DE DATOS
# ─────────────────────────────────────────────
def ingresar_datos():
    while True:
        # ── Número de puntos
        while True:
            try:
                n = int(input(f"{C_INFO}¿Cuántos puntos deseas ingresar? (mínimo 3): {C_RESET}"))
                if n >= 3:
                    break
                print(f"{C_ERR}  Se necesitan al menos 3 puntos.{C_RESET}")
            except ValueError:
                print(f"{C_ERR}  Ingresa un número entero válido.{C_RESET}")

        # ── Valores de X
        print(f"\n{C_TITLE}── Ingresa los valores de X ──{C_RESET}")
        xs = []
        for i in range(n):
            while True:
                try:
                    val = float(input(f"  x[{i}] = "))
                    if val in xs:
                        print(f"{C_ERR}  Valor repetido. Los x deben ser distintos.{C_RESET}")
                    else:
                        xs.append(val)
                        break
                except ValueError:
                    print(f"{C_ERR}  Ingresa un número válido.{C_RESET}")

        # ── Valores de Y
        print(f"\n{C_TITLE}── Ingresa los valores de Y ──{C_RESET}")
        ys = []
        for i in range(n):
            while True:
                try:
                    val = float(input(f"  y[{i}] = "))
                    ys.append(val)
                    break
                except ValueError:
                    print(f"{C_ERR}  Ingresa un número válido.{C_RESET}")

        # ── Condición de frontera
        print(f"\n{C_TITLE}── Condición de frontera ──{C_RESET}")
        print("  [1] Spline NATURAL   → S''(x0) = S''(xn) = 0  (recomendado)")
        print("  [2] Spline SUJETO    → se especifican f'(x0) y f'(xn)")
        while True:
            opc = input("  Elige opción (1/2): ").strip()
            if opc in ("1", "2"):
                break
            print(f"{C_ERR}  Opción inválida.{C_RESET}")

        fp0 = fpn = 0.0
        if opc == "2":
            while True:
                try:
                    fp0 = float(input(f"  f'(x0) = f'({xs[0]}) = "))
                    fpn = float(input(f"  f'(xn) = f'({xs[-1]}) = "))
                    break
                except ValueError:
                    print(f"{C_ERR}  Ingresa números válidos.{C_RESET}")

        frontera = "natural" if opc == "1" else "sujeto"

        # ── Mostrar tabla de datos
        print(f"\n{C_TITLE}┌─────────────────────────┐")
        print(f"│    TABLA DE DATOS       │")
        print(f"├────────┬────────────────┤")
        print(f"│   X    │       Y        │")
        print(f"├────────┼────────────────┤{C_RESET}")
        for i in range(n):
            print(f"  {xs[i]:>8.4f}  │  {ys[i]:>12.4f}")
        print(f"{C_TITLE}└────────────────────────┘{C_RESET}")
        print(f"  Condición de frontera: {C_OK}{frontera.upper()}{C_RESET}")
        if frontera == "sujeto":
            print(f"  f'(x0) = {fp0},  f'(xn) = {fpn}")

        # ── Confirmación
        print()
        conf = input(f"{C_WARN}¿Los datos son correctos? (s/n): {C_RESET}").strip().lower()
        if conf == "s":
            return np.array(xs), np.array(ys), frontera, fp0, fpn
        else:
            # ── Opción de modificar puntos específicos
            while True:
                mod = input(f"{C_WARN}¿Deseas modificar un punto específico (m) o reingresar todo (r)? (m/r): {C_RESET}").strip().lower()
                if mod == "r":
                    print()
                    break  # Vuelve al inicio del while True
                elif mod == "m":
                    while True:
                        try:
                            idx = int(input(f"  Índice del punto a modificar (0 a {n-1}): "))
                            if 0 <= idx < n:
                                break
                            print(f"{C_ERR}  Índice fuera de rango.{C_RESET}")
                        except ValueError:
                            print(f"{C_ERR}  Ingresa un entero válido.{C_RESET}")
                    while True:
                        try:
                            nuevo_x = float(input(f"  Nuevo x[{idx}] (actual={xs[idx]}): "))
                            if nuevo_x in [xs[j] for j in range(n) if j != idx]:
                                print(f"{C_ERR}  Valor de X repetido.{C_RESET}")
                            else:
                                xs[idx] = nuevo_x
                                break
                        except ValueError:
                            print(f"{C_ERR}  Valor inválido.{C_RESET}")
                    while True:
                        try:
                            xs[idx] = nuevo_x
                            ys[idx] = float(input(f"  Nuevo y[{idx}] (actual={ys[idx]}): "))
                            break
                        except ValueError:
                            print(f"{C_ERR}  Valor inválido.{C_RESET}")
                    # Reordenar por x
                    orden = np.argsort(xs)
                    xs = np.array(xs)[orden]
                    ys = np.array(ys)[orden]
                    print(f"{C_OK}  Punto modificado.{C_RESET}")
                    # Volver a mostrar tabla
                    print(f"\n{C_TITLE}┌─────────────────────────┐")
                    print(f"│    TABLA ACTUALIZADA    │")
                    print(f"├────────┬────────────────┤{C_RESET}")
                    for i in range(n):
                        print(f"  x[{i}]={xs[i]:>8.4f}  │  y[{i}]={ys[i]:>8.4f}")
                    conf2 = input(f"\n{C_WARN}¿Ahora los datos son correctos? (s/n): {C_RESET}").strip().lower()
                    if conf2 == "s":
                        return np.array(xs), np.array(ys), frontera, fp0, fpn
                else:
                    print(f"{C_ERR}  Opción inválida, elige 'm' o 'r'.{C_RESET}")

# ─────────────────────────────────────────────
#  CÁLCULO DE SPLINES CÚBICOS
# ─────────────────────────────────────────────
def calcular_splines(x, y, frontera="natural", fp0=0.0, fpn=0.0):
    n = len(x) - 1  # número de subintervalos
    h = np.diff(x)  # h[i] = x[i+1] - x[i]

    # ── Construir sistema tridiagonal para M (segundas derivadas)
    # Tamaño del sistema interno: (n+1) x (n+1)
    A = np.zeros((n + 1, n + 1))
    b = np.zeros(n + 1)

    # Ecuaciones internas
    for i in range(1, n):
        A[i, i - 1] = h[i - 1]
        A[i, i]     = 2 * (h[i - 1] + h[i])
        A[i, i + 1] = h[i]
        b[i] = 6 * ((y[i + 1] - y[i]) / h[i] - (y[i] - y[i - 1]) / h[i - 1])

    # ── Condición de frontera
    if frontera == "natural":
        A[0, 0] = 1.0
        A[n, n] = 1.0
        b[0] = 0.0
        b[n] = 0.0
    else:  # sujeto
        A[0, 0] = 2 * h[0]
        A[0, 1] = h[0]
        b[0] = 6 * ((y[1] - y[0]) / h[0] - fp0)
        A[n, n - 1] = h[n - 1]
        A[n, n]     = 2 * h[n - 1]
        b[n] = 6 * (fpn - (y[n] - y[n - 1]) / h[n - 1])

    M = np.linalg.solve(A, b)  # M[i] = S''(x_i)

    # ── Coeficientes a, b, c, d para cada segmento
    coefs = []
    for i in range(n):
        ai = y[i]
        bi = (y[i + 1] - y[i]) / h[i] - h[i] * (2 * M[i] + M[i + 1]) / 6
        ci = M[i] / 2
        di = (M[i + 1] - M[i]) / (6 * h[i])
        coefs.append((ai, bi, ci, di))

    return coefs, M

# ─────────────────────────────────────────────
#  IMPRIMIR RESULTADOS
# ─────────────────────────────────────────────
def imprimir_resultados(x, y, coefs, M):
    n = len(coefs)
    print(f"\n{C_TITLE}╔══════════════════════════════════════════════════════════╗")
    print(f"║              RESULTADOS DE SPLINES CÚBICOS               ║")
    print(f"╚══════════════════════════════════════════════════════════╝{C_RESET}")

    # ── Segundas derivadas (momentos)
    print(f"\n{C_TITLE}── Segundas derivadas M[i] = S''(x_i) ──{C_RESET}")
    for i, mi in enumerate(M):
        print(f"  M[{i}] = S''({x[i]:.4f}) = {mi:.6f}")

    # ── Polinomios por tramo
    print(f"\n{C_TITLE}── Polinomios por segmento ──{C_RESET}")
    print(f"{C_INFO}  Forma: S_i(x) = a + b(x - x_i) + c(x - x_i)² + d(x - x_i)³{C_RESET}\n")
    for i, (a, b, c, d) in enumerate(coefs):
        print(f"{C_OK}  Segmento {i+1}: x ∈ [{x[i]:.4f}, {x[i+1]:.4f}]{C_RESET}")
        print(f"    S_{i+1}(x) = {a:.6f}")
        signo_b = "+" if b >= 0 else "-"
        signo_c = "+" if c >= 0 else "-"
        signo_d = "+" if d >= 0 else "-"
        print(f"           {signo_b} {abs(b):.6f}·(x - {x[i]:.4f})")
        print(f"           {signo_c} {abs(c):.6f}·(x - {x[i]:.4f})²")
        print(f"           {signo_d} {abs(d):.6f}·(x - {x[i]:.4f})³")
        print()

# ─────────────────────────────────────────────
#  EVALUAR SPLINE EN UN PUNTO
# ─────────────────────────────────────────────
def evaluar(xval, x, coefs):
    n = len(coefs)
    # Encontrar el segmento correcto
    for i in range(n - 1):
        if x[i] <= xval <= x[i + 1]:
            a, b, c, d = coefs[i]
            t = xval - x[i]
            return a + b * t + c * t**2 + d * t**3
    # Último segmento (incluye el extremo derecho)
    i = n - 1
    a, b, c, d = coefs[i]
    t = xval - x[i]
    return a + b * t + c * t**2 + d * t**3

# ─────────────────────────────────────────────
#  PREGUNTAR POR PUNTOS ADICIONALES
# ─────────────────────────────────────────────
def preguntar_puntos(x, coefs):
    while True:
        resp = input(f"\n{C_WARN}¿Deseas calcular un punto adicional? (s/n): {C_RESET}").strip().lower()
        if resp != "s":
            break
        while True:
            try:
                xval = float(input(f"  Ingresa x* (entre {x[0]:.4f} y {x[-1]:.4f}): "))
                if x[0] <= xval <= x[-1]:
                    resultado = evaluar(xval, x, coefs)
                    print(f"  {C_OK}S({xval}) = {resultado:.8f}{C_RESET}")
                    break
                else:
                    print(f"{C_ERR}  x* fuera del rango de interpolación.{C_RESET}")
            except ValueError:
                print(f"{C_ERR}  Ingresa un número válido.{C_RESET}")

# ─────────────────────────────────────────────
#  GRÁFICA
# ─────────────────────────────────────────────
def graficar(x, y, coefs):
    xs_plot = np.linspace(x[0], x[-1], 500)
    ys_plot = [evaluar(xi, x, coefs) for xi in xs_plot]

    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor("#1e1e2e")
    ax.set_facecolor("#1e1e2e")

    # Curva spline
    ax.plot(xs_plot, ys_plot, color="#89b4fa", linewidth=2.5, label="Spline cúbico")

    # Puntos originales
    ax.scatter(x, y, color="#f38ba8", zorder=5, s=70, label="Puntos de datos")

    # Líneas verticales en nodos
    for xi in x:
        ax.axvline(xi, color="#45475a", linewidth=0.6, linestyle="--")

    ax.set_title("Interpolación por Splines Cúbicos", color="white", fontsize=14, pad=12)
    ax.set_xlabel("x", color="#cdd6f4")
    ax.set_ylabel("S(x)", color="#cdd6f4")
    ax.tick_params(colors="#cdd6f4")
    for spine in ax.spines.values():
        spine.set_edgecolor("#45475a")
    ax.legend(facecolor="#313244", edgecolor="#45475a", labelcolor="white")
    ax.grid(True, color="#313244", linewidth=0.5)

    plt.tight_layout()
    print(f"\n{C_INFO}  Mostrando gráfica... (ciérrala para terminar){C_RESET}")
    plt.show()

# ─────────────────────────────────────────────
#  FLUJO PRINCIPAL
# ─────────────────────────────────────────────
def main():
    banner()
    while True:
        # 1. Ingresar datos
        x, y, frontera, fp0, fpn = ingresar_datos()

        # Ordenar por x (por si el usuario ingresó desordenado)
        orden = np.argsort(x)
        x, y = x[orden], y[orden]

        # 2. Calcular splines
        print(f"\n{C_INFO}  Calculando splines...{C_RESET}")
        coefs, M = calcular_splines(x, y, frontera, fp0, fpn)

        # 3. Imprimir resultados
        imprimir_resultados(x, y, coefs, M)

        # 4. Puntos adicionales
        preguntar_puntos(x, coefs)

        # 5. Graficar
        graficar(x, y, coefs)

        # 6. ¿Calcular con datos nuevos?
        print(f"\n{C_TITLE}{'═'*44}{C_RESET}")
        reiniciar = input(f"{C_WARN}¿Deseas calcular con datos nuevos? (s/n): {C_RESET}").strip().lower()
        if reiniciar != "s":
            print(f"\n{C_OK}  ¡Hasta luego! Programa terminado.{C_RESET}\n")
            break
        print("\n" + "─" * 44 + "\n")

if __name__ == "__main__":
    main()
