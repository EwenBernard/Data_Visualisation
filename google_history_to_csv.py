import json, os
import csv

header = ['StartLocationLat', 'StartLocationLon', 'EndLocationLat', 'EndLocationLon', 'StartTime', 'EndTime', 'Distance', 'ActivityType']
i = 0
path = "Takeout/Historique des positions/Semantic Location History"
extractPath = "Extracted_Google_Maps_Data"

if not os.path.exists(extractPath):
    os.mkdir(extractPath)
    for folder in os.listdir(path):
        os.mkdir(extractPath + "/" + folder)
        for file in os.listdir(path + "/" + folder):
            print(file)
            with open(path + "/" + folder + "/" + file, "r",  encoding="utf8") as location_history:
                jsonData = json.loads(location_history.read())
                with open(extractPath + "/" + folder + "/" + file[:-5] + "_EXTRACT.csv", "w", newline='') as f:
                    dataset = []
                    writer = csv.writer(f)
                    writer.writerow(header)
                    timelineObjects = jsonData.get("timelineObjects")
                    for items in timelineObjects:
                        activitySegments = items.get("activitySegment")
                        if activitySegments is not None:
                            data = []
                            data.append(activitySegments.get('startLocation').get('latitudeE7'))
                            data.append(activitySegments.get('startLocation').get('longitudeE7'))
                            data.append(activitySegments.get('endLocation').get('latitudeE7'))
                            data.append(activitySegments.get('endLocation').get('longitudeE7'))
                            data.append(activitySegments.get('duration').get('startTimestampMs'))
                            data.append(activitySegments.get('duration').get('endTimestampMs'))
                            data.append(activitySegments.get('distance'))
                            data.append(activitySegments.get('activityType'))
                            if len(data) > 0:
                                dataset.append(data)
                    writer.writerows(dataset)
            print("Processed " + file)



