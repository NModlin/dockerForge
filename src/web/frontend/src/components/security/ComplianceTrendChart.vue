<template>
  <div class="compliance-trend-chart">
    <v-chart :option="chartOption" autoresize />
  </div>
</template>

<script>
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  ToolboxComponent
} from 'echarts/components';
import VChart from 'vue-echarts';
import { format, parseISO } from 'date-fns';

// Register ECharts components
use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  ToolboxComponent
]);

export default {
  name: 'ComplianceTrendChart',
  
  components: {
    VChart
  },
  
  props: {
    data: {
      type: Array,
      required: true
    },
    timeRange: {
      type: String,
      default: '30d'
    }
  },
  
  computed: {
    chartOption() {
      // Process data for chart
      const dates = this.data.map(item => format(parseISO(item.timestamp), 'yyyy-MM-dd HH:mm'));
      const complianceScores = this.data.map(item => item.compliance_score);
      
      // Calculate visible data range based on time range
      let startIndex = 0;
      if (this.data.length > 30) {
        switch (this.timeRange) {
          case '7d':
            startIndex = this.data.length - 7;
            break;
          case '30d':
            startIndex = this.data.length - 30;
            break;
          case '90d':
            startIndex = this.data.length - 90;
            break;
          case '180d':
            startIndex = this.data.length - 180;
            break;
          default:
            startIndex = 0;
        }
        startIndex = Math.max(0, startIndex);
      }
      
      return {
        title: {
          text: 'Compliance Score Trend',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          formatter: function(params) {
            const date = params[0].axisValue;
            const score = params[0].data;
            return `${date}<br/>Compliance Score: <strong>${score}%</strong>`;
          }
        },
        toolbox: {
          feature: {
            saveAsImage: { title: 'Save as Image' }
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '10%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: dates,
          axisLabel: {
            formatter: function(value) {
              return format(parseISO(value), 'MMM dd');
            }
          }
        },
        yAxis: {
          type: 'value',
          min: 0,
          max: 100,
          axisLabel: {
            formatter: '{value}%'
          }
        },
        series: [
          {
            name: 'Compliance Score',
            type: 'line',
            data: complianceScores,
            markLine: {
              silent: true,
              lineStyle: {
                color: '#5cb85c'
              },
              data: [
                {
                  yAxis: 90,
                  name: 'Compliant'
                }
              ]
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  {
                    offset: 0,
                    color: 'rgba(58, 71, 212, 0.3)'
                  },
                  {
                    offset: 1,
                    color: 'rgba(58, 71, 212, 0.1)'
                  }
                ]
              }
            },
            itemStyle: {
              color: '#3a47d4'
            },
            lineStyle: {
              width: 3
            }
          }
        ],
        dataZoom: [
          {
            type: 'inside',
            start: (startIndex / this.data.length) * 100,
            end: 100
          },
          {
            start: (startIndex / this.data.length) * 100,
            end: 100
          }
        ]
      };
    }
  }
};
</script>

<style scoped>
.compliance-trend-chart {
  width: 100%;
  height: 100%;
}
</style>
