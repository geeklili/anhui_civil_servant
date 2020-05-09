import requests
from lxml import etree
from pymongo import MongoClient
import time
import re

mongo_local = MongoClient("mongodb://root:localhost:3717")
civil_servant = mongo_local.crawler.civil_servant

headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
           "Accept-Encoding": "gzip, deflate",
           "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
           "Connection": "keep-alive",
           "Host": "ah.huatu.com",
           "Upgrade-Insecure-Requests": "1",
           "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36"}


def get_one():
	"""通过xpath来解析抓取
	"""
	for page_num in range(800):
		url = "http://ah.huatu.com/zt/skzwb/search/?year=&diqu=&jingli=&nianling=&xueli=&zhuanye=&page=%s" % page_num
		ret = requests.get(url=url, headers=headers)
		page = etree.HTML(ret.content.lower())
		year_li = page.xpath(u"/html/body/div[1]/div[2]/div[3]/table/tbody/tr/td[1]/text()")
		area_li = page.xpath(u"/html/body/div[1]/div[2]/div[3]/table/tbody/tr/td[2]/text()")
		department_li = page.xpath(u"/html/body/div[1]/div[2]/div[3]/table/tbody/tr/td[3]/text()")
		post_li = page.xpath(u"/html/body/div[1]/div[2]/div[3]/table/tbody/tr/td[4]/text()")
		edu_li = page.xpath(u"/html/body/div[1]/div[2]/div[3]/table/tbody/tr/td[5]/text()")
		major_li = page.xpath(u"/html/body/div[1]/div[2]/div[3]/table/tbody/tr/td[6]/text()")
		need_num_li = page.xpath(u"/html/body/div[1]/div[2]/div[3]/table/tbody/tr/td[7]/text()")
		part_num_li = page.xpath(u"/html/body/div[1]/div[2]/div[3]/table/tbody/tr/td[8]/text()")
		score_line_li = page.xpath(u"/html/body/div[1]/div[2]/div[3]/table/tbody/tr/td[9]/text()")
		url_li = page.xpath(u"/html/body/div[1]/div[2]/div[3]/table/tbody/tr/td[10]/a/@href")
		for ind in range(20):
			try:
				di = dict()
				di['year'] = year_li[ind]
				di['area'] = area_li[ind]
				di['department'] = department_li[ind]
				di['post'] = post_li[ind]
				di['edu'] = edu_li[ind]
				di['major'] = major_li[ind]
				di['need'] = need_num_li[ind]
				di['part'] = part_num_li[ind]
				di['score'] = score_line_li[ind]
				di['url'] = url_li[ind]
				print(di)
				civil_servant.insert_one(di)
			except Exception as e:
				print(e)
				with open('./data/error_url.txt', 'a+', encoding='utf-8') as f:
					f.write(url + '\n')


def get_two():
	"""
	通过正则表达式来抓取
	"""
	for page_num in range(800):
		url = "http://ah.huatu.com/zt/skzwb/search/?year=&diqu=&jingli=&nianling=&xueli=&zhuanye=&page=%s" % page_num
		ret = requests.get(url=url, headers=headers)
		content = ret.text
		content = content.replace('\n', '')
		ret2 = re.findall('<tr>.*?</tr>', content)
		print(page_num)
		for ind, i in enumerate(ret2):
			if ind == 0:
				continue
			try:
				ret3 = re.sub('<.*?>', '|', i)
				ret4 = [i for i in ret3.split('|') if i]
				href = re.findall('href=\"(.*?)\">查看', i)
				di = dict()
				di['year'] = ret4[0]
				di['area'] = ret4[1]
				di['department'] = ret4[2]
				di['post'] = ret4[3]
				di['edu'] = ret4[4]
				di['major'] = ret4[5]
				di['need'] = ret4[6]
				di['part'] = ret4[7]
				di['score'] = ret4[8]
				di['url'] = href[0]
				di['page_num'] = page_num
				civil_servant.insert_one(di)
			except Exception as e:
				with open('./data/error_url2.txt', 'a+', encoding='utf-8') as f:
					f.write(url + '\n')


if __name__ == '__main__':
	get_two()
