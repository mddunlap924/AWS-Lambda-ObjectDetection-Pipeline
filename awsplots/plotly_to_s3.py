import datetime
from PIL import Image
import plotly.graph_objects as go
import plotly.express as px


def upload_html_to_s3(tmp_dir, s3, bucket, fig):
    """ Export the Plotly Graph as HTML and Upload on S3 Bucket Static Website """
    # Store html in temporary folder and then upload to S3 bucket
    fig.write_html(tmp_dir + 'index_' + bucket + '.html')

    # Upload index.html file to S3 bucket
    s3.upload_file(Filename=tmp_dir + 'index_' + bucket + '.html',
                   Bucket=bucket,
                   Key='index.html',
                   ExtraArgs={'ContentType': 'text/html'},
                   )
    print(f'Uploaded HTML to S3 {bucket}')
    return


def create_plotly_line_fig(df):
    """ Create a Plotly Line Chart Graph to Plot Database Counts per Object """
    # Change Date into a Datetime Object for more plotting functionality
    df['date'] = df['date'].apply(lambda x: datetime.datetime.strptime(x, "%d-%b-%Y"))

    # Initialize figures for line plots and YoloV5 image with bounding boxes
    fig_line_plot = go.Figure()

    # Create Line Plot
    for key in df.keys().to_list():
        if key != 'date':
            fig_line_plot.add_trace(
                go.Scatter(x=df.date,
                           y=df[key],
                           name=key.capitalize())
            )

    # Add Annotations and Buttons for Line Plot
    fig_line_plot.update_layout(
        updatemenus=[go.layout.Updatemenu(
            active=0,
            buttons=list(
                [dict(label='All',
                      method='update',
                      args=[{'visible': [True, True, True, True, True, True]},
                            {'title': 'All',
                             'showlegend': True}]),
                 dict(label='Bicycle',
                      method='update',
                      args=[{'visible': [True, False, False, False, False, False]},
                            # the index of True aligns with the indices of plot traces
                            {'title': 'Bicycle',
                             'showlegend': True}]),
                 dict(label='Car',
                      method='update',
                      args=[{'visible': [False, True, False, False, False, False]},
                            {'title': 'Car',
                             'showlegend': True}]),
                 dict(label='Motorcycle',
                      method='update',
                      args=[{'visible': [False, False, True, False, False, False]},
                            {'title': 'Motorcycle',
                             'showlegend': True}]),
                 dict(label='Bus',
                      method='update',
                      args=[{'visible': [False, False, False, True, False, False]},
                            {'title': 'Bus',
                             'showlegend': True}]),
                 dict(label='Truck',
                      method='update',
                      args=[{'visible': [False, False, False, False, True, False]},
                            {'title': 'Truck',
                             'showlegend': True}]),
                 dict(label='Person',
                      method='update',
                      args=[{'visible': [False, False, False, False, False, True]},
                            {'title': 'Person',
                             'showlegend': True}]),
                 ])
        )
        ])

    # Include plot title and axis labels
    fig_line_plot.update_layout(xaxis_title='Date',
                                yaxis_title='Count',
                                title={
                                    'text': "Counted Objects using YoloV5 vs. Date",
                                    'y': 0.92,
                                    'x': 0.5,
                                    'xanchor': 'center',
                                    'yanchor': 'top'},
                                )
    return fig_line_plot


def create_plotly_img_fig(tmp_dir):
    """ Plotly Zoom on Static Images or Imshow """
    # https://plotly.com/python/images/
    # https://plotly.com/python/imshow/

    # Load image from temporary directory
    img_path = tmp_dir + 'Single_Image.jpg'
    img = Image.open(img_path)

    # Plotly graph showing multi-channel image
    fig = px.imshow(img)
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)
    return fig
