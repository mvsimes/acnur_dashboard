# =============================================================================
# App Functions
#
# María Victoria Simes.
# Open Data & Visualización dinámica.
# Master en Data Science y Big Data 2022 - 2023
# =============================================================================

import streamlit as st
import math
import pydeck as pdk
import pandas as pd
from bokeh.models import ColumnDataSource, FactorRange, BasicTickFormatter
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
from plotnine import *

poptype_2_column = {'Apátridas': 'stateless',
                    'Desplazados internos': 'internally_displaced',
                    'Desplazados internos retornados': 'returned_internally_displaced',
                    'Refugiados': 'refugees',
                    'Refugiados retornados': 'returned_refugees',
                    'Solicitantes de asilo': 'asylum_seekers',
                    'Venezolanos desplazados': 'other_need',
                    'Otras poblaciones': 'other_concern',
                    'Todas': 'Todas'}

column_2_poptype = {name_column: spanish for spanish, name_column in
                    poptype_2_column.items()}

petitions_2_column = {'Solicitudes': 'total_applied',
                      'Status de refugiado reconocido': 'refugee_recognized',
                      'Otro status reconocido': 'other_recognized',
                      'Status de refugiado rechazado': 'asylum_rejected',
                      'Caso cerrado': 'claims_closed'}

column_2_petitions = {name_column: spanish for spanish, name_column in
                      petitions_2_column.items()}


def continent_selectbox(exclude_continents=[], value=1, suffix='', index=0):
    all_continents = ['Africa', 'América del Norte', 'Apátrida', 'Asia',
                      'Desconocido', 'Europa', 'Latinoamérica y el Caribe',
                      'Oceania', 'Todos']

    continents_2_show = [c for c in all_continents if c not in
                         exclude_continents]

    selectbox_name = '**Continente**' if not suffix else f'**Continente {suffix}**'

    continent = st.selectbox(selectbox_name, continents_2_show, key=value, index=index)

    # Diccionario de las opciones a elegir como clave y los valores de la columna
    # 'continent_origin_country'.
    continent_2_category = {'Africa': 'Africa',
                            'América del Norte': 'Northern America',
                            'Apátrida': 'Stateless',
                            'Asia': 'Asia',
                            'Desconocido': 'Unknown',
                            'Europa': 'Europe',
                            'Latinoamérica y el Caribe':
                                'Latin America and the Caribbean',
                            'Oceania': 'Oceania',
                            'Todos':  'Todos'}

    return continent_2_category[continent]


def map_movement_year(df_map_1):
    # Slider widget para filtrar por año
    year = st.selectbox(
        '**Selecciona un año**',
        range(1970, max(df_map_1['year'])), index=18)

    # Filtro el set de datos por el año elegido.
    df_map_1 = df_map_1.loc[(df_map_1.year == year)]

    # A partir de 1995 el flujo de refugiados mundial aumenta de forma exponencial y la
    # visualización se torna inentendible. Es por eso que he decidido agregar la opción de
    # filtrar por continente cuando el usuario quiera consultar más alla del año 1995.
    if year > 1995:
        st.markdown(
            """
            **Debido al aumento del flujo de refugiados mundial, elige un
            continente para una mejor visualización.**
            """
        )

        continent_origin = continent_selectbox(['Apátrida',
                                                'Desconocido',
                                                'Todos'])

        df_map_1 = df_map_1.loc[df_map_1.continent_origin_country ==
                                continent_origin]

    # Specify a deck.gl ArcLayer
    arc_layer = pdk.Layer(
        "ArcLayer",
        data=df_map_1,
        get_source_position=['longitude_origin_country',
                             'latitude_origin_country'],
        get_target_position=['longitude_asylum_country',
                             'latitude_asylum_country'],
        get_width=0.4 if year > 1995 else 1,
        get_source_color=[185, 45, 4],
        get_target_color=[250, 253, 197]
    )

    view_state = pdk.ViewState(latitude=0, longitude=0, zoom=1,)

    st.pydeck_chart(pdk.Deck(arc_layer, initial_view_state=view_state))
# Fuente: https://pydeck.gl/gallery/arc_layer.html


def population_selectbox():
    option_type_refugee = st.selectbox('**Tipo de población**',
                                       ('Apátridas',
                                        'Desplazados internos',
                                        'Desplazados internos retornados',
                                        'Refugiados',
                                        'Refugiados retornados',
                                        'Solicitantes de asilo',
                                        'Venezolanos desplazados',
                                        'Otras poblaciones',
                                        'Todas'),
                                       index=3)

    return poptype_2_column[option_type_refugee], option_type_refugee


def plot_evolution_time(df_graph_1, column_name, option_type_refugee):
    if df_graph_1.empty:
        st.write('No existen datos para la selección realizada, prueba otra.')
    else:
        # Realizo algunos cambios en el data frame para graficar.
        max_value = max(df_graph_1[column_name])

        if math.log10(max_value) < 3:
            denominator = 1
            suffix = ''
        elif math.log10(max_value) < 6:
            denominator = 1000
            suffix = '(en miles)'
        else:
            denominator = 1000000
            suffix = '(en millones)'

        df_graph_1[column_name] = df_graph_1[column_name] / denominator

        column_with_suffix = f'{option_type_refugee} {suffix}'

        df_graph_1 = df_graph_1.rename(columns={'year': 'Año',
                                                column_name: column_with_suffix})

        df_graph_1['Año'] = df_graph_1['Año'].astype(str)

        # Defino el gráfico con los filtros definidos.
        st.line_chart(data=df_graph_1, x='Año', y=column_with_suffix)


def plot_evolution_time_all(df_graph_1):
    if df_graph_1.empty:
        st.write('No existen datos para la selección realizada, prueba otra.')
    else:
        # Realizo algunos cambios en el data frame para graficar.
        max_value = max(df_graph_1.iloc[:, 1])

        if math.log10(max_value) < 3:
            denominator = 1
            suffix = ''
        elif math.log10(max_value) < 6:
            denominator = 1000
            suffix = 'en miles'
        else:
            denominator = 1000000
            suffix = 'en millones'

        df_graph_1.iloc[:, 1:] = df_graph_1.iloc[:, 1:] / denominator

        df_graph_1 = df_graph_1.rename(columns={'year': 'Año'} |
                                       column_2_poptype)

        df_graph_1['Año'] = df_graph_1['Año'].astype(str)

        # Defino el gráfico con los filtros definidos.
        st.markdown(f'Población expresada en millones {suffix}')
        st.line_chart(data=df_graph_1, x='Año')


def petition_multiselect():
    option_petition = st.multiselect('**Solicitudes y tipos de resoluciones**',
                                     ('Solicitudes',
                                      'Status de refugiado reconocido',
                                      'Otro status reconocido',
                                      'Status de refugiado rechazado',
                                      'Caso cerrado'), default='Solicitudes')

    selection = [petitions_2_column[o] for o in option_petition]
    return selection


def plot_petitions_time(df_graph_2, columns_names):
    # Para poder realizar este gráfico tengo que convertir las columnas en filas.
    df_graph_2 = pd.melt(df_graph_2, id_vars='year',
                         value_vars=columns_names).sort_values(['year',
                                                                'variable'])

    # Renombro las columnas a su versión en español.
    df_graph_2['variable'] = df_graph_2['variable'].apply(lambda c:
                                                          column_2_petitions[c])

    # Defino los ejes del gráfico.
    axis_x = list(zip(df_graph_2['year'].astype(str), df_graph_2['variable']))
    axis_y = df_graph_2['value']

    # Defino la estructura 'ColumnDataSource', la cual mapea los nombres de las
    # columnas en secuencias o arrays, y es requerimiento de la librería Bokeh.
    source = ColumnDataSource(data=dict(x=axis_x,
                                        counts=axis_y,
                                        label=df_graph_2['variable']))

    # Defino una paleta de colores para el gráfico.
    palette = ['#14848f', '#d4c44e', '#5ab4bd', '#f58624', '#c27615']

    # Figure: es otra de las estructuras requeridas por Bokeh para graficar y
    # sirve para definir cuestiones relacionas a la visualización.
    graph_2 = figure(
        x_range=FactorRange(*axis_x),
        sizing_mode='stretch_both',
        height=400,
        x_axis_label='Año',
        y_axis_label='',
    )

    # Defino el gráfico de barras con sus parámetros.
    graph_2.vbar(x='x',
                 top='counts',
                 width=1,
                 source=source,
                 line_color="white",
                 fill_color=factor_cmap(
                     'x',
                     palette=palette,
                     factors=df_graph_2['variable'].unique(),
                     start=1,
                     end=5),
                 legend_group='label')

    # Ajusto algunos detalles estéticos del gráfico.
    graph_2.xgrid.grid_line_color = None
    graph_2.xaxis.major_label_text_font_size = '1px'
    graph_2.xaxis.major_label_text_color = 'white'
    graph_2.xaxis.major_tick_line_color = 'white'
    graph_2.xaxis.axis_line_color = 'white'
    graph_2.yaxis.axis_line_color = 'white'
    graph_2.yaxis.major_tick_line_color = 'white'
    graph_2.yaxis.minor_tick_line_color = 'white'
    graph_2.yaxis.major_label_text_color = '#9396a5'
    graph_2.yaxis.formatter = BasicTickFormatter(use_scientific=False)

    st.bokeh_chart(graph_2)
# Fuente: https://docs.bokeh.org/en/latest/docs/examples/basic/bars/nested_colormapped.html


def country_selectbox(df, continent_election, variable):
    countries = df.loc[(df.continent == continent_election)]
    countries = countries[variable]
    country = st.selectbox('**País**', countries)

    return country


def plot_population(df_graph_3):
    df_graph_3['variable'] = df_graph_3['variable'].apply(lambda x: column_2_poptype[x])

    max_value = max(df_graph_3['value'])
    if math.log10(max_value) < 3:
        denominator = 1
        suffix = ''
        suffix_label = ''
    elif math.log10(max_value) < 6:
        denominator = 1000
        suffix = '(en miles)'
        suffix_label = 'm'
    else:
        denominator = 1000000
        suffix = '(en millones)'
        suffix_label = 'M'

    df_graph_3['value'] = df_graph_3['value'] / denominator

    palette_2 = {'Apátridas': '#14848f',
                 'Desplazados internos': '#d4c44e',
                 'Desplazados internos retornados': '#5ab4bd',
                 'Refugiados': '#f58624',
                 'Refugiados retornados': '#c27615',
                 'Solicitantes de asilo': '#1d445e',
                 'Venezolanos desplazados': '#b5d63d',
                 'Otras poblaciones': '#ffae49'}

    graph_3 = ggplot(df_graph_3, aes(x='variable', y='value', fill='variable'))\
        + geom_bar(stat='identity', width=0.5)\
        + geom_text(aes(label='value'), nudge_y=7, color='#9396a5',
                    format_string='{:.2f}' + suffix_label)\
        + scale_x_discrete(name='Tipo de población')\
        + scale_y_continuous(name=f'Cantidad de personas {suffix}')\
        + scale_fill_manual(values=palette_2)\
        + coord_flip()\
        + theme(panel_background=element_rect(fill='white'),
                axis_title=element_text(color='#9396a5', size=9),
                axis_text=element_text(color='#9396a5', size=8),
                axis_ticks=element_line(color='#9396a5'),
                legend_position='none')

    st.pyplot(ggplot.draw(graph_3))


def map_refugee(df_map_3):
    icon_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Yara_Said_refugee_flag.svg/640px-Yara_Said_refugee_flag.svg.png'
    icon_data = {
        "url": icon_url,
        "width": 150,
        "height": 100,
    }

    data = df_map_3
    data["icon_data"] = None
    for i in data.index:
        data["icon_data"][i] = icon_data

    icon_layer = pdk.Layer(
        type="IconLayer",
        data=data,
        get_icon="icon_data",
        get_size=4,
        size_scale=4,
        get_position=['longitude',
                      'latitude'],
    )

    view_state = pdk.ViewState(latitude=0, longitude=0, zoom=1.7,)
    st.pydeck_chart(pdk.Deck(icon_layer, initial_view_state=view_state, map_style='light'))
# Fuente: https://pydeck.gl/gallery/icon_layer.html
