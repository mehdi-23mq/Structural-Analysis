import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from solver import PortalFrameSolver
from plotting import create_full_figure, create_comparison_figure

st.set_page_config(
    page_title="Schnittgrößen Einfeldrahmen Simulation",
    page_icon="📐",
    layout="wide"
)

# Custom CSS styling
st.markdown("""
<style>
    .main-title {
        font-size: 26px;
        font-weight: bold;
        color: #003399;
        margin-bottom: 5px;
    }
    .sub-title {
        font-size: 15px;
        color: #555555;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #F8F9FA;
        border-left: 4px solid #003399;
        padding: 12px;
        border-radius: 4px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📐 Einfeldrahmen Schnittgrößen-Simulation</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Interaktive Berechnung der Schnittgrößen (M, V, N) & Auflagerkräfte mit visueller Diagrammdarstellung und nummerischen Werten</div>', unsafe_allow_html=True)

# Sidebar
st.sidebar.header("⚙️ System-Parameter")

system_type = st.sidebar.selectbox(
    "Tragsystem",
    ["Zweigelenkrahmen", "Dreigelenkrahmen", "Eingespannter Rahmen"],
    index=0
)

st.sidebar.subheader("📐 Geometrie")
col_g1, col_g2 = st.sidebar.columns(2)
l = col_g1.number_input("Spannweite l [m]", min_value=1.0, max_value=20.0, value=5.0, step=0.5)
h = col_g2.number_input("Höhe h [m]", min_value=1.0, max_value=15.0, value=3.0, step=0.5)

st.sidebar.subheader("⬇️ Belastung")
q = st.sidebar.number_input("Vertikallast q_k [kN/m]", min_value=0.0, max_value=100.0, value=8.4, step=0.1)
H = st.sidebar.number_input("Horizontallast H_{w,k} [kN]", min_value=0.0, max_value=100.0, value=5.0, step=0.1)

st.sidebar.subheader("🏗️ Steifigkeiten")
col_s1, col_s2 = st.sidebar.columns(2)
EI_R = col_s1.number_input("EI (Riegel)", min_value=0.1, max_value=100.0, value=1.0, step=0.1)
EI_S = col_s2.number_input("EI (Stiele)", min_value=0.1, max_value=100.0, value=1.0, step=0.1)

st.sidebar.subheader("🎨 Diagrammanpassung")
show_values = st.sidebar.checkbox("Werte in Schnittgrößen anzeigen", value=True)
scale_fac = st.sidebar.slider("Diagrammskalierung", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

# Initialize Solver
solver = PortalFrameSolver(l=l, h=h, q=q, H=H, EI_R=EI_R, EI_S=EI_S, system_type=system_type)
data_comb = solver.solve_case()

# Metrics header
c1, c2, c3, c4 = st.columns(4)
res_kv = data_comb['key_values']
res_react = data_comb['reactions']

c1.metric("Auflager A (Ah / Av)", f"{res_react['Ah']:.2f} / {res_react['Av']:.2f} kN")
c2.metric("Auflager B (Bh / Bv)", f"{res_react['Bh']:.2f} / {res_react['Bv']:.2f} kN")
c3.metric("Eckmomente M1 / M2", f"{res_kv['M1']:.2f} / {res_kv['M2']:.2f} kNm")
c4.metric("Max. Feldmoment M_max", f"{res_kv['M_max_beam']:.2f} kNm", delta=f"bei x = {res_kv['x_max']:.2f} m")

# Main Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🖼️ Momentenverlauf (wie Bild)",
    "📊 Schnittgrößen-Übersicht (M, V, N)",
    "🔢 Ergebnistabelle",
    "📥 Export"
])

with tab1:
    st.subheader("Vergleich der Lastfälle mit nummerischen Werten & Auflagerkräften")
    st.write("Exakte Nachbildung der Anordnung aus Ihrer Vorlage (Vertikallast, Horizontallast, Überlagerung) mit allen Momentenwerten und Auflagerreaktionen:")
    fig_comp = create_comparison_figure(solver, scale_fac=scale_fac, show_values=show_values)
    st.pyplot(fig_comp, use_container_width=True)

with tab2:
    st.subheader("Vollständige Schnittgrößenübersicht für die Überlagerung (q + H)")
    fig_full = create_full_figure(solver, scale_fac=scale_fac, show_values=show_values)
    st.pyplot(fig_full, use_container_width=True)

with tab3:
    st.subheader("Numerische Schnittgrößen & Auflagerreaktionen")
    
    # Load cases comparison table
    c_q = solver.solve_case(q_val=q, H_val=0.0)
    c_h = solver.solve_case(q_val=0.0, H_val=H)
    c_tot = solver.solve_case(q_val=q, H_val=H)
    
    df_res = pd.DataFrame({
        "Größe": [
            "Horizontalkraft A_h [kN]",
            "Vertikalkraft A_v [kN]",
            "Horizontalkraft B_h [kN]",
            "Vertikalkraft B_v [kN]",
            "Eckmoment links M_1 [kNm]",
            "Eckmoment rechts M_2 [kNm]",
            "Max. Feldmoment M_max [kNm]",
            "Stelle x(M_max) [m]",
            "Normalkraft Riegel N [kN]",
            "Normalkraft Stiel 1 N [kN]",
            "Normalkraft Stiel 2 N [kN]"
        ],
        "a) Nur q_k": [
            f"{c_q['reactions']['Ah']:.2f}",
            f"{c_q['reactions']['Av']:.2f}",
            f"{c_q['reactions']['Bh']:.2f}",
            f"{c_q['reactions']['Bv']:.2f}",
            f"{c_q['key_values']['M1']:.2f}",
            f"{c_q['key_values']['M2']:.2f}",
            f"{c_q['key_values']['M_max_beam']:.2f}",
            f"{c_q['key_values']['x_max']:.2f}",
            f"{c_q['key_values']['N_beam']:.2f}",
            f"{c_q['key_values']['N_col1']:.2f}",
            f"{c_q['key_values']['N_col2']:.2f}"
        ],
        "b) Nur H_{w,k}": [
            f"{c_h['reactions']['Ah']:.2f}",
            f"{c_h['reactions']['Av']:.2f}",
            f"{c_h['reactions']['Bh']:.2f}",
            f"{c_h['reactions']['Bv']:.2f}",
            f"{c_h['key_values']['M1']:.2f}",
            f"{c_h['key_values']['M2']:.2f}",
            f"{c_h['key_values']['M_max_beam']:.2f}",
            f"{c_h['key_values']['x_max']:.2f}",
            f"{c_h['key_values']['N_beam']:.2f}",
            f"{c_h['key_values']['N_col1']:.2f}",
            f"{c_h['key_values']['N_col2']:.2f}"
        ],
        "c) Überlagerung (q + H)": [
            f"{c_tot['reactions']['Ah']:.2f}",
            f"{c_tot['reactions']['Av']:.2f}",
            f"{c_tot['reactions']['Bh']:.2f}",
            f"{c_tot['reactions']['Bv']:.2f}",
            f"{c_tot['key_values']['M1']:.2f}",
            f"{c_tot['key_values']['M2']:.2f}",
            f"{c_tot['key_values']['M_max_beam']:.2f}",
            f"{c_tot['key_values']['x_max']:.2f}",
            f"{c_tot['key_values']['N_beam']:.2f}",
            f"{c_tot['key_values']['N_col1']:.2f}",
            f"{c_tot['key_values']['N_col2']:.2f}"
        ]
    })
    
    st.table(df_res)

with tab4:
    st.subheader("Exportierbare Schnittgrößen-Daten")
    st.write("Hier können Sie die berechneten Werte entlang des Riegels (x = 0 bis l) als CSV exportieren:")
    
    df_beam_export = pd.DataFrame({
        "x_beam_[m]": c_tot['x_beam'],
        "M_beam_[kNm]": c_tot['M_beam'],
        "V_beam_[kN]": c_tot['V_beam'],
        "N_beam_[kN]": c_tot['N_beam']
    })
    
    st.dataframe(df_beam_export.head(10))
    
    csv_data = df_beam_export.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 CSV-Datei herunterladen",
        data=csv_data,
        file_name="schnittgroessen_riegel.csv",
        mime="text/csv"
    )
