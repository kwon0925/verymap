import puppeteer from 'puppeteer';
import fs from 'fs/promises';
import path from 'path';

interface Shop {
  name: string;
  address: string;
  category: string;
  veryPrice: string;
  paymentRatio: string;
  country?: string;
  state?: string;
  city?: string;
}

async function crawlShops() {
  console.log('🚀 크롤링 시작...');
  
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  try {
    const page = await browser.newPage();
    
    // User agent 설정
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36');
    
    console.log('📄 페이지 로딩 중...');
    await page.goto('https://pay.verychat.io/shops', {
      waitUntil: 'networkidle0',
      timeout: 60000
    });

    // 페이지가 완전히 로드될 때까지 충분히 대기
    console.log('⏳ 페이지 렌더링 대기 중...');
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // 스크롤하여 lazy loading 트리거
    await page.evaluate(() => {
      window.scrollTo(0, document.body.scrollHeight);
    });
    await new Promise(resolve => setTimeout(resolve, 2000));

    // "더보기" 버튼을 반복 클릭하여 모든 데이터 로드
    console.log('📥 "더보기" 버튼 클릭 중...');
    let clickCount = 0;
    let previousHeight = 0;
    let sameHeightCount = 0;

    while (true) {
      try {
        // 여러 방법으로 "더보기" 버튼 찾기
        const moreButton = await page.evaluate(() => {
          // 텍스트로 버튼 찾기
          const buttons = Array.from(document.querySelectorAll('button, a, div[role="button"]'));
          const moreBtn = buttons.find(btn => {
            const text = btn.textContent?.trim().toLowerCase() || '';
            return text.includes('더보기') || 
                   text.includes('more') || 
                   text.includes('load more') ||
                   text.includes('더 보기');
          });

          if (moreBtn) {
            (moreBtn as HTMLElement).scrollIntoView({ behavior: 'smooth', block: 'center' });
            return true;
          }
          return false;
        });

        if (moreButton) {
          // 버튼 클릭
          await page.evaluate(() => {
            const buttons = Array.from(document.querySelectorAll('button, a, div[role="button"]'));
            const moreBtn = buttons.find(btn => {
              const text = btn.textContent?.trim().toLowerCase() || '';
              return text.includes('더보기') || 
                     text.includes('more') || 
                     text.includes('load more') ||
                     text.includes('더 보기');
            });
            if (moreBtn) {
              (moreBtn as HTMLElement).click();
            }
          });

          clickCount++;
          console.log(`   ${clickCount}번째 더보기 클릭...`);
          
          // 새 데이터 로딩 대기
          await new Promise(resolve => setTimeout(resolve, 2000));

          // 페이지 높이 확인 (변화가 없으면 더 이상 로드할 데이터 없음)
          const currentHeight = await page.evaluate(() => document.body.scrollHeight);
          
          if (currentHeight === previousHeight) {
            sameHeightCount++;
            if (sameHeightCount >= 3) {
              console.log('✅ 더 이상 로드할 데이터가 없습니다');
              break;
            }
          } else {
            sameHeightCount = 0;
            previousHeight = currentHeight;
          }
        } else {
          console.log('✅ 더보기 버튼을 찾을 수 없습니다');
          break;
        }

        // 무한 루프 방지 (최대 50번)
        if (clickCount >= 50) {
          console.log('⚠️ 최대 클릭 횟수 도달');
          break;
        }
      } catch (error) {
        console.log('⚠️ 버튼 클릭 중 오류:', error);
        break;
      }
    }

    console.log(`📊 총 ${clickCount}번 더보기 클릭 완료`);

    // 스크린샷 저장 (디버깅용)
    await page.screenshot({ path: 'debug-screenshot.png', fullPage: true });
    console.log('📸 스크린샷 저장: debug-screenshot.png');

    // 페이지 HTML 일부 저장 (디버깅용)
    const htmlContent = await page.content();
    await fs.writeFile('debug-page.html', htmlContent, 'utf-8');
    console.log('📄 HTML 저장: debug-page.html');

    // 페이지 HTML 구조 확인
    console.log('🔍 페이지 구조 분석 중...');
    
    // 모든 상점 데이터 수집
    const shops: Shop[] = await page.evaluate(() => {
      const results: Shop[] = [];
      
      // 모든 링크 요소 찾기 (상점 페이지로 가는 링크)
      const allLinks = Array.from(document.querySelectorAll('a'));
      const shopLinks = allLinks.filter(link => {
        const href = link.getAttribute('href') || '';
        return href.includes('/shop/') || href.includes('shop');
      });

      console.log(`찾은 상점 링크 수: ${shopLinks.length}`);

      // 링크가 없으면 다른 방법 시도
      let shopElements: Element[] = shopLinks.length > 0 ? shopLinks : [];
      
      if (shopElements.length === 0) {
        // 모든 div를 찾아서 상점 카드로 보이는 것 필터링
        const allDivs = Array.from(document.querySelectorAll('div'));
        
        // 상점 정보가 있을 것 같은 div 찾기
        shopElements = allDivs.filter(div => {
          const childCount = div.children.length;
          const textLength = (div.textContent || '').length;
          
          // 적절한 크기의 컨테이너 (너무 작거나 크지 않음)
          return childCount >= 2 && childCount <= 20 && textLength > 20 && textLength < 500;
        });
        
        console.log(`후보 요소 수: ${shopElements.length}`);
        
        // 더 정확한 필터링
        shopElements = shopElements.filter(el => {
          const text = el.textContent || '';
          const hasLocation = text.match(/[가-힣]{2,}(시|도|구|군|동|읍|면)/);
          const hasCategory = text.match(/(식당|카페|미용|패션|취미|사무|가전|의료|부동산|여행|반려|사주|타로|기타|지원)/);
          return hasLocation || hasCategory;
        });
      }

      console.log(`최종 요소 수: ${shopElements.length}`);

      shopElements.forEach((element, index) => {
        try {
          const textContent = element.textContent || '';
          
          // 빈 요소 스킵
          if (!textContent.trim()) return;
          
          // 상점명, 주소, 카테고리 등 추출
          const lines = textContent
            .split('\n')
            .map(l => l.trim())
            .filter(l => l && l.length > 0);
          
          // 최소 정보가 있는지 확인
          if (lines.length < 2) return;

          const shop: Shop = {
            name: '',
            address: '',
            category: '',
            veryPrice: '',
            paymentRatio: ''
          };

          // 상점명 찾기 (보통 첫 번째 줄)
          for (const line of lines) {
            if (line && !line.includes('VERY') && !line.includes('결제') && !line.includes('생태계') && line.length > 1) {
              if (!shop.name) {
                shop.name = line;
              } else if (!shop.address && line.length > 5) {
                shop.address = line;
                break;
              }
            }
          }

          // VERY 단가 찾기
          const priceMatch = textContent.match(/VERY\s*단가([^\n결제]+)/);
          if (priceMatch) {
            shop.veryPrice = priceMatch[1].trim();
          }

          // 결제비율 찾기
          const ratioMatch = textContent.match(/결제\s*비율([^\nV]+)/);
          if (ratioMatch) {
            shop.paymentRatio = ratioMatch[1].trim();
          }

          // 카테고리 추출
          const categories = [
            '식당/카페', '미용', '패션/잡화', '취미/도서', '사무기기', 
            '가전/게임', '의료/건강', '부동산/인테리어', '여행/숙박', 
            '반려동물', '사주/타로', '지원센터', '기타'
          ];
          
          for (const cat of categories) {
            if (textContent.includes(cat)) {
              shop.category = cat;
              break;
            }
          }

          // 유효한 데이터만 추가
          if (shop.name && shop.address) {
            results.push(shop);
          }
        } catch (err) {
          console.error(`요소 ${index} 파싱 오류:`, err);
        }
      });

      return results;
    });

    console.log(`✅ ${shops.length}개의 상점 데이터 수집 완료`);

    // 중복 제거 (이름 + 주소 기준)
    const uniqueShops = shops.filter((shop, index, self) => {
      return index === self.findIndex(s => 
        s.name === shop.name && s.address === shop.address
      );
    });

    console.log(`🔍 중복 제거 후: ${uniqueShops.length}개`);

    // 주소 파싱하여 국가/시도/시군구 분류
    const parsedShops = uniqueShops.map(shop => parseAddress(shop));

    // 데이터 저장
    const dataDir = path.join(process.cwd(), 'data');
    await fs.mkdir(dataDir, { recursive: true });
    
    const filePath = path.join(dataDir, 'shops.json');
    await fs.writeFile(filePath, JSON.stringify(parsedShops, null, 2), 'utf-8');
    
    console.log(`💾 데이터 저장 완료: ${filePath}`);
    console.log(`📊 총 ${parsedShops.length}개 상점`);

    // 통계 출력
    const stats = getStats(parsedShops);
    console.log('\n📈 통계:');
    console.log(`- 국가: ${stats.countries}개`);
    console.log(`- 카테고리: ${stats.categories}개`);

  } catch (error) {
    console.error('❌ 크롤링 오류:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

function parseAddress(shop: Shop): Shop {
  const address = shop.address.toLowerCase();
  const originalAddress = shop.address;
  
  // 한국 주소 파싱
  if (address.includes('서울') || address.includes('seoul')) {
    shop.country = '대한민국';
    shop.state = '서울특별시';
    const districts = ['강남구', '서초구', '송파구', '강동구', '동작구', '관악구', '영등포구', '양천구', '구로구', '금천구', '강서구', '마포구', '서대문구', '은평구', '노원구', '도봉구', '강북구', '성북구', '중랑구', '동대문구', '광진구', '성동구', '용산구', '중구', '종로구'];
    for (const district of districts) {
      if (originalAddress.includes(district)) {
        shop.city = district;
        break;
      }
    }
  } else if (address.includes('부산') || address.includes('busan')) {
    shop.country = '대한민국';
    shop.state = '부산광역시';
    shop.city = extractDistrict(originalAddress);
  } else if (address.includes('경기') || address.includes('gyeonggi')) {
    shop.country = '대한민국';
    shop.state = '경기도';
    shop.city = extractCity(originalAddress);
  } else if (address.includes('인천') || address.includes('incheon')) {
    shop.country = '대한민국';
    shop.state = '인천광역시';
    shop.city = extractDistrict(originalAddress);
  } else if (address.includes('대전') || address.includes('daejeon')) {
    shop.country = '대한민국';
    shop.state = '대전광역시';
    shop.city = extractDistrict(originalAddress);
  } else if (address.includes('대구') || address.includes('daegu')) {
    shop.country = '대한민국';
    shop.state = '대구광역시';
    shop.city = extractDistrict(originalAddress);
  } else if (address.includes('광주') || address.includes('gwangju')) {
    shop.country = '대한민국';
    shop.state = '광주광역시';
    shop.city = extractDistrict(originalAddress);
  } else if (address.includes('울산') || address.includes('ulsan')) {
    shop.country = '대한민국';
    shop.state = '울산광역시';
    shop.city = extractDistrict(originalAddress);
  } else if (address.includes('세종') || address.includes('sejong')) {
    shop.country = '대한민국';
    shop.state = '세종특별자치시';
  } else if (address.includes('제주') || address.includes('jeju')) {
    shop.country = '대한민국';
    shop.state = '제주특별자치도';
    if (originalAddress.includes('제주시')) shop.city = '제주시';
    else if (originalAddress.includes('서귀포시')) shop.city = '서귀포시';
  } else if (address.includes('강원') || address.includes('gangwon')) {
    shop.country = '대한민국';
    shop.state = '강원도';
    shop.city = extractCity(originalAddress);
  } else if (address.includes('충청북도') || address.includes('충북') || address.includes('chungbuk')) {
    shop.country = '대한민국';
    shop.state = '충청북도';
    shop.city = extractCity(originalAddress);
  } else if (address.includes('충청남도') || address.includes('충남') || address.includes('chungnam')) {
    shop.country = '대한민국';
    shop.state = '충청남도';
    shop.city = extractCity(originalAddress);
  } else if (address.includes('전라북도') || address.includes('전북') || address.includes('jeonbuk')) {
    shop.country = '대한민국';
    shop.state = '전라북도';
    shop.city = extractCity(originalAddress);
  } else if (address.includes('전라남도') || address.includes('전남') || address.includes('jeonnam')) {
    shop.country = '대한민국';
    shop.state = '전라남도';
    shop.city = extractCity(originalAddress);
  } else if (address.includes('경상북도') || address.includes('경북') || address.includes('gyeongbuk')) {
    shop.country = '대한민국';
    shop.state = '경상북도';
    shop.city = extractCity(originalAddress);
  } else if (address.includes('경상남도') || address.includes('경남') || address.includes('gyeongnam')) {
    shop.country = '대한민국';
    shop.state = '경상남도';
    shop.city = extractCity(originalAddress);
  }
  // 인도네시아
  else if (address.includes('indonesia') || address.includes('jawa') || address.includes('jakarta')) {
    shop.country = '인도네시아';
    shop.state = extractIndonesiaState(shop.address);
  }
  // 파키스탄
  else if (address.includes('pakistan') || address.includes('islamabad') || address.includes('karachi')) {
    shop.country = '파키스탄';
    shop.state = extractPakistanState(shop.address);
  }
  // 나이지리아
  else if (address.includes('nigeria') || address.includes('lagos') || address.includes('abuja')) {
    shop.country = '나이지리아';
    shop.state = extractNigeriaState(shop.address);
  }
  // 가나
  else if (address.includes('ghana') || address.includes('accra')) {
    shop.country = '가나';
    shop.state = 'Greater Accra';
  }
  // 케냐
  else if (address.includes('kenya') || address.includes('nairobi')) {
    shop.country = '케냐';
    shop.state = 'Nairobi';
  }
  // 네팔
  else if (address.includes('nepal') || address.includes('kathmandu') || address.includes('bhaktapur')) {
    shop.country = '네팔';
    shop.state = extractNepalState(shop.address);
  }
  
  return shop;
}

function extractDistrict(address: string): string {
  const match = address.match(/([가-힣]+구)/);
  return match ? match[1] : '';
}

function extractCity(address: string): string {
  // 시/군 목록 (전국)
  const cities = [
    // 경기도
    '수원시', '성남시', '고양시', '용인시', '부천시', '안산시', '안양시', '남양주시', 
    '화성시', '평택시', '의정부시', '시흥시', '파주시', '김포시', '광명시', '광주시', 
    '군포시', '오산시', '이천시', '양주시', '안성시', '구리시', '포천시', '의왕시', 
    '하남시', '여주시', '동두천시', '과천시', '가평군', '양평군', '연천군',
    // 강원도
    '춘천시', '원주시', '강릉시', '동해시', '태백시', '속초시', '삼척시',
    '홍천군', '횡성군', '영월군', '평창군', '정선군', '철원군', '화천군', '양구군', '인제군', '고성군', '양양군',
    // 충청북도
    '청주시', '충주시', '제천시', '보은군', '옥천군', '영동군', '증평군', '진천군', '괴산군', '음성군', '단양군',
    // 충청남도
    '천안시', '공주시', '보령시', '아산시', '서산시', '논산시', '계룡시', '당진시',
    '금산군', '부여군', '서천군', '청양군', '홍성군', '예산군', '태안군',
    // 전라북도
    '전주시', '군산시', '익산시', '정읍시', '남원시', '김제시',
    '완주군', '진안군', '무주군', '장수군', '임실군', '순창군', '고창군', '부안군',
    // 전라남도
    '목포시', '여수시', '순천시', '나주시', '광양시',
    '담양군', '곡성군', '구례군', '고흥군', '보성군', '화순군', '장흥군', '강진군', 
    '해남군', '영암군', '무안군', '함평군', '영광군', '장성군', '완도군', '진도군', '신안군',
    // 경상북도
    '포항시', '경주시', '김천시', '안동시', '구미시', '영주시', '영천시', '상주시', '문경시', '경산시',
    '군위군', '의성군', '청송군', '영양군', '영덕군', '청도군', '고령군', '성주군', '칠곡군', 
    '예천군', '봉화군', '울진군', '울릉군',
    // 경상남도
    '창원시', '진주시', '통영시', '사천시', '김해시', '밀양시', '거제시', '양산시',
    '의령군', '함안군', '창녕군', '고성군', '남해군', '하동군', '산청군', '함양군', '거창군', '합천군'
  ];
  
  for (const city of cities) {
    if (address.includes(city)) {
      return city;
    }
  }
  return '';
}

function extractIndonesiaState(address: string): string {
  if (address.includes('Jakarta')) return 'Jakarta';
  if (address.includes('Jawa Timur') || address.includes('Banyuwangi') || address.includes('Malang')) return 'Jawa Timur';
  if (address.includes('Lampung')) return 'Lampung';
  return '';
}

function extractPakistanState(address: string): string {
  if (address.includes('Islamabad')) return 'Islamabad';
  if (address.includes('Karachi')) return 'Sindh';
  if (address.includes('Lahore')) return 'Punjab';
  if (address.includes('Katsina') || address.includes('Kano')) return 'Katsina';
  if (address.includes('Bhakkar')) return 'Punjab';
  return '';
}

function extractNigeriaState(address: string): string {
  if (address.includes('Lagos')) return 'Lagos';
  if (address.includes('Akure')) return 'Ondo';
  if (address.includes('Ogbomoso')) return 'Oyo';
  if (address.includes('Jos')) return 'Plateau';
  return '';
}

function extractNepalState(address: string): string {
  if (address.includes('Kathmandu')) return 'Bagmati';
  if (address.includes('Bhaktapur')) return 'Bagmati';
  return '';
}

function getStats(shops: Shop[]) {
  const countries = new Set(shops.map(s => s.country).filter(Boolean));
  const categories = new Set(shops.map(s => s.category).filter(Boolean));
  
  return {
    countries: countries.size,
    categories: categories.size
  };
}

// 실행
crawlShops().catch(console.error);
