# -*- coding: UTF-8 -*-
import base64
import hashlib
import re
import requests

# 顾客编码(clientCode)： LLYLKJSZ
# 您的应用 校验码 (checkWord) ： STGuVhBlDznxZbvyFFSxP5fdsyH8geFq
clientCode = 'LLYLKJSZ'
checkWord = 'STGuVhBlDznxZbvyFFSxP5fdsyH8geFq'
#公司顺丰月结账号id 7550069706

#生成验证码
def getVerifyCode(xml):
    paramStr = xml + checkWord
    md5 = hashlib.md5()
    md5.update(paramStr.encode('utf-8'))
    #返回二进制数据，hexdigest返回十六进制数据
    sign = md5.digest()
    #base64方式编码
    verifyCode = base64.b64encode(sign)
    return verifyCode
#将响应xml转为字典
def resToDict(str):
    #正则匹配到响应数据
    resData = re.search(r'<order.*?>',str).group()[1:-1].split(' ')[1:]
    resDict = {}
    #响应为正常
    try:
        for i in resData:
            data = i.split('=')
            resDict[data[0]] = data[1].split('""')
        return resDict
    #响应为失败
    except:
        resData = re.search(r'<Error.*?</Error>',str).group()
        return resData

#封装 （生成订单、查询订单接口）请求参数
def requestXml(orderData):
    xml="""
    <Request service="OrderService" lang="cn_ZH">    
    <Head>{clientCode}</Head>    
    <Body>        
    <Order 
        orderid="{orderid}" 
        j_company='深圳榴莲科技有限公司'
        j_contact='张先生'  
        j_tel='075526806888'
        j_mobile='075526806888'          
        j_province='广东省'            
        j_city='深圳市'            
        j_county='福田区'                      
        j_address='福田区南山街道滨江社区滨河大道2001号7楼08-09单元' 
        d_contact='{getman}' 
        d_tel='4008111111'
        d_mobile='{orderPhone}'         
        d_province='{d_provice}'            
        d_city='{d_city}'            
        d_county='{d_county}'                              
        d_address='{d_address}'
        express_type='1'  
        pay_method='1' 
        custid='7550069706'          
        parcel_quantity='1'            
        is_docall='2'            
        send_startTime = '{sendTime} 10:30:00'          
        remark='{goodNmae}'            
        is_unified_waybill_no='1'>       
    </Order>    
    </Body>
    </Request>
    """.format(clientCode=clientCode,orderid=orderData['orderNum'],getman=orderData['getman'],
               orderPhone=orderData['orderPhone'],d_provice=orderData['d_provice'],
               d_city=orderData['d_city'],
               d_county=orderData['d_county'],d_address=orderData['d_adress'],
               goodNmae=orderData['goodName'],sendTime=orderData['sendTime'])
    return xml
#调用生成订单接口,获取响应字典
def addOrders(xml):
    url = 'http://bsp-oisp.sf-express.com/bsp-oisp/sfexpressService'
    #生成验证码
    code = getVerifyCode(xml)
    #提交post请求，获取响应文本
    res = requests.post(url=url,data={'xml':xml,'code':code}).text
    #文本转为字典
    resData = resToDict(res)
    return resData

#调用订单查询接口,获取响应字典
def checkOrders(orderNum):
    url = 'http://bsp-oisp.sf-express.com/bsp-oisp/sfexpressService'
    checkXml = """
    <Request service="OrderSearchService"  lang="zh-CN">
    <Head>{clientCode}</Head>
    <Body>
    <OrderSearch orderid="{orderNum}"/>
    </Body>
    </Request>
    """.format(clientCode=clientCode,orderNum=orderNum)
    code = getVerifyCode(checkXml)
    res = requests.post(url=url,data={'xml':checkXml,'code':code}).text
    resData = resToDict(res)
    return resData

#封装 （取消订单接口）请求参数
def delRequestXml(orderNum):
    delXml = """<Request service="OrderConfirmService" lang="zh-CN">
        <Head>{clientCode}</Head>
        <Body>
        <OrderConfirm
        orderid="{order_num}"
        dealtype="2">
        </OrderConfirm>
        </Body>
        </Request>""".format(clientCode=clientCode, order_num=orderNum)
    return delXml
#调用取消订单接口,获取响应字典
def delOrders(xml):
    url = 'http://bsp-oisp.sf-express.com/bsp-oisp/sfexpressService'
    code = getVerifyCode(xml)
    res = requests.post(url=url,data={'xml':xml,'code':code}).text
    resDict = resToDict(res)
    return resDict

#封装 物流信息查询参数，获取请求xml
def rootXml(orderNum):
    rootXml = """<Request service='RouteService' lang='zh-CN'>
    <Head>{clientCode}</Head>
    <Body>
    <RouteRequest
    tracking_type='1'
    method_type='1'
    tracking_number='{orderNum}'/>
    </Body>
    </Request>""".format(clientCode=clientCode,orderNum=orderNum)
    return rootXml
#调用物流信息查询接口，获取响应字典
def queryRoot(xml):
    url = "http://bsp-oisp.sf-express.com/bsp-oisp/sfexpressService"
    code = getVerifyCode(xml)
    res = requests.post(url=url,data={'xml':xml,'verifyCode':code}).text
    #匹配所需要的数据，re.s可将换行的数据作为一个整体匹配，以防错过换行后的数据。
    resPonse = re.findall(r'<Route.*?>',res,re.S)
    sendData = []
    #获取每一项数据
    for i in resPonse:
        dataOne = re.findall(r'.+?= ".*?"',i)
        objDict = {}
        for dataTwo in dataOne:
            data = dataTwo.split('=')
            #将每项数据转为字典的键和值保存
            objDict[data[0].strip(' ')] = data[1].strip(' ')
            sendData.append(objDict)
    return sendData

if __name__ == '__main__':
    objDict = {
        'couponid':'',
        'getman':'周先生',
        'goodImg':'http://liulian.szbeacon.com/1.png',
        'goodName':'纪念册',
        'goodNum':'1',
        'goodPrice':'100.00',
        'sendTime':'2019-09-23 15:30:03',
        'd_adress':'广东,深圳,福田区,鹿丹村一号',
        'd_provice':'湖南省',
        'd_city':'岳阳市',
        'd_county':'汨罗市',
        'orderEndTime':'2019-09-23 15:30:03',
        'orderNum':'',
        'orderPhone':'13874569406',
        'orderTruePay':'0.01',
        'orderUser':'',
        'type':1,
        'zhoubianid':2,
    }
    xml = requestXml(objDict)
    print(xml)
















