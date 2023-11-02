import requests
import numpy as np
from models.location_request import LocationRequestModel
from fastapi import APIRouter, HTTPException

router = APIRouter()



@router.post("/api/location/synchronize")
async def predict(body: LocationRequestModel):
    try:
        micro_times = []
        latitudes = []
        longitudes = []

        for location in body.locations:
            micro_times.append(location['microTime'])
            latitudes.append(location['latitude'])
            longitudes.append(location['longitude'])

        # time from locations, set first to 0
        micro_times = np.array(micro_times)
        micro_times = micro_times - micro_times[0]

        # time from juang's prediction
        times_to_estimate = np.array(body.times)
        micro_times_to_estimate = times_to_estimate * 1_000_000

        # estimated_geolocations = np.interp(micro_times_to_estimate, nearest_times, nearest_geolocations[1])
        estimated_latitudes = np.interp(micro_times_to_estimate, micro_times, latitudes)
        estimated_longitudes = np.interp(micro_times_to_estimate, micro_times, longitudes)

        result = []
        for i, time in enumerate(body.times):
            result.append({
                'time': time,
                'latitude': estimated_latitudes[i],
                'longitude': estimated_longitudes[i]
            })

        return {
            'locations': result
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))