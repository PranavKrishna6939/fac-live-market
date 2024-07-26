import streamlit as st
import datetime
import pandas as pd
import plotly.graph_objects as go
import time
import numpy as np

st.set_page_config(layout="wide")
st.title(":red[Candle-Stick] Chart")
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp {
        max-width: 100%;
        padding: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def resample_ohlc(df, timeframe):
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df = df.set_index('Timestamp')
    ohlc = df['Spot'].resample(timeframe).ohlc()
    return ohlc.reset_index()

def load_data():
    # Replace this with the path to your actual CSV file
    today = datetime.datetime.now().date().strftime("%d_%m_%Y")
    now = datetime.datetime.now()
    offset = datetime.timedelta(hours=5, minutes=30)
    tstamp = now + offset
    tstamp = tstamp.strftime("%H:%M:%S")
    if ((tstamp > "09:15:00") and (tstamp < "15:30:00")):
        df = pd.read_csv('RawLogs_{today}.csv')
    else:
        df = pd.read_csv('example.csv')
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    return df

def calculate_sar(data):
    af = 0.02
    af_step = 0.02
    af_max = 0.2
    trend = 1
    sar = data['low'].iloc[0]
    ep = data['high'].iloc[0]
    sar_list = [sar]

    for i in range(1, len(data)):
        if trend == 1:
            sar = sar + af * (ep - sar)
            if sar > data['low'].iloc[i]:
                trend = 0
                sar = ep
                ep = data['low'].iloc[i]
                af = af_step
            else:
                if data['high'].iloc[i] > ep:
                    ep = data['high'].iloc[i]
                    af = min(af + af_step, af_max)
        else:
            sar = sar - af * (sar - ep)
            if sar < data['high'].iloc[i]:
                trend = 1
                sar = ep
                ep = data['high'].iloc[i]
                af = af_step
            else:
                if data['low'].iloc[i] < ep:
                    ep = data['low'].iloc[i]
                    af = min(af + af_step, af_max)
        
        sar_list.append(sar)

    return pd.Series(sar_list, index=data.index)

def create_candlestick_chart(df, timeframe, show_sar):
    ohlc_data = resample_ohlc(df, timeframe)
    ohlc_data['SAR'] = calculate_sar(ohlc_data)
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=ohlc_data['Timestamp'],
        open=ohlc_data['open'],
        high=ohlc_data['high'],
        low=ohlc_data['low'],
        close=ohlc_data['close'],
        name='Candlesticks'
    ))

    if show_sar:
        fig.add_trace(go.Scatter(
            x=ohlc_data['Timestamp'],
            y=ohlc_data['SAR'],
            mode='markers',
            marker=dict(
                color=np.where(ohlc_data['SAR'] > ohlc_data['close'], 'red', 'green'),
                symbol='diamond',
                size=4
            ),
            name='Parabolic SAR'
        ))

    fig.update_layout(
        xaxis_title='Timestamp',
        yaxis_title='Market Price',
        xaxis_rangeslider_visible=True,
        height=800  # Increase the height of the chart
    )

    return fig

def main():
    col1, col2 = st.columns([3, 1])
    with col1:
        timeframe = st.selectbox(
            'Select Timeframe',
            ('1min', '2min', '5min', '15min', '30min', '1H')
        )
    with col2:
        show_sar = st.checkbox('Show Parabolic SAR', value=True)

    chart_placeholder = st.empty()

    while True:
        df = load_data()

        fig = create_candlestick_chart(df, timeframe, show_sar)
        chart_placeholder.plotly_chart(fig, use_container_width=True)

        time.sleep(1)

if __name__ == '__main__':
    main()
