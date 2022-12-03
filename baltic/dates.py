#!/usr/bin/env python
# filename: dates.py
#
# Inspiration: https://github.com/evogytis/baltic
# License: GNU General Public License v3.0 (https://opensource.org/licenses/GPL-3.0)
#


from datetime import datetime
import re


def decimal_date(date: str, fmt: str = "%Y-%m-%d", variable: bool = False):
    """ Converts calendar dates in specified format to decimal date. """
    if fmt == "":
        return date
    delimiter = re.search(
        "[^0-9A-Za-z%]", fmt
    )  ## search for non-alphanumeric symbols in fmt (should be field delimiter)
    delimit = None
    if delimiter is not None:
        delimit = delimiter.group()

    if variable == True:  ## if date is variable - extract what is available
        if delimit is not None:
            dateL = len(date.split(delimit))  ## split date based on symbol
        else:
            dateL = 1  ## no non-alphanumeric characters in date, assume dealing with an imprecise date (something like just year)

        if dateL == 2:
            fmt = delimit.join(
                fmt.split(delimit)[:-1]
            )  ## reduce fmt down to what's available
        elif dateL == 1:
            fmt = delimit.join(fmt.split(delimit)[:-2])

    adatetime = datetime.strptime(date, fmt)  ## convert to datetime object
    year = adatetime.year  ## get year
    boy = datetime(year, 1, 1)  ## get beginning of the year
    eoy = datetime(year + 1, 1, 1)  ## get beginning of next year
    return year + (
        (adatetime - boy).total_seconds() / ((eoy - boy).total_seconds())
    )  ## return fractional year


def calendar_date(timepoint: int, fmt="%Y-%m-%d"):
    """ Converts decimal dates to a specified calendar date format. """
    year = int(timepoint)
    rem = timepoint - year

    base = datetime(year, 1, 1)
    result = base + dt.timedelta(
        seconds=(base.replace(year=base.year + 1) - base).total_seconds() * rem
    )

    return datetime.strftime(result, fmt)


def convert_date(x: str, start: str, end: str):
    """ Converts calendar dates between given formats """
    return datetime.strftime(datetime.strptime(x, start), end)

