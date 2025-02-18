import streamlit as st
import pandas as pd
import plotly.express as px
import json

st.set_page_config(page_title="Gestão de Demandas - Comunidades", layout="wide")
st.title("📂 Gestão de Demandas - Comunidades")

def load_json(file):
    try:
        df = pd.read_json(file)
        st.write("📊 Dados carregados com sucesso a partir do JSON!")
        return df
    except Exception as e:
        st.error(f"⚠️ Erro ao carregar o arquivo JSON: {e}")
        return None

COORDENADAS_FIXAS = {
    "ÁGUAS DE SANTA BÁRBARA": (-22.7666740, -49.2141300),
    "ANHEMBI": (-22.789859, -48.140030),
    "AVAÍ": (-22.159374, -49.369551),
    "BAURU": (-22.262420, -49.180159),
    "BOTUCATU": (-22.835740, -48.231794),
    "GUARANTÃ": (-21.906337, -49.586856),
    "ITATINGA": (-23.038354, -48.668439),
    "LENCOIS PAULISTA": (-22.573064, -48.785689),
    "PAULISTÂNIA": (-22.582313, -49.390672),
    "PRESIDENTE ALVES": (-22.084878, -49.422422),
    "REGINÓPOLIS": (-21.926986, -49.221164),
    "SÃO PEDRO": (-22.585806, -47.916186),
    "LINS": (-21.682648, -49.797577),
    "GETULINA": (-21.786340, -49.940519),
    "GÁLIA": (-22.304004, -49.565130),
    "SANTA CRUZ DO RIO PARDO": (-22.805438, -49.475661),
    "PONGAÍ": (-21.7948626, -49.3606179)
}

def obter_coordenadas(cidade):
    return COORDENADAS_FIXAS.get(cidade.upper(), (None, None))

file_name = 'rc2.json'
data = load_json(file_name)

if data is not None and not data.empty:
    st.subheader("📋 Filtros de Demandas")
    col1, col2 = st.columns(2)
    with col1:
        demanda_num = st.text_input("🔍 Número da demanda (#):")
    with col2:
        supervisor_name = st.multiselect("👤 Supervisor(s):", options=data['supervisor'].unique())

    filtered_data = data.copy()
    if demanda_num:
        filtered_data = filtered_data[filtered_data['#'].astype(str) == demanda_num]
    if supervisor_name:
        filtered_data = filtered_data[filtered_data['supervisor'].str.lower().isin([name.lower() for name in supervisor_name])]

    st.markdown(f"### 📊 Total de Demandas Filtradas: **{len(filtered_data)}**")
    st.dataframe(filtered_data)

    supervisor_counts = filtered_data['supervisor'].value_counts().reset_index()
    supervisor_counts.columns = ['Supervisor', 'Contagem']
    fig_supervisor = px.bar(supervisor_counts, x='Supervisor', y='Contagem', title='Demandas por Supervisor', text='Contagem', color_discrete_sequence=['#00a7ab'])
    fig_supervisor.update_layout(dragmode=False)
    st.plotly_chart(fig_supervisor)

    # Gráfico de barras horizontais por classificação
    st.subheader("📊 Demandas por Classificação")
    classificacao_counts = filtered_data['Classificação'].value_counts().reset_index()
    classificacao_counts.columns = ['Classificação', 'Contagem']
    classificacao_counts = classificacao_counts.sort_values(by='Contagem', ascending=True)
    
    fig_classificacao = px.bar(
        classificacao_counts,
        x='Contagem',
        y='Classificação',
        orientation='h',
        title='Classificação das Demandas',
        text='Contagem',
        color_discrete_sequence=['#00a7ab']
    )
    fig_classificacao.update_layout(dragmode=False)
    st.plotly_chart(fig_classificacao)

    ocorrencias = filtered_data['Cidade'].value_counts().reset_index()
    ocorrencias.columns = ['Cidade', 'Contagem']
    coordenadas = [(cidade, *obter_coordenadas(cidade), ocorrencias.loc[ocorrencias['Cidade'] == cidade, 'Contagem'].values[0]) for cidade in ocorrencias['Cidade'] if cidade in COORDENADAS_FIXAS]
    coordenadas_df = pd.DataFrame(coordenadas, columns=['Cidade', 'latitude', 'longitude', 'Contagem']).dropna()

    map_styles = ["open-street-map", "carto-positron", "carto-darkmatter", "stamen-terrain", "stamen-toner", "stamen-watercolor"]
    selected_style = st.sidebar.selectbox("🌎 Escolha o estilo do mapa:", map_styles)

    st.subheader(f"🗺️ Mapa de Ocorrências - Estilo: {selected_style}")
    fig_mapa = px.scatter_map(
        coordenadas_df,
        lat='latitude',
        lon='longitude',
        hover_name='Cidade',
        title="Ocorrências no Estado de São Paulo",
        size='Contagem',
        color_discrete_sequence=['#00a7ab'],
        zoom=7,
        height=600,
        width=800
    )
    fig_mapa.update_layout(
        map_style=selected_style,
        map_center={"lat": -22.8, "lon": -49.3},
        autosize=False,
        width=800,
        dragmode=False
    )
    st.plotly_chart(fig_mapa, use_container_width=False)
else:
    st.warning("🚫 Arquivo rc2.json não carregado ou vazio.")
