<template>
  <div class="chart-container">
    <canvas ref="canvas"></canvas>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default {
  name: 'LineChart',
  
  props: {
    chartData: {
      type: Object,
      required: true
    },
    chartOptions: {
      type: Object,
      default: () => ({})
    },
    height: {
      type: Number,
      default: 200
    }
  },
  
  data() {
    return {
      chart: null
    };
  },
  
  watch: {
    chartData: {
      handler() {
        this.updateChart();
      },
      deep: true
    },
    chartOptions: {
      handler() {
        this.updateChart();
      },
      deep: true
    }
  },
  
  mounted() {
    this.createChart();
  },
  
  beforeDestroy() {
    if (this.chart) {
      this.chart.destroy();
    }
  },
  
  methods: {
    createChart() {
      const canvas = this.$refs.canvas;
      if (!canvas) return;
      
      // Set canvas height
      canvas.height = this.height;
      
      // Create chart
      this.chart = new Chart(canvas, {
        type: 'line',
        data: this.chartData,
        options: this.getChartOptions()
      });
    },
    
    updateChart() {
      if (!this.chart) {
        this.createChart();
        return;
      }
      
      this.chart.data = this.chartData;
      this.chart.options = this.getChartOptions();
      this.chart.update();
    },
    
    getChartOptions() {
      // Default options
      const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 0 // Disable animation for better performance
        },
        scales: {
          x: {
            grid: {
              display: false
            }
          },
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(200, 200, 200, 0.1)'
            }
          }
        },
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            mode: 'index',
            intersect: false
          }
        }
      };
      
      // Merge with provided options
      return {
        ...defaultOptions,
        ...this.chartOptions
      };
    }
  }
};
</script>

<style scoped>
.chart-container {
  position: relative;
  width: 100%;
  height: 100%;
}
</style>
