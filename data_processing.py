# Data processing functions
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

def generate_rent_summary(df_rent):
    """
    Generate a summary of rental properties grouped by property type, bedrooms, and bathrooms.
    
    Args:
        df_rent (pd.DataFrame): DataFrame containing rental property data
                                Must have columns: 'Property Type', 'Beds', 'Baths', 'Monthly Rent v2'
    
    Returns:
        pd.DataFrame: Summary statistics with count, min, median, and max rent for each group
    """
    df_rent['Rent'] = pd.to_numeric(df_rent['Rent'], errors='coerce')
    #df_rent['Sq Ft'] = pd.to_numeric(df_rent['Sq Ft'], errors='coerce')
    #df_rent['Rent per Sq Ft'] = df_rent['Rent'] / df_rent['Sq Ft']
    
    rent_summary = df_rent.groupby(['Property Type', 'Beds', 'Baths'])['Rent'].agg([
        ('Count', 'count'),
        ('Min Rent', 'min'),
        ('Median Rent', 'median'),
        ('Max Rent', 'max')
    ]).reset_index()
    
    return rent_summary


def calculate_investment_metrics(sale_df, rent_summary):
    """
    Calculate investment metrics for properties by joining rent data and computing financial indicators.
    
    Parameters:
    - sale_df: DataFrame with property listings including Price, Property Type, Beds, Baths
    - rent_summary: DataFrame with rental data including Property Type, Beds, Baths, Median Rent per Sq Ft
    
    Returns:
    - DataFrame with original data plus investment metrics, sorted by Cap Rate
    """
    # First ensure the column names match exactly between dataframes
    rent_df_clean = rent_summary.rename(columns={
        'Property Type': 'Property Type',
        'Beds': 'Beds',
        'Baths': 'Baths',
        'Median Rent': 'Median Rent'
    })
    
    # Perform the left join to keep all rows from df
    result_df = sale_df.merge(
        rent_df_clean[['Property Type', 'Beds', 'Baths', 'Median Rent']], 
        on=['Property Type', 'Beds', 'Baths'],
        how='left'
    )
    
    # 1. Create Estimated Annual Rent column
    result_df['Estimated Annual Rent'] = result_df['Median Rent'] * 12
    
    # 2. Create Projected Expenses column
    result_df['Projected Expenses'] = result_df['Estimated Annual Rent'] * 0.5
    
    # 3. Create NOI (Net Operating Income) column
    result_df['NOI'] = result_df['Estimated Annual Rent'] - result_df['Projected Expenses']
    
    # 4. Create Cap Rate column (as a percentage)
    result_df['Cap Rate'] = 100 * result_df['NOI'] / result_df['Price']
    
    # Sort by Cap Rate in descending order (highest first)
    result_df = result_df.sort_values(by='Cap Rate', ascending=False).reset_index()
    
    # Create a renamed copy of Price as Sale Price if needed
    result_df['Listing Price'] = result_df['Price']
    
    # Select only the requested columns in the specified order
    selected_columns = [
        'Address', 'City', 'State', 'Zip', 'Beds', 'Baths', 'Sq Ft', 
        'Property Type', 'Status', 'Listing Price', 'Estimated Annual Rent',
        'Projected Expenses', 'NOI', 'Cap Rate', 'Listing URL', 'Primary Image'
    ]

    numeric_columns = ['Beds', 'Baths', 'Sq Ft', 'Listing Price', 'Estimated Annual Rent', 'Projected Expenses', 'NOI', 'Cap Rate']
    for col in numeric_columns:
        result_df[col] = pd.to_numeric(result_df[col], errors='coerce')
    
    # Return top 10 results
    return result_df[selected_columns].head(10)


def geocode_addresses(df):

    # A little manipulation
    geo_df = df.copy()
    geo_df['full_address'] = geo_df['Address'] + ', ' + geo_df['City'] + ', ' + geo_df['State'] + ' ' + geo_df['Zip'].astype(str)

    # Initialize geocoder with user_agent
    geolocator = Nominatim(user_agent="streamlit_app")
    # Use rate limiter to respect API limits
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    # Add latitude and longitude columns
    geo_df['latitude'] = None
    geo_df['longitude'] = None

    #Add lat and lon to data
    for i, row in geo_df.iterrows():
        try:
            location = geocode(row['full_address'])
            if location:
                geo_df.at[i, 'latitude'] = location.latitude
                geo_df.at[i, 'longitude'] = location.longitude
            else:
                print(f"Could not geocode address: {row['full_address']}")
        except Exception as e:
            print(f"Error geocoding address: {row['full_address']} - {str(e)}")

    # Filter out rows with missing coordinates
    map_df = geo_df.dropna(subset=['latitude', 'longitude'])

    # Calculate the center of the map
    map_center = [
        map_df['latitude'].mean(),
        map_df['longitude'].mean()
    ]

    return map_df, map_center