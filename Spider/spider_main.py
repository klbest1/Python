
# - *- coding: utf- 8 - *-

import url_manager
import html_downloader
import html_parser
import html_outputer
import data_uploader
import data_manager
import constant

class SpiderMain(object):
    """docstring for ClassName"""
    def __init__(self):
        super(SpiderMain, self).__init__()
        self.urls = url_manager.UrlManager()
        self.downloader = html_downloader.HtmlDownloader()
        self.parser = html_parser.HtmlParser()
        self.outputer = html_outputer.HtmlOutputer()
        self.uploader = data_uploader.DataUploader()


    #爬取所有第几页
    def crow_page(self,rootURL,city):

        page_data = self.downloader.download(rootURL)
        pages_urls = self.parser.parse_all_pages(page_data,rootURL)
        self.urls.append_urls(pages_urls)

        self.crow_detail_data(rootURL,city)


    #网站上数据的链接地址    
    def crow_detail_data(self,rootURL,city):
        
        #网站上的链接地址
        while self.urls.has_url():
            url = self.urls.get_url()
            html_data = self.downloader.download(url)
            data_download_urls = self.parser.parser_data(html_data,rootURL)
            if data_download_urls:
                self.urls.append_detail_urls(data_download_urls)
            else:
                print('没有最新数据！@')
                break

        self.crow_excel_data(rootURL,city)


    def crow_excel_data(self,rootURL,city):
        
        yunpan_datas = []
        while self.urls.has_detail_url():
            dataPath =  self.urls.get_detail_url()
            #链接地址
            url = dataPath["url"]
            data_time = dataPath["date"]
            html_data = self.downloader.download(url)

            data_Save_path = {}
            yunPan_urls = self.parser.parser_excel_data(html_data,rootURL)
            #网盘地址
            data_Save_path[constant.KExcel_Yun_URL] = yunPan_urls
            data_Save_path["date"] = data_time
            data_Save_path["dataURL"] = url
            yunpan_datas.append(data_Save_path)

        #上传到服务器
        for  item in yunpan_datas:
            url = item["dataURL"]
            date = item["date"]
            yun_pan_URL = item["excelYunPanURL"]
            self.uploader.upload_data_save_url(url,city,date,False,rootURL,yun_pan_URL)


    #爬取链接下的地址
    def crow_download_excel_url(self):
        baidu_pan_urls = data_manager.datamanager.data_need_download
        if baidu_pan_urls:
           data_property = baidu_pan_urls.pop()
           yunPan_urls = data_property.get(constant.KExcel_Yun_URL)
           self.craw_array_excel_url(yunPan_urls,data_property)

    #每一个链接下有多个excel地址
    def craw_array_excel_url(self,array,yunPorperty):
        if array is None or len(array) == 0:
            self.crow_download_excel_url()
        yun_pan_url = array.pop()
        print(yun_pan_url)
        if yun_pan_url:
           firstURl = yun_pan_url[constant.KBuilding_Yun_URL] + "?adapt=pc&fr=ftw"
           sign,timestamp,uk,shareid,fid_list,bdstoken = self.parser.get_sign(firstURl)
           donwload_url = self.parser.get_download_url("https://pan.baidu.com/api/sharedownload",sign,timestamp,uk,shareid,fid_list,bdstoken)
           print("excel直接下载地址：")
           print(donwload_url)
           title = yun_pan_url[constant.KBuilding_title]
           self.uploader.update_data_withExcelDownloadURL(yunPorperty,donwload_url,title)
        

        self.craw_array_excel_url(array,yunPorperty)

    #解析Excel摇号排名数据
    def analyze_excel_ranking_data(self):
        property = data_manager.datamanager.find_data_not_analyzied()
        if property:
            excel_address_array = property.get(constant.KExcel_download_URL)
            date = property.get('publishDate')
            #分析Excel数据
            self.analyze_excel_array(excel_address_array,date,property)
      

# [{"yunPanURL":"https://pan.baidu.com/s/1xPxs68X51WFloiIYILvncg","buildingTitle":"2018年5月14日瀚城新天地4栋刚需登记购房人公证摇号排序结果"},{"yunPanURL":"https://pan.baidu.com/s/1oG9ahybH_yluuID2aru1dA","buildingTitle":"2018年5月14日瀚城新天地4栋棚改货币化安置住户公证摇号排序结果"},{"yunPanURL":"https://pan.baidu.com/s/19CTFm1MdH0Znhwkb61Qtxw",
# "buildingTitle":"2018年5月14日瀚城新天地4栋普通登记购房人公证摇号排序结果"}]
# #解析Excel数组里面每条地址
    def analyze_excel_array(self,array,date,yunPorperty):
       if array is None or len(array) == 0:
        #更改解析状态
        self.uploader.update_data_withExcelAnalyzed(yunPorperty,True)
        #Excel解析完毕，进行下一组递归
        self.analyze_excel_ranking_data()
       else:
        address_dic = array.pop()
        address = address_dic[constant.KBuilding_Yun_URL]
        title = address_dic[constant.KBuilding_title]
        excel_name = title + ".xls"
        self.downloader.download_excel(address,excel_name)
        data_manager.datamanager.analysis_excel_choseHouseOrder_data(excel_name,self.upload_excel_data,title,date)
        #继续解析excel
        self.analyze_excel_array(array,date,yunPorperty)


    #上传Excel数据到Leancloud
    def upload_excel_data(self,data_array):
        self.uploader.upload_excel_ranking(data_array)

if __name__ == "__main__":
    
    rootURL = "http://www.cdgzc.com/gongshigonggao"
    spiderman = SpiderMain()
    spiderman.crow_page(rootURL,"成都")
    #spiderman.crow_download_excel_url()
    spiderman.analyze_excel_ranking_data()

