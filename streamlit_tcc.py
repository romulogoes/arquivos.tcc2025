import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px

st.set_page_config(page_title="Dashboard ENEM Itacoatiara", layout="wide")

CSV_PATH = "MD_ENEM_ITACOATIARA_FULL.csv"  #meu arquivo principal

try:
    df = pd.read_csv(CSV_PATH, encoding="cp1252", sep=";", dtype=str)
except FileNotFoundError:
    st.error(f"Arquivo não encontrado: {CSV_PATH}")
    st.stop()
except Exception as e:
    st.error(f"Erro ao abrir o CSV: {e}")
    st.stop()

campo_anos = st.sidebar.selectbox(
    "Anos",
    ["2019", "2023", "2019 e 2023"], index=2
)
selecionar_todos = st.sidebar.checkbox("Incluir os estudantes sem escola associada", value=True)
if not selecionar_todos:
    df = df[df["CO_MUNICIPIO_ESC"] == "1301902"]

if campo_anos != "2019 e 2023":
    df = df[df["NU_ANO"].astype(str) == campo_anos]

df["NU_ANO"] = pd.to_numeric(df["NU_ANO"], errors="coerce")

exp = st.expander("📊 Inscrições no exame", expanded=True)
with exp:
    col1, col2 = st.columns(2)
    with col2:
        _c1, _c2, _c3 = st.columns(3)
        st.metric(label="Inscritos", value=int(len(df)))
        st.metric(label="Regulares", value=int(len(df[df["IN_TREINEIRO"] == "0"])))
        st.metric(label="Treineiros     ", value=int(len(df[df["IN_TREINEIRO"] == "1"])))
    with col1:
        df_count = df.groupby("NU_ANO").size().reset_index(name="Quantidade")
        df_count["Ano"] = df_count["NU_ANO"].astype(str)

        chart = alt.Chart(df_count).mark_bar(color="#4C78A8").encode(
            x=alt.X("Ano:O", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Quantidade:Q")
        )
        text = chart.mark_text(dy=-10, color="black", baseline="bottom", fontSize=18).encode(text=alt.Text("Quantidade:Q"))
        st.altair_chart(chart + text, use_container_width=True)

exp = st.expander("✅ Presença nas provas", expanded=True)
with exp:
    dias = {
        "Dia 1 - Ciências Humanas, Linguagens e Redação": "TP_PRESENCA_CH",
        "Dia 2 - Ciências da Natureza e Matemática": "TP_PRESENCA_CN"
    }

    col1, col2 = st.columns(2)
    for i, (nome_dia, coluna) in enumerate(dias.items()):
        if coluna not in df.columns:
            st.warning(f"Coluna {coluna} não encontrada no CSV.")
            continue

        df[coluna] = df[coluna].replace({
            "0": "Ausente",
            "1": "Presente",
            "2": "Eliminado"
        })

        main_col = col1 if i == 0 else col2
        with main_col:
            st.subheader(nome_dia)
            sub_col1, sub_col2 = st.columns(2)

            count = df.groupby(coluna).size().reset_index(name="Quantidade")
            fig_pizza = px.pie(
                count, values="Quantidade", names=coluna,
                title="Percentual de presença", hole=0.3,
                labels = {"TP_PRESENCA_CH": "Categoria"}
            )
            fig_pizza.update_traces(
                textfont={"size": 18},
                textinfo="percent",
                texttemplate="%{percent:.2%}"
            )
            with sub_col1:
                st.plotly_chart(fig_pizza, use_container_width=True)

            barra = df.groupby(["NU_ANO", coluna]).size().reset_index(name="Quantidade")

            fig_barra = px.bar(
                barra,
                x="NU_ANO", y="Quantidade",
                color=coluna, text="Quantidade",
                barmode="group",
                title="Situação por ano",
                category_orders={coluna: ["Presente", "Ausente", "Eliminado"]},
                labels={"NU_ANO": "Ano", "Quantidade": "Quantidade",
        coluna: "Categoria" }
            )

            with sub_col2:
                st.plotly_chart(fig_barra, use_container_width=True)

exp = st.expander("📈 Notas Médias", expanded=True) #-----NOTAS MÉDIAS
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

            df_soma = (
                df_plot.groupby("Área")["Nota"]
                .sum()
                .reset_index()
            )

            fig_medias = px.bar(
                df_soma, x="Área", y="Nota",
                text="Nota",
                title="Soma das Médias por Área (2019 + 2023)",
                category_orders={
                    "Área": ["Ciências da Natureza", "Ciências Humanas", "Linguagens e Códigos", "Matemática",
                             "Redação"]}

            )
            fig_medias.update_traces(texttemplate="%{text:.0f}", textposition="inside")
            fig_medias.update_yaxes(tickformat="d")
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

exp = st.expander("📦 Boxplots", expanded=True)      #-------BOXPLOTS
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
                    rows.append({"Area": area, "Ano": int(ano), "Media": float(media) if not np.isnan(media) else np.nan})

        if not rows:
            st.warning("Não foi possível calcular heatmaps a partir de colunas de nota. Mostrando exemplo.")
            df_small = pd.DataFrame({
                ("Médias gerais","2019"): [1,5,3,7],
                ("Médias gerais","2023"): [10,20,15,25],
            })
            df_small.columns = pd.MultiIndex.from_tuples(df_small.columns)
            df_small["Dependência"] = ["Federal","Estadual","Municipal","Privada"]
            df_small.set_index("Dependência", inplace=True)
            fig = px.imshow(np.hstack([df_small[("Médias gerais","2019")].values.reshape(-1,1), df_small[("Médias gerais","2023")].values.reshape(-1,1)]),
                            x=["2019","2023"], y=df_small.index, text_auto=True, aspect="auto", title="Heatmap exemplo (Médias gerais)")
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
                        dep_rows.append({"Dependencia": dep, "Area": area, "Media": float(media) if not np.isnan(media) else np.nan})
            if dep_rows:
                df_dep = pd.DataFrame(dep_rows)
                pivot2 = df_dep.pivot(index="Dependencia", columns="Area", values="Media")
                fig2 = px.imshow(pivot2, text_auto=".1f", aspect="auto", title="Heatmap: média por Dependência x Área")
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Coluna 'TP_DEPENDENCIA' não encontrada — não foi possível gerar o heatmap detalhado por dependência.")


def main():
    st.sidebar.header("Controle do App")

    path2019 = st.sidebar.text_input("Caminho CSV 2019", value="MICRODADOS_ITA_2019_FILTRADO.csv")
    path2023 = st.sidebar.text_input("Caminho CSV 2023", value="MICRODADOS_ITA_2023_FILTRADO.csv")

    try:
        df = carregar_dados(path2019=path2019, path2023=path2023)
    except FileNotFoundError as e:
        st.error(f"Arquivo não encontrado: {e}")
        return

    df_filtrado = filtros(df.copy())

    titulo()
    st.write("Qtd. total (após filtros):", int(len(df_filtrado)))

    inscritos(df_filtrado)
    presenca(df_filtrado)
    medias_por_area(df_filtrado)
    boxplot_por_area(df_filtrado)
    heatmaps(df_filtrado)

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