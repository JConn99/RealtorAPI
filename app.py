### Import Libraries
import streamlit as st
import requests
import pandas as pd
import json
import pydeck as pdk

from api_functions import search_rental_properties, display_and_store_rentals
from api_functions import search_properties, display_and_store_properties
from data_processing import generate_rent_summary, calculate_investment_metrics, geocode_addresses

# Configuration Secrets
REALTOR_API_KEY = st.secrets.realtor_api_key.REALTOR_API_KEY
MAPBOX_API_KEY = st.secrets.mapbox_api_key.MAPBOX_API_KEY
pdk.settings.mapbox_key = MAPBOX_API_KEY

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
        results = search_rental_properties(api_key=REALTOR_API_KEY, location=zip_code)

        if results:
            # Store results in DataFrame and display
            df_rent = display_and_store_rentals(results)
            rent_summary = generate_rent_summary(df_rent)

        
        # Fetch For Sale Results as well
        sale_results = search_properties(api_key=REALTOR_API_KEY, location=zip_code)
        if sale_results:
            # Store results in DataFrame and display
            df_sale = display_and_store_properties(sale_results)
            sale_results = calculate_investment_metrics(df_sale, rent_summary)

        # Display as interactive table
        st.subheader('Rental Summary of Available Properties')

        # Apply styling to the dataframe
        styled_summary_rent = rent_summary.style.format({
            'Min Rent': '${:.0f}',
            'Median Rent': '${:.0f}',
            'Max Rent': '${:.0f}',
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

        ### Geo Information
        st.title("Address Map Visualization")

        # Get Locations
        map_df, map_center = geocode_addresses(df = sale_results)

        if len(map_df) > 0:
            st.subheader("Map of Addresses")
        
        map_view = st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/streets-v11',
            initial_view_state=pdk.ViewState(
                latitude=map_center[0],
                longitude=map_center[1],
                zoom=13,
                pitch=0,
            ),
            layers=[
                pdk.Layer(
                    'ScatterplotLayer',
                    data=map_df,
                    get_position='[longitude, latitude]',
                    get_color='[200, 30, 0, 160]',
                    get_radius=50,
                    pickable=True,
                    auto_highlight=True
                )],
            tooltip={
                "html": "<b>Address:</b> {Address}",
                "style": {
                    "backgroundColor": "steelblue",
                    "color": "white"
                    }
                }
            )
        )


        # #Display For Sale Properties
        # st.subheader('For Sale Available Properties')

        # # Apply styling to the sale dataframe
        # styled_summary_sale = sale_results.style.format({
        #     'Listing Price': '${:,.0f}',
        #     'Estimated Annual Rent': '${:,.0f}',
        #     'Projected Expenses': '${:,.0f}',
        #     'NOI': '${:,.0f}',
        #     'Cap Rate': '{:.1f}%',
        #     'Beds': '{:.0f}',
        #     'Baths': '{:.0f}',
        #     'Sq Ft': '{:,.0f}'
        # }, na_rep="N/A").set_properties(**{
        #     'text-align': 'center',
        #     'font-size': '14px',
        #     'border': '1px solid #EAEAEA'
        # }).set_table_styles([
        #     {'selector': 'th', 'props': [('background-color', '#f2f2f2'), 
        #                                 ('color', '#333'), 
        #                                 ('font-weight', 'bold'),
        #                                 ('text-align', 'center')]},
        #     {'selector': 'tr:hover', 'props': [('background-color', '#f9f9f9')]},
        # ])
        # st.dataframe(styled_summary_sale, use_container_width=True, height=400)
        # #st.dataframe(styled_summary_sale, column_config={"Link": st.column_config.LinkColumn("Listing URL")})

        # # Add download button for the for sale data
        # sale_csv = sale_results.to_csv(index=False)
        # st.download_button(
        #     label="Download data as CSV",
        #     data=sale_csv,
        #     file_name="forsale_summary.csv",
        #     mime="text/csv",
        # )
                
        # # Optional: Add filters
        # #st.subheader('Filter Results')
        # #min_beds = st.slider('Minimum Bedrooms', 0, 5, 0)
        # #max_price = st.slider('Maximum Price ($)', 500, 10000, 10000, step=100)


        st.title("Property Listings")

        # Create a card for each property
        for i, row in sale_results.iterrows():
            # Create a container for each property
            property_container = st.container()
            
            with property_container:
                cols = st.columns([2, 3])
                
                # Column 1: Image
                with cols[0]:
                    st.image(row['Primary Image'], use_column_width=True)
                
                # Column 2: Property details with reduced top padding
                with cols[1]:
                    st.markdown(f"""
                        <div style='line-height: 1.1; padding-top: 0; margin-top: -10px;'>
                            <h3 style='margin-bottom: 0.2rem; margin-top: 0;'>{row['Address']}</h3>
                            <p style='margin-bottom: 0.2rem;'>{row['City']}, {row['State']} {row['Zip']}</p>
                            <p style='font-size: 1.2rem; font-weight: 500;'>${row['Listing Price']:,.0f}</p>
                        </div>
                    """, unsafe_allow_html=True)

                    # Add listing price prominently after location
                    #st.markdown(f"### {row['Listing Price']}")
                    
                    # Property specs
                    specs_cols = st.columns(3)
                    specs_cols[0].metric("Beds", row['Beds'])
                    specs_cols[1].metric("Baths", row['Baths'])
                    specs_cols[2].metric("Sq Ft", row['Sq Ft'])

                    
                    # Financial details
                    st.write(f"**Type:** {row['Property Type']} | **Status:** {row['Status']}")
                    
                    # Investment metrics with proper formatting
                    metrics_cols = st.columns(3)
                    metrics_cols[0].metric("Annual Rent", f"${row['Estimated Annual Rent']:,.0f}")
                    metrics_cols[1].metric("NOI", f"${row['NOI']:,.0f}")
                    metrics_cols[2].metric("Cap Rate", f"{row['Cap Rate']:.1f}%")
                    
                    # Add a link to the listing
                    st.markdown(f"[View Listing]({row['Listing URL']})")
            
            # Add a divider between properties
            st.divider()






