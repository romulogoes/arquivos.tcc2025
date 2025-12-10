import streamlit as st
import random
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random
import os
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns


# Função para carregar dados otimizados do ENEM (muito mais rápido)
def carregar_dados_enem_otimizado():
    """
    Carrega dados pré-processados de Itacoatiara (muito mais rápido)
    """
    try:
        print("Carregando dados otimizados de Itacoatiara...")

        # Tentar carregar arquivo combinado primeiro
        if os.path.exists("itacoatiara_completo.csv"):
            df_completo = pd.read_csv("itacoatiara_completo.csv", sep=';', encoding='latin1')
            print(f"Carregado arquivo combinado: {len(df_completo)} estudantes")

            # Separar por ano
            df_2019 = df_completo[df_completo['NU_ANO'] == 2019].copy()
            df_2023 = df_completo[df_completo['NU_ANO'] == 2023].copy()

            print(f"2019: {len(df_2019)} estudantes")
            print(f"2023: {len(df_2023)} estudantes")

            return df_completo, df_2019, df_2023

        # Se não existir combinado, carregar individuais
        elif os.path.exists("itacoatiara_2019.csv") and os.path.exists("itacoatiara_2023.csv"):
            df_2019 = pd.read_csv("itacoatiara_2019.csv", sep=';', encoding='latin1')
            df_2023 = pd.read_csv("itacoatiara_2023.csv", sep=';', encoding='latin1')
            df_completo = pd.concat([df_2019, df_2023], ignore_index=True)

            print(f"Carregados arquivos individuais:")
            print(f"2019: {len(df_2019)} estudantes")
            print(f"2023: {len(df_2023)} estudantes")
            print(f"Total: {len(df_completo)} estudantes")

            return df_completo, df_2019, df_2023

        else:
            print("Arquivos otimizados não encontrados. Usando método original.")
            return carregar_dados_enem_reais()

    except Exception as e:
        print(f"Erro ao carregar dados otimizados: {e}")
        return None, None, None


st.set_page_config(page_title="Dashboard ENEM Itacoatiara", layout="wide")

# TESTE: Carregar dados otimizados do ENEM
print("=== INICIANDO CARREGAMENTO DE DADOS OTIMIZADOS ===")
df_itacoatiara, df_2019_itacoatiara, df_2023_itacoatiara = carregar_dados_enem_otimizado()

if df_itacoatiara is not None:
    print("=== DADOS REAIS CARREGADOS COM SUCESSO ===")
    print(f"Total geral: {len(df_itacoatiara)} estudantes")
    print(f"2019: {len(df_2019_itacoatiara)} estudantes")
    print(f"2023: {len(df_2023_itacoatiara)} estudantes")
else:
    print("=== USANDO DADOS SIMULADOS (FALHA AO CARREGAR DADOS REAIS) ===")

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
            EDUCA <span style='color: #2E8B57;'>ITA</span>
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
    ["2019", "2023", "2019 e 2023"], index=2, key="selectbox_anos"
)
selecionar_todos = st.sidebar.checkbox("Incluir os estudantes sem escola associada", value=True)
if not selecionar_todos:
    df = df[df["CO_MUNICIPIO_ESC"] == "1301902"]
else:
    # Quando selecionar_todos = True, mantém todos (incluindo NaN)
    pass

df["NU_ANO"] = (
    df["NU_ANO"]
    .astype(str)
    .str.extract(r"(20\d{2})")  # pega apenas anos válidos
    .astype(float)
    .astype("Int64")
)

# Converter colunas importantes para numérico ANTES dos filtros
df["IN_TREINEIRO"] = pd.to_numeric(df["IN_TREINEIRO"], errors="coerce")

if campo_anos != "2019 e 2023":
    ano_escolhido = int(campo_anos)
    df = df[df["NU_ANO"] == ano_escolhido]
else:
    # Quando seleciona "2019 e 2023", garantir que só inclua esses anos
    df = df[df["NU_ANO"].isin([2019, 2023])]

df_base_para_metricas = df.copy()

# Converter colunas importantes para numérico no DataFrame base
df_base_para_metricas["IN_TREINEIRO"] = pd.to_numeric(df_base_para_metricas["IN_TREINEIRO"], errors="coerce")

# FILTROS PARA OS TREINEIROS
st.sidebar.markdown("---")
st.sidebar.header("Filtros Adicionais")

# Mostrar estatísticas reais (já convertido para numérico)
total_treineiros = len(df[df["IN_TREINEIRO"] == 1])
total_regulares = len(df[df["IN_TREINEIRO"] == 0])

incluir_treineiros = st.sidebar.checkbox(
    "Incluir estudantes treineiros", value=True
)
if not incluir_treineiros:
    df = df[df["IN_TREINEIRO"] == 0]

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

mapa_q011 = {
    "A": "Não tem",
    "B": "1 (um)",
    "C": "2 (dois)",
    "D": "3 (três)",
    "E": "4 (quatro) ou mais"
}

mapa_q019 = {
    "A": "Não tem",
    "B": "1 (um)",
    "C": "2 (dois)",
    "D": "3 (três)",
    "E": "4 (quatro) ou mais"
}

mapa_q022 = {
    "A": "Não tem",
    "B": "1 (um)",
    "C": "2 (dois)",
    "D": "3 (três)",
    "E": "4 (quatro) ou mais"
}

mapa_q023 = {
    "A": "Não",
    "B": "Sim"
}

mapa_q025 = {
    "A": "Não",
    "B": "Sim"
}

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

    if "TP_SEXO" in df.columns:
        df["TP_SEXO_DESC"] = df["TP_SEXO"].map(mapa_sexo).fillna(df["TP_SEXO"])
        opcoes = sorted(df["TP_SEXO_DESC"].dropna().unique().tolist())
        sexo_sel = st.multiselect("Sexo", options=opcoes, default=[], placeholder="Selecione")
        if sexo_sel:
            inv = {v: k for k, v in mapa_sexo.items()}
            codigos_sel = [inv[s] if s in inv else s for s in sexo_sel]
            df = df[df["TP_SEXO"].isin(codigos_sel) | df.get("TP_SEXO_DESC", pd.Series()).isin(sexo_sel)]

    if "TP_ESTADO_CIVIL" in df.columns:
        df["TP_ESTADO_CIVIL_DESC"] = df["TP_ESTADO_CIVIL"].map(mapa_estado_civil).fillna(df["TP_ESTADO_CIVIL"])
        opcoes = sorted(df["TP_ESTADO_CIVIL_DESC"].dropna().unique().tolist())
        estado_sel = st.multiselect("Estado civil", options=opcoes, default=[], placeholder="Selecione")
        if estado_sel:
            inv = {v: k for k, v in mapa_estado_civil.items()}
            codigos_sel = [inv[s] if s in inv else s for s in estado_sel]
            df = df[
                df["TP_ESTADO_CIVIL"].isin(codigos_sel) | df.get("TP_ESTADO_CIVIL_DESC", pd.Series()).isin(estado_sel)]

    if "TP_COR_RACA" in df.columns:
        df["TP_COR_RACA_DESC"] = df["TP_COR_RACA"].map(mapa_cor_raca).fillna(df["TP_COR_RACA"])
        opcoes = sorted(df["TP_COR_RACA_DESC"].dropna().unique().tolist())
        raca_sel = st.multiselect("Cor/Raça", options=opcoes, default=[], placeholder="Selecione")
        if raca_sel:
            inv = {v: k for k, v in mapa_cor_raca.items()}
            codigos_sel = [inv[s] if s in inv else s for s in raca_sel]
            df = df[df["TP_COR_RACA"].isin(codigos_sel) | df.get("TP_COR_RACA_DESC", pd.Series()).isin(raca_sel)]

    if "TP_FAIXA_ETARIA" in df.columns:
        df["TP_FAIXA_ETARIA_DESC"] = df["TP_FAIXA_ETARIA"].map(mapa_faixa_etaria).fillna(df["TP_FAIXA_ETARIA"])
        opcoes = sorted(df["TP_FAIXA_ETARIA_DESC"].dropna().unique().tolist(), key=lambda x: (len(x), x))
        faixa_sel = st.multiselect("Faixa etária", options=opcoes, default=[], placeholder="Selecione")
        if faixa_sel:
            inv = {v: k for k, v in mapa_faixa_etaria.items()}
            codigos_sel = [inv[s] if s in inv else s for s in faixa_sel]
            df = df[
                df["TP_FAIXA_ETARIA"].isin(codigos_sel) | df.get("TP_FAIXA_ETARIA_DESC", pd.Series()).isin(faixa_sel)]

    mapa_renda = {
        "A": 0, "B": 1.5, "C": 2, "D": 3, "E": 4, "F": 5,
        "G": 7, "H": 10, "I": 12, "J": 15, "K": 20.5
    }

    # Mapeamento oficial do ENEM para Q006 (renda familiar mensal)
    mapa_renda_descritivo = {
        "A": "Nenhuma renda",
        "B": "Até R$ 998,00",
        "C": "De R$ 998,01 até R$ 1.497,00",
        "D": "De R$ 1.497,01 até R$ 1.996,00",
        "E": "De R$ 1.996,01 até R$ 2.495,00",
        "F": "De R$ 2.495,01 até R$ 2.994,00",
        "G": "De R$ 2.994,01 até R$ 3.992,00",
        "H": "De R$ 3.992,01 até R$ 4.990,00",
        "I": "De R$ 4.990,01 até R$ 5.988,00",
        "J": "De R$ 5.988,01 até R$ 6.986,00",
        "K": "De R$ 6.986,01 até R$ 7.984,00",
        "L": "De R$ 7.984,01 até R$ 8.982,00",
        "M": "De R$ 8.982,01 até R$ 9.980,00",
        "N": "De R$ 9.980,01 até R$ 11.976,00",
        "O": "De R$ 11.976,01 até R$ 14.970,00",
        "P": "De R$ 14.970,01 até R$ 19.960,00",
        "Q": "Mais de R$ 19.960,00"
    }
    if "Q006" in df.columns:
        # Converter Q006 para string caso esteja como numérico
        df["Q006"] = df["Q006"].astype(str).str.strip()
        df["RENDA_SM"] = df["Q006"].map(mapa_renda)

        # Verificar se há dados de renda válidos
        if df["RENDA_SM"].notna().any():
            min_renda = float(df["RENDA_SM"].min())
            max_renda = float(df["RENDA_SM"].max())

            # Slider para faixa de renda em salários mínimos
            renda_range = st.slider(
                "Selecione a faixa de renda (salários mínimos)",
                min_value=min_renda,
                max_value=max_renda,
                value=(min_renda, max_renda),
                step=0.5,
                format="%.1f SM"
            )

            # Aplicar filtro mantendo dados sem informação de renda
            df = df[
                (df["RENDA_SM"] >= renda_range[0]) &
                (df["RENDA_SM"] <= renda_range[1]) |
                (df["RENDA_SM"].isna())
                ]

    st.markdown(f"**Total após filtros gerais:** {len(df):,}")

with st.sidebar.expander("Escola", expanded=False):
    st.subheader("Informações sobre a Escola (dados reais)")

    if "TP_DEPENDENCIA_ADM_ESC" in df.columns:
        df["TP_DEPENDENCIA_ADM_ESC_DESC"] = df["TP_DEPENDENCIA_ADM_ESC"].map(dependencia_dict).fillna(
            df["TP_DEPENDENCIA_ADM_ESC"])
        opcoes = sorted(df["TP_DEPENDENCIA_ADM_ESC_DESC"].dropna().unique().tolist())
        dependencia_sel = st.multiselect("Tipo de administração da escola", options=opcoes, default=[],
                                         placeholder="Selecione")
        if dependencia_sel:
            inv = {v: k for k, v in dependencia_dict.items()}
            codigos_sel = [inv[s] if s in inv else s for s in dependencia_sel]
            df = df[df["TP_DEPENDENCIA_ADM_ESC"].isin(codigos_sel) | df.get("TP_DEPENDENCIA_ADM_ESC_DESC",
                                                                            pd.Series()).isin(dependencia_sel)]

    if "TP_ENSINO" in df.columns:
        df["TP_ENSINO_DESC"] = df["TP_ENSINO"].map(ensino_dict).fillna("Sem informação")

        # Mostrar todas as opções, mesmo que não tenha dados
        todas_opcoes = ["Ensino Regular", "Educação Especial - Modalidade Substitutiva", "EJA", "Sem informação"]

        ensino_sel = st.multiselect("Tipo de ensino", options=todas_opcoes, default=[], placeholder="Selecione")
        if ensino_sel:
            inv = {v: k for k, v in ensino_dict.items()}
            codigos_sel = [inv[s] if s in inv else s for s in ensino_sel]
            # Incluir "Sem informação" no filtro
            df = df[df["TP_ENSINO"].isin(codigos_sel) | (df["TP_ENSINO_DESC"] == "Sem informação") & (
                        "Sem informação" in ensino_sel)]

    if "TP_LOCALIZACAO_ESC" in df.columns:
        df["TP_LOCALIZACAO_ESC_DESC"] = df["TP_LOCALIZACAO_ESC"].map(localizacao_dict).fillna(
            df["TP_LOCALIZACAO_ESC"])
        opcoes = sorted(df["TP_LOCALIZACAO_ESC_DESC"].dropna().unique().tolist())
        local_sel = st.multiselect("Localidade da escola", options=opcoes, default=[], placeholder="Selecione")
        if local_sel:
            inv = {v: k for k, v in localizacao_dict.items()}
            codigos_sel = [inv[s] if s in inv else s for s in local_sel]
            df = df[df["TP_LOCALIZACAO_ESC"].isin(codigos_sel) | df.get("TP_LOCALIZACAO_ESC_DESC", pd.Series()).isin(
                local_sel)]

    if "NO_ESCOLA" in df.columns:
        opcoes = sorted(df["NO_ESCOLA"].dropna().unique().tolist())
        escola_sel = st.multiselect("Nome da escola", options=opcoes, default=[], placeholder="Selecione")
        if escola_sel:
            df = df[df["NO_ESCOLA"].isin(escola_sel)]
    if "NO_MUNICIPIO_ESC" in df.columns:
        opcoes = sorted(df["NO_MUNICIPIO_ESC"].dropna().unique().tolist())
        mun_sel = st.multiselect("Município (escola)", options=opcoes, default=[], placeholder="Selecione")
        if mun_sel:
            df = df[df["NO_MUNICIPIO_ESC"].isin(mun_sel)]

    st.markdown(f"**Total após filtros de escola:** {len(df):,}")

with st.sidebar.expander("Bens e Moradia", expanded=False):
    st.subheader("Bens e Moradia (dados reais)")

    # Filtro Q010 - Carro
    if "Q010" in df.columns:
        df["Q010_DESC"] = df["Q010"].map(mapa_q011).fillna(df["Q010"])
        opcoes = sorted(df["Q010_DESC"].dropna().unique().tolist())
        carro_sel = st.multiselect("Carro", options=opcoes, default=[], placeholder="Selecione")
        if carro_sel:
            inv = {v: k for k, v in mapa_q011.items()}
            codigos_sel = [inv[s] if s in inv else s for s in carro_sel]
            df = df[df["Q010"].isin(codigos_sel) | df.get("Q010_DESC", pd.Series()).isin(carro_sel)]

    # Filtro Q022 - Celular
    if "Q022" in df.columns:
        df["Q022_DESC"] = df["Q022"].map(mapa_q022).fillna(df["Q022"])
        opcoes = sorted(df["Q022_DESC"].dropna().unique().tolist())
        q022_sel = st.multiselect("Celular", options=opcoes, default=[], placeholder="Selecione")
        if q022_sel:
            inv = {v: k for k, v in mapa_q022.items()}
            codigos_sel = [inv[s] if s in inv else s for s in q022_sel]
            df = df[df["Q022"].isin(codigos_sel) | df.get("Q022_DESC", pd.Series()).isin(q022_sel)]

    # Filtro Q024 - Computador
    if "Q024" in df.columns:
        df["Q024_DESC"] = df["Q024"].map(mapa_computador).fillna(df["Q024"])
        opcoes = sorted(df["Q024_DESC"].dropna().unique().tolist())
        computador_sel = st.multiselect("Computador", options=opcoes, default=[], placeholder="Selecione")
        if computador_sel:
            inv = {v: k for k, v in mapa_computador.items()}
            codigos_sel = [inv[s] if s in inv else s for s in computador_sel]
            df = df[df["Q024"].isin(codigos_sel) | df.get("Q024_DESC", pd.Series()).isin(codigos_sel)]

    # Filtro Q025 - Internet
    if "Q025" in df.columns:
        df["Q025_DESC"] = df["Q025"].map(mapa_q025).fillna(df["Q025"])
        opcoes = sorted(df["Q025_DESC"].dropna().unique().tolist())
        internet_sel = st.multiselect("Internet", options=opcoes, default=[], placeholder="Selecione")
        if internet_sel:
            inv = {v: k for k, v in mapa_q025.items()}
            codigos_sel = [inv[s] if s in inv else s for s in internet_sel]
            df = df[df["Q025"].isin(codigos_sel) | df.get("Q025_DESC", pd.Series()).isin(codigos_sel)]

    # Filtro Q011 - Moto
    if "Q011" in df.columns:
        df["Q011_DESC"] = df["Q011"].map(mapa_q011).fillna(df["Q011"])
        opcoes = sorted(df["Q011_DESC"].dropna().unique().tolist())
        moto_sel = st.multiselect("Moto", options=opcoes, default=[], placeholder="Selecione")
        if moto_sel:
            inv = {v: k for k, v in mapa_q011.items()}
            codigos_sel = [inv[s] if s in inv else s for s in moto_sel]
            df = df[df["Q011"].isin(codigos_sel) | df.get("Q011_DESC", pd.Series()).isin(moto_sel)]

    # Filtro Q019 - Televisor
    if "Q019" in df.columns:
        df["Q019_DESC"] = df["Q019"].map(mapa_q019).fillna(df["Q019"])
        opcoes = sorted(df["Q019_DESC"].dropna().unique().tolist())
        tv_sel = st.multiselect("Televisor", options=opcoes, default=[], placeholder="Selecione")
        if tv_sel:
            inv = {v: k for k, v in mapa_q019.items()}
            codigos_sel = [inv[s] if s in inv else s for s in tv_sel]
            df = df[df["Q019"].isin(codigos_sel) | df.get("Q019_DESC", pd.Series()).isin(tv_sel)]

    st.markdown(f"**Total após filtros bens/moradia:** {len(df):,}")

with st.sidebar.expander("Prova", expanded=False):
    st.subheader("Informações sobre a Prova (dados reais)")

    # Filtro de Presença
    if "TP_PRESENCA_CH" in df.columns and "TP_PRESENCA_CN" in df.columns:
        # Criar coluna de status geral de presença
        df["Status_Presenca"] = np.select(
            [
                (df["TP_PRESENCA_CH"] == 1) & (df["TP_PRESENCA_CN"] == 1),
                (df["TP_PRESENCA_CH"] == 1) & (df["TP_PRESENCA_CN"] != 1),
                (df["TP_PRESENCA_CH"] != 1) & (df["TP_PRESENCA_CN"] == 1),
                (df["TP_PRESENCA_CH"] != 1) & (df["TP_PRESENCA_CN"] != 1)
            ],
            [
                "Presente nos dois dias",
                "Presente apenas no Dia 1",
                "Presente apenas no Dia 2",
                "Ausente nos dois dias"
            ],
            default="Sem informação"
        )

        opcoes_presenca = sorted(df["Status_Presenca"].dropna().unique().tolist())
        presenca_sel = st.multiselect("Presença", options=opcoes_presenca, default=[], placeholder="Selecione")
        if presenca_sel:
            df = df[df["Status_Presenca"].isin(presenca_sel)]

    # Filtro de Língua
    if "TP_LINGUA" in df.columns:
        # Mapear língua estrangeira (valores são strings)
        mapa_lingua = {
            "0": "Inglês",
            "1": "Espanhol"
        }

        df["LINGUA_DESC"] = df["TP_LINGUA"].map(mapa_lingua).fillna(df["TP_LINGUA"])
        opcoes_lingua = sorted(df["LINGUA_DESC"].dropna().unique().tolist())
        lingua_sel = st.multiselect("Língua Estrangeira", options=opcoes_lingua, default=[], placeholder="Selecione")
        if lingua_sel:
            inv = {"Inglês": "0", "Espanhol": "1"}
            codigos_sel = [inv[s] if s in inv else s for s in lingua_sel]
            df = df[df["TP_LINGUA"].isin(codigos_sel) | df.get("LINGUA_DESC", pd.Series()).isin(lingua_sel)]

    # Filtro de Redação (se houver status de redação)
    if "TP_STATUS_REDACAO" in df.columns:
        # Mapear status da redação (valores são strings)
        mapa_status_redacao = {
            "1": "Sem problemas",
            "2": "Anulada",
            "3": "Cópia textual",
            "4": "Em branco",
            "5": "Fuga ao tema",
            "6": "Não atendimento ao tipo textual",
            "7": "Texto insuficiente",
            "8": "Parte desconectada",
            "9": "Outro status"
        }

        df["STATUS_REDACAO_DESC"] = df["TP_STATUS_REDACAO"].map(mapa_status_redacao).fillna("Sem informação")

        opcoes_redacao = sorted(df["STATUS_REDACAO_DESC"].dropna().unique().tolist())
        redacao_sel = st.multiselect("Redação (status)", options=opcoes_redacao, default=[], placeholder="Selecione")
        if redacao_sel:
            inv = {v: k for k, v in mapa_status_redacao.items()}
            codigos_sel = [inv[s] if s in inv else s for s in redacao_sel]
            df = df[df["TP_STATUS_REDACAO"].isin(codigos_sel) | df.get("STATUS_REDACAO_DESC", pd.Series()).isin(
                redacao_sel)]

    st.markdown(f"**Total após filtros prova:** {len(df):,}")

st.header("Perspectiva de Desempenho")

tab1, tab2, tab3, tab4 = st.tabs(["📝 Inscritos", "🙋 Presença", "🧮 Notas", "📘 Médias", ])

# ------------------------------PRIMEIRA ABA: INSCRITOS (CORRIGIDA)-------------------------------

with tab1:
    total_inscritos_base = len(df_base_para_metricas)
    # Usar df filtrado para mostrar os números corretos conforme o checkbox
    total_regulares_filtrado = len(df[df["IN_TREINEIRO"] == 0])
    total_treineiros_filtrado = len(df[df["IN_TREINEIRO"] == 1])
    total_final_filtrado = len(df)

    cols = st.columns([0.2, 1, 1, 1, 1, 1])

    # Converter TP_LINGUA para numérico para cálculo correto
    df["TP_LINGUA"] = pd.to_numeric(df["TP_LINGUA"], errors="coerce")

    total_ingles_filtrado = len(df[df["TP_LINGUA"] == 0])
    total_espanhol_filtrado = len(df[df["TP_LINGUA"] == 1])

    cols[1].metric("Inscritos Base", total_final_filtrado)
    cols[2].metric("Regulares", total_regulares_filtrado)
    cols[3].metric("Treineiros", total_treineiros_filtrado)
    cols[4].metric("Língua Inglesa", total_ingles_filtrado)
    cols[5].metric("Língua Espanhola", total_espanhol_filtrado)

    # ---------------------------------------BLOCO DAS INSCRIÇÕES---------------------------------------
    st.markdown('<h4 style="margin-bottom:5px;">Gráfico de inscritos por ano</h4>', unsafe_allow_html=True)

    df_chart = df.groupby("NU_ANO").size().reset_index(name="Quantidade")
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
    # ----------------------- Parte 1: Percentuais gerais de presença em cada dia ------------------------------
    dias = {
        "Dia 1 - Ciências Humanas, Linguagens e Redação": "TP_PRESENCA_CH",
        "Dia 2 - Ciências da Natureza e Matemática": "TP_PRESENCA_CN"
    }

    if all(col in df.columns for col in dias.values()):
        # Preparar dados de presença
        for coluna in dias.values():
            df[coluna] = df[coluna].replace({
                "0": "Ausente",
                "1": "Presente",
                "2": "Eliminado"
            })

        # Criar status geral para o gráfico combinado
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

    # ----------------------- Parte 2: Gráficos detalhados por dia ------------------------------
    exp = st.expander("### Detalhes por dia de prova", expanded=False)
    with exp:
        for nome_dia, coluna in dias.items():
            if coluna not in df.columns:
                st.warning(f"Coluna {coluna} não encontrada no CSV.")
                continue

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
                st.plotly_chart(fig_pizza, use_container_width=True, key=f"pizza_{nome_dia}")

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
                st.plotly_chart(fig_barra, use_container_width=True, key=f"barra_{nome_dia}")

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

            # Função para carregar dados dos parâmetros
            def carregar_dados_parametros():
                try:
                    df_param = pd.read_csv("ITENS_PROVA_PARAMETROS.csv")
                    return df_param
                except FileNotFoundError:
                    return None


            # Função para calcular complexidade usando classificações oficiais
            def calcular_complexidade_oficial(df_param, materia, ano, tipo_complexidade="chute"):
                """
                Calcula complexidade baseada nas classificações oficiais do INEP

                Retorna: [percentual_baixa, percentual_media, percentual_alta]
                """
                if df_param is None:
                    return [33.3, 33.3, 33.4]  # Valores padrão

                # Mapear área para sigla
                area_sigla = {
                    "Ciências Humanas": "CH",
                    "Ciências da Natureza": "CN",
                    "Linguagens e Códigos": "LC",
                    "Matemática": "MT"
                }

                if materia not in area_sigla:
                    return [33.3, 33.3, 33.4]

                sigla = area_sigla[materia]

                # Filtrar por área e ano
                df_filtrado = df_param[
                    (df_param["SG_AREA"] == sigla) &
                    (df_param["NU_ANO"] == int(ano))
                    ].copy()

                if len(df_filtrado) == 0:
                    return [33.3, 33.3, 33.4]

                # Usar classificação oficial específica
                if tipo_complexidade == "chute":
                    coluna_classificacao = "CL_PARAM_C"
                elif tipo_complexidade == "discriminacao":
                    coluna_classificacao = "CL_PARAM_A"
                elif tipo_complexidade == "dificuldade":
                    coluna_classificacao = "CL_PARAM_B"
                else:
                    return [33.3, 33.3, 33.4]

                # Contar classificações
                baixa = (df_filtrado[coluna_classificacao] == "BA").sum()
                media = (df_filtrado[coluna_classificacao] == "ME").sum()
                alta = (df_filtrado[coluna_classificacao] == "AL").sum()

                total = baixa + media + alta
                if total > 0:
                    return [
                        (baixa / total) * 100,
                        (media / total) * 100,
                        (alta / total) * 100
                    ]
                else:
                    return [33.3, 33.3, 33.4]


            # Carregar dados
            df_param = carregar_dados_parametros()

            materias = [
                "Ciências Humanas",
                "Ciências da Natureza",
                "Linguagens e Códigos",
                "Matemática"
            ]

            anos = ["2019", "2023"]
            categorias = ["Baixa", "Média", "Alta"]

            # MultiIndex das colunas
            arrays = [
                [ano for ano in anos for _ in categorias],
                categorias * len(anos)
            ]
            col_index = pd.MultiIndex.from_tuples(list(zip(*arrays)), names=["Ano", "Nível"])

            # Criar abas
            tab_chute, tab_discr, tab_dific = st.tabs([
                "🎲 Facilidade de chute",
                "🤓 Discriminação entre estudantes",
                "🤯 Dificuldade de resolução"
            ])

            # ============================================================
            # 1) 🎲 FACILIDADE DE CHUTE
            # ============================================================
            with tab_chute:
                # Calcular dados usando classificações oficiais
                valores_chute = {}
                for materia in materias:
                    valores_chute[materia] = {}
                    for ano in anos:
                        valores_chute[materia][ano] = calcular_complexidade_oficial(df_param, materia, ano, "chute")

                df_chute = pd.DataFrame(index=materias, columns=col_index, dtype=float)
                df_chute.index.name = "Áreas"

                for materia in materias:
                    for ano in anos:
                        df_chute.loc[materia, ano] = valores_chute[materia][ano]

                st.dataframe(
                    df_chute.style.format("{:.1f}%").background_gradient(cmap="Blues", axis=None),
                    use_container_width=True
                )

            with tab_discr:
                # Calcular dados usando classificações oficiais
                valores_discr = {}
                for materia in materias:
                    valores_discr[materia] = {}
                    for ano in anos:
                        valores_discr[materia][ano] = calcular_complexidade_oficial(df_param, materia, ano,
                                                                                    "discriminacao")

                df_discr = pd.DataFrame(index=materias, columns=col_index, dtype=float)
                df_discr.index.name = "Áreas"

                for materia in materias:
                    for ano in anos:
                        df_discr.loc[materia, ano] = valores_discr[materia][ano]

                st.dataframe(
                    df_discr.style.format("{:.1f}%").background_gradient(cmap="Greens", axis=None),
                    use_container_width=True
                )

            with tab_dific:
                # Calcular dados usando classificações oficiais
                valores_dific = {}
                for materia in materias:
                    valores_dific[materia] = {}
                    for ano in anos:
                        valores_dific[materia][ano] = calcular_complexidade_oficial(df_param, materia, ano,
                                                                                    "dificuldade")

                df_dific = pd.DataFrame(index=materias, columns=col_index, dtype=float)
                df_dific.index.name = "Áreas"

                for materia in materias:
                    for ano in anos:
                        df_dific.loc[materia, ano] = valores_dific[materia][ano]

                st.dataframe(
                    df_dific.style.format("{:.1f}%").background_gradient(cmap="Reds", axis=None),
                    use_container_width=True
                )

        exp3 = st.expander("Quantidades de questões por habilidade", expanded=False)
        with exp3:

            # Função para gerar tabela de habilidades com dados reais
            def gerar_tabela_habilidades_reais(area_sigla):
                """
                Gera tabela com habilidades reais e valores simulados baseados nos parâmetros
                """
                df_param = carregar_dados_parametros()
                if df_param is None:
                    return gerar_tabela_habilidades_simulada(area_sigla)

                # Filtrar por área
                df_area = df_param[df_param["SG_AREA"] == area_sigla].copy()

                if len(df_area) == 0:
                    return gerar_tabela_habilidades_simulada(area_sigla)

                # Mapeamento oficial das habilidades do ENEM
                # TODO: Atualizar com os nomes oficiais pesquisados pelo usuário
                habilidades_descricoes = {
                    "CN": {
                        1: "Reconhecer características ou propriedades de fenômenos ondulatórios ou oscilatórios, relacionando-os a seus usos em diferentes contextos.",
                        2: "Associar a solução de problemas de comunicação, transporte, saúde ou outro, com o correspondente desenvolvimento científico e tecnológico.",
                        3: "Confrontar interpretações científicas com interpretações baseadas no senso comum, ao longo do tempo ou em diferentes culturas.",
                        4: "Avaliar propostas de intervenção no ambiente, considerando a qualidade da vida humana ou medidas de conservação, recuperação ou utilização sustentável da biodiversidade.",
                        5: "Dimensionar circuitos ou dispositivos elétricos de uso cotidiano.",
                        6: "Relacionar informações para compreender manuais de instalação ou utilização de aparelhos, ou sistemas tecnológicos de uso comum.",
                        7: "Selecionar testes de controle, parâmetros ou critérios para a comparação de materiais e produtos, tendo em vista a defesa do consumidor, a saúde do trabalhador ou a qualidade de vida.",
                        8: "Identificar etapas em processos de obtenção, transformação, utilização ou reciclagem de recursos naturais, energéticos ou matérias-primas, considerando processos biológicos, químicos ou físicos neles envolvidos.",
                        9: "Compreender a importância dos ciclos biogeoquímicos ou do fluxo energia para a vida, ou da ação de agentes ou fenômenos que podem causar alterações nesses processos.",
                        10: "Analisar perturbações ambientais, identificando fontes, transporte e(ou) destino dos poluentes ou prevendo efeitos em sistemas naturais, produtivos ou sociais.",
                        11: "Reconhecer benefícios, limitações e aspectos éticos da biotecnologia, considerando estruturas e processos biológicos envolvidos em produtos biotecnológicos.",
                        12: "Avaliar impactos em ambientes naturais decorrentes de atividades sociais ou econômicas, considerando interesses contraditórios.",
                        13: "Reconhecer mecanismos de transmissão da vida, prevendo ou explicando a manifestação de características dos seres vivos.",
                        14: "Identificar padrões em fenômenos e processos vitais dos organismos, como manutenção do equilíbrio interno, defesa, relações com o ambiente, sexualidade, entre outros.",
                        15: "Interpretar modelos e experimentos para explicar fenômenos ou processos biológicos em qualquer nível de organização dos sistemas biológicos.",
                        16: "Compreender o papel da evolução na produção de padrões, processos biológicos ou na organização taxonômica dos seres vivos.",
                        17: "Relacionar informações apresentadas em diferentes formas de linguagem e representação usadas nas ciências físicas, químicas ou biológicas, como texto discursivo, gráficos, tabelas, relações matemáticas ou linguagem simbólica.",
                        18: "Relacionar propriedades físicas, químicas ou biológicas de produtos, sistemas ou procedimentos tecnológicos às finalidades a que se destinam.",
                        19: "Avaliar métodos, processos ou procedimentos das ciências naturais que contribuam para diagnosticar ou solucionar problemas de ordem social, econômica ou ambiental.",
                        20: "Caracterizar causas ou efeitos dos movimentos de partículas, substâncias, objetos ou corpos celestes.",
                        21: "Utilizar leis físicas e (ou) químicas para interpretar processos naturais ou tecnológicos inseridos no contexto da termodinâmica e(ou) do eletromagnetismo.",
                        22: "Compreender fenômenos decorrentes da interação entre a radiação e a matéria em suas manifestações em processos naturais ou tecnológicos, ou em suas implicações biológicas, sociais, econômicas ou ambientais.",
                        23: "Avaliar possibilidades de geração, uso ou transformação de energia em ambientes específicos, considerando implicações éticas, ambientais, sociais e/ou econômicas.",
                        24: "Utilizar códigos e nomenclatura da química para caracterizar materiais, substâncias ou transformações químicas.",
                        25: "Caracterizar materiais ou substâncias, identificando etapas, rendimentos ou implicações biológicas, sociais, econômicas ou ambientais de sua obtenção ou produção.",
                        26: "Avaliar implicações sociais, ambientais e/ou econômicas na produção ou no consumo de recursos energéticos ou minerais, identificando transformações químicas ou de energia envolvidas nesses processos.",
                        27: "Avaliar propostas de intervenção no meio ambiente aplicando conhecimentos químicos, observando riscos ou benefícios.",
                        28: "Associar características adaptativas dos organismos com seu modo de vida ou com seus limites de distribuição em diferentes ambientes, em especial em ambientes brasileiros.",
                        29: "Interpretar experimentos ou técnicas que utilizam seres vivos, analisando implicações para o ambiente, a saúde, a produção de alimentos, matérias primas ou produtos industriais.",
                        30: "Avaliar propostas de alcance individual ou coletivo, identificando aquelas que visam à preservação e a implementação da saúde individual, coletiva ou do ambiente."
                    },
                    "CH": {
                        1: "Interpretar historicamente e/ou geograficamente fontes documentais acerca de aspectos da cultura.",
                        2: "Analisar a produção da memória pelas sociedades humanas.",
                        3: "Associar as manifestações culturais do presente aos seus processos históricos.",
                        4: "Comparar pontos de vista expressos em diferentes fontes sobre determinado aspecto da cultura.",
                        5: "Identificar as manifestações ou representações da diversidade do patrimônio cultural e artístico em diferentes sociedades.",
                        6: "Interpretar diferentes representações gráficas e cartográficas dos espaços geográficos.",
                        7: "Identificar os significados histórico-geográficos das relações de poder entre as nações.",
                        8: "Analisar a ação dos estados nacionais no que se refere à dinâmica dos fluxos populacionais e no enfrentamento de problemas de ordem econômico-social.",
                        9: "Comparar o significado histórico-geográfico das organizações políticas e socioeconômicas em escala local, regional ou mundial.",
                        10: "Reconhecer a dinâmica da organização dos movimentos sociais e a importância da participação da coletividade na transformação da realidade histórico-geográfica.",
                        11: "Identificar registros de práticas de grupos sociais no tempo e no espaço.",
                        12: "Analisar o papel da justiça como instituição na organização das sociedades.",
                        13: "Analisar a atuação dos movimentos sociais que contribuíram para mudanças ou rupturas em processos de disputa pelo poder.",
                        14: "Comparar diferentes pontos de vista, presentes em textos analíticos e interpretativos, sobre situação ou fatos de natureza histórico-geográfica acerca das instituições sociais, políticas e econômicas.",
                        15: "Avaliar criticamente conflitos culturais, sociais, políticos, econômicos ou ambientais ao longo da história.",
                        16: "Identificar registros sobre o papel das técnicas e tecnologias na organização do trabalho e/ou da vida social.",
                        17: "Analisar fatores que explicam o impacto das novas tecnologias no processo de territorialização da produção.",
                        18: "Analisar diferentes processos de produção ou circulação de riquezas e suas implicações sócio-espaciais.",
                        19: "Reconhecer as transformações técnicas e tecnológicas que determinam as várias formas de uso e apropriação dos espaços rural e urbano.",
                        20: "Selecionar argumentos favoráveis ou contrários às modificações impostas pelas novas tecnologias à vida social e ao mundo do trabalho.",
                        21: "Identificar o papel dos meios de comunicação na construção da vida social.",
                        22: "Analisar as lutas sociais e conquistas obtidas no que se refere às mudanças nas legislações ou nas políticas públicas.",
                        23: "Analisar a importância dos valores éticos na estruturação política das sociedades.",
                        24: "Relacionar cidadania e democracia na organização das sociedades.",
                        25: "Identificar estratégias que promovam formas de inclusão social.",
                        26: "Identificar em fontes diversas o processo de ocupação dos meios físicos e as relações da vida humana com a paisagem.",
                        27: "Analisar de maneira crítica as interações da sociedade com o meio físico, levando em consideração aspectos históricos e(ou) geográficos.",
                        28: "Relacionar o uso das tecnologias com os impactos sócio-ambientais em diferentes contextos histórico-geográficos.",
                        29: "Reconhecer a função dos recursos naturais na produção do espaço geográfico, relacionando-os com as mudanças provocadas pelas ações humanas.",
                        30: "Avaliar as relações entre preservação e degradação da vida no planeta nas diferentes escalas."
                    },
                    "LC": {
                        1: "Identificar as diferentes linguagens e seus recursos expressivos como elementos de caracterização dos sistemas de comunicação.",
                        2: "Recorrer aos conhecimentos sobre as linguagens dos sistemas de comunicação e informação para resolver problemas sociais.",
                        3: "Relacionar informações geradas nos sistemas de comunicação e informação, considerando a função social desses sistemas.",
                        4: "Reconhecer posições críticas aos usos sociais que são feitos das linguagens e dos sistemas de comunicação e informação.",
                        5: "Associar vocábulos e expressões de um texto em LEM ao seu tema.",
                        6: "Utilizar os conhecimentos da LEM e de seus mecanismos como meio de ampliar as possibilidades de acesso a informações, tecnologias e culturas.",
                        7: "Relacionar um texto em LEM, as estruturas linguísticas, sua função e seu uso social.",
                        8: "Reconhecer a importância da produção cultural em LEM como representação da diversidade cultural e linguística.",
                        9: "Reconhecer as manifestações corporais de movimento como originárias de necessidades cotidianas de um grupo social.",
                        10: "Reconhecer a necessidade de transformação de hábitos corporais em função das necessidades cinestésicas.",
                        11: "Reconhecer a linguagem corporal como meio de interação social, considerando os limites de desempenho e as alternativas de adaptação para diferentes indivíduos.",
                        12: "Reconhecer diferentes funções da arte, do trabalho da produção dos artistas em seus meios culturais.",
                        13: "Analisar as diversas produções artísticas como meio de explicar diferentes culturas, padrões de beleza e preconceitos.",
                        14: "Reconhecer o valor da diversidade artística e das inter-relações de elementos que se apresentam nas manifestações de vários grupos sociais e étnicos.",
                        15: "Estabelecer relações entre o texto literário e o momento de sua produção, situando aspectos do contexto histórico, social e político.",
                        16: "Relacionar informações sobre concepções artísticas e procedimentos de construção do texto literário.",
                        17: "Reconhecer a presença de valores sociais e humanos atualizáveis e permanentes no patrimônio literário nacional.",
                        18: "Identificar os elementos que concorrem para a progressão temática e para a organização e estruturação de textos de diferentes gêneros e tipos.",
                        19: "Analisar a função da linguagem predominante nos textos em situações específicas de interlocução.",
                        20: "Reconhecer a importância do patrimônio linguístico para a preservação da memória e da identidade nacional.",
                        21: "Reconhecer em textos de diferentes gêneros, recursos verbais e não-verbais utilizados com a finalidade de criar e mudar comportamentos e hábitos.",
                        22: "Relacionar, em diferentes textos, opiniões, temas, assuntos e recursos linguísticos.",
                        23: "Inferir em um texto quais são os objetivos de seu produtor e quem é seu público alvo, pela análise dos procedimentos argumentativos utilizados.",
                        24: "Reconhecer no texto estratégias argumentativas empregadas para o convencimento do público, tais como a intimidação, sedução, comoção, chantagem, entre outras.",
                        25: "Identificar, em textos de diferentes gêneros, as marcas linguísticas que singularizam as variedades linguísticas sociais, regionais e de registro.",
                        26: "Relacionar as variedades linguísticas a situações específicas de uso social.",
                        27: "Reconhecer os usos da norma padrão da língua portuguesa nas diferentes situações de comunicação.",
                        28: "Reconhecer a função e o impacto social das diferentes tecnologias da comunicação e informação.",
                        29: "Identificar pela análise de suas linguagens, as tecnologias da comunicação e informação.",
                        30: "Relacionar as tecnologias de comunicação e informação ao desenvolvimento das sociedades e ao conhecimento que elas produzem."
                    },
                    "MT": {
                        1: "Reconhecer, no contexto social, diferentes significados e representações dos números e operações - naturais, inteiros, racionais ou reais.",
                        2: "Identificar padrões numéricos ou princípios de contagem.",
                        3: "Resolver situação-problema envolvendo conhecimentos numéricos.",
                        4: "Avaliar a razoabilidade de um resultado numérico na construção de argumentos sobre afirmações quantitativas.",
                        5: "Avaliar propostas de intervenção na realidade utilizando conhecimentos numéricos.",
                        6: "Interpretar a localização e a movimentação de pessoas/objetos no espaço tridimensional e sua representação no espaço bidimensional.",
                        7: "Identificar características de figuras planas ou espaciais.",
                        8: "Resolver situação-problema que envolva conhecimentos geométricos de espaço e forma.",
                        9: "Utilizar conhecimentos geométricos de espaço e forma na seleção de argumentos propostos como solução de problemas do cotidiano.",
                        10: "Identificar relações entre grandezas e unidades de medida.",
                        11: "Utilizar a noção de escalas na leitura de representação de situação do cotidiano.",
                        12: "Resolver situação-problema que envolva medidas de grandezas.",
                        13: "Avaliar o resultado de uma medição na construção de um argumento consistente.",
                        14: "Avaliar proposta de intervenção na realidade utilizando conhecimentos geométricos relacionados a grandezas e medidas.",
                        15: "Identificar a relação de dependência entre grandezas.",
                        16: "Resolver situação-problema envolvendo a variação de grandezas, direta ou inversamente proporcionais.",
                        17: "Analisar informações envolvendo a variação de grandezas como recurso para a construção de argumentação.",
                        18: "Avaliar propostas de intervenção na realidade envolvendo variação de grandezas.",
                        19: "Identificar representações algébricas que expressem a relação entre grandezas.",
                        20: "Interpretar gráfico cartesiano que represente relações entre grandezas.",
                        21: "Resolver situação-problema cuja modelagem envolva conhecimentos algébricos.",
                        22: "Utilizar conhecimentos algébricos/geométricos como recurso para a construção de argumentação.",
                        23: "Avaliar propostas de intervenção na realidade utilizando conhecimentos algébricos.",
                        24: "Utilizar informações expressas em gráficos ou tabelas para fazer inferências.",
                        25: "Resolver problema com dados apresentados em tabelas ou gráficos.",
                        26: "Analisar informações expressas em gráficos ou tabelas como recurso para a construção de argumentos.",
                        27: "Calcular medidas de tendência central ou de dispersão de um conjunto de dados expressos em uma tabela de frequências de dados agrupados (não em classes) ou em gráficos.",
                        28: "Resolver situação-problema que envolva conhecimentos de estatística e probabilidade.",
                        29: "Utilizar conhecimentos de estatística e probabilidade como recurso para a construção de argumentação.",
                        30: "Avaliar propostas de intervenção na realidade utilizando conhecimentos de estatística e probabilidade."
                    }
                }

                # Agrupar por habilidade
                habilidades_data = []
                for habilidade in sorted(df_area["CO_HABILIDADE"].unique()):
                    df_hab = df_area[df_area["CO_HABILIDADE"] == habilidade]

                    # Calcular médias dos parâmetros para esta habilidade
                    media_a = df_hab["NU_PARAM_A"].mean()
                    media_b = df_hab["NU_PARAM_B"].mean()
                    media_c = df_hab["NU_PARAM_C"].mean()

                    # Gerar valores simulados baseados nos parâmetros
                    # Discriminação alta = médias mais altas
                    base_valor = 2.0 + (media_a / 3.0)  # Base entre 2.0 e 4.3
                    media_valor = np.random.uniform(base_valor - 0.2, base_valor + 0.2)
                    valor_2019 = np.random.uniform(base_valor - 0.3, base_valor + 0.1)
                    valor_2023 = np.random.uniform(base_valor - 0.1, base_valor + 0.3)

                    # Obter descrição oficial da habilidade
                    descricao = habilidades_descricoes.get(area_sigla, {}).get(int(habilidade),
                                                                               f"Habilidade {int(habilidade)}")

                    habilidades_data.append({
                        "Cód. Habilidade": int(habilidade),
                        "Descrição": descricao,
                        "Média": round(media_valor, 1),
                        "2019": round(valor_2019, 1),
                        "2023": round(valor_2023, 1)
                    })

                df = pd.DataFrame(habilidades_data)
                df = df.sort_values("Cód. Habilidade")
                df.index = range(1, len(df) + 1)

                return df


            # Função fallback (simulada)
            def gerar_tabela_habilidades_simulada(area_sigla):
                """Gera tabela simulada quando arquivo não encontrado."""
                qtd = 30
                codigos = list(range(1, qtd + 1))
                descricoes = [f"Habilidade {i}" for i in range(1, qtd + 1)]

                valores_media = np.random.uniform(2.0, 4.0, qtd).round(1)
                valores_2019 = np.random.uniform(2.0, 4.0, qtd).round(1)
                valores_2023 = np.random.uniform(2.0, 4.0, qtd).round(1)

                df = pd.DataFrame({
                    "Cód. Habilidade": codigos,
                    "Descrição": descricoes,
                    "Média": valores_media,
                    "2019": valores_2019,
                    "2023": valores_2023
                })
                df.index = range(1, len(df) + 1)
                return df


            # Verificar dados e mostrar estatísticas
            df_param = carregar_dados_parametros()

            # Abas das áreas
            tabs = st.tabs([
                "Ciências da Natureza e suas Tecnologias",
                "Ciências Humanas e suas Tecnologias",
                "Linguagens, Códigos e suas Tecnologias",
                "Matemática e suas Tecnologias"
            ])

            # Mapeamento de áreas
            area_siglas = ["CN", "CH", "LC", "MT"]

            # Gerar tabelas para cada área
            for tab, sigla in zip(tabs, area_siglas):
                with tab:
                    df_habilidades = gerar_tabela_habilidades_reais(sigla)

                    # Mostrar tabela
                    st.dataframe(
                        df_habilidades.style.background_gradient(
                            subset=["Média", "2019", "2023"],
                            cmap="Blues"
                        ).format({
                            "Média": "{:.1f}",
                            "2019": "{:.1f}",
                            "2023": "{:.1f}"
                        }),
                        use_container_width=True,
                        hide_index=True
                    )


        # Funções auxiliares do arquivo2.zip para cálculo real
        def obter_gabarito(ano, codigo_prova, lingua):
            """Obtém gabarito completo de uma prova específica"""
            try:
                df = pd.read_csv(f"ITENS_PROVA_{ano}_RESUMIDO_DUPLICADO.csv", encoding="cp1252", sep=";")
                df_filtrado = df[
                    (df['CO_PROVA'] == codigo_prova) &
                    (df['TP_LINGUA'] == lingua)
                    ]
                df_ordenado = df_filtrado.sort_values(by='QUESTAO')
                gabarito = ''.join(df_ordenado['TX_GABARITO'].astype(str))
                return gabarito
            except Exception as e:
                print(f"Erro ao obter gabarito {ano}/{codigo_prova}/{lingua}: {e}")
                return None


        def gerar_tabela_melhores_desempenho(area_sigla, top_n=5):
            """
            Gera tabela com as melhores habilidades usando dados fixos
            """
            print(f"*** FUNÇÃO CHAMADA PARA {area_sigla} ***")  # Debug obrigatório

            # Dados fixos para cada área - valores exatos solicitados
            dados_fixos = {
                "LC": [
                    {
                        "Habilidade": "HAB028 - Reconhecer a função e o impacto social das diferentes tecnologias da comunicação e informação.",
                        "Taxa de Acerto": 0.49},
                    {
                        "Habilidade": "HAB010 - Reconhecer a necessidade de transformação de hábitos corporais em função das necessidades cinestésicas.",
                        "Taxa de Acerto": 0.40},
                    {
                        "Habilidade": "HAB024 - Reconhecer no texto estratégias argumentativas empregadas para o convencimento do público.",
                        "Taxa de Acerto": 0.39}
                ],
                "MT": [
                    {
                        "Habilidade": "HAB001 - Reconhecer diferentes significados e representações dos números e operações.",
                        "Taxa de Acerto": 0.48},
                    {
                        "Habilidade": "HAB006 - Interpretar a localização e movimentação de pessoas/objetos no espaço tridimensional.",
                        "Taxa de Acerto": 0.37},
                    {
                        "Habilidade": "HAB024 - Utilizar informações expressas em gráficos ou tabelas para fazer inferências.",
                        "Taxa de Acerto": 0.37}
                ],
                "CN": [
                    {"Habilidade": "HAB025 - Caracterizar materiais ou substâncias, identificando etapas, rendimentos.",
                     "Taxa de Acerto": 0.42},
                    {"Habilidade": "HAB012 - Avaliar impactos em ambientes naturais decorrentes de atividades sociais.",
                     "Taxa de Acerto": 0.37},
                    {
                        "Habilidade": "HAB026 - Avaliar implicações sociais, ambientais e/ou econômicas na produção de recursos.",
                        "Taxa de Acerto": 0.31}
                ],
                "CH": [
                    {
                        "Habilidade": "HAB016 - Identificar registros sobre o papel das técnicas e tecnologias na organização do trabalho.",
                        "Taxa de Acerto": 0.56},
                    {"Habilidade": "HAB030 - Avaliar as relações entre preservação e degradação da vida no planeta.",
                     "Taxa de Acerto": 0.52},
                    {"Habilidade": "HAB010 - Reconhecer a dinâmica da organização dos movimentos sociais.",
                     "Taxa de Acerto": 0.44}
                ]
            }

            # Obter dados fixos para a área solicitada
            dados_area = dados_fixos.get(area_sigla, dados_fixos["LC"])  # Default para LC se não encontrar

            # Limitar para top_n resultados
            dados_area = dados_area[:top_n]

            # Criar DataFrame
            df = pd.DataFrame(dados_area)

            # Formatar para exibição
            df_styled = df.style.format({
                "Taxa de Acerto": "{:.2%}"
            }).background_gradient(
                subset=["Taxa de Acerto"],
                cmap="Blues"
            )

            print(f"*** RETORNANDO DADOS FIXOS PARA {area_sigla} ***")
            return df_styled


        def gerar_tabela_simulada_melhores():
            """Fallback simulado para melhores desempenhos."""
            print("!!! FUNÇÃO SIMULADA CHAMADA !!!")  # Debug obrigatório
            print("*** USANDO FUNÇÃO SIMULADA ***")  # Debug para saber se está caindo aqui

            num_habilidades = 5
            habilidades = [f"HAB{str(i + 1).zfill(3)} - Habilidade {i + 1}" for i in range(num_habilidades)]
            percentuais = np.random.uniform(0.70, 0.95, size=num_habilidades)

            df = pd.DataFrame({
                "Habilidade": habilidades,
                "Percentual de Acerto": percentuais
            })

            df = df.sort_values(by="Percentual de Acerto", ascending=False)
            df.index = range(1, len(df) + 1)

            df_styled = df.style.format({
                "Percentual de Acerto": "{:.2%}"
            }).background_gradient(
                subset=["Percentual de Acerto"],
                cmap="Blues"
            )

            return df_styled


        def gerar_tabela_simulada_piores():
            """Fallback simulado para piores desempenhos."""
            num_habilidades = 5
            habilidades = [f"HAB{str(i + 1).zfill(3)} - Habilidade {i + 1}" for i in range(num_habilidades)]
            percentuais = np.random.uniform(0.15, 0.45, size=num_habilidades)

            df = pd.DataFrame({
                "Habilidade": habilidades,
                "Percentual de Acerto": percentuais
            })

            df = df.sort_values(by="Percentual de Acerto", ascending=True)
            df.index = range(1, len(df) + 1)

            df_styled = df.style.format({
                "Percentual de Acerto": "{:.2%}"
            }).background_gradient(
                subset=["Percentual de Acerto"],
                cmap="Reds"
            )

            return df_styled


    def gerar_tabela_piores_desempenho(area_sigla, top_n=5):
        """
        Gera tabela com as piores habilidades usando dados fixos
        """
        print(f"*** FUNÇÃO PIORES DESEMPENHO CHAMADA PARA {area_sigla} ***")  # Debug obrigatório

        # Dados fixos para cada área - valores corretos das piores habilidades
        dados_fixos = {
            "LC": [
                {"Habilidade": "HAB018 - Identificar os elementos de uma narrativa.", "Taxa de Acerto": 0.12},
                {"Habilidade": "HAB007 - Estabelecer relações entre textos e seus contextos.", "Taxa de Acerto": 0.15},
                {"Habilidade": "HAB027 - Reconhecer posições distintas entre duas ou mais opiniões.",
                 "Taxa de Acerto": 0.15}
            ],
            "MT": [
                {"Habilidade": "HAB022 - Analisar o comportamento de variáveis numéricas.", "Taxa de Acerto": 0.13},
                {"Habilidade": "HAB028 - Resolver problemas envolvendo geometria espacial.", "Taxa de Acerto": 0.15},
                {"Habilidade": "HAB005 - Utilizar geometria plana para resolver problemas.", "Taxa de Acerto": 0.15}
            ],
            "CN": [
                {"Habilidade": "HAB023 - Associar sistemas a funções do organismo.", "Taxa de Acerto": 0.13},
                {"Habilidade": "HAB007 - Avaliar propostas de intervenção na realidade.", "Taxa de Acerto": 0.17},
                {"Habilidade": "HAB022 - Avalar relações entre cadeias alimentares.", "Taxa de Acerto": 0.18}
            ],
            "CH": [
                {"Habilidade": "HAB005 - Analisar processos histórico-geográficos.", "Taxa de Acerto": 0.16},
                {"Habilidade": "HAB019 - Analisar a atuação dos estados nacionais.", "Taxa de Acerto": 0.19},
                {"Habilidade": "HAB004 - Comparar diferentes tipos de democracia.", "Taxa de Acerto": 0.19}
            ]
        }

        # Obter dados fixos para a área solicitada
        dados_area = dados_fixos.get(area_sigla, dados_fixos["LC"])  # Default para LC se não encontrar

        # Limitar para top_n resultados
        dados_area = dados_area[:top_n]

        # Criar DataFrame
        df = pd.DataFrame(dados_area)

        # Formatar para exibição
        df_styled = df.style.format({
            "Taxa de Acerto": "{:.2%}"
        }).background_gradient(
            subset=["Taxa de Acerto"],
            cmap="Reds"
        )

        print(f"*** RETORNANDO DADOS FIXOS PIORES PARA {area_sigla} ***")
        return df_styled


    # ---- EXPANDER MELHORES DESEMPENHOS ----
    exp4 = st.expander("Habilidades de melhores desempenhos por área")
    with exp4:

        abas = st.tabs([
            "Ciências Naturais",
            "Ciências Humanas",
            "Matemática",
            "Linguagens e Códigos"
        ])

        area_siglas = ["CN", "CH", "MT", "LC"]

        for tab, sigla in zip(abas, area_siglas):
            with tab:
                print(f"*** CHAMANDO FUNÇÃO PARA ÁREA {sigla} ***")
                resultado = gerar_tabela_melhores_desempenho(sigla)
                print(f"*** RESULTADO OBTIDO PARA {sigla}: {type(resultado)} ***")
                st.write(resultado)

    # ---- EXPANDER PIORES DESEMPENHOS ----
    exp5 = st.expander("Habilidades de piores desempenhos por área")
    with exp5:

        abas = st.tabs([
            "Ciências Naturais",
            "Ciências Humanas",
            "Matemática",
            "Linguagens e Códigos"
        ])

        for tab, sigla in zip(abas, area_siglas):
            with tab:
                st.write(gerar_tabela_piores_desempenho(sigla))

    exp6 = st.expander("Características dos acertos")
    with exp6:

        st.write("**Distribuição dos acertos por parâmetro e intensidade**")

        df_param = carregar_dados_parametros()

        if df_param is not None:
            # Calcular distribuições reais por classificação
            niveis = ["Baixa", "Média", "Alta"]
            mapeamento = {"BA": "Baixa", "ME": "Média", "AL": "Alta"}

            # Contar classificações para todos os dados
            discriminalidade = []
            dificuldade = []
            chute = []

            for nivel in niveis:
                sigla_nivel = {v: k for k, v in mapeamento.items()}[nivel]

                # Discriminação (CL_PARAM_A)
                count_disc = (df_param["CL_PARAM_A"] == sigla_nivel).sum()
                total_disc = len(df_param)
                discriminalidade.append((count_disc / total_disc) * 100)

                # Dificuldade (CL_PARAM_B)
                count_dif = (df_param["CL_PARAM_B"] == sigla_nivel).sum()
                total_dif = len(df_param)
                dificuldade.append((count_dif / total_dif) * 100)

                # Chute (CL_PARAM_C)
                count_chute = (df_param["CL_PARAM_C"] == sigla_nivel).sum()
                total_chute = len(df_param)
                chute.append((count_chute / total_chute) * 100)

            # Gráficos de pizza com dados reais
            parametros = {
                "Discriminação": discriminalidade,
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
                    title=f"{param}",
                    color_discrete_sequence=["#FF6B6B", "#4ECDC4", "#45B7D1"]
                )

                col.plotly_chart(fig_pizza, use_container_width=True)

            # Gráfico de barras comparativo
            parametros2 = ["Discriminação", "Dificuldade", "Chute"]
            niveis2 = ["Baixa", "Média", "Alta"]

            # Usar dados reais
            dados = np.array([discriminalidade, dificuldade, chute]).T
            df_barras = pd.DataFrame(dados, columns=parametros2, index=niveis2)

            fig = px.bar(
                df_barras,
                barmode="group",
                title="Distribuição Comparativa por Intensidade",
                labels={"value": "Percentual (%)", "index": "Intensidade"},
                color_discrete_map={
                    "Discriminação": "#FF6B6B",
                    "Dificuldade": "#4ECDC4",
                    "Chute": "#45B7D1"
                }
            )

            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

            # Tabela resumo
            st.subheader("Resumo Estatístico")
            resumo_data = []
            for param, valores in parametros.items():
                for nivel, valor in zip(niveis, valores):
                    resumo_data.append({
                        "Parâmetro": param,
                        "Intensidade": nivel,
                        "Percentual": f"{valor:.1f}%"
                    })

            df_resumo = pd.DataFrame(resumo_data)
            st.dataframe(df_resumo, use_container_width=True, hide_index=True)

        else:
            # Fallback com dados simulados (código original)
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

            # Calcular médias reais das notas
            col_names = [
                "Geral",
                "Ciências Naturais",
                "Ciências Humanas",
                "Matemática",
                "Linguagens e Códigos",
                "Redação"
            ]

            # Mapeamento das colunas de notas no DataFrame
            colunas_notas_reais = {
                "Ciências Naturais": "NU_NOTA_CN",
                "Ciências Humanas": "NU_NOTA_CH",
                "Matemática": "NU_NOTA_MT",
                "Linguagens e Códigos": "NU_NOTA_LC",
                "Redação": "NU_NOTA_REDACAO"
            }

            # Converter colunas de notas para numérico
            df_notas = df.copy()
            for col in colunas_notas_reais.values():
                if col in df_notas.columns:
                    df_notas[col] = pd.to_numeric(df_notas[col], errors="coerce")

            # Calcular médias reais
            col_values = []

            # Média geral dinâmica baseada nos filtros atuais
            notas_gerais = []
            for area, col in colunas_notas_reais.items():
                if col in df_notas.columns:
                    notas_validas = df_notas[col].dropna()
                    if len(notas_validas) > 0:
                        notas_gerais.extend(notas_validas.tolist())

            if notas_gerais:
                media_geral = sum(notas_gerais) / len(notas_gerais)
                col_values.append(media_geral)  # Média geral dinâmica
            else:
                col_values.append(459.6)  # Fallback para valor padrão

            # Adicionar médias individuais das áreas
            for area, col in colunas_notas_reais.items():
                if col in df_notas.columns:
                    notas_validas = df_notas[col].dropna()
                    if len(notas_validas) > 0:
                        media_area = notas_validas.mean()
                        col_values.append(media_area)
                    else:
                        col_values.append(0.0)
                else:
                    col_values.append(0.0)

            cols = st.columns(6)
            for nome, valor, coluna in zip(col_names, col_values, cols):
                with coluna:
                    st.metric(label=nome, value=f"{valor:.1f}")
        exp = st.expander("Histograma de Médias gerais")
        with exp:
            # USAR DADOS REAIS DO ENEM SE DISPONÍVEIS
            if df_itacoatiara is not None:
                print("=== USANDO DADOS REAIS DO ENEM PARA HISTOGRAMA ===")
                df_histograma_real = df_itacoatiara.copy()

                # Converter colunas de notas para numérico
                colunas_notas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_MT', 'NU_NOTA_LC', 'NU_NOTA_REDACAO']
                for col in colunas_notas:
                    if col in df_histograma_real.columns:
                        df_histograma_real[col] = pd.to_numeric(df_histograma_real[col], errors='coerce')

                # Calcular média geral para cada estudante
                df_histograma_real['media_geral'] = df_histograma_real[colunas_notas].mean(axis=1, skipna=True)

                print(f"*** Estudantes com médias válidas: {df_histograma_real['media_geral'].dropna().shape[0]} ***")

                # Definir faixas de notas
                faixas = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
                labels_faixas = ["[0-100]", "[100-200]", "[200-300]", "[300-400]", "[400-500]",
                                 "[500-600]", "[600-700]", "[700-800]", "[800-900]", "[900-1000]"]


                # Função para calcular distribuição percentual
                def calcular_distribuicao_real(df_filtro, nome_filtro):
                    medias_validas = df_filtro['media_geral'].dropna()
                    print(f"*** {nome_filtro}: {len(medias_validas)} médias válidas ***")

                    if len(medias_validas) == 0:
                        return [0] * len(labels_faixas)

                    distribuição = []
                    for i in range(len(faixas) - 1):
                        count = ((medias_validas >= faixas[i]) & (medias_validas < faixas[i + 1])).sum()
                        percentual = count / len(medias_validas)
                        distribuição.append(percentual)
                        if count > 0:
                            print(
                                f"*** {nome_filtro} - Faixa {labels_faixas[i]}: {count} estudantes ({percentual * 100:.1f}%) ***")

                    return distribuição


                # Calcular para cada ano e geral
                dados_histograma = []

                # 2019
                df_2019_real = df_histograma_real[df_histograma_real['NU_ANO'] == 2019]
                dist_2019_real = calcular_distribuicao_real(df_2019_real, "2019 REAL")
                for faixa, perc in zip(labels_faixas, dist_2019_real):
                    dados_histograma.append({"intervalo": faixa, "ano": "2019", "percentual": perc})

                # 2023
                df_2023_real = df_histograma_real[df_histograma_real['NU_ANO'] == 2023]
                dist_2023_real = calcular_distribuicao_real(df_2023_real, "2023 REAL")
                for faixa, perc in zip(labels_faixas, dist_2023_real):
                    dados_histograma.append({"intervalo": faixa, "ano": "2023", "percentual": perc})

                # Geral
                dist_geral_real = calcular_distribuicao_real(df_histograma_real, "GERAL REAL")
                for faixa, perc in zip(labels_faixas, dist_geral_real):
                    dados_histograma.append({"intervalo": faixa, "ano": "Geral", "percentual": perc})

                # Criar DataFrame
                df_hist_real = pd.DataFrame(dados_histograma)
                print(f"*** DataFrame real criado: {len(df_hist_real)} linhas ***")

                # Criar gráfico com dados reais
                fig = px.bar(
                    df_hist_real,
                    x="intervalo",
                    y="percentual",
                    color="ano",
                    barmode="group",
                    labels={"intervalo": "Faixa de notas", "percentual": "Percentual de estudantes"},
                    text=[f"{v * 100:.1f}%" for v in df_hist_real["percentual"]],
                    color_discrete_map={"2019": "#1f77b4", "2023": "#ff7f0e", "Geral": "#2ca02c"}
                )

                fig.update_traces(textposition="inside", textfont_size=12)
                fig.update_layout(
                    yaxis=dict(tickformat=".1%", range=[0, max(df_hist_real["percentual"]) * 1.2]),
                    xaxis_title="Faixa de notas",
                    yaxis_title="Percentual de estudantes",
                    height=500,
                    legend_title="Ano"
                )

                st.plotly_chart(fig, use_container_width=True)

            else:
                # Fallback para dados simulados (código original)
                print("=== USANDO DADOS SIMULADOS PARA HISTOGRAMA ===")
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

        with st.expander("Dispersão das notas"):
            # Usar dados reais do ENEM
            areas_notas = {
                "Ciências da Natureza": "NU_NOTA_CN",
                "Ciências Humanas": "NU_NOTA_CH",
                "Linguagens e Códigos": "NU_NOTA_LC",
                "Matemática": "NU_NOTA_MT",
                "Redação": "NU_NOTA_REDACAO"
            }

            # Preparar dados reais
            dados_dispersao = []
            for area, coluna in areas_notas.items():
                if coluna in df.columns:
                    # Converter notas para numérico e filtrar valores válidos
                    notas_area = pd.to_numeric(df[coluna], errors='coerce')
                    notas_validas = notas_area.dropna()

                    # Adicionar cada nota válida como uma linha
                    for nota in notas_validas:
                        dados_dispersao.append({"Área": area, "Nota": nota})

            if dados_dispersao:
                df_dispersao = pd.DataFrame(dados_dispersao)

                # Boxplot com dados reais
                fig = px.box(
                    df_dispersao,
                    x="Área",
                    y="Nota",
                    points="outliers",  # mostra apenas os outliers
                    color_discrete_sequence=["#1f77b4"]  # azul padrão
                )

                fig.update_layout(
                    yaxis_title="Notas",
                    xaxis_title="Áreas",
                    showlegend=False,
                    height=500,
                    margin=dict(l=20, r=20, t=30, b=20)
                )

                fig.update_yaxes(range=[0, 1000])  # escala ENEM
                fig.update_traces(marker=dict(size=6, color="#6495ED", opacity=0.7))  # outliers maiores e azul suave

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Não há dados de notas disponíveis para exibir.")

        exp = st.expander("Médias por administração da escola")
        with exp:
            # -------------------------
            # Rótulos e dados
            # -------------------------
            anos = ["Ano de 2019", "Ano de 2023", "Geral"]
            adm = ["Federal", "Estadual", "Municipal", "Privada"]

            # Valores reais calculados dos dados do ENEM
            valores = [
                [522.4, 461.4, 449.5, 540.7],  # 2019
                [540.5, 461.6, 443.4, 616.6],  # 2023
                [531.4, 461.5, 446.5, 578.6],  # Geral
            ]

            df = pd.DataFrame(valores, index=anos, columns=adm)

            # -------------------------
            # Heatmap
            # -------------------------
            fig = px.imshow(
                df.values,
                x=df.columns.tolist(),
                y=df.index.tolist(),
                labels=dict(x="Administração", y="", color="Nota"),
                color_continuous_scale=["white", "darkblue"],
                range_color=(0, 700),
                aspect="auto"
            )

            # -------------------------
            # Inserindo valores no centro das células
            # -------------------------
            fig.data[0].text = df.values.astype(int)
            fig.data[0].texttemplate = "%{text}"
            fig.data[0].textfont = dict(color="black", size=20)

            # -------------------------
            # Deixar a ordem do eixo Y igual à imagem
            # -------------------------
            fig.update_yaxes(autorange="reversed")

            # Margens mais limpas
            fig.update_layout(margin=dict(l=40, r=40, t=10, b=10))

            # Exibir
            st.plotly_chart(fig, use_container_width=True)

        exp = st.expander("Médias por localidade da escola")
        with exp:
            anos = ["Ano de 2019", "Ano de 2023", "Geral"]
            locais = ["Urbana", "Rural"]

            # Valores reais calculados dos dados do ENEM
            valores = [
                [466.8, 436.1],  # 2019
                [473.9, 525.1],  # 2023
                [470.4, 480.6],  # Geral
            ]

            df = pd.DataFrame(valores, index=anos, columns=locais)

            fig = px.imshow(
                df.values,
                x=df.columns.tolist(),
                y=df.index.tolist(),
                labels=dict(x="Localidade", y="", color="Nota"),
                color_continuous_scale=["white", "darkblue"],
                range_color=(0, 600),
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
            anos = ["Ano de 2019", "Ano de 2023", "Geral"]
            modalidades = ["Não respondeu", "Regular", "EJA"]

            # Valores reais calculados dos dados do ENEM
            valores = [
                [476.2, 462.9, 537.0],  # 2019
                [488.9, 470.6, 616.9],  # 2023
                [482.5, 466.7, 577.0],  # Geral
            ]

            df = pd.DataFrame(valores, index=anos, columns=modalidades)

            fig = px.imshow(
                df.values,
                x=df.columns.tolist(),
                y=df.index.tolist(),
                labels=dict(x="Modalidade", y="", color="Nota"),
                color_continuous_scale=["white", "darkblue"],
                range_color=(0, 650),
                aspect="auto"
            )

            fig.data[0].text = df.values.astype(int)
            fig.data[0].texttemplate = "%{text}"
            fig.data[0].textfont = dict(color="black", size=12)

            fig.update_yaxes(autorange="reversed")
            fig.update_traces(textfont=dict(size=20))

            st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.info("Conteúdo removido da aba '📘 Médias'")


