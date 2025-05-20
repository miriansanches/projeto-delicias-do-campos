import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Configuração do app
st.set_page_config(page_title="Dashboard RH", layout="wide")
st.title("📊 Dashboard de RH – Análise de Horas Extras e Anomalias")

# Arquivo fixo
ARQUIVO_EXCEL = "Dados_RH_Tratado_Geral.vf.xlsx"

if not Path(ARQUIVO_EXCEL).exists():
    st.error(f"Arquivo '{ARQUIVO_EXCEL}' não encontrado.")
    st.stop()

# Carregamento das abas
frequencia_df = pd.read_excel(ARQUIVO_EXCEL, sheet_name="Geral")
funcionarios_df = pd.read_excel(ARQUIVO_EXCEL, sheet_name="Funcionários")

# Conversões de datas
frequencia_df["Data"] = pd.to_datetime(frequencia_df["Data"], dayfirst=True, errors="coerce")
funcionarios_df["Data_admissao"] = pd.to_datetime(funcionarios_df["Data_admissao"], dayfirst=True, errors="coerce")

# Merge dos dataframes
df = pd.merge(frequencia_df, funcionarios_df, on="Id_funcionario", how="left")

# Colunas auxiliares
df["Mês"] = df["Data"].dt.month
df["Ano_Admissao"] = df["Data_admissao"].dt.year
df["Anomalia_Flag"] = df["Anomalias"].apply(lambda x: 1 if str(x).strip().lower() == "anomalia" else 0)

# Menu lateral
st.sidebar.header("Menu de Navegação")
painel = st.sidebar.radio("Escolha a análise:", ["Horas Extras", "Anomalias"])

# Dicionário de classificações
classificacoes = {
    "Funcionário": "Nome_x",
    "Setor": "Setor_x",
    "Cargo": "Cargo_x",
    "Turno": "Turno_x",
    "Dia da Semana": "Dia_Semana_x",
    "Sexo": "Sexo_x",
    "Salário": "Salário",
    "Mês": "Mês",
    "Ano de Admissão": "Ano_Admissao"
}

# Análise de Horas Extras
if painel == "Horas Extras":
    st.subheader("🔧 Classificações de Horas Extras")
    opcao = st.sidebar.selectbox("Classificar Horas Extras por:", list(classificacoes.keys()))
    coluna = classificacoes[opcao]

    agrupado = df.groupby(coluna)["Horas_extras"].sum().reset_index().sort_values(by="Horas_extras", ascending=False)
    agrupado["Horas (hh:mm)"] = pd.to_timedelta(agrupado["Horas_extras"], unit="m").astype(str).str.slice(0, 5)

    st.dataframe(agrupado, use_container_width=True)

    fig = px.bar(
        agrupado.head(10),
        x=coluna,
        y="Horas_extras",
        text="Horas (hh:mm)",
        color=coluna,
        title=f"Top 10 - Horas Extras por {opcao}",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(xaxis_title=opcao, yaxis_title="Horas Extras (min)")
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

# Análise de Anomalias
else:
    st.subheader("⚠️ Análises de Anomalias (Atrasos > 2h ou Saídas Antecipadas)")
    opcao = st.sidebar.selectbox("Classificar Anomalias por:", list(classificacoes.keys()))
    coluna = classificacoes[opcao]

    resumo = (
        df.groupby(coluna)
        .agg(Total=('Anomalia_Flag', 'count'),
             Anomalias=('Anomalia_Flag', 'sum'))
        .reset_index()
    )
    resumo["% Anomalias"] = (resumo["Anomalias"] / resumo["Total"]) * 100
    resumo = resumo.sort_values(by="Anomalias", ascending=False)

    st.dataframe(resumo, use_container_width=True)

    fig_abs = px.bar(
        resumo.head(10),
        x=coluna,
        y="Anomalias",
        text="Anomalias",
        color=coluna,
        title=f"Top 10 - Total de Anomalias por {opcao}",
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    fig_abs.update_traces(textposition="outside")
    fig_abs.update_layout(xaxis_title=opcao, yaxis_title="Total de Anomalias")
    st.plotly_chart(fig_abs, use_container_width=True)

    fig_pct = px.bar(
        resumo.head(10),
        x=coluna,
        y="% Anomalias",
        text="% Anomalias",
        color=coluna,
        title=f"Top 10 - % Anomalias por {opcao}",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_pct.update_traces(texttemplate='%{text:.1f}%', textposition="outside")
    fig_pct.update_layout(xaxis_title=opcao, yaxis_title="% de Anomalias")
    st.plotly_chart(fig_pct, use_container_width=True)
