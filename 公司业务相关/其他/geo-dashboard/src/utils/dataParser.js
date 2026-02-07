/**
 * GEO数据解析器 - 解析Excel并计算KPI
 */
import * as XLSX from "xlsx";

// 字段映射（对应Excel列）
const FIELD_MAP = {
  date: "检测日期",
  platform: "AI平台",
  keyword: "查询关键词",
  keywordType: "关键词类型",
  isExposed: "是否露出",
  position: "露出位置",
  exposeType: "露出类型",
  isWin: "我方胜出",
  content: "露出原文",
  screenshot: "证据截图",
};

/**
 * 解析Excel文件
 */
export function parseExcel(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: "array" });
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        const jsonData = XLSX.utils.sheet_to_json(worksheet);

        // 转换数据格式
        const records = jsonData.map((row, index) => ({
          key: index,
          date: formatDate(row[FIELD_MAP.date]),
          platform: row[FIELD_MAP.platform] || "",
          keyword: row[FIELD_MAP.keyword] || "",
          keywordType: row[FIELD_MAP.keywordType] || "",
          isExposed: row[FIELD_MAP.isExposed] === "是",
          position: parseInt(row[FIELD_MAP.position]) || 0,
          exposeType: row[FIELD_MAP.exposeType] || "",
          isWin: row[FIELD_MAP.isWin] || "",
          content: row[FIELD_MAP.content] || "",
          screenshot: row[FIELD_MAP.screenshot] || "",
        }));

        resolve(records);
      } catch (error) {
        reject(error);
      }
    };
    reader.onerror = reject;
    reader.readAsArrayBuffer(file);
  });
}

/**
 * 格式化日期
 */
function formatDate(value) {
  if (!value) return "";
  if (typeof value === "number") {
    // Excel日期序列号转换
    const date = XLSX.SSF.parse_date_code(value);
    return `${date.y}-${String(date.m).padStart(2, "0")}-${String(date.d).padStart(2, "0")}`;
  }
  return String(value);
}

/**
 * 计算核心KPI
 */
export function calculateKPIs(records) {
  if (!records || records.length === 0) {
    return {
      totalCount: 0,
      exposureRate: 0,
      avgPosition: 0,
      winRate: 0,
      exposedCount: 0,
      topThreeRate: 0,
      firstChoiceRate: 0,
    };
  }

  const totalCount = records.length;
  const exposedRecords = records.filter((r) => r.isExposed);
  const exposedCount = exposedRecords.length;

  // 露出率
  const exposureRate = ((exposedCount / totalCount) * 100).toFixed(1);

  // 平均排名（只计算露出的记录）
  const positionsWithValue = exposedRecords.filter((r) => r.position > 0);
  const avgPosition =
    positionsWithValue.length > 0
      ? (
          positionsWithValue.reduce((sum, r) => sum + r.position, 0) /
          positionsWithValue.length
        ).toFixed(1)
      : 0;

  // TOP3占比
  const topThreeCount = exposedRecords.filter(
    (r) => r.position > 0 && r.position <= 3,
  ).length;
  const topThreeRate =
    exposedCount > 0 ? ((topThreeCount / exposedCount) * 100).toFixed(1) : 0;

  // 竞品胜率（排除"无竞品"的记录）
  const competitiveRecords = records.filter(
    (r) => r.isWin && r.isWin !== "无竞品",
  );
  const winCount = competitiveRecords.filter((r) => r.isWin === "是").length;
  const winRate =
    competitiveRecords.length > 0
      ? ((winCount / competitiveRecords.length) * 100).toFixed(1)
      : 0;

  // 首选推荐率（露出类型为"首选推荐"的比例）
  const firstChoiceCount = exposedRecords.filter(
    (r) => r.exposeType === "首选推荐",
  ).length;
  const firstChoiceRate =
    totalCount > 0 ? ((firstChoiceCount / totalCount) * 100).toFixed(1) : 0;

  return {
    totalCount,
    exposedCount,
    exposureRate,
    avgPosition,
    topThreeRate,
    winRate,
    firstChoiceRate,
  };
}

/**
 * 按平台统计露出率
 */
export function getPlatformStats(records) {
  const platforms = ["豆包", "文心一言", "DeepSeek", "通义千问"];

  return platforms
    .map((platform) => {
      const platformRecords = records.filter((r) => r.platform === platform);
      const exposedCount = platformRecords.filter((r) => r.isExposed).length;
      const rate =
        platformRecords.length > 0
          ? ((exposedCount / platformRecords.length) * 100).toFixed(1)
          : 0;

      return {
        platform,
        total: platformRecords.length,
        exposed: exposedCount,
        rate: parseFloat(rate),
      };
    })
    .filter((p) => p.total > 0);
}

/**
 * 按日期统计趋势
 */
export function getTrendData(records) {
  const dateMap = new Map();

  records.forEach((record) => {
    if (!record.date) return;

    if (!dateMap.has(record.date)) {
      dateMap.set(record.date, { total: 0, exposed: 0 });
    }

    const stats = dateMap.get(record.date);
    stats.total++;
    if (record.isExposed) stats.exposed++;
  });

  return Array.from(dateMap.entries())
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(([date, stats]) => ({
      date,
      rate:
        stats.total > 0
          ? parseFloat(((stats.exposed / stats.total) * 100).toFixed(1))
          : 0,
      total: stats.total,
      exposed: stats.exposed,
    }));
}

/**
 * 按关键词类型统计
 */
export function getKeywordTypeStats(records) {
  const types = ["品牌词", "场景词", "对比词", "痛点词"];

  return types.map((type) => {
    const typeRecords = records.filter((r) => r.keywordType === type);
    const exposedCount = typeRecords.filter((r) => r.isExposed).length;
    const rate =
      typeRecords.length > 0
        ? parseFloat(((exposedCount / typeRecords.length) * 100).toFixed(1))
        : 0;

    return {
      type,
      total: typeRecords.length,
      exposed: exposedCount,
      rate,
    };
  });
}

/**
 * 按露出类型统计
 */
export function getExposeTypeStats(records) {
  const exposedRecords = records.filter((r) => r.isExposed && r.exposeType);
  const typeCount = {};

  exposedRecords.forEach((r) => {
    typeCount[r.exposeType] = (typeCount[r.exposeType] || 0) + 1;
  });

  return Object.entries(typeCount).map(([name, value]) => ({
    name,
    value,
  }));
}
