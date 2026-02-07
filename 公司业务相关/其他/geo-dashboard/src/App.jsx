import React, { useState, useMemo } from "react";
import { Upload, Table, Tag, Empty, message } from "antd";
import {
  UploadOutlined,
  ThunderboltOutlined,
  TrophyOutlined,
  AimOutlined,
  DatabaseOutlined,
  StarOutlined,
  LinkOutlined,
} from "@ant-design/icons";
import ReactECharts from "echarts-for-react";
import {
  parseExcel,
  calculateKPIs,
  getPlatformStats,
  getTrendData,
  getKeywordTypeStats,
  getExposeTypeStats,
} from "./utils/dataParser";

// 示例数据
const DEMO_DATA = [
  {
    key: 0,
    date: "2026-01-25",
    platform: "豆包",
    keyword: "50万纯电轿车推荐",
    keywordType: "场景词",
    isExposed: true,
    position: 2,
    exposeType: "推荐型",
    isWin: "否",
    content: "智己LS9续航超700km",
    screenshot: "",
  },
  {
    key: 1,
    date: "2026-01-25",
    platform: "DeepSeek",
    keyword: "智己LS9怎么样",
    keywordType: "品牌词",
    isExposed: true,
    position: 1,
    exposeType: "首选推荐",
    isWin: "无竞品",
    content: "LS9综合实力出众",
    screenshot: "",
  },
  {
    key: 2,
    date: "2026-01-25",
    platform: "文心一言",
    keyword: "家用大空间电车",
    keywordType: "场景词",
    isExposed: false,
    position: 0,
    exposeType: "",
    isWin: "",
    content: "",
    screenshot: "",
  },
  {
    key: 3,
    date: "2026-01-26",
    platform: "豆包",
    keyword: "智驾最好的车",
    keywordType: "痛点词",
    isExposed: true,
    position: 3,
    exposeType: "列举型",
    isWin: "是",
    content: "智己LS9智驾领先",
    screenshot: "",
  },
  {
    key: 4,
    date: "2026-01-26",
    platform: "通义千问",
    keyword: "LS9对比ET7",
    keywordType: "对比词",
    isExposed: true,
    position: 1,
    exposeType: "首选推荐",
    isWin: "是",
    content: "综合对比LS9更优",
    screenshot: "",
  },
  {
    key: 5,
    date: "2026-01-26",
    platform: "DeepSeek",
    keyword: "续航长的电车",
    keywordType: "痛点词",
    isExposed: true,
    position: 2,
    exposeType: "推荐型",
    isWin: "否",
    content: "LS9续航700+km",
    screenshot: "",
  },
  {
    key: 6,
    date: "2026-01-27",
    platform: "文心一言",
    keyword: "智己LS9续航",
    keywordType: "品牌词",
    isExposed: true,
    position: 1,
    exposeType: "首选推荐",
    isWin: "无竞品",
    content: "官方续航738km",
    screenshot: "",
  },
  {
    key: 7,
    date: "2026-01-27",
    platform: "豆包",
    keyword: "40万电车怎么选",
    keywordType: "场景词",
    isExposed: true,
    position: 2,
    exposeType: "推荐型",
    isWin: "是",
    content: "推荐智己LS9",
    screenshot: "",
  },
  {
    key: 8,
    date: "2026-01-28",
    platform: "通义千问",
    keyword: "智能驾驶好的车",
    keywordType: "痛点词",
    isExposed: true,
    position: 1,
    exposeType: "首选推荐",
    isWin: "是",
    content: "LS9智驾第一梯队",
    screenshot: "",
  },
  {
    key: 9,
    date: "2026-01-28",
    platform: "DeepSeek",
    keyword: "纯电轿车推荐",
    keywordType: "场景词",
    isExposed: false,
    position: 0,
    exposeType: "",
    isWin: "",
    content: "",
    screenshot: "",
  },
];

function App() {
  const [data, setData] = useState(DEMO_DATA);
  const [loading, setLoading] = useState(false);

  // 计算各项统计数据
  const kpis = useMemo(() => calculateKPIs(data), [data]);
  const platformStats = useMemo(() => getPlatformStats(data), [data]);
  const trendData = useMemo(() => getTrendData(data), [data]);
  const keywordStats = useMemo(() => getKeywordTypeStats(data), [data]);
  const exposeTypeStats = useMemo(() => getExposeTypeStats(data), [data]);

  // 处理文件上传
  const handleUpload = async (file) => {
    setLoading(true);
    try {
      const records = await parseExcel(file);
      setData(records);
      message.success(`成功导入 ${records.length} 条记录`);
    } catch (error) {
      message.error("文件解析失败，请检查格式");
      console.error(error);
    }
    setLoading(false);
    return false;
  };

  // 平台柱状图配置
  const platformChartOption = {
    tooltip: { trigger: "axis" },
    grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
    xAxis: {
      type: "category",
      data: platformStats.map((p) => p.platform),
      axisLabel: { color: "#94a3b8" },
      axisLine: { lineStyle: { color: "#334155" } },
    },
    yAxis: {
      type: "value",
      max: 100,
      axisLabel: { color: "#94a3b8", formatter: "{value}%" },
      splitLine: { lineStyle: { color: "#1e293b" } },
    },
    series: [
      {
        name: "露出率",
        type: "bar",
        data: platformStats.map((p) => p.rate),
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: "#00d4ff" },
              { offset: 1, color: "#6366f1" },
            ],
          },
        },
        label: {
          show: true,
          position: "top",
          color: "#f8fafc",
          formatter: "{c}%",
        },
      },
    ],
  };

  // 趋势折线图配置
  const trendChartOption = {
    tooltip: { trigger: "axis" },
    grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
    xAxis: {
      type: "category",
      data: trendData.map((t) => t.date),
      axisLabel: { color: "#94a3b8" },
      axisLine: { lineStyle: { color: "#334155" } },
    },
    yAxis: {
      type: "value",
      max: 100,
      axisLabel: { color: "#94a3b8", formatter: "{value}%" },
      splitLine: { lineStyle: { color: "#1e293b" } },
    },
    series: [
      {
        name: "露出率",
        type: "line",
        data: trendData.map((t) => t.rate),
        smooth: true,
        symbol: "circle",
        symbolSize: 8,
        lineStyle: { width: 3, color: "#00d4ff" },
        itemStyle: { color: "#00d4ff", borderColor: "#fff", borderWidth: 2 },
        areaStyle: {
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: "rgba(0,212,255,0.3)" },
              { offset: 1, color: "rgba(0,212,255,0)" },
            ],
          },
        },
      },
    ],
  };

  // 关键词雷达图配置
  const radarChartOption = {
    tooltip: {},
    radar: {
      indicator: keywordStats.map((k) => ({ name: k.type, max: 100 })),
      axisLine: { lineStyle: { color: "#334155" } },
      splitLine: { lineStyle: { color: "#1e293b" } },
      splitArea: {
        areaStyle: { color: ["rgba(0,212,255,0.02)", "rgba(0,212,255,0.05)"] },
      },
      axisName: { color: "#94a3b8" },
    },
    series: [
      {
        type: "radar",
        data: [
          {
            value: keywordStats.map((k) => k.rate),
            name: "露出率",
            areaStyle: { color: "rgba(0,212,255,0.3)" },
            lineStyle: { color: "#00d4ff", width: 2 },
            itemStyle: { color: "#00d4ff" },
          },
        ],
      },
    ],
  };

  // 露出类型饼图配置
  const pieChartOption = {
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    legend: { bottom: 0, textStyle: { color: "#94a3b8" } },
    series: [
      {
        type: "pie",
        radius: ["40%", "70%"],
        center: ["50%", "45%"],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 8, borderColor: "#1a2332", borderWidth: 2 },
        label: { show: true, color: "#f8fafc" },
        data: exposeTypeStats.map((item, i) => ({
          ...item,
          itemStyle: {
            color: ["#00d4ff", "#6366f1", "#10b981", "#f59e0b"][i % 4],
          },
        })),
      },
    ],
  };

  // 表格列定义
  const columns = [
    { title: "日期", dataIndex: "date", key: "date", width: 110 },
    {
      title: "平台",
      dataIndex: "platform",
      key: "platform",
      width: 100,
      render: (v) => <Tag color="blue">{v}</Tag>,
    },
    { title: "关键词", dataIndex: "keyword", key: "keyword", ellipsis: true },
    { title: "类型", dataIndex: "keywordType", key: "keywordType", width: 80 },
    {
      title: "露出",
      dataIndex: "isExposed",
      key: "isExposed",
      width: 70,
      render: (v) =>
        v ? <Tag color="success">是</Tag> : <Tag color="default">否</Tag>,
    },
    {
      title: "位置",
      dataIndex: "position",
      key: "position",
      width: 70,
      render: (v) =>
        v > 0 ? (
          <span style={{ color: v <= 3 ? "#10b981" : "#f8fafc" }}>{v}</span>
        ) : (
          "-"
        ),
    },
    {
      title: "类型",
      dataIndex: "exposeType",
      key: "exposeType",
      width: 100,
      render: (v) =>
        v ? <Tag color={v === "首选推荐" ? "gold" : "default"}>{v}</Tag> : "-",
    },
    {
      title: "胜出",
      dataIndex: "isWin",
      key: "isWin",
      width: 80,
      render: (v) =>
        v === "是" ? (
          <Tag color="success">是</Tag>
        ) : v === "否" ? (
          <Tag color="error">否</Tag>
        ) : v ? (
          <Tag>{v}</Tag>
        ) : (
          "-"
        ),
    },
    {
      title: "露出原文",
      dataIndex: "content",
      key: "content",
      width: 200,
      ellipsis: true,
      render: (v) => v || "-",
    },
    {
      title: "证据",
      dataIndex: "screenshot",
      key: "screenshot",
      width: 80,
      render: (v) =>
        v ? (
          <a
            href={v}
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: "#00d4ff" }}
          >
            <LinkOutlined /> 查看
          </a>
        ) : (
          "-"
        ),
    },
  ];

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="dashboard-header">
        <div>
          <h1 className="dashboard-title">智己LS9 GEO效果监测看板</h1>
          <p className="dashboard-subtitle">
            Generative Engine Optimization Dashboard
          </p>
        </div>
        <div className="upload-section">
          <Upload
            beforeUpload={handleUpload}
            showUploadList={false}
            accept=".xlsx,.xls"
          >
            <button className="upload-btn">
              <UploadOutlined /> 上传Excel数据
            </button>
          </Upload>
        </div>
      </header>

      {/* Main Content */}
      <main className="dashboard-content">
        {/* KPI Cards - 6个核心指标 */}
        <div className="kpi-row">
          <div className="kpi-card animate-fade-in">
            <div className="kpi-label">
              <ThunderboltOutlined /> 露出率
            </div>
            <div className="kpi-value accent">{kpis.exposureRate}%</div>
            <div className="kpi-sub">
              露出 {kpis.exposedCount} / 检测 {kpis.totalCount}
            </div>
          </div>
          <div className="kpi-card animate-fade-in">
            <div className="kpi-label">
              <AimOutlined /> 平均排名
            </div>
            <div className="kpi-value">{kpis.avgPosition || "-"}</div>
            <div className="kpi-sub">TOP3占比 {kpis.topThreeRate}%</div>
          </div>
          <div className="kpi-card animate-fade-in">
            <div className="kpi-label">
              <TrophyOutlined /> 竞品胜率
            </div>
            <div className="kpi-value accent">{kpis.winRate}%</div>
            <div className="kpi-sub">有竞品场景下的胜出比例</div>
          </div>
          <div className="kpi-card animate-fade-in">
            <div className="kpi-label">
              <StarOutlined /> 首选推荐率
            </div>
            <div className="kpi-value accent">{kpis.firstChoiceRate}%</div>
            <div className="kpi-sub">被AI首选推荐的比例</div>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="charts-grid">
          <div className="chart-card">
            <h3 className="chart-title">分平台露出率</h3>
            <ReactECharts
              option={platformChartOption}
              style={{ height: 280 }}
            />
          </div>
          <div className="chart-card">
            <h3 className="chart-title">露出率趋势</h3>
            <ReactECharts option={trendChartOption} style={{ height: 280 }} />
          </div>
          <div className="chart-card">
            <h3 className="chart-title">关键词类型覆盖</h3>
            <ReactECharts option={radarChartOption} style={{ height: 280 }} />
          </div>
          <div className="chart-card">
            <h3 className="chart-title">露出类型分布</h3>
            <ReactECharts option={pieChartOption} style={{ height: 280 }} />
          </div>
        </div>

        {/* Data Table */}
        <div className="table-section">
          <div className="table-header">
            <h3 className="table-title">
              <DatabaseOutlined /> 检测明细
            </h3>
          </div>
          <Table
            columns={columns}
            dataSource={data}
            pagination={{ pageSize: 10 }}
            size="middle"
            loading={loading}
          />
        </div>
      </main>
    </div>
  );
}

export default App;
