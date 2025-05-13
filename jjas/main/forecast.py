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
    
    mape = np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])
    capped_mape = np.clip(mape, 0, 1.0)  # Cap to 1.0 (100%)
    return np.mean(capped_mape) * 100  # Return as percentage

def forecast_all():
    items = SalesRecordItem.objects.filter(quantity__gt=0, is_deleted=False).select_related('sales_record', 'product')

    data = []
    for item in items:
        if item.sales_record and item.sales_record.date_issued and item.product_id:
            data.append({
                'unique_id': str(item.product_id),
                'ds': item.sales_record.date_issued,
                'y': item.quantity
            })

    df = pd.DataFrame(data)
    if df.empty:
        return []

    # Convert to month start and aggregate
    df['ds'] = pd.to_datetime(df['ds']).dt.tz_localize(None).dt.to_period('M').dt.to_timestamp()
    df = df.groupby(['unique_id', 'ds']).agg({'y': 'sum'}).reset_index()

    forecast_results = []
    horizon = 6  # months
    current_month = pd.Timestamp(now()).to_period('M').to_timestamp()

    for product_id, group_df in df.groupby('unique_id'):
        product_name = str(items.filter(product_id=product_id).first().product.name)
        group_df = group_df.sort_values('ds')
        num_unique_months = group_df['ds'].nunique()

        if num_unique_months < 2:
            # Fallback for less than 2 months of data
            fallback = group_df[group_df['ds'] >= current_month - pd.DateOffset(months=6)]
            result = sum_recent_months_fallback(product_id, fallback, product_name)
            result['strategy'] = 'fallback'
            forecast_results.append(result)
            continue

        try:
            # Forecast using TSB
            models = [TSB(alpha_d=0.8, alpha_p=0.9)]
            sf = StatsForecast(models=models, freq='MS', n_jobs=1)
            sf.fit(group_df)
            forecast_df = sf.predict(h=horizon)

            forecast_row = forecast_df[forecast_df['unique_id'] == product_id]
            if forecast_row.empty or len(forecast_row) < 6:
                raise ValueError("TSB returned insufficient forecast rows.")

            # Compute MAPE if at least 4 months of history
            if num_unique_months >= 4:
                train_cut = group_df.iloc[:-3]
                test_cut = group_df.iloc[-3:]

                sf_temp = StatsForecast(models=models, freq='MS', n_jobs=1)
                sf_temp.fit(train_cut)
                pred_cut = sf_temp.predict(h=3)
                pred_values = pred_cut[pred_cut['unique_id'] == product_id]['TSB'].values
                test_values = test_cut['y'].values
                mape = safe_mape(test_values, pred_values)
            else:
                mape = 0.0

            forecast_values = forecast_row['TSB'].values
            forecast_30 = forecast_values[0]
            forecast_90 = forecast_values[:3].sum()
            forecast_180 = forecast_values[:6].sum()
            

            forecast_results.append({
                'product_id': product_id,
                'product_name': product_name,
                'forecast_30_day': float(forecast_30),
                'forecast_90_day': float(forecast_90),
                'forecast_180_day': float(forecast_180),
                'accuracy': round(mape * 100, 2),
                'strategy': 'forecast'
            })

        except Exception as e:
            print(f"TSB error for product {product_id}: {e}")
            fallback = group_df[group_df['ds'] >= current_month - pd.DateOffset(months=6)]
            result = sum_recent_months_fallback(product_id, fallback, product_name)
            result['strategy'] = 'fallback-error'
            forecast_results.append(result)

    return forecast_results


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
        'strategy': 'fallback'
    }
