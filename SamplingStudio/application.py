#################################################################
# ########################## Sampling Studio ############################
# TEAM MEMBERS:Mohamed Naaser        Mahmoud Hamdy
#              Bassant Medhat        Yousr Ashraf
########################## Imports #########################################
from ast import And
from distutils.command.upload import upload
from pickle import NONE
from turtle import color
from requests import session
import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image

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
div.stButton > button:first-child {
    background-color: #191970;
    color:#ffffff;
    border-radius: 60px;
    font-weight: bold
}
div.stButton > button:hover {
    background-color:#B0C4DE;
    color:#191970;
    }
</style>""", unsafe_allow_html=True)

######################## Global Variables ########################################
# SIN Signal Plotting:
global sig
y_stamps = []
Data = noise = []
max_freq = 0


def wsinterp(x, xp, fp, left=None, right=None):
    scalar = np.isscalar(x)
    if scalar:
        x = np.array(x)
        x.resize(1)
    u = np.resize(x, (len(xp), len(x)))
    v = (xp - u.T) / (xp[1] - xp[0])
    m = fp * np.sinc(v)
    fp_at_x = np.sum(m, axis=1)
    if left is None:
        left = fp[0]
    fp_at_x[x < xp[0]] = left
    if right is None:
        right = fp[-1]
    fp_at_x[x > xp[-1]] = right
    if scalar:
        return float(fp_at_x)
    return fp_at_x


######################## Functions ########################################
# SIN Signal Plotting:

def Add_Sine():
    t = np.arange(0, 1, 0.001)
    st.title(f'Select from the option To draw Sine Signal')
    #  the user choose the amplitude from 0 -> 5.1
    plot_amplitude = st.sidebar.slider('Choose the amplitude', 0.0, 5.1, 0.1)
    #  the user choose the Frequency from 0 -> 100
    plot_freq = st.sidebar.slider('Choose the frequency', 0, 100, 0)
    st.session_state["frequency"] = plot_freq
    # sampling_freq = st.slider(
    #     "Specify frequency", min_value=0, max_value=200, value=20, step=1)
    # st.session_state["frequency_sampling"] = sampling_freq
    if 'max_freq' not in st.session_state:
        st.session_state.max_freq = 1
    fig = plt.figure(figsize=(10, 5))
    plt.grid(color='r', linestyle='-', linewidth=2)
    
    # create buttons next to each others
    col1, col2 = st.sidebar.columns(2)
    with col1:
        sin_button1 = st.button("Draw Wave")
    with col2:
        # reset to the first drawn signal
        sin_button2 = st.button("Remove Wave")

    # Adding Another Sin wave option
    if sin_button1:
        # the choosen frequency from slider
        freq = plot_freq
        st.session_state.max_freq = max(freq, st.session_state.max_freq)
        # calculate the y value for sin wave
        y = plot_amplitude*np.sin(2*np.pi*freq*t)
        # In case it is the fisrt drawn signal -> store it in sine session
        if 'sine' not in st.session_state:
            st.session_state['sine'] += y
        else:
            # In case it is not the fisrt drawn signal -> add it to the stored one
            st.session_state['sine'] += plot_amplitude*np.sin(2*np.pi*freq*t)
            #
            st.session_state['delete'].append({
                'function': 'sine (x)',
                'freq': plot_freq,
                'amp': plot_amplitude
            })

        # A state that stores the information of signal in case it is choosen to be deleted

        # Draw the signal either it is the first or added one
        plt.plot(t, st.session_state['sine'], 'b')

    # In case of Remove option:
    if sin_button2:
        if st.session_state.r != '':
            if len(st.session_state['delete']) > 2:
                st.session_state['delete'].remove(st.session_state.r)
                st.session_state['sine'] -= st.session_state.r['amp'] * \
                    np.sin(2*np.pi*st.session_state.r['freq']*t)
                # st.experimental_rerun()
            else:
                st.session_state['sine'] *= 0
                st.session_state['delete'].pop(1)
                plt.plot(t, st.session_state['sine'], 'b')
                # st.experimental_rerun()
            # st.experimental_rerun
            # st.experimental_rerun()

     # selection box for the signal the user want to delete
    st.session_state.r = st.sidebar.selectbox(
        "Select from the Added Signals", options=st.session_state['delete'])

    # Choose the frequency of sampling:
    # sampling_freq = st.sidebar.slider("Specify frequency", 0, 100, 1)
    sampling_freq = st.sidebar.slider("Specify frequency", min_value=0, max_value= 8,value=2, step=1)
    # Store the sampled frequency to frequency_sampling session
    st.session_state["frequency_sampling"] = sampling_freq
    # Store the sampled frequency to frequency_sampling session
    if (st.sidebar.button("Sample Signal")):
        freq = plot_freq
        sr = sampling_freq
        time, amp = sampling_sine(freq, plot_amplitude, sampling_freq,
         st.session_state.max_freq)
        plt.ylabel('Amplitude')
        plt.xlabel('Time (s)')
        st.subheader("Signal Reconstruction")
        # plt.plot(time, amp)

    if ('sine' in st.session_state):
        if len(st.session_state['sine']) > 1:
            Download(np.column_stack((t, st.session_state['sine'])))
    if ('sine' not in st.session_state):
        st.session_state['sine'] = np.zeros(1000)
    plt.plot(t, st.session_state['sine'], 'b')
    plt.ylabel('Amplitude')
    plt.xlabel('Time (s)')
    st.subheader("Sampling Data With original signal")
    
    return fig

# Noise Function:


def Noise(Data):
    signal = Data[:, 1]
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
    st.sidebar.slider(
        "SNR Level in DB",
        min_value=0.0,
        max_value=100.0,
        key="noise"
    )
    # show the slide bar in the app
    st.write("Noise added with SNR", st.session_state.noise)
    # take the noise value from the user in SNR
    # The SNR = the measure of strenght of the desired signal relative to the background noise
    SNR_DB = st.session_state.noise
    # The noise created is the Average DB power - SNR
    Noise_DB = SignalPower_DB - SNR_DB
    # change the noise power from DB scale to watts
    Noise_watts = 10 ** (Noise_DB/10)
    # pick up random numbers from niose
    # random.normal(loc=centre of the distribution, scale=spread or “width”) of the distribution, o/p size)
    noise = np.random.normal(0, np.sqrt(Noise_watts), len(Data))
    # create a new column for the signal noise
    return noise

# Sine sampling:


def sampling_sine(plot_freq, plot_amplitude, sampling_freq, max_freq):
    rate = 2 * sampling_freq*max_freq
    fig= plt.figure( figsize=(10, 5))
    ts = np.arange(0, 1, 1/rate)
    t_rec = np.linspace(0, 1, 10000)
    my_data = signal.resample(st.session_state['sine'], rate)
    a_rec = wsinterp(t_rec, ts, my_data)
    #plt.plot(ts, my_data, 'x')
    
    plt.stem(ts,my_data)
    plt.plot(t_rec, a_rec, color='r')
   
    st.plotly_chart(fig)
    return ts, my_data
# Plotting Signal Normally Using Plotly:


def Upload_Plot(my_data, noise):
    # the first 2000 number in time and magnitude from the imported data
    # One Complete cycle
    n = 2000
    t = st.session_state.data[:, 0]
    # Time (x-axis)
    t = t[:n]
    a = st.session_state.data[:, 1][:n]
    # Amplitude
    # a = a[:n]
    # In case the choosen is sin signal
    freq_of_data = st.sidebar.slider("Specify frequency", 0, 100, 2)
    amp_of_data = st.sidebar.slider("Specify amplitude", 0.0, 1.0, 0.2)

    # create buttons next to each others
    col1, col2 = st.sidebar.columns(2)
    with col1:
        upload_button1 = st.button("Plot Data")
    with col2:
        # reset to the first drawn signal
        upload_button2 = st.button("Remove Plot")

    # Plotting the uploaded file
    if upload_button1:
        st.session_state.list.append({
            'function': 'Sin x',
            'amp': amp_of_data,
            'freq': freq_of_data
        })

        st.session_state['data'][:, 1][:n] += amp_of_data * \
            np.sin(2*np.pi*freq_of_data*t)

    if upload_button2:
        if st.session_state.r != '':
            st.session_state['list'].remove(st.session_state.r)
            st.session_state['data'][:, 1][:n] -= st.session_state.r['amp'] * \
                np.sin(2*np.pi*st.session_state.r['freq']*t)
    st.session_state.r = st.sidebar.selectbox(
        "Added Functions", options=st.session_state['list'])
    

    if (len(noise) != 0):

    # Store the sampled frequency to frequency_sampling session

     st.session_state['data'][:, 1][:n] += noise[:n]
    freq = st.sidebar.slider("Specify frequency", min_value=0, max_value= 100,value=1, step=1)
    if (st.sidebar.button("Add Samples")):
        Add_Samples(freq)
    fig = plt.figure(figsize=(10, 5))
    st.subheader("Original signal")
    plt.plot(t, st.session_state['data'][:, 1][:n], color='r')
    st.plotly_chart(fig)
    Download(np.column_stack((t, st.session_state['data'][:, 1][:n])))


# Adding Noise to the Signal:
def Add_Samples(freq):
    n = 2000
    t = st.session_state['data'][:, 0][:n]
    t = t[:n]
    a = st.session_state['data'][:, 1][:n]
    a = a[:n]

    fig = plt.figure(figsize=(10, 5))

    sampledPionts = 2*freq
    ts = np.linspace(0, 1, sampledPionts)
    my_data = signal.resample(a, sampledPionts)
    t_rec = np.linspace(0, 1, 10000)
    a_rec = wsinterp(t_rec, ts, my_data)
    st.subheader("Reconstructed signal")
    plt.plot(t_rec, a_rec,color='b')
    plt.plot(ts, my_data,"x", 'b')
    
    # return ts,my_data
    st.plotly_chart(fig)


def Download(Data_to_be):
    Data_to_be = pd.DataFrame(Data_to_be).to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="Download data as CSV",
        data=Data_to_be,
        file_name='Data of the drawn signal.csv',
        mime='text/csv',
    )

###################################### Interface ############################################

# sidebar menu:
with st.sidebar:
    selected1 = option_menu(
        menu_title='Studio Options',
        options=[ 'Sine Signal', 'Upload Signal'],
        icons=[ 'reception-4',
               'arrow-bar-up'],
        # arrows-fullscreen
        menu_icon='activity',
        styles={
            "container": {"color": "black", "padding": "25px", "padding-top": "50px"},
            "icon": {"color": "#00008B", "font-size": "25px"},
            "nav-link": {"font-size": "19px", "text-align": "left", "margin": "1px", "--hover-color": "#B0C4DE"},
            "nav-link-selected": {'color': 'black', "background-color": "#B0C4DE"},
        }
    )



if selected1 == 'Sine Signal':
    if 'delete' not in st.session_state:
        st.session_state.delete = ['']
    st.plotly_chart(Add_Sine())



if selected1 == 'Upload Signal':

    # if 'list' in st.session_state:
    #     del st.session_state.list  
    # if 'list' not in st.session_state:
    #         st.session_state.list = ['']   
  
    st.subheader('Choose the file you want to upload')
    upload_file = st.file_uploader('Choose a file', type='csv')
    if upload_file is not None:
   
        Data = pd.read_csv(upload_file)
        Data = Data.to_numpy()
        # if st.session_state['counter']==1:
            
        #     st.session_state.list = ['']
        #     st.session_state.counter = 0
        if 'data' not in st.session_state:
            # Store the data in session
            st.session_state.data = Data
        if 'list' not in st.session_state:
            st.session_state.list = ['']

        # if st.session_state['counter']==1:
        #     st.session_state.data = Data
        #     st.session_state.list = ['']
        #     st.session_state.counter = 0


        # Noise
        # Extract the noise using the uploaded data
        noise = Noise(Data)
        # To draw with adding the Noise
        if (st.sidebar.button("Add Noise", key=None, help="This button is used to add noise to a signal")):
            Upload_Plot(Data, noise)
        else:
            # To draw without adding the Noise
            noise = []
            # draw with emty noise list
            Upload_Plot(Data, noise)
    else:
        if 'data' not in st.session_state:
            # Store the data in session
            st.session_state.data = Data
        del st.session_state.data
        if 'list' not in st.session_state:
            st.session_state.list = ['']
        del st.session_state.list
        st.error('Please upload a file')

