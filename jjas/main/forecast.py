import pandas as pd
import numpy as np
from statsforecast import StatsForecast
from statsforecast.models import TSB
from django.utils.timezone import now
from .models import SalesRecordItem

def safe_mape(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    mask = y_true != 0
    if not np.any(mask):
        return 0.0  # Avoid division by zero
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask]))

def forecast_all():
    return {
        'product_id': 3,
        'product_name': "product_name",
        'forecast_30_day': 23,
        'forecast_90_day': 23,
        'forecast_180_day': 23,
        'accuracy': 0.1,
        "strategy": "forecast",
    }, {
        'product_id': 3,
        'product_name': "product_name",
        'forecast_30_day': 23,
        'forecast_90_day': 23,
        'forecast_180_day': 23,
        'accuracy': 0.1,
        "strategy": "forecast",
    }, {
        'product_id': 3,
        'product_name': "product_name",
        'forecast_30_day': 23,
        'forecast_90_day': 23,
        'forecast_180_day': 23,
        'accuracy': 0.1,
        "strategy": "forecast",
    }, {
        'product_id': 3,
        'product_name': "product_name",
        'forecast_30_day': 23,
        'forecast_90_day': 23,
        'forecast_180_day': 23,
        'accuracy': 0.1,
        "strategy": "forecast",
    }, {
        'product_id': 3,
        'product_name': "product_name",
        'forecast_30_day': 23,
        'forecast_90_day': 23,
        'forecast_180_day': 23,
        'accuracy': 0.1,
        "strategy": "forecast",
    }, {
        'product_id': 3,
        'product_name': "product_name",
        'forecast_30_day': 23,
        'forecast_90_day': 23,
        'forecast_180_day': 23,
        'accuracy': 0.1,
        "strategy": "forecast",
    }, {
        'product_id': 3,
        'product_name': "product_name",
        'forecast_30_day': 23,
        'forecast_90_day': 23,
        'forecast_180_day': 23,
        'accuracy': 0.1,
        "strategy": "forecast",
    }, {
        'product_id': 3,
        'product_name': "product_name",
        'forecast_30_day': 23,
        'forecast_90_day': 23,
        'forecast_180_day': 23,
        'accuracy': 0.1,
        "strategy": "forecast",
    }, {
        'product_id': 3,
        'product_name': "product_name",
        'forecast_30_day': 23,
        'forecast_90_day': 23,
        'forecast_180_day': 23,
        'accuracy': 0.1,
        "strategy": "forecast",
    }, {
        'product_id': 3,
        'product_name': "product_name",
        'forecast_30_day': 23,
        'forecast_90_day': 23,
        'forecast_180_day': 23,
        'accuracy': 0.1,
        "strategy": "forecast",
    }, {
        'product_id': 3,
        'product_name': "product_name",
        'forecast_30_day': 23,
        'forecast_90_day': 23,
        'forecast_180_day': 23,
        'accuracy': 0.1,
        "strategy": "forecast",
    }, {
        'product_id': 3,
        'product_name': "product_name",
        'forecast_30_day': 23,
        'forecast_90_day': 23,
        'forecast_180_day': 23,
        'accuracy': 0.1,
        "strategy": "forecast",
    }, {
        'product_id': 3,
        'product_name': "product_name",
        'forecast_30_day': 23,
        'forecast_90_day': 23,
        'forecast_180_day': 23,
        'accuracy': 0.1,
        "strategy": "forecast",
    }, {
        'product_id': 3,
        'product_name': "product_name",
        'forecast_30_day': 23,
        'forecast_90_day': 23,
        'forecast_180_day': 23,
        'accuracy': 0.1,
        "strategy": "forecast",
    }, {
        'product_id': 3,
        'product_name': "product_name",
        'forecast_30_day': 23,
        'forecast_90_day': 23,
        'forecast_180_day': 23,
        'accuracy': 0.1,
        "strategy": "forecast",
    }, 


def sum_recent_months_fallback(product_id, df, product_name):
    current_month = pd.Timestamp(now()).to_period('M').to_timestamp()

    def sum_last_n_months(n):
        start = current_month - pd.DateOffset(months=n)
        return float(df[(df['ds'] > start) & (df['ds'] <= current_month)]['y'].sum())

    return {
        'product_id': product_id,
        'product_name': product_name,
        'forecast_30_day': sum_last_n_months(1),
        'forecast_90_day': sum_last_n_months(3),
        'forecast_180_day': sum_last_n_months(6),
        'accuracy': 0.0,
        "strategy": "fallback"
    }
