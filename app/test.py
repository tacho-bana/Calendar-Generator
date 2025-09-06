from ics import Calendar

# .icsファイルを読み込む
with open("myCalendar.ics", "r", encoding="utf-8") as f:
    ics_data = f.read()

calendar = Calendar(ics_data)

# カレンダー内のイベントを確認
for event in calendar.events:
    print("========")
    print("UID:", event.uid)
    print("SUMMARY:", event.name)
    print("START:", event.begin)
    print("END:", event.end)
    print("DESCRIPTION:", event.description)