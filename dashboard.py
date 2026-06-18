import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Terrazoo | Jardinagem", layout="wide", page_icon="🌿")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #f0f2f0; }
[data-testid="stSidebar"] { background-color: #206A47; }
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] select { background-color: #1a5538 !important; color: white !important; }
h1, h2, h3 { color: #1a1a1a !important; }
p { color: #1a1a1a !important; }
div[data-testid="stMetric"] {
    background: white !important;
    border-radius: 10px !important;
    padding: 20px !important;
    border-top: 5px solid #206A47 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.12) !important;
}
div[data-testid="stMetric"] label {
    color: #222222 !important;
    font-size: 15px !important;
    font-weight: 700 !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #206A47 !important;
    font-size: 30px !important;
    font-weight: 800 !important;
}
div[data-testid="stMetric"] [data-testid="stMetricDelta"] svg { display: none; }
.section { background: white; border-radius: 12px; padding: 20px 24px; margin-bottom: 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
.sec-title { font-size: 17px !important; font-weight: 700 !important; color: #206A47 !important; border-left: 4px solid #5BCD97; padding-left: 10px; margin-bottom: 16px; }
</style>
""", unsafe_allow_html=True)

ORDEM_MES = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
GREEN  = '#206A47'
LGREEN = '#5BCD97'
RED    = '#E24B4A'
GRAY   = '#888888'

with st.sidebar:
    st.markdown("## Terrazoo")
    st.markdown("### Jardinagem")
    st.markdown("---")
    uploaded_file = st.file_uploader("Importar planilha (.xlsx)", type=["xlsx"])
    st.markdown("---")

@st.cache_data
def carregar_dados(file):
    df = pd.read_excel(file)
    df = df[df['Mês'] != 'Totais'].copy()
    cols_num = [c for c in df.columns if any(x in c for x in ["Receita","Margem","Ticket"])]
    for c in cols_num:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    df['Mês'] = pd.Categorical(df['Mês'], categories=ORDEM_MES, ordered=True)
    return df

if not uploaded_file:
    st.markdown("# Dashboard Jardinagem — Terrazoo")
    st.info("Importe sua planilha Excel na barra lateral para carregar o dashboard.")
    st.markdown("""
    **O dashboard inclui:**
    - KPIs de receita e margem (2026 vs 2025)
    - Evolução mensal de receita e margem %
    - Ranking de lojas e fornecedores
    - Top 20 produtos mais vendidos
    - Margem % por loja com comparativo 2025
    """)
    st.stop()

df = carregar_dados(uploaded_file)

with st.sidebar:
    st.markdown("### Filtros")
    mes_opts = ["Todos"] + [m for m in ORDEM_MES if m in df['Mês'].unique()]
    mes  = st.selectbox("Mes", mes_opts)
    loja_opts = ["Todas"] + sorted(df['Nome Fantasia Loja'].dropna().unique().tolist())
    loja = st.selectbox("Loja", loja_opts)
    forn_opts = ["Todos"] + sorted(df['Nome Fantasia Fornecedor'].dropna().unique().tolist())
    forn = st.selectbox("Fornecedor", forn_opts)

df_f = df.copy()
if mes  != "Todos":  df_f = df_f[df_f['Mês'] == mes]
if loja != "Todas":  df_f = df_f[df_f['Nome Fantasia Loja'] == loja]
if forn != "Todos":  df_f = df_f[df_f['Nome Fantasia Fornecedor'] == forn]

rec26   = df_f['Receita (- dev.)  2026'].sum()
rec25   = df_f['Receita (- dev.)  2025'].sum()
mg26    = df_f['Margem Gerencial (R$) 2026'].sum()
mg25    = df_f['Margem Gerencial (R$) 2025'].sum()
var_rec = ((rec26 - rec25) / rec25 * 100) if rec25 != 0 else 0
var_mg  = ((mg26  - mg25)  / mg25  * 100) if mg25  != 0 else 0
mg_pct  = (mg26 / rec26 * 100) if rec26 != 0 else 0
n_lojas = df_f['Nome Fantasia Loja'].nunique()

# HEADER
st.markdown(f"<h1 style='color:#1a1a1a;font-size:26px;margin-bottom:4px;'>Dashboard Jardinagem — Terrazoo</h1>", unsafe_allow_html=True)
periodo = f"Mes: {mes}" if mes != "Todos" else "Jan a Jun 2026"
st.markdown(f"<p style='color:#444;font-size:14px;'>Periodo: {periodo} &nbsp;|&nbsp; Loja: {loja} &nbsp;|&nbsp; Fornecedor: {forn}</p>", unsafe_allow_html=True)
st.markdown("---")

# ── 1. KPIs ──────────────────────────────────────────────────────────────────
st.markdown("<p class='sec-title'>1. Indicadores Gerais</p>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
k1.metric("Receita 2026",  f"R$ {rec26:,.0f}".replace(",","."), f"{var_rec:+.1f}% vs 2025")
k2.metric("Receita 2025",  f"R$ {rec25:,.0f}".replace(",","."))
k3.metric("Margem R$",     f"R$ {mg26:,.0f}".replace(",","."),  f"{var_mg:+.1f}% vs 2025")
k4.metric("Margem %",      f"{mg_pct:.1f}%",                    f"{n_lojas} lojas ativas")
st.markdown("---")

# ── 2. EVOLUCAO MENSAL ───────────────────────────────────────────────────────
st.markdown("<p class='sec-title'>2. Evolucao Mensal</p>", unsafe_allow_html=True)
mensal = df_f.groupby('Mês', observed=True).agg(
    rec26=('Receita (- dev.)  2026','sum'),
    rec25=('Receita (- dev.)  2025','sum'),
    mg26 =('Margem Gerencial (R$) 2026','sum'),
    mg25 =('Margem Gerencial (R$) 2025','sum'),
).reset_index().sort_values('Mês')
mensal['mg_pct26'] = (mensal['mg26'] / mensal['rec26'].replace(0, 1) * 100).round(1)
mensal['mg_pct25'] = (mensal['mg25'] / mensal['rec25'].replace(0, 1) * 100).round(1)

col1, col2 = st.columns(2)
with col1:
    st.markdown("<p style='color:#1a1a1a;font-weight:700;font-size:15px;'>Receita Mensal — 2026 vs 2025</p>", unsafe_allow_html=True)
    fig1 = go.Figure()
    fig1.add_bar(x=mensal['Mês'], y=mensal['rec26'], name='2026', marker_color=GREEN,
                 text=mensal['rec26'].apply(lambda v: f"R${v/1e3:.0f}k"), textposition='outside',
                 textfont=dict(color='#1a1a1a', size=11))
    fig1.add_bar(x=mensal['Mês'], y=mensal['rec25'], name='2025', marker_color=LGREEN)
    fig1.update_layout(barmode='group', plot_bgcolor='white', paper_bgcolor='white',
                       height=320, margin=dict(t=30,b=10,l=10,r=10),
                       legend=dict(orientation='h', y=1.1, font=dict(color='#1a1a1a')),
                       yaxis=dict(gridcolor='#eeeeee', tickfont=dict(color='#1a1a1a')),
                       xaxis=dict(tickfont=dict(color='#1a1a1a')), font=dict(color='#1a1a1a'))
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("<p style='color:#1a1a1a;font-weight:700;font-size:15px;'>Margem % Mensal — 2026 vs 2025</p>", unsafe_allow_html=True)
    fig2 = go.Figure()
    fig2.add_scatter(x=mensal['Mês'], y=mensal['mg_pct26'], name='2026', mode='lines+markers+text',
                     line=dict(color=GREEN, width=3), marker=dict(size=9),
                     text=mensal['mg_pct26'].apply(lambda v: f"{v:.1f}%"),
                     textposition='top center', textfont=dict(color=GREEN, size=12, family='Arial Black'))
    fig2.add_scatter(x=mensal['Mês'], y=mensal['mg_pct25'], name='2025', mode='lines+markers+text',
                     line=dict(color=GRAY, width=2, dash='dash'), marker=dict(size=7),
                     text=mensal['mg_pct25'].apply(lambda v: f"{v:.1f}%"),
                     textposition='bottom center', textfont=dict(color=GRAY, size=11))
    fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                       height=320, margin=dict(t=30,b=10,l=10,r=10),
                       legend=dict(orientation='h', y=1.1, font=dict(color='#1a1a1a')),
                       yaxis=dict(ticksuffix='%', gridcolor='#eeeeee', tickfont=dict(color='#1a1a1a')),
                       xaxis=dict(tickfont=dict(color='#1a1a1a')), font=dict(color='#1a1a1a'))
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ── 3. RANKINGS ──────────────────────────────────────────────────────────────
st.markdown("<p class='sec-title'>3. Rankings — Lojas e Fornecedores</p>", unsafe_allow_html=True)
col3, col4 = st.columns(2)

with col3:
    st.markdown("<p style='color:#1a1a1a;font-weight:700;font-size:15px;'>Top 10 Lojas — Receita 2026</p>", unsafe_allow_html=True)
    top_lojas = df_f.groupby('Nome Fantasia Loja')['Receita (- dev.)  2026'].sum().nlargest(10).reset_index()
    top_lojas.columns = ['Loja','Receita']
    top_lojas['label'] = top_lojas['Receita'].apply(lambda v: f"R${v/1e3:.0f}k")
    fig3 = px.bar(top_lojas, x='Receita', y='Loja', orientation='h',
                  color_discrete_sequence=[GREEN], text='label')
    fig3.update_layout(plot_bgcolor='white', paper_bgcolor='white', height=380,
                       margin=dict(t=10,b=10,l=10,r=80),
                       yaxis=dict(autorange='reversed', tickfont=dict(color='#1a1a1a')),
                       xaxis=dict(gridcolor='#eeeeee', tickfont=dict(color='#1a1a1a')),
                       font=dict(color='#1a1a1a'))
    fig3.update_traces(textposition='outside', textfont=dict(color='#1a1a1a', size=12))
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown("<p style='color:#1a1a1a;font-weight:700;font-size:15px;'>Top 10 Fornecedores — Receita 2026</p>", unsafe_allow_html=True)
    top_forn = df_f.groupby('Nome Fantasia Fornecedor')['Receita (- dev.)  2026'].sum().nlargest(10).reset_index()
    top_forn.columns = ['Fornecedor','Receita']
    top_forn['label'] = top_forn['Receita'].apply(lambda v: f"R${v/1e3:.0f}k")
    fig4 = px.bar(top_forn, x='Receita', y='Fornecedor', orientation='h',
                  color_discrete_sequence=['#1a7a52'], text='label')
    fig4.update_layout(plot_bgcolor='white', paper_bgcolor='white', height=380,
                       margin=dict(t=10,b=10,l=10,r=80),
                       yaxis=dict(autorange='reversed', tickfont=dict(color='#1a1a1a')),
                       xaxis=dict(gridcolor='#eeeeee', tickfont=dict(color='#1a1a1a')),
                       font=dict(color='#1a1a1a'))
    fig4.update_traces(textposition='outside', textfont=dict(color='#1a1a1a', size=12))
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ── 4. PRODUTOS ──────────────────────────────────────────────────────────────
st.markdown("<p class='sec-title'>4. Top 20 Produtos Mais Vendidos</p>", unsafe_allow_html=True)
top_prod = df_f.groupby('Produto').agg(
    receita=('Receita (- dev.)  2026','sum'),
    margem=('Margem Gerencial (R$) 2026','sum')
).reset_index()
top_prod['mg_pct'] = (top_prod['margem'] / top_prod['receita'].replace(0,1) * 100).round(1)
top_prod = top_prod.nlargest(20, 'receita')
top_prod['label'] = top_prod['receita'].apply(lambda v: f"R${v/1e3:.0f}k")

fig5 = px.bar(top_prod, x='receita', y='Produto', orientation='h',
              color='mg_pct', color_continuous_scale=[[0,RED],[0.5,LGREEN],[1,GREEN]],
              text='label')
fig5.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                   height=640, margin=dict(t=10,b=10,l=10,r=140),
                   yaxis=dict(autorange='reversed', tickfont=dict(color='#1a1a1a')),
                   xaxis=dict(gridcolor='#eeeeee', tickfont=dict(color='#1a1a1a')),
                   coloraxis_colorbar=dict(title='Margem %', ticksuffix='%',
                                           tickfont=dict(color='#1a1a1a'),
                                           title_font=dict(color='#1a1a1a')),
                   font=dict(color='#1a1a1a'))
fig5.update_traces(textposition='outside', textfont=dict(color='#1a1a1a', size=11))
st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# ── 5. MARGEM % POR LOJA — COM COMPARATIVO 2025 ──────────────────────────────
st.markdown("<p class='sec-title'>5. Margem % por Loja — 2026 vs 2025</p>", unsafe_allow_html=True)

mg_loja = df_f.groupby('Nome Fantasia Loja').apply(
    lambda x: pd.Series({
        'mg_pct26': round(x['Margem Gerencial (R$) 2026'].sum() / x['Receita (- dev.)  2026'].sum() * 100, 1) if x['Receita (- dev.)  2026'].sum() != 0 else 0,
        'mg_pct25': round(x['Margem Gerencial (R$) 2025'].sum() / x['Receita (- dev.)  2025'].sum() * 100, 1) if x['Receita (- dev.)  2025'].sum() != 0 else 0,
    })
).reset_index().sort_values('mg_pct26', ascending=False)

media26 = mg_loja['mg_pct26'].mean()
media25 = mg_loja['mg_pct25'].mean()

fig6 = go.Figure()
fig6.add_bar(x=mg_loja['Nome Fantasia Loja'], y=mg_loja['mg_pct26'], name='2026',
             marker_color=GREEN, text=mg_loja['mg_pct26'].apply(lambda v: f"{v:.1f}%"),
             textposition='outside', textfont=dict(color='#1a1a1a', size=11))
fig6.add_bar(x=mg_loja['Nome Fantasia Loja'], y=mg_loja['mg_pct25'], name='2025',
             marker_color=LGREEN, text=mg_loja['mg_pct25'].apply(lambda v: f"{v:.1f}%"),
             textposition='outside', textfont=dict(color='#444', size=10))
fig6.add_hline(y=media26, line_dash='dash', line_color=GREEN, line_width=2,
               annotation_text=f"Media 2026: {media26:.1f}%",
               annotation_font=dict(color=GREEN, size=12), annotation_position='top left')
fig6.add_hline(y=media25, line_dash='dot', line_color=GRAY, line_width=1.5,
               annotation_text=f"Media 2025: {media25:.1f}%",
               annotation_font=dict(color=GRAY, size=11), annotation_position='bottom right')
fig6.update_layout(barmode='group', plot_bgcolor='white', paper_bgcolor='white',
                   height=420, margin=dict(t=50,b=10,l=10,r=10),
                   xaxis=dict(tickangle=35, tickfont=dict(color='#1a1a1a')),
                   yaxis=dict(ticksuffix='%', gridcolor='#eeeeee', tickfont=dict(color='#1a1a1a')),
                   legend=dict(orientation='h', y=1.08, font=dict(color='#1a1a1a')),
                   font=dict(color='#1a1a1a'))
st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
with st.expander("Ver dados detalhados"):
    st.dataframe(df_f.sort_values('Receita (- dev.)  2026', ascending=False).head(1000), use_container_width=True)

st.caption("Terrazoo · Dashboard Jardinagem · Desenvolvido com Streamlit")
