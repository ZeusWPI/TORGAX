import icalendar
import requests
from flask import Flask

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

def compress_calendar(uid):
    r = requests.get(f"https://centauro.ugent.be/calendar/ical/{uid}")
    if r.status_code != 200:
        raise ValueError("Request failed")
    c = icalendar.Calendar.from_ical(r.text)
    merged_calendar = icalendar.Calendar()

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

@application.route("/<uid>", strict_slashes=False)
@application.route("/<uid>/<ignored>", strict_slashes=False)
def convert(uid, ignored=None):
    if uid.isalnum():
        try:
            compressed = compress_calendar(uid)
            return compressed.to_ical()
        except ValueError:
            return 'Calendar does not exist\n'
    else:
        return 'Nein\n'

if __name__ == "__main__":
    application.run(debug=True)
