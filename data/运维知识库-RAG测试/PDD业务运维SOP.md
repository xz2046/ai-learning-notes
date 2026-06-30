# PDD sop

PDD appid：

| 12712c9d757d5ae9cb34b6a29f1795bd | pdd X86独跑 |
| --- | --- |
| 20f397735f552a93f068753b1e00617b | pdd X86混跑 |
| d03b41e96a2614ad9ecd59adf3302ed7 | pdd X86混跑--同省 |

客户侧可能会让修改内核参数，该参数已在hook脚本中添加：

sysctl -w net.ipv6.neigh.default.gc\_thresh1=8192 sysctl -w net.ipv6.neigh.default.gc\_thresh2=16384 sysctl -w net.ipv6.neigh.default.gc\_thresh3=32768

### PDD异网补点：

客户要求appid：20f397735f552a93f068753b1e00617b下资源存储补低于160T，约390台资源

选点要求：

*   nat1/2/6；
    
*   只要三大运营商的，小运营商不要
    
*   跑满率2-7成；
    
*   单机带宽：300-2000M
    
*   地区：不要新疆、内蒙古、宁夏这些偏远地区的
    
*   丢包不要太严重的
    
*   磁盘带宽比1：1以上。
    
*   如果以上条件筛选设备够多，可以优先选华南华东地区设备，和线路数少的设备
    

主要交付来源V1腾挪

少量设备可以和博文对从V1每天新进设备里挪

大量交付走腾挪流程。

V1新进设备交付流程详细：

1.  捞取V1近一天新进设备：[https://tw15a0050.onething.net:17813/monitor/recruit/node\_list?&uuid=wxy01JY3QMR3T9MR314JDRRG0G4MK&day=1](https://tw15a0050.onething.net:17813/monitor/recruit/node_list?&uuid=wxy01JY3QMR3T9MR314JDRRG0G4MK&day=1)
    
2.  批量查询设备信息页面[https://tw15a0050.onething.net:17813/monitor/x86/bkj\_base\_info?&sn\_list=](https://tw15a0050.onething.net:17813/monitor/x86/bkj_base_info?&sn_list=)查询设备信息，结果粘贴到excel中过滤（是否离线，nat类型，是否同省，这个appid只交非同省设备，是否三大运营商，省份偏远地区去掉，整机带宽300-1700，磁盘带宽比1以上，cpu10核以上）
    
3.  剩余设备粘贴到基础指标看板中，去掉丢包过高设备![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbRVENmQOm9/img/48b2b105-eb27-45e1-8b90-17aa3478ace5.png)
    
4.  最终设备在表格中登记后，通过招募解耦到APPID:7b3b543ca4ed1b470d16350eb0e066ed的主跑方案。[请至钉钉文档查看附件《pdd 新进设备跑量跟踪》。](https://alidocs.dingtalk.com/i/nodes/EpGBa2Lm8ajZr3zQIweoKYBRWgN7R35y?iframeQuery=anchorId%3DX02mmp01u5lzih1fysexoc)
    
5.  腾挪后第二天跟踪跑量，低跑的回切appid：c90ebb2d73a3df5cafb121b88de96b79