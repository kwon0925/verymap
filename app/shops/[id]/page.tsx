'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface Shop {
  name: string;
  address: string;
  category: string;
  veryPrice: string;
  paymentRatio: string;
  link?: string;
  phone?: string;
  hours?: string;
  description?: string;
  address_detail?: string;
  price_info?: string;
  payment_methods?: string[];
}

export default function ShopDetail({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [shop, setShop] = useState<Shop | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/data/shops.json')
      .then(res => res.json())
      .then((data: Shop[]) => {
        // id로 상점 찾기 (링크의 마지막 부분과 매칭)
        const foundShop = data.find(s => s.link?.includes(params.id));
        setShop(foundShop || null);
        setLoading(false);
      })
      .catch(err => {
        console.error('데이터 로드 실패:', err);
        setLoading(false);
      });
  }, [params.id]);

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

  if (!shop) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">상점을 찾을 수 없습니다</h2>
          <Link href="/" className="text-blue-600 hover:text-blue-800">
            홈으로 돌아가기
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <header className="bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.back()}
              className="p-2 hover:bg-white/20 rounded-lg transition"
            >
              ← 뒤로
            </button>
            <div>
              <h1 className="text-xl font-bold">상점 상세정보</h1>
            </div>
          </div>
        </div>
      </header>

      {/* 상세 정보 */}
      <div className="container mx-auto px-4 py-6 max-w-2xl">
        <div className="bg-white rounded-xl shadow-lg p-6 space-y-6">
          {/* 상점명 & 카테고리 */}
          <div>
            <div className="flex items-start justify-between mb-2">
              <h2 className="text-2xl font-bold text-gray-900">{shop.name}</h2>
              {shop.category && (
                <span className="px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-full">
                  {shop.category}
                </span>
              )}
            </div>
          </div>

          {/* 주소 */}
          <div className="border-t pt-4">
            <h3 className="text-sm font-semibold text-gray-500 mb-2">📍 주소</h3>
            <p className="text-gray-900">{shop.address_detail || shop.address}</p>
          </div>

          {/* 전화번호 */}
          {shop.phone && (
            <div className="border-t pt-4">
              <h3 className="text-sm font-semibold text-gray-500 mb-2">📞 전화번호</h3>
              <a
                href={`tel:${shop.phone.replace(/[^0-9]/g, '')}`}
                className="text-xl font-bold text-blue-600 hover:text-blue-800 inline-flex items-center gap-2"
              >
                {shop.phone}
                <span className="text-sm bg-blue-100 text-blue-700 px-3 py-1 rounded-full">
                  전화 걸기
                </span>
              </a>
            </div>
          )}

          {/* 영업시간 */}
          {shop.hours && (
            <div className="border-t pt-4">
              <h3 className="text-sm font-semibold text-gray-500 mb-2">🕐 영업시간</h3>
              <p className="text-gray-900">{shop.hours}</p>
            </div>
          )}

          {/* VERY 단가 */}
          {shop.veryPrice && shop.veryPrice !== '-' && (
            <div className="border-t pt-4">
              <h3 className="text-sm font-semibold text-gray-500 mb-2">💰 VERY 단가</h3>
              <p className="text-2xl font-bold text-gray-900">{shop.price_info || shop.veryPrice}</p>
            </div>
          )}

          {/* 결제비율 */}
          {shop.paymentRatio && shop.paymentRatio !== '-' && (
            <div className="border-t pt-4">
              <h3 className="text-sm font-semibold text-gray-500 mb-2">💳 결제비율</h3>
              <p className="text-2xl font-bold text-gray-900">{shop.paymentRatio}</p>
              {shop.payment_methods && shop.payment_methods.length > 0 && (
                <div className="mt-2 space-y-1">
                  {shop.payment_methods.map((method, idx) => (
                    <p key={idx} className="text-sm text-gray-600">{method}</p>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* 설명 */}
          {shop.description && (
            <div className="border-t pt-4">
              <h3 className="text-sm font-semibold text-gray-500 mb-2">📝 상세 설명</h3>
              <p className="text-gray-700 leading-relaxed">{shop.description}</p>
            </div>
          )}

          {/* 원본 링크 */}
          {shop.link && (
            <div className="border-t pt-4">
              <a
                href={shop.link}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition"
              >
                VeryPay에서 보기 →
              </a>
            </div>
          )}
        </div>

        {/* 돌아가기 버튼 */}
        <div className="mt-6 text-center">
          <button
            onClick={() => router.back()}
            className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
          >
            ← 목록으로 돌아가기
          </button>
        </div>
      </div>
    </div>
  );
}
