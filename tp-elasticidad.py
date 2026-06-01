import numpy as np
import plotly.graph_objects as go
import streamlit as st


# =====================================================
# CONFIGURACION GENERAL
# =====================================================

st.set_page_config(
    page_title="Simulador Economico Pro",
    page_icon="📈",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.4rem; }
    div[data-testid="stMetric"] {
        background: rgba(127, 127, 127, 0.08);
        border: 1px solid rgba(127, 127, 127, 0.18);
        border-radius: 10px;
        padding: 14px 16px;
    }
    .small-note {
        color: #8b949e;
        font-size: 0.92rem;
        line-height: 1.45;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Simulador de Mercado e Intervenciones del Estado")
st.caption("Economia para Ingenieros - UNSTA | Version mejorada comparada con la app HTML de referencia")


# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:
    st.header("Configuracion")

    modulo = st.selectbox(
        "Seleccionar modulo",
        [
            "Dashboard",
            "Mercado Competitivo",
            "Elasticidad",
            "Precio Maximo",
            "Precio Minimo",
            "Impuestos",
            "Subsidios",
            "Cuotas",
            "Comparacion de Mercados",
            "Sensibilidad",
            "Simulacion Temporal",
        ],
    )

    tema = st.radio("Tema visual", ["Oscuro", "Claro"], horizontal=True)

    st.divider()
    st.subheader("Demanda")
    a = st.number_input("a - intercepto Qd", min_value=1.0, value=120.0, step=5.0)
    b = st.number_input("b - pendiente Qd", min_value=0.1, value=2.0, step=0.1)

    st.subheader("Oferta")
    c = st.number_input("c - intercepto Qo", value=20.0, step=5.0)
    d = st.number_input("d - pendiente Qo", min_value=0.1, value=2.0, step=0.1)


# =====================================================
# FUNCIONES ECONOMICAS
# =====================================================

def demanda(precio, a_val=a, b_val=b):
    return a_val - b_val * precio


def oferta(precio, c_val=c, d_val=d):
    return c_val + d_val * precio


def equilibrio(a_val, b_val, c_val, d_val):
    if b_val + d_val == 0:
        return np.nan, np.nan
    p_eq = (a_val - c_val) / (b_val + d_val)
    q_eq = a_val - b_val * p_eq
    return p_eq, q_eq


def elasticidad_punto_medio(p1, p2, q1, q2):
    if (q1 + q2) == 0 or (p1 + p2) == 0:
        return np.nan
    var_q = (q2 - q1) / ((q1 + q2) / 2)
    var_p = (p2 - p1) / ((p1 + p2) / 2)
    if var_p == 0:
        return np.nan
    return var_q / var_p


def elasticidad_en_equilibrio(a_val, b_val, c_val, d_val):
    p_eq, _ = equilibrio(a_val, b_val, c_val, d_val)
    p1 = p_eq * 0.99
    p2 = p_eq * 1.01
    q1 = a_val - b_val * p1
    q2 = a_val - b_val * p2
    return abs(elasticidad_punto_medio(p1, p2, q1, q2))


def fmt_money(valor):
    if np.isnan(valor):
        return "-"
    return f"${valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_units(valor):
    if np.isnan(valor):
        return "-"
    return f"{valor:,.2f} u".replace(",", "X").replace(".", ",").replace("X", ".")


def classify_elasticity(valor):
    if np.isnan(valor):
        return "No calculable"
    if abs(valor) > 1:
        return "Demanda elastica"
    if abs(valor) < 1:
        return "Demanda inelastica"
    return "Elasticidad unitaria"


def base_chart(a_val, b_val, c_val, d_val, title, extra_traces=None):
    p_eq, q_eq = equilibrio(a_val, b_val, c_val, d_val)
    max_price = max(20, p_eq * 2.5 if p_eq > 0 else 100)
    precios = np.linspace(0, max_price, 400)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=demanda(precios, a_val, b_val),
            y=precios,
            mode="lines",
            name="Demanda",
            line=dict(color="#f85149", width=4),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=oferta(precios, c_val, d_val),
            y=precios,
            mode="lines",
            name="Oferta",
            line=dict(color="#3fb950", width=4),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[q_eq],
            y=[p_eq],
            mode="markers+text",
            name="Equilibrio",
            text=["P* / Q*"],
            textposition="top center",
            marker=dict(size=16, color="#e3b341", line=dict(color="white", width=1)),
        )
    )

    if extra_traces:
        for trace in extra_traces:
            fig.add_trace(trace)

    dark = tema == "Oscuro"
    fig.update_layout(
        title=dict(text=title, x=0.5),
        template="plotly_dark" if dark else "plotly_white",
        paper_bgcolor="#0E1117" if dark else "white",
        plot_bgcolor="#0E1117" if dark else "white",
        xaxis_title="Cantidad",
        yaxis_title="Precio",
        hovermode="closest",
        height=620,
        margin=dict(l=40, r=30, t=70, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(rangemode="tozero")
    fig.update_yaxes(rangemode="tozero")
    return fig


def show_market_metrics(a_val, b_val, c_val, d_val):
    p_eq, q_eq = equilibrio(a_val, b_val, c_val, d_val)
    ed = elasticidad_en_equilibrio(a_val, b_val, c_val, d_val)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Precio equilibrio", fmt_money(p_eq))
    col2.metric("Cantidad equilibrio", fmt_units(q_eq))
    col3.metric("Ingreso total", fmt_money(p_eq * q_eq))
    col4.metric("Elasticidad base", f"{ed:.3f}", classify_elasticity(ed))


def intervention_summary():
    p_eq, q_eq = equilibrio(a, b, c, d)
    impuesto = 10
    subsidio = 10
    pmax = max(1, p_eq * 0.75)
    pmin = p_eq * 1.25

    c_tax = c - impuesto * d
    p_comp = (a - c_tax) / (b + d)
    q_tax = c_tax + d * p_comp

    c_sub = c + subsidio * d
    p_sub = (a - c_sub) / (b + d)
    q_sub = c_sub + d * p_sub

    qd_max = demanda(pmax)
    qo_max = oferta(pmax)
    qd_min = demanda(pmin)
    qo_min = oferta(pmin)

    return [
        {"Escenario": "Libre", "Precio": p_eq, "Cantidad efectiva": q_eq, "Resultado": "Equilibrio"},
        {"Escenario": "Impuesto", "Precio": p_comp, "Cantidad efectiva": q_tax, "Resultado": "Menor cantidad"},
        {"Escenario": "Subsidio", "Precio": p_sub, "Cantidad efectiva": q_sub, "Resultado": "Mayor cantidad"},
        {"Escenario": "Precio maximo", "Precio": pmax, "Cantidad efectiva": min(qd_max, qo_max), "Resultado": f"Escasez {qd_max - qo_max:.2f}"},
        {"Escenario": "Precio minimo", "Precio": pmin, "Cantidad efectiva": min(qd_min, qo_min), "Resultado": f"Excedente {qo_min - qd_min:.2f}"},
    ]


p_eq, q_eq = equilibrio(a, b, c, d)

if np.isnan(p_eq) or np.isnan(q_eq):
    st.error("Los parametros no permiten calcular el equilibrio.")
    st.stop()

if p_eq < 0 or q_eq < 0:
    st.warning("Con estos parametros el equilibrio queda fuera del primer cuadrante. Revisa interceptos y pendientes.")


# =====================================================
# MODULOS
# =====================================================

if modulo == "Dashboard":
    st.subheader("Dashboard general")
    st.markdown('<p class="small-note">Resumen del mercado y comparacion rapida de intervenciones.</p>', unsafe_allow_html=True)

    show_market_metrics(a, b, c, d)

    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.plotly_chart(base_chart(a, b, c, d, "Mercado en equilibrio"), use_container_width=True)

    with col2:
        escenarios = intervention_summary()
        escenarios_formateados = [
            {
                "Escenario": row["Escenario"],
                "Precio": fmt_money(row["Precio"]),
                "Cantidad efectiva": fmt_units(row["Cantidad efectiva"]),
                "Resultado": row["Resultado"],
            }
            for row in escenarios
        ]
        st.dataframe(escenarios_formateados, use_container_width=True, hide_index=True)

        bar = go.Figure()
        bar.add_bar(x=[row["Escenario"] for row in escenarios], y=[row["Precio"] for row in escenarios], name="Precio", marker_color="#58a6ff")
        bar.add_bar(x=[row["Escenario"] for row in escenarios], y=[row["Cantidad efectiva"] for row in escenarios], name="Cantidad", marker_color="#3fb950")
        bar.update_layout(
            title="Comparacion de intervenciones",
            template="plotly_dark" if tema == "Oscuro" else "plotly_white",
            barmode="group",
            height=340,
        )
        st.plotly_chart(bar, use_container_width=True)


elif modulo == "Mercado Competitivo":
    st.subheader("Mercado competitivo")
    show_market_metrics(a, b, c, d)

    st.latex(r"Q_d = a - bP")
    st.latex(r"Q_o = c + dP")
    st.plotly_chart(base_chart(a, b, c, d, "Oferta, demanda y equilibrio"), use_container_width=True)

    st.info(
        f"El equilibrio ocurre cuando Qd = Qo. Con estos datos: P* = {p_eq:.2f} y Q* = {q_eq:.2f}."
    )


elif modulo == "Elasticidad":
    st.subheader("Elasticidad de la demanda")

    col1, col2 = st.columns(2)
    with col1:
        p1 = st.number_input("Precio 1", value=max(0.0, p_eq * 0.75), step=1.0)
        p2 = st.number_input("Precio 2", value=max(1.0, p_eq * 1.25), step=1.0)
    with col2:
        q1 = demanda(p1)
        q2 = demanda(p2)
        st.metric("Cantidad 1", fmt_units(q1))
        st.metric("Cantidad 2", fmt_units(q2))

    ed = elasticidad_punto_medio(p1, p2, q1, q2)
    show_market_metrics(a, b, c, d)
    st.metric("Elasticidad punto medio", f"{ed:.3f}", classify_elasticity(ed))

    extra = [
        go.Scatter(
            x=[q1, q2],
            y=[p1, p2],
            mode="markers+lines+text",
            name="Puntos de elasticidad",
            text=["P1", "P2"],
            textposition="top center",
            marker=dict(size=13, color="#39d353"),
            line=dict(color="#39d353", dash="dot"),
        )
    ]
    st.plotly_chart(base_chart(a, b, c, d, "Elasticidad por punto medio", extra), use_container_width=True)

    if abs(ed) > 1:
        st.success("La demanda es elastica: una baja de precio tiende a aumentar el ingreso total.")
    elif abs(ed) < 1:
        st.warning("La demanda es inelastica: una baja de precio tiende a reducir el ingreso total.")
    else:
        st.info("La demanda es unitaria: el ingreso total se mantiene aproximadamente constante.")


elif modulo == "Precio Maximo":
    st.subheader("Precio maximo")
    precio_max = st.slider("Precio maximo", 0.0, float(max(1, p_eq * 2)), float(max(1, p_eq * 0.75)), step=0.5)

    qd_max = demanda(precio_max)
    qo_max = oferta(precio_max)
    escasez = qd_max - qo_max

    col1, col2, col3 = st.columns(3)
    col1.metric("Cantidad demandada", fmt_units(qd_max))
    col2.metric("Cantidad ofrecida", fmt_units(qo_max))
    col3.metric("Escasez", fmt_units(max(0, escasez)))

    extra = [
        go.Scatter(
            x=[0, max(qd_max, qo_max, q_eq) * 1.1],
            y=[precio_max, precio_max],
            mode="lines",
            name="Precio maximo",
            line=dict(color="#e3b341", dash="dash", width=3),
        )
    ]
    st.plotly_chart(base_chart(a, b, c, d, "Efecto de un precio maximo", extra), use_container_width=True)

    if precio_max < p_eq:
        st.warning("El precio maximo es efectivo porque queda por debajo del precio de equilibrio y genera escasez.")
    else:
        st.info("El precio maximo no es vinculante porque queda por encima del precio de equilibrio.")


elif modulo == "Precio Minimo":
    st.subheader("Precio minimo")
    precio_min = st.slider("Precio minimo", 0.0, float(max(1, p_eq * 2.5)), float(p_eq * 1.25), step=0.5)

    qd_min = demanda(precio_min)
    qo_min = oferta(precio_min)
    excedente = qo_min - qd_min

    col1, col2, col3 = st.columns(3)
    col1.metric("Cantidad demandada", fmt_units(qd_min))
    col2.metric("Cantidad ofrecida", fmt_units(qo_min))
    col3.metric("Excedente", fmt_units(max(0, excedente)))

    extra = [
        go.Scatter(
            x=[0, max(qd_min, qo_min, q_eq) * 1.1],
            y=[precio_min, precio_min],
            mode="lines",
            name="Precio minimo",
            line=dict(color="#bc8cff", dash="dash", width=3),
        )
    ]
    st.plotly_chart(base_chart(a, b, c, d, "Efecto de un precio minimo", extra), use_container_width=True)

    if precio_min > p_eq:
        st.warning("El precio minimo es efectivo porque queda por encima del equilibrio y genera excedente.")
    else:
        st.info("El precio minimo no es vinculante porque queda por debajo del precio de equilibrio.")


elif modulo == "Impuestos":
    st.subheader("Impuestos")
    impuesto = st.slider("Impuesto por unidad", 0.0, 50.0, 10.0, step=0.5)
    aplicado_a = st.radio("Aplicado legalmente a", ["Vendedores", "Compradores"], horizontal=True)

    if aplicado_a == "Vendedores":
        c_new = c - impuesto * d
        a_new = a
    else:
        c_new = c
        a_new = a - impuesto * b

    p_vend = (a_new - c_new) / (b + d)
    p_comp = p_vend + impuesto
    q_new = c_new + d * p_vend
    recaudacion = impuesto * q_new
    carga_comp = (p_comp - p_eq) * q_new
    carga_vend = (p_eq - p_vend) * q_new

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Precio comprador", fmt_money(p_comp))
    col2.metric("Precio vendedor", fmt_money(p_vend))
    col3.metric("Nueva cantidad", fmt_units(q_new))
    col4.metric("Recaudacion", fmt_money(recaudacion))

    col5, col6 = st.columns(2)
    pct_comp = carga_comp / recaudacion * 100 if recaudacion else 0
    pct_vend = carga_vend / recaudacion * 100 if recaudacion else 0
    col5.metric("Carga compradores", fmt_money(carga_comp), f"{pct_comp:.1f}%")
    col6.metric("Carga vendedores", fmt_money(carga_vend), f"{pct_vend:.1f}%")

    precios = np.linspace(0, max(20, p_eq * 2.5), 400)
    extra = [
        go.Scatter(
            x=oferta(precios, c_new, d),
            y=precios,
            mode="lines",
            name="Oferta con impuesto",
            line=dict(color="#e3b341", width=4, dash="dash"),
        ),
        go.Scatter(
            x=[q_new, q_new],
            y=[p_vend, p_comp],
            mode="lines+markers",
            name="Brecha del impuesto",
            line=dict(color="#f85149", width=4),
            marker=dict(size=10),
        ),
    ]
    st.plotly_chart(base_chart(a, b, c, d, "Incidencia de un impuesto", extra), use_container_width=True)


elif modulo == "Subsidios":
    st.subheader("Subsidios")
    subsidio = st.slider("Subsidio por unidad", 0.0, 50.0, 10.0, step=0.5)

    c_new = c + subsidio * d
    p_comp = (a - c_new) / (b + d)
    q_new = c_new + d * p_comp
    p_vend = p_comp + subsidio
    costo = subsidio * q_new
    ganancia_comp = (p_eq - p_comp) * q_new
    ganancia_vend = (p_vend - p_eq) * q_new

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Precio comprador", fmt_money(p_comp))
    col2.metric("Precio vendedor", fmt_money(p_vend))
    col3.metric("Nueva cantidad", fmt_units(q_new))
    col4.metric("Costo fiscal", fmt_money(costo))

    col5, col6 = st.columns(2)
    col5.metric("Beneficio compradores", fmt_money(ganancia_comp))
    col6.metric("Beneficio vendedores", fmt_money(ganancia_vend))

    precios = np.linspace(0, max(20, p_vend * 2), 400)
    extra = [
        go.Scatter(
            x=oferta(precios, c_new, d),
            y=precios,
            mode="lines",
            name="Oferta con subsidio",
            line=dict(color="#58a6ff", width=4, dash="dash"),
        ),
        go.Scatter(
            x=[q_new, q_new],
            y=[p_comp, p_vend],
            mode="lines+markers",
            name="Brecha del subsidio",
            line=dict(color="#3fb950", width=4),
            marker=dict(size=10),
        ),
    ]
    st.plotly_chart(base_chart(a, b, c, d, "Efecto de un subsidio", extra), use_container_width=True)


elif modulo == "Cuotas":
    st.subheader("Cuotas")
    max_q = max(1.0, float(max(a, q_eq * 1.5)))
    cuota = st.slider("Limite de cantidad", 1.0, max_q, float(max(1, q_eq * 0.75)), step=1.0)

    precio_demanda = (a - cuota) / b
    precio_oferta = (cuota - c) / d
    renta_unitaria = precio_demanda - precio_oferta
    renta_total = renta_unitaria * cuota

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cuota", fmt_units(cuota))
    col2.metric("Precio demanda", fmt_money(precio_demanda))
    col3.metric("Precio oferta", fmt_money(precio_oferta))
    col4.metric("Renta total", fmt_money(renta_total))

    extra = [
        go.Scatter(
            x=[cuota, cuota],
            y=[0, max(precio_demanda, precio_oferta, p_eq) * 1.25],
            mode="lines",
            name="Cuota",
            line=dict(color="#bc8cff", dash="dash", width=4),
        )
    ]
    st.plotly_chart(base_chart(a, b, c, d, "Efecto de una cuota", extra), use_container_width=True)

    if cuota < q_eq:
        st.warning("La cuota es restrictiva: limita la cantidad por debajo del equilibrio y crea renta por unidad.")
    else:
        st.info("La cuota no restringe el mercado porque esta por encima de Q*.")


elif modulo == "Comparacion de Mercados":
    st.subheader("Comparacion de mercados")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Mercado A")
        a1 = st.number_input("a A", value=float(a), step=5.0)
        b1 = st.number_input("b A", min_value=0.1, value=float(b), step=0.1)
        c1 = st.number_input("c A", value=float(c), step=5.0)
        d1 = st.number_input("d A", min_value=0.1, value=float(d), step=0.1)
    with col_b:
        st.markdown("#### Mercado B")
        a2 = st.number_input("a B", value=float(a * 1.2), step=5.0)
        b2 = st.number_input("b B", min_value=0.1, value=float(b * 0.75), step=0.1)
        c2 = st.number_input("c B", value=float(c), step=5.0)
        d2 = st.number_input("d B", min_value=0.1, value=float(d * 1.25), step=0.1)

    p_a, q_a = equilibrio(a1, b1, c1, d1)
    p_b, q_b = equilibrio(a2, b2, c2, d2)
    ed_a = elasticidad_en_equilibrio(a1, b1, c1, d1)
    ed_b = elasticidad_en_equilibrio(a2, b2, c2, d2)

    tabla = [
        {"Mercado": "A", "P*": round(p_a, 3), "Q*": round(q_a, 3), "Ingreso total": round(p_a * q_a, 3), "Elasticidad": round(ed_a, 3)},
        {"Mercado": "B", "P*": round(p_b, 3), "Q*": round(q_b, 3), "Ingreso total": round(p_b * q_b, 3), "Elasticidad": round(ed_b, 3)},
    ]
    st.dataframe(tabla, use_container_width=True, hide_index=True)

    g1, g2 = st.columns(2)
    g1.plotly_chart(base_chart(a1, b1, c1, d1, "Mercado A"), use_container_width=True)
    g2.plotly_chart(base_chart(a2, b2, c2, d2, "Mercado B"), use_container_width=True)

    mas_elastico = "A" if ed_a > ed_b else "B"
    mayor_ingreso = "A" if p_a * q_a > p_b * q_b else "B"
    st.info(
        f"El mercado {mas_elastico} tiene demanda mas elastica. "
        f"El mercado {mayor_ingreso} tiene mayor ingreso total de equilibrio."
    )


elif modulo == "Sensibilidad":
    st.subheader("Sensibilidad de la incidencia impositiva")
    impuesto = st.slider("Impuesto usado para la tabla", 0.0, 50.0, 10.0, step=0.5)
    multiplicadores = [0.5, 0.75, 1, 1.25, 1.5, 2]

    filas = []
    for mult in multiplicadores:
        b_temp = b * mult
        p0, q0 = equilibrio(a, b_temp, c, d)
        c_tax = c - impuesto * d
        p_comp = (a - c_tax) / (b_temp + d)
        p_vend = p_comp - impuesto
        q_new = c_tax + d * p_comp
        recaudacion = impuesto * q_new
        carga_comp = (p_comp - p0) * q_new
        pct_comp = carga_comp / recaudacion * 100 if recaudacion else 0
        filas.append(
            {
                "b demanda": round(b_temp, 2),
                "P*": round(p0, 2),
                "Q*": round(q0, 2),
                "P comprador": round(p_comp, 2),
                "P vendedor": round(p_vend, 2),
                "Q nueva": round(q_new, 2),
                "Recaudacion": round(recaudacion, 2),
                "% compradores": round(pct_comp, 1),
                "% vendedores": round(100 - pct_comp, 1),
            }
        )

    st.dataframe(filas, use_container_width=True, hide_index=True)
    st.caption("Al cambiar b cambia la elasticidad de la demanda y, con eso, la distribucion de la carga del impuesto.")


elif modulo == "Simulacion Temporal":
    st.subheader("Simulacion temporal")

    col1, col2, col3 = st.columns(3)
    with col1:
        periodos = st.slider("Periodos", 2, 12, 6)
    with col2:
        delta_a = st.number_input("Cambio de a por periodo", value=5.0, step=1.0)
    with col3:
        delta_c = st.number_input("Cambio de c por periodo", value=0.0, step=1.0)

    datos = []
    a_t = a
    c_t = c
    for t in range(periodos):
        p_t, q_t = equilibrio(a_t, b, c_t, d)
        datos.append({"Periodo": t, "a": a_t, "c": c_t, "P*": p_t, "Q*": q_t, "Ingreso total": p_t * q_t})
        a_t += delta_a
        c_t += delta_c

    datos_redondeados = [
        {
            "Periodo": row["Periodo"],
            "a": round(row["a"], 2),
            "c": round(row["c"], 2),
            "P*": round(row["P*"], 2),
            "Q*": round(row["Q*"], 2),
            "Ingreso total": round(row["Ingreso total"], 2),
        }
        for row in datos
    ]
    st.dataframe(datos_redondeados, use_container_width=True, hide_index=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[row["Periodo"] for row in datos], y=[row["P*"] for row in datos], mode="lines+markers", name="Precio P*", line=dict(color="#58a6ff", width=4)))
    fig.add_trace(go.Scatter(x=[row["Periodo"] for row in datos], y=[row["Q*"] for row in datos], mode="lines+markers", name="Cantidad Q*", yaxis="y2", line=dict(color="#3fb950", width=4)))
    fig.update_layout(
        title="Evolucion del equilibrio",
        template="plotly_dark" if tema == "Oscuro" else "plotly_white",
        height=520,
        xaxis=dict(title="Periodo"),
        yaxis=dict(title="Precio"),
        yaxis2=dict(title="Cantidad", overlaying="y", side="right"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)


st.divider()
st.caption("TP Economia para Ingenieros - UNSTA | Version Streamlit mejorada con dashboard, sensibilidad y comparaciones.")
