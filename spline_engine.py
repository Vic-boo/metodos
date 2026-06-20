"""
spline_engine.py
─────────────────────────────────────────────
Motor matemático de Splines Cúbicos (sin I/O de consola).
Contiene exactamente la misma lógica numérica que el programa
original de consola, separada para poder reutilizarla desde la
interfaz gráfica (GUI).
"""

import numpy as np


def calcular_splines(x, y, frontera="natural", fp0=0.0, fpn=0.0):
    """
    Calcula los coeficientes (a, b, c, d) de cada segmento del spline
    cúbico, resolviendo el sistema tridiagonal de momentos M_i = S''(x_i).
    """
    n = len(x) - 1
    h = np.diff(x)

    A = np.zeros((n + 1, n + 1))
    b = np.zeros(n + 1)

    for i in range(1, n):
        A[i, i - 1] = h[i - 1]
        A[i, i] = 2 * (h[i - 1] + h[i])
        A[i, i + 1] = h[i]
        b[i] = 6 * ((y[i + 1] - y[i]) / h[i] - (y[i] - y[i - 1]) / h[i - 1])

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
        A[n, n] = 2 * h[n - 1]
        b[n] = 6 * (fpn - (y[n] - y[n - 1]) / h[n - 1])

    M = np.linalg.solve(A, b)

    coefs = []
    for i in range(n):
        ai = y[i]
        bi = (y[i + 1] - y[i]) / h[i] - h[i] * (2 * M[i] + M[i + 1]) / 6
        ci = M[i] / 2
        di = (M[i + 1] - M[i]) / (6 * h[i])
        coefs.append((ai, bi, ci, di))

    return coefs, M


def evaluar(xval, x, coefs):
    """Evalúa S(xval) ubicando el segmento correcto."""
    n = len(coefs)
    for i in range(n - 1):
        if x[i] <= xval <= x[i + 1]:
            a, b, c, d = coefs[i]
            t = xval - x[i]
            return a + b * t + c * t ** 2 + d * t ** 3
    i = n - 1
    a, b, c, d = coefs[i]
    t = xval - x[i]
    return a + b * t + c * t ** 2 + d * t ** 3


def encontrar_optimos(x, coefs):
    """
    Encuentra máximos y mínimos locales del spline resolviendo
    S_i'(t) = b + 2c·t + 3d·t² = 0 dentro de cada segmento.
    Devuelve lista de tuplas (x_opt, y_opt, tipo).
    """
    n = len(coefs)
    optimos = []

    for i in range(n):
        a, b, c, d = coefs[i]
        t0, t1 = 0.0, x[i + 1] - x[i]

        A_cuad, B_cuad, C_cuad = 3 * d, 2 * c, b
        raices_t = []
        if abs(A_cuad) < 1e-12:
            if abs(B_cuad) > 1e-12:
                raices_t.append(-C_cuad / B_cuad)
        else:
            disc = B_cuad ** 2 - 4 * A_cuad * C_cuad
            if disc >= 0:
                sq = np.sqrt(disc)
                raices_t.append((-B_cuad + sq) / (2 * A_cuad))
                raices_t.append((-B_cuad - sq) / (2 * A_cuad))

        for t in raices_t:
            if t0 + 1e-9 < t < t1 - 1e-9:
                segunda_deriv = 2 * c + 6 * d * t
                if segunda_deriv > 1e-9:
                    tipo = "mínimo"
                elif segunda_deriv < -1e-9:
                    tipo = "máximo"
                else:
                    tipo = "inflexión (tangente horizontal)"
                x_opt = x[i] + t
                y_opt = a + b * t + c * t ** 2 + d * t ** 3
                optimos.append((x_opt, y_opt, tipo))

    optimos.sort(key=lambda p: p[0])
    return optimos


def formatear_polinomios(x, coefs):
    """Devuelve un string con los polinomios por tramo, listo para mostrar."""
    lineas = []
    lineas.append("Forma: S_i(x) = a + b(x - x_i) + c(x - x_i)² + d(x - x_i)³\n")
    for i, (a, b, c, d) in enumerate(coefs):
        lineas.append(f"Segmento {i + 1}: x ∈ [{x[i]:.4f}, {x[i + 1]:.4f}]")
        lineas.append(f"  S_{i + 1}(x) = {a:.6f}")
        signo_b = "+" if b >= 0 else "-"
        signo_c = "+" if c >= 0 else "-"
        signo_d = "+" if d >= 0 else "-"
        lineas.append(f"         {signo_b} {abs(b):.6f}·(x - {x[i]:.4f})")
        lineas.append(f"         {signo_c} {abs(c):.6f}·(x - {x[i]:.4f})²")
        lineas.append(f"         {signo_d} {abs(d):.6f}·(x - {x[i]:.4f})³")
        lineas.append("")
    return "\n".join(lineas)


def formatear_momentos(x, M):
    lineas = ["Segundas derivadas M[i] = S''(x_i):\n"]
    for i, mi in enumerate(M):
        lineas.append(f"  M[{i}] = S''({x[i]:.4f}) = {mi:.6f}")
    return "\n".join(lineas)


def interpretar_resultados(x, y, M, optimos, frontera, fp0, fpn):
    """
    Genera una interpretación en lenguaje natural de los resultados,
    a partir de los datos numéricos (sin asumir ningún caso de uso
    específico): tendencia general, comportamiento en los extremos,
    y lectura de cada óptimo encontrado.
    """
    parrafos = []

    # ── Tendencia global
    delta_total = y[-1] - y[0]
    if delta_total > 0:
        tendencia = "creciente"
    elif delta_total < 0:
        tendencia = "decreciente"
    else:
        tendencia = "neutra (mismo valor inicial y final)"
    parrafos.append(
        f"Entre x = {x[0]:.4f} y x = {x[-1]:.4f}, la variable interpolada presenta una "
        f"tendencia global <strong>{tendencia}</strong>: pasa de {y[0]:.4f} a {y[-1]:.4f} "
        f"(Δy = {delta_total:+.4f})."
    )

    # ── Condición de frontera
    if frontera == "natural":
        parrafos.append(
            "Se usó la condición de frontera <strong>natural</strong> "
            f"(S''({x[0]:.4f}) = S''({x[-1]:.4f}) = 0): no se impuso ninguna velocidad "
            "de cambio específica en los extremos, por lo que la curva es la de "
            "menor curvatura total posible (la más \"suave\") compatible con los puntos dados."
        )
    else:
        parrafos.append(
            "Se usó la condición de frontera <strong>sujeta</strong>, con pendiente inicial "
            f"S'({x[0]:.4f}) = {fp0:.4f} y pendiente final S'({x[-1]:.4f}) = {fpn:.4f}. "
            "Esto fuerza a la curva a iniciar y terminar con una razón de cambio exacta, "
            "en vez de dejarla libre como en el caso natural."
        )

    # ── Lectura de los óptimos
    if not optimos:
        parrafos.append(
            "<strong>No se detectaron máximos ni mínimos locales</strong> dentro del dominio: "
            "la curva interpolada es monótona (siempre creciente o siempre decreciente) "
            "entre los puntos dados. Esto indica que, según los datos disponibles, "
            "la variable no cambia de tendencia en ningún punto intermedio."
        )
    else:
        n_max = sum(1 for _, _, t in optimos if t == "máximo")
        n_min = sum(1 for _, _, t in optimos if t == "mínimo")
        resumen = []
        if n_max:
            resumen.append(f"{n_max} máximo(s) local(es)")
        if n_min:
            resumen.append(f"{n_min} mínimo(s) local(es)")
        parrafos.append(
            f"Se detectaron {' y '.join(resumen)} dentro del dominio. Esto significa que, "
            "aunque los puntos originales no lo muestren directamente, <strong>la curva cambia "
            "de tendencia entre ellos</strong> (sube y luego baja, o baja y luego sube)."
        )
        for x_opt, y_opt, tipo in optimos:
            if tipo == "máximo":
                parrafos.append(
                    f"&nbsp;&nbsp;•&nbsp; En <strong>x = {x_opt:.4f}</strong> la curva alcanza un <strong>máximo local</strong> de "
                    f"<strong>y = {y_opt:.4f}</strong>: antes de este punto la variable venía creciendo "
                    "y después comienza a decrecer. Es el valor más alto que toma la curva "
                    "en esa zona del dominio."
                )
            elif tipo == "mínimo":
                parrafos.append(
                    f"&nbsp;&nbsp;•&nbsp; En <strong>x = {x_opt:.4f}</strong> la curva alcanza un <strong>mínimo local</strong> de "
                    f"<strong>y = {y_opt:.4f}</strong>: antes de este punto la variable venía decreciendo "
                    "y después comienza a crecer. Es el valor más bajo que toma la curva "
                    "en esa zona del dominio."
                )
            else:
                parrafos.append(
                    f"&nbsp;&nbsp;•&nbsp; En <strong>x = {x_opt:.4f}</strong> hay un punto de inflexión con tangente "
                    f"horizontal (y = {y_opt:.4f}): la curva momentáneamente deja de "
                    "crecer o decrecer, pero retoma la misma dirección que traía."
                )

    # ── Curvatura en los nodos (concavidad)
    cambios_concavidad = 0
    for i in range(1, len(M)):
        if M[i - 1] * M[i] < 0:
            cambios_concavidad += 1
    if cambios_concavidad > 0:
        parrafos.append(
            f"La segunda derivada S''(x) cambia de signo {cambios_concavidad} vez(ces) "
            "a lo largo del dominio, lo que confirma que la curva alterna entre "
            "concavidad hacia arriba y hacia abajo (coherente con los óptimos detectados)."
        )

    return parrafos

