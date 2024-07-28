import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const BarChart = ({ data, component_code }) => {
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
      <Bar data={chartData} />
    </div>
  );
};

export default BarChart;
