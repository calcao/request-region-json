#! /usr/bin/env python
#coding:utf-8


import requests
import HTMLParser
import json
import codecs
import sys
reload(sys) 
sys.setdefaultencoding('utf-8')

provinces = []

#解析html
class RegionParser(HTMLParser.HTMLParser):
	def __init__(self):
		HTMLParser.HTMLParser.__init__(self)
		self.datas = []
		self.region = []
		self.region_tag_start_flag = False

	def handle_starttag(self,tag, attrs):
		if 'p' == tag:
			if 0 == len(attrs):
				pass
			else:
				for attr in attrs:
					if 'MsoNormal' == attr[1]:
						# print attrs
						self.region_tag_start_flag = True
						if 0 == len(self.region):
							pass
						else:
							self.datas.append(self.region)
							self.region = []


	def handle_endtag(self, tag):
		pass


	def handle_data(self, data):
		if True == self.region_tag_start_flag:
			text = data.decode('utf-8').strip()
			if text:
				self.region.append(text)



#获取省
def getProvince(datas):
	new_data = []
	for data in datas:
		if data[0].endswith('0000'):
			provinces.append({'code':data[0],'name':data[1],'child':[]})
		else:
			new_data.append(data)
	return new_data

#获取市
def getArea(datas):
	new_data=[]
	for data in datas:
		if data[0].endswith('00'):
			pcode = data[0][:2]+'0000'
			for p in provinces:
				if p['code'] == pcode:
					p['child'].append({'code':data[0],'name':data[1],'child':[]})
		else:
			new_data.append(data)
	return new_data

#获取区
def getCounty(datas):
	for data in datas:
		ppcode = data[0][:2]+'0000'
		pcode = data[0][:4]+'00'
		for p in provinces:
			if p['code'] == ppcode:
				for a in p['child']:
					if a['code'] == pcode:
						a['child'].append({'code':data[0],'name':data[1]})

#纠正部分数据
def correctData():
	global provinces
	for pp in provinces:
		if len(pp['child']) == 0:
			pp['child'].append({'code':pp['code'],'name':pp['name'],'child':[{'code':pp['code'],'name':pp['name']}]})
		else:
			for p in pp['child']:
				if len(p['child']) == 0:
					p['child'].append({'name':'市辖区','code':p['code']})



def writeData():
	json_str = json.dumps(provinces,ensure_ascii=False)
	with codecs.open('./region.json','w',encoding='utf-8') as rs:
		rs.write(json_str)





if __name__ == '__main__':
	headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
	res = requests.get('http://www.stats.gov.cn/tjsj/tjbz/xzqhdm/201703/t20170310_1471429.html',headers= headers)
	regionParser = RegionParser()
	regionParser.feed(res.content)
	regionParser.close()
	areaDatas = getProvince(regionParser.datas)
	countyDatas = getArea(areaDatas)
	getCounty(countyDatas)
	correctData()
	writeData()

	
			






