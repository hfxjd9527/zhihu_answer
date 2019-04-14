# #coding=utf-8
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import multiprocessing
import time
from selenium import webdriver
import pdfkit
import PyPDF2


class ZhihuInfos():
    # 定义一个知乎类
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 30)  # 设置超时时间
    pdf_path = "./pdf_file/"
    if not os.path.exists(pdf_path):
        os.makedirs(pdf_path)

    html_path = "./html_file/"
    if not os.path.exists(html_path):
        os.makedirs(html_path)

    def get_pagesource(self, url):
        # 获得网页源代码
        self.driver.get(url=url)
        self.driver.maximize_window()
        time.sleep(5)

        # 执行点击动作
        for i in range(1, 11):
            content_click = '#Profile-answers > div:nth-child(2) > div:nth-child(' + str(
                i) + ') > div > div.RichContent.is-collapsed > div.RichContent-inner'
            try:
                complete_content = self.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, content_click)))
                complete_content.click()
                time.sleep(1)
            except BaseException:
                pass
        pagedata = self.driver.page_source
        return pagedata

    def save_to_html(self, base_file_name, url):
        # 将网页源代码保存为HTML
        filename = base_file_name + ".html"
        pagedata = self.get_pagesource(url)
        with open(self.html_path + filename, "wb") as f:
            f.write(pagedata.encode("utf-8", "ignore"))
            f.close()
        return filename

    def html_to_pdf(self, base_file_name, url):
        # 将HTML保存为PDF
        htmlname = self.save_to_html(base_file_name, url)
        pdfname = base_file_name + ".pdf"
        htmlfile = open(self.html_path + htmlname, 'r', encoding='utf-8')
        confg = pdfkit.configuration(
            wkhtmltopdf=r'D:\htmlpdf\wkhtmltopdf\bin\wkhtmltopdf.exe')
        pdfkit.from_url(htmlfile, self.pdf_path + pdfname, configuration=confg)

    def Many_to_one(self):
        # 将多个PDF合成一个
        filelist = []
        # 找出所有的pdf文件,并将文件名保存至列表。
        for filename in os.listdir('./pdf_file'):
            if filename.endswith('.pdf'):
                filelist.append(filename)

        # 创建一个新的pdf
        newPdfFile = PyPDF2.PdfFileWriter()

        # 循环打开每一个pdf文件，将内容添加至新的pdf
        for filename in filelist:
            pdfFile = open('./pdf_file/' + filename, 'rb')
            pdfObj = PyPDF2.PdfFileReader(pdfFile)
            # 获取页数
            pageNum = pdfObj.numPages

            for num in range(pageNum):
                pageContent = pdfObj.getPage(num)
                newPdfFile.addPage(pageContent)

        newFile = open(self.pdf_path + '张佳玮.pdf', 'wb')
        newPdfFile.write(newFile)
        newFile.close()


if __name__ == "__main__":
    start = time.time()
    zhihu = ZhihuInfos()
    for i in range(4, 7):
        url = 'https://www.zhihu.com/people/zhang-jia-wei/answers?page=' + \
            str(i)
        base_file_name = "zhihu{}".format(i)
        p = multiprocessing.Process(
            target=zhihu.html_to_pdf, args=(
                base_file_name, url))
        p.daemon = True
        p.start()
        p.join()
    zhihu.Many_to_one()
    end = time.time()
    print("共计用时%.4f秒" % (end - start))
