import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# Set page layout and title
st.set_page_config(page_title="Airline Demand Tracker", layout="wide")
st.title("✈️ Airline Booking Demand Trends")

# Load data from free public API (Aviationstack)
@st.cache_data
def load_flight_data():
    API_KEY = cc1fc5b5e7c4027c1d78a3c1b7978803
    url = "http://api.aviationstack.com/v1/flights"
    params = {
        "access_key": API_KEY,
        "limit": 100
    }
    
    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        flights = res.json().get("data", [])
        return pd.json_normalize(flights)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Fetch the flight data
df = load_flight_data()

# Check if we got any data
if df.empty:
    st.warning("No flight data available at the moment.")
else:
    # Clean and select useful columns
    df["airline_name"] = df["airline.name"]
    df["dep_airport"] = df["departure.airport"]
    df["arr_airport"] = df["arrival.airport"]
    df["flight_status"] = df["flight_status"].fillna("unknown")

    st.sidebar.header("🔍 Filter Options")

    airline_options = ["All"] + sorted(df["airline_name"].dropna().unique())
    selected_airline = st.sidebar.selectbox("Choose Airline", airline_options)

    status_options = ["All"] + sorted(df["flight_status"].unique())
    selected_status = st.sidebar.selectbox("Flight Status", status_options)

    # Apply filters
    if selected_airline != "All":
        df = df[df["airline_name"] == selected_airline]

    if selected_status != "All":
        df = df[df["flight_status"] == selected_status]

    st.markdown(f"### Showing {len(df)} flights")

    # -------- Popular Routes --------
    st.subheader("📍 Most Frequent Routes")
    route_data = df.groupby(["dep_airport", "arr_airport"]).size().reset_index(name="flight_count")
    route_data = route_data.sort_values(by="flight_count", ascending=False).head(10)

    fig_routes = px.bar(route_data,
                        x="flight_count",
                        y="arr_airport",
                        color="dep_airport",
                        orientation="h",
                        labels={"flight_count": "Flights"},
                        title="Top 10 Routes")
    st.plotly_chart(fig_routes, use_container_width=True)

    # -------- Flight Status Pie Chart --------
    st.subheader("📊 Flight Status Overview")
    status_data = df["flight_status"].value_counts().reset_index()
    status_data.columns = ["Status", "Count"]

    fig_status = px.pie(status_data,
                        names="Status",
                        values="Count",
                        title="Flight Status Distribution")
    st.plotly_chart(fig_status, use_container_width=True)

    # -------- Optional AI Summary (placeholder) --------
    st.subheader("💡 Demand Summary (Coming Soon)")
    st.info("This section can be powered by ChatGPT to summarize trends like demand spikes or price changes.")
