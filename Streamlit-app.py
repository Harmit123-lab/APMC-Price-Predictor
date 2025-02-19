import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import hashlib
import os
import joblib
import statsmodels
from matplotlib import font_manager as fm
from pathlib import Path


base_dir = Path("D:/APMC-price-predictor")
font_path = base_dir / "NotoSerifGujarati-Black.ttf"
guj_fonts = fm.FontProperties(fname=font_path)


def safe_filename(product_name):
    return hashlib.md5(product_name.encode('utf-8')).hexdigest()


st.header("Welcome to APMC Price Predictor!")

category = st.selectbox("Category:", ("Commodities", "Fruits", "Vegetables"), index=None, placeholder="Select a category")

if category is not None:
    
    st.write(f"you choose category as {category}")

    if category == "Commodities":
        product = st.selectbox("Products:",
                            ('કપાસ બી. ટી.', 'ઘઉં લોકવન', 'ઘઉં ટુકડા', 'મગફળી જીણી', 'સિંગદાણા જાડા',
                            'સિંગ ફાડીયા', 'એરંડા / એરંડી', 'જીરૂ', 'ક્લંજી', 'વરીયાળી', 'ધાણા',
                            'લસણ સુકું', 'ડુંગળી લાલ', 'અડદ', 'તુવેર', 'રાયડો', 'રાય', 'મેથી', 'કાંગ',
                            'કરીજીરી', 'સુરજમુખી', 'ગુવાર બી', 'મગફળી જાડી', 'સફેદ ચણા', 'મગફળી નવી',
                            'તલ - તલી', 'ધાણી', 'બાજરો', 'જુવાર', 'મકાઇ', 'મગ', 'ચણા', 'વાલ', 'વાલ પાપડી',
                            'ચોળા / ચોળી', 'સોયાબીન', 'અજમાં', 'ગોગળી', 'વટાણા', 'તલ કાળા', 'મઠ', 'ઇસબગુલ',
                            'રાજગરો', 'તલ લાલ', 'કપાસ નવો', 'સુવાદાણા', 'મગફળી 66', 'અરીઠા', 'કળથી',
                            'મરચા સૂકા પટ્ટો', 'મરચા', 'ડુંગળી સફેદ', 'નવા ધાણા'),
                            index=None,
                            placeholder="Select a product to predict its price")
        
        if product is not None:
            st.write(f"You choose to find prediction for   {product}")
            
            file_path = base_dir / "data/commodities/temp.csv"
            save_dir = base_dir / "models/commodities_saved_models"
            
            data = pd.read_csv(file_path, parse_dates=['Date'], index_col='Date')
            
            product_name = product
            product_data = data[data["Item Name"] == product_name]
            
            hashed_name = safe_filename(product_name)
            model_filename = os.path.join(save_dir, f"arima_model_{hashed_name}.pkl")
            
            if product_data.empty:
                st.warning(f"No data found for the commodity: {product_name}")

            else:
                # Extract the 'Average Price' column for the selected commodity
                price_data = product_data['Average Price']

                # Plot the raw price data for the selected commodity
                data_figure = plt.figure(figsize=(12, 6))
                plt.plot(price_data.index, price_data, label=f'Prices', marker='o', linestyle='-')
                plt.title(f'Price Trend for {product_name}', fontproperties=guj_fonts)
                plt.xlabel('Date')
                plt.ylabel('Average Price')
                plt.xticks(rotation=90)
                plt.legend()
                plt.grid()
                plt.tight_layout()
                st.pyplot(data_figure) # plt.show()

            if os.path.exists(model_filename):
                st.write(f"Model for {product_name} loaded successfully.")
                loaded_model = joblib.load(model_filename)
                st.write(loaded_model.summary())
                
                # Step 6: In-sample Predictions
                pred = loaded_model.get_prediction(start=0, end=len(price_data)-1)
                pred_mean = pred.predicted_mean
                pred_ci = pred.conf_int()
                
                # Step 7: Forecast Future Prices
                forecast_steps = st.slider("Number of days to forecast:", min_value=1, max_value=30, value=10)
                forecast = loaded_model.get_forecast(steps=forecast_steps)
                forecast_mean = forecast.predicted_mean
                forecast_ci = forecast.conf_int()
                
                # Step 8: Plot the Results with Detailed Y-Axis (Zoomed-In)
                prediction_figure = plt.figure(figsize=(12, 6))

                # # Plot observed prices
                plt.plot(price_data.index, price_data, label='Observed', marker='o', linestyle='-', color='blue')

                # # Plot in-sample predictions
                plt.plot(pred_mean.index, pred_mean, label='In-sample Prediction', color='orange', linestyle='--')

                # # Plot forecasted prices
                plt.plot(forecast_mean.index, forecast_mean, label='Forecast', color='green', linestyle='-.')

                # # Add confidence intervals for forecasts
                plt.fill_between(forecast_ci.index,
                                forecast_ci.iloc[:, 0],
                                forecast_ci.iloc[:, 1], color='green', alpha=0.2, label='Forecast CI')

                # # Adjust the y-axis range based on observed and forecasted prices
                plt.ylim(price_data.min() * 0.95, price_data.max() * 1.05)

                # # Graph labels and legend
                plt.title(f'Price Prediction for {product_name}', fontproperties=guj_fonts)
                plt.xlabel('Date')
                plt.ylabel('Average Price')
                plt.xticks(rotation=90)
                plt.legend()
                plt.grid()
                plt.tight_layout()
                st.pyplot(prediction_figure) #plt.show()
            else:
                st.warning(f"Model for {product_name} not found.")
        
        else:
           st.warning('Please select a product.') 
            
else:
    st.warning('Please select a category.')