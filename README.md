# uinfo
该程序主要用来探测URL信息,包含状态码、响应长度、Title、Server等，自带扩展dirsearch字典，默认保存成csv文件,

自动解析dirsearch格式URL扫描结果文件,响应长度小于1的资源不进行展示。(Alpha版本)
## 使用帮助 ##
python uinfo.py -h
## Usage ##
      usage: uinfo.py [-h] [-t {file,domain,dir}] [-p PATH] [-d DOMAIN] [-w WORD] [-s SEM] [-ua USER_AGENT] [-o OUTPUT]

      该程序主要用来探测URL信息,返回对应的响应长度、title、server等字段，默认仅显示状态码为200的资源。

      optional arguments:
        -h, --help            show this help message and exit
        -t {file,domain,dir}, --type {file,domain,dir}
                              请求的文件类型:
                              file 为内容全是完整url的文件
                              domain 为内容是多个域名的文件
                              dir 为dirsearch扫描之后的url文件
                              默认为 file
        -p PATH, --path PATH  待请求的文件路径
        -d DOMAIN, --domain DOMAIN
                              请求的单个主域名
        -w WORD, --word WORD  目录字典和-d参数一起使用，如果不加则默认为当前目录下的dicc.txt
        -s SEM, --sem SEM     并发的数量，默认200
        -ua USER_AGENT, --user-agent USER_AGENT
                              请求的User-Agent,有默认UA
        -o OUTPUT, --output OUTPUT
                              保存的文件名称,默认为result.csv

      Example:
              python .\uinfo.py -t file -p url_file.txt #加载URL文件
              python .\uinfo.py -t domain -p domains.txt #加载域名文件
              python .\uinfo.py -t dir -p dirsearch.txt #加载dirsearch结果的URL文件
              python .\uinfo.py -d https://www.baidu.com #扫描单个域名

        
## Example:
        python uinfo.py -t file -p url_file.txt #加载URL文件
        python uinfo.py -t domain -p domains.txt #加载域名文件
        python uinfo.py -t dir -p dirsearch.txt #加载dirsearch结果的URL文件
        python uinfo.py -d https://www.baidu.com #扫描单个域名
