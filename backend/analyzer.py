import pandas as pd

def analyze_data(path):
    df = pd.read_csv(path)

    df['ctr'] = (df['clicks'] / df['impressions']) * 100
    df['rpm'] = (df['revenue'] / df['impressions']) * 1000

    insights = []

    for _, row in df.iterrows():
        if row['ctr'] < 1.5:
            insights.append({
                "ad_unit": row['ad_unit_id'],
                "issue": "Low CTR",
                "value": round(row['ctr'], 2)
            })

        if row['rpm'] < 2:
            insights.append({
                "ad_unit": row['ad_unit_id'],
                "issue": "Low Revenue",
                "value": round(row['rpm'], 2)
            })

    return insights