# -*- encoding: utf8 -*-
import json
import os
import xml.etree.ElementTree as ET

def find_line_number(file_name, code_line):
    encodings = ['utf-8', 'gbk']  # 定义要尝试的编码列表
    
    for encoding in encodings:
        try:
            with open(file_name, "r", encoding=encoding) as fr:
                i = 0
                for line in fr:
                    i += 1
                    if line.find(code_line) != -1:
                        return i
        except UnicodeDecodeError:
            continue  # 如果出现UnicodeDecodeError异常，尝试下一个编码
    
    return 0  # 如果所有的编码都尝试完毕后仍然出现异常，则返回0


def processing(xmlFilePath, language):
    tree = ET.parse(xmlFilePath)
    root = tree.getroot()
    issues = []
    # 遍历所有的CodeIssue标签
    for code_issue in root.iter('CodeIssue'):
        priority = code_issue.find('Priority').text
        severity = code_issue.find('Severity').text
        title = code_issue.find('Title').text
        description = code_issue.find('Description').text
        file_name = code_issue.find('FileName').text
        line = code_issue.find('Line').text
        code_line = code_issue.find('CodeLine').text
        checked = code_issue.find('Checked').text
        check_colour = code_issue.find('CheckColour').text
        if code_line:
            line = find_line_number(file_name, code_line)
        else:
            line = 0
        issues.append(
            {
                "path": file_name,
                "rule": language + '-' + severity,
                "msg": "title : " + title + '\n' + "description : " + description,
                "line": line
            }
        )
    return issues
