import pandas as pd
from models import Attraction

print "here"

path = "D:\Documents\Tripadvisor\Singapore\Singapore_procd.csv"

df = pd.read_csv(path)

COUNTRY = 'Singapore'

attractions = [
    Attraction(
        name = df.loc[row]['Attraction'],
        rating = df.loc[row]['Rating'],
        num_reviews = df.loc[row]['NumReviews'],
        address = df.loc[row]['Address'],
        duration = df.loc[row]['Durations'],
        score = df.loc[row]['Score'],
        coordinates = df.loc[row]['Coordinates'],
        review_summary = df.loc[row]['ReviewsSummary'],
        day_0 = df.loc[row]['0'],
        day_1 = df.loc[row]['1'],
        day_2 = df.loc[row]['2'],
        day_3 = df.loc[row]['3'],
        day_4 = df.loc[row]['4'],
        day_5 = df.loc[row]['5'],
        day_6 = df.loc[row]['6'],
        country = COUNTRY,
        about = df.loc[row]['About'],
        categories = df.loc[row]['Categories'],
    )
    for row in range(len(df))
]
Attraction.objects.bulk_create(attractions)
