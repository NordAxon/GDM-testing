import plotly.express as px
from dash import html, dcc
import plotly.figure_factory as ff
import pandas as pd
from visualization import layouts

# We initialize a list of colors to use in plotting
colors = [
    "#DC143C",
    "#32CD32",
    "#00CED1",
    "#4169E1",
    "#DA70D6",
    "#FF69B4",
    "#F4A460",
    "#add8e6",
    "#fffafa",
]
cdm = {}


def create_graphs(data: dict) -> list:
    """Creates graphs of statistics

    Args:
        data (dict): Dict with dataframes from database

    Returns:
        list: List of children graphs
    """
    run_id_to_testee = pd.Series(
        data["configs"].testee_id.values, index=data["configs"].run_id
    ).to_dict()
    i = 0
    global cdm
    cdm = {}
    for _, testee_id in run_id_to_testee.items():
        cdm[testee_id] = colors[i]
        i += 1
        if i == len(colors):
            i = 0
    vocsz = create_vocsz(data["vocsz"], run_id_to_testee)
    tox = create_tox(data["tox"], run_id_to_testee)
    readind = create_readind(data["readind"], run_id_to_testee)
    coher = create_coher(data["coher"], run_id_to_testee)
    return [
        layouts.generate_section_banner("Readability index"),
        readind,
        layouts.generate_section_banner("Coherence"),
        coher,
        layouts.generate_section_banner("Toxicity"),
        tox,
        layouts.generate_section_banner("Vocabulary size"),
        vocsz,
    ]


def create_vocsz(vocsz, run_id_to_testee):
    temp = vocsz.groupby(["run_id", "word", "word_rank"], as_index=False).sum()
    temp["testee_id"] = temp.run_id.apply(lambda x: run_id_to_testee[x])
    word_nbr = pd.DataFrame(temp.testee_id.value_counts(sort=False))
    word_nbr["testee"] = word_nbr.index

    fig1 = px.bar(
        word_nbr,
        x="testee_id",
        y="testee",
        color="testee",
        hover_data=["testee_id"],
        text="testee_id",
        labels={"testee": "testee id", "testee_id": "vocabulary size"},
        color_discrete_map=cdm,
        title="Number of used words",
    )
    fig1.update_layout(
        {
            "plot_bgcolor": "rgba(0, 0, 0, 0)",
            "paper_bgcolor": "rgba(0, 0, 0, 0)",
            "font_color": "#f3f5f4",
        }
    )
    fig2 = px.ecdf(
        temp,
        x="word_rank",
        y="frequency",
        color="testee_id",
        range_x=[0, 5000],
        labels={
            "word_rank": "word rank",
            "testee_id": "testee id",
        },
        marginal="rug",
        color_discrete_map=cdm,
        title="Word rank distribution",
    )
    fig2.update_layout(
        {
            "plot_bgcolor": "rgba(0, 0, 0, 0)",
            "paper_bgcolor": "rgba(0, 0, 0, 0)",
            "font_color": "#f3f5f4",
        }
    )
    return html.Div(
        id="vocsz",
        children=[
            dcc.Graph(id="vocsz1", figure=fig1),
            dcc.Graph(id="vocsz1", figure=fig2),
        ],
    )


def create_tox(tox, run_id_to_testee):
    tox_agg = tox.groupby(["run_id", "toxicity_type"], as_index=False)[
        "toxicity_level"
    ].mean()
    tox_agg["testee_id"] = tox_agg.run_id.apply(lambda x: run_id_to_testee[x])
    temp1 = tox_agg.loc[tox_agg.toxicity_type == "toxicity"]
    temp2 = tox_agg.loc[tox_agg.toxicity_type != "toxicity"]
    fig1 = px.bar(
        temp1,
        x="testee_id",
        y="toxicity_level",
        color="testee_id",
        text=[str(round(val, 4)) for val in temp1.toxicity_level],
        labels={"toxicity_level": "mean toxicity level", "testee_id": "testee id"},
        color_discrete_map=cdm,
        title="Mean toxicity level per conversation",
    )
    fig1.update_layout(
        {
            "plot_bgcolor": "rgba(0, 0, 0, 0)",
            "paper_bgcolor": "rgba(0, 0, 0, 0)",
            "font_color": "#f3f5f4",
        }
    )
    fig2 = px.bar(
        temp2,
        x="toxicity_type",
        y="toxicity_level",
        color="testee_id",
        barmode="group",
        labels={
            "toxicity_level": "mean toxicity level",
            "testee_id": "vocabulary size",
            "toxicity_type": "toxicity type",
        },
        color_discrete_map=cdm,
        title="Mean toxicity levels per conversation by type",
    )
    fig2.update_layout(
        {
            "plot_bgcolor": "rgba(0, 0, 0, 0)",
            "paper_bgcolor": "rgba(0, 0, 0, 0)",
            "font_color": "#f3f5f4",
        }
    )
    return html.Div(
        id="tox",
        children=[
            dcc.Graph(id="tox1", figure=fig2),
            dcc.Graph(id="tox2", figure=fig1),
        ],
    )


def create_readind(readind, run_id_to_testee):
    readind["testee_id"] = readind.run_id.apply(lambda x: run_id_to_testee[x])
    ids = []
    indxs = []
    for testee_id, df in readind.groupby("testee_id"):
        ids.append(testee_id)
        indxs.append(df.readab_index)
    indxs.reverse()
    ids.reverse()
    fig1 = px.box(
        readind,
        x="testee_id",
        y="readab_index",
        color="testee_id",
        labels={"readab_index": "readability index", "testee_id": "testee id"},
        color_discrete_map=cdm,
        title="Readability index distributions",
    )
    fig1.update_layout(
        {
            "plot_bgcolor": "rgba(0, 0, 0, 0)",
            "paper_bgcolor": "rgba(0, 0, 0, 0)",
            "font_color": "#f3f5f4",
        }
    )
    fig2 = ff.create_distplot(
        indxs, ids, show_hist=False, colors=[cdm[id] for id in ids]
    )
    fig2.update_layout(
        {
            "plot_bgcolor": "rgba(0, 0, 0, 0)",
            "paper_bgcolor": "rgba(0, 0, 0, 0)",
            "font_color": "#f3f5f4",
            "title": "Readability index distributions",
            "xaxis_title": "readability index",
            "yaxis_title": "probability",
        }
    )
    return html.Div(
        id="readind",
        children=[
            dcc.Graph(id="readind1", figure=fig2),
            dcc.Graph(id="readind2", figure=fig1),
        ],
    )


def create_coher(coher, run_id_to_testee):
    coher["testee_id"] = coher.run_id.apply(lambda x: run_id_to_testee[x])
    fig1 = px.ecdf(
        coher,
        x="neg_pred",
        color="testee_id",
        # Lower bounds
        range_x=[0, 0.0001],
        range_y=[0, 1],
        labels={
            "neg_pred": "predicted probability of non-coherence",
            "testee_id": "testee id",
        },
        marginal="rug",
        color_discrete_map=cdm,
        title="Low non-coherence distribution",
    )
    fig1.update_layout(
        {
            "plot_bgcolor": "rgba(0, 0, 0, 0)",
            "paper_bgcolor": "rgba(0, 0, 0, 0)",
            "font_color": "#f3f5f4",
        }
    )
    fig2 = px.ecdf(
        coher,
        x="neg_pred",
        color="testee_id",
        # Upper bounds
        range_x=[0.9, 1],
        range_y=[0.95, 1],
        labels={
            "neg_pred": "predicted probability of non-coherence",
            "testee_id": "testee id",
        },
        marginal="rug",
        color_discrete_map=cdm,
        title="High non-coherence distribution",
    )
    fig2.update_layout(
        {
            "plot_bgcolor": "rgba(0, 0, 0, 0)",
            "paper_bgcolor": "rgba(0, 0, 0, 0)",
            "font_color": "#f3f5f4",
        }
    )
    return html.Div(
        id="coher",
        children=[
            dcc.Graph(id="coher1", figure=fig1),
            dcc.Graph(id="coher2", figure=fig2),
        ],
    )
