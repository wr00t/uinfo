#coding:utf-8
import sys
import csv
import time
import httpx
import asyncio
import argparse
from pathlib import Path
from parsel import Selector
from urllib.parse import urlparse

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'}

def read_url_file(path):
    print("\n[*] 加载文件：{} \n".format(path))
    ds = []
    with open(path) as f:
        for x in f:
            ds.append(x.strip())
    print('共加载 {} 条记录\n'.format(len(ds)))
    return ds

def read_dicc_file(path):
    print("\n[*] 加载文件：{} \n".format(path))
    ds = []
    ext_list = ['jsp','php','aspx']
    with open(path) as f:
        for x in f:
            x = x.strip()
            if x in ['.ico','.png','.gif','.jpg','favicon.ico']:
                continue
            if '%EXT%' in x:
                for e in ext_list:
                    new_x = x.replace('%EXT%',e)
                    ds.append(new_x.strip())
            else:
                ds.append(x.strip())
    ds = list(set(ds))
    ds.sort()
    print('共加载 {} 条记录\n'.format(len(ds)))
    return ds

def parse_dirsearch_file(path):
    print("\n[*] 加载dirsearch文件：{} \n".format(path))
    ds = []
    with open(path) as f:
        for x in f:
            if x.strip() and '# Dirsearch' not in x:
                res_list = x.split('   ')
                ds.append(res_list[2].strip())
    print('共加载 {} 条记录\n'.format(len(ds)))
    return ds

def write_to_csv(path,res_list):
    with open(path,'w',newline='',encoding='utf-8') as csv_file:
        csvwriter = csv.writer(csv_file)
        csvwriter.writerow(['请求类型','请求URL','响应URL','响应状态码','响应长度','title','响应类型','server'])
        for r in res_list:
            csvwriter.writerow(r.split('\t'))

async def get_url_info(sem,url):
    try:
        async with sem:
            async with httpx.AsyncClient(headers=headers,verify = False,follow_redirects = True) as client:
                response = await client.get(url)
                status_code = response.status_code
                if status_code == 200 or status_code == 301 or status_code == 302 or status_code == 401:
                    res_length = response.headers.get('content-length') if response.headers.get('content-length') else len(response.content)
                    if res_length > 1:
                        req_url = url
                        res_url = response.url
                        content = response.text
                        req_suffix = Path(urlparse(url).path).suffix[1:]
                        req_suffix = req_suffix if req_suffix else 'None'
                        select_obj = Selector(text=content).xpath('//title/text()').get()
                        title = select_obj if select_obj else 'None'
                        res_content_type = response.headers.get('content-type') if response.headers.get('content-type') else 'None'
                        res_content_type = res_content_type[:res_content_type.find(';')] if res_content_type.find(';')>-1 else res_content_type
                        res_server = response.headers.get('server') if response.headers.get('server') else 'None'
                        strs = '{}\t{}\t{}\t{}\t{:.2f}KB\t{}\t{}\t{}'.format(req_suffix,req_url,res_url,status_code,float(res_length)/1024,title,res_content_type,res_server)
                        print(strs)
                        return strs
    except Exception as e:
        pass

async def asyn_request(urls):
        sem = asyncio.Semaphore(200)
        task_list = []  
        for url in urls:
            task = asyncio.create_task(get_url_info(sem, url))  
            task_list.append(task)
        return await asyncio.gather(*task_list) 

def usage(msg=None):
    print('Usage python '+sys.argv[0]+' [Options] use -h for help')
    sys.exit()
    
def begin(url_file,save_file,file_type='default',req_type='file',req_domain=''):
    urls = []
    if req_type == 'domain' and req_domain:
        dir_url = read_dicc_file('dicc.txt')
        req_domain = req_domain if req_domain.endswith('/') else req_domain+'/'
        urls = list(map(lambda o:req_domain+o,dir_url))
    elif file_type == 'dirasearch' :
        urls = parse_dirsearch_file(url_file)
    elif req_type == 'file':
        urls = read_url_file(url_file)
    print("[*] 开始探测.......................")
    s = time.time()
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(asyn_request(urls))
    e = time.time()
    print("\n[*] over! 用时: {:.2f} 秒 \n".format(e-s))
    res = list(filter(None, res))
    if res:
        print("[*] 写入文件：{} \n".format(save_file))
        write_to_csv(save_file,res)
        print('共写入 {} 条记录\n'.format(len(res)))
    else:
        print('[*] 无记录不写入文件！\n')
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'\n')
        

if __name__ == '__main__':
    file_name = sys.argv[0]
    parser = parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,epilog = 'Example: \n\tpython '+file_name+' -f url_file.txt \n\tpython '+file_name+' -fd dirsearch.txt \n\tpython '+file_name+' -u https://www.baidu.com\n\n\t\t\t\t\t\t\n',description='该程序主要用来探测URL信息,默认仅显示状态码为200、301、302、401的资源。')
    parser.error = usage
    parser.add_argument('-f', '--file', help="需要请求的URL文件，为完整URL地址", required=False)
    parser.add_argument('-fd', '--dirsearch_file', help="dirsearch结果的URL文件,自动解析", required=False)
    parser.add_argument('-u', '--url', help="请求的主域名", required=False)
    parser.add_argument('-d', '--dic', help="目录字典和-u参数一起使用，如果不加则默认为当前目录下dicc.txt", required=False)
    parser.add_argument('-s', '--sem', help="并发的数量，默认100", required=False)
    parser.add_argument('-ua', '--user-agent', help="请求的User-Agent,有默认UA", required=False)
    parser.add_argument('-o', '--output', help="保存的文件名称,默认为result.csv", required=False)
    
    args,unknown=parser.parse_known_args()
    
    if unknown or len(sys.argv) < 2:
        usage()
    
    url_file = args.file
    req_domain = args.url
    save_file = args.output if args.output else 'result.csv'
    dirsearch_file = args.dirsearch_file
    
    if url_file and dirsearch_file == None:
        begin(url_file,save_file)
    
    if dirsearch_file:
        begin(dirsearch_file,save_file,file_type = 'dirasearch')
    
    if req_domain and dirsearch_file == None and url_file == None:
        begin(dirsearch_file,save_file,file_type = 'dirasearch',req_type='domain',req_domain=req_domain)
    