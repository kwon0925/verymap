import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

interface VisitorStats {
  today: number;
  total: number;
  lastUpdate: string;
}

const statsFilePath = path.join(process.cwd(), 'data', 'visitor_stats.json');

// 방문자 통계 읽기
function readStats(): VisitorStats {
  try {
    if (fs.existsSync(statsFilePath)) {
      const data = fs.readFileSync(statsFilePath, 'utf-8');
      return JSON.parse(data);
    }
  } catch (error) {
    console.error('Error reading stats:', error);
  }
  
  return {
    today: 0,
    total: 0,
    lastUpdate: new Date().toISOString().split('T')[0]
  };
}

// 방문자 통계 저장
function saveStats(stats: VisitorStats): void {
  try {
    const dir = path.dirname(statsFilePath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    fs.writeFileSync(statsFilePath, JSON.stringify(stats, null, 2), 'utf-8');
  } catch (error) {
    console.error('Error saving stats:', error);
  }
}

// GET: 방문자 수 조회
export async function GET() {
  const stats = readStats();
  const today = new Date().toISOString().split('T')[0];
  
  // 날짜가 바뀌었으면 오늘 방문자 수 초기화
  if (stats.lastUpdate !== today) {
    stats.today = 0;
    stats.lastUpdate = today;
    saveStats(stats);
  }
  
  return NextResponse.json({
    today: stats.today,
    total: stats.total
  });
}

// POST: 방문자 수 증가
export async function POST(request: NextRequest) {
  try {
    const stats = readStats();
    const today = new Date().toISOString().split('T')[0];
    
    // 날짜가 바뀌었으면 오늘 방문자 수 초기화
    if (stats.lastUpdate !== today) {
      stats.today = 0;
      stats.lastUpdate = today;
    }
    
    // 방문자 수 증가
    stats.today += 1;
    stats.total += 1;
    
    saveStats(stats);
    
    return NextResponse.json({
      today: stats.today,
      total: stats.total,
      success: true
    });
  } catch (error) {
    console.error('Error updating visitor count:', error);
    // 에러 발생 시에도 기본값 반환
    return NextResponse.json({
      today: 0,
      total: 0,
      success: false,
      error: 'Failed to update visitor count'
    }, { status: 500 });
  }
}
