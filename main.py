#-*- coding:utf-8 -*-

import sys
from xml.sax import ContentHandler
from xml.sax import make_parser

INSTURCTION = u'''
//------------------------------------------------------------
//此文件导表生成，无需手动添加
//------------------------------------------------------------
'''

DEFINE_HEAD = u"#define"

begin = u"//----------------------- Auto Genrate Begin --------------------\n"
end = u"//----------------------- Auto Genrate End   --------------------\n"
ifndef = u"#ifndef __IDIP_TOOL_H__\n"
define = u"#define __IDIP_TOOL_H__\n"
endif = u"#endif\n"

#用sax处理xml
class IdipHandler(ContentHandler):
	def __init__(self):
		self.all_cmds_flag = False
		self.cmd_info_flag = False
		self.all_cmds = {}
		self.cmd_info = {}
		pass
	
	def startElement(self, name, attrs):
		if name == "command" and attrs.has_key("name") and attrs["name"] == "cmd":
			self.all_cmds_flag = True
		if name == "entry" and self.all_cmds_flag is True:
			cmd_info = {}
			cmd = attrs["cmd"]
			req = attrs["req"]
			rsp = attrs["rsp"]
			desc = attrs["desc"]
			cmd_info["req"] = req
			cmd_info["rsp"] = rsp 
			cmd_info["desc"] = desc
			self.all_cmds[cmd] = cmd_info

		if name == "macrosgroup" and attrs.has_key("name") and attrs["name"] == "NET_CMD_ID":
			self.cmd_info_flag = True
		if name == "macro" and self.cmd_info_flag is True:
			self.cmd_info[attrs["name"]] =  attrs["value"]
		pass
	
	def characters(self, data):
		pass
	
	def endElement(self, name):
		if name == "command":
			self.all_cmds_flag = False
		if name == "macrosgroup":
			self.cmd_info_flag = False 
		pass

def write_file(all_cmds, cmd_info, output_file):
	try:
		with open(output_file, "w+b") as fd:
			fd.write(INSTURCTION.encode("utf-8"))	
			fd.write(ifndef + define + "\n")
			#fd.write(define)
			#fd.write("\n")
			for info in all_cmds.itervalues():
				desc = info["desc"].encode("utf-8")
				req = info["req"]
				rsp = info["rsp"]
				fd.write("//" + desc + "\n")
				fd.write(DEFINE_HEAD + " " + req + " " + "(" + str(int(cmd_info[req], 16)) + ")" + "\n")
				fd.write(DEFINE_HEAD + " " + rsp + " " + "(" + str(int(cmd_info[rsp], 16)) + ")" + "\n")
			fd.write("\n")

			fd.write("mapping ReqCmd2ResCmd = { \n")
			for info in all_cmds.itervalues():
				desc = info["desc"].encode("utf-8")
				req = info["req"]
				rsp = info["rsp"]
				fd.write("//" + desc + "\n")
				fd.write(req + ":" + rsp + "," + "\n")
			fd.write("}" + "\n")
			fd.write("\n" + endif)
			#fd.write(endif)
	except:
		msg = "\rcan not write to " + output_file 
		print msg 
		raise()

def handler_xml(xml_file, output_file):
	parser = make_parser()
	handler = IdipHandler()
	parser.setContentHandler(handler)
	parser.parse(xml_file)

	write_file(handler.all_cmds, handler.cmd_info, output_file)
	#print handler.all_cmds
	#print handler.cmd_info


USAGE="python gen_idip_xml.py path idip.xml idiptool.h"

if __name__== "__main__":
	if len(sys.argv) != 4:
		print USAGE
		exit(1)
	
	path, xml_file, output_file = sys.argv[1:]
	handler_xml(xml_file, output_file)



