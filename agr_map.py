import streamlit as st
import folium
from folium.plugins import Draw
import what3words
import pandas as pd

# Custom CSS to mimic W3W: Navy header/footer, red accents, clean sans-serif
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; font-family: 'Helvetica', sans-serif; }
    header { background-color: #001a3a !important; color: white !important; padding: 10px; }
    footer { visibility: hidden; }  /* Hide default footer */
    .custom-footer { background-color: #001a3a; color: white; text-align: center; padding: 10px; position: fixed; bottom: 0; width: 100%; }
    .red-accent { color: #ff0000; font-weight: bold; }
    .orange-button { background-color: #f5a623; color: white; border: none; padding: 5px 10px; border-radius: 5px; }
    .stTextInput > div > div > input { border: 1px solid #001a3a; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# Header with SLRG branding (green accent)
st.markdown("<header><h2 style='color: white; text-align: center;'>SLRG AGR Interactive Map</h2></header>", unsafe_allow_html=True)

# Sidebar for search/calc (mimics W3W side panels)
with st.sidebar:
    st.subheader("Search & Calculate")
    w3w_input = st.text_input("Enter What3Words (e.g., filled.count.soap):")
    # Replace with your W3W API key
    w3w = what3words.Geocoder("YOUR_W3W_API_KEY_HERE")
    if w3w_input:
        res = w3w.convert_to_coordinates(w3w_input)
        if 'coordinates' in res:
            lat, lng = res['coordinates']['lat'], res['coordinates']['lng']
            st.write(f"Coords: {lat}, {lng}")
            sample_agr = calculate_agr(1500)  # Placeholder
            st.write(f"Estimated AGR: <span class='red-accent'>£{sample_agr}</span>", unsafe_allow_html=True)
        else:
            st.write("Invalid W3W—check key/address.")

# Sample data (expand later)
sample_data = pd.DataFrame({
    'area': ['Edinburgh', 'Rural Highlands'],
    'land_value_per_sqm': [1500, 50],
    'discount_rate': [0.05, 0.05]
})

def calculate_agr(land_value_per_sqm, area_sqm=9):
    annual_rental = land_value_per_sqm * area_sqm * sample_data['discount_rate'][0]
    agr = annual_rental * 1.0
    return round(agr, 2)

# Main map (centered on Scotland, W3W style)
st.write("Explore estimated AGR. Uses gov data—approximate.")
m = folium.Map(location=[56.4907, -4.2026], zoom_start=7, tiles='OpenStreetMap')  # Clean base like W3W
folium.Rectangle(
    bounds=[[55.9, -3.3], [56.0, -3.1]],
    color="#ff0000",  # Red border like W3W accents
    fill=True,
    fill_opacity=0.3,
    popup=f"Sample AGR: <span style='color: #ff0000;'>£{calculate_agr(1500)}</span> (Edinburgh)"
).add_to(m)
Draw(export=False).add_to(m)
st.components.v1.html(folium.Figure().add_child(m).render(), height=600)

# Custom footer with navigation (like W3W bottom bar)
st.markdown("""
    <div class='custom-footer'>
        <a href='https://www.slrg.scot' style='color: white;'>SLRG Home</a> | 
        <a href='#' style='color: white;'>About AGR</a> | 
        <a href='#' style='color: white;'>Developer</a>
    </div>
""", unsafe_allow_html=True)

st.write("Next: Integrate real data. Thoughts on colors or layout tweaks?")