"use strict";(self["webpackChunkdockerforge_web_ui"]=self["webpackChunkdockerforge_web_ui"]||[]).push([[814],{2814:function(e,t,l){l.r(t),l.d(t,{default:function(){return b}});var n=l(641),o=l(33);const r={class:"network-detail"},a={key:0,class:"d-flex justify-center align-center my-5"},d={key:0};function s(e,t,l,s,i,u){const k=(0,n.g2)("v-icon"),c=(0,n.g2)("v-btn"),b=(0,n.g2)("v-col"),g=(0,n.g2)("v-row"),w=(0,n.g2)("v-progress-circular"),_=(0,n.g2)("v-alert"),m=(0,n.g2)("v-chip"),v=(0,n.g2)("v-spacer"),f=(0,n.g2)("v-card-title"),h=(0,n.g2)("v-simple-table"),p=(0,n.g2)("v-card-text"),y=(0,n.g2)("v-card"),F=(0,n.g2)("v-list-item-icon"),L=(0,n.g2)("v-list-item-title"),C=(0,n.g2)("v-list-item-subtitle"),W=(0,n.g2)("v-list-item-content"),D=(0,n.g2)("v-list-item"),N=(0,n.g2)("v-list"),X=(0,n.g2)("v-card-actions"),x=(0,n.g2)("v-dialog");return(0,n.uX)(),(0,n.CE)("div",r,[(0,n.bF)(g,null,{default:(0,n.k6)((()=>[(0,n.bF)(b,{cols:"12"},{default:(0,n.k6)((()=>[(0,n.bF)(c,{text:"",to:"/networks",class:"mb-4"},{default:(0,n.k6)((()=>[(0,n.bF)(k,{left:""},{default:(0,n.k6)((()=>t[2]||(t[2]=[(0,n.eW)("mdi-arrow-left")]))),_:1}),t[3]||(t[3]=(0,n.eW)(" Back to Networks "))])),_:1})])),_:1})])),_:1}),i.loading?((0,n.uX)(),(0,n.CE)("div",a,[(0,n.bF)(w,{indeterminate:"",color:"primary"})])):i.error?((0,n.uX)(),(0,n.Wv)(_,{key:1,type:"error",class:"mb-4"},{default:(0,n.k6)((()=>[(0,n.eW)((0,o.v_)(i.error),1)])),_:1})):i.network?((0,n.uX)(),(0,n.Wv)(g,{key:3},{default:(0,n.k6)((()=>[(0,n.bF)(b,{cols:"12",md:"8"},{default:(0,n.k6)((()=>[(0,n.bF)(y,{class:"mb-4"},{default:(0,n.k6)((()=>[(0,n.bF)(f,{class:"headline"},{default:(0,n.k6)((()=>[(0,n.eW)((0,o.v_)(i.network.name)+" ",1),(0,n.bF)(m,{class:"ml-2",color:u.getScopeColor(i.network.scope),"text-color":"white",small:""},{default:(0,n.k6)((()=>[(0,n.eW)((0,o.v_)(i.network.scope),1)])),_:1},8,["color"]),(0,n.bF)(v),(0,n.bF)(c,{color:"error",text:"",onClick:u.showDeleteDialog,disabled:u.isDefaultNetwork},{default:(0,n.k6)((()=>[(0,n.bF)(k,{left:""},{default:(0,n.k6)((()=>t[5]||(t[5]=[(0,n.eW)("mdi-delete")]))),_:1}),t[6]||(t[6]=(0,n.eW)(" Delete "))])),_:1},8,["onClick","disabled"])])),_:1}),(0,n.bF)(p,null,{default:(0,n.k6)((()=>[(0,n.bF)(h,null,{default:(0,n.k6)((()=>[(0,n.Lk)("tbody",null,[(0,n.Lk)("tr",null,[t[7]||(t[7]=(0,n.Lk)("td",{class:"font-weight-bold"},"ID",-1)),(0,n.Lk)("td",null,(0,o.v_)(i.network.id),1)]),(0,n.Lk)("tr",null,[t[8]||(t[8]=(0,n.Lk)("td",{class:"font-weight-bold"},"Driver",-1)),(0,n.Lk)("td",null,(0,o.v_)(i.network.driver),1)]),(0,n.Lk)("tr",null,[t[9]||(t[9]=(0,n.Lk)("td",{class:"font-weight-bold"},"Subnet",-1)),(0,n.Lk)("td",null,(0,o.v_)(i.network.subnet),1)]),(0,n.Lk)("tr",null,[t[10]||(t[10]=(0,n.Lk)("td",{class:"font-weight-bold"},"Gateway",-1)),(0,n.Lk)("td",null,(0,o.v_)(i.network.gateway||"N/A"),1)]),(0,n.Lk)("tr",null,[t[11]||(t[11]=(0,n.Lk)("td",{class:"font-weight-bold"},"IP Range",-1)),(0,n.Lk)("td",null,(0,o.v_)(i.network.ip_range||"N/A"),1)]),(0,n.Lk)("tr",null,[t[12]||(t[12]=(0,n.Lk)("td",{class:"font-weight-bold"},"Internal",-1)),(0,n.Lk)("td",null,(0,o.v_)(i.network.internal?"Yes":"No"),1)]),(0,n.Lk)("tr",null,[t[13]||(t[13]=(0,n.Lk)("td",{class:"font-weight-bold"},"Created",-1)),(0,n.Lk)("td",null,(0,o.v_)(u.formatDate(i.network.created_at)),1)]),i.network.labels&&Object.keys(i.network.labels).length>0?((0,n.uX)(),(0,n.CE)("tr",d,[t[14]||(t[14]=(0,n.Lk)("td",{class:"font-weight-bold"},"Labels",-1)),(0,n.Lk)("td",null,[((0,n.uX)(!0),(0,n.CE)(n.FK,null,(0,n.pI)(i.network.labels,((e,t)=>((0,n.uX)(),(0,n.Wv)(m,{key:t,class:"mr-2 mb-2",small:""},{default:(0,n.k6)((()=>[(0,n.eW)((0,o.v_)(t)+": "+(0,o.v_)(e),1)])),_:2},1024)))),128))])])):(0,n.Q3)("",!0)])])),_:1})])),_:1})])),_:1}),i.network.options&&Object.keys(i.network.options).length>0?((0,n.uX)(),(0,n.Wv)(y,{key:0,class:"mb-4"},{default:(0,n.k6)((()=>[(0,n.bF)(f,null,{default:(0,n.k6)((()=>t[15]||(t[15]=[(0,n.eW)("Network Options")]))),_:1}),(0,n.bF)(p,null,{default:(0,n.k6)((()=>[(0,n.bF)(h,null,{default:(0,n.k6)((()=>[t[16]||(t[16]=(0,n.Lk)("thead",null,[(0,n.Lk)("tr",null,[(0,n.Lk)("th",null,"Option"),(0,n.Lk)("th",null,"Value")])],-1)),(0,n.Lk)("tbody",null,[((0,n.uX)(!0),(0,n.CE)(n.FK,null,(0,n.pI)(i.network.options,((e,t)=>((0,n.uX)(),(0,n.CE)("tr",{key:t},[(0,n.Lk)("td",null,(0,o.v_)(t),1),(0,n.Lk)("td",null,(0,o.v_)(e),1)])))),128))])])),_:1})])),_:1})])),_:1})):(0,n.Q3)("",!0)])),_:1}),(0,n.bF)(b,{cols:"12",md:"4"},{default:(0,n.k6)((()=>[(0,n.bF)(y,null,{default:(0,n.k6)((()=>[(0,n.bF)(f,null,{default:(0,n.k6)((()=>t[17]||(t[17]=[(0,n.eW)("Connected Containers")]))),_:1}),0===i.connectedContainers.length?((0,n.uX)(),(0,n.Wv)(p,{key:0},{default:(0,n.k6)((()=>t[18]||(t[18]=[(0,n.Lk)("p",{class:"text-center"},"No containers are connected to this network",-1)]))),_:1})):((0,n.uX)(),(0,n.Wv)(N,{key:1,dense:""},{default:(0,n.k6)((()=>[((0,n.uX)(!0),(0,n.CE)(n.FK,null,(0,n.pI)(i.connectedContainers,(e=>((0,n.uX)(),(0,n.Wv)(D,{key:e.id,to:`/containers/${e.id}`},{default:(0,n.k6)((()=>[(0,n.bF)(F,null,{default:(0,n.k6)((()=>[(0,n.bF)(k,{color:"running"===e.status?"success":"grey"},{default:(0,n.k6)((()=>t[19]||(t[19]=[(0,n.eW)(" mdi-docker ")]))),_:2},1032,["color"])])),_:2},1024),(0,n.bF)(W,null,{default:(0,n.k6)((()=>[(0,n.bF)(L,null,{default:(0,n.k6)((()=>[(0,n.eW)((0,o.v_)(e.name),1)])),_:2},1024),(0,n.bF)(C,null,{default:(0,n.k6)((()=>[(0,n.eW)((0,o.v_)(e.ip_address||"No IP assigned"),1)])),_:2},1024)])),_:2},1024)])),_:2},1032,["to"])))),128))])),_:1}))])),_:1})])),_:1})])),_:1})):((0,n.uX)(),(0,n.Wv)(_,{key:2,type:"warning",class:"mb-4"},{default:(0,n.k6)((()=>t[4]||(t[4]=[(0,n.eW)(" Network not found ")]))),_:1})),(0,n.bF)(x,{modelValue:i.deleteDialog,"onUpdate:modelValue":t[1]||(t[1]=e=>i.deleteDialog=e),"max-width":"500"},{default:(0,n.k6)((()=>[(0,n.bF)(y,null,{default:(0,n.k6)((()=>[(0,n.bF)(f,{class:"headline"},{default:(0,n.k6)((()=>t[20]||(t[20]=[(0,n.eW)("Delete Network")]))),_:1}),(0,n.bF)(p,null,{default:(0,n.k6)((()=>[t[21]||(t[21]=(0,n.eW)(" Are you sure you want to delete the network ")),(0,n.Lk)("strong",null,(0,o.v_)(i.network?.name),1),t[22]||(t[22]=(0,n.eW)("? This action cannot be undone. ")),i.connectedContainers.length>0?((0,n.uX)(),(0,n.Wv)(_,{key:0,type:"warning",class:"mt-3",dense:""},{default:(0,n.k6)((()=>[(0,n.eW)(" This network is currently used by "+(0,o.v_)(i.connectedContainers.length)+" container(s). Deleting it may cause those containers to lose connectivity. ",1)])),_:1})):(0,n.Q3)("",!0)])),_:1}),(0,n.bF)(X,null,{default:(0,n.k6)((()=>[(0,n.bF)(v),(0,n.bF)(c,{color:"grey darken-1",text:"",onClick:t[0]||(t[0]=e=>i.deleteDialog=!1)},{default:(0,n.k6)((()=>t[23]||(t[23]=[(0,n.eW)(" Cancel ")]))),_:1}),(0,n.bF)(c,{color:"red darken-1",text:"",onClick:u.deleteNetwork},{default:(0,n.k6)((()=>t[24]||(t[24]=[(0,n.eW)(" Delete ")]))),_:1},8,["onClick"])])),_:1})])),_:1})])),_:1},8,["modelValue"])])}var i=l(2977),u={name:"NetworkDetail",data(){return{loading:!0,error:null,network:null,connectedContainers:[],deleteDialog:!1}},computed:{...(0,i.L8)({isAuthenticated:"auth/isAuthenticated",token:"auth/token"}),isDefaultNetwork(){return!!this.network&&["bridge","host","none"].includes(this.network.name)}},created(){this.fetchNetworkDetails()},methods:{async fetchNetworkDetails(){this.loading=!0,this.error=null;try{setTimeout((()=>{"n1"===this.$route.params.id?(this.network={id:"n1",name:"bridge",driver:"bridge",subnet:"172.17.0.0/16",gateway:"172.17.0.1",scope:"local",internal:!1,created_at:"2025-03-15T10:00:00Z",options:{"com.docker.network.bridge.default_bridge":"true","com.docker.network.bridge.enable_icc":"true","com.docker.network.bridge.enable_ip_masquerade":"true","com.docker.network.bridge.host_binding_ipv4":"0.0.0.0","com.docker.network.bridge.name":"docker0","com.docker.network.driver.mtu":"1500"}},this.connectedContainers=[{id:"c1",name:"nginx",status:"running",ip_address:"172.17.0.2"},{id:"c2",name:"redis",status:"running",ip_address:"172.17.0.3"}]):"n4"===this.$route.params.id?(this.network={id:"n4",name:"app_network",driver:"bridge",subnet:"172.18.0.0/16",gateway:"172.18.0.1",scope:"local",internal:!1,created_at:"2025-03-16T09:00:00Z",labels:{"com.example.environment":"development","com.example.project":"dockerforge"}},this.connectedContainers=[{id:"c3",name:"postgres",status:"stopped",ip_address:"172.18.0.2"}]):"n5"===this.$route.params.id?(this.network={id:"n5",name:"overlay_network",driver:"overlay",subnet:"10.0.0.0/24",gateway:"10.0.0.1",scope:"swarm",internal:!1,created_at:"2025-03-16T08:00:00Z",options:{"com.docker.network.driver.overlay.vxlanid_list":"4097","com.docker.network.driver.overlay.mtu":"1450"}},this.connectedContainers=[]):(this.network={id:this.$route.params.id,name:"unknown_network",driver:"bridge",subnet:"192.168.0.0/24",gateway:"192.168.0.1",scope:"local",internal:!1,created_at:"2025-03-16T00:00:00Z"},this.connectedContainers=[]),this.loading=!1}),1e3)}catch(e){this.error="Failed to load network details. Please try again.",this.loading=!1}},formatDate(e){const t=new Date(e);return t.toLocaleString()},getScopeColor(e){switch(e){case"swarm":return"purple";case"global":return"blue";case"local":default:return"green"}},showDeleteDialog(){this.deleteDialog=!0},async deleteNetwork(){try{this.$router.push("/networks")}catch(e){this.error=`Failed to delete network ${this.network.name}`,this.deleteDialog=!1}}}},k=l(6262);const c=(0,k.A)(u,[["render",s],["__scopeId","data-v-67e3625e"]]);var b=c}}]);
//# sourceMappingURL=814.dc7d00e9.js.map