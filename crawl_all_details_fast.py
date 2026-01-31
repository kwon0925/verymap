import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# 스레드 안전을 위한 락
print_lock = Lock()
update_lock = Lock()
progress_lock = Lock()

# 진행 상황 추적 (전역 변수)
completed_count = 0
total_count = 0
start_time_global = None

def crawl_shop_detail(url, driver):
    """상점 상세 페이지 완전 크롤링 (오리궁뎅이 백운점 방식)"""
    try:
        driver.get(url)
        time.sleep(2)  # 페이지 로딩 충분히 대기
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        all_text = soup.get_text()
        
        detail = {
            'phone': '',
            'hours': '',
            'description': '',
            'address_detail': '',
            'price_info': '',
            'payment_methods': []
        }
        
        # 전화번호 - 더 정확한 패턴
        phone_patterns = [
            r'010[-.\s]?\d{4}[-.\s]?\d{4}',
            r'\+82[-.\s]?10[-.\s]?\d{4}[-.\s]?\d{4}',
            r'02[-.\s]?\d{3,4}[-.\s]?\d{4}',
            r'0\d{1,2}[-.\s]?\d{3,4}[-.\s]?\d{4}',
        ]
        
        for pattern in phone_patterns:
            phone_match = re.search(pattern, all_text)
            if phone_match:
                phone = phone_match.group(0).replace(' ', '').replace('.', '-')
                if not re.match(r'^\d{1,2}-\d{1,2}$', phone):
                    if phone.startswith('+82'):
                        phone = phone.replace('+82', '0').replace('-', '')
                        if len(phone) == 11 and phone.startswith('010'):
                            phone = f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
                    detail['phone'] = phone
                    break
        
        # 페이지의 모든 텍스트를 줄 단위로 분석
        lines = [line.strip() for line in all_text.split('\n') if line.strip()]
        
        # 매장 소개가 포함된 줄 찾기 (한 줄에 모든 정보가 있을 수 있음)
        description_parts = []
        
        for i, line in enumerate(lines):
            # 영업시간
            if any(kw in line for kw in ['영업시간', '운영시간', 'Hours', '오픈']):
                detail['hours'] = line
                if i + 1 < len(lines):
                    detail['hours'] += ' ' + lines[i + 1]
            
            # 매장 소개가 포함된 줄 찾기 - 정규식으로 분리
            if any(kw in line for kw in ['오리불고기', '오리주물럭', '오리탕', '점심특선', '쌈밥', '신선한야채', '건강밥상', '메뉴', '특선', '정식']):
                # 정규식으로 메뉴 정보 추출
                menu_patterns = [
                    r'오리불고기[전문점]*',
                    r'오리주물럭\([^)]+\)',
                    r'오리탕',
                    r'점심특선[ㅡ-]?[^(\n]+',
                    r'\([^)]*야채[^)]*\)',
                    r'결제\s*\d+%\.\s*1베리\s*\d+원'
                ]
                
                for pattern in menu_patterns:
                    matches = re.findall(pattern, line)
                    for match in matches:
                        if match.strip() and match not in description_parts:
                            description_parts.append(match.strip())
                
                # 패턴으로 찾지 못한 경우 전체 텍스트 사용
                if not description_parts and len(line) > 5:
                    # 불필요한 키워드 제외
                    skip_keywords = ['KR', 'verypay', 'verychain', 'verychat', 'veryads', 'VeryPay', 'Logo', 'VERYPAY']
                    if not any(skip in line for skip in skip_keywords):
                        if line not in description_parts:
                            description_parts.append(line)
        
        # 매장 소개를 하나의 문자열로 합치기
        if description_parts:
            detail['description'] = '\n'.join(description_parts)
        
        # 설명이 없으면 메타 태그에서 찾기
        if not detail['description']:
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                detail['description'] = meta_desc.get('content', '')
        
        return detail
        
    except Exception as e:
        with print_lock:
            print(f"  [오류] {url}: {str(e)[:50]}")
        return {
            'phone': '',
            'hours': '',
            'description': '',
            'address_detail': '',
            'price_info': '',
            'payment_methods': []
        }

def create_driver():
    """브라우저 드라이버 생성"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 헤드리스 모드로 더 빠르게
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")  # 이미지 로딩 비활성화
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def process_shop(shop, original_index, display_index, total):
    """단일 매장 처리"""
    driver = create_driver()
    try:
        if not shop.get('link'):
            return None, original_index
        
        shop_name = shop.get('name', 'Unknown')[:40]
        
        # 시작 알림
        with print_lock:
            print(f"[진행중] {shop_name}... 크롤링 시작")
        
        detail = crawl_shop_detail(shop['link'], driver)
        
        # 완료 알림 및 진행률 업데이트
        global completed_count, start_time_global
        with progress_lock:
            completed_count += 1
            elapsed = time.time() - start_time_global if start_time_global else 0
            progress = (completed_count / total) * 100
            avg_time = elapsed / completed_count if completed_count > 0 else 0
            remaining = (total - completed_count) * avg_time / 5  # 5개 병렬 처리 고려
            
            # 진행률 바 (ASCII 문자 사용)
            bar_length = 30
            filled = int(bar_length * completed_count / total)
            bar = '#' * filled + '-' * (bar_length - filled)
            
            print(f"\n[{completed_count}/{total}] {progress:.1f}% |{bar}|")
            print(f"  [완료] {shop_name}")
            print(f"  [시간] 경과: {elapsed/60:.1f}분 | 예상 남은 시간: {remaining/60:.1f}분")
            print("-" * 60)
        
        return (shop, detail), original_index
    finally:
        driver.quit()

# 메인 실행
if __name__ == '__main__':
    # 기존 데이터 로드
    with open('public/data/shops.json', 'r', encoding='utf-8') as f:
        shops = json.load(f)
    
    # 링크가 있는 매장만 필터링
    shops_with_links = [(shop, i) for i, shop in enumerate(shops) if shop.get('link')]
    
    # 전역 변수 초기화
    completed_count = 0
    total_count = len(shops_with_links)
    start_time_global = time.time()
    
    print("=" * 60)
    print(f"[시작] 전체 매장 상세 정보 크롤링 시작")
    print(f"[정보] 총 {total_count}개의 매장")
    print(f"[정보] 병렬 처리: 최대 5개 동시 실행")
    print(f"[정보] 예상 소요 시간: 약 {total_count * 1.5 / 5 / 60:.1f}분")
    print("=" * 60)
    print("\n진행 상황:\n")
    
    start_time = time.time()
    updated_count = 0
    
    # 병렬 처리 (최대 5개 동시 실행)
    with ThreadPoolExecutor(max_workers=5) as executor:
        # 모든 작업 제출
        future_to_shop = {
            executor.submit(process_shop, shop, original_index, display_index+1, len(shops_with_links)): (shop, original_index)
            for display_index, (shop, original_index) in enumerate(shops_with_links)
        }
        
        # 완료된 작업 처리
        for future in as_completed(future_to_shop):
            try:
                result, original_index = future.result()
                if result:
                    shop, detail = result
                    # 기존 데이터에 상세 정보 업데이트
                    with update_lock:
                        shops[original_index].update(detail)
                        updated_count += 1
            except Exception as e:
                with print_lock:
                    print(f"  [오류] 작업 처리 중 오류: {e}")
    
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print(f"[완료] 크롤링 완료!")
    print(f"[결과] 총 {updated_count}개의 매장 상세 정보 업데이트")
    print(f"[시간] 소요 시간: {elapsed_time:.1f}초 ({elapsed_time/60:.1f}분)")
    print("=" * 60)
    
    print("\n[저장] 데이터 저장 중...")
    # 저장
    with open('public/data/shops.json', 'w', encoding='utf-8') as f:
        json.dump(shops, f, ensure_ascii=False, indent=2)
    
    print("[완료] shops.json 저장 완료!")
