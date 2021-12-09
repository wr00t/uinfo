# uinfo
该程序主要用来探测URL信息,包含状态码、响应长度、Title、Server等，自带扩展dirsearch字典，默认保存成csv文件,自动解析dirsearch格式URL文件。
## 使用帮助
python uinfo.py -h
## Example:
python uinfo.py -f url_file.txt<br>
python uinfo.py -fd dirsearch.txt<br>
python uinfo.py -u https://www.baidu.com<br>
