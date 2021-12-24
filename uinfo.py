#coding:utf-8
import re
import sys
import csv
import time
import httpx
import random
import string
import hashlib
import asyncio
import argparse
from pathlib import Path
from parsel import Selector
from urllib.parse import urlparse

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'}

def genearate_md5_sign(data):
    if data:
        return hashlib.md5(data.encode(encoding='utf-8')).hexdigest()
    
'''
    随机生成url，请求获取结果生成md5签名
'''
def probe_sign(domain):
    random_strs = ''.join(random.choice(string.ascii_letters+string.digits) for i in range(10))
    url = domain+random_strs+'.'+random_strs
    print('[*] 生成随机URL {}\n'.format(url))
    sign = None
    try:
        res = httpx.get(url,headers=headers,verify = False,follow_redirects = True)
        sign = genearate_md5_sign(res.text)
        print('[*] 响应签名为： {}\n'.format(sign))
        return sign
    except:
        pass
    return sign

def read_url_file(path):
    ds = []
    with open(path) as f:
        for x in f:
            ds.append(x.strip())
    ds = list(set(ds))
    return ds

'''
    读取字典文件，去重排序
'''
def read_dicc_file(path):
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
    return ds

'''
    加载dirsearch结果的URL文件并去重
'''
def parse_dirsearch_file(path):
    ds = []
    with open(path) as f:
        for x in f:
            if x.strip() and '# Dirsearch' not in x:
                res = re.findall('(\d+)\s+(\w*)\s+(.*)\s',x)
                ds.append(res[0][2].strip())
    ds = list(set(ds))
    return ds

def write_to_csv(path,res_list,mode='w',title=True):
    if res_list:
        print("[*] 写入文件：{} \n".format(path))
        with open(path,mode,newline='',encoding='utf-8') as csv_file:
            csvwriter = csv.writer(csv_file)
            if title:
                csvwriter.writerow(['请求类型','请求URL','响应URL','响应状态码','响应长度','title','响应类型','server'])
            for r in res_list:
                csvwriter.writerow(r.split('\t'))
        print('[*] 共写入 {} 条记录\n'.format(len(res_list)))
    else:
        print('[*] 无记录不写入文件！\n')

async def get_url_info(sem,url,ex_content_sign=None):
    try:
        async with sem:
            async with httpx.AsyncClient(headers=headers,verify = False,follow_redirects = True) as client:
                response = await client.get(url)
                status_code = response.status_code
                if status_code == 200:
                    res_length = response.headers.get('content-length') if response.headers.get('content-length') else len(response.content)
                    if float(res_length) > 1:
                        req_url = url
                        res_url = response.url
                        content = response.text
                        if ex_content_sign:
                            content_sign = genearate_md5_sign(content)
                            if content_sign != ex_content_sign:
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
                        else:
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

async def asyn_request(urls,sem,ex_content_sign=None):
        sem = asyncio.Semaphore(sem)
        task_list = []  
        for url in urls:
            task = asyncio.create_task(get_url_info(sem, url,ex_content_sign))  
            task_list.append(task)
        return await asyncio.gather(*task_list) 

def usage(msg=None):
    print('\n\tUsage python '+sys.argv[0]+' [Options] use -h for help\n')
    sys.exit()
    
def begin_scan(urls,sem,ex_content_sign=None):
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(asyn_request(urls,sem,ex_content_sign))
    return list(filter(None, res))
        

if __name__ == '__main__':
    file_name = sys.argv[0]
    parser = parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,epilog = 'Example: \n\tpython '+file_name+' -t file -p url_file.txt #加载URL文件\n\tpython '+file_name+' -t domain -p domains.txt #加载域名文件\n\tpython '+file_name+' -t dir -p dirsearch.txt #加载dirsearch结果的URL文件\n\tpython '+file_name+' -d https://www.baidu.com #扫描单个域名\n\n\t\t\t\t\t\t\n',description='该程序主要用来探测URL信息,返回对应的响应长度、title、server等字段，默认仅显示状态码为200的资源。')
    parser.error = usage
    parser.add_argument('-t', '--type',help="请求的文件类型:\nfile 为内容全是完整url的文件\ndomain 为多个域名文件\ndir 为dirsearch的url文件\n默认为 file", default='file',choices=['file','domain','dir'],required=False)
    parser.add_argument('-p', '--path', help="待请求的文件路径", required=False)
    parser.add_argument('-d', '--domain', help="请求的单个主域名", required=False)
    parser.add_argument('-w', '--word', help="目录字典和-d参数一起使用，如果不加则默认为当前目录下的dicc.txt", default='dicc.txt',required=False)
    parser.add_argument('-s', '--sem', help="并发的数量，默认200", default=200, required=False)
    parser.add_argument('-ua', '--user-agent', help="请求的User-Agent,有默认UA", required=False)
    parser.add_argument('-o', '--output', help="保存的文件名称,默认为result.csv", default='result.csv', required=False)
    
    args,unknown=parser.parse_known_args()
    
    sem = args.sem
    file_type = args.type
    file_path = args.path
    word_path = args.word
    result_file = args.output
    domain = args.domain
    
    if file_type and file_path == None and domain == None:
        usage()
    
    print(time.strftime("\n[*] %Y-%m-%d %H:%M:%S", time.localtime()))
    print("[*] 程序启动 .......................\n")
    start_time = time.time()
    if domain:# 单个域名扫描
        dicc_list = read_dicc_file(word_path)
        print('[*] 加载字典文件 {} ,共 {} 条记录...'.format(word_path,len(dicc_list)))
        new_domain = domain if domain.endswith('/') else domain+'/'
        print('[*] 开始扫描域名 {} ...\n'.format(new_domain))
        urls = list(map(lambda o:new_domain+o,dicc_list))
        sign = probe_sign(new_domain)
        result = begin_scan(urls,sem,sign)
        end_time = time.time()
        print("\n[*] 扫描域名 {} 结束,用时: {:.2f} 秒 \n".format(new_domain,end_time-start_time))
        write_to_csv(result_file,result)
    else:
        if file_type == 'file':# URL文件扫描
            print('[*] 加载URL文件 {} ,共 {} 条记录...'.format(file_path,len(read_dicc_file(file_path))))
            urls = read_url_file(file_path)
            result = begin_scan(urls,sem)
            file_end_time = time.time()
            print("\n[*] 扫描结束,用时: {:.2f} 秒 \n".format(file_end_time-start_time))
            write_to_csv(result_file,result)
        elif file_type == 'domain': # 域名文件扫描
            domain_list = read_url_file(file_path)
            dicc_list = read_dicc_file(word_path)
            print('[*] 加载域名文件 {} ,共 {} 个域名...'.format(file_path,len(domain_list)))
            print('[*] 加载字典文件 {} ,共 {} 条记录...\n'.format(word_path,len(dicc_list)))
            i = 1
            for domain in domain_list:
                new_domain = domain if domain.endswith('/') else domain+'/'
                print('[*] 探测第 {} 个域名 {} \n'.format(i,new_domain))
                urls = list(map(lambda o:new_domain+o,dicc_list))
                domain_start_time = time.time()
                sign = probe_sign(new_domain)
                result = begin_scan(urls,sem,sign)
                domain_end_time = time.time()
                print("\n\n[*] 探测 {} 结束,用时: {:.2f} 秒 \n".format(new_domain,domain_end_time-domain_start_time))
                if i == 1:
                    write_to_csv(result_file,result)
                else:
                    write_to_csv(result_file,result,mode='a+',title=False)
                i+=1
        elif file_type == 'dir':# dirsearch文件扫描
            urls = parse_dirsearch_file(file_path)
            print('[*] 加载dirsearch文件 {} ,共 {} 条记录...\n'.format(file_path,len(urls)))
            result = begin_scan(urls,sem)
            ds_end_time = time.time()
            print("\n[*] 扫描结束,用时: {:.2f} 秒 \n".format(ds_end_time-start_time))
            write_to_csv(result_file,result)
    end_time = time.time()
    print(time.strftime("\n[*] %Y-%m-%d %H:%M:%S", time.localtime()))
    print("\n[*] 程序扫描结束，共计用时: {:.2f} 秒 \n".format(end_time-start_time))
    
