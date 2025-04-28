import streamlit as st
import requests
import pandas as pd
import json

from api_functions import search_rental_properties, display_and_store_rentals
from api_functions import search_properties, display_and_store_properties
from data_processing import generate_rent_summary, calculate_investment_metrics

API_KEY = "f8652a60a8mshf167b4d824fc77bp1b9522jsnb4348a0da4d6"

# Set page title and description
st.title('Realtor.com Rental Property Finder')
st.write('Enter a zip code to find available rental properties in that area.')

# Create a form to capture Enter key presses
with st.form(key='zip_search_form'):
    zip_code = st.text_input('Enter Zip Code', key='zip_input')
    search_button = st.form_submit_button('Search')

# Optional: Add validation for zip code format
if zip_code and not (zip_code.isdigit() and len(zip_code) == 5):
    st.warning('Please enter a valid 5-digit zip code')

# Only process when the search button is clicked and zip code is valid
if search_button and zip_code and zip_code.isdigit() and len(zip_code) == 5:
    with st.spinner('Fetching properties...'):
        # Fetch API
        results = search_rental_properties(API_KEY, zip_code)

        if results:
            # Store results in DataFrame and display
            df_rent = display_and_store_rentals(results)
            rent_summary = generate_rent_summary(df_rent)

        
        # Fetch For Sale Results as well
        sale_results = search_properties(API_KEY, zip_code)
        if sale_results:
            # Store results in DataFrame and display
            df_sale = display_and_store_properties(sale_results)
            sale_results = calculate_investment_metrics(df_sale, rent_summary)

        # Display as interactive table
        st.subheader('Rental Summary of Available Properties')

        # Apply styling to the dataframe
        styled_summary_rent = rent_summary.style.format({
            'Min Rent per Sq Ft': '${:.2f}',
            'Median Rent per Sq Ft': '${:.2f}',
            'Max Rent per Sq Ft': '${:.2f}',
            'Count': '{:.0f}',
            'Beds': '{:.0f}'
        }).set_properties(**{
            'text-align': 'center',
            'font-size': '14px',
            'border': '1px solid #EAEAEA'
        }).set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#f2f2f2'), 
                                        ('color', '#333'), 
                                        ('font-weight', 'bold'),
                                        ('text-align', 'center')]},
            {'selector': 'tr:hover', 'props': [('background-color', '#f9f9f9')]},
        ])

        # Display the styled dataframe
        st.dataframe(styled_summary_rent, use_container_width=True, height=400)

        # Add download button for the data
        rent_csv = rent_summary.to_csv(index=False)
        st.download_button(
            label="Download data as CSV",
            data=rent_csv,
            file_name="rental_summary.csv",
            mime="text/csv",
        )


        #Display For Sale Properties
        st.subheader('For Sale Available Properties')

        # Apply styling to the sale dataframe
        styled_summary_sale = sale_results.style.format({
            'Listing Price': '${:,.0f}',
            'Estimated Annual Rent': '${:,.0f}',
            'Projected Expenses': '${:,.0f}',
            'NOI': '${:,.0f}',
            'Cap Rate': '{:.1f}%',
            'Beds': '{:.0f}',
            'Baths': '{:.0f}',
            'Sq Ft': '{:,.0f}'
        }, na_rep="N/A").set_properties(**{
            'text-align': 'center',
            'font-size': '14px',
            'border': '1px solid #EAEAEA'
        }).set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#f2f2f2'), 
                                        ('color', '#333'), 
                                        ('font-weight', 'bold'),
                                        ('text-align', 'center')]},
            {'selector': 'tr:hover', 'props': [('background-color', '#f9f9f9')]},
        ])
        st.dataframe(styled_summary_sale, use_container_width=True, height=400)
        #st.dataframe(styled_summary_sale, column_config={"Link": st.column_config.LinkColumn("Listing URL")})

        # Add download button for the for sale data
        sale_csv = sale_results.to_csv(index=False)
        st.download_button(
            label="Download data as CSV",
            data=sale_csv,
            file_name="forsale_summary.csv",
            mime="text/csv",
        )
                
        # Optional: Add filters
        #st.subheader('Filter Results')
        #min_beds = st.slider('Minimum Bedrooms', 0, 5, 0)
        #max_price = st.slider('Maximum Price ($)', 500, 10000, 10000, step=100)




