# -*- coding: utf-8 -*-
import base64
import json
import os
import sys
import time
from threading import Thread
import flask
from flask import jsonify,Response
import Client_modal
import Mode_Tools
import Mode_ConfigFile
import prometheus_client
from prometheus_client.core import CollectorRegistry
from prometheus_client import Gauge,Counter,generate_latest
class Config(object):
    Sys_LocalAddress = None
    Sys_ListeningAddress = None
    Sys_ListeningPort = None
    Sys_KeyFilePath = None
    Sys_SystemKeyPath = None
    Sys_SystemKeyFileNode = None
    Sys_ProcessListCpuTop = None
    Sys_ProcessListMemTop = None
    Too_SystemShellRunKubeternets = None
    Cat_RegisterCatalog = None
    Cat_ServerCatalogAddress = None
    def init_Config(self,ConfigPath):
        Config = Mode_ConfigFile.ConfigFile()
        Config.init_class(ConfigPath,m_logs)
        self.Sys_LocalAddress = Config.ReadConfigFile("System","Local_Address")
        self.Sys_ListeningAddress = Config.ReadConfigFile("System","ListeningAddress")
        self.Sys_ListeningPort = Config.ReadConfigFile("System", "ListeningPort")
        self.Sys_KeyFilePath = Config.ReadConfigFile("System", "KeyFilePath")
        self.Sys_SystemKeyPath = Config.ReadConfigFile("System", "SystemKeyPath")
        self.Sys_SystemKeyFileNode = Config.ReadConfigFile("System", "SystemKeyFileNode")
        self.Sys_ProcessListCpuTop = int(Config.ReadConfigFile("System", "ProcessListCpuTop"))
        self.Sys_ProcessListMemTop = int(Config.ReadConfigFile("System", "ProcessListMemTop"))
        self.Too_SystemShellRunKubeternets = str(base64.b64decode(Config.ReadConfigFile("Tools", "SystemShellRunKubeternets")), encoding='utf-8')
        self.Cat_RegisterCatalog = bool(Config.ReadConfigFile("ServerCatalog", "RegisterCatalog"))
        self.Cat_ServerCatalogAddress = Config.ReadConfigFile("ServerCatalog", "ServerCatalogAddress")
        return True

m_Config = Config()
m_logs = Mode_Tools.logs()
obgect_flask = flask.Flask("Iecas")
m_Config.init_Config(os.path.dirname(sys.argv[0]) + "/Config/Agent.ini")

def API_Send_Data(object:str):
    m_http = flask.make_response(jsonify(object))  #响应体数据
    m_http.status = "200"
    m_http.headers ["Server"] = "Iecas"
    return m_http

#system_registry_auto = CollectorRegistry(auto_describe=False)
#@obgect_flask.route("/metrics",methods=['get','post'])
#def requests_count():
#    m_mem = Client_modal.get_free(False)
#    m_mem_gauge = []
#    m_buff_count = -1
#    for m_keyname in m_mem.keys():
#        m_buff_count += 1
#        m_mem_gauge.append(Gauge(str(m_keyname), "内存扩展信息",registry=system_registry_auto))
#        m_mem_gauge[m_buff_count].set(m_mem[m_keyname])
#    return Response(generate_latest(registry), mimetype="text/plain")


@obgect_flask.route("/run/<name>/<push>",methods=['get','post'])
def API_Shell_Run(name,push:None):
    m_file_mkdir = os.path.dirname(sys.argv[0]) + "/Plugin/" +  name
    if os.path.isfile(m_file_mkdir) == False:
        return "[ERROR]No File:{0}".format(m_file_mkdir)
    m_run_ret = os.popen('{0} {1}'.format(m_file_mkdir,push))
    m_run_ret = m_run_ret.read().strip()
    m_logs.info("请求执行脚本:{0} * 参数:{1} * 执行结果:{2}".format(m_file_mkdir,push,m_run_ret))
    m_check_values = m_run_ret.split("|")
    if len(m_check_values) != 2:
        return "[{0}][{1}]Error,push is >2.".format(m_file_mkdir,push)
    if m_check_values[0] != "str" and m_check_values[0] != "bool" and m_check_values[0] != "json":
        return "[{0}][{1}]Error,Ret Push Type ERROR.".format(m_file_mkdir,push)
    return m_run_ret

@obgect_flask.route('/',methods=['get'])
def API_index():
    return """<p style="text-align: center;"><span style="color: rgb(255, 0, 0); font-size: 24px;"><strong>404</strong></span></p><p style="text-align: center;"><strong>当前为代理端模块</strong></p><p style="text-align: center;"><strong>请求对应的API接口返回对应数据</strong></p><p style="text-align: center;"><strong>具体请参考API文档</strong></p>"""

@obgect_flask.route('/systemtake',methods=['get','post'])
def systemtake():
    m_values = None
    m_values = {
        'code': 200,
        'msg':"正常"
    }
    return API_Send_Data(m_values)


@obgect_flask.route('/get/system_info',methods=['get','post'])
def API_system_info():
    return API_Send_Data(Client_modal.get_sysinfo(m_Config.Too_SystemShellRunKubeternets))

@obgect_flask.route('/get/memory_info',methods=['get','post'])
def API_system_memory_info():
    m_format = flask.request.args.get("format").lower()
    if m_format == "true":
        m_format = True
    else:
        m_format = False
    return API_Send_Data(Client_modal.get_free(m_format))

@obgect_flask.route('/get/disk_status',methods=['get','post'])
def API_system_disk_status():
    m_format = flask.request.args.get("format").lower()
    if m_format == "true":
        m_format = True
    else:
        m_format = False
    return API_Send_Data(Client_modal.get_disk_used(m_format))

@obgect_flask.route('/get/network_status',methods=['get','post'])
def API_system_network_status():
    m_format = flask.request.args.get("format").lower()
    if m_format == "true":
        m_format = True
    else:
        m_format = False
    return API_Send_Data(Client_modal.get_network_used(m_format))

@obgect_flask.route('/get/cpu_usage',methods=['get','post'])
def API_system_cpu_usage():
    return API_Send_Data(Client_modal.get_cpu_usage())

@obgect_flask.route('/get/cpu_usage_info',methods=['get','post'])
def API_system_cpu_usage_info():
    return API_Send_Data(Client_modal.get_cpu_usage_info())

@obgect_flask.route('/get/disk_info',methods=['get','post'])
def API_system_disk_info():
    m_format = flask.request.args.get("format").lower()
    if m_format == "true":
        m_format = True
    else:
        m_format = False
    return API_Send_Data(Client_modal.get_disk_list(m_format))
@obgect_flask.route('/get/load_info',methods=['get','post'])
def API_system_load_info():
    return API_Send_Data(Client_modal.get_system_loadavg())

@obgect_flask.route('/get/time_info',methods=['get','post'])
def API_system_time_info():
    return API_Send_Data(Client_modal.get_system_time())

@obgect_flask.route('/get/system_authority_expire',methods=['get','post'])
def API_system_authority_time():
    return API_Send_Data(Client_modal.get_system_authority_time(m_Config.Sys_SystemKeyPath,m_Config.Sys_SystemKeyFileNode))

@obgect_flask.route('/get/process_list_cputop',methods=['get','post'])
def API_system_cpu_top():
    return API_Send_Data(Client_modal.get_cpu_top(m_Config.Sys_ProcessListCpuTop))


@obgect_flask.route('/get/process_list_memtop',methods=['get','post'])
def API_system_mem_top():
    return API_Send_Data(Client_modal.get_mem_top(m_Config.Sys_ProcessListMemTop))

def System_check_key():
    m_values = Mode_Tools.unlock_key(m_Config.Sys_KeyFilePath)
    if m_values[1] == False:
        m_logs.error("授权信息:{0}".format(m_values[0]))
    else:
        m_logs.info("授权信息:{0}".format(m_values[0]))
    while True:
        if m_values[1] == False:
            m_logs.error("当前授权文件错误,请检查或申请授权后重试。")
            Mode_Tools.kill_stop_me()
        else:
            m_ket_time = time.strftime("%Y-%m-%d", time.strptime(m_values[0]["到期时间"], "%Y-%m-%d"))
            m_local_time = time.strftime("%Y-%m-%d", time.localtime())
            if  m_local_time > m_ket_time:
                m_logs.error("当前授权已到期,请联系相关人员更新授权文件!授权信息：{0}".format(m_values[0]))
                Mode_Tools.kill_stop_me()
            else:
                m_logs.info("当前授权合法,当前授权信息:{0}".format(m_values[0]))
        time.sleep(120)
if __name__ == '__main__':
    #Mode_Tools.genetate_key("易云网信-侯坤翰","2022-10-22","17332799251","侯坤翰-测试使用-测试开发","/root/python_file/New_iecas/deploy.key")
    m_logo = base64.b64decode(
        "IF9fX19fICAgICAgICAgICAgICAgICAgICAgICAgICAgXyAgIF8gIC"
        "AgICAgICAgICAgDQp8XyAgIF98ICAgICAgICAgICAgICAgICAgICAg"
        "ICAgIHwgfCAoXykgICAgICAgICAgICANCiAgfCB8ICBfIF9fICBfX1"
        "8gXyBfXyAgIF9fXyAgX19ffCB8XyBfICBfX18gIF8gX18gIA0KICB8"
        "IHwgfCAnXyBcLyBfX3wgJ18gXCAvIF8gXC8gX198IF9ffCB8LyBfIF"
        "x8ICdfIFwgDQogX3wgfF98IHwgfCBcX18gXCB8XykgfCAgX18vIChf"
        "X3wgfF98IHwgKF8pIHwgfCB8IHwNCnxfX19fX3xffCB8X3xfX18vIC"
        "5fXy8gXF9fX3xcX19ffFxfX3xffFxfX18vfF98IHxffA0KICAgICAg"
        "ICAgICAgICAgIHwgfCAgICAgICAgICAgICAgICAgICAgICAgICAgIC"
        "AgICAgDQogICAgICAgICAgICAgICAgfF98ICAgICAgICAgICAgICAg"
        "ICAgICAgICAgICAgICAgICANCkluZm86WWl5dW4gV2FuZ3hpbiAoQm"
        "VpamluZykgSW5mb3JtYXRpb24gVGVjaG5vbG9neSBDby4sIEx0ZA0"
        "KVmVyc2lvbjpbVmVyc2lvbl0NCg=="
    )
    m_logs.debug("\n"+str(m_logo, encoding="utf-8").replace("[Version]", " [1.0.0 Beta]"))
    if Mode_Tools.check_potr_use(m_Config.Sys_ListeningAddress,int(m_Config.Sys_ListeningPort)) ==True:
        m_logs.error("当前端口:{0} 已被占用,请您更换端口或结束占用端口的程序".format(m_Config.Sys_ListeningAddress+":"+m_Config.Sys_ListeningPort))
        Mode_Tools.kill_stop_me()

    m_logs.info("-------进入检查授权文件------")
    if os.path.exists(m_Config.Sys_KeyFilePath) == False:
        m_logs.error("授权文件不存在,请检查授权文件:{0}".format(m_Config.Sys_KeyFilePath))
        Mode_Tools.kill_stop_me()
    else:
        m_logs.info("已经检测到授权文件:[{0}],即将启动定时任务:120s检测一次。".format(m_Config.Sys_KeyFilePath))
        m_Thread_check = Thread(target=System_check_key)
        m_Thread_check.daemon = True
        m_Thread_check.start()
        time.sleep(0.5)
    m_logs.info("-------结束检查授权文件------")
    if m_Config.Cat_RegisterCatalog == True:
        if os.path.exists(os.path.dirname(sys.argv[0])+"/Config/Catalog.json") == False:
            m_logs.error("当前注册服务目录Json文件不存在,请检查安装包完整性或者手动创建!")
            m_logs.error("当前Json文件不存在,跳过服务目录注册选项.")
        else:
            m_logs.info("当前已经配置注册到服务目录,即将注册服务目录!")
            m_catalog_json = open(os.path.dirname(sys.argv[0])+"/Config/Catalog.json").read()
            m_catalog_json = m_catalog_json.replace("{ADDRESS}",m_Config.Sys_LocalAddress)
            m_catalog_json = m_catalog_json.replace("{Port}", m_Config.Sys_ListeningPort)
            m_catalog_json = m_catalog_json.replace("{originalPort}", m_Config.Sys_ListeningPort)
            m_catalog_json = json.dumps(m_catalog_json)
            try:
                m_post_retun = requests.post("http://{0}/inner/serviceMetadata/register".format(m_Config.Cat_ServerCatalogAddress),data=m_catalog_json, headers={'Content-Type':"application/json"}, timeout=3)
                m_post_retun = json.loads(m_post_retun.text)
                m_logs.info("服务目录返回:{0}".format(m_post_retun))
            except:
                m_logs.error("请求注册失败,请检查您的服务目录是否正常运行.")
    else:
        m_logs.info("当前没有配置注册服务目录,取消注册服务目录.")
    m_logs.info("当前所有配置检查以及运行完毕,即将启动服务进程.")
    obgect_flask.run(port=m_Config.Sys_ListeningPort, debug=False, host=m_Config.Sys_ListeningAddress)




