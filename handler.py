import boto3
import requests

from datetime import datetime

CATALOG = 'https://tcgbusfs.blob.core.windows.net/blobtcmsv/TCMSV_alldesc.json'
LIVE = 'https://tcgbusfs.blob.core.windows.net/blobtcmsv/TCMSV_allavailable.json'


interesting_ids = {
    '001',
    '079',
}


def transform_park(park):
    available_car = park['availablecar']

    return {
        'id': park['id'],
        'availablecar': 0 if available_car == -9 else available_car,
    }


def put_metric(park):
    cw = boto3.client("cloudwatch")

    payload = [
        {
          'MetricName': 'parking',
          'Dimensions': [
            {
              'Name': 'park-id',
              'Value': park['id'],
            },
          ],
          'Value': park['availablecar'],
          'Unit': 'Count',
        },
      ]

    print(payload)

    response = cw.put_metric_data(
      Namespace='scu-cloud-2105',
      MetricData=payload,
    )

    print(response)


def crawl(event, context):
    parking_info = requests.get(LIVE).json().get('data', {}).get('park', [])
    interesting_parks = [park for park in parking_info if park.get('id') in interesting_ids]

    for park in interesting_parks:
        put_metric(park)

    return {
        'event': event,
        'parks': [transform_park(park) for park in interesting_parks],
    }


