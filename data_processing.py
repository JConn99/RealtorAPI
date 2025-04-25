# Data processing functions
import pandas as pd

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
    rent_summary = df_rent.groupby(['Property Type', 'Beds', 'Baths'])['Rent'].agg([
        ('Count', 'count'),
        ('Min Rent', 'min'),
        ('Median Rent', 'median'),
        ('Max Rent', 'max')
    ]).reset_index()
    
    return rent_summary