import streamlit as st
import random
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
from PIL import Image

st.set_page_config(page_title="Dashboard ENEM Itacoatiara", layout="wide")

col_logo, col_titulo = st.columns([1, 6])

with col_logo:
    try:
        imagem = Image.open("logo.png")
        st.image(imagem, width=120)
    except FileNotFoundError:
        st.warning("Coloque o arquivo 'logo.png' na pasta.")

with col_titulo:
    st.markdown(
        """
        <h1 style='font-size: 45px; margin-top: 20px;'>
            EDUDATA <span style='color: #2E8B57;'>ITA</span>
        </h1>
        <p style='font-size: 18px; color: gray;'>Avaliação de desempenho escolar: Itacoatiara</p>
        """,
        unsafe_allow_html=True
    )

CSV_PATH = "MD_ENEM_ITACOATIARA_FULL.csv"  # MEU ARQUIVO PRINCIPAL

try:
    df = pd.read_csv(CSV_PATH, encoding="cp1252", sep=";", dtype=str)
except FileNotFoundError:
    st.error("O arquivo CSV não foi encontrado.")
    st.stop()

total_geral_no_csv = len(df)

campo_anos = st.sidebar.selectbox(
    "Anos",
    ["2019", "2023", "2019 e 2023"], index=2
)
selecionar_todos = st.sidebar.checkbox("Incluir os estudantes sem escola associada", value=True)
if not selecionar_todos:
    df = df[df["CO_MUNICIPIO_ESC"] == "1301902"]

df["NU_ANO"] = (
    df["NU_ANO"]
    .astype(str)
    .str.extract(r"(20\d{2})")  # pega apenas anos válidos
    .astype(float)
    .astype("Int64")
)

if campo_anos != "2019 e 2023":
    ano_escolhido = int(campo_anos)
    df = df[df["NU_ANO"] == ano_escolhido]

df_base_para_metricas = df.copy()

# FILTROS PARA OS TREINEIROS
st.sidebar.markdown("---")
st.sidebar.header("Filtros Adicionais")

incluir_treineiros = st.sidebar.checkbox(
    "Incluir estudantes treineiros", value=True
)
if not incluir_treineiros:
    df = df[df["IN_TREINEIRO"] == "0"]

mapa_sexo = {"M": "Masculino", "F": "Feminino"}
mapa_estado_civil = {
    "0": "Não informado",
    "1": "Solteiro(a)",
    "2": "Casado(a)",
    "3": "Divorciado(a)",
    "4": "Viúvo(a)"
}
mapa_cor_raca = {
    "0": "Não declarado",
    "1": "Branca",
    "2": "Preta",
    "3": "Parda",
    "4": "Amarela",
    "5": "Indígena"
}
mapa_faixa_etaria = {
    "1": "Menor de 17 anos",
    "2": "17 anos",
    "3": "18 anos",
    "4": "19 anos",
    "5": "20 anos",
    "6": "21 anos",
    "7": "22 anos",
    "8": "23 anos",
    "9": "24 anos",
    "10": "25 a 29 anos",
    "11": "30 a 34 anos",
    "12": "35 a 39 anos",
    "13": "40 a 44 anos",
    "14": "45 a 49 anos",
    "15": "50 a 54 anos",
    "16": "55 a 59 anos",
    "17": "60 anos ou mais"
}

dependencia_dict = {"1": "Federal", "2": "Estadual", "3": "Municipal", "4": "Privada"}
ensino_dict = {"1": "Ensino Regular", "2": "Educação Especial - Modalidade Substitutiva", "3": "EJA"}
localizacao_dict = {"1": "Urbana", "2": "Rural"}

mapa_computador = {
    "A": "Não possui computador",
    "B": "1 computador",
    "C": "2 computadores",
    "D": "3 computadores",
    "E": "4 ou mais computadores"
}
mapa_celular = {
    "A": "Não possui celular",
    "B": "1 celular",
    "C": "2 celulares",
    "D": "3 celulares",
    "E": "4 ou mais celulares"
}
mapa_internet = {
    "A": "Não possui acesso à Internet",
    "B": "Acesso por celular",
    "C": "Acesso por computador",
    "D": "Acesso por outros meios",
    "E": "Possui acesso por múltiplos meios"
}
mapa_tv = {
    "A": "Não possui televisão",
    "B": "1 televisão",
    "C": "2 televisões",
    "D": "3 televisões",
    "E": "4 ou mais televisões"
}
mapa_automovel = {
    "A": "Não possui carro nem moto",
    "B": "Possui somente carro",
    "C": "Possui somente moto",
    "D": "Possui carro e moto"
}

# -----------------------
# EXPANDERS NA SIDEBAR (Geral, Escola, Bens e Moradia) usando valores reais do df_filtrado
# -----------------------
with st.sidebar.expander("Geral", expanded=False):
    st.subheader("Filtros gerais (dados reais)")

    tmp = df.copy()

    if "TP_SEXO" in tmp.columns:
        tmp["TP_SEXO_DESC"] = tmp["TP_SEXO"].map(mapa_sexo).fillna(tmp["TP_SEXO"])
        opcoes = sorted(tmp["TP_SEXO_DESC"].dropna().unique().tolist())
        sexo_sel = st.multiselect("Sexo", options=opcoes, default=[])
        if sexo_sel:
            inv = {v: k for k, v in mapa_sexo.items()}
            codigos_sel = [inv[s] if s in inv else s for s in sexo_sel]
            df = df[df["TP_SEXO"].isin(codigos_sel) | df.get("TP_SEXO_DESC", pd.Series()).isin(sexo_sel)]

    if "TP_ESTADO_CIVIL" in tmp.columns:
        tmp["TP_ESTADO_CIVIL_DESC"] = tmp["TP_ESTADO_CIVIL"].map(mapa_estado_civil).fillna(tmp["TP_ESTADO_CIVIL"])
        opcoes = sorted(tmp["TP_ESTADO_CIVIL_DESC"].dropna().unique().tolist())
        estado_sel = st.multiselect("Estado civil", options=opcoes, default=[])
        if estado_sel:
            inv = {v: k for k, v in mapa_estado_civil.items()}
            codigos_sel = [inv[s] if s in inv else s for s in estado_sel]
            df = df[
                df["TP_ESTADO_CIVIL"].isin(codigos_sel) | df.get("TP_ESTADO_CIVIL_DESC", pd.Series()).isin(estado_sel)]

    if "TP_COR_RACA" in tmp.columns:
        tmp["TP_COR_RACA_DESC"] = tmp["TP_COR_RACA"].map(mapa_cor_raca).fillna(tmp["TP_COR_RACA"])
        opcoes = sorted(tmp["TP_COR_RACA_DESC"].dropna().unique().tolist())
        raca_sel = st.multiselect("Cor/Raça", options=opcoes, default=[])
        if raca_sel:
            inv = {v: k for k, v in mapa_cor_raca.items()}
            codigos_sel = [inv[s] if s in inv else s for s in raca_sel]
            df = df[df["TP_COR_RACA"].isin(codigos_sel) | df.get("TP_COR_RACA_DESC", pd.Series()).isin(raca_sel)]

    if "TP_FAIXA_ETARIA" in tmp.columns:
        tmp["TP_FAIXA_ETARIA_DESC"] = tmp["TP_FAIXA_ETARIA"].map(mapa_faixa_etaria).fillna(tmp["TP_FAIXA_ETARIA"])
        opcoes = sorted(tmp["TP_FAIXA_ETARIA_DESC"].dropna().unique().tolist(), key=lambda x: (len(x), x))
        faixa_sel = st.multiselect("Faixa etária", options=opcoes, default=[])
        if faixa_sel:
            inv = {v: k for k, v in mapa_faixa_etaria.items()}
            codigos_sel = [inv[s] if s in inv else s for s in faixa_sel]
            df = df[
                df["TP_FAIXA_ETARIA"].isin(codigos_sel) | df.get("TP_FAIXA_ETARIA_DESC", pd.Series()).isin(faixa_sel)]

    mapa_renda = {
        "A": 0, "B": 1.5, "C": 2, "D": 3, "E": 4, "F": 5,
        "G": 7, "H": 10, "I": 12, "J": 15, "K": 20,
        "L": 25, "M": 30, "N": 40, "O": 50
    }
    if "Q006" in df.columns:
        df["RENDA_SM"] = df["Q006"].map(mapa_renda)
        if df["RENDA_SM"].notna().any():
            min_renda = float(df["RENDA_SM"].min())
            max_renda = float(df["RENDA_SM"].max())
            renda_range = st.slider(
                "Selecione a faixa de renda (salários mínimos)",
                min_value=min_renda,
                max_value=max_renda,
                value=(min_renda, max_renda),
                step=0.5
            )
            df = df[(df["RENDA_SM"] >= renda_range[0]) & (df["RENDA_SM"] <= renda_range[1])]

    st.markdown(f"**Total após filtros gerais:** {len(df):,}")

with st.sidebar.expander("Escola", expanded=False):
    st.subheader("Informações sobre a Escola (dados reais)")
    tmp = df.copy()

    if "TP_DEPENDENCIA_ADM_ESC" in tmp.columns:
        tmp["TP_DEPENDENCIA_ADM_ESC_DESC"] = tmp["TP_DEPENDENCIA_ADM_ESC"].map(dependencia_dict).fillna(
            tmp["TP_DEPENDENCIA_ADM_ESC"])
        opcoes = sorted(tmp["TP_DEPENDENCIA_ADM_ESC_DESC"].dropna().unique().tolist())
        dependencia_sel = st.multiselect("Tipo de administração da escola", options=opcoes, default=[])
        if dependencia_sel:
            inv = {v: k for k, v in dependencia_dict.items()}
            codigos_sel = [inv[s] if s in inv else s for s in dependencia_sel]
            df = df[df["TP_DEPENDENCIA_ADM_ESC"].isin(codigos_sel) | df.get("TP_DEPENDENCIA_ADM_ESC_DESC",
                                                                            pd.Series()).isin(dependencia_sel)]

    if "TP_ENSINO" in tmp.columns:
        tmp["TP_ENSINO_DESC"] = tmp["TP_ENSINO"].map(ensino_dict).fillna(tmp["TP_ENSINO"])
        opcoes = sorted(tmp["TP_ENSINO_DESC"].dropna().unique().tolist())
        ensino_sel = st.multiselect("Tipo de ensino", options=opcoes, default=[])
        if ensino_sel:
            inv = {v: k for k, v in ensino_dict.items()}
            codigos_sel = [inv[s] if s in inv else s for s in ensino_sel]
            df = df[df["TP_ENSINO"].isin(codigos_sel) | df.get("TP_ENSINO_DESC", pd.Series()).isin(ensino_sel)]

    if "TP_LOCALIZACAO_ESC" in tmp.columns:
        tmp["TP_LOCALIZACAO_ESC_DESC"] = tmp["TP_LOCALIZACAO_ESC"].map(localizacao_dict).fillna(
            tmp["TP_LOCALIZACAO_ESC"])
        opcoes = sorted(tmp["TP_LOCALIZACAO_ESC_DESC"].dropna().unique().tolist())
        local_sel = st.multiselect("Localidade da escola", options=opcoes, default=[])
        if local_sel:
            inv = {v: k for k, v in localizacao_dict.items()}
            codigos_sel = [inv[s] if s in inv else s for s in local_sel]
            df = df[df["TP_LOCALIZACAO_ESC"].isin(codigos_sel) | df.get("TP_LOCALIZACAO_ESC_DESC", pd.Series()).isin(
                local_sel)]

    if "NO_ESCOLA" in tmp.columns:
        opcoes = sorted(tmp["NO_ESCOLA"].dropna().unique().tolist())
        escola_sel = st.multiselect("Nome da escola", options=opcoes, default=[])
        if escola_sel:
            df = df[df["NO_ESCOLA"].isin(escola_sel)]
    if "NO_MUNICIPIO_ESC" in tmp.columns:
        opcoes = sorted(tmp["NO_MUNICIPIO_ESC"].dropna().unique().tolist())
        mun_sel = st.multiselect("Município (escola)", options=opcoes, default=[])
        if mun_sel:
            df = df[df["NO_MUNICIPIO_ESC"].isin(mun_sel)]

    st.markdown(f"**Total após filtros de escola:** {len(df):,}")

with st.sidebar.expander("Bens e Moradia", expanded=False):
    st.subheader("Bens e Moradia (dados reais)")
    tmp = df.copy()

    if "Q024" in tmp.columns:
        tmp["Q024_DESC"] = tmp["Q024"].map(mapa_computador).fillna(tmp["Q024"])
        opcoes = sorted(tmp["Q024_DESC"].dropna().unique().tolist())
        computador_sel = st.multiselect("Computador", options=opcoes, default=[])
        if computador_sel:
            inv = {v: k for k, v in mapa_computador.items()}
            codigos_sel = [inv[s] if s in inv else s for s in computador_sel]
            df = df[df["Q024"].isin(codigos_sel) | df.get("Q024_DESC", pd.Series()).isin(codigos_sel)]

    if "Q027" in tmp.columns:
        tmp["Q027_DESC"] = tmp["Q027"].map(mapa_celular).fillna(tmp["Q027"])
        opcoes = sorted(tmp["Q027_DESC"].dropna().unique().tolist())
        celular_sel = st.multiselect("Celular", options=opcoes, default=[])
        if celular_sel:
            inv = {v: k for k, v in mapa_celular.items()}
            codigos_sel = [inv[s] if s in inv else s for s in celular_sel]
            df = df[df["Q027"].isin(codigos_sel) | df.get("Q027_DESC", pd.Series()).isin(codigos_sel)]

    if "Q025" in tmp.columns:
        tmp["Q025_DESC"] = tmp["Q025"].map(mapa_internet).fillna(tmp["Q025"])
        opcoes = sorted(tmp["Q025_DESC"].dropna().unique().tolist())
        internet_sel = st.multiselect("Internet", options=opcoes, default=[])
        if internet_sel:
            inv = {v: k for k, v in mapa_internet.items()}
            codigos_sel = [inv[s] if s in inv else s for s in internet_sel]
            df = df[df["Q025"].isin(codigos_sel) | df.get("Q025_DESC", pd.Series()).isin(codigos_sel)]

    if "Q026" in tmp.columns:
        tmp["Q026_DESC"] = tmp["Q026"].map(mapa_tv).fillna(tmp["Q026"])
        opcoes = sorted(tmp["Q026_DESC"].dropna().unique().tolist())
        tv_sel = st.multiselect("Televisão", options=opcoes, default=[])
        if tv_sel:
            inv = {v: k for k, v in mapa_tv.items()}
            codigos_sel = [inv[s] if s in inv else s for s in tv_sel]
            df = df[df["Q026"].isin(codigos_sel) | df.get("Q026_DESC", pd.Series()).isin(codigos_sel)]

    if "Q028" in tmp.columns:
        tmp["Q028_DESC"] = tmp["Q028"].map(mapa_automovel).fillna(tmp["Q028"])
        opcoes = sorted(tmp["Q028_DESC"].dropna().unique().tolist())
        automovel_sel = st.selectbox("Automóvel", options=[""] + opcoes, index=0)
        if automovel_sel:
            inv = {v: k for k, v in mapa_automovel.items()}
            codigo = inv[automovel_sel] if automovel_sel in inv else automovel_sel
            df = df[(df["Q028"] == codigo) | (df.get("Q028_DESC", pd.Series()) == automovel_sel)]

    st.markdown(f"**Total após filtros bens/moradia:** {len(df):,}")

st.header("Perspectiva de Desempenho")

tab1, tab2, tab3, tab4 = st.tabs(["📝 Inscritos", "🙋 Presença", "🧮 Notas", "📘 Médias", ])

# ------------------------------PRIMEIRA ABA: INSCRITOS (CORRIGIDA)-------------------------------

with tab1:
    total_inscritos_base = len(df_base_para_metricas)
    total_regulares_base = len(df_base_para_metricas[df_base_para_metricas["IN_TREINEIRO"] == "0"])
    total_treineiros_base = len(df_base_para_metricas[df_base_para_metricas["IN_TREINEIRO"] == "1"])
    total_final_filtrado = len(df)

    cols = st.columns([0.2, 1, 1, 1, 1, 1])

    total_ingles_base = len(df_base_para_metricas[df_base_para_metricas["TP_LINGUA"] == 0])
    total_espanhol_base = len(df_base_para_metricas[df_base_para_metricas["TP_LINGUA"] == 1])

    cols[1].metric("Inscritos Base", total_inscritos_base)
    cols[2].metric("Regulares", total_regulares_base)
    cols[3].metric("Treineiros", total_treineiros_base)
    cols[4].metric("Língua Inglesa", total_ingles_base)
    cols[5].metric("Língua Espanhola", total_espanhol_base)

    # ---------------------------------------BLOCO DAS INSCRIÇÕES---------------------------------------
    st.markdown('<h4 style="margin-bottom:5px;">Gráfico de inscritos por ano</h4>', unsafe_allow_html=True)

    df_chart = df_base_para_metricas.groupby("NU_ANO").size().reset_index(name="Quantidade")
    df_chart = df_chart[df_chart["NU_ANO"].isin([2019, 2023])]
    df_chart["NU_ANO"] = df_chart["NU_ANO"].astype(str)

    fig_inscritos = px.bar(
        df_chart,
        x="NU_ANO",
        y="Quantidade",
        text="Quantidade",
        color_discrete_sequence=["#005FB8"]
    )

    fig_inscritos.update_traces(
        textposition="inside",
        textfont=dict(size=16, color="white"),
        cliponaxis=False
    )

    fig_inscritos.update_layout(
        xaxis_title="Ano",
        yaxis_title="Qtd. de inscritos",
        xaxis=dict(tickmode='array', tickvals=["2019", "2023"]),
        plot_bgcolor="white",
        showlegend=False,
        height=450,
        margin=dict(t=20)
    )

    fig_inscritos.update_yaxes(showgrid=True, gridcolor='#E5E5E5')
    st.plotly_chart(fig_inscritos, use_container_width=True)

# -----------------------Segunda ABA: PRESENÇA---------------------------------
with tab2:
    # Expander fechado por padrão
    exp = st.expander("### Presença nos dois dias de prova", expanded=False)
    with exp:
        dias = {
            "Dia 1 - Ciências Humanas, Linguagens e Redação": "TP_PRESENCA_CH",
            "Dia 2 - Ciências da Natureza e Matemática": "TP_PRESENCA_CN"
        }

        for nome_dia, coluna in dias.items():
            if coluna not in df.columns:
                st.warning(f"Coluna {coluna} não encontrada no CSV.")
                continue

            df[coluna] = df[coluna].replace({
                "0": "Ausente",
                "1": "Presente",
                "2": "Eliminado"
            })

            st.subheader(nome_dia)
            col1, col2 = st.columns(2)

            count = df.groupby(coluna).size().reset_index(name="Quantidade")
            fig_pizza = px.pie(
                count, values="Quantidade", names=coluna,
                title="Percentual de presença", hole=0.3,
                labels={coluna: "Categoria"}
            )
            fig_pizza.update_traces(
                textfont={"size": 18},
                textinfo="percent+label",
                texttemplate="%{label}: %{percent:.1%}"
            )
            with col1:
                st.plotly_chart(fig_pizza, use_container_width=True)

            barra = df.groupby(["NU_ANO", coluna]).size().reset_index(name="Quantidade")
            barra_total = barra.groupby("NU_ANO")["Quantidade"].transform("sum")
            barra["Percentual"] = barra["Quantidade"] / barra_total

            fig_barra = px.bar(
                barra,
                x="NU_ANO", y="Percentual",
                color=coluna, text=barra["Percentual"].apply(lambda x: f"{x:.1%}"),
                barmode="group",
                title="Situação por ano",
                category_orders={coluna: ["Presente", "Ausente", "Eliminado"]},
                labels={"NU_ANO": "Ano", "Percentual": "Percentual",
                        coluna: "Categoria"}
            )
            fig_barra.update_yaxes(tickformat=".0%")
            with col2:
                st.plotly_chart(fig_barra, use_container_width=True)

        # ----------------------- Parte 2: Gráfico geral de presença combinada (Dia 1 + Dia 2) ------------------------------
        if all(col in df.columns for col in dias.values()):
            df["Status_Geral"] = np.select(
                [
                    (df["TP_PRESENCA_CH"] == "Presente") & (df["TP_PRESENCA_CN"] == "Presente"),
                    (df["TP_PRESENCA_CH"] == "Presente") & (df["TP_PRESENCA_CN"] != "Presente"),
                    (df["TP_PRESENCA_CH"] != "Presente") & (df["TP_PRESENCA_CN"] == "Presente"),
                    (df["TP_PRESENCA_CH"] != "Presente") & (df["TP_PRESENCA_CN"] != "Presente")
                ],
                [
                    "Presente nos dois dias",
                    "Apenas no 1º dia",
                    "Apenas no 2º dia",
                    "Ausente em ambos os dias"
                ],
                default="Dados insuficientes"
            )

            st.markdown("---")
            st.subheader("Percentuais gerais de presença em cada dia")

            # Cálculo REAL por meio do DF
            geral = df["Status_Geral"].value_counts(dropna=False).reset_index()
            geral.columns = ["Situação", "Quantidade"]

            # Cálculo do percentual real
            total = geral["Quantidade"].sum()
            geral["Percentual"] = geral["Quantidade"] / total

            # Paleta usada no restante do dashboard
            cores = {
                "Apenas no 1º dia": "#FFA15A",
                "Apenas no 2º dia": "#00CC96",
                "Ausente em ambos os dias": "#EF553B",
                "Presente nos dois dias": "#636EFA"
            }

            # Ordenação correta no gráfico
            ordem = [
                "Apenas no 1º dia",
                "Apenas no 2º dia",
                "Ausente em ambos os dias",
                "Presente nos dois dias"
            ]

            fig_geral = px.bar(
                geral,
                x="Situação",
                y="Percentual",
                text=geral["Percentual"].apply(lambda x: f"{x:.1%}"),
                color="Situação",
                color_discrete_map=cores,
                category_orders={"Situação": ordem}
            )

            fig_geral.update_yaxes(tickformat=".0%")
            fig_geral.update_traces(textposition="inside", insidetextfont_color="white")

            st.plotly_chart(fig_geral, use_container_width=True)

# ------------------------------------------NOTAS MÉDIAS-----------------------------------------
with tab3:
    subtab1, subtab2 = st.tabs(["📝 Questões", "📘 Medidas Centrais"])

    with subtab1:
        exp1 = st.expander("Quantidades totais de questões")
        with exp1:
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Ciências da Natureza", 45)
            col2.metric("Ciências Humanas", 45)
            col3.metric("Matemática", 45)
            col4.metric("Linguagens e Códigos", 45)
            col5.metric("Total", 180)

        exp2 = st.expander("Quantidades de questões por complexidade", expanded=False)
        with exp2:

            materias = ["Ciências Naturais", "Ciências Humanas", "Matemática",
                        "Linguagens e Códigos", "Redação", "Total"]

            anos = ["2019", "2023"]
            categorias = ["Baixa", "Média", "Alta"]

            arrays = [
                [ano for ano in anos for _ in categorias],
                categorias * len(anos)
            ]
            tuples = list(zip(*arrays))
            col_index = pd.MultiIndex.from_tuples(tuples, names=["Ano", "Nível"])
            df_complex = pd.DataFrame(index=materias, columns=col_index, dtype=float)
            for materia in materias:
                for ano in anos:
                    df_complex.loc[materia, ano] = np.random.rand(3) * 100

            st.write(df_complex)

        exp3 = st.expander("Quantidades de questões por habilidade")
        with exp3:
            num_habilidades = 30

            anos = ["Média"] + [str(ano) for ano in range(2018, 2024)]

            habilidades = [f"HAB{str(i + 1).zfill(3)} - Habilidade {i + 1}" for i in range(num_habilidades)]

            valores = np.random.randint(1, 11, size=(num_habilidades, len(anos)))

            df_hab = pd.DataFrame(valores, columns=anos)
            df_hab.insert(0, "Habilidade", habilidades)

            st.write(df_hab)

        exp4 = st.expander("Habilidades de melhores desempenhos por área")
        with exp4:
            ini = 0.2
            fim = 0.9
            asc = True

            num_habilidades = 3
            habilidades = [f"HAB{str(i + 1).zfill(3)} - Habilidade {i + 1}" for i in range(num_habilidades)]

            percentuais = np.random.uniform(ini, fim, size=num_habilidades)

            df_hab = pd.DataFrame({
                "Habilidade": habilidades,
                "Percentual de Acerto": percentuais
            })
            df_hab = df_hab.sort_values(by="Percentual de Acerto", ascending=asc)
            df_hab.index = list(range(1, len(df_hab) + 1))
            st.write(df_hab)

        exp5 = st.expander("Habilidades de piores desempenhos por área")
        with exp5:
            st.write("Conteúdo aqui (se quiser deixar vazio, pode remover o 'with')")

        exp6 = st.expander("Características dos acertos")
        with exp6:

            st.write("**Distribuição dos acertos por parâmetro e intensidade**")

            niveis = ["Baixa", "Média", "Alta"]

            valores_D = [random.randint(10, 100) for _ in niveis]
            total_D = sum(valores_D)
            discriminalidade = [v * 100 / total_D for v in valores_D]

            valores_F = [random.randint(10, 100) for _ in niveis]
            total_F = sum(valores_F)
            dificuldade = [v * 100 / total_F for v in valores_F]

            valores_C = [random.randint(10, 100) for _ in niveis]
            total_C = sum(valores_C)
            chute = [v * 100 / total_C for v in valores_C]

            parametros = {
                "Discriminalidade": discriminalidade,
                "Dificuldade": dificuldade,
                "Chute": chute
            }

            col1, col2, col3 = st.columns(3)

            for col, (param, valores) in zip([col1, col2, col3], parametros.items()):
                df_temp = pd.DataFrame({
                    "Intensidade": niveis,
                    "Percentual": valores
                })

                fig_pizza = px.pie(
                    df_temp,
                    names="Intensidade",
                    values="Percentual",
                    title=param,
                )

                col.plotly_chart(fig_pizza, use_container_width=True)

            parametros2 = ["Dificuldade", "Discriminalidade", "Chute"]
            niveis2 = ["Baixa", "Média", "Alta"]

            dados = np.random.randint(10, 100, size=(len(niveis2), len(parametros2)))
            df_barras = pd.DataFrame(dados, columns=parametros2, index=niveis2)

            fig = px.bar(
                df_barras,
                barmode="group",
                title="Percentual de acerto por parâmetro e intensidade",
                labels={"value": "Percentual (%)", "index": "Intensidade"}
            )

            st.plotly_chart(fig, use_container_width=True)

    with subtab2:
        exp = st.expander("Médias por ano e área")
        with exp:
            st.subheader("Médias aritméticas")

            col_names = [
                "Geral",
                "Ciências Naturais",
                "Ciências Humanas",
                "Matemática",
                "Linguagens e Códigos",
                "Redação"
            ]

            # Valores fictícios — substitua depois pelos reais
            col_values = [10., 20., 30., 40., 50., 60.]

            cols = st.columns(6)
            for nome, valor, coluna in zip(col_names, col_values, cols):
                with coluna:
                    st.metric(label=nome, value=valor)

        exp = st.expander("Histograma de Médias gerais")
        with exp:
            data = {
                "intervalo": [
                    "[0-100]", "[0-100]",
                    "[100-200]", "[100-200]",
                    "[200-300]", "[200-300]",
                    "[300-400]", "[300-400]",
                    "[400-500]", "[400-500]",
                ],
                "ano": ["2019", "2023"] * 5,
                "percentual": [0.1, 0.3, 0.15, 0.25, 0.2, 0.2, 0.25, 0.15, 0.3, 0.1],
            }

            df = pd.DataFrame(data)

            fig = px.bar(
                df,
                x="intervalo",
                y="percentual",
                color="ano",
                barmode="group",
                labels={"intervalo": "Faixa de notas", "percentual": "Percentual"},
                text=[f"{v * 100:.1f}%" for v in df["percentual"]],
            )

            fig.update_traces(textposition="inside", textfont_size=16)
            fig.update_layout(yaxis=dict(tickformat=".1%", range=[0, 0.35]))

            st.plotly_chart(fig, use_container_width=True)

        exp = st.expander("Médias por administração da escola")
        with exp:
            anos = ["2019", "2023"]
            adm = ["Federal", "Estadual", "Municipal", "Privada", "Sem informação"]

            np.random.seed(42)
            valores = np.random.randint(100, 501, size=(len(anos), len(adm)))

            df = pd.DataFrame(valores, index=anos, columns=adm)

            fig = px.imshow(
                df.values,
                x=df.columns.tolist(),
                y=df.index.tolist(),
                labels=dict(x="Administração", y="Ano", color="Nota"),
                color_continuous_scale=["white", "darkblue"],
                range_color=(0, 500),
                aspect="auto"
            )

            fig.data[0].text = df.values.astype(int)
            fig.data[0].texttemplate = "%{text}"
            fig.data[0].textfont = dict(color="black", size=12)

            fig.update_yaxes(autorange="reversed")
            fig.update_traces(textfont=dict(size=20))

            st.plotly_chart(fig, use_container_width=True)

        exp = st.expander("Médias por localidade da escola")
        with exp:
            anos = ["2019", "2023"]
            locais = ["Urbana", "Rural", "Sem informação"]

            np.random.seed(42)
            valores = np.random.randint(100, 501, size=(len(anos), len(locais)))

            df = pd.DataFrame(valores, index=anos, columns=locais)

            fig = px.imshow(
                df.values,
                x=df.columns.tolist(),
                y=df.index.tolist(),
                labels=dict(x="Localidade", y="Ano", color="Nota"),
                color_continuous_scale=["white", "darkblue"],
                range_color=(0, 500),
                aspect="auto"
            )

            fig.data[0].text = df.values.astype(int)
            fig.data[0].texttemplate = "%{text}"
            fig.data[0].textfont = dict(color="black", size=12)

            fig.update_yaxes(autorange="reversed")
            fig.update_traces(textfont=dict(size=20))

            st.plotly_chart(fig, use_container_width=True)

        exp = st.expander("Médias por modalidade de ensino")
        with exp:
            anos = ["2019", "2023"]
            modalidades = ["Regular", "EJA", "Educação Especial", "Sem informação"]

            np.random.seed(42)
            valores = np.random.randint(100, 501, size=(len(anos), len(modalidades)))

            df = pd.DataFrame(valores, index=anos, columns=modalidades)

            fig = px.imshow(
                df.values,
                x=df.columns.tolist(),
                y=df.index.tolist(),
                labels=dict(x="Modalidade", y="Ano", color="Nota"),
                color_continuous_scale=["white", "darkblue"],
                range_color=(0, 500),
                aspect="auto"
            )

            fig.data[0].text = df.values.astype(int)
            fig.data[0].texttemplate = "%{text}"
            fig.data[0].textfont = dict(color="black", size=12)

            fig.update_yaxes(autorange="reversed")
            fig.update_traces(textfont=dict(size=20))

            st.plotly_chart(fig, use_container_width=True)

with tab4:
    exp = st.expander("📈 Notas Médias", expanded=False)
    with exp:
        areas = {
            "CN": "Ciências da Natureza",
            "CH": "Ciências Humanas",
            "LC": "Linguagens e Códigos",
            "MT": "Matemática",
            "REDACAO": "Redação"
        }

        medias = []
        for sigla, nome in areas.items():
            col_nota = f"NU_NOTA_{sigla}"
            if col_nota in df.columns:
                df[col_nota] = pd.to_numeric(df[col_nota], errors="coerce")
                temp_soma = pd.DataFrame({
                    "NU_ANO": ["Soma Total"],
                    "Nota": [df[col_nota].sum()],
                    "Área": [nome]
                })
                medias.append(temp_soma)

        if medias:
            df_medias = pd.concat(medias)
            ordem_areas = list(areas.values())
            df_medias["Área"] = pd.Categorical(df_medias["Área"], categories=ordem_areas, ordered=True)

            col1, col2 = st.columns(2)

            with col1:
                colunas_de_notas = list(areas.keys())
                colunas_de_notas = [f"NU_NOTA_{sigla}" for sigla in colunas_de_notas]

                mapa_nomes = {f"NU_NOTA_{sigla}": nome for sigla, nome in areas.items()}

                df_longo = df.melt(
                    id_vars=['NU_ANO'],
                    value_vars=colunas_de_notas,
                    var_name='Area_Original',
                    value_name='Nota'
                )
                df_longo['Área'] = df_longo['Area_Original'].map(mapa_nomes)
                df_medias = df_longo.groupby(['NU_ANO', 'Área'])['Nota'].mean().reset_index()
                df_plot = df_medias[df_medias["NU_ANO"].isin([2019, 2023])].copy()

                df_media = (
                    df_plot.groupby("Área")["Nota"]
                    .mean()
                    .reset_index()
                )

                cores_areas = {
                    "Ciências da Natureza": "#1f77b4",  # azul
                    "Ciências Humanas": "#ff7f0e",  # laranja
                    "Linguagens e Códigos": "#2ca02c",  # verde
                    "Matemática": "#d62728",  # vermelho
                    "Redação": "#9467bd"  # roxo
                }

                fig_medias = px.bar(
                    df_media, x="Área", y="Nota",
                    text="Nota",
                    title="Média das Notas por Área (2019 + 2023)",
                    category_orders={
                        "Área": ["Ciências da Natureza", "Ciências Humanas", "Linguagens e Códigos", "Matemática",
                                 "Redação"]
                    },
                    color="Área",
                    color_discrete_map=cores_areas
                )
                fig_medias.update_traces(texttemplate="%{text:.0f}", textposition="inside")
                fig_medias.update_yaxes(tickformat="d")
                fig_medias.update_layout(showlegend=False)
                st.plotly_chart(fig_medias, use_container_width=True)

            with col2:
                colunas_de_notas = list(areas.keys())
                colunas_de_notas = [f"NU_NOTA_{sigla}" for sigla in colunas_de_notas]

                mapa_nomes = {f"NU_NOTA_{sigla}": nome for sigla, nome in areas.items()}

                df_longo = df.melt(
                    id_vars=['NU_ANO'],
                    value_vars=colunas_de_notas,
                    var_name='Area_Original',
                    value_name='Nota'
                )
                df_longo['Área'] = df_longo['Area_Original'].map(mapa_nomes)

                df_medias = df_longo.groupby(['NU_ANO', 'Área'])['Nota'].mean().reset_index()
                df_plot = df_medias[df_medias["NU_ANO"].isin([2019, 2023])]
                df_plot['NU_ANO'] = df_plot['NU_ANO'].astype(str)

                fig = px.bar(
                    df_plot, x="Área", y="Nota",
                    color="NU_ANO", barmode="group", text="Nota",
                    title="Médias por Área (2019 vs 2023)",
                    category_orders={
                        "Área": ["Ciências da Natureza", "Ciências Humanas", "Linguagens e Códigos", "Matemática",
                                 "Redação"],
                        "NU_ANO": ["2019", "2023"]
                    },
                    labels={"NU_ANO": "Ano"}
                )

                fig.update_traces(
                    texttemplate="%{text:.0f}",
                    textposition="inside",
                    textangle=0,  # vertical
                    insidetextanchor="end",
                    textfont={"size": 16, "color": "white"}
                )

                fig.update_layout(uniformtext_minsize=10, uniformtext_mode="hide")
                fig.update_yaxes(tickformat="d")
                st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------BOXPLOTS-----------------------------------
    exp = st.expander("📦 Boxplots", expanded=False)
    with exp:
        notas_cols = []

        cols = st.columns(3)
        cols.extend(st.columns(2))

        ordem_siglas = ["LC", "CH", "REDACAO", "CN", "MT"]
        ordem_areas = [
            "Ciências da Natureza",
            "Linguagens e Códigos",
            "Redação",
            "Ciências Humanas",
            "Matemática"
        ]

        for sigla in ordem_siglas:
            nome = areas.get(sigla)
            col_nota = f"NU_NOTA_{sigla}"
            if nome and col_nota in df.columns:
                with cols[0]:
                    df[col_nota] = pd.to_numeric(df[col_nota], errors="coerce")
                    st.subheader(f"{nome}")
                    fig = px.box(
                        df,
                        x="NU_ANO",
                        y=col_nota,
                        points="all",
                        title=f"{nome} por ano",
                        labels={col_nota: "Nota"}
                    )
                    fig.update_yaxes(tickformat="d")
                    st.plotly_chart(fig, use_container_width=True)
                    notas_cols.append(col_nota)
            del cols[0]

        if notas_cols:
            df_long = df.melt(
                id_vars=["NU_ANO"],
                value_vars=notas_cols,
                var_name="Área",
                value_name="Nota"
            )
            df_long["Área"] = df_long["Área"].str.replace("NU_NOTA_", "")
            df_long["Área"] = df_long["Área"].map(areas)

            df_long["Área"] = pd.Categorical(df_long["Área"], categories=ordem_areas, ordered=True)

            st.subheader("Boxplots gerais por área (2019 e 2023 juntos)")
            fig_all = px.box(
                df_long,
                x="Área",
                y="Nota",
                color="NU_ANO",
                points="all",
                title="Comparação de notas por área",
                color_discrete_sequence=px.colors.qualitative.Set2,
                category_orders={"Área": ordem_areas}
            )
            fig_all.update_yaxes(tickformat="d")
            st.plotly_chart(fig_all, use_container_width=True)

            st.subheader("Boxplots gerais por área (2019 e 2023 juntos)")
            fig_all = px.box(
                df_long,
                x="Área",
                y="Nota",
                color="NU_ANO",
                points="all",
                title="Comparação de notas por área",
                color_discrete_sequence=px.colors.qualitative.Set2
            )

with tab4:
    def heatmaps(df):
        with st.expander("Heatmaps", expanded=False):
            notas_cols = {
                "Ciências da Natureza": "NU_NOTA_CN",
                "Ciências Humanas": "NU_NOTA_CH",
                "Ling. e Códigos": "NU_NOTA_LC",
                "Matematica": "NU_NOTA_MT",
                "Redação": "NU_NOTA_REDACAO"
            }

            rows = []
            for area, col in notas_cols.items():
                if col in df.columns:
                    for ano in sorted(df["NU_ANO"].unique()):
                        sub = df[df["NU_ANO"] == ano]
                        media = pd.to_numeric(sub[col], errors="coerce").mean(skipna=True)
                        rows.append(
                            {"Area": area, "Ano": int(ano), "Media": float(media) if not np.isnan(media) else np.nan})

            if not rows:
                st.warning("Não foi possível calcular heatmaps a partir de colunas de nota. Mostrando exemplo.")
                df_small = pd.DataFrame({
                    ("Médias gerais", "2019"): [1, 5, 3, 7],
                    ("Médias gerais", "2023"): [10, 20, 15, 25],
                })
                df_small.columns = pd.MultiIndex.from_tuples(df_small.columns)
                df_small["Dependência"] = ["Federal", "Estadual", "Municipal", "Privada"]
                df_small.set_index("Dependência", inplace=True)
                fig = px.imshow(np.hstack([df_small[("Médias gerais", "2019")].values.reshape(-1, 1),
                                           df_small[("Médias gerais", "2023")].values.reshape(-1, 1)]),
                                x=["2019", "2023"], y=df_small.index, text_auto=True, aspect="auto",
                                title="Heatmap exemplo (Médias gerais)")
                st.plotly_chart(fig, use_container_width=True)
                return

            df_med = pd.DataFrame(rows)
            pivot = df_med.pivot(index="Area", columns="Ano", values="Media")
            fig = px.imshow(pivot, text_auto=".1f", aspect="auto", title="Heatmap: média por área (2019 vs 2023)")
            st.plotly_chart(fig, use_container_width=True)

            if "TP_DEPENDENCIA" in df.columns:
                col_depend = "TP_DEPENDENCIA"

                dep_rows = []
                for dep in df[col_depend].dropna().unique():
                    for area, col in notas_cols.items():
                        if col in df.columns:
                            sub = df[(df[col_depend] == dep)]
                            media = pd.to_numeric(sub[col], errors="coerce").mean(skipna=True)
                            dep_rows.append({"Dependencia": dep, "Area": area,
                                             "Media": float(media) if not np.isnan(media) else np.nan})
                if dep_rows:
                    df_dep = pd.DataFrame(dep_rows)
                    pivot2 = df_dep.pivot(index="Dependencia", columns="Area", values="Media")
                    fig2 = px.imshow(pivot2, text_auto=".1f", aspect="auto",
                                     title="Heatmap: média por Dependência x Área")
                    st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info(
                    "Coluna 'TP_DEPENDENCIA' não encontrada — não foi possível gerar o heatmap detalhado por dependência.")


    def main():
        st.sidebar.header("Controle do App")

        path2019 = st.sidebar.text_input("Caminho CSV 2019", value="MICRODADOS_ITA_2019_FILTRADO.csv")
        path2023 = st.sidebar.text_input("Caminho CSV 2023", value="MICRODADOS_ITA_2023_FILTRADO.csv")

        try:
            df = carregar_dados(path2019=path2019, path2023=path2023)
        except FileNotFoundError as e:
            st.error(f"Arquivo não encontrado: {e}")
            return

        df = filtros(df.copy())

        titulo()
        st.write("Qtd. total (após filtros):", int(len(df)))

        inscritos(df)
        presenca(df)
        medias_por_area(df)
        boxplot_por_area(df)
        heatmaps(df)

        df_small = pd.DataFrame({
            ("Médias gerais", "2019"): [1, 5, 3, 7],
            ("Médias gerais", "2023"): [10, 20, 15, 25],
            ("Qtd. participantes", "2019"): [100, 120, 110, 130],
            ("Qtd. participantes", "2023"): [100, 120, 110, 130],
        })
        df_small.columns = pd.MultiIndex.from_tuples(df_small.columns)
        df_small["Dependência"] = ["Federal", "Estadual", "Municipal", "Privada"]
        df_small.set_index("Dependência", inplace=True)
        styled_df = df_small.style.background_gradient(axis=0, cmap="YlGn")
        st.dataframe(styled_df)


    # NOTAS POR ÁREA
    st.markdown("---")
    with st.expander("🎯 Faixa de Notas por Área e Geral", expanded=False):

        bins = [0, 200, 400, 600, 800, 1000]
        labels = ["0–200", "201–400", "401–600", "601–800", "801–1000"]

        faixa_data = []
        for sigla, nome in areas.items():
            col_nota = f"NU_NOTA_{sigla}"
            if col_nota in df.columns:
                df_temp = df.copy()
                df_temp["Área"] = nome
                df_temp["Faixa"] = pd.cut(df_temp[col_nota], bins=bins, labels=labels, include_lowest=True)
                faixa_data.append(df_temp[["Área", "Faixa"]])

        if faixa_data:
            df_faixa = pd.concat(faixa_data)
            faixa_counts = df_faixa.value_counts(["Área", "Faixa"]).reset_index(name="Quantidade")

            fig_faixa_area = px.bar(
                faixa_counts,
                x="Faixa",
                y="Quantidade",
                color="Área",
                barmode="group",
                title="Distribuição de faixas de notas por área",
                category_orders={"Faixa": labels}
            )
            st.plotly_chart(fig_faixa_area, use_container_width=True)
        else:
            st.warning("Não há dados de notas disponíveis para gerar o gráfico de faixas.")

    # PARTICIPANTES POR ESCOLA
    st.markdown("---")
    st.subheader("🏫 Quantidade de Participantes por Administração de Escola (Percentual por Ano)")

    if "NU_ANO" in df.columns and "TP_DEPENDENCIA_ADM_ESC" in df.columns:
        df_escola = df[["NU_ANO", "TP_DEPENDENCIA_ADM_ESC"]].dropna()

        mapa_escolas = {
            "1": "Federal",
            "2": "Estadual",
            "3": "Municipal",
            "4": "Privada",
            1: "Federal",
            2: "Estadual",
            3: "Municipal",
            4: "Privada"
        }

        df_escola["Tipo_Escola"] = df_escola["TP_DEPENDENCIA_ADM_ESC"].map(mapa_escolas)

        contagem = df_escola.value_counts(["NU_ANO", "Tipo_Escola"]).reset_index(name="Quantidade")

        contagem["Percentual"] = contagem.groupby("NU_ANO")["Quantidade"].transform(lambda x: (x / x.sum()) * 100)

        # ------------------------------------------ GRÁFICO DE BARRAS -----------------------------------------
        st.markdown("#### Distribuição Percentual por Tipo de Escola e Ano")
        fig_bar = px.bar(
            contagem,
            x="Tipo_Escola",
            y="Percentual",
            color="Tipo_Escola",
            facet_col="NU_ANO",
            text_auto=".1f",
            labels={"Tipo_Escola": "Tipo de Escola", "Percentual": "Percentual (%)"},
            title="Percentual de Participantes por Administração de Escola (por Ano)"
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

        # --- GRÁFICO DE PIZZA (SELETOR MANUAL) ---
        anos = sorted(contagem["NU_ANO"].unique())
        ano_escolhido = st.selectbox("Selecione o ano para visualizar o gráfico de pizza:", anos)

        dados_ano = contagem[contagem["NU_ANO"] == ano_escolhido]
        fig_pizza = px.pie(
            dados_ano,
            names="Tipo_Escola",
            values="Percentual",
            hole=0.4,
            title=f"Distribuição Percentual de Participantes por Tipo de Escola - {ano_escolhido}"
        )
        fig_pizza.update_traces(textinfo="percent+label", textfont_size=14)
        st.plotly_chart(fig_pizza, use_container_width=True)

        # --- NOVO TRECHO: GRÁFICOS DE PIZZA PARA TODOS OS ANOS (RELATIVOS) ---
        st.markdown("#### Comparativo Percentual entre os Anos (Gráficos de Pizza)")
        colunas = st.columns(len(anos))  # Cria uma coluna para cada ano

        for i, ano in enumerate(anos):
            dados_ano_relativo = contagem[contagem["NU_ANO"] == ano]

            fig_pizza_rel = px.pie(
                dados_ano_relativo,
                names="Tipo_Escola",
                values="Percentual",
                hole=0.4,
                title=f"{ano}",
                color="Tipo_Escola",
            )
            fig_pizza_rel.update_traces(textinfo="percent+label", textfont_size=14)
            fig_pizza_rel.update_layout(showlegend=(i == 0))  # Legenda apenas no primeiro gráfico

            with colunas[i]:
                st.plotly_chart(fig_pizza_rel, use_container_width=True)

    else:
        st.warning("As colunas 'NU_ANO' e 'TP_DEPENDENCIA_ADM_ESC' não foram encontradas no CSV.")

    exp = st.expander("📦 Boxplots", expanded=True)  # -------BOXPLOTS
    with exp:
        notas_cols = []

        cols = st.columns(3)
        cols.extend(st.columns(2))

        ordem_siglas = ["LC", "CH", "REDACAO", "CN", "MT"]
        ordem_areas = [
            "Ciências da Natureza",
            "Linguagens e Códigos",
            "Redação",
            "Ciências Humanas",
            "Matemática"
        ]

        for sigla in ordem_siglas:
            nome = areas.get(sigla)
            col_nota = f"NU_NOTA_{sigla}"
            if nome and col_nota in df.columns:
                with cols[0]:
                    df[col_nota] = pd.to_numeric(df[col_nota], errors="coerce")
                    st.subheader(f"{nome}")
                    fig = px.box(
                        df,
                        x="NU_ANO",
                        y=col_nota,
                        points="all",
                        title=f"{nome} por ano",
                        labels={col_nota: "Nota"}
                    )
                    fig.update_yaxes(tickformat="d")
                    st.plotly_chart(fig, use_container_width=True)
                    notas_cols.append(col_nota)
            del cols[0]

        if notas_cols:
            df_long = df.melt(
                id_vars=["NU_ANO"],
                value_vars=notas_cols,
                var_name="Área",
                value_name="Nota"
            )
            df_long["Área"] = df_long["Área"].str.replace("NU_NOTA_", "")
            df_long["Área"] = df_long["Área"].map(areas)

            df_long["Área"] = pd.Categorical(df_long["Área"], categories=ordem_areas, ordered=True)

            st.subheader("Boxplots gerais por área (2019 e 2023 juntos)")
            fig_all = px.box(
                df_long,
                x="Área",
                y="Nota",
                color="NU_ANO",
                points="all",
                title="Comparação de notas por área",
                color_discrete_sequence=px.colors.qualitative.Set2,
                category_orders={"Área": ordem_areas}
            )
            fig_all.update_yaxes(tickformat="d")
            st.plotly_chart(fig_all, use_container_width=True)

            st.subheader("Boxplots gerais por área (2019 e 2023 juntos)")
            fig_all = px.box(
                df_long,
                x="Área",
                y="Nota",
                color="NU_ANO",
                points="all",
                title="Comparação de notas por área",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig_all, use_container_width=True)

    # HEATMAP
    st.markdown("---")
    st.subheader("📌 Heatmap de Notas por Área e Ano")

    colunas_notas = {
        "Ciências da Natureza": "NU_NOTA_CN",
        "Ciências Humanas": "NU_NOTA_CH",
        "Linguagens e Códigos": "NU_NOTA_LC",
        "Matemática": "NU_NOTA_MT",
        "Redação": "NU_NOTA_REDACAO"
    }

    # Converter colunas de notas para numérico
    for col in colunas_notas.values():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Verificar se há dados disponíveis
    areas_disponiveis = []
    for area, coluna in colunas_notas.items():
        if coluna in df.columns and df[coluna].notna().any():
            areas_disponiveis.append(area)

    if not areas_disponiveis:
        st.warning("Não há dados de notas disponíveis para gerar o heatmap.")
        st.stop()

    # Calcular médias reais por área e ano
    linhas = []
    for area, coluna in colunas_notas.items():
        if coluna in df.columns and df[coluna].notna().any():
            medias = (
                df.groupby("NU_ANO")[coluna]
                .mean()
                .reset_index(name="Média")
            )
            # Converter para porcentagem da nota máxima (1000 pontos)
            medias["Média_Percentual"] = (medias["Média"] / 1000) * 100
            medias["Área"] = area
            linhas.append(medias)

    if linhas:
        df_medias = pd.concat(linhas)

        # Criar pivot table para o heatmap (usando porcentagens)
        pivot_percent = df_medias.pivot(index="Área", columns="NU_ANO", values="Média_Percentual")
        pivot_absoluto = df_medias.pivot(index="Área", columns="NU_ANO", values="Média")

        # Ordenar áreas de forma consistente
        ordem_areas = ["Ciências da Natureza", "Ciências Humanas", "Linguagens e Códigos", "Matemática", "Redação"]
        pivot_percent = pivot_percent.reindex(ordem_areas, fill_value=np.nan)
        pivot_absoluto = pivot_absoluto.reindex(ordem_areas, fill_value=np.nan)

        # Criar heatmap com dados em porcentagem
        fig = px.imshow(
            pivot_percent,
            text_auto=".1f",
            color_continuous_scale="RdYlBu_r",  # Escala de cores invertida (vermelho para baixo, azul para alto)
            title="Heatmap das Médias por Área e Ano (em % da nota máxima)",
            aspect="auto",
            labels=dict(color="Percentual (%)")
        )

        fig.update_layout(
            xaxis_title="Ano",
            yaxis_title="Área",
            coloraxis_colorbar_title="Percentual (%)"
        )

        st.plotly_chart(fig, use_container_width=True)

        # Mostrar tabela com valores em porcentagem e absoluto
        st.subheader("📊 Tabela de Médias Detalhadas")

        # Criar DataFrame combinado
        tabela_combinada = pd.DataFrame()
        for area in ordem_areas:
            if area in pivot_percent.index:
                for ano in sorted(pivot_percent.columns):
                    perc = pivot_percent.loc[area, ano]
                    absol = pivot_absoluto.loc[area, ano]
                    if not pd.isna(perc) and not pd.isna(absol):
                        tabela_combinada.loc[area, f"{ano} (%)"] = f"{perc:.1f}%"
                        tabela_combinada.loc[area, f"{ano}"] = f"{absol:.0f}"

        st.dataframe(tabela_combinada, use_container_width=True)

        # Estatísticas adicionais
        st.subheader("📈 Estatísticas Adicionais")
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Percentual médio geral por ano:**")
            media_ano = pivot_percent.mean()
            for ano in sorted(media_ano.index):
                st.write(f"{ano}: {media_ano[ano]:.1f}%")

        with col2:
            st.write("**Percentual médio geral por área:**")
            media_area = pivot_percent.mean(axis=1)
            for area in ordem_areas:
                if area in media_area.index:
                    st.write(f"{area}: {media_area[area]:.1f}%")

        # Adicionar referência
        st.info("📌 Referência: 100% = 1000 pontos (nota máxima do ENEM)")
    else:
        st.warning("Não foi possível calcular as médias para o heatmap.")


