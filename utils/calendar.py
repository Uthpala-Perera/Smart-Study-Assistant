def export_calendar(subject, exam_date):
    content = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:Study {subject}
DTSTART:{exam_date.strftime('%Y%m%d')}
END:VEVENT
END:VCALENDAR
"""
    with open("study_schedule.ics", "w") as f:
        f.write(content)