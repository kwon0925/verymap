import time
import json
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# 진행 상황 추적
print_lock = Lock()
completed = 0
total = 0
start_time = None

def create_driver():
    """Chrome 드라이버 생성 (병렬 처리용)"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")  # 이미지 로드 안함 (속도 향상)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def load_all_shops(driver):
    """더보기 버튼 클릭하여 모든 매장 로드"""
    print("\n[Step 1] Loading all shops...")
    click_count = 0
    
    while True:
        try:
            more_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '더보기') or contains(text(), 'Load More')]"))
            )
            driver.execute_script("arguments[0].click();", more_button)
            click_count += 1
            sys.stdout.write(f"\r  Clicking 'Load More'... {click_count} times")
            sys.stdout.flush()
            time.sleep(1.5)
        except:
            print(f"\n  All shops loaded! (Total clicks: {click_count})")
            break

def crawl_basic_info(driver):
    """기본 페이지에서 모든 매장 정보 크롤링"""
    url = "https://pay.verychat.io/shops"
    driver.get(url)
    time.sleep(2)
    
    # 모든 매장 로드
    load_all_shops(driver)
    
    # HTML 파싱
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    shops = soup.select('a[href^="/shops/"]')
    
    results = []
    
    print(f"\n[Step 2] Extracting basic info from {len(shops)} shops...")
    
    for shop in shops:
        try:
            # ID 추출
            shop_id = shop.get('href').split('/')[-1]
            
            # 기본 정보
            name = shop.select_one('h3').get_text(strip=True) if shop.select_one('h3') else ""
            address = shop.select_one('p').get_text(strip=True) if shop.select_one('p') else ""
            
            # VERY 단가 및 결제비율
            info_spans = shop.find_all('span', class_='font-pretendard')
            
            very_price = ""
            payment_ratio = ""
            
            for i, span in enumerate(info_spans):
                txt = span.get_text(strip=True)
                if "VERY 단가" in txt or "VERY단가" in txt:
                    if i + 1 < len(info_spans):
                        very_price = info_spans[i+1].get_text(strip=True)
                elif "결제 비율" in txt or "결제비율" in txt:
                    if i + 1 < len(info_spans):
                        payment_ratio = info_spans[i+1].get_text(strip=True)
            
            # 이미지
            img = shop.find('img')
            img_url = img.get('src') if img else ""
            
            # 카테고리
            category = ""
            category_tag = shop.find('span', class_='text-xs')
            if category_tag:
                category = category_tag.get_text(strip=True)
            
            results.append({
                "name": name,
                "address": address,
                "category": category,
                "veryPrice": very_price,
                "paymentRatio": payment_ratio,
                "link": f"https://pay.verychat.io/shops/{shop_id}",
                "phone": "",
                "hours": "",
                "description": ""
            })
        except Exception as e:
            continue
    
    print(f"  Extracted {len(results)} shops!")
    return results

def crawl_detail_info(shop, driver):
    """상세 페이지 크롤링"""
    try:
        driver.get(shop['link'])
        time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # 매장 소개
        intro_section = soup.find('div', id='introduction')
        if intro_section:
            intro_p = intro_section.find('p')
            if intro_p:
                shop['description'] = intro_p.get_text(strip=True)
        
        # 전화번호
        phone_tag = soup.find('a', href=lambda x: x and x.startswith('tel:'))
        if phone_tag:
            shop['phone'] = phone_tag.get_text(strip=True)
        
        # 영업시간
        hours_section = soup.find(text=lambda x: x and '영업시간' in x)
        if hours_section:
            hours_parent = hours_section.find_parent()
            if hours_parent:
                shop['hours'] = hours_parent.get_text(strip=True)
        
        return True
    except Exception as e:
        return False

def process_shop(shop, index, total_count):
    """개별 매장 처리 (병렬 처리용)"""
    global completed, start_time
    
    driver = create_driver()
    
    try:
        success = crawl_detail_info(shop, driver)
        
        with print_lock:
            completed += 1
            progress = (completed / total_count) * 100
            elapsed = time.time() - start_time
            avg_time = elapsed / completed
            remaining = avg_time * (total_count - completed)
            
            # 진행 상황 표시 (한 줄로)
            bar_length = 30
            filled = int(bar_length * completed / total_count)
            bar = '#' * filled + '-' * (bar_length - filled)
            
            sys.stdout.write(f"\r  [{completed}/{total_count}] {progress:.1f}% |{bar}| Elapsed: {elapsed:.0f}s | Remaining: {remaining:.0f}s")
            sys.stdout.flush()
            
            # 10개마다 줄바꿈
            if completed % 10 == 0:
                print(f"\n  >> Checkpoint: {completed}/{total_count} shops completed")
        
        return shop, success
    except Exception as e:
        with print_lock:
            print(f"\n  [ERROR] {shop['name']}: {str(e)[:50]}")
        return shop, False
    finally:
        driver.quit()

def main():
    global completed, total, start_time
    
    print("="*60)
    print("VeryChat Shops Crawler - Parallel Processing")
    print("="*60)
    
    # 메인 드라이버로 기본 정보 크롤링
    main_driver = create_driver()
    
    try:
        # 기본 정보 크롤링
        shops = crawl_basic_info(main_driver)
        total = len(shops)
        
        print(f"\n[Step 3] Crawling details from {total} shops (Parallel)...")
        print("  Workers: 5 threads")
        print()
        
        # 병렬 처리로 상세 정보 크롤링
        completed = 0
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(process_shop, shop, i, total) for i, shop in enumerate(shops)]
            
            for future in as_completed(futures):
                try:
                    shop, success = future.result()
                except Exception as e:
                    print(f"\n  [ERROR] Thread error: {str(e)[:50]}")
        
        print("\n\n[Step 4] Saving to shops.json...")
        
        # JSON 저장
        with open('public/data/shops.json', 'w', encoding='utf-8') as f:
            json.dump(shops, f, ensure_ascii=False, indent=2)
        
        total_time = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"[DONE] Crawling completed!")
        print(f"  Total shops: {total}")
        print(f"  Total time: {total_time:.1f}s ({total_time/60:.1f}min)")
        print(f"  Average: {total_time/total:.1f}s per shop")
        print(f"  Saved to: public/data/shops.json")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
    finally:
        main_driver.quit()

if __name__ == '__main__':
    main()
