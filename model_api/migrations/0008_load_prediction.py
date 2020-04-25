# Generated by Django 3.0.4 on 2020-04-12 23:09

from django.db import migrations
import csv
import datetime

GLOBAL_QUARANTINE_PREDICTION_CSV_PATH = '../results/forecasts/formatted_reports/formatted_global_forecasts_quarantine_4_24.csv'
GLOBAL_RELEASED_PREDICTION_CSV_PATH = '../results/forecasts/formatted_reports/formatted_global_forecasts_released_4_24(cleaned).csv'
US_QUARANTINE_PREDICTION_CSV_PATH = '../results/forecasts/formatted_reports/formatted_us_forecasts_quarantine_4_24.csv'
US_RELEASED_PREDICTION_CSV_PATH = '../results/forecasts/formatted_reports/formatted_us_forecasts_released_4_24(cleaned).csv'

paths = [GLOBAL_QUARANTINE_PREDICTION_CSV_PATH, GLOBAL_RELEASED_PREDICTION_CSV_PATH, US_QUARANTINE_PREDICTION_CSV_PATH, US_RELEASED_PREDICTION_CSV_PATH]

def load_covid19_prediction(apps, schema_editor):
    Area = apps.get_model('model_api', 'Area')
    Covid19QuarantinePredictionDataPoint = apps.get_model('model_api', 'Covid19QuarantinePredictionDataPoint')
    Covid19ReleasedPredictionDataPoint = apps.get_model('model_api', 'Covid19ReleasedPredictionDataPoint')
    
    for path in paths:
        with open(path, 'r') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            
            for row in reader:
                area = None
                if 'global' in path:
                    country = row[1]
                    state = ''
                elif 'us' in path:
                    country = 'US'
                    state = row[1]
                else:
                    msg = 'Unknown prediction filename. Stop loading prediction data.'
                    print (msg)
                    break 

                # Find the area in the model_api_area
                try: 
                    area = Area.objects.get(country=country, state=state)
                except Area.DoesNotExist:
                    msg = "Could not find the area for country '{0}'".format(country)
                    if state:                            
                        msg += " and state '{0}'".format(state)
                    area = Area(state=state, country=country)
                    area.save()
                    msg += ' in model_api_area. New area created.'
                    print(msg)

                except Area.MultipleObjectsReturned:
                    msg = "Found multiple areas for country '{0}'".format(country)
                    if state:
                        msg += " and state '{0}'".format(state)
                    msg += ' in model_api_area. Skip this area.'
                    print(msg)
                    continue
            
                for i in range(2, len(header)):
                    date = header[i]
                    val = int(float(row[i]))

                    covid19_prediction_data_point = None
                    if 'quarantine' in path:
                        covid19_prediction_data_point = Covid19QuarantinePredictionDataPoint(area=area, date=date, val=val)
                    elif 'released' in path:
                        covid19_prediction_data_point = Covid19ReleasedPredictionDataPoint(area=area, date=date, val=val)
                    else:
                        msg = 'Unknown prediction filename. Stop loading prediction data.'
                        print (msg)
                        break
                    covid19_prediction_data_point.save()

def delete_covid19_prediction(apps, schema_editor):
    Area = apps.get_model('model_api', 'Area')
    Covid19QuarantinePredictionDataPoint = apps.get_model('model_api', 'Covid19QuarantinePredictionDataPoint')
    Covid19ReleasedPredictionDataPoint = apps.get_model('model_api', 'Covid19ReleasedPredictionDataPoint')
    
    # Clear all prediction data points.
    Area.objects.all().delete()
    Covid19QuarantinePredictionDataPoint.all().delete()
    Covid19ReleasedPredictionDataPoint.all().delete()

class Migration(migrations.Migration):


    dependencies = [
        ('model_api', '0007_covid19predictiondatapoint'),
    ]

    operations = [
        migrations.RunPython(load_covid19_prediction, delete_covid19_prediction)
    ]
