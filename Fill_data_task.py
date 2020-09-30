#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 10:07:02 2020

@author: matthias
"""

import pandas as pd

def granular_data(df):
	# function transforms supplier data into new dataframe with unique attributes as features (columns)
    #df ... pd.DataFrame with unique attributes in column Attribute Names
    # unique attributes in column 'Attribute Names'
    attribute_names = df['Attribute Names'].unique().tolist()
    # new DataFrame unique attributes of supplier data file as features
    df_new = pd.DataFrame(columns = attribute_names)
    IDS = df.ID.unique() # unique ID values
    abs_counter = 0
    for ID in IDS:
        df_fixed_ID = df[df.ID==ID] # DataFrame with only one ID (only one car)
        temp_count = 0
        for attribute_name in attribute_names:
            if temp_count == 0:
                df_new.at[abs_counter, 'manufacturer'] = df_fixed_ID['MakeText'].iloc[0] # all values of 'MakeText' are the same, I pick the first one
                df_new.at[abs_counter, 'model'] = df_fixed_ID['ModelTypeText'].iloc[0]
                df_new.at[abs_counter, 'ID'] = df_fixed_ID['ID'].iloc[0]
            temp_list = df_fixed_ID[df_fixed_ID['Attribute Names']==attribute_name]['Attribute Values'].values # attribute value for a certain attribute name as a list
            if len(temp_list)==0: # check if list empty
                # if list empty, enter 'null'
                df_new.at[abs_counter, attribute_name] = 'null'
            else: # if list not empty take the first (and only) entry
                df_new.at[abs_counter, attribute_name] = temp_list[0]
            temp_count +=1
        abs_counter +=1
    return df_new

def conv_str_to_number(df, column_list):
    # function to convert strings into integers
    # df ... Dataframe
    # column_list ... list of strings, list with features of df, which should be converted into numbers
    for column in column_list:
        df[column] = pd.to_numeric(df[column], errors='ignore')
    return df

def remove_unit(df, old_column_name, new_column_name, unit_to_remove):
    # functions removes unit from entries and converts remaining string into number
    # df ... DataFrame
    # old_column_name ... string, old name of column
    # new_column_name ... string, new name of column
    # unit_to_remove ... string, unit to remove in column df.old_column_name
    
    # change column name
    df.rename(columns={old_column_name: new_column_name}, inplace = True)
    # remove string unit_to_remove
    df.replace(to_replace= r' ' + unit_to_remove + '$', value='',regex=True, inplace = True)
    # replace 'null' with 0
    df[new_column_name].replace(to_replace='null', value=0, inplace = True)
    # convert string into number
    df = conv_str_to_number(df_norm, [new_column_name])    
    return df

def integration(df):
    # function transforms df into target data scheme
    # df ... Dataframe to transform
    df_integration = pd.DataFrame()
    df_integration['carType'] = df_proc.BodyTypeText
    df_integration['color'] = df_proc.BodyColorText
    df_integration['condition'] = df_proc.ConditionTypeText
    df_integration['currency'] = 'null'
    df_integration['drive'] = 'null'
    df_integration['city'] = df_proc.City
    df_integration['country'] = 'CH'
    df_integration['make'] = df_proc.manufacturer
    df_integration['manufacture_year'] = df_proc.FirstRegYear
    df_integration['milage'] = df_proc.Km
    df_integration['milage_unit'] = 'kilometer'
    df_integration['model'] = df_proc.model
    df_integration['model_variant'] = 'null'
    df_integration['price_on_request'] = 'null''price_on_request'
    df_integration['type'] = df_proc.BodyTypeText.replace(to_replace = ['Cabriolet', 'SUV / Geländewagen', 'Kombi', 'Limousine', 'Coupé', 
                                                                        'Kompaktvan / Minivan', 'Pick-up', 'Kleinwagen'], value = 'car')
    df_integration['zip'] = df_proc.City.replace(to_replace = ['Zuzwil', 'Sursee', 'Porrentruy', 'St. Gallen', 
                                                               'Basel','Safenwil'],
                                                value = ['9524', '6210', '2900', '9000-9022','4000-4091','5745'])
    df_integration['manufacture_month'] = df_proc.FirstRegMonth
    df_integration['fuel_consumption_unit'] = 'l/100km_consumption'
    
    return df_integration
    
    
# read supplier file
df = pd.read_json(path_or_buf = 'supplier_car.json',lines=True)
# step 1: Pre-processing
df_proc = granular_data(df)

#-------------------------------------------------------------------------------------
# step 2: normalisation

df_norm = df_proc.copy()
# converting strings into numnbers
column_list = ['Seats', 'Ccm', 'Doors', 'FirstRegYear', 'Km', 'FirstRegMonth', 'Hp' ]
df_norm = conv_str_to_number(df_norm, column_list)

# change consumption data
df_norm = remove_unit(df_norm, 'ConsumptionTotalText', 'Consumption l/100km', 'l/100km')

# change emission data
df_norm = remove_unit(df_norm, 'Co2EmissionText', 'CO2 emission g/km', 'g/km')

#-------------------------------------------------------------------------------------
# step 3: integration

df_integration = integration(df_norm)

#-------------------------------------------------------------------------------------
# step 4: Export into Excel file
with pd.ExcelWriter('output.xlsx') as writer:  
    df_proc.to_excel(writer, sheet_name='pre-processing', index=False)
    df_norm.to_excel(writer, sheet_name='normalisation', index=False)
    df_integration.to_excel(writer, sheet_name='integration', index=False)
