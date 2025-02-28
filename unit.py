import streamlit as st
import time
import requests
from datetime import datetime

# Load CSS first
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()

# ========== CONVERSION FUNCTIONS ==========
def convert_length(value, from_unit, to_unit):
    conversions = {
        'meters': 1,
        'kilometers': 1000,
        'centimeters': 0.01,
        'millimeters': 0.001,
        'miles': 1609.34,
        'yards': 0.9144,
        'feet': 0.3048,
        'inches': 0.0254
    }
    return value * conversions[from_unit] / conversions[to_unit]

def convert_temperature(value, from_unit, to_unit):
    if from_unit == to_unit:
        return value
    # Convert to Celsius first
    if from_unit == 'fahrenheit':
        value = (value - 32) * 5/9
    elif from_unit == 'kelvin':
        value = value - 273.15
    
    # Convert from Celsius to target
    if to_unit == 'fahrenheit':
        return (value * 9/5) + 32
    elif to_unit == 'kelvin':
        return value + 273.15
    else:
        return value

def convert_weight(value, from_unit, to_unit):
    conversions = {
        'kilograms': 1,
        'grams': 0.001,
        'milligrams': 1e-6,
        'pounds': 0.453592,
        'ounces': 0.0283495,
        'tons': 1000
    }
    return value * conversions[from_unit] / conversions[to_unit]

def convert_currency(value, from_curr, to_curr):
    API_KEY = "296112d6b2eea2af7c31acf1"  # Replace with your key
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{from_curr}/{to_curr}/{value}"
    response = requests.get(url)
    data = response.json()
    return data.get('conversion_result', 0)

# Area conversions
AREA_CONVERSIONS = {
    'square meters': 1,
    'square kilometers': 1e6,
    'square miles': 2589988.11,
    'acres': 4046.86,
    'hectares': 10000
}

# ========== UNIT CATEGORIES ==========
UNIT_CATEGORIES = {
    'Length': {
        'units': ['meters', 'kilometers', 'centimeters', 'millimeters', 
                 'miles', 'yards', 'feet', 'inches'],
        'converter': convert_length
    },
    'Temperature': {
        'units': ['celsius', 'fahrenheit', 'kelvin'],
        'converter': convert_temperature
    },
    'Weight': {
        'units': ['kilograms', 'grams', 'milligrams', 
                 'pounds', 'ounces', 'tons'],
        'converter': convert_weight
    },
    'Currency': {
        'units': ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'INR'],
        'converter': convert_currency
    },
    'Area': {
        'units': ['square meters', 'square kilometers', 
                 'square miles', 'acres', 'hectares'],
        'converter': lambda v, f, t: v * AREA_CONVERSIONS[f] / AREA_CONVERSIONS[t]
    }
}

# ========== APP UI COMPONENTS ==========
# Initialize session state
if 'conversions' not in st.session_state:
    st.session_state.conversions = []
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Header with dark mode toggle
col1, col2 = st.columns([3,1])
with col1:
    st.markdown('<div class="rgb-header"><h1>🌈 RGB Unit Converter</h1></div>', unsafe_allow_html=True)
with col2:
    if st.button('🌓 Toggle Dark Mode'):
        st.session_state.dark_mode = not st.session_state.dark_mode

# Dark mode CSS injection
if st.session_state.dark_mode:
    st.markdown("""
    <style>
        .main {
            background: linear-gradient(
                135deg,
                rgba(30, 30, 30, 1) 0%,
                rgba(50, 50, 50, 1) 100%
            ) !important;
            color: white !important;
        }
        .converter-container {
            background: rgba(40, 40, 40, 0.9) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Main converter UI
with st.container():
    st.markdown('<div class="converter-container">', unsafe_allow_html=True)
    
    category = st.selectbox('Select Category', list(UNIT_CATEGORIES.keys()))
    
    col1, col2 = st.columns(2)
    with col1:
        from_unit = st.selectbox('From', UNIT_CATEGORIES[category]['units'])
    with col2:
        to_unit = st.selectbox('To', UNIT_CATEGORIES[category]['units'])
    
    value = st.number_input('Enter Value', min_value=0.0, format="%.4f")
    
    if st.button('✨ Convert'):
        try:
            # Show conversion animation
            progress_bar = st.progress(0)
            status_text = st.empty()
            for i in range(100):
                progress_bar.progress(i + 1)
                status_text.text(f"Converting... {i+1}%")
                time.sleep(0.01)
            progress_bar.empty()
            status_text.empty()
            
            # Perform conversion
            converter = UNIT_CATEGORIES[category]['converter']
            result = converter(value, from_unit, to_unit)
            
            # Store conversion
            st.session_state.conversions.append({
                'time': datetime.now().strftime("%H:%M:%S"),
                'value': value,
                'from': from_unit,
                'result': result,
                'to': to_unit
            })
            
            # Show result
            st.balloons()
            st.markdown(f"""
            <div class="result rgb-glow">
                <div style="font-size:1.5rem; margin-bottom:10px;">🚀 Conversion Complete!</div>
                {value:.4f} {from_unit} =<br>
                <strong style="font-size:2rem; color: rgb(var(--rgb-2))">{result:.4f} {to_unit}</strong>
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ Conversion Error: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Conversion history
if st.session_state.conversions:
    with st.expander("📜 Conversion History"):
        for conv in reversed(st.session_state.conversions):
            st.write(f"{conv['time']}: {conv['value']} {conv['from']} → {conv['result']:.4f} {conv['to']}")

# Unit information
with st.expander("ℹ️ Unit Information"):
    st.markdown("""
    ### Unit Reference Guide
    - **Length**: Standard metric and imperial measurements
    - **Temperature**: Celsius, Fahrenheit, Kelvin scales
    - **Currency**: Real-time exchange rates (updated hourly)
    - **Weight**: Metric and imperial mass units
    - **Area**: Land measurement units
    """)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 2rem; color: #666;">
    Created by Uzma Riaz and Made with ❤️ using Streamlit | RGB Theme v1.0
</div>
""", unsafe_allow_html=True)