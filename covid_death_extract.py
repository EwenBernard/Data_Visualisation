import csv
import glob

path = "covid_death"
header = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST",
          "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"]

with open(path + "/covid_death_by_month.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    line = []
    for file in glob.glob(path + "/*.txt"):
        print("process " + file)
        num_lines = sum(1 for line in open(file, 'r', encoding="utf8", errors='ignore'))
        line.append(num_lines)
    writer.writerow(line)
