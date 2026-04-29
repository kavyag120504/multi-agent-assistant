import os
import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

DEFAULT_TIMEZONE = os.getenv("USER_TIMEZONE", "Asia/Kolkata")


def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError(
                    "credentials.json not found. Download it from Google Cloud Console "
                    "and place it in the project root."
                )
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)


def _safe_timezone(tz_str: str) -> str:
    """Validate IANA timezone string, fall back to default if invalid."""
    try:
        ZoneInfo(tz_str)
        return tz_str
    except (ZoneInfoNotFoundError, Exception):
        return DEFAULT_TIMEZONE


def handle_calendar(user_message, context: str = ""):
    from tools.llm_client import get_llm
    from langchain_core.messages import HumanMessage, SystemMessage

    # ── Validate credentials files exist ────────────────────────────────────
    if not os.path.exists('credentials.json') and not os.path.exists('token.json'):
        return (
            "❌ Google Calendar is not set up.\n"
            "Please download `credentials.json` from Google Cloud Console "
            "and place it in the project root folder."
        )

    try:
        llm = get_llm()
        context_hint = f"\nConversation so far:\n{context}\n" if context else ""

        # ── Detect action ────────────────────────────────────────────────────
        messages = [
            SystemMessage(content=f"""
            Classify the calendar request into one of:
            - create_event
            - view_events
            - delete_event
            - update_event

            Examples:
            "Schedule a meeting tomorrow at 3pm"     -> create_event
            "Add dentist appointment on Friday"      -> create_event
            "What are my events today?"              -> view_events
            "Show my upcoming meetings"              -> view_events
            "Delete my meeting tomorrow"             -> delete_event
            "Cancel the dentist appointment"         -> delete_event
            "Reschedule my 3pm meeting to 5pm"       -> update_event
            "Change the team sync to Monday"         -> update_event
            {context_hint}
            Respond with just the action word, nothing else.
            """),
            HumanMessage(content=user_message)
        ]
        action = llm.invoke(messages).content.strip().lower()
        if action not in ("create_event", "view_events", "delete_event", "update_event"):
            action = "view_events"

        # ── Extract timezone if user mentions one ────────────────────────────
        tz_messages = [
            SystemMessage(content="""
            If the user mentions a timezone or city that implies a timezone, extract it
            as a valid IANA timezone string (e.g. America/New_York, Europe/London, Asia/Kolkata).
            If no timezone is mentioned, respond with: DEFAULT
            Respond with just the timezone string or DEFAULT, nothing else.
            """),
            HumanMessage(content=user_message)
        ]
        tz_result = llm.invoke(tz_messages).content.strip()
        timezone  = _safe_timezone(tz_result) if tz_result != "DEFAULT" else DEFAULT_TIMEZONE

        service = get_calendar_service()

        if action == "create_event":
            return create_event(service, user_message, llm, timezone)
        elif action == "delete_event":
            return delete_event(service, user_message, llm)
        elif action == "update_event":
            return update_event(service, user_message, llm, timezone)
        else:
            return view_events(service, user_message, llm, timezone)

    except FileNotFoundError as e:
        return f"❌ {str(e)}"
    except Exception as e:
        err = str(e).lower()
        if "invalid_grant" in err or "token" in err:
            return (
                "❌ Google Calendar authentication expired.\n"
                "Please delete `token.json` and restart the app to re-authenticate."
            )
        if "quota" in err or "rate" in err:
            return "⚠️ Google Calendar API quota exceeded. Please try again later."
        return f"⚠️ Calendar error: {str(e)}"


# ── CREATE ────────────────────────────────────────────────────────────────────
def create_event(service, user_message, llm, timezone):
    from langchain_core.messages import HumanMessage, SystemMessage

    today = datetime.datetime.now(ZoneInfo(timezone)).strftime("%Y-%m-%d %H:%M")

    messages = [
        SystemMessage(content=f"""
        Extract event details from the user message.
        Today's date and time is: {today}
        Timezone: {timezone}

        Respond in this exact format, nothing else:
        TITLE: event title
        DATE: YYYY-MM-DD
        TIME: HH:MM
        DURATION: minutes (default 60)
        DESCRIPTION: optional description or leave blank
        LOCATION: optional location or leave blank
        """),
        HumanMessage(content=user_message)
    ]

    response = llm.invoke(messages).content.strip()
    details  = {}
    for line in response.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            details[key.strip()] = value.strip()

    title       = details.get('TITLE', 'New Event')
    date        = details.get('DATE', datetime.datetime.now().strftime('%Y-%m-%d'))
    time_str    = details.get('TIME', '09:00')
    description = details.get('DESCRIPTION', '')
    location    = details.get('LOCATION', '')

    try:
        duration = int(details.get('DURATION', 60))
    except ValueError:
        duration = 60

    try:
        start_dt = datetime.datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        return "❌ I couldn't parse the date/time. Try: *\"Schedule a meeting on 2025-05-10 at 14:00\"*"

    end_dt = start_dt + datetime.timedelta(minutes=duration)

    event_body = {
        'summary': title,
        'start':   {'dateTime': start_dt.isoformat(), 'timeZone': timezone},
        'end':     {'dateTime': end_dt.isoformat(),   'timeZone': timezone},
    }
    if description:
        event_body['description'] = description
    if location:
        event_body['location'] = location

    created    = service.events().insert(calendarId='primary', body=event_body).execute()
    event_link = created.get('htmlLink', '')

    return (
        f"✅ **Event created!**\n"
        f"📅 **{title}**\n"
        f"🕐 {start_dt.strftime('%B %d, %Y at %I:%M %p')} ({timezone})\n"
        f"⏱️ Duration: {duration} minutes"
        + (f"\n📍 Location: {location}" if location else "")
        + (f"\n📝 {description}" if description else "")
        + (f"\n🔗 [Open in Google Calendar]({event_link})" if event_link else "")
    )


# ── VIEW ──────────────────────────────────────────────────────────────────────
def view_events(service, user_message="", llm=None, timezone=DEFAULT_TIMEZONE):
    from langchain_core.messages import HumanMessage, SystemMessage

    scope = "upcoming"
    if llm and user_message:
        scope_messages = [
            SystemMessage(content="""
            Does the user want to see:
            - today    (events only for today)
            - upcoming (next several events)
            - week     (events this week)
            Respond with just: today, upcoming, or week
            """),
            HumanMessage(content=user_message)
        ]
        scope = llm.invoke(scope_messages).content.strip().lower()
        if scope not in ("today", "upcoming", "week"):
            scope = "upcoming"

    now = datetime.datetime.now(ZoneInfo(timezone))

    if scope == "today":
        time_min    = now.replace(hour=0, minute=0, second=0).isoformat()
        time_max    = now.replace(hour=23, minute=59, second=59).isoformat()
        max_results = 20
        label       = "Today's Events"
    elif scope == "week":
        time_min    = now.isoformat()
        time_max    = (now + datetime.timedelta(days=7)).isoformat()
        max_results = 20
        label       = "This Week's Events"
    else:
        time_min    = now.isoformat()
        time_max    = None
        max_results = 7
        label       = "Upcoming Events"

    params = {
        "calendarId":   "primary",
        "timeMin":      time_min,
        "maxResults":   max_results,
        "singleEvents": True,
        "orderBy":      "startTime",
    }
    if time_max:
        params["timeMax"] = time_max

    events_result = service.events().list(**params).execute()
    events        = events_result.get('items', [])

    if not events:
        return f"📅 No events found for **{label.lower()}**."

    output = f"📅 **{label}:**\n\n"
    for event in events:
        start       = event['start'].get('dateTime', event['start'].get('date'))
        title       = event.get('summary', 'No title')
        location    = event.get('location', '')
        description = event.get('description', '')

        try:
            dt        = datetime.datetime.fromisoformat(start)
            formatted = dt.strftime('%b %d, %Y  %I:%M %p')
        except Exception:
            formatted = start

        output += f"📌 **{title}**\n   🕐 {formatted}"
        if location:
            output += f"\n   📍 {location}"
        if description:
            output += f"\n   📝 {description[:80]}{'...' if len(description) > 80 else ''}"
        output += "\n\n"

    return output


# ── DELETE ────────────────────────────────────────────────────────────────────
def delete_event(service, user_message, llm):
    from langchain_core.messages import HumanMessage, SystemMessage

    now           = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary', timeMin=now,
        maxResults=10, singleEvents=True, orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    if not events:
        return "📅 You have no upcoming events to delete."

    event_list = ""
    for i, event in enumerate(events):
        title = event.get('summary', 'No title')
        start = event['start'].get('dateTime', event['start'].get('date'))
        try:
            dt        = datetime.datetime.fromisoformat(start.replace('Z', ''))
            formatted = dt.strftime('%b %d at %I:%M %p')
        except Exception:
            formatted = start
        event_list += f"{i}: {title} on {formatted}\n"

    messages = [
        SystemMessage(content=f"""
        The user wants to delete a calendar event.
        Upcoming events (with index numbers):
        {event_list}

        Based on the user message, respond with ONLY the index number.
        If no match, respond with: -1
        """),
        HumanMessage(content=user_message)
    ]
    response = llm.invoke(messages).content.strip()

    try:
        index = int(response)
    except Exception:
        index = -1

    if index == -1 or index >= len(events):
        return "❌ Couldn't match that event. Try using the event name more clearly."

    event_to_delete = events[index]
    service.events().delete(calendarId='primary', eventId=event_to_delete['id']).execute()
    return f"🗑️ Deleted: **{event_to_delete.get('summary', 'Event')}**"


# ── UPDATE ────────────────────────────────────────────────────────────────────
def update_event(service, user_message, llm, timezone):
    from langchain_core.messages import HumanMessage, SystemMessage

    now           = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary', timeMin=now,
        maxResults=10, singleEvents=True, orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    if not events:
        return "📅 You have no upcoming events to update."

    event_list = ""
    for i, event in enumerate(events):
        title = event.get('summary', 'No title')
        start = event['start'].get('dateTime', event['start'].get('date'))
        try:
            dt        = datetime.datetime.fromisoformat(start.replace('Z', ''))
            formatted = dt.strftime('%b %d at %I:%M %p')
        except Exception:
            formatted = start
        event_list += f"{i}: {title} on {formatted}\n"

    find_messages = [
        SystemMessage(content=f"""
        The user wants to update a calendar event.
        Upcoming events:
        {event_list}

        Respond with ONLY the index number of the event to update.
        If no match, respond with: -1
        """),
        HumanMessage(content=user_message)
    ]
    index_resp = llm.invoke(find_messages).content.strip()
    try:
        index = int(index_resp)
    except Exception:
        index = -1

    if index == -1 or index >= len(events):
        return "❌ Couldn't find that event. Try using the event name more clearly."

    event = events[index]
    today = datetime.datetime.now(ZoneInfo(timezone)).strftime("%Y-%m-%d %H:%M")

    update_messages = [
        SystemMessage(content=f"""
        The user wants to update this event: {event.get('summary')}
        Today is: {today}

        Extract the new values from the user message.
        Respond in this format (only include fields that are changing):
        TITLE: new title (or leave blank if not changing)
        DATE: YYYY-MM-DD (or leave blank if not changing)
        TIME: HH:MM (or leave blank if not changing)
        DURATION: minutes (or leave blank if not changing)
        """),
        HumanMessage(content=user_message)
    ]
    update_resp = llm.invoke(update_messages).content.strip()
    new_details = {}
    for line in update_resp.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            val = value.strip()
            if val:
                new_details[key.strip()] = val

    if 'TITLE' in new_details:
        event['summary'] = new_details['TITLE']

    if 'DATE' in new_details or 'TIME' in new_details:
        current_start = event['start'].get('dateTime', '')
        try:
            current_dt = datetime.datetime.fromisoformat(current_start)
        except Exception:
            current_dt = datetime.datetime.now()

        new_date  = new_details.get('DATE', current_dt.strftime('%Y-%m-%d'))
        new_time  = new_details.get('TIME', current_dt.strftime('%H:%M'))

        try:
            new_start = datetime.datetime.strptime(f"{new_date} {new_time}", "%Y-%m-%d %H:%M")
        except ValueError:
            return "❌ I couldn't parse the new date/time. Try: *\"Reschedule to 2025-05-10 at 15:00\"*"

        current_end = event['end'].get('dateTime', '')
        try:
            current_end_dt = datetime.datetime.fromisoformat(current_end)
            duration       = int((current_end_dt - current_dt).total_seconds() / 60)
        except Exception:
            duration = 60

        if 'DURATION' in new_details:
            try:
                duration = int(new_details['DURATION'])
            except ValueError:
                duration = 60

        new_end        = new_start + datetime.timedelta(minutes=duration)
        event['start'] = {'dateTime': new_start.isoformat(), 'timeZone': timezone}
        event['end']   = {'dateTime': new_end.isoformat(),   'timeZone': timezone}

    updated = service.events().update(
        calendarId='primary', eventId=event['id'], body=event
    ).execute()

    title = updated.get('summary', 'Event')
    start = updated['start'].get('dateTime', '')
    try:
        dt        = datetime.datetime.fromisoformat(start)
        formatted = dt.strftime('%B %d, %Y at %I:%M %p')
    except Exception:
        formatted = start

    return f"✅ **Event updated!**\n📅 **{title}**\n🕐 {formatted} ({timezone})"
