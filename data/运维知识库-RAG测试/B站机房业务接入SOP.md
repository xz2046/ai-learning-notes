# B站机房业务接入SOP

### 筛选符合业务要求的设备根据资源特征选择合适的B站业务进行交付

#### B站业务通用需求配置

*   NAT类型：1/2/4/6 
    
*   磁盘：最低配置：单机预期跑量的2倍ssd，推荐2.5倍。（单机3G跑量的推荐7T ssd盘）
    
*   CPU内存：3G跑量最低48核CPU，推荐64核以上；内存推荐为CPU核数的1.5倍以上。
    
*   设备配置和网络质量满足的情况下：b站单机跑量均值在3G左右，由此可以根据机房出口推算所需设备数量，100G出口推荐35台设备。（不同地区、异网条件会对跑量有较大影响，大批量上资源时建议先上两台设备测试跑量。）
    

#### B站机房业务

*   X86-B站APP(F2) --b站正常全天跑量业务。
    
*   X86-F2-B(机房交付) --b站全天跑量业务，也用于突发业务交付。
    
    *   **B站突发业务跑量时间：19：00-20：30**
        
    *   非突发时间段业务控量**不建议用控制实例数方式**，会导致业务缓存变慢，推荐整机限速或者业务限速的模式，**且不要完全限速**，单机至少留10M的用于业务心跳上报的带宽。
        
*   X86-B站APP(F2X) --20：30-22：00不跑资源或者20-22点需要切换异网标签资源交付业务。
    
    *   20：30-22：00不跑资源限速时间段需要有一定底量，不能完全限速或设备离线。
        
*   X86-F2L --适用于20：30后不跑资源交付。
    

#### 业务交付

*   在运控节点管理界面进行业务交付
    
    *   如果是切换业务，则直接选择更换业务，外部业务中选择对应业务，确定配置符合要求情况下直接强切交付。
        
    *   如果是内部招募解耦，则点更换业务后，选内部业务，选择对应appid进行交付，不同appid对应不同的业务组合。
        
*   节点管理页面使用问题可反馈董晓赟，或在运营提效使用反馈群中反馈
    

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbogrb9GOm9/img/6b4d9df2-df50-4971-bb3f-d0ccbecaa7d4.png)

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbogrb9GOm9/img/fd4557ec-cca6-4e1f-862e-11a6fabeb07c.png)![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbogrb9GOm9/img/24acf875-518a-4676-bd73-3b93e82d3d36.png)

### 业务交付后资源标签调整

###### b站跑本网同省资源标签打法：

*   需要同时打同省标签和本网对应的异网标签。如移动设备本网同省需要打同省标签和异网移动标签。（该方案近期会有调整，调整后再同步）
    

###### 不同的异网标签对业务跑量有影响，同一机房大规模交付后时需选择最优异网标签。有两种方案：

1.  **mtr工具探测，**在一个机房中找一台设备部署mtr，根据mtr探测结果选择交付标签。优点是快，部署几小时后即可有网络质量结论。缺点是对突发机房不适用，200M以下设备会判定为异常设备，无探测结果。
    
    *   **mtr部署方法**：wget [http://tw06d0006.onething.net/iaas\_tools/mtr\_exploration\_v2.01.tar.gz](http://tw06d0006.onething.net/iaas_tools/mtr_exploration_v2.01.tar.gz) -O /opt/mtr\_exploration.tar.gz;tar -zxf /opt/mtr\_exploration.tar.gz -C /opt/;sh /opt/mtr\_exploration/stop.sh;sh /opt/mtr\_exploration/start.sh 
        
    *   **mtr结果看板**：[https://ss-data.onething.net/superset/dashboard/1256/?native\_filters\_key=ED-iYJ9Z8LoOaBa79eNlAAp8TKmSoOWmf7d\_HiH0BcMS8VMK9oxA3mCT8QTEjn4Z](https://ss-data.onething.net/superset/dashboard/1256/?native_filters_key=ED-iYJ9Z8LoOaBa79eNlAAp8TKmSoOWmf7d_HiH0BcMS8VMK9oxA3mCT8QTEjn4Z)  输入部署的sn查看不同运营商对应各地区的网络质量重传情况。
        
    *   ![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbogrb9GOm9/img/174f9189-09bd-40d0-85e5-7065ceacef9b.png)
        

1.  找三台设备分别部署不同的异网标签（如本网移动跑异网设备，三台分别打异网电信、异网联通和异网电信联通双标签），看跑量变化，优势：通用性强、结果明确。缺点是需要业务有一定缓存后才能看出明显区别，需要时间。可以配合mtr同时进行测试。
    
    ###### 需要定时切异网标签资源配置方法：
    
    *   配置位置在运控的节点管理界面，点击更换业务后勾选定时切换。该功能支持单次切换和每天定时切换。需要注意根据资源要求设置对应的资源标签切换时间，要给业务标签切换生效留一定调度生效时间，10分钟左右。
        
    *   ![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbogrb9GOm9/img/4ab1ca41-5b55-4c0e-a5c4-ba017c8670d8.png)
        

### 业务交付后关注指标

#### 网络质量

1.  需要关注机房晚高峰期间的丢包和重传情况，丢包会直接影响业务跑量。
    
    *   如果是定时切异网设备需要关注切异网后的网络质量情况
        
2.  B站业务重传情况：
    
    *   实时查看方法：B站业务诊断脚本：wget -O /tmp/CheckBz.py   [http://tw06d0006.onething.net/yangxy/CheckBz.py](http://tw06d0006.onething.net/yangxy/CheckBz.py)  && chmod +x /tmp/CheckBz.py   &&python /tmp/CheckBz.py 输出会包含B站业务进程和重传数据信息
        
    *   历史数据查看：bizdoc看板：[https://ss-data.onething.net/superset/dashboard/1261/?native\_filters\_key=wMMcmoDLJ256\_M3OtPQxgxtZXbKhvwu66-6zPaPSN\_IZ9m5geoYVR154rf2aIAPZ](https://ss-data.onething.net/superset/dashboard/1261/?native_filters_key=wMMcmoDLJ256_M3OtPQxgxtZXbKhvwu66-6zPaPSN_IZ9m5geoYVR154rf2aIAPZ)
        
3.  特殊资源需要本网异网运营商跑量情况：
    
    *   本网异网数据看板：[https://ss-data.onething.net/superset/dashboard/1276/?native\_filters\_key=Qmx1RemfzfTxFLeqijcA52oyQSrkT15AK4p3vE4g4CLGbCjQjRmiRi6oSUn4bv9p](https://ss-data.onething.net/superset/dashboard/1276/?native_filters_key=Qmx1RemfzfTxFLeqijcA52oyQSrkT15AK4p3vE4g4CLGbCjQjRmiRi6oSUn4bv9p)
        
    *   视界数据表查询：[https://horizon-data.onething.net/?pid=6304&menu\_id=8774](https://horizon-data.onething.net/?pid=6304&menu_id=8774)
        
    *   ![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbogrb9GOm9/img/6855fe2e-5457-46b1-a02b-73258bc39a5e.png)
        

#### 计费数据

1.  关注机房是否亏损。--联系机房运营同学查询
    
2.  关注机房计费带宽数据。 --联系成本同学查询