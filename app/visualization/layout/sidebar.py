from dash import html, dcc
import dash_bootstrap_components as dbc

class Sidebar:
    def __init__(self, df):
        self.df = df

    def create(self):
        return dbc.Col([
            html.H4('Filters', 
                   style={
                       'font-size': '1.1rem',
                       'font-weight': '500',
                       'color': '#444',
                       'margin-bottom': '0.5rem'
                   }),
            html.Hr(style={'margin': '0.5rem 0'}),
            
            # UMAP Parameters
            html.Label('UMAP Parameters'),
            dbc.Row([
                dbc.Col([
                    html.Label('n_neighbors'),
                    dcc.Input(
                        id='n-neighbors-input',
                        type='number',
                        value=15,
                        min=2,
                        max=100,
                        step=1,
                        style={'width': '100%'}
                    ),
                ], width=6),
                dbc.Col([
                    html.Label('min_dist'),
                    dcc.Input(
                        id='min-dist-input',
                        type='number',
                        value=0.1,
                        min=0.0,
                        max=1.0,
                        step=0.1,
                        style={'width': '100%'}
                    ),
                ], width=6),
            ]),
            html.Br(),
            
            # Subject filter
            html.Label('Subject ID'),
            dcc.Dropdown(
                id='subject-filter',
                options=[{'label': str(id), 'value': id} 
                        for id in self.df['subject_id'].unique()],
                multi=True,
                placeholder='Select subjects...'
            ),
            html.Br(),
            
            # Stage filter
            html.Label('Training Stage'),
            dcc.Dropdown(
                id='stage-filter',
                options=[{'label': str(stage), 'value': stage} 
                        for stage in self.df['current_stage_actual'].unique()],
                multi=True,
                placeholder='Select stage...'
            ),
            html.Br(),

            # Task filter
            html.Label('Task'),
            dcc.Dropdown(
                id='task-filter',
                options=[{'label': str(task), 'value': task} 
                        for task in self.df['task'].unique()],
                multi=True,
                placeholder='Select task...'
            ),
            html.Br(),
            
            # Session range filter
            html.Label('Session Range'),
            dcc.RangeSlider(
                id='session-range',
                min=self.df['session'].min(),
                max=self.df['session'].max(),
                step=1,
                marks={i: str(i) for i in range(
                    self.df['session'].min(), 
                    self.df['session'].max()+1, 
                    5)},
                value=[self.df['session'].min(), self.df['session'].max()]
            ),
            
            # Processing State Card
            dbc.Card([
                dbc.CardHeader('Processing State'),
                dbc.CardBody(id='processing-state')
            ])
        ], width=2)