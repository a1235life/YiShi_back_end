#auther:yyb
#time:2019/12/26
import json
import sys
import jsonpath
import requests
import base64

API_KEY = 'KCRpdtqKNymFd0EwLN0vknr0'
SECRET_KEY = 'TBgdiKpZ2sSgxQTzdcB4XYFGvzVGiziC'
IMAGE_RECOGNIZE_URL = "https://aip.baidubce.com/rest/2.0/image-classify/v2/dish"
"""  TOKEN start """
TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'
IS_PY3 = sys.version_info.major == 3
if IS_PY3:
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from urllib.parse import urlencode
def fetch_token():
    global result_str
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    if (IS_PY3):
        post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req, timeout=5)
        result_str = f.read()
    except URLError as err:
        print(err)
    if (IS_PY3):
        result_str = result_str.decode()
    result = json.loads(result_str)
    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not 'brain_all_scope' in result['scope'].split(' '):
            print ('please ensure has check the  ability')
            exit()
        return result['access_token']
    else:
        print ('please overwrite the correct API_KEY and SECRET_KEY')
        exit()

# 二进制方式打开图片文件
def photo(datainfo):
    request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general"
    img = bytes(datainfo, encoding = "utf8")
    print('图片格式',type(img))
    params = {"image":img}
    access_token = fetch_token()
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    if response:
        jsondata=response.json()
        print(jsondata)
        print('返回的数据类型：',type(jsondata))
        arraydata=jsonpath.jsonpath(response.json(),'$..keyword')
        #arraydata=jsonpath.jsonpath(response.json(),'$..root')
        print(arraydata)
        print('解析的数据类型：',type(arraydata))
    return arraydata
