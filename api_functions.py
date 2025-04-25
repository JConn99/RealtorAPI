### These are the functions used to call the API
import streamlit as st
import requests
import pandas as pd
import json

def search_rental_properties(api_key, location, limit=1000):
    """
    Search for rental properties using the Realtor API
    
    Parameters:
        api_key (str): Your RapidAPI key
        location (str): Zip, e.g. 63122 or City and state, e.g., "Kirkwood, MO"
        min_price (int, optional): Minimum rental price
        max_price (int, optional): Maximum rental price
        beds (int, optional): Number of bedrooms
        baths (int, optional): Number of bathrooms
        limit (int, optional): Maximum number of results to return
    
    Returns:
        dict: JSON response from the API
    """
    url = "https://realtor16.p.rapidapi.com/search/forrent"
    

    querystring =  {"location":location, 
                    "search_radius" : "0",
                    "limit":limit}

    # Add optional filters if provided
    #if min_price:
    #    querystring["price_min"] = str(min_price)
    #if max_price:
    #    querystring["price_max"] = str(max_price)
    #if beds:
    #    querystring["beds_min"] = str(beds)
    #if baths:
    #    querystring["baths_min"] = str(baths)
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "realtor16.p.rapidapi.com"
    }
    
    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def display_and_store_rentals(properties_data):
    """Display rental property information and store in a pandas DataFrame"""
    if not properties_data or 'properties' not in properties_data:
        print("No rental properties found or invalid data")
        return None
    
    # List to store property data for DataFrame
    property_records = []
    
    # Process each property
    for prop in properties_data['properties']:
        try:
            print(f"\n{'='*50}")
            
            # Address information
            address = prop.get('location', {}).get('address', {})
            address_line = address.get('line', 'N/A')
            city = address.get('city', 'N/A')
            state = address.get('state_code', 'N/A')
            zip_code = address.get('postal_code', 'N/A')
            
            #print(f"Address: {address_line}")
            #print(f"City: {city}")
            #print(f"State: {state}")
            #print(f"Zip: {zip_code}")
            
            # Property details
            description = prop.get('description', {})
            rent = prop.get('list_price')
            beds = description.get('beds', 'N/A')
            baths = description.get('baths_consolidated', 'N/A')
            sqft = description.get('sqft', 'N/A')
            property_type_desc = description.get('type', 'N/A')
            sub_type = description.get('sub_type', 'N/A')
            
            # Error handling for rent formatting
            if rent is not None:
                try:
                    #print(f"Monthly Rent: ${rent:,}")
                    formatted_rent = f"${rent:,}"
                    rent = rent
                except (TypeError, ValueError):
                    #print(f"Monthly Rent: ${rent}")
                    formatted_rent = f"${rent}"
                    rent = rent
            else:
                #print("Monthly Rent: N/A")
                formatted_rent = "N/A"
                rent = "N/A"
                
            #print(f"Beds: {beds}")
            #print(f"Baths: {baths}")
            #print(f"Sq Ft: {sqft}")
            #print(f"Property Type: {property_type_desc}")
            #print(f"Sub Type: {sub_type}")
            
            # Status flags
            flags = prop.get('flags', {})
            status_flags = []
            if flags and isinstance(flags, dict):
                if flags.get('is_new_listing'):
                    status_flags.append("NEW LISTING")
                if flags.get('is_pending'):
                    status_flags.append("PENDING")
                
            status = ', '.join(status_flags) if status_flags else "ACTIVE"
            #print(f"Status: {status}")
            
            # Price reduction info
            price_reduced = prop.get('price_reduced_amount')
            #if price_reduced is not None:
            #    try:
            #        print(f"Price Reduced: ${price_reduced:,}")
            #    except (TypeError, ValueError):
            #        print(f"Price Reduced: ${price_reduced}")
            
            # Listing information
            listing_id = prop.get('listing_id', 'N/A')
            property_id = prop.get('property_id', 'N/A')
            list_date = prop.get('list_date', 'N/A')
            
            #print(f"Listing ID: {listing_id}")
            #print(f"Property ID: {property_id}")
            #if list_date:
            #    print(f"List Date: {list_date}")
            
            # Pet policy with error handling
            pet_policy = prop.get('pet_policy', {})
            pets_allowed = []
            
            try:
                if pet_policy and isinstance(pet_policy, dict):
                    if pet_policy.get('cats'):
                        pets_allowed.append("Cats")
                    if pet_policy.get('dogs_small'):
                        pets_allowed.append("Small Dogs")
                    if pet_policy.get('dogs_large'):
                        pets_allowed.append("Large Dogs")
                
                pets_string = ', '.join(pets_allowed) if pets_allowed else "No information"
                #print(f"Pets Allowed: {pets_string}")
            except Exception as e:
                pets_string = "Error retrieving pet information"
                print(f"Pets Allowed: Error ({str(e)})")
            
            # Get security deposit info from details if available
            security_deposit = "N/A"
            availability_date = "N/A"
            
            try:
                details = prop.get('details', [])
                if details and isinstance(details, list):
                    for detail in details:
                        if not isinstance(detail, dict):
                            continue
                            
                        category = detail.get('category')
                        texts = detail.get('text', [])
                        
                        if not isinstance(texts, list):
                            continue
                            
                        if category == "Rental Info":
                            for text in texts:
                                if isinstance(text, str) and "Security Deposit:" in text:
                                    security_deposit = text.split("Security Deposit:")[1].strip()
                        
                        if category == "Other Property Info":
                            for text in texts:
                                if isinstance(text, str) and "Availability Date:" in text:
                                    availability_date = text.split("Availability Date:")[1].strip()
            except Exception as e:
                print(f"Error processing property details: {str(e)}")
                
            #if security_deposit != "N/A":
            #    print(f"Security Deposit: ${security_deposit}")
            #if availability_date != "N/A":
            #    print(f"Available From: {availability_date}")
            
            # Images
            primary_image = "N/A"
            try:
                primary_photo = prop.get('primary_photo', {})
                if primary_photo and isinstance(primary_photo, dict):
                    primary_image = primary_photo.get('href', 'N/A')
                
                #if primary_image != 'N/A':
                #    print(f"Primary Image: {primary_image}")
            except Exception as e:
                print(f"Error processing image: {str(e)}")
            
            # Additional photos count
            additional_photos = 0
            try:
                photos = prop.get('photos', [])
                if photos and isinstance(photos, list):
                    additional_photos = max(0, len(photos) - 1)
                
                #if additional_photos > 0:
                #    print(f"Additional Photos: {additional_photos}")
            except Exception as e:
                print(f"Error counting photos: {str(e)}")
                additional_photos = "Error"
            
            # Virtual tours
            virtual_tour = "N/A"
            try:
                virtual_tours = prop.get('virtual_tours', [])
                if virtual_tours and isinstance(virtual_tours, list) and len(virtual_tours) > 0:
                    if isinstance(virtual_tours[0], dict):
                        virtual_tour = virtual_tours[0].get('href', 'N/A')
                
                #if virtual_tour != 'N/A':
                #    print(f"Virtual Tour: {virtual_tour}")
            except Exception as e:
                print(f"Error processing virtual tour: {str(e)}")
            
            # Contact info
            contact_phone = "N/A"
            try:
                advertisers = prop.get('advertisers', [])
                if advertisers and isinstance(advertisers, list):
                    for advertiser in advertisers:
                        if not isinstance(advertiser, dict):
                            continue
                            
                        if advertiser.get('type') == "management" and advertiser.get('office'):
                            office = advertiser.get('office')
                            if isinstance(office, dict):
                                phones = office.get('phones', [])
                                if phones and isinstance(phones, list) and len(phones) > 0:
                                    if isinstance(phones[0], dict):
                                        contact_phone = phones[0].get('number', 'N/A')
                
                #if contact_phone != 'N/A':
                #    print(f"Contact Phone: {contact_phone}")
            except Exception as e:
                print(f"Error processing contact info: {str(e)}")
            
            # Permalink
            permalink = prop.get('permalink', 'N/A')
            listing_url = "N/A"
            try:
                if permalink != 'N/A':
                    listing_url = f"https://www.realtor.com/rentals/details/{permalink}"
                    #print(f"Listing URL: {listing_url}")
            except Exception as e:
                print(f"Error creating listing URL: {str(e)}")
            
            # Add data to records list
            try:
                property_records.append({
                    "Address": address_line,
                    "City": city,
                    "State": state,
                    "Zip": zip_code,
                    "Monthly Rent": formatted_rent,
                    "Rent": rent,
                    "Beds": beds,
                    "Baths": baths,
                    "Sq Ft": sqft,
                    "Property Type": property_type_desc,
                    "Sub Type": sub_type,
                    "Status": status,
                    "Security Deposit": security_deposit,
                    "Available From": availability_date,
                    "Pets Allowed": pets_string,
                    "Listing ID": listing_id,
                    "Property ID": property_id,
                    "List Date": list_date,
                    "Contact Phone": contact_phone,
                    "Primary Image": primary_image,
                    "Additional Photos": additional_photos,
                    "Virtual Tour": virtual_tour,
                    "Listing URL": listing_url
                })
            except Exception as e:
                print(f"Error adding property to records: {str(e)}")
        
        except Exception as e:
            print(f"Error processing property: {str(e)}")
            continue
    
    # Create DataFrame from records
    try:
        df = pd.DataFrame(property_records)
        
        #print(f"\n{'='*50}")
        #print(f"Found {len(property_records)} rental properties.")
        #print("Data stored in DataFrame")
        
        # Display DataFrame overview
        #print("\nDataFrame Preview:")
        #print(f"Shape: {df.shape}")
        #print(df.head())
        
        return df
    except Exception as e:
        print(f"Error creating DataFrame: {str(e)}")
        return None



# List to store property data for DataFrame

def search_properties(api_key, location, limit=1000):
    """
    Search for properties using the Realtor API
    
    Parameters:
        api_key (str): Your RapidAPI key
        location (str): City and state, e.g., "New York, NY"
        property_type (str): Type of property (house, condo, apartment)
        limit (int): Maximum number of results to return
    
    Returns:
        dict: JSON response from the API
    """
    url = 'https://realtor16.p.rapidapi.com/search/forsale'

    querystring =  {"location":location, 
                    "search_radius":"0",
                    "limit":limit}
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "realtor16.p.rapidapi.com"
    }
    
    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        #print(response.text)
        return None

def display_and_store_properties(properties_data):
    """Display property information in a readable format based on the actual JSON structure"""

    #Empty df to be filled in
    property_records = []

    if not properties_data or 'properties' not in properties_data:
        print("No properties found or invalid data")
        return
    
    for prop in properties_data['properties']:
        #print(f"\n{'='*50}")
        
        # Address information
        address = prop.get('location', {}).get('address', {})
        address_line = address.get('line', 'N/A')
        city = address.get('city', 'N/A')
        state = address.get('state_code', 'N/A')
        zip_code = address.get('postal_code', 'N/A')
        
        #print(f"Address: {address_line}")
        #print(f"City: {city}")
        #print(f"State: {state}")
        #print(f"Zip: {zip_code}")
        
        # Property details
        description = prop.get('description', {})
        price = prop.get('list_price', 'N/A')
        beds = description.get('beds', 'N/A')
        baths = description.get('baths_consolidated', 'N/A')
        sqft = description.get('sqft', 'N/A')
        lot_sqft = description.get('lot_sqft', 'N/A')
        property_type_desc = description.get('type', 'N/A')
        
        #if price != 'N/A':
        #    print(f"Price: ${price:,}")
        #else:
        #    print(f"Price: {price}")
        #print(f"Beds: {beds}")
        #print(f"Baths: {baths}")
        #print(f"Sq Ft: {sqft}")
        #print(f"Lot Size (sq ft): {lot_sqft}")
        #print(f"Property Type: {property_type_desc}")
        
        
        # Status flags
        flags = prop.get('flags', {})
        status_flags = []
        if flags.get('is_new_listing'):
            status_flags.append("NEW LISTING")
        if flags.get('is_price_reduced'):
            status_flags.append("PRICE REDUCED")
        if flags.get('is_pending'):
            status_flags.append("PENDING")
        if flags.get('is_foreclosure'):
            status_flags.append("FORECLOSURE")
        if flags.get('is_coming_soon'):
            status_flags.append("COMING SOON")
        if flags.get('is_new_construction'):
            status_flags.append("NEW CONSTRUCTION")
        if flags.get('is_contingent'):
            status_flags.append("CONTINGENT")
            
        status = ', '.join(status_flags) if status_flags else "ACTIVE"
        #print(f"Status: {status}")
        
        # Listing information
        listing_id = prop.get('listing_id', 'N/A')
        property_id = prop.get('property_id', 'N/A')
        list_date = prop.get('list_date', 'N/A')
        
        #print(f"Listing ID: {listing_id}")
        #print(f"Property ID: {property_id}")
        #print(f"List Date: {list_date}")
        
        # Images
        primary_image = (prop.get('primary_photo') or {}).get('href', 'N/A')
        #if primary_image != 'N/A':
        #    print(f"Primary Image: {primary_image}")
        
        # Additional photos count
        photos = prop.get('photos', [])
        additional_photos = len(photos) - 1 if photos and len(photos) > 1 else 0
        #if additional_photos > 0:
        #    print(f"Additional Photos: {additional_photos}")
        
        # Virtual tours
        virtual_tours = prop.get('virtual_tours', [])
        virtual_tour = virtual_tours[0].get('href', 'N/A') if virtual_tours and len(virtual_tours) > 0 else 'N/A'
        #if virtual_tour != 'N/A':
        #    print(f"Virtual Tour: {virtual_tour}")
        
        # Listing agency
        branding = prop.get('branding', [])
        listed_by = branding[0].get('name', 'N/A') if branding and len(branding) > 0 else 'N/A'
        #if listed_by != 'N/A':
        #    print(f"Listed By: {listed_by}")
        
        # Permalink
        permalink = prop.get('permalink', 'N/A')
        listing_url = f"https://www.realtor.com/realestateandhomes-detail/{permalink}" if permalink != 'N/A' else 'N/A'
        #print(f"Listing URL: {listing_url}")
        
        # Add data to records list
        property_records.append({
            "Address": address_line,
            "City": city,
            "State": state,
            "Zip": zip_code,
            "Price": price,
            "Beds": beds,
            "Baths": baths,
            "Sq Ft": sqft,
            "Lot Size (sq ft)": lot_sqft,
            "Property Type": property_type_desc,
            "Status": status,
            "Listing ID": listing_id,
            "Property ID": property_id,
            "List Date": list_date,
            "Primary Image": primary_image,
            "Additional Photos": additional_photos,
            "Virtual Tour": virtual_tour,
            "Listed By": listed_by,
            "Listing URL": listing_url
        })
    
    # Create DataFrame from records
    df = pd.DataFrame(property_records)
    
    #print(f"\n{'='*50}")
    #print(f"Found {len(property_records)} properties.")
    #print("Data stored in DataFrame")
    
    # Display DataFrame overview
    #print("\nDataFrame Preview:")
    #print(f"Shape: {df.shape}")
    #print(df.head())
    
    return df