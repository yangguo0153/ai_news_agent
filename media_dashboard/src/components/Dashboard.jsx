import React, { useMemo } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from "chart.js";
import { Bar, Doughnut } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
);

const Dashboard = ({ data, filters, onFilterChange, filteredData }) => {
  // --- Stats Calculation ---
  const stats = useMemo(() => {
    const totalReads = filteredData.reduce((acc, item) => acc + item.reads, 0);
    const totalInteractions = filteredData.reduce(
      (acc, item) => acc + item.interactions,
      0,
    );
    const totalShares = 0; // Not available in data
    const totalCollects = 0; // Not available in data
    return { totalReads, totalInteractions, totalShares, totalCollects };
  }, [filteredData]);

  // --- Chart Data Preparation ---
  const effectivenessData = {
    labels: ["阅读量", "评论量", "转发量", "收藏量"],
    datasets: [
      {
        label: "效果数",
        data: [
          stats.totalReads,
          stats.totalInteractions,
          stats.totalShares,
          stats.totalCollects,
        ],
        backgroundColor: [
          "#5B9BD5", // Blue for reads
          "#ED7D31", // Orange for comments (interactions)
          "#A5A5A5", // Gray for shares
          "#FFC000", // Yellow for collects
        ],
        barThickness: 60,
      },
    ],
  };

  const effectivenessOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: "效果数",
        font: { size: 18 },
      },
      tooltip: {
        enabled: true,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        // Optional: format large numbers on Y axis if needed
      },
      x: {
        display: false, // Hide X-axis labels to avoid duplication/overlap with custom overlay
        grid: {
          display: false,
        },
      },
    },
  };

  const platformStats = useMemo(() => {
    const counts = {};
    filteredData.forEach((item) => {
      counts[item.platform] = (counts[item.platform] || 0) + 1;
    });

    // Sort by count descending
    const sortedDetails = Object.entries(counts).sort((a, b) => b[1] - a[1]);

    // Top 10 Logic
    let top10 = sortedDetails;
    let othersCount = 0;

    if (sortedDetails.length > 10) {
      top10 = sortedDetails.slice(0, 10);
      const others = sortedDetails.slice(10);
      othersCount = others.reduce((acc, curr) => acc + curr[1], 0);
    }

    const finalLabels = top10.map((d) => d[0]);
    const finalData = top10.map((d) => d[1]);

    if (othersCount > 0) {
      finalLabels.push("其他");
      finalData.push(othersCount);
    }

    return { labels: finalLabels, data: finalData };
  }, [filteredData]);

  const platformData = {
    labels: platformStats.labels,
    datasets: [
      {
        data: platformStats.data,
        backgroundColor: [
          "#62a7b7", // Teal
          "#2c3e50", // Dark Blue
          "#e74c3c", // Red
          "#f1c40f", // Yellow
          "#8e44ad", // Purple
          "#16a085", // Green
          "#2ecc71",
          "#3498db",
          "#e67e22",
          "#95a5a6",
          "#bdc3c7", // Grey for others
        ],
        borderWidth: 1,
      },
    ],
  };

  const platformOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "right", // Legend on right
        labels: {
          boxWidth: 12,
          font: { size: 10 }, // Smaller font to avoid blocking
        },
      },
      title: {
        display: true,
        text: "平台占比",
        font: { size: 18 },
        padding: { bottom: 20 },
      },
    },
    layout: {
      // padding: { right: 20 } // Add padding if needed
    },
  };

  // --- Unique Filter Options ---
  const uniqueProjects = useMemo(
    () => [...new Set(data.map((d) => d.project))],
    [data],
  );
  const uniqueMedias = useMemo(
    () => [...new Set(data.map((d) => d.media))],
    [data],
  );
  const uniquePlatforms = useMemo(
    () => [...new Set(data.map((d) => d.platform))],
    [data],
  );

  return (
    <div className="dashboard-container">
      {/* Header / Brand */}
      <header className="top-nav">
        <div className="nav-left">
          <span className="nav-item active">首页</span>
          <span className="nav-item">媒体</span>
          <span className="nav-item">平台账号</span>
          <span className="nav-item active-red">合作列表</span>
          <span className="nav-item">品牌动态</span>
        </div>
        <div className="nav-right">
          <div className="user-avatar"></div>
        </div>
      </header>

      {/* Filter Bar */}
      <div className="filter-card">
        <div className="filter-group">
          <label>项目名：</label>
          <span className="project-name">
            {uniqueProjects[0] || "所有项目"}
          </span>
          {/* Simplifying project selection as usually it's one project per file in this context, but expandable */}
        </div>
        <div className="filter-group">
          <label>媒体名：</label>
          <select
            value={filters.media}
            onChange={(e) => onFilterChange("media", e.target.value)}
          >
            <option value="">请选择</option>
            {uniqueMedias.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </div>
        <div className="filter-group">
          <label>平台：</label>
          <select
            value={filters.platform}
            onChange={(e) => onFilterChange("platform", e.target.value)}
          >
            <option value="">请选择</option>
            {uniquePlatforms.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </div>
        <div className="filter-group">
          <label>效果维度：</label>
          <select>
            <option>请选择</option>
          </select>
        </div>
      </div>

      {/* Charts Section */}
      <div className="charts-card">
        <div className="chart-container">
          <Bar data={effectivenessData} options={effectivenessOptions} />
          <div className="chart-overlay-stats">
            <div>
              <span>{stats.totalReads}</span> 阅读量
            </div>
            <div>
              <span>{stats.totalInteractions}</span> 评论量
            </div>
            <div>
              <span>0</span> 转发量
            </div>
            <div>
              <span>0</span> 收藏量
            </div>
          </div>
        </div>
        <div className="chart-container">
          <Doughnut data={platformData} options={platformOptions} />
        </div>
      </div>

      {/* Data Table */}
      <div className="table-card">
        <div className="table-header-actions">
          <button className="btn-export">导出</button>
        </div>
        <table>
          <thead>
            <tr>
              <th>序号</th>
              <th>媒体</th>
              <th>平台</th>
              <th>平台账号</th>
              <th>推荐点位</th>
              <th>标题</th>
              <th>
                阅读量 <span className="sort-icon">⇅</span>
              </th>
              <th>
                评论量 <span className="sort-icon">⇅</span>
              </th>
              <th>
                转发量 <span className="sort-icon">⇅</span>
              </th>
              <th>
                收藏量 <span className="sort-icon">⇅</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {filteredData.map((item) => (
              <tr key={item.id}>
                <td>{item.id}</td>
                <td>{item.media}</td>
                <td>{item.platform}</td>
                <td>{item.account}</td>
                <td>{item.position}</td>
                <td>
                  <a
                    href={item.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="title-link"
                  >
                    {item.title}
                  </a>
                </td>
                <td>
                  {item.reads > 10000
                    ? (item.reads / 10000).toFixed(2) + "万"
                    : item.reads}
                </td>
                <td>{item.interactions}</td>
                <td>-</td>
                <td>-</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Dashboard;
