import streamlit as st
import requests
import pandas as pd
import json

from api_functions import search_rental_properties, display_and_store_rentals
from data_processing import generate_rent_summary

API_KEY = "f8652a60a8mshf167b4d824fc77bp1b9522jsnb4348a0da4d6"

# Set page title and description
st.title('Realtor.com Rental Property Finder')
st.write('Enter a zip code to find available rental properties in that area.')

# Create zip code input field
zip_code = st.text_input('Enter zip code:', placeholder='e.g., 63122')

# Optional: Add validation for zip code format
if zip_code and not (zip_code.isdigit() and len(zip_code) == 5):
    st.warning('Please enter a valid 5-digit zip code')

# Create a search button
search_button = st.button('Search Properties')


# Only process when the search button is clicked and zip code is valid
if search_button and zip_code and zip_code.isdigit() and len(zip_code) == 5:
    with st.spinner('Fetching rental properties...'):
        # Fetch API
        results = search_rental_properties(API_KEY, zip_code)

        if results:
            # Store results in DataFrame and display
            df_rent = display_and_store_rentals(results)
            rent_summary = generate_rent_summary(df_rent)

# Display as interactive table
        st.subheader('Rental Summary of Available Properties')
        st.dataframe(rent_summary)
                
        # Optional: Add filters
        #st.subheader('Filter Results')
        #min_beds = st.slider('Minimum Bedrooms', 0, 5, 0)
        #max_price = st.slider('Maximum Price ($)', 500, 10000, 10000, step=100)




