# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import re
import json
import requests


class MadrasHcOriginalSpider(scrapy.Spider):


	years = range(2018, 1949, -1)
	case_no = range(1,100000)
	case_type = ["A","APPLN","APPL.","CMSA","CMA","CMA(MD)","CMP","CMSA(MD)","CMP(MD)",
				 "CRP NPD(MD)","CRP PD(MD)","CRP NPD","CRP PD","CRP","CRP(MD)","CS",
				 "CMA(MD)","CMA NPD","CMA PD","CMP(MD)","COM APEL","COMP.A","CP","CONT(MD)",
				 "CONT A","CONT A(MD)","CONT APP","CONT P","CONT P(MD)","CRL A","<br />CRL A(MD)",
				 "CRL MP","CRL MP(MD)","CRL OP","CRL OP(MD)","CRL RC","CRL RC(MD)","CLMP(MD)",
				 "CLOP(MD)","CROS.OBJ","CROS.OBJ(MD)","CRP(MD)","ELP","EP","AS","HCMP","HCMP(MD)",
				 "HCP","HCP(MD)","IA","IC","IN","IP","LTS","LPA","LPA(MD)","MC(MD)","MC","MP",
				 "MP(MD)","OA","OMS","OP","OSA","RCMP","RCP","RC","RT","RT(MD)","REVW(MD)","REV.(MD)",
				 "REV.APLC(MD)","REV.APCR(MD)","REV.APLW(MD)","REV.APPL(MD)","REV.APPL","REV.APLC",
				 "REV.APLW","REV.W(MD)","REV.STP","REV.STP(MD)","SA","SA(MD)","STA","STP","SUB A",
				 "SUB APPL","SCMP","SCP","TCA","TCA(MD)","TCP","TCP(MD)","TC(MD)","TC","TCMP","TCMP(MD)",
				 "TC(MD)","TOS","TMA","TMA(MD)","TMSA","TMSA(MD)","TR APPL","TR CMP","TR CMA","TRCS",
				 "TR AS","VCMP","WVMP","WAMP","WPMP","WA(MD)","WAMP(MD)","WP(MD)",
				 "WPMP(MD)","WA","WA(MD)","WMP","WMP(MD)","WP","WP(MD)","WVMP(MD)"]


	name = 'madras_hc_original'
	allowed_domains = ['courtnic.nic.in']
	start_urls = ['http://courtnic.nic.in/']

	count = 0


	def start_requests(self):
		
		
		for year in self.years:
			for case_types in self.case_type:
				for case_nos in self.case_no:
					if self.count >= 500:
						self.count = 1
						break

					entity_id = case_types + "/" + str(case_nos) + "/" + str(year)

					
					

					yield scrapy.Request(url='http://courtnic.nic.in/HCS/list_new2_v1.asp?ctype=' + str(case_types) + "&cno="+ str(case_nos) + "&Cyear="+ str(year) + "&Court_Id=3", callback=self.getCaseDetails, meta={'entity_id': entity_id})

					




	def getCaseDetails(self, response):

		
		error_500 = response.xpath("/html/body/p[1]/font/strong/text()")
		error_404 = response.xpath("//center//text()")
		
		if (len(error_500) != 0) or (len(error_404) != 0):
			self.count+=1
		else:
			self.count=1

			td = response.xpath("//table")[2]
			rows = td.xpath("tr")
			cased = {}
			cased = {el.xpath("td/text()").extract()[0]:el.xpath("td/text()").extract()[1] for el in rows if len(el.xpath("td/text()").extract()) == 2}
		
			case_status = cased["Case Status :"]

			case_updated_on = ""

			try:
				case_updated_on = cased["Case Updated On :"]
			except:
				print("")

			val = cased["Status Of :"]
			status_of = re.sub("<.*?>", "", str(val).replace('\xa0', u' '))
			as_of = status_of.split("  ")
			as_off = as_of[1:4]
			status_off = as_of[0]
			as_offf = ' '.join(j for j in as_off)

			last_date_of_hear = ""
			try :
				last_date_of_hear = cased["Last Hearing Date :"]
			except :
				print("")
			
			val1 = cased["Litigants :"]
			petitioner = re.sub("<.*?>", "", str(val1).replace('\xa0', u' '))
			respondent = petitioner.split("  ")
			petitionerr = respondent[0]
			respondentt = respondent[1:4]
			respondenttt = respondentt[1]
			next_date_of_hear = ""
			try :
				next_date_of_hear = cased["Next / Final Date of Hearing :"]
			except :
				print("")
			category = cased["Category :"]
			
			entity_id = response.meta["entity_id"]

			pet_adv = ""
			res_adv = ""

			try:
				pet_adv = cased["Pet's Adv :"]
			except:
				print("")

			try:
				res_adv = cased["Res's Adv :"]
			except:
				print("")
			
			
			
			conn_apps = response.xpath("//td//text()").extract()
			conn_apps1 = conn_apps.index("Connected Application(s)")
			conn_apps2 = conn_apps.index("Connected Matter(s)")
			con_applications = conn_apps[conn_apps1 + 1 : conn_apps2]

			try:
				orders = conn_apps.index("Order(s)")
			except:
				orders = None


			if orders is not None:
				con_applications = conn_apps[conn_apps1 + 1 : orders]
			else:
				con_applications = conn_apps[conn_apps1 + 1 : conn_apps2]

			
	
			coco = dict()

			countt=0

			
			if con_applications[0] != "No Connected Application" :
				while countt<len(con_applications):
				
					try  :
					
						con_apps_casetype = con_applications[countt]
						con_apps_caseno = con_applications[countt+1]
						con_apps_caseyear = con_applications[countt+2].strip()


						coco[countt] = {
										'case_type':con_apps_casetype,
										'case_no':con_apps_caseno,
										'case_year' : con_apps_caseyear,
										'relation_type': 'C'
									}
						

						countt+=3

						
					except :
						print("No Connected Application")
s
	

	
			
			
			con_matters = conn_apps[conn_apps2 + 1 : ]
			
			
			i=0

			
			if con_matters[0] != "No Connected Cases" :
				while i<len(con_matters):
				
					try :

					
						con_matters_casetype = con_matters[0]
						con_matters_caseno = con_matters[1]
						con_matters_caseyear = con_matters[2].strip()
						

						coco[countt] = {
										'case_type':con_matters_casetype,
										'case_no':con_matters_caseno,
										'case_year' : con_matters_caseyear,
										'relation_type': 'M'
									}
						i+=3
					except :
	
						print("No Connected Cases")

						
				



			pdf_url = response.css('a::attr(href)').extract()
			pdf_date = response.css('.MyTD:nth-child(12) td::text').extract()

		
			
			em = ""
			el = ""

	

			for el in pdf_url:
				if el != "":
					el="http://courtnic.nic.in/hcs/" + str(el)
					em+=el.strip() 
				else :
					print("")

		



			ll = ""

			for el in pdf_date:
				if el == "Connected Matter(s)" or el == "No Orders":
					print("")
					
				else :
					ll += el.strip()




			API_ENDPOINT = "https://ychineelcc.execute-api.ap-south-1.amazonaws.com/prod/PDFtoS3"        
			data = {'url': em}
			r = requests.post(url=API_ENDPOINT, json=data)

			pdf = ""

			try: 
				for rr in em:
					if rr != "":
						pdf = r.text
						break
			except:
				print("")
			

		


			item = {
						'case':
							{'case_status' : case_status,
							'status_of' : status_off,
							# 'As of' : as_offf,
							'petitioner' : petitionerr,
							'respondent' : respondenttt,
							'pet_adv' : pet_adv,
							'res_adv' : res_adv,
							'last_date_of_hearing ' : last_date_of_hear,
							'next/final_date_of_hearing' : next_date_of_hear,
							'case_updated_on' : case_updated_on,
							'category' : category},
					
						'judgement' : 
							{'pdf' : pdf,
							'judgement_date' : ll,
							'judgement_type' : 'O'},
					
						'connected_case' : coco
					}
							



			yield item







			# lamb = "https://ss91qgkk47.execute-api.ap-south-1.amazonaws.com/prod/testNode"
			# jsonu = json.dumps({"entity_id": entity_id, "entity_type": "case", "source": "court.nic.in/madras-original", "data": item, "processed" : False})
			# bornAgainDict = json.loads(jsonu.replace('""','"null"'))
			# r = requests.post(lamb, json=bornAgainDict)

			
			

		
		
