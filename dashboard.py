# Run this app with `python dashboard.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc
from visualization import data, graphs, layouts
from dash.dependencies import Input, Output

app = Dash(
    __name__,
    meta_tags=[
        {"name": "GDM-testing", "content": "width=device-width, initial-scale=1"}
    ],
)
app.title = "GDM-testing"
server = app.server
app.config["suppress_callback_exceptions"] = False

available_ids = data.get_available_experiment_ids()
if len(available_ids) == 0:
    raise Exception("No experiments available")


@app.callback(
    [Output("app-content", "children")],
    [Input("app-tabs", "value")],
    [Input("id-select-dropdown", "value")],
)
def render_content(tab_switch: str, experiment_id: str) -> tuple:
    """Render the content of the page

    Args:
        tab_switch (str): Chosen tab
        experiment_id (str): ID of experiment chosen in dropdown

    Returns:
        tuple: Children of the subpage
    """
    if tab_switch == "tab1":
        configs = data.get_configs(experiment_id)
        return (
            html.Div(
                id="status-container",
                children=[
                    html.Div(
                        id="settings-container",
                        children=[
                            layouts.generate_section_banner("Run-configurations:"),
                            data.format_configs(configs),
                        ],
                    ),
                ],
            ),
        )
    else:
        experiment_data = data.get_data(experiment_id)
        return (
            html.Div(
                id="graphs-container",
                children=[
                    html.Div(
                        id="graph-container-1",
                        children=graphs.create_graphs(experiment_data),
                    ),
                ],
            ),
        )


# We initialize a layout that has to contain the components used for callbacks
app.layout = html.Div(
    id="big-app-container",
    children=[
        html.Div(
            id="banner",
            className="banner",
            children=[
                html.Div(
                    id="id-select-menu",
                    children=[
                        html.H4("Select Experiment ID:"),
                        dcc.Dropdown(
                            id="id-select-dropdown",
                            options=list(
                                {"label": param, "value": param}
                                for param in available_ids
                            ),
                            value=available_ids[0],
                        ),
                    ],
                ),
                html.Div(
                    id="banner-text",
                    children=[
                        html.H5("GDM-testing"),
                        html.H6(f"Framework for testing GDMs based on four metrics"),
                    ],
                ),
            ],
        ),
        layouts.build_tabs(),
        html.Div(
            id="app-container",
            children=[
                html.Div(id="app-content"),
            ],
        ),
    ],
)


# Running the server
if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
