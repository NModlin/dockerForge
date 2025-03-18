"use strict";(self["webpackChunkdockerforge_web_ui"]=self["webpackChunkdockerforge_web_ui"]||[]).push([[722],{722:function(e,t,l){l.r(t),l.d(t,{default:function(){return v}});var a=l(641),o=l(33);const n={class:"volume-detail"},u={key:0,class:"d-flex justify-center align-center my-5"},s={key:0},r={class:"mt-2 text-center"};function d(e,t,l,d,i,c){const m=(0,a.g2)("v-icon"),k=(0,a.g2)("v-btn"),v=(0,a.g2)("v-col"),g=(0,a.g2)("v-row"),_=(0,a.g2)("v-progress-circular"),b=(0,a.g2)("v-alert"),f=(0,a.g2)("v-spacer"),h=(0,a.g2)("v-card-title"),F=(0,a.g2)("v-chip"),p=(0,a.g2)("v-simple-table"),y=(0,a.g2)("v-card-text"),W=(0,a.g2)("v-card"),L=(0,a.g2)("v-progress-linear"),C=(0,a.g2)("v-list-item-icon"),D=(0,a.g2)("v-list-item-title"),w=(0,a.g2)("v-list-item-subtitle"),X=(0,a.g2)("v-list-item-content"),x=(0,a.g2)("v-list-item"),V=(0,a.g2)("v-list"),P=(0,a.g2)("v-card-actions"),z=(0,a.g2)("v-dialog");return(0,a.uX)(),(0,a.CE)("div",n,[(0,a.bF)(g,null,{default:(0,a.k6)((()=>[(0,a.bF)(v,{cols:"12"},{default:(0,a.k6)((()=>[(0,a.bF)(k,{text:"",to:"/volumes",class:"mb-4"},{default:(0,a.k6)((()=>[(0,a.bF)(m,{left:""},{default:(0,a.k6)((()=>t[2]||(t[2]=[(0,a.eW)("mdi-arrow-left")]))),_:1}),t[3]||(t[3]=(0,a.eW)(" Back to Volumes "))])),_:1})])),_:1})])),_:1}),i.loading?((0,a.uX)(),(0,a.CE)("div",u,[(0,a.bF)(_,{indeterminate:"",color:"primary"})])):i.error?((0,a.uX)(),(0,a.Wv)(b,{key:1,type:"error",class:"mb-4"},{default:(0,a.k6)((()=>[(0,a.eW)((0,o.v_)(i.error),1)])),_:1})):i.volume?((0,a.uX)(),(0,a.Wv)(g,{key:3},{default:(0,a.k6)((()=>[(0,a.bF)(v,{cols:"12",md:"8"},{default:(0,a.k6)((()=>[(0,a.bF)(W,{class:"mb-4"},{default:(0,a.k6)((()=>[(0,a.bF)(h,{class:"headline"},{default:(0,a.k6)((()=>[(0,a.eW)((0,o.v_)(i.volume.name)+" ",1),(0,a.bF)(f),(0,a.bF)(k,{color:"error",text:"",onClick:c.showDeleteDialog},{default:(0,a.k6)((()=>[(0,a.bF)(m,{left:""},{default:(0,a.k6)((()=>t[5]||(t[5]=[(0,a.eW)("mdi-delete")]))),_:1}),t[6]||(t[6]=(0,a.eW)(" Delete "))])),_:1},8,["onClick"])])),_:1}),(0,a.bF)(y,null,{default:(0,a.k6)((()=>[(0,a.bF)(p,null,{default:(0,a.k6)((()=>[(0,a.Lk)("tbody",null,[(0,a.Lk)("tr",null,[t[7]||(t[7]=(0,a.Lk)("td",{class:"font-weight-bold"},"ID",-1)),(0,a.Lk)("td",null,(0,o.v_)(i.volume.id),1)]),(0,a.Lk)("tr",null,[t[8]||(t[8]=(0,a.Lk)("td",{class:"font-weight-bold"},"Driver",-1)),(0,a.Lk)("td",null,(0,o.v_)(i.volume.driver),1)]),(0,a.Lk)("tr",null,[t[9]||(t[9]=(0,a.Lk)("td",{class:"font-weight-bold"},"Mount Point",-1)),(0,a.Lk)("td",null,(0,o.v_)(i.volume.mountpoint),1)]),(0,a.Lk)("tr",null,[t[10]||(t[10]=(0,a.Lk)("td",{class:"font-weight-bold"},"Size",-1)),(0,a.Lk)("td",null,(0,o.v_)(i.volume.size),1)]),(0,a.Lk)("tr",null,[t[11]||(t[11]=(0,a.Lk)("td",{class:"font-weight-bold"},"Created",-1)),(0,a.Lk)("td",null,(0,o.v_)(c.formatDate(i.volume.created_at)),1)]),i.volume.labels&&Object.keys(i.volume.labels).length>0?((0,a.uX)(),(0,a.CE)("tr",s,[t[12]||(t[12]=(0,a.Lk)("td",{class:"font-weight-bold"},"Labels",-1)),(0,a.Lk)("td",null,[((0,a.uX)(!0),(0,a.CE)(a.FK,null,(0,a.pI)(i.volume.labels,((e,t)=>((0,a.uX)(),(0,a.Wv)(F,{key:t,class:"mr-2 mb-2",small:""},{default:(0,a.k6)((()=>[(0,a.eW)((0,o.v_)(t)+": "+(0,o.v_)(e),1)])),_:2},1024)))),128))])])):(0,a.Q3)("",!0)])])),_:1})])),_:1})])),_:1})])),_:1}),(0,a.bF)(v,{cols:"12",md:"4"},{default:(0,a.k6)((()=>[(0,a.bF)(W,{class:"mb-4"},{default:(0,a.k6)((()=>[(0,a.bF)(h,null,{default:(0,a.k6)((()=>t[13]||(t[13]=[(0,a.eW)("Usage")]))),_:1}),(0,a.bF)(y,null,{default:(0,a.k6)((()=>[(0,a.bF)(L,{value:c.usagePercentage,height:"25",color:c.usageColor,striped:""},{default:(0,a.k6)((()=>[(0,a.Lk)("strong",null,(0,o.v_)(c.usagePercentage)+"%",1)])),_:1},8,["value","color"]),(0,a.Lk)("div",r,(0,o.v_)(i.volume.used||"0 B")+" / "+(0,o.v_)(i.volume.size||"0 B"),1)])),_:1})])),_:1}),(0,a.bF)(W,null,{default:(0,a.k6)((()=>[(0,a.bF)(h,null,{default:(0,a.k6)((()=>t[14]||(t[14]=[(0,a.eW)("Connected Containers")]))),_:1}),0===i.connectedContainers.length?((0,a.uX)(),(0,a.Wv)(y,{key:0},{default:(0,a.k6)((()=>t[15]||(t[15]=[(0,a.Lk)("p",{class:"text-center"},"No containers are using this volume",-1)]))),_:1})):((0,a.uX)(),(0,a.Wv)(V,{key:1,dense:""},{default:(0,a.k6)((()=>[((0,a.uX)(!0),(0,a.CE)(a.FK,null,(0,a.pI)(i.connectedContainers,(e=>((0,a.uX)(),(0,a.Wv)(x,{key:e.id,to:`/containers/${e.id}`},{default:(0,a.k6)((()=>[(0,a.bF)(C,null,{default:(0,a.k6)((()=>[(0,a.bF)(m,{color:"running"===e.status?"success":"grey"},{default:(0,a.k6)((()=>t[16]||(t[16]=[(0,a.eW)(" mdi-docker ")]))),_:2},1032,["color"])])),_:2},1024),(0,a.bF)(X,null,{default:(0,a.k6)((()=>[(0,a.bF)(D,null,{default:(0,a.k6)((()=>[(0,a.eW)((0,o.v_)(e.name),1)])),_:2},1024),(0,a.bF)(w,null,{default:(0,a.k6)((()=>[(0,a.eW)((0,o.v_)(e.status),1)])),_:2},1024)])),_:2},1024)])),_:2},1032,["to"])))),128))])),_:1}))])),_:1})])),_:1})])),_:1})):((0,a.uX)(),(0,a.Wv)(b,{key:2,type:"warning",class:"mb-4"},{default:(0,a.k6)((()=>t[4]||(t[4]=[(0,a.eW)(" Volume not found ")]))),_:1})),(0,a.bF)(z,{modelValue:i.deleteDialog,"onUpdate:modelValue":t[1]||(t[1]=e=>i.deleteDialog=e),"max-width":"500"},{default:(0,a.k6)((()=>[(0,a.bF)(W,null,{default:(0,a.k6)((()=>[(0,a.bF)(h,{class:"headline"},{default:(0,a.k6)((()=>t[17]||(t[17]=[(0,a.eW)("Delete Volume")]))),_:1}),(0,a.bF)(y,null,{default:(0,a.k6)((()=>[t[18]||(t[18]=(0,a.eW)(" Are you sure you want to delete the volume ")),(0,a.Lk)("strong",null,(0,o.v_)(i.volume?.name),1),t[19]||(t[19]=(0,a.eW)("? This action cannot be undone and may result in data loss. ")),i.connectedContainers.length>0?((0,a.uX)(),(0,a.Wv)(b,{key:0,type:"warning",class:"mt-3",dense:""},{default:(0,a.k6)((()=>[(0,a.eW)(" This volume is currently used by "+(0,o.v_)(i.connectedContainers.length)+" container(s). Deleting it may cause those containers to malfunction. ",1)])),_:1})):(0,a.Q3)("",!0)])),_:1}),(0,a.bF)(P,null,{default:(0,a.k6)((()=>[(0,a.bF)(f),(0,a.bF)(k,{color:"grey darken-1",text:"",onClick:t[0]||(t[0]=e=>i.deleteDialog=!1)},{default:(0,a.k6)((()=>t[20]||(t[20]=[(0,a.eW)(" Cancel ")]))),_:1}),(0,a.bF)(k,{color:"red darken-1",text:"",onClick:c.deleteVolume},{default:(0,a.k6)((()=>t[21]||(t[21]=[(0,a.eW)(" Delete ")]))),_:1},8,["onClick"])])),_:1})])),_:1})])),_:1},8,["modelValue"])])}var i=l(2977),c={name:"VolumeDetail",data(){return{loading:!0,error:null,volume:null,connectedContainers:[],deleteDialog:!1}},computed:{...(0,i.L8)({isAuthenticated:"auth/isAuthenticated",token:"auth/token"}),usagePercentage(){return this.volume&&this.volume.used&&this.volume.size?Math.min(Math.round(parseInt(this.volume.used)/parseInt(this.volume.size)*100),100):0},usageColor(){return this.usagePercentage>90?"error":this.usagePercentage>70?"warning":"success"}},created(){this.fetchVolumeDetails()},methods:{async fetchVolumeDetails(){this.loading=!0,this.error=null;try{setTimeout((()=>{this.volume={id:this.$route.params.id,name:"postgres_data",driver:"local",mountpoint:"/var/lib/docker/volumes/postgres_data/_data",size:"1.2 GB",used:"800 MB",created_at:"2025-03-15T10:00:00Z",labels:{"com.example.description":"PostgreSQL Data","com.example.environment":"production"}},this.connectedContainers=[{id:"c1",name:"postgres",status:"running"}],this.loading=!1}),1e3)}catch(e){this.error="Failed to load volume details. Please try again.",this.loading=!1}},formatDate(e){const t=new Date(e);return t.toLocaleString()},showDeleteDialog(){this.deleteDialog=!0},async deleteVolume(){try{this.$router.push("/volumes")}catch(e){this.error=`Failed to delete volume ${this.volume.name}`,this.deleteDialog=!1}}}},m=l(6262);const k=(0,m.A)(c,[["render",d],["__scopeId","data-v-0bbd8c9e"]]);var v=k}}]);