import React from "react";
import { Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

const truncateLabel = (label, maxLength = 20) => {
  return label.length > maxLength ? `${label.slice(0, maxLength)}...` : label;
};

const PieChart = ({ data, component_code }) => {
    let chartData = {};

    try {
      const generateChartData = new Function('data', `
        const truncateLabel = ${truncateLabel.toString()};
        return {
          ${component_code}
        };
      `);
      chartData = generateChartData(data);
    } catch (error) {
      console.error("Error generating chart data:", error);
    }
  
    console.log("Constructed chartData:", chartData);

  return (
    <div className="chart-container max-w-xs sm:min-w-sm md:min-w-md lg:min-w-lg">
      <Pie data={chartData} />
    </div>
  );
};

export default PieChart;
