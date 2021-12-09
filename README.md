# uinfo
该程序主要用来探测URL信息,包含状态码、响应长度、Title、Server等，自带扩展dirsearch字典，默认保存成csv文件,自动解析dirsearch格式URL文件。
## 使用帮助 ##
python uinfo.py -h
## Usage ##
      usage: uinfo.py [-h] [-f FILE] [-fd DIRSEARCH_FILE] [-u URL] [-d DIC] [-s SEM] [-ua USER_AGENT] [-o OUTPUT]
      该程序主要用来探测URL信息,包含状态码、响应长度、Title、Server等，自带扩展dirsearch字典，默认保存成csv文件,自动解析dirsearch格式URL文件。

      optional arguments:
        -h, --help            show this help message and exit
        -f FILE, --file FILE  需要请求的URL文件，为完整URL地址
        -fd DIRSEARCH_FILE, --dirsearch_file DIRSEARCH_FILE
                              dirsearch结果的URL文件,自动解析
        -u URL, --url URL     请求的主域名
        -d DIC, --dic DIC     目录字典和-u参数一起使用，如果不加则默认为当前目录下dicc.txt
        -s SEM, --sem SEM     并发的数量，默认200
        -ua USER_AGENT, --user-agent USER_AGENT
                              请求的User-Agent,有默认UA
        -o OUTPUT, --output OUTPUT
                              保存的文件名称,默认为result.csv
## Example:
python uinfo.py -f url_file.txt<br>
python uinfo.py -fd dirsearch.txt<br>
python uinfo.py -u https://www.baidu.com<br>
