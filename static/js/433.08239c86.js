"use strict";(self["webpackChunkdockerforge_web_ui"]=self["webpackChunkdockerforge_web_ui"]||[]).push([[433],{5433:function(e,l,t){t.r(l),t.d(l,{default:function(){return _}});var a=t(641),u=t(33);const n={class:"image-detail"};function d(e,l,t,d,i,o){const s=(0,a.g2)("v-icon"),k=(0,a.g2)("v-spacer"),r=(0,a.g2)("v-btn"),c=(0,a.g2)("v-card-title"),_=(0,a.g2)("v-skeleton-loader"),f=(0,a.g2)("v-card-text"),b=(0,a.g2)("v-alert"),m=(0,a.g2)("v-list-item-title"),g=(0,a.g2)("v-list-item-subtitle"),h=(0,a.g2)("v-list-item-content"),v=(0,a.g2)("v-list-item"),F=(0,a.g2)("v-chip"),y=(0,a.g2)("v-list"),W=(0,a.g2)("v-col"),p=(0,a.g2)("v-row"),L=(0,a.g2)("v-divider"),I=(0,a.g2)("v-tab"),C=(0,a.g2)("v-tabs"),X=(0,a.g2)("v-simple-table"),w=(0,a.g2)("v-card"),S=(0,a.g2)("v-tab-item"),E=(0,a.g2)("v-tabs-items"),x=(0,a.g2)("v-container"),V=(0,a.g2)("v-snackbar");return(0,a.uX)(),(0,a.CE)("div",n,[(0,a.bF)(x,{fluid:""},{default:(0,a.k6)((()=>[(0,a.bF)(p,null,{default:(0,a.k6)((()=>[(0,a.bF)(W,{cols:"12"},{default:(0,a.k6)((()=>[(0,a.bF)(w,null,{default:(0,a.k6)((()=>[(0,a.bF)(c,{class:"headline"},{default:(0,a.k6)((()=>[(0,a.bF)(s,{large:"",left:""},{default:(0,a.k6)((()=>l[4]||(l[4]=[(0,a.eW)("mdi-docker")]))),_:1}),l[7]||(l[7]=(0,a.eW)(" Image Details ")),(0,a.bF)(k),(0,a.bF)(r,{color:"primary",onClick:o.goBack},{default:(0,a.k6)((()=>[(0,a.bF)(s,{left:""},{default:(0,a.k6)((()=>l[5]||(l[5]=[(0,a.eW)("mdi-arrow-left")]))),_:1}),l[6]||(l[6]=(0,a.eW)(" Back to Images "))])),_:1},8,["onClick"])])),_:1}),i.loading?((0,a.uX)(),(0,a.Wv)(f,{key:0},{default:(0,a.k6)((()=>[(0,a.bF)(_,{type:"article"})])),_:1})):e.image?((0,a.uX)(),(0,a.CE)(a.FK,{key:2},[(0,a.bF)(f,null,{default:(0,a.k6)((()=>[(0,a.bF)(p,null,{default:(0,a.k6)((()=>[(0,a.bF)(W,{cols:"12",md:"6"},{default:(0,a.k6)((()=>[(0,a.bF)(y,{dense:""},{default:(0,a.k6)((()=>[(0,a.bF)(v,null,{default:(0,a.k6)((()=>[(0,a.bF)(h,null,{default:(0,a.k6)((()=>[(0,a.bF)(m,null,{default:(0,a.k6)((()=>l[9]||(l[9]=[(0,a.eW)("ID")]))),_:1}),(0,a.bF)(g,null,{default:(0,a.k6)((()=>[(0,a.eW)((0,u.v_)(e.image.id),1)])),_:1})])),_:1})])),_:1}),(0,a.bF)(v,null,{default:(0,a.k6)((()=>[(0,a.bF)(h,null,{default:(0,a.k6)((()=>[(0,a.bF)(m,null,{default:(0,a.k6)((()=>l[10]||(l[10]=[(0,a.eW)("Short ID")]))),_:1}),(0,a.bF)(g,null,{default:(0,a.k6)((()=>[(0,a.eW)((0,u.v_)(e.image.short_id),1)])),_:1})])),_:1})])),_:1}),(0,a.bF)(v,null,{default:(0,a.k6)((()=>[(0,a.bF)(h,null,{default:(0,a.k6)((()=>[(0,a.bF)(m,null,{default:(0,a.k6)((()=>l[11]||(l[11]=[(0,a.eW)("Tags")]))),_:1}),(0,a.bF)(g,null,{default:(0,a.k6)((()=>[((0,a.uX)(!0),(0,a.CE)(a.FK,null,(0,a.pI)(e.image.tags,(e=>((0,a.uX)(),(0,a.Wv)(F,{key:e,class:"ma-1",small:"",color:"primary","text-color":"white"},{default:(0,a.k6)((()=>[(0,a.eW)((0,u.v_)(e),1)])),_:2},1024)))),128))])),_:1})])),_:1})])),_:1}),(0,a.bF)(v,null,{default:(0,a.k6)((()=>[(0,a.bF)(h,null,{default:(0,a.k6)((()=>[(0,a.bF)(m,null,{default:(0,a.k6)((()=>l[12]||(l[12]=[(0,a.eW)("Size")]))),_:1}),(0,a.bF)(g,null,{default:(0,a.k6)((()=>[(0,a.eW)((0,u.v_)(o.formatSize(e.image.size)),1)])),_:1})])),_:1})])),_:1}),(0,a.bF)(v,null,{default:(0,a.k6)((()=>[(0,a.bF)(h,null,{default:(0,a.k6)((()=>[(0,a.bF)(m,null,{default:(0,a.k6)((()=>l[13]||(l[13]=[(0,a.eW)("Created")]))),_:1}),(0,a.bF)(g,null,{default:(0,a.k6)((()=>[(0,a.eW)((0,u.v_)(o.formatDate(e.image.created_at)),1)])),_:1})])),_:1})])),_:1})])),_:1})])),_:1}),(0,a.bF)(W,{cols:"12",md:"6"},{default:(0,a.k6)((()=>[(0,a.bF)(y,{dense:""},{default:(0,a.k6)((()=>[e.image.author?((0,a.uX)(),(0,a.Wv)(v,{key:0},{default:(0,a.k6)((()=>[(0,a.bF)(h,null,{default:(0,a.k6)((()=>[(0,a.bF)(m,null,{default:(0,a.k6)((()=>l[14]||(l[14]=[(0,a.eW)("Author")]))),_:1}),(0,a.bF)(g,null,{default:(0,a.k6)((()=>[(0,a.eW)((0,u.v_)(e.image.author),1)])),_:1})])),_:1})])),_:1})):(0,a.Q3)("",!0),e.image.architecture?((0,a.uX)(),(0,a.Wv)(v,{key:1},{default:(0,a.k6)((()=>[(0,a.bF)(h,null,{default:(0,a.k6)((()=>[(0,a.bF)(m,null,{default:(0,a.k6)((()=>l[15]||(l[15]=[(0,a.eW)("Architecture")]))),_:1}),(0,a.bF)(g,null,{default:(0,a.k6)((()=>[(0,a.eW)((0,u.v_)(e.image.architecture),1)])),_:1})])),_:1})])),_:1})):(0,a.Q3)("",!0),e.image.os?((0,a.uX)(),(0,a.Wv)(v,{key:2},{default:(0,a.k6)((()=>[(0,a.bF)(h,null,{default:(0,a.k6)((()=>[(0,a.bF)(m,null,{default:(0,a.k6)((()=>l[16]||(l[16]=[(0,a.eW)("OS")]))),_:1}),(0,a.bF)(g,null,{default:(0,a.k6)((()=>[(0,a.eW)((0,u.v_)(e.image.os),1)])),_:1})])),_:1})])),_:1})):(0,a.Q3)("",!0),e.image.digest?((0,a.uX)(),(0,a.Wv)(v,{key:3},{default:(0,a.k6)((()=>[(0,a.bF)(h,null,{default:(0,a.k6)((()=>[(0,a.bF)(m,null,{default:(0,a.k6)((()=>l[17]||(l[17]=[(0,a.eW)("Digest")]))),_:1}),(0,a.bF)(g,null,{default:(0,a.k6)((()=>[(0,a.eW)((0,u.v_)(e.image.digest),1)])),_:1})])),_:1})])),_:1})):(0,a.Q3)("",!0)])),_:1})])),_:1})])),_:1})])),_:1}),(0,a.bF)(L),(0,a.bF)(C,{modelValue:i.activeTab,"onUpdate:modelValue":l[0]||(l[0]=e=>i.activeTab=e),"background-color":"primary",dark:""},{default:(0,a.k6)((()=>[(0,a.bF)(I,null,{default:(0,a.k6)((()=>l[18]||(l[18]=[(0,a.eW)("Labels")]))),_:1}),(0,a.bF)(I,null,{default:(0,a.k6)((()=>l[19]||(l[19]=[(0,a.eW)("Environment")]))),_:1}),(0,a.bF)(I,null,{default:(0,a.k6)((()=>l[20]||(l[20]=[(0,a.eW)("Ports")]))),_:1}),(0,a.bF)(I,null,{default:(0,a.k6)((()=>l[21]||(l[21]=[(0,a.eW)("Volumes")]))),_:1}),(0,a.bF)(I,null,{default:(0,a.k6)((()=>l[22]||(l[22]=[(0,a.eW)("Security")]))),_:1})])),_:1},8,["modelValue"]),(0,a.bF)(E,{modelValue:i.activeTab,"onUpdate:modelValue":l[1]||(l[1]=e=>i.activeTab=e)},{default:(0,a.k6)((()=>[(0,a.bF)(S,null,{default:(0,a.k6)((()=>[(0,a.bF)(w,{flat:""},{default:(0,a.k6)((()=>[(0,a.bF)(f,null,{default:(0,a.k6)((()=>[e.image.labels&&Object.keys(e.image.labels).length>0?((0,a.uX)(),(0,a.Wv)(X,{key:0},{default:(0,a.k6)((()=>[l[23]||(l[23]=(0,a.Lk)("thead",null,[(0,a.Lk)("tr",null,[(0,a.Lk)("th",null,"Key"),(0,a.Lk)("th",null,"Value")])],-1)),(0,a.Lk)("tbody",null,[((0,a.uX)(!0),(0,a.CE)(a.FK,null,(0,a.pI)(e.image.labels,((e,l)=>((0,a.uX)(),(0,a.CE)("tr",{key:l},[(0,a.Lk)("td",null,(0,u.v_)(l),1),(0,a.Lk)("td",null,(0,u.v_)(e),1)])))),128))])])),_:1})):((0,a.uX)(),(0,a.Wv)(b,{key:1,type:"info"},{default:(0,a.k6)((()=>l[24]||(l[24]=[(0,a.eW)("No labels found")]))),_:1}))])),_:1})])),_:1})])),_:1}),(0,a.bF)(S,null,{default:(0,a.k6)((()=>[(0,a.bF)(w,{flat:""},{default:(0,a.k6)((()=>[(0,a.bF)(f,null,{default:(0,a.k6)((()=>[e.image.env&&e.image.env.length>0?((0,a.uX)(),(0,a.Wv)(X,{key:0},{default:(0,a.k6)((()=>[l[25]||(l[25]=(0,a.Lk)("thead",null,[(0,a.Lk)("tr",null,[(0,a.Lk)("th",null,"Key"),(0,a.Lk)("th",null,"Value")])],-1)),(0,a.Lk)("tbody",null,[((0,a.uX)(!0),(0,a.CE)(a.FK,null,(0,a.pI)(e.image.env,(e=>((0,a.uX)(),(0,a.CE)("tr",{key:e.key},[(0,a.Lk)("td",null,(0,u.v_)(e.key),1),(0,a.Lk)("td",null,(0,u.v_)(e.value),1)])))),128))])])),_:1})):((0,a.uX)(),(0,a.Wv)(b,{key:1,type:"info"},{default:(0,a.k6)((()=>l[26]||(l[26]=[(0,a.eW)("No environment variables found")]))),_:1}))])),_:1})])),_:1})])),_:1}),(0,a.bF)(S,null,{default:(0,a.k6)((()=>[(0,a.bF)(w,{flat:""},{default:(0,a.k6)((()=>[(0,a.bF)(f,null,{default:(0,a.k6)((()=>[e.image.exposed_ports&&e.image.exposed_ports.length>0?((0,a.uX)(),(0,a.Wv)(X,{key:0},{default:(0,a.k6)((()=>[l[27]||(l[27]=(0,a.Lk)("thead",null,[(0,a.Lk)("tr",null,[(0,a.Lk)("th",null,"Container Port"),(0,a.Lk)("th",null,"Protocol")])],-1)),(0,a.Lk)("tbody",null,[((0,a.uX)(!0),(0,a.CE)(a.FK,null,(0,a.pI)(e.image.exposed_ports,(e=>((0,a.uX)(),(0,a.CE)("tr",{key:`${e.container_port}-${e.protocol}`},[(0,a.Lk)("td",null,(0,u.v_)(e.container_port),1),(0,a.Lk)("td",null,(0,u.v_)(e.protocol),1)])))),128))])])),_:1})):((0,a.uX)(),(0,a.Wv)(b,{key:1,type:"info"},{default:(0,a.k6)((()=>l[28]||(l[28]=[(0,a.eW)("No exposed ports found")]))),_:1}))])),_:1})])),_:1})])),_:1}),(0,a.bF)(S,null,{default:(0,a.k6)((()=>[(0,a.bF)(w,{flat:""},{default:(0,a.k6)((()=>[(0,a.bF)(f,null,{default:(0,a.k6)((()=>[e.image.volumes&&e.image.volumes.length>0?((0,a.uX)(),(0,a.Wv)(X,{key:0},{default:(0,a.k6)((()=>[l[29]||(l[29]=(0,a.Lk)("thead",null,[(0,a.Lk)("tr",null,[(0,a.Lk)("th",null,"Container Path"),(0,a.Lk)("th",null,"Mode")])],-1)),(0,a.Lk)("tbody",null,[((0,a.uX)(!0),(0,a.CE)(a.FK,null,(0,a.pI)(e.image.volumes,(e=>((0,a.uX)(),(0,a.CE)("tr",{key:e.container_path},[(0,a.Lk)("td",null,(0,u.v_)(e.container_path),1),(0,a.Lk)("td",null,(0,u.v_)(e.mode||"rw"),1)])))),128))])])),_:1})):((0,a.uX)(),(0,a.Wv)(b,{key:1,type:"info"},{default:(0,a.k6)((()=>l[30]||(l[30]=[(0,a.eW)("No volumes found")]))),_:1}))])),_:1})])),_:1})])),_:1}),(0,a.bF)(S,null,{default:(0,a.k6)((()=>[(0,a.bF)(w,{flat:""},{default:(0,a.k6)((()=>[(0,a.bF)(f,null,{default:(0,a.k6)((()=>[(0,a.bF)(p,null,{default:(0,a.k6)((()=>[(0,a.bF)(W,{cols:"12"},{default:(0,a.k6)((()=>[(0,a.bF)(r,{color:"primary",onClick:o.scanImage,loading:i.scanning},{default:(0,a.k6)((()=>[(0,a.bF)(s,{left:""},{default:(0,a.k6)((()=>l[31]||(l[31]=[(0,a.eW)("mdi-shield-search")]))),_:1}),l[32]||(l[32]=(0,a.eW)(" Scan for Vulnerabilities "))])),_:1},8,["onClick","loading"])])),_:1})])),_:1}),e.scans.length>0?((0,a.uX)(),(0,a.Wv)(p,{key:0},{default:(0,a.k6)((()=>[(0,a.bF)(W,{cols:"12"},{default:(0,a.k6)((()=>[l[35]||(l[35]=(0,a.Lk)("h3",null,"Scan History",-1)),(0,a.bF)(X,null,{default:(0,a.k6)((()=>[l[34]||(l[34]=(0,a.Lk)("thead",null,[(0,a.Lk)("tr",null,[(0,a.Lk)("th",null,"ID"),(0,a.Lk)("th",null,"Type"),(0,a.Lk)("th",null,"Status"),(0,a.Lk)("th",null,"Started"),(0,a.Lk)("th",null,"Completed"),(0,a.Lk)("th",null,"Vulnerabilities"),(0,a.Lk)("th",null,"Actions")])],-1)),(0,a.Lk)("tbody",null,[((0,a.uX)(!0),(0,a.CE)(a.FK,null,(0,a.pI)(e.scans,(e=>((0,a.uX)(),(0,a.CE)("tr",{key:e.id},[(0,a.Lk)("td",null,(0,u.v_)(e.id),1),(0,a.Lk)("td",null,(0,u.v_)(e.scan_type),1),(0,a.Lk)("td",null,[(0,a.bF)(F,{small:"",color:o.getScanStatusColor(e.status),"text-color":"white"},{default:(0,a.k6)((()=>[(0,a.eW)((0,u.v_)(e.status),1)])),_:2},1032,["color"])]),(0,a.Lk)("td",null,(0,u.v_)(o.formatDate(e.started_at)),1),(0,a.Lk)("td",null,(0,u.v_)(o.formatDate(e.completed_at)),1),(0,a.Lk)("td",null,[e.critical_count>0?((0,a.uX)(),(0,a.Wv)(F,{key:0,small:"",color:"red","text-color":"white",class:"mr-1"},{default:(0,a.k6)((()=>[(0,a.eW)((0,u.v_)(e.critical_count)+" Critical ",1)])),_:2},1024)):(0,a.Q3)("",!0),e.high_count>0?((0,a.uX)(),(0,a.Wv)(F,{key:1,small:"",color:"orange","text-color":"white",class:"mr-1"},{default:(0,a.k6)((()=>[(0,a.eW)((0,u.v_)(e.high_count)+" High ",1)])),_:2},1024)):(0,a.Q3)("",!0),e.medium_count>0?((0,a.uX)(),(0,a.Wv)(F,{key:2,small:"",color:"yellow","text-color":"black",class:"mr-1"},{default:(0,a.k6)((()=>[(0,a.eW)((0,u.v_)(e.medium_count)+" Medium ",1)])),_:2},1024)):(0,a.Q3)("",!0),e.low_count>0?((0,a.uX)(),(0,a.Wv)(F,{key:3,small:"",color:"blue","text-color":"white"},{default:(0,a.k6)((()=>[(0,a.eW)((0,u.v_)(e.low_count)+" Low ",1)])),_:2},1024)):(0,a.Q3)("",!0)]),(0,a.Lk)("td",null,[(0,a.bF)(r,{icon:"",small:"",onClick:l=>o.viewScanDetails(e.id),disabled:"completed"!==e.status},{default:(0,a.k6)((()=>[(0,a.bF)(s,{small:""},{default:(0,a.k6)((()=>l[33]||(l[33]=[(0,a.eW)("mdi-eye")]))),_:1})])),_:2},1032,["onClick","disabled"])])])))),128))])])),_:1})])),_:1})])),_:1})):((0,a.uX)(),(0,a.Wv)(p,{key:1},{default:(0,a.k6)((()=>[(0,a.bF)(W,{cols:"12"},{default:(0,a.k6)((()=>[(0,a.bF)(b,{type:"info"},{default:(0,a.k6)((()=>l[36]||(l[36]=[(0,a.eW)("No security scans have been performed on this image")]))),_:1})])),_:1})])),_:1}))])),_:1})])),_:1})])),_:1})])),_:1},8,["modelValue"])],64)):((0,a.uX)(),(0,a.Wv)(f,{key:1},{default:(0,a.k6)((()=>[(0,a.bF)(b,{type:"error"},{default:(0,a.k6)((()=>l[8]||(l[8]=[(0,a.eW)("Image not found")]))),_:1})])),_:1}))])),_:1})])),_:1})])),_:1})])),_:1}),(0,a.bF)(V,{modelValue:i.snackbar,"onUpdate:modelValue":l[3]||(l[3]=e=>i.snackbar=e),color:i.snackbarColor,timeout:3e3},{action:(0,a.k6)((({attrs:e})=>[(0,a.bF)(r,(0,a.v6)({text:""},e,{onClick:l[2]||(l[2]=e=>i.snackbar=!1)}),{default:(0,a.k6)((()=>l[37]||(l[37]=[(0,a.eW)("Close")]))),_:2},1040)])),default:(0,a.k6)((()=>[(0,a.eW)((0,u.v_)(i.snackbarText)+" ",1)])),_:1},8,["modelValue","color"])])}var i=t(2977),o=t(9061),s=t(5794),k={name:"ImageDetail",data(){return{activeTab:0,loading:!1,scanning:!1,snackbar:!1,snackbarText:"",snackbarColor:"success"}},computed:{...(0,i.aH)("images",["image","scans"]),imageId(){return this.$route.params.id}},created(){this.fetchImageDetails(),this.fetchImageScans()},methods:{...(0,i.i0)("images",["getImage","getImageScans","scanImageVulnerabilities"]),async fetchImageDetails(){this.loading=!0;try{await this.getImage(this.imageId)}catch(e){this.showError("Failed to fetch image details: "+e.message)}finally{this.loading=!1}},async fetchImageScans(){try{await this.getImageScans(this.imageId)}catch(e){this.showError("Failed to fetch image scans: "+e.message)}},async scanImage(){this.scanning=!0;try{await this.scanImageVulnerabilities(this.imageId),this.showSuccess("Security scan initiated"),await this.fetchImageScans()}catch(e){this.showError("Failed to scan image: "+e.message)}finally{this.scanning=!1}},viewScanDetails(e){this.$router.push({name:"ImageSecurity",params:{id:this.imageId,scanId:e}})},goBack(){this.$router.push({name:"Images"})},formatSize(e){if(!e)return"Unknown";const l=["B","KB","MB","GB","TB"];let t=e,a=0;while(t>=1024&&a<l.length-1)t/=1024,a++;return`${t.toFixed(2)} ${l[a]}`},formatDate(e){if(!e)return"Unknown";try{return(0,o.A)((0,s.A)(e),"MMM d, yyyy HH:mm")}catch(l){return e}},getScanStatusColor(e){switch(e){case"completed":return"success";case"running":return"info";case"failed":return"error";default:return"grey"}},showSuccess(e){this.snackbarText=e,this.snackbarColor="success",this.snackbar=!0},showError(e){this.snackbarText=e,this.snackbarColor="error",this.snackbar=!0}}},r=t(6262);const c=(0,r.A)(k,[["render",d],["__scopeId","data-v-5ae86ad1"]]);var _=c}}]);