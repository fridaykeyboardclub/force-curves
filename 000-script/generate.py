#! /usr/bin/env python3

import urllib
import os
from dataclasses import dataclass
from os.path import dirname, join
import csv
from matplotlib import pyplot as plot

def do_directory_walk():
    this_dir = dirname(dirname(__file__))
    print(this_dir)
    rootdir = dirname(this_dir)
    print(rootdir)

    savedir = join(this_dir, "image_output")
    if not os.path.exists(savedir):
        print("Created image output directory")
        os.mkdir(join(this_dir, "image_output"))

    markdown_file = open(join(savedir, "000_curves.md"), "w")
    markdown_file.write("# Force Curves\n\nFrom [ThereminGoat](https://github.com/ThereminGoat/force-curves)\n\n")

    for switch_dir_name in sorted(os.listdir(rootdir)):
        switch_dir_path = join(rootdir, switch_dir_name)
        if switch_dir_name == "000-script" or switch_dir_name.startswith("."):
            continue
        if not os.path.isdir(switch_dir_path):
            continue

        files_in_dir = os.listdir(switch_dir_path)
        csv_files = [x for x in files_in_dir if x.endswith(".csv") and not x.endswith("HighResolutionRaw.csv") and not x.endswith("HighResoultionRaw.csv")]
        for csv_file in csv_files:
            print(csv_file)
            csv_path = join(switch_dir_path, csv_file)
            csv_data = read_csv_data(csv_path)
            create_image(savedir, switch_dir_name, csv_data)

            escaped_filename = urllib.parse.quote(switch_dir_name)
            markdown_file.write("### %s\n\n![%s](%s.png)\n\n" % (switch_dir_name, switch_dir_name, escaped_filename))

    markdown_file.close()

    pass

@dataclass
class CsvData:
    data_x: list[float]
    data_y: list[float]
    peak_before_25: float

def read_csv_data(file: str) -> CsvData:
    with open(file) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        data_x = []
        data_y = []
        max_x = 0.0
        max_y_before_25 = 0.0
        for row in reader:
            try:
                # Data lines start with ints
                index = int(row[0])
                if row[5] == "OK": # indicates good data
                    displacement = float(row[3])
                    weight = float(row[1])
                    if displacement < max_x:
                        break
                    data_x.append(displacement)
                    data_y.append(weight)
                    max_x = displacement
                    if displacement <= 2.5:
                        max_y_before_25 = max(max_y_before_25, weight)
            except ValueError:
                pass
        print("%s data points read" % (len(data_x),))
        return CsvData(data_x, data_y, max_y_before_25)

def create_image(savedir: str, name: str, data: CsvData):
    plot.plot(data.data_x, data.data_y)
    plot.title(name)
    print("Peak before 25: %s" % (data.peak_before_25, ))
    axismax = 100 if data.peak_before_25 < 100 else 140
    plot.axis([0.0, 4.5, 0.0, axismax])
    plot.grid(visible=True)
    savename = name + ".png"
    plot.savefig(join(savedir, savename))
    plot.clf()

if __name__ == "__main__":
    do_directory_walk()

