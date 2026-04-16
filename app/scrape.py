import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By

def scrape(stu_id:str, password:str) -> list:

    # chrome driverの設定（ChromeDriver互換性修正を保持）
    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(options=options, service=service)
        print("ChromeDriver接続成功")
    except Exception:
        try:
            service = ChromeService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
            driver = webdriver.Chrome(options=options, service=service)
            print("Chromium ChromeDriver接続成功")
        except Exception:
            try:
                driver = webdriver.Chrome(options=options)
                print("システムChromeDriver接続成功")
            except Exception:
                raise Exception("ChromeDriverの初期化に失敗しました。")

    # urlを指定
    url="https://muscat.musashino-u.ac.jp/portal/top.do"
    driver.get(url)

    # 学籍番号を入力
    login_id = "s" + stu_id
    driver.find_element(By.XPATH,"//*[@id='userId']").send_keys(login_id)

    # パスワードを入力
    driver.find_element(By.XPATH,"//*[@id='password']").send_keys(password)

    # ログインボタンをクリック
    btn = driver.find_element(By.XPATH,"//*[@id='loginButton']")
    btn.click()

    time.sleep(2)  # ログイン待機

    # My時間割ページに直接アクセス（動いていた方法）
    print("My時間割ページにアクセス中...")
    timetable_url = "https://muscat.musashino-u.ac.jp/portal/prtlmjkr.do?clearAccessData=true&contenam=prtlmjkr&kjnmnNo=15"
    driver.get(timetable_url)
    
    time.sleep(3)
    
    # ページタイトルを確認
    try:
        title = driver.find_element(By.TAG_NAME, "h2").text
        print(f"時間割ページタイトル: {title}")
    except:
        print("ページタイトル取得失敗")
    
    # 時間割データを抽出
    print("時間割データを抽出中...")
    jikanwari = []
    
    # 各学期のデータを取得（1-4学期）
    semester_urls = [
        "?buttonName=switchJikanwariKikan&kikankn=1",  # 1学期
        "?buttonName=switchJikanwariKikan&kikankn=2",  # 2学期  
        "?buttonName=switchJikanwariKikan&kikankn=3",  # 3学期
        "?buttonName=switchJikanwariKikan&kikankn=4"   # 4学期
    ]
    
    for semester_idx, url_param in enumerate(semester_urls):
        print(f"学期 {semester_idx + 1} の時間割を処理中...")
        
        # 学期切り替え（全学期で実行）
        try:
            semester_url = f"https://muscat.musashino-u.ac.jp/portal/prtlmjkr.do{url_param}"
            print(f"学期 {semester_idx + 1} URL: {semester_url}")
            driver.get(semester_url)
            time.sleep(3)
            print(f"学期 {semester_idx + 1} のページに移動完了")
            
            # 現在のページタイトルを確認して学期切り替えが成功したかチェック
            try:
                page_title = driver.find_element(By.TAG_NAME, "title").get_attribute("textContent")
                print(f"学期 {semester_idx + 1} ページタイトル: {page_title}")
            except:
                print(f"学期 {semester_idx + 1} ページタイトル取得失敗")
                
        except Exception as e:
            print(f"学期 {semester_idx + 1} への移動エラー: {e}")
                
        # 現在の構造に基づいた時間割データ取得
        semester_data = []
        try:
            # 正確な時間割テーブル構造に基づいたアプローチ
            all_cells = driver.find_elements(By.XPATH, "//table[contains(@class, 'jikanwari_table')]//tr[contains(@class, 'rule_')]//td[@class='item']//table[@class='jikanwariKoma']//td[@class='item']")
            print(f"学期 {semester_idx + 1}: {len(all_cells)} 個のセルを発見")
            
            # より詳細なデバッグ情報
            if semester_idx == 0:
                time_table_exists = driver.find_elements(By.XPATH, "//table[contains(@class, 'jikanwari_table')]")
                rule_rows = driver.find_elements(By.XPATH, "//table[contains(@class, 'jikanwari_table')]//tr[contains(@class, 'rule_')]")
                item_cells = driver.find_elements(By.XPATH, "//table[contains(@class, 'jikanwari_table')]//tr[contains(@class, 'rule_')]//td[@class='item']")
                print(f"デバッグ情報 - 時間割テーブル: {len(time_table_exists)}個, rule行: {len(rule_rows)}個, itemセル: {len(item_cells)}個")
            
            if len(all_cells) >= 42:  # 7限 x 6曜日 = 42セル以上期待
                # 1限から7限まで処理
                for period in range(7):  # 7限まで対応
                    period_row = []
                    # 月曜日から土曜日まで
                    for day in range(6):
                        cell_idx = period * 6 + day
                        if cell_idx < len(all_cells):
                            cell = all_cells[cell_idx]
                            cell_html = cell.get_attribute("innerHTML")
                            cell_text = cell.text.strip()
                            
                            # 空のセルをチェック
                            if ("時間割情報が存在しない" in cell_html or 
                                "<br><br><br>" in cell_html or 
                                not cell_text):
                                period_row.append("")
                            else:
                                period_row.append(cell_text)
                                
                            if semester_idx == 0 and period < 2:  # デバッグ出力
                                print(f"セル[{period+1}限,{day+1}曜日]: {'データあり' if cell_text else '空'}")
                        else:
                            period_row.append("")
                    
                    semester_data.append(period_row)
                
                # 曜日ごとに再編成（working versionと互換性のため）
                reorganized_data = []
                for day in range(6):  # 月〜土
                    day_schedule = []
                    for period in range(7):  # 1-7限
                        if period < len(semester_data) and day < len(semester_data[period]):
                            day_schedule.append(semester_data[period][day])
                        else:
                            day_schedule.append("")
                    reorganized_data.append(day_schedule)
                
                # 日曜日も追加（通常は空）
                reorganized_data.append([""] * 7)  # 7限分
                
                jikanwari.append(reorganized_data)
                course_count = len([item for sublist in reorganized_data for item in sublist if item])
                print(f"学期 {semester_idx + 1} 完了 - {course_count} 個の授業データを取得")
                
            else:
                print(f"学期 {semester_idx + 1}: セル数が不足 ({len(all_cells)}個)")
                # 空のデータで埋める（7限対応）
                empty_semester = [[""] * 7 for _ in range(7)]  # 7曜日 x 7限
                jikanwari.append(empty_semester)
                
        except Exception as e:
            print(f"学期 {semester_idx + 1} でエラー発生: {str(e)}")
            # 空のデータで埋める（7限対応）
            empty_semester = [[""] * 7 for _ in range(7)]  # 7曜日 x 7限
            jikanwari.append(empty_semester)

    # chromeを終了
    driver.close()

    print(f"取得完了。{len(jikanwari)}学期分のデータを取得しました。")
    return jikanwari