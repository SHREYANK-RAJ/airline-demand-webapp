import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# Set Streamlit page layout and title
st.set_page_config(page_title="Airline Booking Demand Trends", layout="wide")
st.title("✈️ Airline Booking Demand Trends")

# Function to fetch flight data from AviationStack API
@st.cache_data
def load_flight_data():
    API_KEY = "cc1fc5b5e7c4027c1d78a3c1b7978803"  # Insert your API key directly here
    url = "http://api.aviationstack.com/v1/flights"
    params = {
        "access_key": API_KEY,
        "limit": 100
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        flights = response.json().get("data", [])
        return pd.json_normalize(flights)
    except Exception as e:
        st.error(f"Could not fetch flight data: {e}")
        return pd.DataFrame()

# Load data
df = load_flight_data()

if df.empty:
    st.warning("No flight data found. Please try again later.")
else:
    # Select important columns
    df["airline_name"] = df["airline.name"]
    df["dep_airport"] = df["departure.airport"]
    df["arr_airport"] = df["arrival.airport"]
    df["flight_status"] = df["flight_status"].fillna("unknown")

    # Sidebar filters
    st.sidebar.header("🔍 Filter Options")
    airlines = ["All"] + sorted(df["airline_name"].dropna().unique())
    selected_airline = st.sidebar.selectbox("Airline", airlines)

    statuses = ["All"] + sorted(df["flight_status"].unique())
    selected_status = st.sidebar.selectbox("Flight Status", statuses)

    # Apply filters
    if selected_airline != "All":
        df = df[df["airline_name"] == selected_airline]

    if selected_status != "All":
        df = df[df["flight_status"] == selected_status]

    st.markdown(f"### Showing {len(df)} flights")

    # Popular Routes Visualization
    st.subheader("📍 Most Frequent Routes")
    route_stats = df.groupby(["dep_airport", "arr_airport"]).size().reset_index(name="flights")
    route_stats = route_stats.sort_values("flights", ascending=False).head(10)

    fig_routes = px.bar(route_stats, 
                        x="flights", 
                        y="arr_airport", 
                        color="dep_airport", 
                        orientation="h", 
                        title="Top 10 Routes")
    st.plotly_chart(fig_routes, use_container_width=True)

    # Flight Status Pie Chart
    st.subheader("📊 Flight Status Breakdown")
    status_counts = df["flight_status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]

    fig_status = px.pie(status_counts, names="Status", values="Count")
    st.plotly_chart(fig_status, use_container_width=True)
