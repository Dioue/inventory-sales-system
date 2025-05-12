import pandas as pd
from statsforecast import StatsForecast
from statsforecast.models import TSB
from datetime import timedelta
from django.db.models import Sum
import numpy as np

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

def get_sales_data_for_forecast(product_id):
    data = (
        SalesRecordItem.objects
        .filter(product_id=product_id)
        .values('sales_record__date_issued')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('sales_record__date_issued')
    )

    if not data:
        return None

    df = pd.DataFrame.from_records(data)
    df.rename(columns={'sales_record__date_issued': 'ds', 'total_quantity': 'y'}, inplace=True)
    df['ds'] = pd.to_datetime(df['ds'])
    df['unique_id'] = str(product_id)
    return df[['unique_id', 'ds', 'y']]

def forecast_all_products():
    tsb_model = TSB(alpha_d=0.3, alpha_p=0.1)
    forecast_horizon = 180

    results = []

    product_ids = get_all_products_with_sales()
    for product_id in product_ids:
        df = get_sales_data_for_forecast(product_id)
        if df is None or df.empty:
            continue

        total_sales = df['y'].sum()
        product_name = Product.objects.filter(id=product_id).first().name

        # Fallback if sales are too low
        if total_sales < 10:
            recent = df.set_index("ds").resample("ME").sum().tail(6)
            results.append({
                "product_id": product_id,
                "product_name": product_name,
                "strategy": "fallback",
                "1_month": recent['y'].iloc[-1] if len(recent) >= 1 else 0,
                "3_months": recent['y'].tail(3).sum() if len(recent) >= 3 else 0,
                "6_months": recent['y'].sum(),
                "accuracy": round(0, 2)
            })
            continue

        # Forecasting
        df = df.set_index("ds").groupby("unique_id")["y"].resample("D").sum().reset_index()
        model = StatsForecast(models=[tsb_model], freq='D', n_jobs=1)
        fitted = model.fit(df)
        forecast = fitted.predict(h=forecast_horizon)

        forecast["ds"] = pd.date_range(start=df['ds'].max() + timedelta(days=1), periods=forecast_horizon, freq="D")
        forecast = forecast.set_index("ds").groupby("unique_id")["TSB"].resample("ME").sum().reset_index()

        # Accuracy calculation
        train = df[df['ds'] <= df['ds'].max() - timedelta(days=30)]
        test = df[df['ds'] > df['ds'].max() - timedelta(days=30)]

        if len(test) < 10:
            accuracy = 0
        else:
            model_bt = StatsForecast(models=[tsb_model], freq="D", n_jobs=1)
            fitted_bt = model_bt.fit(train)
            forecast_bt = fitted_bt.predict(h=30)
            y_pred = forecast_bt['TSB'].values
            y_true = test.set_index("ds").groupby("unique_id")["y"].resample("D").sum().values
            accuracy = 100 - compute_mape(y_true, y_pred)

        results.append({
            "product_id": product_id,
            "product_name": product_name,
            "strategy": "forecast",
            "1_month": forecast.groupby("unique_id")["TSB"].sum().iloc[0] if len(forecast) >= 1 else 0,
            "3_months": forecast.groupby("unique_id")["TSB"].sum().iloc[:3].sum() if len(forecast) >= 3 else 0,
            "6_months": forecast.groupby("unique_id")["TSB"].sum().iloc[:6].sum(),
            "accuracy": round(accuracy, 2) if accuracy is not None else 0,
        })

    return results
