import csv
from datetime import date, timedelta
from collections import OrderedDict

from jinja2 import FileSystemLoader, Environment

# 🙌 🐍 🙌

# the calendar year you'd like to display
YEAR = 2019

# the name of CSV file with dates to highlight
# assumes the date is in the first column in YYYY-MM-DD format
# and the event is in the second column
DATA_FILE = 'data.csv'

# name of your template
TEMPLATE = 'template.html'

# name of the output HTML file
OUTFILE = 'calendar.html'

# for each month table, we'll need a grid of 7 days/week and 6 rows
GRID = 7 * 6

# open the CSV file
with open(DATA_FILE) as df:

    # read it into a csv.reader object
    reader = csv.reader(df)

    # skip the headers
    next(reader)

    # drop it into a dictionary
    # keys are YYYY-MM-DD date in column 1 [0]
    # values (description of the event) are in column 2 [1]
    event_data = {x[0]: x[1] for x in reader}

# create a new ordered dictionary to hold a year's worth of data --
# keys will be month names, e.g. 'Jan', while values will be a list
# that includes both days of the month and empty strings for blank
# spots at the start/end of a calendar month (e.g., previous and next months)
year_data = OrderedDict()

# define start and end days -- a calendar year
start = date(YEAR, 1, 1)
end = date(YEAR, 12, 31)

# get the difference b/t the two
diff = end - start

# loop over the range of days
for x in range(diff.days + 1):

    # the current day we're working on here
    d = start + timedelta(days=x)

    # get the month name as three-letter string, e.g. Jan
    month = d.strftime('%b')

    # if the month key doesn't exist already, add it -- the
    # value, again, will be a list of days + blanks
    if not year_data.get(month):
        year_data[month] = []

    # get the YYYY-MM-DD version of the date
    formatted_date = d.isoformat()

    # create a new dictionary for this day
    # default is just the date, nothing else
    record = {'date': d}

    # however! if we try to look up this date in our dictionary of events
    # and find something, add a new entry to that dictionary with
    # details of the event
    event = event_data.get(formatted_date)

    if event:
        record['event'] = event

    # now whang it into the list for this month
    year_data[month].append(record)

# next, add the blanks before and after the start of the actual
# days for this month to fill out the 7*6 calendar grid

# loop over the ordered dict
for month in year_data:

    # grab the day of the week for the first day of the month
    # 0 = Monday, 1 = Tuesday, etc.
    firstwday = year_data[month][0]['date'].weekday()

    # each month calendar will start with Sunday (6)
    # so if this is a Sunday, we don't need to prepend anything
    # if it's not, drop some empty strings in there
    if firstwday < 6:

        # get a list of empty strings, however many is called for
        # e.g. Monday is 0, so we want to prepend 0+1 blank strings
        prepend = ['' for x in range(firstwday + 1)]

        # and prepend those to the list for this month
        year_data[month][:0] = prepend

    # now, check to see how many blanks to append to the end of the month
    # it'll be 42 minus however many items we have in our list now
    blanks_to_append = GRID - len(year_data[month])

    # if we have blanks to append
    if blanks_to_append:

        # make a list of em
        end_blanks = ['' for x in range(blanks_to_append)]

        # and drop em onto the end of the list
        year_data[month].extend(end_blanks)

    # confirm that each list for each month matches the
    # number of entries on a 7 * 6 grid
    assert(len(year_data[month]) == GRID)

# create a Jinja loader that looks in the current directory
loader = FileSystemLoader(searchpath='./')

# set up the Jinja environment using this loader
env = Environment(loader=loader)

# we hate extra white space and want to kill it dead
env.trim_blocks = True
env.lstrip_blocks = True
env.rstrip_blocks = True

# load up the template
template = env.get_template(TEMPLATE)

# and render it with the data we've spent so much time massaging
output = template.render(data=year_data, year=YEAR)

# finally, write out the rendered template to file
with open(OUTFILE, 'w') as outfile:
    outfile.write(output)

print(f'Wrote to {OUTFILE}')
