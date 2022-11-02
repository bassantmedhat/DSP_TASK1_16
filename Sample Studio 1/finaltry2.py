#################################################################
# ########################## Sampling Studio ############################
# TEAM MEMBERS:Mohamed Naaser        Mahmoud Hamdy
#              Bassant Medhat        Yousr Ashraf
########################## Imports #########################################
from ast import And
from cProfile import label
from distutils.command.upload import upload
from pickle import NONE
from turtle import color
from requests import delete, session
import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image

import plotly_express as px
import numpy as np
import pandas as pd
from numpy import append, genfromtxt
import time
import matplotlib.pyplot as plt
import random
import plotly.graph_objs as go
import plotly.figure_factory as FF
from scipy import signal
import matplotlib.pyplot as plt
from IPython import display

########################## Page Configurations #########################################
st.set_page_config(page_title="sampling studio",
                   page_icon="📶", layout="wide",
                   initial_sidebar_state="expanded",
                   )

# styles from css file
with open('style.css') as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

# Styling of the sliders
ColorMinMax = st.markdown(''' <style> div.stSlider > div[data-baseweb = "slider"] > div[data-testid="stTickBar"] > div {
    background: rgb(1 1 1 / 0%); } </style>''', unsafe_allow_html=True)

Slider_Cursor = st.markdown(''' <style> div.stSlider > div[data-baseweb="slider"] > div > div > div[role="slider"]{
    background-color: rgb(14, 38, 74); box-shadow: rgb(14 38 74 / 20%) 0px 0px 0px 0.2rem;} </style>''', unsafe_allow_html=True)

Slider_Number = st.markdown(''' <style> div.stSlider > div[data-baseweb="slider"] > div > div > div > div
                                { color: rgb(14, 38, 74); 
                                font-weight: bold
                                } </style>''', unsafe_allow_html=True)

# Styling of the buttons
m = st.markdown("""
<style>
div.stButton > button:hover {
    background-color:#B0C4DE;
    color:#191970;
    }
</style>""", unsafe_allow_html=True)

######################## Global Variables ########################################
fig = go.Figure()
######################## Functions ########################################

upload_file = st.sidebar.file_uploader(
    'Choose a file', type='csv', label_visibility='hidden')

if upload_file is not None:
    if 'delete' not in st.session_state:
        st.session_state.delete = []
    Data = pd.read_csv(upload_file)

    Data = Data.to_numpy()
    print(Data[:, 2][0])
    st.session_state.max_freq = Data[:, 2][0]
    if 't' in st.session_state:
        a = len(st.session_state.t)
        x = Data[:, 0][len(Data)-1]
        st.session_state.t = np.linspace(0, x, len(Data[:, 1]))
    if 'data' not in st.session_state:
        st.session_state.data = Data[:, 1]

    if 'addbrowse' not in st.session_state:
        st.session_state.addbrowse = True
    if st.session_state.addbrowse:
        st.session_state.sine = Data[:, 1]
        st.session_state.addbrowse = False
        st.experimental_rerun()

else:
    if 'data' in st.session_state:
        st.session_state['sine'] = np.zeros(1000)
        del st.session_state.data
        del st.session_state.addbrowse
        del st.session_state.delete
        st.session_state.max_freq = 0
        st.session_state.t = np.arange(0, 1, 0.001)
        st.experimental_rerun()
    # st.error('Please upload a file')


# Signal Plotting:
def Add_Sine():
    # Create a delete sesion for remove list
    if 'delete' not in st.session_state:
        st.session_state.delete = []
    if 't' not in st.session_state and upload_file is None:
        st.session_state.t = np.arange(0, 1, 0.001)

    # create buttons next to each others
    column1, column2 = st.sidebar.columns(2)
    with column1:
        # reset to the first drawn signal
        #  the user choose the Frequency from 0 -> 100
        frequency_slider = st.slider(
            'Frequency', 1, 100, 1, key='frequency', format='%f')
    with column2:
        #  the user choose the amplitude from 0 -> 5.1
        amplitude_slider = st.slider(
            'Amplitude', 0.0, 2.0, 0.1, key='amplitude', format='%f')

    column3, column4 = st.sidebar.columns(2)
    with column3:
        # the user choose the phase
        phase_slider = st.slider(
            "Phase", min_value=0.0, max_value=2.0, value=0.01, step=0.1, key='phase', format='%fπ')
    with column4:
        # The noise option:
        st.slider("SNR", min_value=1.0,
                  max_value=100.0, value=100.0, step=0.9, key='noise', format='%f')

    col1, col2 = st.sidebar.columns(2)
    with col1:
        add_signal_button = st.button("Add Signal")
    # with col2:
    #     noise_button = st.button("Add Noise")

    if 'max_freq' not in st.session_state:
        st.session_state.max_freq = 1

    # Adding Another Sin wave option
    if add_signal_button:
        # Get the highest frequency from all drawn signal and store it
        st.session_state.max_freq = max(
            frequency_slider, st.session_state.max_freq)
        # calculate the y value for sin wave
        y = amplitude_slider * \
            np.sin(2*np.pi*frequency_slider *
                   st.session_state.t + (phase_slider * np.pi))
        # In case it is the fisrt drawn signal -> store it in sine session
        # In case it is not -> add it to the fisrt drawn signal
        if 'sine' not in st.session_state:
            st.session_state['sine'] += y

        else:
            # In case it is not the fisrt drawn signal -> add it to the stored one
            st.session_state['sine'] += amplitude_slider * \
                np.sin(2*np.pi*frequency_slider *
                       st.session_state.t + (phase_slider * np.pi))
        # Add all drawn signal to the delete list -> for remove button
        st.session_state['delete'].append({
            'function': 'sine (x)',
            'freq': frequency_slider,
            'amp': amplitude_slider,
            'phase': phase_slider * np.pi
        })

    st.session_state.r = st.sidebar.selectbox(
        "Select to remove a signal", options=st.session_state['delete'])

    remove_col, factor_column = st.sidebar.columns(2)
    with remove_col:
        remove_button = st.button("Remove Signal")
    with factor_column:
        factor_button = st.checkbox("Using Factor of Max Frequency")
    # In case of Remove option:
    if remove_button:
        if (len(st.session_state.delete) > 0):
            st.session_state['delete'].remove(st.session_state.r)
            st.session_state['sine'] -= st.session_state.r['amp'] * \
                np.sin(
                2*np.pi*st.session_state.r['freq']*st.session_state.t+st.session_state.r['phase'])
            if len(st.session_state['delete']) == 0 and upload_file is None:
                st.session_state.sine = np.zeros(1000)
            st.experimental_rerun()

    # Sampling Frequency for signal
    st.session_state['frequency_with_factor'] = 0

    if factor_button:
        st.session_state.frequency_with_factor = st.sidebar.slider(
            "Factor Sampling", min_value=0, max_value=10, value=2, step=1, format='%f')
        # st.session_state.frequency_with_factor = SampleFreq * st.session_state.max_freq
        st.session_state.SampleFreq = st.session_state.frequency_with_factor * \
            st.session_state.max_freq
        Sample_All_Signal()

    else:
        # Sampling Frequency for signal
        st.sidebar.slider(
            "Sample frequency", min_value=0, max_value=400, value=2, step=1, key='SampleFreq', format='%f', on_change=Sample_All_Signal)

    # Download The drawn sin signal
    if ('sine' in st.session_state):
        if len(st.session_state['sine']) > 1:
            max_freq_column = np.zeros(st.session_state['sine'].shape)
            max_freq_column[:] = st.session_state.max_freq
            # print(len(st.session_state.t))
            Download(np.column_stack(
                (st.session_state.t, st.session_state['sine'], max_freq_column)))
    if ('sine' not in st.session_state):
        st.session_state['sine'] = np.zeros(1000)
        st.session_state['sine'] = .1 * np.sin(2*np.pi*1 * st.session_state.t)
        st.session_state['delete'].append({
            'function': 'sine (x)',
            'freq': 1,
            'amp': .1,
            'phase': 0
        })
        st.experimental_rerun()

    # Plotting
    fig.add_trace(go.Scatter(x=st.session_state.t, y=st.session_state['sine']+amplitude_slider *
                             np.sin(2*np.pi*frequency_slider *
                                    st.session_state.t+phase_slider * np.pi)+Noise(),
                             mode='lines',
                             name='Signal'))
    if 'ts' and 't_rec' in st.session_state:

        t_rec = st.session_state['t_rec']
        y_rec = st.session_state['rec']
        ys = st.session_state['samples']
        ts = st.session_state['ts']
        fig.add_scatter(name="Reconstructed", x=t_rec,
                        y=y_rec, line_color="#FF4B4B")
        fig.update_traces(
            marker={'size': 10}, line_color="#FF4B4B", selector=dict(mode='markers'))

        fig.add_trace(go.Scatter(x=ts, y=ys, mode='markers', name='Samples'))
        fig.update_traces(
            marker={'size': 10}, line_color="blue", selector=dict(mode='markers'))

        fig.update_traces(marker={'size': 10})
    fig.update_layout(showlegend=True, margin=dict(l=0, r=0, t=0, b=0), legend=dict(yanchor="top",
                                                                                    y=0.95, xanchor="right", x=0.99), xaxis_title="Time (Sec)", yaxis_title="Amplitude (mV)", font_size=15, plot_bgcolor='#DCD8F9', width=600)
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black',
                     gridcolor='#FFFFFF', title_font=dict(size=24, family='Arial'))
    fig.update_yaxes(showline=True, linewidth=2, linecolor='black',
                     gridcolor='#FFFFFF', title_font=dict(size=24, family='Arial'))
    return fig

# Call the sampling function fot the phase shift:


def Sample_All_Signal():
    sampling_Function(st.session_state.SampleFreq)
    plt.ylabel('Amplitude(m)')
    plt.xlabel('Time(s)')

# sampling Function:


def sampling_Function(sampling_frequency):
    # last time value of data or file
    last_time_value = st.session_state.t[len(st.session_state.t)-1]
    # No. of sample points need for the original signal
    frequency_rate = int(last_time_value * sampling_frequency)
    if (sampling_frequency == 0):
        st.error("Please set the sample frequency to at least 1")
    else:
        # sesstion state for time values
        t_rec = np.linspace(0, last_time_value, 10000)
        ts = np.arange(0, last_time_value, last_time_value/frequency_rate)
        if 'ts' not in st.session_state:
            st.session_state['ts'] = ts
        st.session_state['ts'] = ts
        if 't_rec' not in st.session_state:
            st.session_state['t_rec'] = t_rec

        st.session_state['t_rec'] = t_rec

        my_data = signal.resample(st.session_state['sine'], frequency_rate)
        # no. of points in one sec in the original file = len(st.session_state.t) / st.session_state.t[-1])
        #
        sampling_distance = int((len(st.session_state.t) /
                                 st.session_state.t[-1])/sampling_frequency)

        # the sampled y values
        my_data = st.session_state.sine[::sampling_distance]
        # store the sampling distance in time state for use
        ts = st.session_state.t[::sampling_distance]
        st.session_state.ts = ts
        # reconstruction of y values
        a_rec = wsinterp(t_rec, ts, my_data)

        if 'samples' not in st.session_state:
            st.session_state['samples'] = my_data
        st.session_state['samples'] = my_data
        if 'rec' not in st.session_state:
            st.session_state['rec'] = a_rec
        st.session_state['rec'] = a_rec

# The Reconstruction Function:
def wsinterp(reconstruction_array, Time_samples, y_samples, left=None, right=None):
    # reconstruction_array -> time of re
    scalar = np.isscalar(reconstruction_array)
    if scalar:
        reconstruction_array = np.array(reconstruction_array)
        reconstruction_array.resize(1)
    # array of (nT) time samples of reconstruction
    u = np.resize(reconstruction_array, (len(Time_samples), len(reconstruction_array)))\
        # steps in time = Time_samples[1] - Time_samples[0]
    v = (Time_samples - u.T) / (Time_samples[1] - Time_samples[0])
    # the rule of recunstruction
    # m -> y reconstructed
    m = y_samples * np.sinc(v)

    # the summation of sinc functions at each point
    y_samples_at_reconstruction_array = np.sum(m, axis=1)
    # Inforce the points to take the shape of the curve
    if left is None:
        left = y_samples[0]
    y_samples_at_reconstruction_array[reconstruction_array <
                                              Time_samples[0]] = left
    if right is None:
        right = y_samples[-1]
    y_samples_at_reconstruction_array[reconstruction_array >
                                              Time_samples[-1]] = right
    if scalar:
        return float(y_samples_at_reconstruction_array)
    return y_samples_at_reconstruction_array

# Noise Function:


def Noise():
    signal = st.session_state['sine']
    # The signal Power:
    Signal_Power = signal ** 2
    # get the average of the signal power
    SignalPowerAVG = np.mean(Signal_Power)
    # change the average power to DB scale
    SignalPower_DB = 10 * np.log10(SignalPowerAVG)

    # The Noise:
    if "noise" not in st.session_state:
        # standard noise if not choosen from slider = 10
        st.session_state.noise = 10.0
    # the noise values are from 0 -> 100
    # take the noise value from the user in SNR
    # The SNR = the measure of strenght of the desired signal relative to the background noise
    SNR_DB = st.session_state.noise
    # The noise created is the Average DB power - SNR
    Noise_DB = SignalPower_DB - SNR_DB
    # change the noise power from DB scale to watts
    Noise_watts = 10 ** (Noise_DB/10)
    # pick up random numbers from niose
    # random.normal(loc=centre of the distribution, scale=spread or “width”) of the distribution, o/p size)
    noise = np.random.normal(0, np.sqrt(Noise_watts),
                             len(st.session_state['sine']))
    # create a new column for the signal noise
    return noise

# The download function:


def Download(downloaded_data):
    downloaded_data = pd.DataFrame(downloaded_data).to_csv(
        index=False).encode('utf-8')
    st.sidebar.download_button(
        label="Download as CSV",
        data=downloaded_data,
        file_name='Data of the drawn signal.csv',
        mime='text/csv',
    )

###################################### Interface ############################################


Data = Add_Sine()


st.plotly_chart(fig,  use_container_width=True)
