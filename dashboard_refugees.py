# =============================================================================
# Dashboard Refugees.
#
# María Victoria Simes.
# Open Data & Visualización dinámica.
# Master en Data Science y Big Data 2022 - 2023
# =============================================================================

import streamlit as st
import pandas as pd
import app_functions as af
from streamlit_option_menu import option_menu


# =============================================================================
# Sets de Datos
# =============================================================================
population = pd.read_csv('./data/processed/acnur_data_population.csv')
asylum_petitions = pd.read_csv('./data/processed/acnur_data_asylum_petitions.csv')
countries = pd.read_csv('./data/processed/acnur_countries.csv')
demographics = pd.read_csv('./data/processed/acnur_data_demographics.csv')


# =============================================================================
# Página.
# =============================================================================
st.set_page_config(layout="wide", page_title='Refugiados')

# =============================================================================
# Menú lateral
# =============================================================================
# Customizando un header
st.sidebar.title('Una introducción a la situación de los refugiados.')
st.sidebar.caption('Made by María Victoria Simes.')

# Opciones
with st.sidebar:
    selected = option_menu('Datos refugiados', ['Problemática',
                                                'Situación general',
                                                'Situación por país'])
# ========================
# Apartado 1: Introducción.
# ========================
if selected == 'Problemática':
    # Breve introducción a la problemática.
    st.title('Obligado a dejar mi hogar, mi país.')

    row1_1, row1_2 = st.columns((3, 3))
    with row1_1:
        st.subheader('¿Que significa ser refugiado?')
        st.markdown(
            """
        ##
        El Artículo 14 de la Declaración Universal de Derechos Humanos reconoce
        el derecho de las personas a solicitar asilo en otros países a raíz de
        persecución. En base a este artículo, la Convención de Naciones Unidas
        sobre el Estatus de los Refugiados, define a estos como personas que no
        pueden o no quieren regresar a su país de origen por fundados temores de
        ser perseguidos por motivos de raza, religión, nacionalidad, pertenencia
        a un determinado grupo socual y opinión política.
            """
        )

    with row1_2:
        st.subheader('¿Quién protege a los refugiados en el mundo?')
        st.markdown(
            """
        ##
        La protección de las personas refugiadas engloba muchos aspectos.
        Entre estos, la garantía de no ser devueltas al peligro, el acceso a
        procedimientos de asilo justos y eficientes, y medidas para asegurar
        que se respeten sus derechos humanos básicos, al tiempo que se les
        aseguran soluciones a largo plazo. El Alto Comisionado de las Naciones
        Unidas para los Refugiados tiene como misión proteger a los refugiados
        y desplazados, y promover soluciones duraderas a su situación, mediante
        el reasentamiento voluntario en su país de origen o en el de acogida.
            """
        )

    st.markdown('---')

    # Mapa: Movimiento por años.
    # Definición del set de datos.
    df_map_1 = population[['year', 'name_origin_country', 'name_asylum_country',
                           'continent_origin_country', 'longitude_origin_country',
                           'latitude_origin_country', 'longitude_asylum_country',
                           'latitude_asylum_country']]

    df_map_1 = df_map_1.dropna()

    df_map_1 = df_map_1.loc[(df_map_1.name_origin_country != 'Unknown') |
                            df_map_1.name_asylum_country != 'Unknown']

    df_map = df_map_1.loc[(df_map_1.name_origin_country !=
                           df_map_1.name_asylum_country)]
    # Llamo a la función correspondiente para dibujar el mapa.
    af.map_movement_year(df_map_1)
    st.caption('Fuente: Elaboración propia con datos extraídos de ACNUR.')

# ==============================
# Apartado 2: Situación general.
# ==============================
elif selected == 'Situación general':
    st.header('Situación general de los refugiados')

    # Subtítulo 1: Evolución a lo largo del tiempo
    st.subheader('Evolución de los flujos de poblacionales a lo largo del tiempo')
    row2_1, row2_2 = st.columns((3, 3))

    # Para filtrar por tipo de población.
    with row2_1:
        column_name, option_type_refugee = af.population_selectbox()

    # Para filtrar por continente
    with row2_2:
        continent_name = af.continent_selectbox()

    # Filtrado del set de datos por continente elegido.
    if continent_name != 'Todos':
        # Definición del set de datos filtrando por continente elegido y agru-
        # pando por año.
        df_graph_1 = population.loc[population.continent_origin_country ==
                                    continent_name].groupby(
                                        ['year'], as_index=False).sum()
    else:
        df_graph_1 = population.groupby(['year'], as_index=False).sum()

    # Filtrado del set de datos por tipo de población elegida.
    if column_name != 'Todas':
        df_graph_1 = df_graph_1.loc[df_graph_1[column_name] != 0, ['year',
                                                                   column_name]]

        # Llamo la función para dibujar el gráfico.
        af.plot_evolution_time(df_graph_1, column_name, option_type_refugee)
        st.caption('Fuente: Elaboración propia con datos extraídos de ACNUR.')

    else:
        columns_not_show = ['longitude_origin_country',
                            'latitude_origin_country',
                            'longitude_asylum_country',
                            'latitude_asylum_country']
        df_graph_1 = df_graph_1.drop(columns=columns_not_show)

        # Llamo la función para dibujar el gráfico.
        af.plot_evolution_time_all(df_graph_1)
        st.caption('Fuente: Elaboración propia con datos extraídos de ACNUR.')

    # Subtítulo 2: Solicitudes de asilo vs. resoluciones.
    st.markdown('---')
    st.subheader('Evolución de las solicitudes y resoluciones de asilo a lo largo del tiempo')

    row3_1, row3_2, row3_3 = st.columns((2, 2, 2))
    # Para filtrar por solicitud y tipo de resolución.
    with row3_1:
        columns_names = af.petition_multiselect()

    # Para filtrar por continente de origen.
    with row3_2:
        origin_continent = af.continent_selectbox(value=2, suffix='de origen')

    # Para filtrar por continente de asilo.
    with row3_3:
        asylum_continent = af.continent_selectbox(exclude_continents=['Apátrida',
                                                                      'Desconocido'],
                                                  value=3,
                                                  suffix='de asilo')

    # Filtrado del set de datos por continente de origen elegido.
    if origin_continent != 'Todos':
        df_graph_2 = asylum_petitions.loc[asylum_petitions.continent_origin_country ==
                                          origin_continent].groupby(['year',
                                                                     'continent_asylum_country'],
                                                                    as_index=False).sum()
    else:
        df_graph_2 = asylum_petitions.groupby(['year',
                                               'continent_asylum_country'],
                                              as_index=False).sum()

    # Filtrado del set de datos por continente de asilo elegido.
    if asylum_continent != 'Todos':
        df_graph_2 = df_graph_2.loc[df_graph_2.continent_asylum_country ==
                                    asylum_continent].groupby(['year'],
                                                              as_index=False).sum()

    # Filtrado del set de datos por selección de columnas.
    df_graph_2 = df_graph_2.loc[:, columns_names +
                                ['year']].groupby(['year'], as_index=False).sum()

    # Llamo la función para dibujar el gráfico
    af.plot_petitions_time(df_graph_2, columns_names)
    st.caption('Fuente: Elaboración propia con datos extraídos de ACNUR.')

# ================================
# Apartado 3: Situación por país.
# ================================
else:
    st.header('Situación de los refugiados por país')

    with st.expander('Selecciona algo diferente'):
        row4_1, row4_2 = st.columns((2, 3))
        with row4_1:
            # Para filtrar por continente.
            continent_election = af.continent_selectbox(exclude_continents=['Apátrida',
                                                                            'Desconocido',
                                                                            'Todos'], index=2)
            # Para filtrar por país.
            country = af.country_selectbox(countries, continent_election,
                                           variable='name')

        with row4_2:
            # Para filtrar por año.
            year = st.selectbox('**Año**', range(1951, 2023), index=70)

            # Para filtrar datos de refugiados recibidos o enviados.
            situation = st.radio('**Refugiados**', ('Recibidos', 'Enviados'))

    st.subheader(f'{country}')

    # Pantalla a mostrar si la opción elegida es ver los refugiados que recibe el país.
    if situation == 'Recibidos':
        description = f'''
                 **Las personas de los siguientes países se localizaron en
                 {country} en el año {year}.**'''

        # Defino los sets de datos.
        df_country = population.loc[(population.name_asylum_country == country) &
                                    (population.year == year)].groupby(['year'],
                                                                       as_index=False).sum()

        df_country_sex = demographics.loc[(demographics.name_asylum_country == country) &
                                          (demographics.year == year)].groupby(['year'],
                                                                               as_index=False).sum()

        df_map_3 = population.loc[(population.name_asylum_country == country) &
                                  (population.year == year)]
        df_map_3 = df_map_3[['longitude_origin_country', 'latitude_origin_country']]
        df_map_3 = df_map_3.dropna()
        df_map_3 = df_map_3.rename(columns={'longitude_origin_country': 'longitude',
                                            'latitude_origin_country': 'latitude'})

        # Defino otra serie de variables necesarias para poder pintar las métricas.
        if df_country.empty:
            value = 0
        else:
            value = df_country.loc[0, ['refugees', 'asylum_seekers', 'other_concern',
                                       'other_need']].sum()

        columns_names = ['refugees', 'asylum_seekers', 'other_concern',
                         'other_need']

    # Pantalla a mostrar si la opción elegida es ver los refugiados que recibe el país.
    else:
        description = f'''
                 **Las personas de {country} se localizaron en los siguientes
                 países en el año {year}.**'''
        # Defino los sets de datos.
        df_country = population.loc[(population.name_origin_country == country) &
                                    (population.year == year)].groupby(['year'],
                                                                       as_index=False).sum()

        df_country_sex = demographics.loc[(demographics.name_origin_country == country) &
                                          (demographics.year == year)].groupby(['year'],
                                                                               as_index=False).sum()

        df_map_3 = population.loc[(population.name_origin_country == country) &
                                  (population.year == year)]
        df_map_3 = df_map_3[['longitude_asylum_country', 'latitude_asylum_country']]
        df_map_3 = df_map_3.dropna()
        df_map_3 = df_map_3.rename(columns={'longitude_asylum_country': 'longitude',
                                            'latitude_asylum_country': 'latitude'})

        # Defino otra serie de variables necesarias para poder pintar las métricas
        value = df_country['refugees'] + df_country['asylum_seekers']\
            + df_country['internally_displaced'] + df_country['other_concern']\
            + df_country['other_need'] + df_country['returned_internally_displaced']

        columns_names = ['refugees', 'asylum_seekers', 'other_concern',
                         'internally_displaced', 'other_need',
                         'returned_internally_displaced']

    # Estructura de ambas pantallas.
    st.write(description)

    # Algunas estadísticas en formato metric.
    row5_1, row5_2, row5_3, row5_4 = st.columns((2, 2, 2, 2))
    with row5_1:
        st.metric(label='**Desplazados por la fuerza**', value=int(value))

    with row5_2:
        st.metric(label='**Apátridas**',
                  value=df_country['stateless'] if not df_country_sex.empty else 0)

    with row5_3:
        value_fem = round((df_country_sex.loc[0, 'f_total'] * 100) /
                          df_country_sex.loc[0, 'total'], 2) if not df_country_sex.empty else 0
        st.metric(label='**Mujeres**', value=f'{value_fem:.2f}%')

    with row5_4:
        value_masc = round((df_country_sex.loc[0, 'm_total'] * 100) /
                           df_country_sex.loc[0, 'total'], 2) if not df_country_sex.empty else 0
        # Fuente: https://zetcode.com/python/fstring/
        st.metric(label='**Hombres**', value=f'{value_masc:.2f}%')

    # Otros datos.
    row6_1, row6_2, row6_3 = st.columns((3, 3, 1))

    # Gráfico cantidad y tipo de población.
    with row6_1:
        # Defino el set de datos para dibujar el gráfico.
        df_graph_3 = pd.melt(df_country, id_vars='year',
                             value_vars=columns_names)
        df_graph_3 = df_graph_3.loc[(df_graph_3.value != 0)]

        # Llamo a la función para dibujar el gráfico.
        if not df_graph_3.empty:
            af.plot_population(df_graph_3)
            st.caption('Fuente: Elaboración propia con datos extraídos de ACNUR.')
        else:
            st.write('**No hay datos para mostrar**')

    # Mapa procedencia geográfica
    with row6_2:
        # Llamo a la función para dibujar el mapa.
        if not df_graph_3.empty:
            af.map_refugee(df_map_3)
            st.caption('Fuente: Elaboración propia con datos extraídos de ACNUR.')
