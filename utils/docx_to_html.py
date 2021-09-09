# 此工具文件用于将扩展名为.docx的word文档转换为html文件
from pydocx import PyDocX
import os


# 通过word文档
def docx_transfer_html(file_location, filename):
    # html = PyDocX.to_html("D:/AI Projects/food-identification/doc/app端系统设计参考-任雪燕.docx")
    html = PyDocX.to_html(file_location + filename + '.docx')
    # f = open("D:/Java/apache-tomcat-8.5.51/webapps/ROOT/ingredients/test.html", 'w', encoding="utf-8")
    f = open(file_location + filename + '.html', 'w', encoding="utf-8")
    f.write(html)
    f.close()
