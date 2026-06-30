# F2X 机房特殊资源运维

### 一、资源汇总

资源登记链接：[请至钉钉文档查看附件《【资源服务】F2\_F2X业务日常资源问题处理.axls》。](https://alidocs.dingtalk.com/i/nodes/YMyQA2dXW7rgjA9wCMr3YDP48zlwrZgb?iframeQuery=anchorId%3DX02mmn62abluapga65iu8)\-F2X-F2L批量资源跟踪-

#### 20-22点不跑机房：sdk656、sdk683    

*   混跑方案：web主跑，web+zj盒子或者  web+aqy+zj盒子
    
*   qos：未设置
    
    ### 20-22点异网，其他时间本网机房：
    
*   江苏移动sdk634、439、537、538、669、721（537、634机房计划3.13日下掉）
    
*   河南移动：738
    
*   湖北联通：712，跑量好，未设置qos
    
*   浙江移动：526，跑量好，未设置qos，机房侧有限速
    
*   青海移动：742  
    
*   同一混跑编排：80bz+30aqy+10hpg
    
    *   {  "mix\_task\_rate": {  "068bb25bbc7d6e80e55a28adc6ac16ac": 1,  "4302b8560ef96866804e14e397dee75b": 1,  "e64463abbd738698bfab3e3902b08f46": 1  },  "mix\_task\_list": \[  "e64463abbd738698bfab3e3902b08f46",  "068bb25bbc7d6e80e55a28adc6ac16ac",  "4302b8560ef96866804e14e397dee75b"  \],  "nic\_alloc\_type": "host",  "mix\_task\_instance\_limit": {  "068bb25bbc7d6e80e55a28adc6ac16ac": 30,  "4302b8560ef96866804e14e397dee75b": 10,  "e64463abbd738698bfab3e3902b08f46": 90  },  "priority\_conf": {  "068bb25bbc7d6e80e55a28adc6ac16ac": 2,  "4302b8560ef96866804e14e397dee75b": 1,  "e64463abbd738698bfab3e3902b08f46": 2  },  "docker\_flag\_map": null }
        
*   qos 设置（当前aqy主跑qos设置机房：721、538部分新交设备，其余均为app高优方案）：
    
    *   b站app高优方案qos，通过spec中conf控制b站在18-20点跑量情况
        
    *   {"enable":true,"rules":\[{"st":"17:10","et":"20:05","s\_buffer":30,"e\_buffer":5,"coef":0.5,"high":\[42868\],"low":\[41962,16913\],"spec":\[{"appid":"e64463abbd738698bfab3e3902b08f46","coef":0.55}\]},{"st":"20:00","et":"20:50","s\_buffer":5,"e\_buffer":10,"coef":0.25,"high":\[42868\],"low":\[41962,16913\]},{"st":"0:20","et":"8:00","s\_buffer":20,"e\_buffer":30,"coef":0.4,"high":\[41962\],"low":\[42868,16913\]}\]}
        
    *   aqy主跑方案，17-20点bz和aqy一块高优
        
    *   {"enable":true,"rules":\[{"st":"17:10","et":"20:05","s\_buffer":30,"e\_buffer":5,"coef":0.8,"high":\[42868,16913\],"low":\[41962\]},{"st":"20:00","et":"20:50","s\_buffer":5,"e\_buffer":10,"coef":0.25,"high":\[42868\],"low":\[41962,16913\]},{"st":"22:30","et":"8:00","s\_buffer":20,"e\_buffer":30,"coef":0.4,"high":\[41962,16913\],"low":\[42868\]}\]}
        

二、关注事项

1.  新交资源需要根据需要设置混跑编排、清理缓存和对应去qos配置
    
2.  进行qos修改后第二天关注一下业务波形是否符合预期，一般在视界：[https://horizon-data.onething.net/?pid=6304&menu\_id=9059](https://horizon-data.onething.net/?pid=6304&menu_id=9059)
    

3.关注机房计费比变化：问对应机房负责人要，或者找![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbRVENmQOm9/img/681fa7a7-96f9-4243-a291-94e0a45cdad5.png)

4.晚高峰同网异网流量占比情况，视界：[https://horizon-data.onething.net/?pid=6304&menu\_id=8774](https://horizon-data.onething.net/?pid=6304&menu_id=8774)