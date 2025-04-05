"use strict";(self["webpackChunkdockerforge_web_ui"]=self["webpackChunkdockerforge_web_ui"]||[]).push([[249],{3249:function(e,t,a){a.r(t),a.d(t,{default:function(){return b}});var l=a(641),o=a(33);const s={class:"backup-list"},r={key:0,class:"d-flex justify-center align-center my-5"},i={class:"text-body-1 mt-2"},u={class:"font-weight-medium"},c={class:"text-caption"};function n(e,t,a,n,d,p){const k=(0,l.g2)("v-text-field"),m=(0,l.g2)("v-col"),b=(0,l.g2)("v-select"),g=(0,l.g2)("v-icon"),f=(0,l.g2)("v-btn"),h=(0,l.g2)("v-row"),B=(0,l.g2)("v-card-text"),y=(0,l.g2)("v-card"),F=(0,l.g2)("v-progress-circular"),_=(0,l.g2)("v-alert"),v=(0,l.g2)("v-chip"),w=(0,l.g2)("v-data-table"),V=(0,l.g2)("v-card-title"),C=(0,l.g2)("v-textarea"),D=(0,l.g2)("v-checkbox"),x=(0,l.g2)("v-form"),W=(0,l.g2)("v-spacer"),T=(0,l.g2)("v-card-actions"),z=(0,l.g2)("v-dialog");return(0,l.uX)(),(0,l.CE)("div",s,[t[40]||(t[40]=(0,l.Lk)("h1",{class:"text-h4 mb-4"},"Backups",-1)),(0,l.bF)(y,{class:"mb-4"},{default:(0,l.k6)((()=>[(0,l.bF)(B,null,{default:(0,l.k6)((()=>[(0,l.bF)(h,null,{default:(0,l.k6)((()=>[(0,l.bF)(m,{cols:"12",sm:"4"},{default:(0,l.k6)((()=>[(0,l.bF)(k,{modelValue:d.filters.name,"onUpdate:modelValue":t[0]||(t[0]=e=>d.filters.name=e),label:"Filter by name","prepend-icon":"mdi-magnify",clearable:"",onInput:p.applyFilters},null,8,["modelValue","onInput"])])),_:1}),(0,l.bF)(m,{cols:"12",sm:"4"},{default:(0,l.k6)((()=>[(0,l.bF)(b,{modelValue:d.filters.type,"onUpdate:modelValue":t[1]||(t[1]=e=>d.filters.type=e),items:d.backupTypeOptions,label:"Filter by type","prepend-icon":"mdi-filter",clearable:"",onChange:p.applyFilters},null,8,["modelValue","items","onChange"])])),_:1}),(0,l.bF)(m,{cols:"12",sm:"4",class:"d-flex align-center justify-end"},{default:(0,l.k6)((()=>[(0,l.bF)(f,{color:"primary",onClick:p.showCreateBackupDialog},{default:(0,l.k6)((()=>[(0,l.bF)(g,{left:""},{default:(0,l.k6)((()=>t[17]||(t[17]=[(0,l.eW)("mdi-plus")]))),_:1}),t[18]||(t[18]=(0,l.eW)(" Create Backup "))])),_:1},8,["onClick"])])),_:1})])),_:1})])),_:1})])),_:1}),d.loading?((0,l.uX)(),(0,l.CE)("div",r,[(0,l.bF)(F,{indeterminate:"",color:"primary"})])):d.error?((0,l.uX)(),(0,l.Wv)(_,{key:1,type:"error",class:"mb-4"},{default:(0,l.k6)((()=>[(0,l.eW)((0,o.v_)(d.error),1)])),_:1})):0===d.backups.length?((0,l.uX)(),(0,l.Wv)(y,{key:2,class:"mb-4 text-center pa-5"},{default:(0,l.k6)((()=>[(0,l.bF)(g,{size:"64",color:"grey lighten-1"},{default:(0,l.k6)((()=>t[19]||(t[19]=[(0,l.eW)("mdi-backup-restore")]))),_:1}),t[22]||(t[22]=(0,l.Lk)("h3",{class:"text-h5 mt-4"},"No backups found",-1)),(0,l.Lk)("p",i,(0,o.v_)(d.filters.name||d.filters.type?"Try adjusting your filters":"Create your first backup to protect your data"),1),(0,l.bF)(f,{color:"primary",class:"mt-4",onClick:p.showCreateBackupDialog},{default:(0,l.k6)((()=>[(0,l.bF)(g,{left:""},{default:(0,l.k6)((()=>t[20]||(t[20]=[(0,l.eW)("mdi-plus")]))),_:1}),t[21]||(t[21]=(0,l.eW)(" Create Backup "))])),_:1},8,["onClick"])])),_:1})):((0,l.uX)(),(0,l.Wv)(y,{key:3},{default:(0,l.k6)((()=>[(0,l.bF)(w,{headers:d.headers,items:d.backups,"items-per-page":10,"footer-props":{"items-per-page-options":[5,10,15,20]},class:"elevation-1"},{"item.name":(0,l.k6)((({item:e})=>[(0,l.Lk)("div",u,(0,o.v_)(e.name),1),(0,l.Lk)("div",c,(0,o.v_)(e.description),1)])),"item.type":(0,l.k6)((({item:e})=>[(0,l.bF)(v,{color:p.getBackupTypeColor(e.type),"text-color":"white",small:""},{default:(0,l.k6)((()=>[(0,l.eW)((0,o.v_)(e.type),1)])),_:2},1032,["color"])])),"item.status":(0,l.k6)((({item:e})=>[(0,l.bF)(v,{color:p.getStatusColor(e.status),"text-color":"white",small:""},{default:(0,l.k6)((()=>[(0,l.eW)((0,o.v_)(e.status),1)])),_:2},1032,["color"])])),"item.size":(0,l.k6)((({item:e})=>[(0,l.eW)((0,o.v_)(p.formatSize(e.size)),1)])),"item.created_at":(0,l.k6)((({item:e})=>[(0,l.eW)((0,o.v_)(p.formatDate(e.created_at)),1)])),"item.actions":(0,l.k6)((({item:e})=>[(0,l.bF)(f,{icon:"",small:"",onClick:t=>p.showRestoreDialog(e),title:"Restore",disabled:"completed"!==e.status},{default:(0,l.k6)((()=>[(0,l.bF)(g,{small:""},{default:(0,l.k6)((()=>t[23]||(t[23]=[(0,l.eW)("mdi-backup-restore")]))),_:1})])),_:2},1032,["onClick","disabled"]),(0,l.bF)(f,{icon:"",small:"",onClick:t=>p.downloadBackup(e),title:"Download",disabled:"completed"!==e.status},{default:(0,l.k6)((()=>[(0,l.bF)(g,{small:""},{default:(0,l.k6)((()=>t[24]||(t[24]=[(0,l.eW)("mdi-download")]))),_:1})])),_:2},1032,["onClick","disabled"]),(0,l.bF)(f,{icon:"",small:"",onClick:t=>p.showDeleteDialog(e),title:"Delete"},{default:(0,l.k6)((()=>[(0,l.bF)(g,{small:""},{default:(0,l.k6)((()=>t[25]||(t[25]=[(0,l.eW)("mdi-delete")]))),_:1})])),_:2},1032,["onClick"])])),_:1},8,["headers","items"])])),_:1})),(0,l.bF)(z,{modelValue:d.createBackupDialog,"onUpdate:modelValue":t[10]||(t[10]=e=>d.createBackupDialog=e),"max-width":"600"},{default:(0,l.k6)((()=>[(0,l.bF)(y,null,{default:(0,l.k6)((()=>[(0,l.bF)(V,{class:"headline"},{default:(0,l.k6)((()=>t[26]||(t[26]=[(0,l.eW)("Create Backup")]))),_:1}),(0,l.bF)(B,null,{default:(0,l.k6)((()=>[(0,l.bF)(x,{ref:"createBackupForm",modelValue:d.createBackupFormValid,"onUpdate:modelValue":t[8]||(t[8]=e=>d.createBackupFormValid=e)},{default:(0,l.k6)((()=>[(0,l.bF)(k,{modelValue:d.newBackup.name,"onUpdate:modelValue":t[2]||(t[2]=e=>d.newBackup.name=e),label:"Backup Name",rules:[e=>!!e||"Name is required"],required:""},null,8,["modelValue","rules"]),(0,l.bF)(C,{modelValue:d.newBackup.description,"onUpdate:modelValue":t[3]||(t[3]=e=>d.newBackup.description=e),label:"Description",rows:"2"},null,8,["modelValue"]),(0,l.bF)(b,{modelValue:d.newBackup.type,"onUpdate:modelValue":t[4]||(t[4]=e=>d.newBackup.type=e),items:d.backupTypeOptions,label:"Backup Type",rules:[e=>!!e||"Type is required"],required:""},null,8,["modelValue","items","rules"]),(0,l.bF)(b,{modelValue:d.newBackup.resources,"onUpdate:modelValue":t[5]||(t[5]=e=>d.newBackup.resources=e),items:d.resourceOptions,label:"Resources to Backup",multiple:"",chips:"",rules:[e=>e.length>0||"Select at least one resource"],required:""},null,8,["modelValue","items","rules"]),(0,l.bF)(D,{modelValue:d.newBackup.includeVolumes,"onUpdate:modelValue":t[6]||(t[6]=e=>d.newBackup.includeVolumes=e),label:"Include volumes"},null,8,["modelValue"]),(0,l.bF)(D,{modelValue:d.newBackup.compress,"onUpdate:modelValue":t[7]||(t[7]=e=>d.newBackup.compress=e),label:"Compress backup"},null,8,["modelValue"])])),_:1},8,["modelValue"])])),_:1}),(0,l.bF)(T,null,{default:(0,l.k6)((()=>[(0,l.bF)(W),(0,l.bF)(f,{color:"grey darken-1",text:"",onClick:t[9]||(t[9]=e=>d.createBackupDialog=!1)},{default:(0,l.k6)((()=>t[27]||(t[27]=[(0,l.eW)(" Cancel ")]))),_:1}),(0,l.bF)(f,{color:"primary",text:"",onClick:p.createBackup,disabled:!d.createBackupFormValid||d.creatingBackup,loading:d.creatingBackup},{default:(0,l.k6)((()=>t[28]||(t[28]=[(0,l.eW)(" Create ")]))),_:1},8,["onClick","disabled","loading"])])),_:1})])),_:1})])),_:1},8,["modelValue"]),(0,l.bF)(z,{modelValue:d.restoreDialog,"onUpdate:modelValue":t[14]||(t[14]=e=>d.restoreDialog=e),"max-width":"500"},{default:(0,l.k6)((()=>[(0,l.bF)(y,null,{default:(0,l.k6)((()=>[(0,l.bF)(V,{class:"headline"},{default:(0,l.k6)((()=>t[29]||(t[29]=[(0,l.eW)("Restore Backup")]))),_:1}),(0,l.bF)(B,null,{default:(0,l.k6)((()=>[t[31]||(t[31]=(0,l.eW)(" Are you sure you want to restore the backup ")),(0,l.Lk)("strong",null,(0,o.v_)(d.selectedBackup?.name),1),t[32]||(t[32]=(0,l.eW)("? ")),(0,l.bF)(_,{type:"warning",class:"mt-3",dense:""},{default:(0,l.k6)((()=>t[30]||(t[30]=[(0,l.eW)(" This will replace your current data with the backup data. This action cannot be undone. ")]))),_:1}),(0,l.bF)(D,{modelValue:d.restoreOptions.includeVolumes,"onUpdate:modelValue":t[11]||(t[11]=e=>d.restoreOptions.includeVolumes=e),label:"Restore volumes",class:"mt-4"},null,8,["modelValue"]),(0,l.bF)(D,{modelValue:d.restoreOptions.stopContainers,"onUpdate:modelValue":t[12]||(t[12]=e=>d.restoreOptions.stopContainers=e),label:"Stop running containers before restore",class:"mt-2"},null,8,["modelValue"])])),_:1}),(0,l.bF)(T,null,{default:(0,l.k6)((()=>[(0,l.bF)(W),(0,l.bF)(f,{color:"grey darken-1",text:"",onClick:t[13]||(t[13]=e=>d.restoreDialog=!1)},{default:(0,l.k6)((()=>t[33]||(t[33]=[(0,l.eW)(" Cancel ")]))),_:1}),(0,l.bF)(f,{color:"warning",text:"",onClick:p.restoreBackup,loading:d.restoringBackup},{default:(0,l.k6)((()=>t[34]||(t[34]=[(0,l.eW)(" Restore ")]))),_:1},8,["onClick","loading"])])),_:1})])),_:1})])),_:1},8,["modelValue"]),(0,l.bF)(z,{modelValue:d.deleteDialog,"onUpdate:modelValue":t[16]||(t[16]=e=>d.deleteDialog=e),"max-width":"500"},{default:(0,l.k6)((()=>[(0,l.bF)(y,null,{default:(0,l.k6)((()=>[(0,l.bF)(V,{class:"headline"},{default:(0,l.k6)((()=>t[35]||(t[35]=[(0,l.eW)("Delete Backup")]))),_:1}),(0,l.bF)(B,null,{default:(0,l.k6)((()=>[t[36]||(t[36]=(0,l.eW)(" Are you sure you want to delete the backup ")),(0,l.Lk)("strong",null,(0,o.v_)(d.selectedBackup?.name),1),t[37]||(t[37]=(0,l.eW)("? This action cannot be undone. "))])),_:1}),(0,l.bF)(T,null,{default:(0,l.k6)((()=>[(0,l.bF)(W),(0,l.bF)(f,{color:"grey darken-1",text:"",onClick:t[15]||(t[15]=e=>d.deleteDialog=!1)},{default:(0,l.k6)((()=>t[38]||(t[38]=[(0,l.eW)(" Cancel ")]))),_:1}),(0,l.bF)(f,{color:"red darken-1",text:"",onClick:p.deleteBackup},{default:(0,l.k6)((()=>t[39]||(t[39]=[(0,l.eW)(" Delete ")]))),_:1},8,["onClick"])])),_:1})])),_:1})])),_:1},8,["modelValue"])])}var d=a(2977),p={name:"BackupList",data(){return{loading:!0,error:null,backups:[],filters:{name:"",type:""},backupTypeOptions:[{text:"All",value:""},{text:"Full",value:"full"},{text:"Containers",value:"containers"},{text:"Images",value:"images"},{text:"Volumes",value:"volumes"},{text:"Configuration",value:"config"}],resourceOptions:["All Containers","All Images","All Volumes","All Networks","Docker Configuration"],headers:[{text:"Name",value:"name",sortable:!0},{text:"Type",value:"type",sortable:!0},{text:"Status",value:"status",sortable:!0},{text:"Size",value:"size",sortable:!0},{text:"Created",value:"created_at",sortable:!0},{text:"Actions",value:"actions",sortable:!1,align:"center"}],createBackupDialog:!1,createBackupFormValid:!1,creatingBackup:!1,newBackup:{name:"",description:"",type:"full",resources:["All Containers"],includeVolumes:!0,compress:!0},restoreDialog:!1,restoringBackup:!1,restoreOptions:{includeVolumes:!0,stopContainers:!0},deleteDialog:!1,selectedBackup:null}},computed:{...(0,d.L8)({isAuthenticated:"auth/isAuthenticated",token:"auth/token"})},created(){this.fetchBackups()},methods:{async fetchBackups(){this.loading=!0,this.error=null;try{setTimeout((()=>{this.backups=[{id:"b1",name:"Weekly Full Backup",description:"Automated weekly backup of all resources",type:"full",status:"completed",size:2684354560,created_at:"2025-03-16T00:00:00Z"},{id:"b2",name:"Pre-deployment Backup",description:"Manual backup before major deployment",type:"containers",status:"completed",size:536870912,created_at:"2025-03-15T12:00:00Z"},{id:"b3",name:"Database Volumes",description:"Backup of database volumes only",type:"volumes",status:"completed",size:1288490188.8,created_at:"2025-03-14T08:00:00Z"},{id:"b4",name:"Configuration Backup",description:"Docker daemon and container configurations",type:"config",status:"completed",size:5242880,created_at:"2025-03-13T16:00:00Z"},{id:"b5",name:"Image Repository",description:"Backup of all local images",type:"images",status:"in-progress",size:0,created_at:"2025-03-17T05:30:00Z"}],this.loading=!1}),1e3)}catch(e){this.error="Failed to load backups. Please try again.",this.loading=!1}},applyFilters(){this.fetchBackups()},formatDate(e){const t=new Date(e);return t.toLocaleString()},formatSize(e){if(0===e)return"0 Bytes";const t=1024,a=["Bytes","KB","MB","GB","TB"],l=Math.floor(Math.log(e)/Math.log(t));return parseFloat((e/Math.pow(t,l)).toFixed(2))+" "+a[l]},getBackupTypeColor(e){switch(e){case"full":return"primary";case"containers":return"success";case"images":return"info";case"volumes":return"warning";case"config":return"purple";default:return"grey"}},getStatusColor(e){switch(e){case"completed":return"success";case"in-progress":return"info";case"failed":return"error";default:return"grey"}},showCreateBackupDialog(){this.newBackup={name:"",description:"",type:"full",resources:["All Containers"],includeVolumes:!0,compress:!0},this.createBackupDialog=!0},async createBackup(){if(this.$refs.createBackupForm.validate()){this.creatingBackup=!0;try{setTimeout((()=>{const e=`b${this.backups.length+1}`,t=(new Date).toISOString();this.backups.unshift({id:e,name:this.newBackup.name,description:this.newBackup.description,type:this.newBackup.type,status:"in-progress",size:0,created_at:t}),setTimeout((()=>{const t=this.backups.findIndex((t=>t.id===e));-1!==t&&(this.backups[t].status="completed",this.backups[t].size=1024*Math.random()*1024*1024*3,this.$forceUpdate())}),3e3),this.createBackupDialog=!1,this.creatingBackup=!1}),1e3)}catch(e){this.error="Failed to create backup. Please try again.",this.creatingBackup=!1}}},showRestoreDialog(e){this.selectedBackup=e,this.restoreOptions={includeVolumes:!0,stopContainers:!0},this.restoreDialog=!0},async restoreBackup(){this.restoringBackup=!0;try{setTimeout((()=>{this.restoreDialog=!1,this.restoringBackup=!1,this.$emit("show-notification",{type:"success",message:`Backup ${this.selectedBackup.name} restored successfully`})}),2e3)}catch(e){this.error=`Failed to restore backup ${this.selectedBackup.name}`,this.restoringBackup=!1}},downloadBackup(e){this.$emit("show-notification",{type:"info",message:`Downloading backup: ${e.name} (${this.formatSize(e.size)})`})},showDeleteDialog(e){this.selectedBackup=e,this.deleteDialog=!0},async deleteBackup(){if(this.selectedBackup)try{this.backups=this.backups.filter((e=>e.id!==this.selectedBackup.id)),this.deleteDialog=!1,this.selectedBackup=null}catch(e){this.error=`Failed to delete backup ${this.selectedBackup.name}`,this.deleteDialog=!1}}}},k=a(6262);const m=(0,k.A)(p,[["render",n],["__scopeId","data-v-9b0d349c"]]);var b=m}}]);
//# sourceMappingURL=249.1126387c.js.map