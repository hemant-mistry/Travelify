import React from "react";
import { Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

const PieChart = ({ data, component_code }) => {
    let chartData = {};

    try {
      const generateChartData = new Function('data', `
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
    <div className="chart-container">
      <Pie data={chartData} />
    </div>
  );
};

export default PieChart;
