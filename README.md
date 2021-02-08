# TORGAX (calendar deduplicator)

TORGAX is a service that does two things:

- Deduplicate only OASIS events
- Deduplicate OASIS and Ufora events, with a possiblitiy to ignore some events

## Before

![Before image of calendar with duplicate courses](before.jpg)

## After

![After image of calendar without duplicate courses](after.jpg)

## How to use it?


### To only deduplicate OASIS events

Go to https://centauro.ugent.be/kalender/mijnKalender, click "Export", copy
the iCalendar URL. It should look something like `https://centauro.ugent.be/calendar/ical/764efa883dda1e11db47671c4a3bbd9e`.
Paste the token (here `764efa883dda1e11db47671c4a3bbd9e`) after `https://torgax.zeus.gent/oasis/`,
then add a slash and then some text, so it becomes a URL like
`https://torgax.zeus.gent/oasis/764efa883dda1e11db47671c4a3bbd9e/torgaxisamazing`.


### To deduplicate OASIS and Ufora events

Go to https://centauro.ugent.be/kalender/mijnKalender, click "Export", copy
the iCalendar URL. It should look something like `https://centauro.ugent.be/calendar/ical/764efa883dda1e11db47671c4a3bbd9e`.
Go to https://ufora.ugent.be, click "Calendar", click "Subscribe", copy the iCalendar URL.
It should look something like `https://ufora.ugent.be/d2l/le/calendar/feed/user/feed.ics?token=61615qsdf31qsdf665sqdf`.

Separate the words you want to ignore by comma's.

URL-encode both URLs and the ignorelist and pass them as query parameter to

`https://torgax.zeus.gent/combine?oasis=ENCODED_OASIS_URL_HERE&ufora=ENCODED_UFORA_URL_HERE&ignore=IGNORELIST_HERE`
