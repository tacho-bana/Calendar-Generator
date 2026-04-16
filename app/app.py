import streamlit as st
import pandas as pd
from scrape import scrape
from generate_calendar import generateCalendar


def main():

    st.title('Calendar Generator')
    st.text('MUSCATのmy時間割から自動でカレンダーを作成します。')

    with st.form("my_form", clear_on_submit=False):

        stu_id = st.number_input(
            '学籍番号(先頭にsは不要です)', 1500000, 3000000, 2000000, step=1)
        password = st.text_input('MUSCATのパスワード', type="password")
        submitted = st.form_submit_button("カレンダーを作成")

    # ボタンを押した時の処理
    if submitted:
        with st.spinner('カレンダー取得中'):

            # 時間割の取得
            try:
                jikanwari = scrape(str(stu_id), password)
            except ValueError as e:
                st.error(str(e))
                st.stop()
            
            # 取得した時間割データを表示
            st.subheader("📅 取得した時間割データ")
            semester_names = ["前期前半", "前期後半", "後期前半", "後期後半"]
            day_names = ["月", "火", "水", "木", "金", "土", "日"]
            
            for i, semester_data in enumerate(jikanwari):
                st.write(f"**{semester_names[i]}**")
                
                # 時間割を表形式で表示
                if semester_data and len(semester_data) == 7:
                    # データフレーム用の辞書を作成（7限対応）
                    schedule_dict = {"時限": ["1限", "2限", "3限", "4限", "5限", "6限", "7限"]}
                    
                    for day_idx, day_name in enumerate(day_names):
                        if day_idx < len(semester_data):
                            schedule_dict[day_name] = semester_data[day_idx]
                        else:
                            schedule_dict[day_name] = [""] * 7
                    
                    df = pd.DataFrame(schedule_dict)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.write("データが正しく取得できませんでした")
                
                st.write("---")

            # カレンダー作成
            calendar = generateCalendar(jikanwari)
            
            # カレンダーの中身を表示
            st.subheader("📄 生成されたカレンダー内容")
            
            # イベント数をカウント
            event_count = calendar.count('BEGIN:VEVENT')
            st.write(f"**生成されたイベント数:** {event_count}件")
            st.write(f"**ファイルサイズ:** {len(calendar)} 文字")
            
            # .icsファイルの全内容を表示
            st.write("**📋 .icsファイルの全内容:**")
            with st.expander("ファイル内容を表示/非表示", expanded=True):
                st.text_area(
                    "生成された.icsファイルの内容",
                    calendar,
                    height=400,
                    help="このテキストが実際のカレンダーファイルの内容です"
                )

            # ファイルダウンロード
            st.download_button(
                label="カレンダーをダウンロード",
                data=calendar,
                file_name="myCalendar.ics",
                mime="text/calendar"
            )


if __name__ == '__main__':
    main()
