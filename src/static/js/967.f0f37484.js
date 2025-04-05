"use strict";(self["webpackChunkdockerforge_web_ui"]=self["webpackChunkdockerforge_web_ui"]||[]).push([[967],{5967:function(e,t,a){a.r(t),a.d(t,{default:function(){return L}});var r=a(641),l=a(33);const s={class:"monitoring-dashboard"},o={key:0,class:"d-flex justify-center align-center my-5"},i={class:"text-h5"},n={class:"mt-2"},c={class:"text-h5"},u={class:"mt-2"},d={class:"text-h5"},m={class:"mt-2"},k={class:"text-h5"},_={class:"text-h5"},g={class:"text-h5"},h={class:"text-h5"},b={class:"text-caption"},f={class:"d-flex align-center"},v={class:"text-caption"},p={key:0},y={key:1},F={class:"d-flex mt-2"};function C(e,t,a,C,w,M){const x=(0,r.g2)("v-progress-circular"),W=(0,r.g2)("v-alert"),L=(0,r.g2)("v-icon"),A=(0,r.g2)("v-card-title"),D=(0,r.g2)("v-card-text"),R=(0,r.g2)("v-card"),U=(0,r.g2)("v-col"),S=(0,r.g2)("v-row"),T=(0,r.g2)("v-divider"),V=(0,r.g2)("v-spacer"),z=(0,r.g2)("v-btn"),X=(0,r.g2)("v-btn-toggle"),I=(0,r.g2)("router-link"),B=(0,r.g2)("v-progress-linear"),P=(0,r.g2)("v-data-table"),$=(0,r.g2)("v-chip"),N=(0,r.g2)("v-expansion-panel-header"),E=(0,r.g2)("v-expansion-panel-content"),H=(0,r.g2)("v-expansion-panel"),Q=(0,r.g2)("v-expansion-panels"),K=(0,r.g2)("v-tab"),Z=(0,r.g2)("v-tabs"),G=(0,r.g2)("v-tab-item"),O=(0,r.g2)("v-tabs-items"),j=(0,r.g2)("v-card-actions"),q=(0,r.g2)("v-dialog");return(0,r.uX)(),(0,r.CE)("div",s,[t[61]||(t[61]=(0,r.Lk)("h1",{class:"text-h4 mb-4"},"Monitoring Dashboard",-1)),w.loading?((0,r.uX)(),(0,r.CE)("div",o,[(0,r.bF)(x,{indeterminate:"",color:"primary"})])):w.error?((0,r.uX)(),(0,r.Wv)(W,{key:1,type:"error",class:"mb-4"},{default:(0,r.k6)((()=>[(0,r.eW)((0,l.v_)(w.error),1)])),_:1})):((0,r.uX)(),(0,r.CE)(r.FK,{key:2},[(0,r.bF)(S,null,{default:(0,r.k6)((()=>[(0,r.bF)(U,{cols:"12",md:"3"},{default:(0,r.k6)((()=>[(0,r.bF)(R,{class:"mb-4"},{default:(0,r.k6)((()=>[(0,r.bF)(A,{class:"headline"},{default:(0,r.k6)((()=>[(0,r.bF)(L,{left:"",color:"primary"},{default:(0,r.k6)((()=>t[7]||(t[7]=[(0,r.eW)("mdi-cpu-64-bit")]))),_:1}),t[8]||(t[8]=(0,r.eW)(" CPU Usage "))])),_:1}),(0,r.bF)(D,{class:"text-center"},{default:(0,r.k6)((()=>[(0,r.bF)(x,{rotate:-90,size:100,width:15,value:w.systemMetrics.cpu_usage,color:M.getResourceColor(w.systemMetrics.cpu_usage)},{default:(0,r.k6)((()=>[(0,r.Lk)("span",i,(0,l.v_)(w.systemMetrics.cpu_usage)+"%",1)])),_:1},8,["value","color"]),(0,r.Lk)("div",n,[(0,r.Lk)("small",null,(0,l.v_)(w.systemMetrics.cpu_cores)+" Cores",1)])])),_:1})])),_:1})])),_:1}),(0,r.bF)(U,{cols:"12",md:"3"},{default:(0,r.k6)((()=>[(0,r.bF)(R,{class:"mb-4"},{default:(0,r.k6)((()=>[(0,r.bF)(A,{class:"headline"},{default:(0,r.k6)((()=>[(0,r.bF)(L,{left:"",color:"green"},{default:(0,r.k6)((()=>t[9]||(t[9]=[(0,r.eW)("mdi-memory")]))),_:1}),t[10]||(t[10]=(0,r.eW)(" Memory Usage "))])),_:1}),(0,r.bF)(D,{class:"text-center"},{default:(0,r.k6)((()=>[(0,r.bF)(x,{rotate:-90,size:100,width:15,value:w.systemMetrics.memory_usage_percent,color:M.getResourceColor(w.systemMetrics.memory_usage_percent)},{default:(0,r.k6)((()=>[(0,r.Lk)("span",c,(0,l.v_)(w.systemMetrics.memory_usage_percent)+"%",1)])),_:1},8,["value","color"]),(0,r.Lk)("div",u,[(0,r.Lk)("small",null,(0,l.v_)(M.formatSize(w.systemMetrics.memory_used))+" / "+(0,l.v_)(M.formatSize(w.systemMetrics.memory_total)),1)])])),_:1})])),_:1})])),_:1}),(0,r.bF)(U,{cols:"12",md:"3"},{default:(0,r.k6)((()=>[(0,r.bF)(R,{class:"mb-4"},{default:(0,r.k6)((()=>[(0,r.bF)(A,{class:"headline"},{default:(0,r.k6)((()=>[(0,r.bF)(L,{left:"",color:"blue"},{default:(0,r.k6)((()=>t[11]||(t[11]=[(0,r.eW)("mdi-harddisk")]))),_:1}),t[12]||(t[12]=(0,r.eW)(" Disk Usage "))])),_:1}),(0,r.bF)(D,{class:"text-center"},{default:(0,r.k6)((()=>[(0,r.bF)(x,{rotate:-90,size:100,width:15,value:w.systemMetrics.disk_usage_percent,color:M.getResourceColor(w.systemMetrics.disk_usage_percent)},{default:(0,r.k6)((()=>[(0,r.Lk)("span",d,(0,l.v_)(w.systemMetrics.disk_usage_percent)+"%",1)])),_:1},8,["value","color"]),(0,r.Lk)("div",m,[(0,r.Lk)("small",null,(0,l.v_)(M.formatSize(w.systemMetrics.disk_used))+" / "+(0,l.v_)(M.formatSize(w.systemMetrics.disk_total)),1)])])),_:1})])),_:1})])),_:1}),(0,r.bF)(U,{cols:"12",md:"3"},{default:(0,r.k6)((()=>[(0,r.bF)(R,{class:"mb-4"},{default:(0,r.k6)((()=>[(0,r.bF)(A,{class:"headline"},{default:(0,r.k6)((()=>[(0,r.bF)(L,{left:"",color:"purple"},{default:(0,r.k6)((()=>t[13]||(t[13]=[(0,r.eW)("mdi-docker")]))),_:1}),t[14]||(t[14]=(0,r.eW)(" Docker Stats "))])),_:1}),(0,r.bF)(D,null,{default:(0,r.k6)((()=>[(0,r.bF)(S,null,{default:(0,r.k6)((()=>[(0,r.bF)(U,{cols:"6",class:"text-center"},{default:(0,r.k6)((()=>[(0,r.Lk)("div",k,(0,l.v_)(w.containerStats.running),1),t[15]||(t[15]=(0,r.Lk)("div",{class:"text-subtitle-1 success--text"},"Running",-1))])),_:1}),(0,r.bF)(U,{cols:"6",class:"text-center"},{default:(0,r.k6)((()=>[(0,r.Lk)("div",_,(0,l.v_)(w.containerStats.total),1),t[16]||(t[16]=(0,r.Lk)("div",{class:"text-subtitle-1"},"Total",-1))])),_:1})])),_:1}),(0,r.bF)(T,{class:"my-2"}),(0,r.bF)(S,null,{default:(0,r.k6)((()=>[(0,r.bF)(U,{cols:"6",class:"text-center"},{default:(0,r.k6)((()=>[(0,r.Lk)("div",g,(0,l.v_)(w.imageStats.count),1),t[17]||(t[17]=(0,r.Lk)("div",{class:"text-subtitle-1"},"Images",-1))])),_:1}),(0,r.bF)(U,{cols:"6",class:"text-center"},{default:(0,r.k6)((()=>[(0,r.Lk)("div",h,(0,l.v_)(w.volumeStats.count),1),t[18]||(t[18]=(0,r.Lk)("div",{class:"text-subtitle-1"},"Volumes",-1))])),_:1})])),_:1})])),_:1})])),_:1})])),_:1})])),_:1}),(0,r.bF)(S,null,{default:(0,r.k6)((()=>[(0,r.bF)(U,{cols:"12",md:"6"},{default:(0,r.k6)((()=>[(0,r.bF)(R,{class:"mb-4"},{default:(0,r.k6)((()=>[(0,r.bF)(A,null,{default:(0,r.k6)((()=>[t[23]||(t[23]=(0,r.eW)(" CPU Usage History ")),(0,r.bF)(V),(0,r.bF)(X,{modelValue:w.cpuTimeRange,"onUpdate:modelValue":t[0]||(t[0]=e=>w.cpuTimeRange=e),mandatory:""},{default:(0,r.k6)((()=>[(0,r.bF)(z,{small:"",value:"1h"},{default:(0,r.k6)((()=>t[19]||(t[19]=[(0,r.eW)("1h")]))),_:1}),(0,r.bF)(z,{small:"",value:"6h"},{default:(0,r.k6)((()=>t[20]||(t[20]=[(0,r.eW)("6h")]))),_:1}),(0,r.bF)(z,{small:"",value:"24h"},{default:(0,r.k6)((()=>t[21]||(t[21]=[(0,r.eW)("24h")]))),_:1}),(0,r.bF)(z,{small:"",value:"7d"},{default:(0,r.k6)((()=>t[22]||(t[22]=[(0,r.eW)("7d")]))),_:1})])),_:1},8,["modelValue"])])),_:1}),(0,r.bF)(D,null,{default:(0,r.k6)((()=>t[24]||(t[24]=[(0,r.Lk)("canvas",{id:"cpuChart",height:"250"},null,-1)]))),_:1})])),_:1})])),_:1}),(0,r.bF)(U,{cols:"12",md:"6"},{default:(0,r.k6)((()=>[(0,r.bF)(R,{class:"mb-4"},{default:(0,r.k6)((()=>[(0,r.bF)(A,null,{default:(0,r.k6)((()=>[t[29]||(t[29]=(0,r.eW)(" Memory Usage History ")),(0,r.bF)(V),(0,r.bF)(X,{modelValue:w.memoryTimeRange,"onUpdate:modelValue":t[1]||(t[1]=e=>w.memoryTimeRange=e),mandatory:""},{default:(0,r.k6)((()=>[(0,r.bF)(z,{small:"",value:"1h"},{default:(0,r.k6)((()=>t[25]||(t[25]=[(0,r.eW)("1h")]))),_:1}),(0,r.bF)(z,{small:"",value:"6h"},{default:(0,r.k6)((()=>t[26]||(t[26]=[(0,r.eW)("6h")]))),_:1}),(0,r.bF)(z,{small:"",value:"24h"},{default:(0,r.k6)((()=>t[27]||(t[27]=[(0,r.eW)("24h")]))),_:1}),(0,r.bF)(z,{small:"",value:"7d"},{default:(0,r.k6)((()=>t[28]||(t[28]=[(0,r.eW)("7d")]))),_:1})])),_:1},8,["modelValue"])])),_:1}),(0,r.bF)(D,null,{default:(0,r.k6)((()=>t[30]||(t[30]=[(0,r.Lk)("canvas",{id:"memoryChart",height:"250"},null,-1)]))),_:1})])),_:1})])),_:1})])),_:1}),t[49]||(t[49]=(0,r.Lk)("h2",{class:"text-h5 mb-3"},"Container Resource Usage",-1)),(0,r.bF)(R,{class:"mb-4"},{default:(0,r.k6)((()=>[(0,r.bF)(P,{headers:w.containerHeaders,items:w.containerResources,"items-per-page":5,"sort-by":["cpu_percent"],"sort-desc":[!0],class:"elevation-1"},{"item.name":(0,r.k6)((({item:e})=>[(0,r.bF)(I,{to:`/containers/${e.id}`,class:"text-decoration-none"},{default:(0,r.k6)((()=>[(0,r.eW)((0,l.v_)(e.name),1)])),_:2},1032,["to"])])),"item.cpu_percent":(0,r.k6)((({item:e})=>[(0,r.bF)(B,{value:e.cpu_percent,height:"20",color:M.getResourceColor(e.cpu_percent),striped:""},{default:(0,r.k6)((()=>[(0,r.Lk)("strong",null,(0,l.v_)(e.cpu_percent.toFixed(1))+"%",1)])),_:2},1032,["value","color"])])),"item.memory_percent":(0,r.k6)((({item:e})=>[(0,r.bF)(B,{value:e.memory_percent,height:"20",color:M.getResourceColor(e.memory_percent),striped:""},{default:(0,r.k6)((()=>[(0,r.Lk)("strong",null,(0,l.v_)(e.memory_percent.toFixed(1))+"%",1)])),_:2},1032,["value","color"]),(0,r.Lk)("div",b,(0,l.v_)(M.formatSize(e.memory_usage)),1)])),"item.network":(0,r.k6)((({item:e})=>[(0,r.Lk)("div",null,[(0,r.bF)(L,{small:"",color:"success"},{default:(0,r.k6)((()=>t[31]||(t[31]=[(0,r.eW)("mdi-arrow-down")]))),_:1}),(0,r.eW)(" "+(0,l.v_)(M.formatSize(e.network_rx))+"/s ",1)]),(0,r.Lk)("div",null,[(0,r.bF)(L,{small:"",color:"info"},{default:(0,r.k6)((()=>t[32]||(t[32]=[(0,r.eW)("mdi-arrow-up")]))),_:1}),(0,r.eW)(" "+(0,l.v_)(M.formatSize(e.network_tx))+"/s ",1)])])),"item.disk":(0,r.k6)((({item:e})=>[(0,r.Lk)("div",null,[(0,r.bF)(L,{small:"",color:"success"},{default:(0,r.k6)((()=>t[33]||(t[33]=[(0,r.eW)("mdi-arrow-down")]))),_:1}),(0,r.eW)(" "+(0,l.v_)(M.formatSize(e.disk_read))+"/s ",1)]),(0,r.Lk)("div",null,[(0,r.bF)(L,{small:"",color:"info"},{default:(0,r.k6)((()=>t[34]||(t[34]=[(0,r.eW)("mdi-arrow-up")]))),_:1}),(0,r.eW)(" "+(0,l.v_)(M.formatSize(e.disk_write))+"/s ",1)])])),"item.actions":(0,r.k6)((({item:e})=>[(0,r.bF)(z,{icon:"",small:"",to:`/containers/${e.id}`,title:"View Details"},{default:(0,r.k6)((()=>[(0,r.bF)(L,{small:""},{default:(0,r.k6)((()=>t[35]||(t[35]=[(0,r.eW)("mdi-eye")]))),_:1})])),_:2},1032,["to"]),(0,r.bF)(z,{icon:"",small:"",onClick:t=>M.showContainerMetrics(e),title:"View Metrics"},{default:(0,r.k6)((()=>[(0,r.bF)(L,{small:""},{default:(0,r.k6)((()=>t[36]||(t[36]=[(0,r.eW)("mdi-chart-line")]))),_:1})])),_:2},1032,["onClick"])])),_:1},8,["headers","items"])])),_:1}),t[50]||(t[50]=(0,r.Lk)("h2",{class:"text-h5 mb-3"},"Alerts and Anomalies",-1)),(0,r.bF)(S,null,{default:(0,r.k6)((()=>[(0,r.bF)(U,{cols:"12"},{default:(0,r.k6)((()=>[(0,r.bF)(Q,null,{default:(0,r.k6)((()=>[((0,r.uX)(!0),(0,r.CE)(r.FK,null,(0,r.pI)(w.alerts,((e,a)=>((0,r.uX)(),(0,r.Wv)(H,{key:a},{default:(0,r.k6)((()=>[(0,r.bF)(N,null,{default:(0,r.k6)((()=>[(0,r.Lk)("div",f,[(0,r.bF)(L,{color:M.getAlertSeverityColor(e.severity),class:"mr-2"},{default:(0,r.k6)((()=>t[37]||(t[37]=[(0,r.eW)(" mdi-alert-circle ")]))),_:2},1032,["color"]),(0,r.Lk)("span",null,(0,l.v_)(e.title),1),(0,r.bF)($,{class:"ml-2","x-small":"",color:M.getAlertSeverityColor(e.severity),"text-color":"white"},{default:(0,r.k6)((()=>[(0,r.eW)((0,l.v_)(e.severity),1)])),_:2},1032,["color"]),(0,r.bF)(V),(0,r.Lk)("span",v,(0,l.v_)(M.formatDate(e.timestamp)),1)])])),_:2},1024),(0,r.bF)(E,null,{default:(0,r.k6)((()=>[(0,r.Lk)("p",null,(0,l.v_)(e.description),1),e.resource?((0,r.uX)(),(0,r.CE)("div",p,[t[38]||(t[38]=(0,r.Lk)("strong",null,"Resource:",-1)),(0,r.eW)(" "+(0,l.v_)(e.resource.name)+" ("+(0,l.v_)(e.resource.type)+") ",1)])):(0,r.Q3)("",!0),e.metrics&&e.metrics.length>0?((0,r.uX)(),(0,r.CE)("div",y,[t[39]||(t[39]=(0,r.Lk)("strong",null,"Metrics:",-1)),(0,r.Lk)("ul",null,[((0,r.uX)(!0),(0,r.CE)(r.FK,null,(0,r.pI)(e.metrics,((e,t)=>((0,r.uX)(),(0,r.CE)("li",{key:t},(0,l.v_)(e.name)+": "+(0,l.v_)(e.value)+" "+(0,l.v_)(e.unit),1)))),128))])])):(0,r.Q3)("",!0),(0,r.Lk)("div",F,[e.acknowledged?(0,r.Q3)("",!0):((0,r.uX)(),(0,r.Wv)(z,{key:0,color:"primary",text:"",small:"",onClick:t=>M.acknowledgeAlert(e)},{default:(0,r.k6)((()=>[(0,r.bF)(L,{left:"",small:""},{default:(0,r.k6)((()=>t[40]||(t[40]=[(0,r.eW)("mdi-check")]))),_:1}),t[41]||(t[41]=(0,r.eW)(" Acknowledge "))])),_:2},1032,["onClick"])),e.resolved?(0,r.Q3)("",!0):((0,r.uX)(),(0,r.Wv)(z,{key:1,color:"success",text:"",small:"",onClick:t=>M.resolveAlert(e)},{default:(0,r.k6)((()=>[(0,r.bF)(L,{left:"",small:""},{default:(0,r.k6)((()=>t[42]||(t[42]=[(0,r.eW)("mdi-check-all")]))),_:1}),t[43]||(t[43]=(0,r.eW)(" Resolve "))])),_:2},1032,["onClick"])),e.resource?((0,r.uX)(),(0,r.Wv)(z,{key:2,color:"info",text:"",small:"",to:M.getResourceLink(e.resource)},{default:(0,r.k6)((()=>[(0,r.bF)(L,{left:"",small:""},{default:(0,r.k6)((()=>t[44]||(t[44]=[(0,r.eW)("mdi-eye")]))),_:1}),t[45]||(t[45]=(0,r.eW)(" View Resource "))])),_:2},1032,["to"])):(0,r.Q3)("",!0)])])),_:2},1024)])),_:2},1024)))),128))])),_:1}),0===w.alerts.length?((0,r.uX)(),(0,r.Wv)(R,{key:0,class:"text-center pa-5"},{default:(0,r.k6)((()=>[(0,r.bF)(L,{size:"64",color:"success"},{default:(0,r.k6)((()=>t[46]||(t[46]=[(0,r.eW)("mdi-check-circle")]))),_:1}),t[47]||(t[47]=(0,r.Lk)("h3",{class:"text-h5 mt-4"},"No active alerts",-1)),t[48]||(t[48]=(0,r.Lk)("p",{class:"text-body-1 mt-2"}," All systems are operating normally ",-1))])),_:1})):(0,r.Q3)("",!0)])),_:1})])),_:1})],64)),(0,r.bF)(q,{modelValue:w.containerMetricsDialog,"onUpdate:modelValue":t[6]||(t[6]=e=>w.containerMetricsDialog=e),"max-width":"800"},{default:(0,r.k6)((()=>[(0,r.bF)(R,null,{default:(0,r.k6)((()=>[(0,r.bF)(A,{class:"headline"},{default:(0,r.k6)((()=>[(0,r.eW)((0,l.v_)(w.selectedContainer?.name)+" Metrics ",1),(0,r.bF)(V),(0,r.bF)(z,{icon:"",onClick:t[2]||(t[2]=e=>w.containerMetricsDialog=!1)},{default:(0,r.k6)((()=>[(0,r.bF)(L,null,{default:(0,r.k6)((()=>t[51]||(t[51]=[(0,r.eW)("mdi-close")]))),_:1})])),_:1})])),_:1}),(0,r.bF)(D,null,{default:(0,r.k6)((()=>[(0,r.bF)(Z,{modelValue:w.activeMetricTab,"onUpdate:modelValue":t[3]||(t[3]=e=>w.activeMetricTab=e)},{default:(0,r.k6)((()=>[(0,r.bF)(K,null,{default:(0,r.k6)((()=>t[52]||(t[52]=[(0,r.eW)("CPU")]))),_:1}),(0,r.bF)(K,null,{default:(0,r.k6)((()=>t[53]||(t[53]=[(0,r.eW)("Memory")]))),_:1}),(0,r.bF)(K,null,{default:(0,r.k6)((()=>t[54]||(t[54]=[(0,r.eW)("Network")]))),_:1}),(0,r.bF)(K,null,{default:(0,r.k6)((()=>t[55]||(t[55]=[(0,r.eW)("Disk")]))),_:1})])),_:1},8,["modelValue"]),(0,r.bF)(O,{modelValue:w.activeMetricTab,"onUpdate:modelValue":t[4]||(t[4]=e=>w.activeMetricTab=e)},{default:(0,r.k6)((()=>[(0,r.bF)(G,null,{default:(0,r.k6)((()=>t[56]||(t[56]=[(0,r.Lk)("div",{class:"pa-4"},[(0,r.Lk)("canvas",{id:"containerCpuChart",height:"250"})],-1)]))),_:1}),(0,r.bF)(G,null,{default:(0,r.k6)((()=>t[57]||(t[57]=[(0,r.Lk)("div",{class:"pa-4"},[(0,r.Lk)("canvas",{id:"containerMemoryChart",height:"250"})],-1)]))),_:1}),(0,r.bF)(G,null,{default:(0,r.k6)((()=>t[58]||(t[58]=[(0,r.Lk)("div",{class:"pa-4"},[(0,r.Lk)("canvas",{id:"containerNetworkChart",height:"250"})],-1)]))),_:1}),(0,r.bF)(G,null,{default:(0,r.k6)((()=>t[59]||(t[59]=[(0,r.Lk)("div",{class:"pa-4"},[(0,r.Lk)("canvas",{id:"containerDiskChart",height:"250"})],-1)]))),_:1})])),_:1},8,["modelValue"])])),_:1}),(0,r.bF)(j,null,{default:(0,r.k6)((()=>[(0,r.bF)(V),(0,r.bF)(z,{color:"primary",text:"",onClick:t[5]||(t[5]=e=>w.containerMetricsDialog=!1)},{default:(0,r.k6)((()=>t[60]||(t[60]=[(0,r.eW)(" Close ")]))),_:1})])),_:1})])),_:1})])),_:1},8,["modelValue"])])}var w=a(2977),M={name:"MonitoringDashboard",data(){return{loading:!0,error:null,refreshInterval:null,systemMetrics:{cpu_usage:0,cpu_cores:0,memory_usage_percent:0,memory_used:0,memory_total:0,disk_usage_percent:0,disk_used:0,disk_total:0},containerStats:{running:0,total:0},imageStats:{count:0},volumeStats:{count:0},cpuTimeRange:"1h",memoryTimeRange:"1h",containerHeaders:[{text:"Name",value:"name",sortable:!0},{text:"CPU",value:"cpu_percent",sortable:!0},{text:"Memory",value:"memory_percent",sortable:!0},{text:"Network I/O",value:"network",sortable:!1},{text:"Disk I/O",value:"disk",sortable:!1},{text:"Actions",value:"actions",sortable:!1,align:"center"}],containerResources:[],alerts:[],containerMetricsDialog:!1,selectedContainer:null,activeMetricTab:0,charts:{cpu:null,memory:null,containerCpu:null,containerMemory:null,containerNetwork:null,containerDisk:null}}},computed:{...(0,w.L8)({isAuthenticated:"auth/isAuthenticated",token:"auth/token"})},watch:{cpuTimeRange(){this.updateCpuChart()},memoryTimeRange(){this.updateMemoryChart()}},created(){this.fetchMonitoringData()},mounted(){this.refreshInterval=setInterval((()=>{this.fetchMonitoringData(!1)}),3e4)},beforeDestroy(){this.refreshInterval&&clearInterval(this.refreshInterval)},methods:{async fetchMonitoringData(e=!0){e&&(this.loading=!0),this.error=null;try{setTimeout((()=>{this.systemMetrics={cpu_usage:35.2,cpu_cores:8,memory_usage_percent:42.7,memory_used:7301444403.2,memory_total:17179869184,disk_usage_percent:68.3,disk_used:220117073920,disk_total:322122547200},this.containerStats={running:7,total:12},this.imageStats={count:23},this.volumeStats={count:8},this.containerResources=[{id:"c1",name:"web-server",cpu_percent:12.5,memory_percent:8.2,memory_usage:268435456,network_rx:1258291.2,network_tx:3670016,disk_read:524288,disk_write:209715.2},{id:"c2",name:"api-service",cpu_percent:28.7,memory_percent:15.3,memory_usage:536870912,network_rx:2936012.8,network_tx:1782579.2,disk_read:314572.8,disk_write:838860.8},{id:"c3",name:"database",cpu_percent:45.2,memory_percent:62.8,memory_usage:2684354560,network_rx:838860.8,network_tx:629145.6,disk_read:5452595.2,disk_write:3250585.6},{id:"c4",name:"cache",cpu_percent:5.3,memory_percent:28.1,memory_usage:805306368,network_rx:4718592,network_tx:3355443.2,disk_read:104857.6,disk_write:52428.8},{id:"c5",name:"worker",cpu_percent:78.9,memory_percent:42.6,memory_usage:939524096,network_rx:314572.8,network_tx:209715.2,disk_read:2202009.6,disk_write:1887436.8}],this.alerts=[{id:"a1",title:"High CPU Usage",description:'Container "worker" is using excessive CPU resources (78.9%). This may indicate a performance issue or resource contention.',severity:"warning",timestamp:"2025-03-17T05:45:00Z",acknowledged:!1,resolved:!1,resource:{type:"container",id:"c5",name:"worker"},metrics:[{name:"CPU Usage",value:78.9,unit:"%"}]},{id:"a2",title:"Memory Leak Detected",description:'Container "database" shows a steady increase in memory usage over the past 6 hours, indicating a possible memory leak.',severity:"critical",timestamp:"2025-03-17T04:30:00Z",acknowledged:!0,resolved:!1,resource:{type:"container",id:"c3",name:"database"},metrics:[{name:"Memory Usage",value:62.8,unit:"%"},{name:"Memory Growth Rate",value:5.2,unit:"%/hour"}]},{id:"a3",title:"Disk Space Warning",description:"Host system is running low on disk space (68.3% used). Consider cleaning up unused images and volumes.",severity:"warning",timestamp:"2025-03-17T03:15:00Z",acknowledged:!1,resolved:!1,resource:{type:"host",id:"host",name:"Docker Host"},metrics:[{name:"Disk Usage",value:68.3,unit:"%"}]}],this.loading=!1,this.$nextTick((()=>{this.initCharts()}))}),1e3)}catch(t){this.error="Failed to load monitoring data. Please try again.",this.loading=!1}},formatDate(e){const t=new Date(e);return t.toLocaleString()},formatSize(e){if(0===e)return"0 Bytes";const t=1024,a=["Bytes","KB","MB","GB","TB"],r=Math.floor(Math.log(e)/Math.log(t));return parseFloat((e/Math.pow(t,r)).toFixed(2))+" "+a[r]},getResourceColor(e){return e>=90?"error":e>=70?"warning":e>=50?"info":"success"},getAlertSeverityColor(e){switch(e){case"critical":return"error";case"warning":return"warning";case"info":return"info";default:return"grey"}},getResourceLink(e){if(!e)return"#";switch(e.type){case"container":return`/containers/${e.id}`;case"image":return`/images/${e.id}`;case"volume":return`/volumes/${e.id}`;case"network":return`/networks/${e.id}`;default:return"#"}},showContainerMetrics(e){this.selectedContainer=e,this.containerMetricsDialog=!0,this.$nextTick((()=>{this.initContainerCharts()}))},acknowledgeAlert(e){e.acknowledged=!0},resolveAlert(e){e.resolved=!0,setTimeout((()=>{this.alerts=this.alerts.filter((t=>t.id!==e.id))}),500)},initCharts(){console.log("Charts would be initialized here in a real implementation");const e={labels:Array.from({length:24},((e,t)=>23-t+"h ago")),datasets:[{label:"CPU Usage (%)",data:Array.from({length:24},(()=>50*Math.random()+20)),borderColor:"#1976D2",backgroundColor:"rgba(25, 118, 210, 0.1)",fill:!0}]},t={labels:Array.from({length:24},((e,t)=>23-t+"h ago")),datasets:[{label:"Memory Usage (%)",data:Array.from({length:24},(()=>30*Math.random()+30)),borderColor:"#4CAF50",backgroundColor:"rgba(76, 175, 80, 0.1)",fill:!0}]};this.charts.cpu=e,this.charts.memory=t},updateCpuChart(){console.log(`CPU chart would be updated with time range: ${this.cpuTimeRange}`)},updateMemoryChart(){console.log(`Memory chart would be updated with time range: ${this.memoryTimeRange}`)},initContainerCharts(){console.log("Container charts would be initialized here in a real implementation");const e={labels:Array.from({length:24},((e,t)=>23-t+"h ago")),datasets:[{label:"CPU Usage (%)",data:Array.from({length:24},(()=>50*Math.random()+20)),borderColor:"#1976D2",backgroundColor:"rgba(25, 118, 210, 0.1)",fill:!0}]},t={labels:Array.from({length:24},((e,t)=>23-t+"h ago")),datasets:[{label:"Memory Usage (%)",data:Array.from({length:24},(()=>30*Math.random()+30)),borderColor:"#4CAF50",backgroundColor:"rgba(76, 175, 80, 0.1)",fill:!0}]},a={labels:Array.from({length:24},((e,t)=>23-t+"h ago")),datasets:[{label:"Network RX (MB/s)",data:Array.from({length:24},(()=>3*Math.random()+1)),borderColor:"#2196F3",backgroundColor:"rgba(33, 150, 243, 0.1)",fill:!0},{label:"Network TX (MB/s)",data:Array.from({length:24},(()=>2*Math.random()+.5)),borderColor:"#FF9800",backgroundColor:"rgba(255, 152, 0, 0.1)",fill:!0}]},r={labels:Array.from({length:24},((e,t)=>23-t+"h ago")),datasets:[{label:"Disk Read (MB/s)",data:Array.from({length:24},(()=>5*Math.random()+.5)),borderColor:"#4CAF50",backgroundColor:"rgba(76, 175, 80, 0.1)",fill:!0},{label:"Disk Write (MB/s)",data:Array.from({length:24},(()=>3*Math.random()+.2)),borderColor:"#9C27B0",backgroundColor:"rgba(156, 39, 176, 0.1)",fill:!0}]};this.charts.containerCpu=e,this.charts.containerMemory=t,this.charts.containerNetwork=a,this.charts.containerDisk=r}}},x=a(6262);const W=(0,x.A)(M,[["render",C],["__scopeId","data-v-558374b5"]]);var L=W}}]);
//# sourceMappingURL=967.f0f37484.js.map