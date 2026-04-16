import datetime
import uuid

def generateCalendar(jikanwari:list) -> str:

    # 学期 (2026年度 令和8年度)
    semester = {
        0: [datetime.date(2026,4,16), datetime.date(2026,6,10)],   # 1学期
        1: [datetime.date(2026,6,13), datetime.date(2026,7,31)],   # 2学期
        2: [datetime.date(2026,9,24), datetime.date(2026,11,17)],  # 3学期
        3: [datetime.date(2026,11,24), datetime.date(2027,1,26)],  # 4学期
    }

    # 休日 (2026年度 令和8年度)
    # ※昭和の日(4/29)・海の日(7/20)は授業実施日のため除外
    holiday = [
        # 5月 GW + 学校行事（1学期）
        datetime.date(2026,5,1),   # 振替休講日（昭和の日4/29の代替）
        datetime.date(2026,5,2),   # 振替休講日（海の日7/20の代替）
        datetime.date(2026,5,4),   # みどりの日
        datetime.date(2026,5,5),   # こどもの日
        datetime.date(2026,5,6),   # 振替休日（憲法記念日の振替）
        datetime.date(2026,5,21),  # 同慶節
        # 10月（3学期）
        datetime.date(2026,10,10), # 摩耶祭
        datetime.date(2026,10,12), # スポーツの日
        # 11月（3学期）
        datetime.date(2026,11,3),  # 文化の日
        # 12月〜1月 冬期一斉休業（4学期）
        datetime.date(2026,12,29),
        datetime.date(2026,12,30),
        datetime.date(2026,12,31),
        datetime.date(2027,1,1),   # 元日
        datetime.date(2027,1,2),
        datetime.date(2027,1,3),
        datetime.date(2027,1,4),
        datetime.date(2027,1,5),
        datetime.date(2027,1,11),  # 成人の日
    ]

    # 時間（JST = UTC+9）
    class_time = {
        0: [( 8, 50), (10, 30)],
        1: [(10, 40), (12, 20)],
        2: [(13, 10), (14, 50)],
        3: [(15,  0), (16, 40)],
        4: [(16, 50), (18, 30)],
        5: [(18, 40), (20, 20)],
        6: [(20, 20), (22,  0)],
    }

    JST = datetime.timezone(datetime.timedelta(hours=9))

    def fmt(dt: datetime.datetime) -> str:
        return dt.strftime('%Y%m%dT%H%M%S')

    events = []

    for sem_idx in range(4):
        start = semester[sem_idx][0]
        stop  = semester[sem_idx][1]
        jikanwari_ = jikanwari[sem_idx]

        while start <= stop:
            weekday = start.weekday()

            # jikanwari_[曜日][時限] の構造
            if weekday != 6 and start not in holiday and weekday < len(jikanwari_):
                day_schedule = jikanwari_[weekday]  # その曜日の全時限

                for period, course in enumerate(day_schedule):
                    if course == '':
                        continue

                    h_start, m_start = class_time[period][0]
                    h_end,   m_end   = class_time[period][1]

                    dt_start = datetime.datetime(start.year, start.month, start.day,
                                                 h_start, m_start, tzinfo=JST)
                    dt_end   = datetime.datetime(start.year, start.month, start.day,
                                                 h_end,   m_end,   tzinfo=JST)

                    summary = course.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
                    events.append(
                        "BEGIN:VEVENT\r\n"
                        f"UID:{uuid.uuid4()}@mu-calendar\r\n"
                        f"DTSTART;TZID=Asia/Tokyo:{fmt(dt_start)}\r\n"
                        f"DTEND;TZID=Asia/Tokyo:{fmt(dt_end)}\r\n"
                        f"SUMMARY:{summary}\r\n"
                        "END:VEVENT\r\n"
                    )

            start += datetime.timedelta(days=1)

    cal_lines = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//MU-Calendar-Generator//JP\r\n"
        "CALSCALE:GREGORIAN\r\n"
        "X-WR-TIMEZONE:Asia/Tokyo\r\n"
        + "".join(events)
        + "END:VCALENDAR\r\n"
    )

    return cal_lines
