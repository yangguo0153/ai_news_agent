import { useState, useEffect, useMemo } from "react";
import Dashboard from "./components/Dashboard";
import "./index.css";

function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    media: "",
    platform: "",
  });

  useEffect(() => {
    fetch("/data.json")
      .then((res) => res.json())
      .then((jsonData) => {
        setData(jsonData);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load data", err);
        setLoading(false);
      });
  }, []);

  const filteredData = useMemo(() => {
    return data.filter((item) => {
      const matchMedia = filters.media ? item.media === filters.media : true;
      const matchPlatform = filters.platform
        ? item.platform === filters.platform
        : true;
      return matchMedia && matchPlatform;
    });
  }, [data, filters]);

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  if (loading) return <div className="loading">Loading Data...</div>;

  return (
    <div className="app">
      <Dashboard
        data={data}
        filters={filters}
        onFilterChange={handleFilterChange}
        filteredData={filteredData}
      />
    </div>
  );
}

export default App;
