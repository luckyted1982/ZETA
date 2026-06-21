import React, { useEffect, useState } from 'react'

/**
 * 雷达图组件（原生SVG实现）
 * 展示8维度评测结果，带动画效果
 */
function RadarChart({ dimensions, scores, benchmarkScores }) {
  const [animatedScores, setAnimatedScores] = useState(scores.map(() => 0))
  const size = 400
  const center = size / 2
  const radius = 140
  const levels = 5
  const angleSlice = (Math.PI * 2) / dimensions.length

  // 动画效果：分数从0递增到目标值
  useEffect(() => {
    const duration = 1500
    const startTime = Date.now()

    const animate = () => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3) // easeOutCubic

      setAnimatedScores(scores.map(s => s * eased))

      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }

    requestAnimationFrame(animate)
  }, [scores])

  // 计算雷达图顶点坐标
  const getCoordinates = (value, index, maxValue = 100) => {
    const angle = index * angleSlice - Math.PI / 2
    const r = (value / maxValue) * radius
    return {
      x: center + r * Math.cos(angle),
      y: center + r * Math.sin(angle),
    }
  }

  // 生成网格多边形
  const gridPolygons = []
  for (let i = 1; i <= levels; i++) {
    const levelValue = (100 / levels) * i
    const points = dimensions.map((_, index) => {
      const coords = getCoordinates(levelValue, index)
      return `${coords.x},${coords.y}`
    }).join(' ')
    gridPolygons.push(
      <polygon
        key={i}
        points={points}
        fill="none"
        stroke="#e5e7eb"
        strokeWidth="1"
      />
    )
  }

  // 生成轴线
  const axes = dimensions.map((_, index) => {
    const endCoords = getCoordinates(100, index)
    return (
      <line
        key={index}
        x1={center}
        y1={center}
        x2={endCoords.x}
        y2={endCoords.y}
        stroke="#e5e7eb"
        strokeWidth="1"
      />
    )
  })

  // 生成数据区域（企业评分）
  const dataPoints = dimensions.map((_, index) => {
    const coords = getCoordinates(animatedScores[index], index)
    return `${coords.x},${coords.y}`
  }).join(' ')

  // 生成基准区域（行业平均）
  const benchmarkPoints = benchmarkScores
    ? dimensions.map((_, index) => {
        const coords = getCoordinates(benchmarkScores[index] || 50, index)
        return `${coords.x},${coords.y}`
      }).join(' ')
    : null

  // 生成标签
  const labels = dimensions.map((dim, index) => {
    const labelCoords = getCoordinates(115, index)
    return (
      <text
        key={index}
        x={labelCoords.x}
        y={labelCoords.y}
        textAnchor="middle"
        dominantBaseline="middle"
        className="text-xs font-medium fill-gray-600"
      >
        {dim}
      </text>
    )
  })

  // 生成数值点
  const dots = dimensions.map((_, index) => {
    const coords = getCoordinates(animatedScores[index], index)
    return (
      <circle
        key={index}
        cx={coords.x}
        cy={coords.y}
        r="4"
        fill="#7B6D8D"
        stroke="white"
        strokeWidth="2"
      />
    )
  })

  return (
    <div className="flex flex-col items-center">
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="radar-animate"
      >
        {/* 背景网格 */}
        {gridPolygons}

        {/* 轴线 */}
        {axes}

        {/* 基准区域（行业平均） */}
        {benchmarkPoints && (
          <polygon
            points={benchmarkPoints}
            fill="rgba(245, 158, 11, 0.1)"
            stroke="#F59E0B"
            strokeWidth="2"
            strokeDasharray="5,5"
          />
        )}

        {/* 数据区域（企业评分） */}
        <polygon
          points={dataPoints}
          fill="rgba(123, 109, 141, 0.2)"
          stroke="#7B6D8D"
          strokeWidth="2"
        />

        {/* 数据点 */}
        {dots}

        {/* 维度标签 */}
        {labels}
      </svg>

      {/* 图例 */}
      <div className="flex gap-6 mt-4">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-primary/30 border-2 border-primary rounded" />
          <span className="text-sm text-gray-600">企业评分</span>
        </div>
        {benchmarkScores && (
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-accent/20 border-2 border-accent border-dashed rounded" />
            <span className="text-sm text-gray-600">行业基准</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default RadarChart
