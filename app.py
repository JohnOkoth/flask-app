from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import numpy as np
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

@app.route('/')

def index():
    return render_template('index4.html')

def home():
   return render_template('index4.html')

# Predefined data
car_types = ['Ford Explorer', 'Hyundai Sonata', 'Mazda CX-9', 'Rivian R1T', 'Subaru Legacy', 'Toyota RAV4']
vehicle_use = ['Business', 'Drive Long', 'Drive Short', 'Pleasure']
car_years = [str(year) for year in range(1990, 2023)]  # Updated range if needed
car_type_coefficients = {
    'Ford Explorer': 0.010390346,
    'Hyundai Sonata': 0.060737991,
    'Mazda CX-9': 0,
    'Rivian R1T': 0.489404768,
    'Subaru Legacy': 0.051222965,
    'Toyota RAV4': -0.013845096
}

# Age category coefficients
age_category_coefficients = {
    'A': 0.110355346,
    'B': 0.064990189,
    'C': 0.057691304,
    'D': 0.057799161,
    'E': -0.114923909,
    'F': 0,
    'G': -0.017234657,
    'H': -0.021153315
}

# Vehicle Use coefficients
vehicle_use_coefficients = {
    'Business': 0.204292730677246,
    'Drive Long': 0.053696249,
    'Drive Short': 0,
    'Pleasure': -0.071455025
}

# UBI coefficients
ubi_coefficients = {
    'Age_A': 0.13097324,
    'Age_B': 0.05129945,
    'Age_C': 0.04407275,
    'Age_D': 0.04433218,
    'Age_E': -0.13094979,
    'Age_F': 0.00000000,
    'Age_G': -0.02091822,
    'Age_H': -0.03078079,
    'Car_Model_Ford Explorer': 0.01116192,
    'Car_Model_Hyundai Sonata': 0.05815648,
    'Car_Model_Mazda_CX-9': 0.00000000,
    'Car_Model_Rivian R1T': 0.37580729,
    'Car_Model_Subaru Legacy': 0.07039180,
    'Car_Model_Toyota RAV4': -0.04172163,
    'Vehicle_Use_Business': 0.17464391,
    'Vehicle_Use_DriveLong': 0.04187783,
    'Vehicle_Use_DriveShort': 0.00000000,
    'Vehicle_Use_Pleasure': -0.09327380
}

bias = 5.602446556
bias2 = 5.31972
bias3 = 5.60138512  # UBI bias

# Path to the Excel file
excel_file_path = 'users_data.xlsx'

@app.route('/options/car_types', methods=['GET'])
def get_car_types():
    return jsonify(car_types), 200

@app.route('/options/vehicle_use', methods=['GET'])
def get_vehicle_use():
    return jsonify(vehicle_use), 200

@app.route('/options/car_years', methods=['GET'])
def get_car_years():
    return jsonify(car_years), 200

@app.route('/user', methods=['POST', 'PUT'])
def manage_user():
    user_data = request.json
    bias_factor = user_data.get('bias_factor', 5.31972)  # Default value if not provided
    success, message, rate, rate2, rate3, rate4 = update_excel(user_data, bias_factor)  # Modify update_excel to return rate3
    if success:
        return jsonify({"message": message, "rate": rate, "rate2": rate2, "rate3": rate3, "rate4": rate4}), 200
    else:
        return jsonify({"message": message}), 400

def calculate_age(dob):
    today = datetime.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def determine_age_category(age, gender):
    if age < 25:
         return 'A' if gender == 'Male' else 'B'
    elif 25 <= age <= 40:
         return 'C' if gender == 'Male' else 'D'
    elif 40 < age <= 55:
         return 'E' if gender == 'Male' else 'F'
    else:
         return 'G' if gender == 'Male' else 'H'

def update_excel(user_data, bias_factor):
    print("Received bias_factor in update_excel:", bias_factor)
    df = load_or_initialize_excel()
    
    car_type = user_data['car_information']['type']
    vehicle_use = user_data['car_information']['use']
    car_year = user_data['car_information']['year']
    dob = datetime.strptime(user_data['personal_information']['dob'], '%Y-%m-%d')  # Assuming dob is in 'YYYY-MM-DD' format
    gender = user_data['personal_information']['gender']  # Extract gender here
    age = calculate_age(dob)
    age_category = determine_age_category(age, gender)

    # Validate car type and year
    if car_type not in car_types or car_year not in car_years:
        return False, "Invalid car type or year", None, None, None

    # Calculate the rate using general coefficients
    rate = np.exp(bias + car_type_coefficients.get(car_type, 0) + age_category_coefficients.get(age_category, 0) + vehicle_use_coefficients.get(vehicle_use, 0))
    
    # Calculate the rate using bias2
    rate2 = np.exp(bias2 + car_type_coefficients.get(car_type, 0) + age_category_coefficients.get(age_category, 0) + vehicle_use_coefficients.get(vehicle_use, 0))
    
    # Calculate the rate using UBI coefficients (bias3)
    rate3 = np.exp(bias3 + ubi_coefficients.get(f'Age_{age_category}', 0) + ubi_coefficients.get(f'Car_Model_{car_type}', 0) + ubi_coefficients.get(f'Vehicle_Use_{vehicle_use}', 0))

    # Calculate rate4 using the selected bias factor
    rate4 = np.exp(bias_factor + car_type_coefficients.get(car_type, 0) + age_category_coefficients.get(age_category, 0) + vehicle_use_coefficients.get(vehicle_use, 0))

    # Construct the new row for the DataFrame
    new_row = {
        'User ID': user_data['user_id'],
        'Name': user_data['personal_information']['name'],
        'Email': user_data['personal_information']['email'],
        'DOB': user_data['personal_information']['dob'],
        'Age': age,
        'Age category': age_category,
        'Gender': gender,
        'Vehicle Use': vehicle_use,
        'Car Type': car_type,
        'Car Make': user_data['car_information']['make'],
        'Car Model': user_data['car_information']['model'],
        'Car Year': car_year,
        'Rate': rate,
        'Rate2': rate2,
        'Rate3': rate3,
        'Rate4': rate4
    }

    # Append or update the DataFrame
    df = append_or_update_df(df, new_row)
    df.to_excel(excel_file_path, index=False, engine='openpyxl')
    return True, "Data updated successfully.", rate, rate2, rate3, rate4

def load_or_initialize_excel():
    if os.path.exists(excel_file_path):
        return pd.read_excel(excel_file_path, engine='openpyxl')
    else:
        return pd.DataFrame(columns=['User ID', 'Name', 'Email', 'Vehicle Use', 'Car Type', 'DOB', 'Age', 'Age category', 'Gender', 'Car Make', 'Car Model', 'Car Year', 'Rate','Rate2','Rate3','Rate4'])

def append_or_update_df(df, new_row):
    if new_row['User ID'] in df['User ID'].values:
        index = df.index[df['User ID'] == new_row['User ID']][0]
        for key in new_row:
            df.at[index, key] = new_row[key]
    else:
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    return df

if __name__ == '__main__':
    print(app.url_map)
    app.run(debug=True, use_reloader=False)
