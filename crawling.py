import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def create_data_folder():
    """root 폴더에 data 폴더가 없으면 생성하는 함수"""
    folder_path = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"📁 폴더 생성 완료: {folder_path}")
    return folder_path


def crawl_google_news():
    data_dir = create_data_folder()
    txt_file_path = os.path.join(data_dir, 'news_title.txt')
    excel_file_path = os.path.join(data_dir, 'news_title.xlsx')

    # 구글 뉴스 검색 URL (검색어: 한국 월드컵, 24시간 이내, 최신순 정렬)
    search_url = "https://www.google.com/search?q=%ED%95%9C%EA%B5%AD+%EC%9B%94%EB%93%9C%EC%BB%B5&tbm=nws&tbs=qdr:d,sbd:1"

    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # 브라우저 창이 뜨는 것을 확인하기 위해 기본 상태로 실행
    driver = webdriver.Chrome(options=options)
    driver.get(search_url)

    news_headlines = []
    max_headlines = 200
    page_count = 1

    print("🚀 크롤링을 시작합니다. (목표 수량: 최대 200개)")

    try:
        while len(news_headlines) < max_headlines:
            print(f"📄 현재 {page_count}페이지 수집 중... (현재 수집된 헤드라인 수: {len(news_headlines)}개)")

            # [변경 포인트 1] 구글 뉴스 레이아웃 전체가 로드될 때까지 대기 (ID 기준이라 안전함)
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "search"))
            )
            time.sleep(1)  # 동적 렌더링을 위한 가벼운 대기

            # [변경 포인트 2] 클래스명 대신 역할(role='heading') 또는 뉴스 링크의 텍스트 구조로 타겟팅
            # 구글 뉴스 탭의 제목들은 항상 특정 링크(a 태그) 안이나 role="heading"을 가진 div 내부에 존재합니다.
            elements = driver.find_elements(By.CSS_SELECTOR, "div[role='heading']")

            # 만약 위의 방식으로 안 잡힐 경우를 대비한 서브 타겟팅 (a 태그 내부 div 전수조사)
            if not elements:
                elements = driver.find_elements(By.CSS_SELECTOR, "a div")

            page_added = 0
            for elem in elements:
                try:
                    title = elem.text.strip()
                    # 제목이 너무 짧거나 너무 길어서 뉴스가 아닌 것 같은 텍스트는 필터링
                    if len(title) > 10 and title not in news_headlines:
                        news_headlines.append(title)
                        page_added += 1
                    if len(news_headlines) >= max_headlines:
                        break
                except:
                    continue

            print(f"   -> 이번 페이지에서 {page_added}개 추가 수집됨.")

            if len(news_headlines) >= max_headlines:
                break

            # 다음 페이지 버튼 클릭 (우측 화살표 `id='pnnext'`)
            try:
                next_button = driver.find_element(By.ID, "pnnext")
                next_button.click()
                page_count += 1
                time.sleep(2.5)  # 안전하게 페이지가 넘어갈 수 있도록 대기 시간 소폭 상향
            except Exception:
                print("🏁 다음 페이지가 없거나 찾을 수 없어 수집을 종료합니다.")
                break

    except Exception as e:
        print(f"⚠️ 크롤링 중 오류 발생: {e}")

    finally:
        driver.quit()

    # 데이터 저장
    if news_headlines:
        print(f"\n✅ 총 {len(news_headlines)}개의 헤드라인 수집 완료!")

        with open(txt_file_path, 'w', encoding='utf-8') as f:
            for title in news_headlines:
                f.write(title + "\n")
        print(f"💾 TXT 저장 완료: {txt_file_path}")

        df = pd.DataFrame(news_headlines, columns=["뉴스 기사 제목"])
        df.to_excel(excel_file_path, index=False)
        print(f"💾 엑셀 저장 완료: {excel_file_path}")
    else:
        print("\n😭 수집된 뉴스 헤드라인이 없습니다. 구글 검색창에 결과가 실제로 정상 노출되는지 브라우저 창을 확인해 주세요.")


if __name__ == "__main__":
    crawl_google_news()