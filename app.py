import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq
from datetime import datetime

import plotly.graph_objs as go

from FactoryData import FactoryData

app = dash.Dash(__name__)

process_names = [
    'cycle_time',
    'time_to_complete',
    'safety_materials',
    'safety_manufacturing',
    'safety_packing',
    'precursor_level',
    'reagent_level',
    'catalyst_level',
    'packaging_level',
    'production_levels',
]

fdata = FactoryData(process_names)


app.layout = html.Div(id='app-content', children=[
    html.Div(className='indicator-box', id='graph-container', children=[
        html.H4('Production levels'),
        dcc.Graph(
            id='production-graph',
            figure=go.Figure({
                'data': [{'x': [], 'y':[]}],
                'layout': go.Layout(
                    yaxis={
                        'title': 'Total units'
                    },
                    height=505
                )
            }),
        )
    ]),
    html.Div(id='status-container', children=[
        html.Div(className='indicator-box', children=[
            daq.StopButton(id='stop-button')
        ]),
        html.Div(className='indicator-box', children=[
            daq.StopButton(id='new-batch', buttonText='Start new batch'),
        ]),
        html.Div(className='indicator-box', children=[
            html.H4("Batch number"),
            daq.LEDDisplay(
                id='batch-number',
                value="124904",
                color='blue'
            ),
            html.Div(
                id='batch-started'
            )
        ]),
        html.Div(className='indicator-box', id='safety-status', children=[
            html.H4("Safety checks by room"),
            daq.Indicator(
                id='room-one-status',
                value='on',
                color='green',
                label='Materials'
            ),
            daq.Indicator(
                id='room-two-status',
                value='on',
                color='orange',
                label='Manufacturing'
            ),
            daq.Indicator(
                id='room-three-status',
                value='on',
                color='red',
                label='Packing'
            )
        ]),
    ]),
    html.Br(),
    html.Div(className='indicator-box', children=[
        html.H4('Cycle time (hours)'),
        daq.Gauge(
            id='cycle-time',
            min=0, max=10,
            showCurrentValue=True,
            color={
                "gradient": True,
                "ranges": {
                    "green": [0, 6],
                    "yellow": [6, 8],
                    "red": [8, 10]
                }
            },
        )
    ]),
    html.Div(className='indicator-box', children=[
        html.H4('Time to completion (hours)'),
        daq.Gauge(
            id='time-to-completion',
            min=0, max=10,
            showCurrentValue=True,
            color='blue'
        )
    ]),
    html.Div(className='indicator-box', children=[
        html.H4('Substance levels'),
        daq.GraduatedBar(
            id='precursor-levels',
            min=0, max=100,
            step=5,
            color='blue',
            label='Precursor'
        ),
        daq.GraduatedBar(
            id='reagent-levels',
            min=0, max=100,
            step=5,
            color='blue',
            label='Reagent'
        ),
        daq.GraduatedBar(
            id='catalyst-levels',
            min=0, max=100,
            step=5,
            color='blue',
            label='Catalyst'
        ),
        daq.GraduatedBar(
            id='packaging-levels',
            min=0, max=100,
            step=5,
            color='blue',
            label='Packaging materials'
        )
    ]),
    html.Div(
        className='indicator-box',
        children=[
            html.H4("Manufacturing room temperature"),
            daq.Thermometer(
                id='manufacturing-temp', 
                min=50, max=90,
                value=70,
                color='blue'
            )
        ]
    ),
    dcc.Interval(
        id='polling-interval',
        n_intervals=0,
        interval=1*1000,
        disabled=True
    ),
    dcc.Store(
        id='annotations-storage',
        data=[]
    )
])

@app.callback(
    [Output('polling-interval', 'disabled'),
     Output('stop-button', 'buttonText')],
    [Input('stop-button', 'n_clicks')],
    state=[State('polling-interval', 'disabled')]
)
def stop_production(_, current):
    return not current, "stop" if current else "start"


@app.callback(
    [Output('batch-number', 'value'),
     Output('annotations-storage', 'data'),
     Output('batch-started', 'children')],
    [Input('new-batch', 'n_clicks')],
    state=[State('batch-number', 'value'),
           State('annotations-storage', 'data'),
           State('polling-interval', 'n_intervals'),
           State('production-graph', 'figure')]
)
def new_batch(_, current_batch, current_annotations, n_intervals, current_fig):

    timestamp = datetime.now().strftime('%H:%M:%S %D')

    if len(current_fig['data'][0]['x']) == 0:
        return current_batch, current_annotations, 'Batch started: {}'.format(timestamp)

    marker_x = current_fig['data'][0]['x'][-1]
    marker_y = current_fig['data'][0]['y'][-1]

    current_annotations.append({
        'x': marker_x,
        'y': marker_y,
        'text': 'Batch no. {}'.format(str(int(current_batch) + 1)),
        'arrowhead': 0,
        'bgcolor': 'blue',
        'font': {'color': 'white'}
    })

    return str(int(current_batch) + 1), current_annotations, 'Batch started: {}'.format(timestamp)


@app.callback(
    [Output('cycle-time', 'value'),
     Output('time-to-completion', 'value'),
     Output('room-one-status', 'color'),
     Output('room-two-status', 'color'),
     Output('room-three-status', 'color'),
     Output('precursor-levels', 'value'),
     Output('reagent-levels', 'value'),
     Output('catalyst-levels', 'value'),
     Output('packaging-levels', 'value'),
     Output('production-graph', 'figure')],
    [Input('polling-interval', 'n_intervals')],
    state=[State('production-graph', 'figure'),
           State('annotations-storage', 'data')]
)
def update_stats(n_intervals, current_fig, current_annotations):

    stats = [fdata.get_data()[pname] for pname in process_names]

    current_data = current_fig['data'][0]
    
    new_data = [{'x': current_data['x'].append(n_intervals/2),
                 'y': current_data['y'].append(
                     current_data['y'][-1] + stats[-1]
                     if len(current_data['y']) > 0
                     else stats[-1] 
                 )}]

    current_fig['layout'].update(annotations=current_annotations)
    current_fig.update(
        figure=go.Figure(
            data=new_data
        )
    )

    stats = stats[:-1]
    stats.append(current_fig)

    return tuple(stats)


if __name__ == '__main__':
    app.run_server(debug=True)
