# TP Economía para Ingenieros — App completa en Streamlit

import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="Simulador Económico",
    layout="wide"
)

# =====================================================
# TITULO
# =====================================================

st.title("📈 Simulador de Mercado e Intervenciones del Estado")
st.markdown("### Economía para Ingenieros - UNSTA")
st.markdown(
    "#### 👩‍💻 Integrantes: Amparo Ruiz • Candelaria Lopez Avila • Luz Maria Ponce de Leon"
)

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("⚙️ Configuración")

modulo = st.sidebar.selectbox(
    "Seleccionar módulo",
    [
        "Mercado Competitivo",
        "Elasticidad",
        "Precio Máximo",
        "Precio Mínimo",
        "Impuestos",
        "Subsidios",
        "Cuotas"
    ]
)

tema = st.sidebar.selectbox(
    "Tema",
    ["Oscuro", "Claro"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Demanda")

a = st.sidebar.slider("a (Demanda)", 10, 200, 120)
b = st.sidebar.slider("b (Demanda)", 1, 20, 2)

st.sidebar.subheader("Oferta")

c = st.sidebar.slider("c (Oferta)", -50, 100, 20)
d = st.sidebar.slider("d (Oferta)", 1, 20, 2)

# =====================================================
# VALIDACION
# =====================================================

if b + d == 0:
    st.error("Las pendientes generan división por cero")
    st.stop()

# =====================================================
# FUNCIONES
# =====================================================


def demanda(P):
    return a - b * P



def oferta(P):
    return c + d * P

# =====================================================
# EQUILIBRIO
# =====================================================

P_eq = (a - c) / (b + d)
Q_eq = demanda(P_eq)

# =====================================================
# DATOS GRAFICOS
# =====================================================

P = np.linspace(0, 100, 500)
Qd = demanda(P)
Qo = oferta(P)

# =====================================================
# GRAFICO
# =====================================================

fig = go.Figure()

if tema == "Oscuro":
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font=dict(color="white")
    )

fig.add_trace(go.Scatter(
    x=Qd,
    y=P,
    mode='lines',
    name='Demanda',
    line=dict(color='red', width=4)
))

fig.add_trace(go.Scatter(
    x=Qo,
    y=P,
    mode='lines',
    name='Oferta',
    line=dict(color='green', width=4)
))

fig.add_trace(go.Scatter(
    x=[Q_eq],
    y=[P_eq],
    mode='markers+text',
    name='Equilibrio',
    text=['Equilibrio'],
    textposition='top center',
    marker=dict(size=18, color='yellow')
))

# =====================================================
# FORMULAS
# =====================================================

st.latex(r"Q_d = a - bP")
st.latex(r"Q_o = c + dP")

# =====================================================
# DASHBOARD
# =====================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Precio Equilibrio", round(P_eq, 2))

with col2:
    st.metric("Cantidad Equilibrio", round(Q_eq, 2))

with col3:
    st.metric("Pendiente Demanda", -b)

# =====================================================
# MERCADO COMPETITIVO
# =====================================================

if modulo == "Mercado Competitivo":

    st.subheader("📊 Mercado Competitivo")

    fig.update_layout(
        title="Oferta y Demanda",
        xaxis_title="Cantidad",
        yaxis_title="Precio",
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("📚 Explicación Económica")

    st.write(
        "El equilibrio de mercado ocurre cuando la cantidad demandada es igual a la cantidad ofrecida."
    )

# =====================================================
# ELASTICIDAD
# =====================================================

elif modulo == "Elasticidad":

    st.subheader("📉 Elasticidad de la Demanda")

    col1, col2 = st.columns(2)

    with col1:
        P1 = st.number_input("Precio 1", value=10.0)
        P2 = st.number_input("Precio 2", value=20.0)

    with col2:
        Q1 = demanda(P1)
        Q2 = demanda(P2)

        st.write(f"Cantidad 1: {round(Q1,2)}")
        st.write(f"Cantidad 2: {round(Q2,2)}")

    variacion_q = (Q2 - Q1) / ((Q1 + Q2) / 2)
    variacion_p = (P2 - P1) / ((P1 + P2) / 2)

    elasticidad = variacion_q / variacion_p

    st.metric("Elasticidad", round(elasticidad, 2))

    valor = abs(elasticidad)

    if valor > 1:
        clasificacion = "Demanda Elástica"
        ingreso = "El ingreso total aumenta cuando baja el precio"

    elif valor < 1:
        clasificacion = "Demanda Inelástica"
        ingreso = "El ingreso total disminuye cuando baja el precio"

    else:
        clasificacion = "Elasticidad Unitaria"
        ingreso = "El ingreso total permanece constante"

    st.success(clasificacion)
    st.info(ingreso)

    fig.add_trace(go.Scatter(
        x=[Q1, Q2],
        y=[P1, P2],
        mode='markers',
        name='Puntos Elasticidad',
        marker=dict(size=12, color='cyan')
    ))

    fig.update_layout(
        title="Elasticidad de la Demanda",
        xaxis_title="Cantidad",
        yaxis_title="Precio",
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# PRECIO MAXIMO
# =====================================================

elif modulo == "Precio Máximo":

    st.subheader("🚫 Precio Máximo")

    precio_max = st.slider(
        "Precio Máximo",
        1,
        int(max(P)),
        int(P_eq - 10) if P_eq > 10 else 5
    )

    Qd_max = demanda(precio_max)
    Qo_max = oferta(precio_max)

    escasez = Qd_max - Qo_max

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Cantidad Demandada", round(Qd_max, 2))

    with col2:
        st.metric("Cantidad Ofrecida", round(Qo_max, 2))

    with col3:
        st.metric("Escasez", round(escasez, 2))

    fig.add_hline(y=precio_max)

    fig.update_layout(
        title="Precio Máximo",
        xaxis_title="Cantidad",
        yaxis_title="Precio",
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)

    st.warning("El precio máximo genera escasez porque la demanda supera a la oferta.")

# =====================================================
# PRECIO MINIMO
# =====================================================

elif modulo == "Precio Mínimo":

    st.subheader("📈 Precio Mínimo")

    precio_min = st.slider(
        "Precio Mínimo",
        1,
        int(max(P)),
        int(P_eq + 10)
    )

    Qd_min = demanda(precio_min)
    Qo_min = oferta(precio_min)

    excedente = Qo_min - Qd_min

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Cantidad Demandada", round(Qd_min, 2))

    with col2:
        st.metric("Cantidad Ofrecida", round(Qo_min, 2))

    with col3:
        st.metric("Excedente", round(excedente, 2))

    fig.add_hline(y=precio_min)

    fig.update_layout(
        title="Precio Mínimo",
        xaxis_title="Cantidad",
        yaxis_title="Precio",
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)

    st.warning("El precio mínimo genera excedente porque la oferta supera a la demanda.")

# =====================================================
# IMPUESTOS
# =====================================================

elif modulo == "Impuestos":

    st.subheader("💰 Impuestos")

    impuesto = st.slider("Impuesto", 1, 50, 10)

    def oferta_impuesto(P):
        return c + d * (P - impuesto)

    Qo_imp = oferta_impuesto(P)

    P_nuevo = (a - c + d * impuesto) / (b + d)
    Q_nuevo = demanda(P_nuevo)

    recaudacion = impuesto * Q_nuevo

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Nuevo Precio", round(P_nuevo, 2))

    with col2:
        st.metric("Nueva Cantidad", round(Q_nuevo, 2))

    with col3:
        st.metric("Recaudación", round(recaudacion, 2))

    fig.add_trace(go.Scatter(
        x=Qo_imp,
        y=P,
        mode='lines',
        name='Oferta con Impuesto',
        line=dict(color='orange', width=4)
    ))

    fig.add_trace(go.Scatter(
        x=[Q_nuevo],
        y=[P_nuevo],
        mode='markers+text',
        text=['Nuevo Equilibrio'],
        textposition='bottom center',
        marker=dict(size=18, color='orange')
    ))

    fig.update_layout(
        title="Impacto del Impuesto",
        xaxis_title="Cantidad",
        yaxis_title="Precio",
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📊 Comparación")

    st.table({
        "Situación": ["Inicial", "Nueva"],
        "Precio": [round(P_eq, 2), round(P_nuevo, 2)],
        "Cantidad": [round(Q_eq, 2), round(Q_nuevo, 2)]
    })

    st.warning(
        "El impuesto desplaza la oferta hacia la izquierda y reduce la cantidad de equilibrio."
    )

# =====================================================
# SUBSIDIOS
# =====================================================

elif modulo == "Subsidios":

    st.subheader("🏛️ Subsidios")

    subsidio = st.slider("Subsidio", 1, 50, 10)

    def oferta_subsidio(P):
        return c + d * (P + subsidio)

    Qo_sub = oferta_subsidio(P)

    P_nuevo = (a - c - d * subsidio) / (b + d)
    Q_nuevo = demanda(P_nuevo)

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Nuevo Precio", round(P_nuevo, 2))

    with col2:
        st.metric("Nueva Cantidad", round(Q_nuevo, 2))

    fig.add_trace(go.Scatter(
        x=Qo_sub,
        y=P,
        mode='lines',
        name='Oferta con Subsidio',
        line=dict(color='blue', width=4)
    ))

    fig.update_layout(
        title="Impacto del Subsidio",
        xaxis_title="Cantidad",
        yaxis_title="Precio",
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📊 Comparación")

    st.table({
        "Situación": ["Inicial", "Nueva"],
        "Precio": [round(P_eq, 2), round(P_nuevo, 2)],
        "Cantidad": [round(Q_eq, 2), round(Q_nuevo, 2)]
    })

    st.success(
        "El subsidio desplaza la oferta hacia la derecha y aumenta la cantidad de equilibrio."
    )

# =====================================================
# CUOTAS
# =====================================================

elif modulo == "Cuotas":

    st.subheader("📦 Cuotas")

    cuota = st.slider("Límite de Cantidad", 1, int(max(Qd)), 40)

    precio_cuota = (a - cuota) / b

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Cantidad Máxima", cuota)

    with col2:
        st.metric("Precio Resultante", round(precio_cuota, 2))

    fig.add_vline(x=cuota)

    fig.add_trace(go.Scatter(
        x=[cuota],
        y=[precio_cuota],
        mode='markers+text',
        text=['Cuota'],
        textposition='top center',
        marker=dict(size=18, color='purple')
    ))

    fig.update_layout(
        title="Sistema de Cuotas",
        xaxis_title="Cantidad",
        yaxis_title="Precio",
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)

    st.warning("La cuota restringe la cantidad ofrecida y eleva el precio.")

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.caption(
    "TP Economía para Ingenieros • UNSTA • Simulador desarrollado por Amparo Ruiz, Candelaria Lopez Avila y Luz Maria Ponce de Leon"
)
fig = go.Figure()

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font=dict(color="white")
)
fig.add_trace(go.Scatter(
    x=Qd,
    y=P,
    mode='lines',
    name='Demanda',
    line=dict(color='red', width=4)
))

fig.add_trace(go.Scatter(
    x=Qo,
    y=P,
    mode='lines',
    name='Oferta',
    line=dict(color='green', width=4)
))
st.markdown("---")

st.subheader("📚 Explicación Económica")

if P_eq > 0:
    st.write(
        "El equilibrio de mercado ocurre cuando la cantidad demandada es igual a la cantidad ofrecida."
    )

if modulo == "Impuestos":
    st.write(
        "El impuesto incrementa el costo de producción, desplaza la oferta hacia la izquierda y genera una caída en la cantidad de equilibrio."
    )

if modulo == "Precio Máximo":
    st.write(
        "El precio máximo genera escasez porque la demanda supera a la oferta."
    )

if modulo == "Precio Mínimo":
    st.write(
        "El precio mínimo genera excedente porque la oferta supera a la demanda."
    )
st.subheader("📊 Comparación")

st.table({
    "Situación": ["Inicial", "Nueva"],
    "Precio": [round(P_eq,2), round(P_nuevo,2)],
    "Cantidad": [round(Q_eq,2), round(Q_nuevo,2)]
})

if b + d == 0:
    st.error("Las pendientes generan división por cero")
    st.stop()
st.markdown("---")
st.caption(
    "TP Economía para Ingenieros • UNSTA • Simulador desarrollado por Amparo Ruiz, Candelaria Lopez Avila y Luz Maria Ponce de Leon"
)

marker=dict(size=18, color='yellow')
st.latex(r"Q_d = a - bP")
st.latex(r"Q_o = c + dP")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Precio Equilibrio", round(P_eq,2))

with col2:
    st.metric("Cantidad Equilibrio", round(Q_eq,2))

with col3:
    st.metric("Pendiente Demanda", -b)

tema = st.sidebar.selectbox(
    "Tema",
    ["Oscuro", "Claro"]
)