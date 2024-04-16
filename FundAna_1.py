import streamlit as st 
import requests

ticker = st.text_input('Ticker', "NFLX").upper()
buttonClicked = st.button('Set')

if buttonClicked:
  requestString = f"""https://query1.finance.yahoo.com/v10/...{ticker}?modules=assetProfile%2Cprice"""
  request = requests.get(f"{requestString}", headers={"USER-AGENT": "Mozilla/5.0"})
  json = request.json()
  data = json["quoteSummary"]["result"][0]

  st.header("Profile")

  st.metric("sector", data["assetProfile"]["sector"])
  st.metric("industry", data["assetProfile"]["industry"])
  st.metric("website", data["assetProfile"]["website"])
  st.metric("marketCap", data["price"]["marketCap"]["fmt"])

  with st.expander("About Company"):
    st.write(data["assetProfile"]["longBusinessSummary"])
