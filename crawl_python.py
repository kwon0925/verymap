import time
import json
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def crawl_verychat_shops(url):
    # 브라우저 설정
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # 창을 띄우지 않고 실행하려면 주석 해제
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    print("[시작] 데이터 로딩 중...")
    
    # 초기 로딩 대기
    time.sleep(3)

    click_count = 0
    while True:
        try:
            # '더보기' 버튼이 나타날 때까지 대기
            more_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), '더보기')]")))
            
            # 버튼 클릭 (자바스크립트로 클릭하여 가려짐 문제 방지)
            driver.execute_script("arguments[0].click();", more_button)
            click_count += 1
            
            # 로딩 대기
            time.sleep(1.5)
            
            # 현재까지 로드된 상점 수 확인
            current_shops = driver.find_elements(By.CSS_SELECTOR, "a[href*='/shop']")
            print(f"   {click_count}번째 더보기 클릭... (현재 {len(current_shops)}개 로드)")

        except Exception as e:
            # 더 이상 '더보기' 버튼이 없으면 반복 종료
            print(f"[완료] 모든 데이터 로드 완료! (총 {click_count}번 클릭)")
            break

    # 전체 페이지 소스 파싱
    print("[파싱] 데이터 파싱 중...")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    shop_list = []
    # 상점 카드 요소들 찾기 (여러 선택자 시도)
    items = soup.select("a[href^='/shops/']")
    
    if not items:
        items = soup.select("a[href*='/shop']")
    
    print(f"[정보] 찾은 상점 요소 수: {len(items)}")

    for idx, item in enumerate(items, 1):
        try:
            # 상점명
            name = ""
            h3 = item.select_one("h3")
            if h3:
                name = h3.get_text(strip=True)
            
            # 카테고리
            category = ""
            cat_span = item.select_one("span.font-pretendard.text-xs")
            if cat_span:
                category = cat_span.get_text(strip=True)
            
            # 주소
            address = ""
            addr_p = item.select_one("p.truncate")
            if addr_p:
                address = addr_p.get_text(strip=True)
            else:
                # 다른 선택자 시도
                addr_p = item.select_one("p")
                if addr_p:
                    address = addr_p.get_text(strip=True)
            
            # 단가 및 결제비율 추출
            spans = item.find_all("span")
            price = ""
            ratio = ""
            
            for i, s in enumerate(spans):
                text = s.text.strip()
                if "VERY 단가" in text or "VERY단가" in text:
                    if i+1 < len(spans):
                        price = spans[i+1].text.strip()
                if "결제 비율" in text or "결제비율" in text:
                    if i+1 < len(spans):
                        ratio = spans[i+1].text.strip()

            # 상세 링크
            href = item.get('href', '')
            if href and not href.startswith('http'):
                href = "https://pay.verychat.io" + href

            if name or address:  # 최소한 이름이나 주소가 있어야 함
                shop_list.append({
                    "name": name,
                    "address": address,
                    "category": category,
                    "veryPrice": price,
                    "paymentRatio": ratio,
                    "link": href
                })
                
                if idx % 100 == 0:
                    print(f"   {idx}개 처리 중...")
                    
        except Exception as e:
            print(f"   [경고] {idx}번째 항목 파싱 오류: {e}")
            continue

    return shop_list

def save_data(data, format='json'):
    """데이터를 JSON 및 CSV로 저장"""
    
    # CSV 저장 (pandas 없이)
    if len(data) > 0:
        import os
        os.makedirs("data", exist_ok=True)
        
        with open("data/verychat_shops.csv", "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"[저장] CSV 저장 완료: data/verychat_shops.csv")
    
    # data 폴더 생성
    import os
    os.makedirs("data", exist_ok=True)
    os.makedirs("public/data", exist_ok=True)
    
    # JSON 저장 (웹앱용)
    with open("data/shops.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[저장] JSON 저장 완료: data/shops.json")
    
    # public 폴더에도 복사
    with open("public/data/shops.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[저장] 웹앱용 JSON 저장 완료: public/data/shops.json")
    
    # 통계 출력
    print(f"\n[통계]")
    print(f"   총 상점 수: {len(data)}")
    if len(data) > 0:
        categories = set(item['category'] for item in data if item['category'])
        print(f"   카테고리 수: {len(categories)}")
        print(f"   카테고리: {', '.join(sorted(categories))}")

# 실행
if __name__ == "__main__":
    TARGET_URL = "https://pay.verychat.io/shops"
    
    print("=" * 60)
    print("[VeryChat] 상점 크롤링 시작")
    print("=" * 60)
    print(f"URL: {TARGET_URL}")
    print()
    
    try:
        data = crawl_verychat_shops(TARGET_URL)
        
        if len(data) > 0:
            print(f"\n[성공] 총 {len(data)}개의 상점 정보를 수집했습니다!")
            save_data(data)
            print("\n[완료] 크롤링 완료!")
        else:
            print("\n[경고] 수집된 데이터가 없습니다. 선택자를 확인해주세요.")
            
    except Exception as e:
        print(f"\n[오류] 오류 발생: {e}")
        import traceback
        traceback.print_exc()
