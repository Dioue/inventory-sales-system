import pandas as pd
from statsforecast import StatsForecast
from statsforecast.models import TSB
from datetime import timedelta
from django.db.models import Sum
import numpy as np
from django.db.models.functions import TruncDay
from .models import SalesRecordItem, Product

def compute_mape(y_true, y_pred):
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

def get_all_products_with_sales():
    return (
        SalesRecordItem.objects
        .values_list('product_id', flat=True)
        .distinct()
    )

def get_bulk_sales_data():
    data = (
        SalesRecordItem.objects
        .annotate(ds=TruncDay('sales_record__date_issued'))
        .values('product_id', 'ds')
        .annotate(y=Sum('quantity'))
        .order_by('product_id', 'ds')
    )
    
    return pd.DataFrame.from_records(data).rename(columns={'product_id': 'unique_id'})

def forecast_all_products_bulk():
    df = get_bulk_sales_data()

    if df.empty:
        return []

    df['ds'] = pd.to_datetime(df['ds'])
    df = df[['unique_id', 'ds', 'y']]

    # Ensure one row per (unique_id, ds) before resampling
    df = df.groupby(['unique_id', 'ds']).agg({'y': 'sum'}).reset_index()

    # Resample to daily frequency for each product
    df = df.set_index('ds').groupby('unique_id').resample('D').sum().reset_index()
    df['y'] = df['y'].fillna(0)

    # Drop any residual duplicates (just in case)
    df = df.drop_duplicates(subset=['unique_id', 'ds'])

    # Filter based on sales thresholds
    product_sales = df.groupby('unique_id')['y'].sum()
    forecast_ids = product_sales[product_sales >= 10].index.tolist()
    fallback_ids = product_sales[product_sales < 10].index.tolist()

    results = []

    if forecast_ids:
        model = StatsForecast(models=[TSB(alpha_d=0.3, alpha_p=0.1)], freq='D', n_jobs=-1)
        df_forecast = df[df['unique_id'].isin(forecast_ids)]
        fitted = model.fit(df_forecast)
        forecast = fitted.predict(h=180)
        forecast['ds'] = pd.date_range(start=df['ds'].max() + timedelta(days=1), periods=180, freq="D")
        forecast = forecast.groupby(['unique_id', pd.Grouper(key='ds', freq='M')])['TSB'].sum().reset_index()
    else:
        forecast = pd.DataFrame()

    # Fetch product names in bulk
    product_names = dict(Product.objects.filter(id__in=forecast_ids + fallback_ids).values_list('id', 'name'))

    for product_id in forecast_ids:
        fcast = forecast[forecast['unique_id'] == product_id]['TSB'].tolist()
        results.append({
            "product_id": product_id,
            "product_name": product_names.get(product_id, "Unnamed"),
            "strategy": "forecast",
            "1_month": fcast[0] if len(fcast) > 0 else 0,
            "3_months": sum(fcast[:3]),
            "6_months": sum(fcast[:6]),
            "accuracy": None
        })

    for product_id in fallback_ids:
        recent = df[df['unique_id'] == product_id].set_index('ds').resample('M').sum().tail(6)
        results.append({
            "product_id": product_id,
            "product_name": product_names.get(product_id, "Unnamed"),
            "strategy": "fallback",
            "1_month": recent['y'].iloc[-1] if len(recent) >= 1 else 0,
            "3_months": recent['y'].tail(3).sum() if len(recent) >= 3 else 0,
            "6_months": recent['y'].sum(),
            "accuracy": 0
        })

    return results