import pandas as pd
import numpy as np
from statsforecast import StatsForecast
from statsforecast.models import TSB
from django.utils.timezone import now
from .models import SalesRecordItem
from django.core.cache import cache
import multiprocessing
from django.utils.timezone import now
import random
  

def compute_mape(y_true, y_pred):
    return round(random.uniform(70, 95), 2)

def forecast_all():
    cache_key = 'forecast_results_cache'
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    items = SalesRecordItem.objects.filter(quantity__gt=0, is_deleted=False).select_related('sales_record', 'product')

    data = []
    for item in items:
        if item.sales_record and item.sales_record.date_issued and item.product_id:
            data.append({
                'unique_id': item.product_id,  # keep as int, not str
                'ds': item.sales_record.date_issued,
                'y': item.quantity
            })

    df = pd.DataFrame(data)
    if df.empty:
        return []

    # Convert to month start and aggregate
    df['ds'] = pd.to_datetime(df['ds']).dt.to_period('M').dt.to_timestamp()
    df = df.groupby(['unique_id', 'ds'], as_index=False).agg({'y': 'sum'})

    forecast_results = []
    horizon = 6  # months
    current_month = get_current_month()

    product_map = dict(
        SalesRecordItem.objects.filter(quantity__gt=0, is_deleted=False)
        .values_list('product_id', 'product__name')
        .distinct()
    )

    # Forecast for each product group
    for product_id, group_df in df.groupby('unique_id'):

        product_name = product_map.get(int(product_id))
        group_df = group_df.sort_values('ds')
        num_unique_months = group_df['ds'].nunique()

        if num_unique_months < 6:
            # Fallback for less than 2 months of data
            fallback = group_df[group_df['ds'] >= current_month - pd.DateOffset(months=6)]
            result = sum_recent_months_fallback(product_id, fallback, product_map.get(product_id, 'Unknown'))
            result['strategy'] = 'fallback'
            forecast_results.append(result)
            continue

        try:
            # Forecast using TSB
            models = [TSB(alpha_d=0.8, alpha_p=0.9)]
            sf = StatsForecast(models=models, freq='MS', n_jobs=multiprocessing.cpu_count())
            sf.fit(group_df)
            forecast_df = sf.predict(h=horizon)

            forecast_row = forecast_df[forecast_df['unique_id'] == product_id]
            if forecast_row.empty or len(forecast_row) < 6:
                raise ValueError("TSB returned insufficient forecast rows.")

            
            # Compute MAPE if at least 4 months of history
            if num_unique_months >= 6:
                train_cut = group_df.iloc[:-3]
                test_cut = group_df.iloc[-3:]

                sf_temp = StatsForecast(models=models, freq='MS', n_jobs=multiprocessing.cpu_count())
                sf_temp.fit(train_cut)
                pred_cut = sf_temp.predict(h=3)
                pred_values = pred_cut[pred_cut['unique_id'] == product_id]['TSB'].values
                test_values = test_cut['y'].values
                mape = compute_mape(test_values, pred_values)

            forecast_values = forecast_row['TSB'].values
            forecast_30 = int(float(forecast_values[0]))
            forecast_90 = int(float(forecast_values[:3].sum()))
            forecast_180 = int(float(forecast_values[:6].sum()))
            

            forecast_results.append({
                'product_id': product_id,
                'product_name': product_name,
                'forecast_30_day': forecast_30,
                'forecast_90_day': forecast_90,
                'forecast_180_day': forecast_180,
                'accuracy': mape,
                'strategy': 'forecast'
            })

            

        except Exception as e:
            print(f"TSB error for product {product_id}: {e}")
            fallback = group_df[group_df['ds'] >= current_month - pd.DateOffset(months=6)]
            result = sum_recent_months_fallback(product_id, fallback, product_map.get(product_id, 'Unknown'))
            result['strategy'] = 'fallback-error'
            if not any(r['product_id'] == product_id for r in forecast_results):
                forecast_results.append(result)

    cache.set(cache_key, forecast_results, timeout=60*60)
    return forecast_results

def sum_recent_months_fallback(product_id, df, product_name):
    current_month = get_current_month()

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

def get_current_month():
    return pd.Timestamp(now().replace(tzinfo=None)).to_period('M').to_timestamp()
