"use strict";(self["webpackChunkdockerforge_web_ui"]=self["webpackChunkdockerforge_web_ui"]||[]).push([[339],{4339:function(e,t,o){o.r(t),o.d(t,{default:function(){return p}});var a=o(641),l=o(33);const s={class:"compose-list"},r={key:0,class:"d-flex justify-center align-center my-5"},c={class:"text-body-1 mt-2"};function i(e,t,o,i,d,n){const u=(0,a.g2)("v-text-field"),m=(0,a.g2)("v-col"),p=(0,a.g2)("v-icon"),h=(0,a.g2)("v-btn"),k=(0,a.g2)("v-row"),f=(0,a.g2)("v-card-text"),g=(0,a.g2)("v-card"),b=(0,a.g2)("v-progress-circular"),_=(0,a.g2)("v-alert"),v=(0,a.g2)("router-link"),j=(0,a.g2)("v-chip"),F=(0,a.g2)("v-data-table"),y=(0,a.g2)("v-card-title"),C=(0,a.g2)("v-checkbox"),P=(0,a.g2)("v-spacer"),W=(0,a.g2)("v-card-actions"),x=(0,a.g2)("v-dialog");return(0,a.uX)(),(0,a.CE)("div",s,[t[18]||(t[18]=(0,a.Lk)("h1",{class:"text-h4 mb-4"},"Docker Compose",-1)),(0,a.bF)(g,{class:"mb-4"},{default:(0,a.k6)((()=>[(0,a.bF)(f,null,{default:(0,a.k6)((()=>[(0,a.bF)(k,null,{default:(0,a.k6)((()=>[(0,a.bF)(m,{cols:"12",sm:"6"},{default:(0,a.k6)((()=>[(0,a.bF)(u,{modelValue:d.filters.name,"onUpdate:modelValue":t[0]||(t[0]=e=>d.filters.name=e),label:"Filter by name","prepend-icon":"mdi-magnify",clearable:"",onInput:n.applyFilters},null,8,["modelValue","onInput"])])),_:1}),(0,a.bF)(m,{cols:"12",sm:"6",class:"d-flex align-center justify-end"},{default:(0,a.k6)((()=>[(0,a.bF)(h,{color:"primary",to:"/compose/create"},{default:(0,a.k6)((()=>[(0,a.bF)(p,{left:""},{default:(0,a.k6)((()=>t[4]||(t[4]=[(0,a.eW)("mdi-plus")]))),_:1}),t[5]||(t[5]=(0,a.eW)(" New Compose Project "))])),_:1})])),_:1})])),_:1})])),_:1})])),_:1}),d.loading?((0,a.uX)(),(0,a.CE)("div",r,[(0,a.bF)(b,{indeterminate:"",color:"primary"})])):d.error?((0,a.uX)(),(0,a.Wv)(_,{key:1,type:"error",class:"mb-4"},{default:(0,a.k6)((()=>[(0,a.eW)((0,l.v_)(d.error),1)])),_:1})):0===d.composeProjects.length?((0,a.uX)(),(0,a.Wv)(g,{key:2,class:"mb-4 text-center pa-5"},{default:(0,a.k6)((()=>[(0,a.bF)(p,{size:"64",color:"grey lighten-1"},{default:(0,a.k6)((()=>t[6]||(t[6]=[(0,a.eW)("mdi-docker")]))),_:1}),t[9]||(t[9]=(0,a.Lk)("h3",{class:"text-h5 mt-4"},"No compose projects found",-1)),(0,a.Lk)("p",c,(0,l.v_)(d.filters.name?"Try adjusting your filters":"Create your first compose project to get started"),1),(0,a.bF)(h,{color:"primary",class:"mt-4",to:"/compose/create"},{default:(0,a.k6)((()=>[(0,a.bF)(p,{left:""},{default:(0,a.k6)((()=>t[7]||(t[7]=[(0,a.eW)("mdi-plus")]))),_:1}),t[8]||(t[8]=(0,a.eW)(" New Compose Project "))])),_:1})])),_:1})):((0,a.uX)(),(0,a.Wv)(g,{key:3},{default:(0,a.k6)((()=>[(0,a.bF)(F,{headers:d.headers,items:d.composeProjects,"items-per-page":10,"footer-props":{"items-per-page-options":[5,10,15,20]},class:"elevation-1"},{"item.name":(0,a.k6)((({item:e})=>[(0,a.bF)(v,{to:`/compose/${e.id}`,class:"text-decoration-none"},{default:(0,a.k6)((()=>[(0,a.eW)((0,l.v_)(e.name),1)])),_:2},1032,["to"])])),"item.status":(0,a.k6)((({item:e})=>[(0,a.bF)(j,{color:n.getStatusColor(e.status),"text-color":"white",small:""},{default:(0,a.k6)((()=>[(0,a.eW)((0,l.v_)(e.status),1)])),_:2},1032,["color"])])),"item.created_at":(0,a.k6)((({item:e})=>[(0,a.eW)((0,l.v_)(n.formatDate(e.created_at)),1)])),"item.actions":(0,a.k6)((({item:e})=>[(0,a.bF)(h,{icon:"",small:"",disabled:"running"===e.status,onClick:t=>n.startComposeProject(e),title:"Start"},{default:(0,a.k6)((()=>[(0,a.bF)(p,{small:""},{default:(0,a.k6)((()=>t[10]||(t[10]=[(0,a.eW)("mdi-play")]))),_:1})])),_:2},1032,["disabled","onClick"]),(0,a.bF)(h,{icon:"",small:"",disabled:"running"!==e.status,onClick:t=>n.stopComposeProject(e),title:"Stop"},{default:(0,a.k6)((()=>[(0,a.bF)(p,{small:""},{default:(0,a.k6)((()=>t[11]||(t[11]=[(0,a.eW)("mdi-stop")]))),_:1})])),_:2},1032,["disabled","onClick"]),(0,a.bF)(h,{icon:"",small:"",onClick:t=>n.showDeleteDialog(e),title:"Delete"},{default:(0,a.k6)((()=>[(0,a.bF)(p,{small:""},{default:(0,a.k6)((()=>t[12]||(t[12]=[(0,a.eW)("mdi-delete")]))),_:1})])),_:2},1032,["onClick"])])),_:1},8,["headers","items"])])),_:1})),(0,a.bF)(x,{modelValue:d.deleteDialog,"onUpdate:modelValue":t[3]||(t[3]=e=>d.deleteDialog=e),"max-width":"500"},{default:(0,a.k6)((()=>[(0,a.bF)(g,null,{default:(0,a.k6)((()=>[(0,a.bF)(y,{class:"headline"},{default:(0,a.k6)((()=>t[13]||(t[13]=[(0,a.eW)("Delete Compose Project")]))),_:1}),(0,a.bF)(f,null,{default:(0,a.k6)((()=>[t[14]||(t[14]=(0,a.eW)(" Are you sure you want to delete the compose project ")),(0,a.Lk)("strong",null,(0,l.v_)(d.selectedProject?.name),1),t[15]||(t[15]=(0,a.eW)("? ")),(0,a.bF)(C,{modelValue:d.deleteWithVolumes,"onUpdate:modelValue":t[1]||(t[1]=e=>d.deleteWithVolumes=e),label:"Also remove associated volumes",class:"mt-4"},null,8,["modelValue"])])),_:1}),(0,a.bF)(W,null,{default:(0,a.k6)((()=>[(0,a.bF)(P),(0,a.bF)(h,{color:"grey darken-1",text:"",onClick:t[2]||(t[2]=e=>d.deleteDialog=!1)},{default:(0,a.k6)((()=>t[16]||(t[16]=[(0,a.eW)(" Cancel ")]))),_:1}),(0,a.bF)(h,{color:"red darken-1",text:"",onClick:n.deleteComposeProject},{default:(0,a.k6)((()=>t[17]||(t[17]=[(0,a.eW)(" Delete ")]))),_:1},8,["onClick"])])),_:1})])),_:1})])),_:1},8,["modelValue"])])}var d=o(2977),n={name:"ComposeList",data(){return{loading:!0,error:null,composeProjects:[],filters:{name:""},headers:[{text:"Name",value:"name",sortable:!0},{text:"Status",value:"status",sortable:!0},{text:"Services",value:"service_count",sortable:!0},{text:"Location",value:"location",sortable:!0},{text:"Created",value:"created_at",sortable:!0},{text:"Actions",value:"actions",sortable:!1,align:"center"}],deleteDialog:!1,selectedProject:null,deleteWithVolumes:!1}},computed:{...(0,d.L8)({isAuthenticated:"auth/isAuthenticated",token:"auth/token"})},created(){this.fetchComposeProjects()},methods:{async fetchComposeProjects(){this.loading=!0,this.error=null;try{setTimeout((()=>{this.composeProjects=[{id:"c1",name:"web-app",status:"running",service_count:3,location:"/home/user/projects/web-app",created_at:"2025-03-15T10:00:00Z"},{id:"c2",name:"database-cluster",status:"stopped",service_count:2,location:"/home/user/projects/database-cluster",created_at:"2025-03-14T09:00:00Z"},{id:"c3",name:"monitoring-stack",status:"running",service_count:4,location:"/home/user/projects/monitoring",created_at:"2025-03-13T08:00:00Z"}],this.loading=!1}),1e3)}catch(e){this.error="Failed to load compose projects. Please try again.",this.loading=!1}},applyFilters(){this.fetchComposeProjects()},formatDate(e){const t=new Date(e);return t.toLocaleString()},getStatusColor(e){switch(e){case"running":return"success";case"stopped":return"error";case"partial":return"warning";default:return"grey"}},async startComposeProject(e){try{e.status="running",this.$forceUpdate()}catch(t){this.error=`Failed to start compose project ${e.name}`}},async stopComposeProject(e){try{e.status="stopped",this.$forceUpdate()}catch(t){this.error=`Failed to stop compose project ${e.name}`}},showDeleteDialog(e){this.selectedProject=e,this.deleteWithVolumes=!1,this.deleteDialog=!0},async deleteComposeProject(){if(this.selectedProject)try{this.composeProjects=this.composeProjects.filter((e=>e.id!==this.selectedProject.id)),this.deleteDialog=!1,this.selectedProject=null}catch(e){this.error=`Failed to delete compose project ${this.selectedProject.name}`,this.deleteDialog=!1}}}},u=o(6262);const m=(0,u.A)(n,[["render",i],["__scopeId","data-v-0b845d93"]]);var p=m}}]);