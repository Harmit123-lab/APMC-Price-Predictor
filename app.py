from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import joblib
import hashlib
from io import BytesIO
import base64
from matplotlib import font_manager as fm
from pathlib import Path

app = Flask(__name__)

app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))

base_dir = Path("D:/APMC-price-predictor-master")
font_path = base_dir / "NotoSerifGujarati-Black.ttf"
guj_fonts = fm.FontProperties(fname=font_path)
file_path = base_dir / "data/commodities/temp.csv"
model_dir = base_dir / "models/commodities_saved_models"

def safe_filename(product_name):
    return hashlib.md5(product_name.encode('utf-8')).hexdigest()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    # Get form data
    category = request.form.get("category")
    product = request.form.get("product")
    
    # category = "Commodities"
    # product = "જીરૂ"

    # Load data
    data = pd.read_csv(file_path, parse_dates=["Date"], index_col="Date", dayfirst=True)
    product_data = data[data["Item Name"] == product]

    if product_data.empty:
        error_message = "Oops.... Given Product does not exist :(   Redirecting to homepage...."
        return render_template("error.html", message=error_message)

    # Prepare file paths
    hashed_name = safe_filename(product)
    model_path = os.path.join(model_dir, f"arima_model_{hashed_name}.pkl")

    # Check if the model exists
    if not os.path.exists(model_path):
        error_message = "Model for the given product not found :(    Redirecting to homepage...."
        return render_template("error.html", message=error_message)

    # Load the model
    loaded_model = joblib.load(model_path)

    # In-sample predictions
    price_data = product_data["Average Price"]
    pred = loaded_model.get_prediction(start=0, end=len(price_data) - 1)
    pred_mean = pred.predicted_mean

    # Forecast
    forecast_steps = 10
    forecast = loaded_model.get_forecast(steps=forecast_steps)
    forecast_mean = forecast.predicted_mean
    forecast_ci = forecast.conf_int()
    
    # Ensure indices are proper DateTime format
    price_data.index = pd.to_datetime(price_data.index)
    forecast_mean.index = pd.to_datetime(forecast_mean.index)
    
    # print(price_data.index.dtype)  # Should be datetime64[ns]
    # print(forecast_mean.index.dtype)  # Should be datetime64[ns]
    # Ensure price_data.index is a DatetimeIndex
    last_date = pd.to_datetime(price_data.index[-1])  # Get the last date in your data
    forecast_horizon = len(forecast_mean)  # Number of future predictions
    
    # Generate future dates, excluding Sundays
    future_dates = []
    current_date = last_date + pd.Timedelta(days=1)

    while len(future_dates) < forecast_horizon:
        if current_date.weekday() != 6:  # 6 corresponds to Sunday
            future_dates.append(current_date)
        current_date += pd.Timedelta(days=1) 
    
    # Send JSON Data
    
    response = {
        "dates": [date.strftime("%d-%m-%Y") for date in price_data.index],
        "observed": [float(val) for val in price_data.values],  # Convert to float
        "predicted": [float(val) for val in pred_mean.values],  # Convert to float
        "forecast_dates": [date.strftime("%d-%m-%Y") for date in future_dates],
        "forecast": [float(val) for val in forecast_mean.values],  # Convert to float
    }
    return render_template("result.html", response=response, product=product)
    # return jsonify(response)

    # # Plot the results
    # fig, ax = plt.subplots(figsize=(10, 5))
    # ax.plot(price_data.index, price_data, label="Observed", color="blue")
    # ax.plot(pred_mean.index, pred_mean, label="In-sample Prediction", color="orange")
    # ax.plot(forecast_mean.index, forecast_mean, label="Forecast", color="green")
    # ax.fill_between(forecast_ci.index, forecast_ci.iloc[:, 0], forecast_ci.iloc[:, 1], color="green", alpha=0.2)
    
    #  # # Adjust the y-axis range based on observed and forecasted prices
    # plt.ylim(price_data.min() * 0.95, price_data.max() * 1.05)
    # ax.set_title(f"Price Prediction for {product}", fontproperties=guj_fonts)
    # ax.set_xlabel("Date")
    # plt.xticks(rotation=90)
    # ax.set_ylabel("Average Price")
    # ax.legend()
    # plt.tight_layout()

    # # Save plot as a base64 string
    # img = BytesIO()
    # plt.savefig(img, format="png")
    # img.seek(0)
    # plot_url = base64.b64encode(img.getvalue()).decode("utf8")

    # return render_template("result.html", plot_url=plot_url, product=product)

if __name__ == "__main__":
    app.run(debug=True)