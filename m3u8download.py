import m3u8
from urllib.parse import urljoin
import requests
from threading import Thread
import re
import os
import sys
import shutil


class M3u8Downloader():
    def __init__(self, url,name,download_path,t_num):
        self.url = url
        self.name = name
        self.download_path = download_path
        self.t_num = t_num
        self.save_path = os.path.join(self.download_path,"."+self.name)
        self.txt_path = os.path.abspath(os.path.join(self.save_path,'file.txt'))
        self.outfile = os.path.abspath(os.path.join(self.save_path,self.name)) #tmp下输出文件
        self.f_outfile = os.path.abspath(os.path.join(self.download_path,self.name)) #最终路径文件

        m3u8_obj = m3u8.load(url_m3u8)
        base_uri = m3u8_obj.base_uri
        self.url_list = [urljoin(base_uri,i) for i in m3u8_obj.files]
        self.now_p = 0
        self.all_p = len(self.url_list)

    def download(self):
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)
        
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        with open(self.txt_path,'w') as f:
            for index in range(len(self.url_list)):
                f.write("file "+ os.path.abspath(self.save_path+os.sep+f'{index}.ts').replace("\\","\\\\")+"\n")


        tmpt_list = []
        allt_list = []
        for index,url in enumerate(self.url_list):
        
            t_in = Thread(target=self.download_,args=(index,url))
            t_in.start()
            tmpt_list.append(t_in)
            allt_list.append(t_in)
            
            if len(tmpt_list) == self.t_num:
                for t_out in tmpt_list:
                    t_out.join()
                tmpt_list = []

        # 等待全部完成
        for t_out in allt_list:
            t_out.join()
        print("下载完成!")
        self.hecheng()

    def download_(self,index,url):
        data = requests.get(url,stream=True).content
        with open(os.path.join(self.save_path,str(index)+".ts"),'wb') as f:
            f.write(data)
        self.now_p += 1
        print(str(round(self.now_p/self.all_p*100,2))+'%')

    def hecheng(self):
        sh = f'ffmpeg -f concat -safe 0 -i "{self.txt_path}" -c copy "{self.outfile}" -loglevel error'
        os.system(sh)
        shutil.move(self.outfile,self.f_outfile)
        shutil.rmtree(self.save_path)   
        print("合并完成")                






if __name__ == "__main__":
    url_m3u8 = ""
    # 地址，视频名称，保存路径，同时下载个数
    M = M3u8Downloader(url_m3u8,'1.mp4',"video",4)
    M.download()

