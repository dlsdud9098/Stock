import React, { useState, useEffect } from 'react';
import DataTable from './DataTable'; // 우리가 만든 DataTable 컴포넌트 불러오기
import './App.css';

function App() {
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // 두 데이터를 모두 담고 있는 새 API 엔드포인트 호출
    const fetchData = () => {
      // fetch('http://127.0.0.1:5000/api/market_data')
      fetch('http://158.180.79.70:5000/api/market_data')
        .then(response => {
          if (!response.ok) {
            throw new Error('네트워크 응답이 올바르지 않습니다.');
          }
          return response.json();
        })
        .then(fetchedData => {
          setMarketData(fetchedData);
        })
        .catch(error => {
          // 반복되는 에러는 콘솔에만 출력하여 화면을 가리지 않도록 처리
          console.error("데이터를 가져오는 중 에러 발생:", error);
          setError(error); // 필요하다면 에러 상태를 업데이트
        })
        .finally(() => {
          // 첫 로딩이 끝났음을 표시
          setLoading(false);
        });
    };

    // 1. 컴포넌트가 마운트되면 먼저 한 번 데이터를 가져옵니다.
    fetchData();

    // 2. 그 후 1초(1000ms)마다 fetchData 함수를 반복해서 호출하는 인터벌을 설정합니다.
    const intervalId = setInterval(fetchData, 1000);

    // 3. (가장 중요!) 컴포넌트가 언마운트될 때(사라질 때) 인터벌을 정리(clean up)합니다.
    // 이 부분이 없으면 컴포넌트가 사라져도 백그라운드에서 계속 API를 호출하여 메모리 누수가 발생합니다.
    return () => {
      clearInterval(intervalId);
    };
  }, []); // 빈 배열을 전달하여 이 effect가 마운트 시 한 번만 실행되도록 설정

  if (loading) return <div>데이터를 불러오는 중입니다...</div>;
  if (error) return <div>에러가 발생했습니다: {error.message}</div>;

  return (
    <div className="App">
      <h1>📈 오늘의 시장 현황</h1>
      {marketData && (
        <>
          {/* 첫 번째 테이블: 체결 정보 */}
          <DataTable title="실시간 체결 정보" data={marketData.df2} />
          
          {/* 두 번째 테이블: 프로그램 매매 현황 */}
          <DataTable title="프로그램 매매 현황" data={marketData.df1} />
        </>
      )}
    </div>
  );
}

export default App;