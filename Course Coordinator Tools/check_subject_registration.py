import re
from subprocess import check_output
import os.path
#convert PDF to text first.

allowable_codes = set([	#core modules
						"DM2230-02",
						"DM2240-02",
						"DM2241-02",
						"DM2242-02",
						"DM2243-02",						
						# SP
						"DM2295-01",
						# compulsory GSMs
						
						# GSMs
						"DMS153-01",
						"DMS270-01",
						"DMS271-01",
						"DMS272-01",
						"DMS257-01",
						"DMS221-01",
						"DMS250-01",
					])

def convert_to_text(PDF_filename):
	text_filename = os.path.splitext(PDF_filename)[0] + ".txt"	
	print check_output(["pdftotext.exe", "-table" , PDF_filename, text_filename], shell=True)
	return text_filename

def extract_modules(filename):
	adminID = ""
	GSMCount = 2
	with open(filename, 'r') as f:
		for line in f:						
			m = re.search("([0-9]{6}[A-Z])", line)
			if m and adminID != m.group(1):					
				if GSMCount != 2:
					print "adminID %s has %d GSMs" % (adminID, GSMCount)
				 
				adminID = m.group(1)				
				GSMCount = 0				

			m = re.search("(DMS?[0-9]{3,4}\-[0-9]{2})", line)
			if m:												
				module_group = m.group(1)
				if module_group not in allowable_codes:
					print adminID, module_group, "not in list"

			m = re.search("(GSM)", line)
			if m:
				GSMCount += 1
			
def extract_GSMs(filename):
	adminID = ""
	with open(filename, 'r') as f:
		for line in f:						
			m = re.search("([0-9]{6}[A-Z])", line)
			if m and adminID != m.group(1):									
				adminID = m.group(1)				
				
			m = re.search("([A-Z]+)\s+(DMS[0-9]{3,4}\-[0-9]{2})", line)
			if m:												
				module_group = m.group(2)
				module_abbr = m.group(1)
				if module_abbr != 'NE':
					print "%s\t%s\t%s" % (adminID, module_group, module_abbr)
	
text_filename = convert_to_text(r"C:\Users\simtj\OneDrive\Work\GDT15\PEM\2016S2/2016S2GD1504.pdf")

extract_modules(text_filename)
#extract_GSMs(text_filename)