'use client';

import { useState, useEffect, useMemo } from 'react';
import dosiData from '@/dosi.json';

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

interface DosiItem {
  sido: string;
  sigungu: string;
  upmyeondong: string;
}

// 시도 매칭 패턴 (유연한 매칭을 위한 매핑)
const SIDO_PATTERNS: Record<string, string[]> = {
  '서울특별시': ['서울'],
  '부산광역시': ['부산'],
  '대구광역시': ['대구'],
  '인천광역시': ['인천'],
  '광주광역시': ['광주'],
  '대전광역시': ['대전'],
  '울산광역시': ['울산'],
  '세종특별자치시': ['세종'],
  '경기도': ['경기'],
  '강원특별자치도': ['강원'],
  '충청북도': ['충북', '충청북'],
  '충청남도': ['충남', '충청남'],
  '전북특별자치도': ['전북', '전라북', '전라북도'],
  '전라남도': ['전남', '전라남'],
  '경상북도': ['경북', '경상북'],
  '경상남도': ['경남', '경상남'],
  '제주특별자치도': ['제주'],
};

// 주소가 특정 시도에 속하는지 확인하는 함수
function matchesSido(address: string, sido: string): boolean {
  // 시도 이름 자체가 포함되어 있는지 확인
  if (address.includes(sido)) {
    return true;
  }
  
  // 축약형이나 별칭도 확인
  const patterns = SIDO_PATTERNS[sido] || [];
  return patterns.some(pattern => address.includes(pattern));
}

// 주소가 특정 시군구에 속하는지 확인하는 함수
function matchesSigungu(address: string, sigungu: string): boolean {
  return address.includes(sigungu);
}

export default function Home() {
  const [shops, setShops] = useState<Shop[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSido, setSelectedSido] = useState<string>('');
  const [selectedSigungu, setSelectedSigungu] = useState<string>('');

  useEffect(() => {
    // 데이터 로드
    fetch('/data/shops.json')
      .then(res => res.json())
      .then(data => {
        setShops(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('데이터 로드 실패:', err);
        setLoading(false);
      });
  }, []);

  // 시도 목록 (dosi.json에서)
  const sidoList = useMemo(() => {
    return dosiData.sido.map(s => s.name);
  }, []);

  // 시군구 목록 (선택된 시도 기준)
  const sigunguList = useMemo(() => {
    if (!selectedSido) return [];
    const sido = dosiData.sido.find(s => s.name === selectedSido);
    return sido ? sido.sigungu.map(sg => sg.name) : [];
  }, [selectedSido]);

  // 필터링된 상점 (유연한 주소 매칭)
  const filteredShops = useMemo(() => {
    return shops.filter(shop => {
      const address = shop.address;
      
      // 시도 필터 (유연한 매칭)
      if (selectedSido) {
        if (!matchesSido(address, selectedSido)) {
          return false;
        }
      }
      
      // 시군구 필터 (유연한 매칭)
      if (selectedSigungu) {
        if (!matchesSigungu(address, selectedSigungu)) {
          return false;
        }
      }
      
      return true;
    });
  }, [shops, selectedSido, selectedSigungu]);

  const handleSidoChange = (sido: string) => {
    setSelectedSido(sido);
    setSelectedSigungu('');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">로딩 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pb-20">
      {/* 헤더 */}
      <header className="bg-gradient-to-r from-blue-600 to-blue-700 text-white sticky top-0 z-10 shadow-lg">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold">🗺️ 베리챗 상점</h1>
          <p className="text-blue-100 text-sm mt-1">전 세계 베리챗 상점을 찾아보세요</p>
        </div>
      </header>

      {/* 필터 섹션 */}
      <div className="bg-white shadow-md sticky top-[88px] z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="space-y-3">
            {/* 시도 선택 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                시/도
              </label>
              <select
                value={selectedSido}
                onChange={(e) => handleSidoChange(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-base"
              >
                <option value="">전체 지역</option>
                {sidoList.map(sido => {
                  const count = shops.filter(s => matchesSido(s.address, sido)).length;
                  return (
                    <option key={sido} value={sido}>
                      {sido} ({count})
                    </option>
                  );
                })}
              </select>
            </div>

            {/* 시군구 선택 */}
            {selectedSido && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  시/군/구
                </label>
                <select
                  value={selectedSigungu}
                  onChange={(e) => setSelectedSigungu(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-base"
                >
                  <option value="">전체</option>
                  {sigunguList.map(sigungu => {
                    const count = shops.filter(s => 
                      matchesSido(s.address, selectedSido) && matchesSigungu(s.address, sigungu)
                    ).length;
                    return (
                      <option key={sigungu} value={sigungu}>
                        {sigungu} ({count})
                      </option>
                    );
                  })}
                </select>
              </div>
            )}
          </div>

          {/* 결과 카운트 */}
          <div className="mt-4 text-sm text-gray-600">
            총 <span className="font-bold text-blue-600">{filteredShops.length}</span>개의 상점
          </div>
        </div>
      </div>

      {/* 상점 리스트 */}
      <div className="container mx-auto px-4 py-6">
        {filteredShops.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">상점이 없습니다</p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredShops.map((shop, index) => (
              <div
                key={index}
                className="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow p-4 border border-gray-100"
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-bold text-lg text-gray-900 flex-1">
                    {shop.name}
                  </h3>
                  {shop.category && (
                    <span className="ml-2 px-3 py-1 bg-blue-100 text-blue-700 text-xs rounded-full whitespace-nowrap">
                      {shop.category}
                    </span>
                  )}
                </div>

                <div className="space-y-2 text-sm">
                  <div className="flex items-start text-gray-600">
                    <span className="mr-2">📍</span>
                    <span className="flex-1">{shop.address}</span>
                  </div>


                  <div className="flex items-center gap-4 pt-2 border-t border-gray-100">
                    {shop.veryPrice && (
                      <div className="flex items-center text-xs">
                        <span className="text-gray-500 mr-1">💰 VERY 단가:</span>
                        <span className="font-semibold text-gray-900">{shop.veryPrice}</span>
                      </div>
                    )}
                    {shop.paymentRatio && (
                      <div className="flex items-center text-xs">
                        <span className="text-gray-500 mr-1">💳 결제비율:</span>
                        <span className="font-semibold text-gray-900">{shop.paymentRatio}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
