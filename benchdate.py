#!/usr/bin/env python3

import json
import re

nums = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

DMY4DASH = "[0-9]{1,2}-[0-9]{1,2}-([0-9]{4})"
DMY4SLASH = "[0-9]{1,2}/[0-9]{1,2}/([0-9]{4})"
DMY4DOT = "[0-9]{1,2}\.[0-9]{1,2}\.([0-9]{4})"
DMY4CDOT = "[0-9]{1,2}·[0-9]{1,2}·([0-9]{4})"
DMY4COLON = "[0-9]{1,2}:[0-9]{1,2}:([0-9]{4})"

DMY2DASH = "[0-9]{1,2}-[0-9]{1,2}-([0-9]{2})"
DMY2SLASH = "[0-9]{1,2}/[0-9]{1,2}/([0-9]{2})"
DMY2DOT = "[0-9]{1,2}\.[0-9]{1,2}\.([0-9]{2})"
DMY2CDOT = "[0-9]{1,2}·[0-9]{1,2}·([0-9]{2})"
DMY2COLON = "[0-9]{1,2}:[0-9]{1,2}:([0-9]{2})"

Y4Y4DASH = "([0-9]{4}) ?- ?([0-9]{4})"
Y4Y4TILDE = "([0-9]{4}) ?~ ?([0-9]{4})"

YEAR4 = "([0-9]{4})"
YEAR2 = "([0-9]{2})"
DAY2 = "[0-9]{2}"
DAY = "[0-9]{1,2}"
MONTH2 = "[0-9]{2}"
MONTH = "[0-9]{1,2}"
AGE1 = "[0-9]{1}"
AGE2 = "[0-9]{2}"
AGE3 = "[0-9]{3}"
NN = "[^0-9]+"
START = "^[^0-9]*"
END = "[^0-9]*$"

patterns = [
    # Year(s) only
    START + YEAR4 + END, # 1974
    START + YEAR2 + END, # 98
    START + YEAR4 + " - '?" + YEAR2 + END, # 1974 - 95
    START + YEAR4 + "-" + YEAR2 + END, # 1974-95
    START + Y4Y4DASH + END, # 1974-1995
    START + Y4Y4DASH + NN + Y4Y4DASH + END, # 1974-1995 1980-2021
    START + Y4Y4DASH + NN + Y4Y4DASH + NN + Y4Y4DASH + END, # 1974-1995 1980-2021
    START + Y4Y4DASH + NN + Y4Y4DASH + NN + Y4Y4DASH + NN + Y4Y4DASH + END, # 1974-1995 1980-2021
    START + YEAR4 + NN + YEAR4 + END, # Jun 1974 - July 1995
    YEAR4 + " to " + YEAR4 + "$", # 1974 1995
    START + Y4Y4TILDE + NN + Y4Y4TILDE + END,
    START + Y4Y4TILDE + NN + Y4Y4TILDE + NN + Y4Y4TILDE + END,
    START + DMY4DOT + NN + DMY4DOT + NN + DMY4DOT + NN + DMY4DOT + END,
    START + YEAR4 + " ~ " + YEAR2 + END,
    START + YEAR4 + NN + YEAR4 + NN + YEAR4 + NN + YEAR4 + END, # Jun 1974 - July 1995
    START + YEAR4 + "-" + YEAR2 + NN + YEAR4 + "-" + YEAR2 + END,

    # Full numeric date
    START + DMY2CDOT + END, # 02.04.1974
    START + DMY2DASH + END, # 02/04/1974
    START + DMY2DOT + END, # 02.04.1974
    START + DMY2SLASH + END, # 02/04/1974
    START + DMY4CDOT + END, # 02·04·74
    START + DMY4DASH + END, # 02/04/74
    START + DMY4DOT + END, # 02.04.74
    START + DMY4SLASH + END, # 02/04/74

    START + DMY4DOT + NN + DMY4DOT + END, # 6.4.1949 - 27.9.2020
    START + DMY2DOT + NN + DMY2DOT + END, # 6.4.49 - 27.9.20
    START + DMY2DOT + NN + DMY4DOT + END, # 6.4.49 - 27.9.2020
    START + DMY2DOT + NN + DMY2DOT + NN + DMY2DOT + NN + DMY2DOT + END, # 6.4.49 - 27.9.20
    START + DMY2DOT + NN + DMY4DOT + NN + DMY2DOT + NN + DMY2DOT + END,

    START + DMY4SLASH + NN + DMY4SLASH + END, # 6/4/1949 - 27/9/2020
    START + DMY2SLASH + NN + DMY2SLASH + END, # 6/4/49 - 27/9/20

    START + DMY4DASH + NN + DMY4DASH + END, # 6-4-1949 - 27-9-2020
    START + DMY2DASH + NN + DMY2DASH + END, # 6-4-49 - 27-9-20
    START + DMY2DASH + NN + DMY4DASH + END, # 6-4-49 - 27-9-2008

    START + DMY4DASH + NN + DMY4DASH + NN + DMY4DASH + NN + DMY4DASH + END, # 6-4-1949 - 27-9-2020 6-4-1949 - 27-9-2020
    START + DMY4SLASH + NN + DMY4SLASH + NN + DMY4SLASH + NN + DMY4SLASH + END, # 6-4-1949 - 27-9-2020 6-4-1949 - 27-9-2020

    START + DMY4DASH + NN + DMY4DASH + NN + DMY4DASH + NN + DMY4DASH + NN + DMY4DASH + NN + DMY4DASH + END, # 6-4-1949 - 27-9-2020 6-4-1949 - 27-9-2020

    START + DMY4SLASH + NN + DMY2SLASH + END,

    # Other
    START + DAY + "th" + NN + YEAR4 + END, # 13th May 1974
    START + DAY + "nd" + NN + YEAR4 + END, # 13nd May 1974
    START + DAY + "rd" + NN + YEAR4 + END, # 13rd May 1974
    START + DAY + NN + YEAR4 + END, # 13 May 1974
    START + DAY + NN + MONTH + NN + YEAR4 + END, # 13 05 1974
    START + DAY2 + "th" + NN + YEAR4 + NN + YEAR4 + END, # 13th May 1974 - 2001
    START + DAY2 + "th" + NN + YEAR4 + NN + DAY2 + "th" + NN + YEAR4 + END, # 13th May 1974 - 13th May 2001
    START + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + END, # 13 May 1974 - 13 May 2001

    # Very specific cases
    START + Y4Y4DASH + NN + AGE2 + END, # 1974-1995 80 years
    START + DAY2 + NN + YEAR4 + NN + AGE2 + END, # 13 Jan 1995 80 years
    START + DAY2 + "th" + NN + YEAR4 + NN + DAY2 + "th" + NN + YEAR4 + NN + AGE3 + END, # 13th May 1974 - 13th May 2001 101 years
    START + Y4Y4DASH + NN + AGE2 + NN + DAY2 + NN + YEAR4 + END, # 1974-1995 80 years 13th Jan 2000
    START + Y4Y4DASH + NN + Y4Y4DASH + NN + Y4Y4DASH + NN + DAY2 + NN + YEAR4 + END, # 1898-1970 1902-1982 1903-1970 24th Dec 1996
    START + "3,500" + NN + Y4Y4DASH + END, # 3,500 banquets 1999-1999
    START + YEAR4 + "/" + YEAR2 + NN + Y4Y4DASH + END, # 1988/89 1923-2000
    START + YEAR4 + " - " + YEAR2 + NN + Y4Y4DASH + END, # 1980-82 1923-2000
    START + YEAR4 + NN + YEAR4 + NN + AGE2 + NN + DAY2 + "th" + NN + YEAR4 + END, # 1980-1980 80 years 1th Jan 1980
    START + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + YEAR4,
    START + DMY4DASH + NN + AGE2 + END,
    START + DMY2DOT + NN + DMY2DOT + NN + DMY2DOT + NN + DMY2DOT + NN + Y4Y4DASH + END,
    START + DAY2 + NN + YEAR4 + NN + Y4Y4DASH + END,
    START + Y4Y4DASH + NN + Y4Y4DASH + NN + AGE2 + END,
    START + Y4Y4DASH + NN + DMY4DASH + NN + DMY4DASH + END,
    START + YEAR4 + NN + YEAR4 + NN + DAY2 + NN + YEAR4 + END,
    START + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + END,
    START + Y4Y4DASH + NN + "1 of 12" + END,
    START + Y4Y4DASH + NN + "Major 20th Arm'd Reg't2NZEF" + NN + YEAR4 + NN + YEAR4 + NN + YEAR4 + NN + YEAR4 + NN + YEAR4 + NN + YEAR4 + END,
    START + "4" + NN + Y4Y4DASH + END,
    START + "Psalm 91v2" + NN + DAY + NN + YEAR4 + END,
    START + AGE2 + NN + Y4Y4DASH + END,
    START + DAY + NN + YEAR4 + NN + AGE1 + END,
    START + DMY2DOT + NN + DMY2DOT + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + END,
    START + AGE2 + NN + DAY + NN + YEAR4 + NN + "[0-9]{5} [0-9]{5}$",
    START + Y4Y4DASH + NN + "[0-9]{5} [0-9]{5}$",
    START + Y4Y4DASH + NN + Y4Y4DASH + NN + "[0-9]{5} [0-9]{5}$",
    START + YEAR4 + "-" + YEAR2 + NN + DAY + NN + YEAR4 + END,
    START + DMY2DASH + NN + AGE2 + NN + DMY2DASH + NN + AGE2 + END,
    START + DMY2DOT + NN + DMY2DOT + NN + AGE2 + END,
    START + AGE2 + NN + DAY2 + NN + YEAR4 + NN + AGE2 + END,
    START + YEAR4 + NN + Y4Y4DASH + END,
    START + YEAR4 + "-" + YEAR2 + NN + DMY2DASH + NN + AGE2 + END,
    START + "[0-9]" + NN + DMY2DOT + NN + DMY2DOT + END,
    START + "[0-9]" + NN + Y4Y4DASH + END,
    START + AGE2 + NN + AGE2 + NN + DAY2 + NN + YEAR4 + END,
    START + DAY + NN + YEAR4 + NN + AGE2 + NN + DAY + NN + YEAR4 + NN + AGE2 + END,
    START + "432" + NN + YEAR4 + END,
    START + "416" + NN + YEAR4 + "-" + YEAR2 + NN + YEAR4 + END,
    START + "109" + NN + YEAR4 + END,
    YEAR4 + NN + "25" + END,
    START + "124-125" + NN + YEAR4 + NN + YEAR4 + END,
    START + YEAR4 + NN + AGE2 + NN + DAY + NN + YEAR4 + END,
    START + DAY + NN + YEAR4 + NN + "[0-9]{2}" + NN + DAY + NN + YEAR4 + END,
    START + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + END,
    START + Y4Y4DASH + NN + DAY + NN + YEAR4 + END,
    START + DMY2SLASH + NN + "_5/0_/(10)" + END,
    START + DMY4DOT + NN + YEAR4 + NN + YEAR4 + END,
    START + "[0-9]{6}" + NN + DMY4DOT + NN + AGE2 + END,
    START + DAY + NN + YEAR4 + NN + "[0-9]{5}" + NN + YEAR4 + END,
    START + Y4Y4DASH + NN + YEAR4 + END,
    START + DAY + NN + YEAR4 + NN + AGE2 + END,
    START + DMY4DOT + NN + DMY4DOT + NN + AGE2 + END,
    START + Y4Y4DASH + NN + YEAR4 + NN + AGE2 + END,
    START + NN + "300" + NN + YEAR4 + NN + DAY + NN + YEAR4 + END,
    START + Y4Y4DASH + NN + "4" + END,
    START + YEAR4 + "\." + MONTH + "\." + DAY + "-" + YEAR4 + "\." + MONTH + "\." + DAY + END,
    START + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + DMY2DASH + NN + DMY2DASH + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + END,
    START + DMY2CDOT + NN + DMY2CDOT + NN + DMY2CDOT + NN + DMY2CDOT + NN + AGE2 + END,
    START + DMY4COLON + NN + DMY4COLON + NN + DMY4COLON + NN + DMY4COLON + END,
    START + DMY2DASH + NN + DMY2DASH + NN + DMY4DOT + NN + DMY4DOT + END,
    START + AGE2 + NN + DMY2DOT + END,
    START + YEAR4 + "/" + YEAR2 + END,
    START + DMY4DOT + NN + DMY4DOT + NN + DMY4DOT + NN + DMY4DOT + NN + DMY4DOT + NN + DMY4DOT + END,
    START + DMY4DOT + NN + DMY4DOT + NN + DMY4DOT + END,
    START + AGE2 + NN + Y4Y4DASH + NN + AGE2 + END,
    START + YEAR4 + NN + AGE2 + END,
    START + DMY2DASH + NN + DMY2DASH + NN + AGE2 + END,
    START + YEAR4 + "-" + YEAR2 + NN + YEAR4 + "-" + YEAR2 + NN + YEAR4 + "-" + YEAR2 + NN + YEAR4 + END,
    START + Y4Y4DASH + NN + "[0-9]{1}" + END,
    START + DMY4SLASH + NN + AGE2 + NN + DMY4SLASH + NN + AGE2 + END,
    START + DMY4SLASH + NN + DMY4SLASH + NN + AGE2 + END,
    START + AGE2 + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + END,
    START + DMY2SLASH + NN + DMY4SLASH + END,
    START + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + AGE2 + END,
    START + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + "1" + NN + DAY + NN + DAY + NN + YEAR4 + END,
    START + YEAR2 + NN + YEAR2 + END,
    START + Y4Y4DASH + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + Y4Y4DASH + NN + Y4Y4DASH + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + Y4Y4DASH + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + END,
    START + Y4Y4DASH + NN + DAY + NN + YEAR4 + NN + AGE2 + END,
    START + YEAR4 + NN + YEAR4 + NN + YEAR4 + END,
    START + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + AGE2 + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + END,
    START + Y4Y4DASH + NN + YEAR4 + NN + AGE2 + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + AGE2 + END,
    START + DMY4DOT + NN + DMY4DOT + NN + "852" + NN + "8904" + NN + "1352" + NN + "293" + NN + "8" + END,
    START + DMY2DOT + NN + DMY2DOT + NN + DAY + NN + YEAR4 + END,
    START + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + NN + DMY4SLASH + NN + DMY4SLASH + NN + DMY2DOT + END,
    START + Y4Y4DASH + NN + DAY + NN + YEAR4 + NN + DAY + NN + YEAR4 + END,
    START + Y4Y4DASH + NN + "51.28377 N  Long: 0.17075" + END,
    START + DMY2DASH + NN + DMY2DASH + NN + DMY2DOT + NN + DMY2DOT + END,
    START + DMY2DASH + NN + AGE2 + END,

    # Not years
    START + "[0-9]{5} [0-9]{3} [0-9]{3}" + END, # 01453 753 358
    START + "[0-9]{1}" + END, # 1
    START + "4'11\" \"oi! Don't forget the 1/2" + END,
    START + "[0-9]{5} [0-9]{5}$",
    START + "23" + NN + "2" + END,
    START + "296 Vauxhall Bridge Road S.W.1." + END,
    START + "526" + END,
    START + "1" + NN + "2" + END,
    START + AGE3 + NN + AGE2 + NN + AGE2 + END,
    START + "100" + END,
]

all_groups = []

def try_find_dates(inscription):
    global all_groups
    count = 0
    for c in inscription:
        if c in nums:
            count += 1
    if count == 0:
        return

    groups = None
    for p in patterns:
        match = re.search(p, inscription)
        if match is not None:
            groups = match.groups()
            break

    if groups is None:
        raise ValueError(inscription)
    else:
        all_groups.append(groups)
        #print(groups)
        pass

with open("benches-new.json", "r") as f:
    js_data = f.read()

data = json.loads(js_data)

total_count = 0
date_count = 0
number_count = 0

bad = False

for f in data['features']:
    inscription = f['properties']['popupContent']
    #total_count += 1
    try:
        try_find_dates(inscription)
        total_count += 1
    except IndexError:
        pass
    except ValueError as err:
        if bad == False:
            #print(err)
            bad = True
        number_count += 1

#print(total_count)
#print(number_count)

l2 = 0
l4 = 0
lo = 0
counts = {}
miny = 3000
maxy = 0
for g in all_groups:
    for year in g:
        if len(year) == 2:
            y = int(year)
            if y >= 21:
                y = int("19" + year)
            else:
                y = int("20" + year)
        elif len(year) == 4:
            y = int(year)

        try:
            counts[y] += 1
        except KeyError:
            counts[y] = 1
        #print(year)
        if y > maxy:
            maxy = y
        if y < miny:
            miny = y

for i in range(miny, maxy+1):
    try:
        print("%d,%d" % (i, counts[i]))
    except KeyError:
        print("%d,0" % (i))

#for k,v in counts.items():
    #print("%d,%d" % (k, v))
