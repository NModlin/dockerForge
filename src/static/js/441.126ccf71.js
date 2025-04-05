"use strict";(self["webpackChunkdockerforge_web_ui"]=self["webpackChunkdockerforge_web_ui"]||[]).push([[441],{3441:function(e,t,i){i.r(t),i.d(t,{default:function(){return S}});var r=i(641),s=i(33);const a={class:"security-dashboard"},o={key:0,class:"d-flex justify-center align-center my-5"},c={class:"text-h4"},l={class:"mt-4"},n={class:"text-h4 red--text"},u={class:"text-h4 orange--text"},d={class:"text-h4 blue--text"},m={class:"text-h4"},_={class:"text-h4"},h={key:3},p={class:"d-flex align-center"},f={key:0},k={class:"d-flex mt-2"};function g(e,t,i,g,y,b){const v=(0,r.g2)("v-progress-circular"),w=(0,r.g2)("v-alert"),x=(0,r.g2)("v-icon"),S=(0,r.g2)("v-card-title"),F=(0,r.g2)("v-chip"),C=(0,r.g2)("v-card-text"),W=(0,r.g2)("v-card"),L=(0,r.g2)("v-col"),A=(0,r.g2)("v-row"),I=(0,r.g2)("v-btn"),R=(0,r.g2)("v-progress-linear"),$=(0,r.g2)("router-link"),E=(0,r.g2)("v-data-table"),D=(0,r.g2)("v-expansion-panel-header"),X=(0,r.g2)("v-expansion-panel-content"),T=(0,r.g2)("v-expansion-panel"),P=(0,r.g2)("v-expansion-panels");return(0,r.uX)(),(0,r.CE)("div",a,[t[23]||(t[23]=(0,r.Lk)("h1",{class:"text-h4 mb-4"},"Security Dashboard",-1)),y.loading?((0,r.uX)(),(0,r.CE)("div",o,[(0,r.bF)(v,{indeterminate:"",color:"primary"})])):y.error?((0,r.uX)(),(0,r.Wv)(w,{key:1,type:"error",class:"mb-4"},{default:(0,r.k6)((()=>[(0,r.eW)((0,s.v_)(y.error),1)])),_:1})):((0,r.uX)(),(0,r.CE)(r.FK,{key:2},[(0,r.bF)(A,null,{default:(0,r.k6)((()=>[(0,r.bF)(L,{cols:"12",md:"4"},{default:(0,r.k6)((()=>[(0,r.bF)(W,{class:"mb-4"},{default:(0,r.k6)((()=>[(0,r.bF)(S,{class:"headline"},{default:(0,r.k6)((()=>[(0,r.bF)(x,{left:"",color:b.getSecurityScoreColor(y.securityScore)},{default:(0,r.k6)((()=>t[0]||(t[0]=[(0,r.eW)(" mdi-shield ")]))),_:1},8,["color"]),t[1]||(t[1]=(0,r.eW)(" Security Score "))])),_:1}),(0,r.bF)(C,{class:"text-center"},{default:(0,r.k6)((()=>[(0,r.bF)(v,{rotate:-90,size:150,width:15,value:y.securityScore,color:b.getSecurityScoreColor(y.securityScore)},{default:(0,r.k6)((()=>[(0,r.Lk)("span",c,(0,s.v_)(y.securityScore),1)])),_:1},8,["value","color"]),(0,r.Lk)("div",l,[(0,r.bF)(F,{color:b.getSecurityScoreColor(y.securityScore),"text-color":"white"},{default:(0,r.k6)((()=>[(0,r.eW)((0,s.v_)(b.getSecurityScoreLabel(y.securityScore)),1)])),_:1},8,["color"])])])),_:1})])),_:1})])),_:1}),(0,r.bF)(L,{cols:"12",md:"4"},{default:(0,r.k6)((()=>[(0,r.bF)(W,{class:"mb-4"},{default:(0,r.k6)((()=>[(0,r.bF)(S,{class:"headline"},{default:(0,r.k6)((()=>[(0,r.bF)(x,{left:"",color:"error"},{default:(0,r.k6)((()=>t[2]||(t[2]=[(0,r.eW)("mdi-alert")]))),_:1}),t[3]||(t[3]=(0,r.eW)(" Vulnerabilities "))])),_:1}),(0,r.bF)(C,null,{default:(0,r.k6)((()=>[(0,r.bF)(A,null,{default:(0,r.k6)((()=>[(0,r.bF)(L,{cols:"4",class:"text-center"},{default:(0,r.k6)((()=>[(0,r.Lk)("div",n,(0,s.v_)(y.vulnerabilityCounts.critical),1),t[4]||(t[4]=(0,r.Lk)("div",{class:"text-subtitle-1"},"Critical",-1))])),_:1}),(0,r.bF)(L,{cols:"4",class:"text-center"},{default:(0,r.k6)((()=>[(0,r.Lk)("div",u,(0,s.v_)(y.vulnerabilityCounts.high),1),t[5]||(t[5]=(0,r.Lk)("div",{class:"text-subtitle-1"},"High",-1))])),_:1}),(0,r.bF)(L,{cols:"4",class:"text-center"},{default:(0,r.k6)((()=>[(0,r.Lk)("div",d,(0,s.v_)(y.vulnerabilityCounts.medium+y.vulnerabilityCounts.low),1),t[6]||(t[6]=(0,r.Lk)("div",{class:"text-subtitle-1"},"Other",-1))])),_:1})])),_:1}),(0,r.bF)(I,{color:"primary",block:"",class:"mt-4",to:"/security/vulnerabilities"},{default:(0,r.k6)((()=>t[7]||(t[7]=[(0,r.eW)(" View All Vulnerabilities ")]))),_:1})])),_:1})])),_:1})])),_:1}),(0,r.bF)(L,{cols:"12",md:"4"},{default:(0,r.k6)((()=>[(0,r.bF)(W,{class:"mb-4"},{default:(0,r.k6)((()=>[(0,r.bF)(S,{class:"headline"},{default:(0,r.k6)((()=>[(0,r.bF)(x,{left:"",color:"warning"},{default:(0,r.k6)((()=>t[8]||(t[8]=[(0,r.eW)("mdi-check-decagram")]))),_:1}),t[9]||(t[9]=(0,r.eW)(" Compliance "))])),_:1}),(0,r.bF)(C,null,{default:(0,r.k6)((()=>[(0,r.bF)(A,null,{default:(0,r.k6)((()=>[(0,r.bF)(L,{cols:"6",class:"text-center"},{default:(0,r.k6)((()=>[(0,r.Lk)("div",m,(0,s.v_)(y.complianceStats.passed),1),t[10]||(t[10]=(0,r.Lk)("div",{class:"text-subtitle-1 success--text"},"Passed",-1))])),_:1}),(0,r.bF)(L,{cols:"6",class:"text-center"},{default:(0,r.k6)((()=>[(0,r.Lk)("div",_,(0,s.v_)(y.complianceStats.failed),1),t[11]||(t[11]=(0,r.Lk)("div",{class:"text-subtitle-1 error--text"},"Failed",-1))])),_:1})])),_:1}),(0,r.bF)(R,{value:y.complianceStats.passed/(y.complianceStats.passed+y.complianceStats.failed)*100,color:"success",height:"20",class:"mt-2"},{default:(0,r.k6)((()=>[(0,r.eW)((0,s.v_)(Math.round(y.complianceStats.passed/(y.complianceStats.passed+y.complianceStats.failed)*100))+"% ",1)])),_:1},8,["value"]),(0,r.bF)(I,{color:"primary",block:"",class:"mt-4",to:"/security/compliance"},{default:(0,r.k6)((()=>t[12]||(t[12]=[(0,r.eW)(" View Compliance Report ")]))),_:1})])),_:1})])),_:1})])),_:1})])),_:1}),t[21]||(t[21]=(0,r.Lk)("h2",{class:"text-h5 mb-3"},"Recent Security Scans",-1)),(0,r.bF)(W,{class:"mb-4"},{default:(0,r.k6)((()=>[(0,r.bF)(E,{headers:y.scanHeaders,items:y.recentScans,"items-per-page":5,class:"elevation-1"},{"item.resource":(0,r.k6)((({item:e})=>[(0,r.bF)($,{to:b.getResourceLink(e),class:"text-decoration-none"},{default:(0,r.k6)((()=>[(0,r.eW)((0,s.v_)(e.resource_name),1)])),_:2},1032,["to"]),(0,r.bF)(F,{"x-small":"",class:"ml-2",color:b.getResourceTypeColor(e.resource_type)},{default:(0,r.k6)((()=>[(0,r.eW)((0,s.v_)(e.resource_type),1)])),_:2},1032,["color"])])),"item.status":(0,r.k6)((({item:e})=>[(0,r.bF)(F,{color:b.getScanStatusColor(e.status),"text-color":"white",small:""},{default:(0,r.k6)((()=>[(0,r.eW)((0,s.v_)(e.status),1)])),_:2},1032,["color"])])),"item.findings":(0,r.k6)((({item:e})=>[e.critical_count>0?((0,r.uX)(),(0,r.Wv)(F,{key:0,color:"error","x-small":"",class:"mr-1"},{default:(0,r.k6)((()=>[(0,r.eW)((0,s.v_)(e.critical_count)+" Critical ",1)])),_:2},1024)):(0,r.Q3)("",!0),e.high_count>0?((0,r.uX)(),(0,r.Wv)(F,{key:1,color:"warning","x-small":"",class:"mr-1"},{default:(0,r.k6)((()=>[(0,r.eW)((0,s.v_)(e.high_count)+" High ",1)])),_:2},1024)):(0,r.Q3)("",!0),e.medium_count>0?((0,r.uX)(),(0,r.Wv)(F,{key:2,color:"info","x-small":"",class:"mr-1"},{default:(0,r.k6)((()=>[(0,r.eW)((0,s.v_)(e.medium_count)+" Medium ",1)])),_:2},1024)):(0,r.Q3)("",!0),0===e.critical_count&&0===e.high_count&&0===e.medium_count?((0,r.uX)(),(0,r.CE)("span",h," No significant findings ")):(0,r.Q3)("",!0)])),"item.scan_date":(0,r.k6)((({item:e})=>[(0,r.eW)((0,s.v_)(b.formatDate(e.scan_date)),1)])),"item.actions":(0,r.k6)((({item:e})=>[(0,r.bF)(I,{icon:"",small:"",to:b.getScanDetailsLink(e),title:"View Details"},{default:(0,r.k6)((()=>[(0,r.bF)(x,{small:""},{default:(0,r.k6)((()=>t[13]||(t[13]=[(0,r.eW)("mdi-eye")]))),_:1})])),_:2},1032,["to"]),(0,r.bF)(I,{icon:"",small:"",onClick:t=>b.runNewScan(e),title:"Run New Scan",disabled:"in-progress"===e.status},{default:(0,r.k6)((()=>[(0,r.bF)(x,{small:""},{default:(0,r.k6)((()=>t[14]||(t[14]=[(0,r.eW)("mdi-refresh")]))),_:1})])),_:2},1032,["onClick","disabled"]),(0,r.bF)(I,{icon:"",small:"",onClick:t=>b.resolveWithAI(e),title:"Resolve with AI",disabled:"in-progress"===e.status||0===e.critical_count&&0===e.high_count,color:"primary"},{default:(0,r.k6)((()=>[(0,r.bF)(x,{small:""},{default:(0,r.k6)((()=>t[15]||(t[15]=[(0,r.eW)("mdi-robot")]))),_:1})])),_:2},1032,["onClick","disabled"])])),_:1},8,["headers","items"])])),_:1}),t[22]||(t[22]=(0,r.Lk)("h2",{class:"text-h5 mb-3"},"Security Recommendations",-1)),(0,r.bF)(A,null,{default:(0,r.k6)((()=>[(0,r.bF)(L,{cols:"12"},{default:(0,r.k6)((()=>[(0,r.bF)(P,null,{default:(0,r.k6)((()=>[((0,r.uX)(!0),(0,r.CE)(r.FK,null,(0,r.pI)(y.recommendations,((e,i)=>((0,r.uX)(),(0,r.Wv)(T,{key:i},{default:(0,r.k6)((()=>[(0,r.bF)(D,null,{default:(0,r.k6)((()=>[(0,r.Lk)("div",p,[(0,r.bF)(x,{color:b.getRecommendationPriorityColor(e.priority),class:"mr-2"},{default:(0,r.k6)((()=>t[16]||(t[16]=[(0,r.eW)(" mdi-alert-circle ")]))),_:2},1032,["color"]),(0,r.Lk)("span",null,(0,s.v_)(e.title),1),(0,r.bF)(F,{class:"ml-2","x-small":"",color:b.getRecommendationPriorityColor(e.priority),"text-color":"white"},{default:(0,r.k6)((()=>[(0,r.eW)((0,s.v_)(e.priority),1)])),_:2},1032,["color"])])])),_:2},1024),(0,r.bF)(X,null,{default:(0,r.k6)((()=>[(0,r.Lk)("p",null,(0,s.v_)(e.description),1),e.affected_resources.length>0?((0,r.uX)(),(0,r.CE)("div",f,[t[17]||(t[17]=(0,r.Lk)("strong",null,"Affected Resources:",-1)),(0,r.Lk)("ul",null,[((0,r.uX)(!0),(0,r.CE)(r.FK,null,(0,r.pI)(e.affected_resources,((e,t)=>((0,r.uX)(),(0,r.CE)("li",{key:t},(0,s.v_)(e.name)+" ("+(0,s.v_)(e.type)+") ",1)))),128))])])):(0,r.Q3)("",!0),(0,r.Lk)("div",k,[(0,r.bF)(I,{color:"primary",text:"",class:"mr-2",onClick:t=>b.applyRecommendation(e)},{default:(0,r.k6)((()=>t[18]||(t[18]=[(0,r.eW)(" Apply Recommendation ")]))),_:2},1032,["onClick"]),(0,r.bF)(I,{color:"info",text:"",onClick:t=>b.resolveRecommendationWithAI(e)},{default:(0,r.k6)((()=>[(0,r.bF)(x,{left:"",small:""},{default:(0,r.k6)((()=>t[19]||(t[19]=[(0,r.eW)("mdi-robot")]))),_:1}),t[20]||(t[20]=(0,r.eW)(" Resolve with AI "))])),_:2},1032,["onClick"])])])),_:2},1024)])),_:2},1024)))),128))])),_:1})])),_:1})])),_:1})],64))])}var y=i(2977),b=i(4335),v={name:"SecurityDashboard",data(){return{loading:!0,error:null,securityScore:0,vulnerabilityCounts:{critical:0,high:0,medium:0,low:0},complianceStats:{passed:0,failed:0},scanHeaders:[{text:"Resource",value:"resource",sortable:!0},{text:"Status",value:"status",sortable:!0},{text:"Findings",value:"findings",sortable:!1},{text:"Scan Date",value:"scan_date",sortable:!0},{text:"Actions",value:"actions",sortable:!1,align:"center"}],recentScans:[],recommendations:[]}},computed:{...(0,y.L8)({isAuthenticated:"auth/isAuthenticated",token:"auth/token"})},created(){this.fetchSecurityData()},methods:{...(0,y.i0)({setActive:"chat/SET_ACTIVE",updateContext:"chat/updateContext"}),async fetchSecurityData(){this.loading=!0,this.error=null;try{setTimeout((()=>{this.securityScore=78,this.vulnerabilityCounts={critical:2,high:5,medium:12,low:23},this.complianceStats={passed:42,failed:8},this.recentScans=[{id:"s1",resource_type:"image",resource_id:"i1",resource_name:"nginx:latest",status:"completed",critical_count:0,high_count:2,medium_count:5,scan_date:"2025-03-16T10:00:00Z"},{id:"s2",resource_type:"image",resource_id:"i2",resource_name:"postgres:13",status:"completed",critical_count:1,high_count:3,medium_count:7,scan_date:"2025-03-16T09:30:00Z"},{id:"s3",resource_type:"container",resource_id:"c1",resource_name:"web-server",status:"completed",critical_count:0,high_count:0,medium_count:0,scan_date:"2025-03-16T09:00:00Z"},{id:"s4",resource_type:"image",resource_id:"i3",resource_name:"node:14-alpine",status:"in-progress",critical_count:0,high_count:0,medium_count:0,scan_date:"2025-03-16T08:45:00Z"},{id:"s5",resource_type:"container",resource_id:"c3",resource_name:"database",status:"failed",critical_count:0,high_count:0,medium_count:0,scan_date:"2025-03-16T08:30:00Z"}],this.recommendations=[{id:"r1",title:"Update nginx image to fix critical vulnerabilities",description:"The current nginx image has 2 critical vulnerabilities that can be fixed by updating to the latest version.",priority:"high",affected_resources:[{name:"nginx:latest",type:"image"},{name:"web-server",type:"container"}]},{id:"r2",title:"Enable user namespace remapping",description:"User namespace remapping provides an additional layer of security by mapping container user IDs to a different range on the host.",priority:"medium",affected_resources:[]},{id:"r3",title:"Apply security policy to restrict privileged containers",description:"Privileged containers have access to all host devices and can pose a security risk. Apply a security policy to restrict their usage.",priority:"high",affected_resources:[{name:"database",type:"container"}]},{id:"r4",title:"Configure network policies to restrict container communication",description:"Implement network policies to restrict communication between containers and limit exposure to potential attacks.",priority:"medium",affected_resources:[]},{id:"r5",title:"Enable content trust for image verification",description:"Content trust ensures that the images you pull are signed and verified, reducing the risk of using compromised images.",priority:"medium",affected_resources:[]}],this.loading=!1}),1e3)}catch(e){this.error="Failed to load security data. Please try again.",this.loading=!1}},formatDate(e){const t=new Date(e);return t.toLocaleString()},getSecurityScoreColor(e){return e>=90?"success":e>=70?"warning":"error"},getSecurityScoreLabel(e){return e>=90?"Good":e>=70?"Needs Improvement":"At Risk"},getScanStatusColor(e){switch(e){case"completed":return"success";case"in-progress":return"info";case"failed":return"error";default:return"grey"}},getResourceTypeColor(e){switch(e){case"image":return"primary";case"container":return"success";case"volume":return"warning";case"network":return"info";default:return"grey"}},getRecommendationPriorityColor(e){switch(e){case"critical":return"error";case"high":return"deep-orange";case"medium":return"warning";case"low":return"info";default:return"grey"}},getResourceLink(e){switch(e.resource_type){case"image":return`/images/${e.resource_id}`;case"container":return`/containers/${e.resource_id}`;case"volume":return`/volumes/${e.resource_id}`;case"network":return`/networks/${e.resource_id}`;default:return"#"}},getScanDetailsLink(e){return"image"===e.resource_type?`/images/${e.resource_id}/security/${e.id}`:`/security/scans/${e.id}`},runNewScan(e){this.$set(e,"status","in-progress"),this.$set(e,"scan_date",(new Date).toISOString()),setTimeout((()=>{this.$set(e,"status","completed")}),3e3)},async resolveWithAI(e){try{const t=await b.A.post(`/api/chat/security/start-workflow?vulnerability_id=${e.id}`);this.updateContext({currentPage:"security",currentContainerId:"container"===e.resource_type?e.resource_id:null,currentImageId:"image"===e.resource_type?e.resource_id:null,vulnerability_id:e.id,workflow_id:t.data.message.context?.workflow_id}),this.setActive(!0),this.$emit("show-notification",{type:"info",message:"AI-assisted resolution workflow started. Check the chat sidebar."})}catch(t){console.error("Error starting security workflow:",t),this.$emit("show-notification",{type:"error",message:"Failed to start AI resolution workflow."})}},async resolveRecommendationWithAI(e){try{const t=await b.A.post(`/api/chat/security/start-workflow?vulnerability_id=${e.id}`);this.updateContext({currentPage:"security",recommendation_id:e.id,workflow_id:t.data.message.context?.workflow_id}),this.setActive(!0),this.$emit("show-notification",{type:"info",message:"AI-assisted resolution workflow started. Check the chat sidebar."})}catch(t){console.error("Error starting recommendation workflow:",t),this.$emit("show-notification",{type:"error",message:"Failed to start AI resolution workflow."})}},applyRecommendation(e){this.$emit("show-notification",{type:"success",message:`Applied recommendation: ${e.title}`}),this.recommendations=this.recommendations.filter((t=>t.id!==e.id)),this.securityScore+=5,this.securityScore>100&&(this.securityScore=100)}}},w=i(6262);const x=(0,w.A)(v,[["render",g],["__scopeId","data-v-370ac8f5"]]);var S=x}}]);
//# sourceMappingURL=441.126ccf71.js.map