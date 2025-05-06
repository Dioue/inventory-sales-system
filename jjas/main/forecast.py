import pandas as pd
from statsforecast import StatsForecast
from statsforecast.models import TSB
from datetime import datetime
from django.db.models import Sum

def get_sales_data_for_forecast(product_id):
    from .models import SalesRecordItem

    data = (
        SalesRecordItem.objects
        .filter(product_id=product_id)
        .values('sales_record__date_issued')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('sales_record__date_issued')
    )

    print(data)

    if not data:
        return None 

    df = pd.DataFrame.from_records(data)
    df.rename(columns={'sales_record__date_issued': 'ds', 'total_quantity': 'y'}, inplace=True)
    df['ds'] = pd.to_datetime(df['ds'])
    df['unique_id'] = str(product_id)

    return df[['unique_id', 'ds', 'y']]

def forecast_tsb(product_id, horizon=30):
    df = get_sales_data_for_forecast(product_id)

    if df is None or df.empty:
        return {
            "error": f"No sales data found for product ID {product_id}. Forecasting aborted."
        }

    tsb_model = TSB(alpha_d=0.3, alpha_p=0.1)
    model = StatsForecast(
        models=[tsb_model],
        freq='D',
        n_jobs=1
    )

    forecast = model.forecast(df=df, h=horizon)
    return forecast
