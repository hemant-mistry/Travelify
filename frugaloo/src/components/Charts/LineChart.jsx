import React from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const truncateLabel = (label, maxLength = 20) => {
  return label.length > maxLength ? `${label.slice(0, maxLength)}...` : label;
};


const LineChart = ({ data, component_code }) => {
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
      <Line data={chartData} />
    </div>
  );
};

export default LineChart;
