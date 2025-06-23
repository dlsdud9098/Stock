import React from 'react';
import './App.css'; // App.css 스타일을 그대로 사용

// 값에 따라 'positive', 'negative' 클래스 이름을 반환하는 함수
const getValueClassName = (value) => {
  if (typeof value === 'string') {
    if (value.startsWith('+')) return 'positive';
    if (value.startsWith('-')) return 'negative';
  }
  if (typeof value === 'number') {
    if (value > 0) return 'positive';
    if (value < 0) return 'negative';
  }
  return '';
};

// title과 data를 props로 받는 테이블 컴포넌트
function DataTable({ title, data }) {
  // 데이터가 없거나 비어있으면 아무것도 렌더링하지 않음
  if (!data || data.length === 0) {
    return <div>{title} 데이터가 없습니다.</div>;
  }

  // 테이블 헤더를 동적으로 생성 (데이터의 첫 번째 행의 키들을 사용)
  const headers = Object.keys(data[0]);

  return (
    <div className="table-container">
      <h2>{title}</h2>
      <table>
        <thead>
          <tr>
            {headers.map(header => <th key={header}>{header}</th>)}
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr key={index}>
              {headers.map(header => {
                const value = row[header];
                const isNumeric = typeof value === 'number';
                return (
                  <td key={header} className={`${isNumeric ? 'numeric' : ''} ${getValueClassName(value)}`}>
                    {isNumeric ? value.toLocaleString() : value}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default DataTable;