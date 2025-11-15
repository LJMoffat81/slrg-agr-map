import streamlit as st
import folium
from folium.plugins import Draw
import what3words
import requests  # For API calls
import json

# Custom CSS (unchanged)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; font-family: 'Helvetica', sans-serif; }
    header { background-color: #001a3a !important; color: white !important; padding: 10px; }
    footer { visibility: hidden; }
    .custom-footer { background-color: #001a3a; color: white; text-align: center; padding: 10px; position: fixed; bottom: 0; width: 100%; }
    .red-accent { color: #ff0000; font-weight: bold; }
    .orange-button { background-color: #f5a623; color: white; border: none; padding: 5px 10px; border-radius: 5px; }
    .stTextInput > div > div > input { border: 1px solid #001a3a; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<header><h2 style='color: white; text-align: center;'>SLRG AGR Interactive Map</h2></header>", unsafe_allow_html=True)

# SPARQL endpoint for dynamic data
SPARQL_ENDPOINT = "https://statistics.gov.scot/sparql"

# Function to query API dynamically
@st.cache_data(ttl=3600)  # Cache for 1hr to respect limits
def query_sparql(query):
    headers = {"Accept": "application/sparql-results+json"}
    params = {"query": query}
    response = requests.post(SPARQL_ENDPOINT, data=params, headers=headers)
    if response.status_code == 200:
        return response.json()["results"]["bindings"]
    else:
        st.error(f"API error: {response.text}")
        return []

# Example query: Get latest vacant land ha by area (adapt for your needs)
def get_vacant_land_data(area_name="Edinburgh"):  # Placeholder; map lat/lng to area
    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?areaname ?periodname ?value
    WHERE {
      ?obs <http://purl.org/linked-data/cube#dataSet> <http://statistics.gov.scot/data/vacant-derelict-land> .
      ?obs <http://purl.org/linked-data/sdmx/2009/dimension#refArea> ?areauri .
      ?obs <http://purl.org/linked-data/sdmx/2009/dimension#refPeriod> ?perioduri .
      ?obs <http://statistics.gov.scot/def/measure-properties/count> ?value .  # Adjust measure (e.g., count for ha)
      ?areauri rdfs:label ?areaname .
      ?perioduri rdfs:label ?periodname .
      FILTER (CONTAINS(?areaname, "%s"))  # Filter by area
    } ORDER BY DESC(?periodname) LIMIT 1  # Latest period
    """ % area_name
    results = query_sparql(query)
    if results:
        return float(results[0]["value"]["value"])  # e.g., ha value
    return 100.0  # Fallback

# AGR calc: Use dynamic data
def calculate_agr(lat, lng, area_sqm=9):
    # TODO: Map lat/lng to area (e.g., via OS API or simple dict)
    area_name = "Edinburgh" if lat > 55.9 else "Highlands"  # Simple stub; replace with geocode
    ha_value = get_vacant_land_data(area_name)  # Dynamic fetch
    value_per_sqm = (ha_value * 1000) / 10000  # Example conversion; refine formula
    annual_rental = value_per_sqm * area_sqm * 0.05
    agr = annual_rental * 1.0
    return round(agr, 2), value_per_sqm

with st.sidebar:
    st.subheader("Search & Calculate")
    w3w_input = st.text_input("Enter What3Words (e.g., filled.count.soap):")
    w3w = what3words.Geocoder("YOUR_W3W_API_KEY_HERE")
    if w3w_input:
        res = w3w.convert_to_coordinates(w3w_input)
        if 'coordinates' in res:
            lat, lng = res['coordinates']['lat'], res['coordinates']['lng']
            st.write(f"Coords: {lat}, {lng}")
            agr, base_sqm = calculate_agr(lat, lng)
            st.write(f"Estimated AGR (3x3m): <span class='red-accent'>£{agr}</span>", unsafe_allow_html=True)
            st.write(f"Base: £{base_sqm}/sqm from live gov API (sources: statistics.gov.scot SVDLS)")
        else:
            st.write("Invalid W3W.")

# Map (add dynamic overlays later)
st.write("Explore AGR using live gov data.")
m = folium.Map(location=[56.4907, -4.2026], zoom_start=7)
Draw(export=False).add_to(m)
st.components.v1.html(folium.Figure().add_child(m).render(), height=600)

st.markdown("""
    <div class='custom-footer'>
        <a href='https://www.slrg.scot' style='color: white;'>SLRG Home</a> | 
        <a href='#' style='color: white;'>About AGR</a> | 
        <a href='#' style='color: white;'>Developer</a>
    </div>
""", unsafe_allow_html=True)