<template>
  <div class="resource-compliance-chart">
    <v-chart :option="chartOption" autoresize />
  </div>
</template>

<script>
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components';
import VChart from 'vue-echarts';

// Register ECharts components
use([
  CanvasRenderer,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
]);

export default {
  name: 'ResourceComplianceChart',
  
  components: {
    VChart
  },
  
  props: {
    data: {
      type: Array,
      required: true
    }
  },
  
  computed: {
    chartOption() {
      // Process data for chart
      const resourceTypes = this.data.map(item => item.resource_type);
      const compliantData = this.data.map(item => item.compliant);
      const nonCompliantData = this.data.map(item => item.non_compliant);
      
      return {
        title: {
          text: 'Resource Type Compliance',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          formatter: function(params) {
            const resourceType = params[0].axisValue;
            const compliant = params[0].data;
            const nonCompliant = params[1].data;
            const total = compliant + nonCompliant;
            const complianceRate = total > 0 ? Math.round((compliant / total) * 100) : 0;
            
            return `${resourceType}<br/>` +
              `Compliant: <strong>${compliant}</strong><br/>` +
              `Non-Compliant: <strong>${nonCompliant}</strong><br/>` +
              `Compliance Rate: <strong>${complianceRate}%</strong>`;
          }
        },
        legend: {
          data: ['Compliant', 'Non-Compliant'],
          top: 'bottom'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: resourceTypes
        },
        yAxis: {
          type: 'value',
          name: 'Count'
        },
        series: [
          {
            name: 'Compliant',
            type: 'bar',
            stack: 'total',
            emphasis: {
              focus: 'series'
            },
            data: compliantData,
            itemStyle: {
              color: '#4caf50'
            }
          },
          {
            name: 'Non-Compliant',
            type: 'bar',
            stack: 'total',
            emphasis: {
              focus: 'series'
            },
            data: nonCompliantData,
            itemStyle: {
              color: '#f44336'
            }
          }
        ]
      };
    }
  }
};
</script>

<style scoped>
.resource-compliance-chart {
  width: 100%;
  height: 100%;
}
</style>
