import icalendar
import requests
from flask import Flask, request
import itertools
import re


# This is awful code, don't judge me

application = Flask(__name__)

def get_course(description):
    return description.split('\n')[1]

def merge_descriptions(first_description, second_description):
    merged = []
    first_description_lines = first_description.split('\n')
    second_description_lines = second_description.split('\n')
    for line_idx, (f_line, s_line) in enumerate(zip(first_description_lines, second_description_lines)):
        if f_line == s_line:
            merged.append(f_line)
        elif f_line[:5] == s_line[:5]:
            f_words = f_line.split(' ')
            s_words = s_line.split(' ')
            merged_line = []
            for idx, (first_word, second_word) in enumerate(zip(f_words, s_words)):
                if first_word == second_word:
                    merged_line.append(first_word)
                else:
                    break
            merged_line += f_words[idx:]
            merged_line.append(' / ')
            merged_line += s_words[idx:]
            merged.append(' '.join(merged_line))
        else:
            merged.append(f_line + ' ' + s_line)
    merged += first_description_lines[line_idx:]
    merged += second_description_lines[line_idx:]
    return '\n'.join(merged).strip()

def compress_calendar(c):
    new_calendar = icalendar.Calendar()
    # mapping from (dtstart, dtend, course) to event
    events = {}

    for event in c.subcomponents:
        # Check if actually an event and not a timezone
        if event.name != 'VEVENT':
            new_calendar.add_component(event)
        else:
            starttime = event.get('dtstart').dt
            endtime = event.get('dtend').dt
            description = str(event.get('description'))
            course = get_course(description)
            triple = (starttime, endtime, course)

            if triple in events:
                merged_description = merge_descriptions(description, str(events[triple].get('description')))
                events[triple]['description'] = icalendar.prop.vText(merged_description)
            else:
                events[triple] = event
                new_calendar.add_component(event)
    return new_calendar

@application.route("/oasis/<uid>", strict_slashes=False)
def convert(uid, ignored=None):
    if uid.isalnum():
        try:
            r = requests.get(f"https://centauro.ugent.be/calendar/ical/{uid}")
            if r.status_code != 200:
                raise ValueError("Request failed")
            c = icalendar.Calendar.from_ical(r.text)
            compressed = compress_calendar(c)
            return compressed.to_ical()
        except ValueError:
            return 'Calendar does not exist\n'
    else:
        return 'Nein\n'

def extract_coursecode(event):
    m = re.search(r'[A-Z][0-9]{6}', event.get('location'))
    if not m:
        m = re.search(r'[A-Z][0-9]{6}', event.get('summary'))
    if m:
        return m.group(0)
    return None

def combiner_inner(ufora, oasis, ignorelist):
    result_calendar = icalendar.Calendar()
    if ufora is None or oasis is None:
        return result_calendar
    ufora_cal = icalendar.Calendar.from_ical(requests.get(ufora).text)
    oasis_cal = icalendar.Calendar.from_ical(requests.get(oasis).text)
    oasis_cal = compress_calendar(oasis_cal)

    timezone_seen = False

    all_events = {}
    for event, calendarname in itertools.chain(zip(ufora_cal.subcomponents, itertools.repeat('Ufora')), zip(oasis_cal.subcomponents, itertools.repeat('Oasis'))):
        if event.name == 'VTIMEZONE' and not timezone_seen:
            result_calendar.add_component(event)
            timezone_seen = True
        elif event.name == 'VEVENT':
            if any((ignore in event.get('location') for ignore in ignorelist)):
                continue
            coursecode = extract_coursecode(event)
            if not coursecode:
                event['description'] = icalendar.prop.vText(event.get('description', '') + f'\n{calendarname}')
                result_calendar.add_component(event)
            else:
                starttime = event.get('dtstart').dt
                endtime = event.get('dtend').dt
                triple = (starttime, endtime, coursecode)
                if triple in all_events:
                    merged_description = merge_descriptions(event.get('description', ''), str(all_events[triple].get('description', '')))
                    all_events[triple]['description'] = icalendar.prop.vText(merged_description)
                    all_events[triple]['location'] = event.get('location') + str(all_events[triple].get('location'))
                else:
                    all_events[triple] = event
    for event in all_events.values():
        result_calendar.add_component(event)
    return result_calendar


@application.route("/combiner")
def combiner():
    ufora = request.args.get('ufora')
    oasis = request.args.get('oasis')
    ignore = [i for i in request.args.get('ignore', '').split(',') if i]
    return combiner_inner(ufora, oasis, ignore).to_ical()

if __name__ == "__main__":
    application.run(debug=True)
