# -*- encoding: utf8 -*-
import json
import os
import subprocess
import threading
import sys
import time
from data import processing


pwd = os.getcwd()
print("pwd : ", pwd)
source_dir = os.getenv("SOURCE_DIR")
print("source dir : ", source_dir)
path = os.environ['PATH']

def stream_reader(proc):
    for line in proc.stdout:
        # 处理子进程的输出内容
        # 根据需要进行判断或处理
        output = line.decode().strip()
        print(output)
        if output.find('Closing VCG') != -1:
            proc.kill()
            break


def get_task_params():
    """
    获取需要任务参数
    """
    task_request_file = os.environ.get("TASK_REQUEST")
    with open(task_request_file, 'r') as fr:
        task_request = json.load(fr)
    task_params = task_request["task_params"]
    return task_params

def scan_len(language):
    to_scan = []
    file_list = []
    for root, directories, files in os.walk(source_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            file_list.append(file_path)
    # .java .jsp web.xml config.xml
    if language == "JAVA":
        for tfile in file_list:
            if tfile.endswith(".java") or tfile.endswith(".jsp") or tfile.endswith("web.xml") or tfile.endswith("config.xml"):
                to_scan.append(tfile)
    # .c .h .cpp .hpp
    if language == "CPP":
        for tfile in file_list:
            if tfile.endswith(".c") or tfile.endswith(".h") or tfile.endswith(".cpp") or tfile.endswith(".hpp"):
                to_scan.append(tfile)
    # .php php.ini	
    if language == "PHP":
        for tfile in file_list:
            if tfile.endswith(".php") or tfile.endswith("php.init"):
                to_scan.append(tfile)
    # .pls .sql .pkb .pks
    if language == "PLSQL":
        for tfile in file_list:
            if tfile.endswith(".pls") or tfile.endswith(".sql") or tfile.endswith(".pkb") or tfile.endswith(".pks"):
                to_scan.append(tfile)
    # VB:	.vb .asp .aspx web.config
    if language == "VB":
        for tfile in file_list:
            if tfile.endswith(".vb") or tfile.endswith(".asp") or tfile.endswith(".aspx") or tfile.endswith("webconfig"):
                to_scan.append(tfile)
    # C#:	.cs .asp .aspx web.config
    if language == "CS":
        for tfile in file_list:
            if tfile.endswith(".cs") or tfile.endswith(".asp") or tfile.endswith(".aspx") or tfile.endswith("web.config"):
                to_scan.append(tfile)
    # COBOL:	.cob .cbl .clt .cl2 .cics
    if language == "COBOL":
        for tfile in file_list:
            if tfile.endswith(".cob") or tfile.endswith(".cbl") or tfile.endswith(".clt") or tfile.endswith(".cl2") or tfile.endswith(".cics"):
                to_scan.append(tfile)
    return to_scan

class Invocation(object):
    def __init__(self, params):
        self.params = params

    def run(self):
        issues = []
        rules = self.params["rules"]
        language = []
        for l in rules:
            if l.find("CPP") != -1:
                language.append("CPP")
                continue
            if l.find("JAVA") != -1:
                language.append("JAVA")
                continue
            if l.find("PLSQL") != -1:
                language.append("PLSQL")
                continue
            if l.find("CS") != -1:
                language.append("CS")
                continue
            if l.find("VB") != -1:
                language.append("VB")
                continue
            if l.find("PHP") != -1:
                language.append("PHP")
                continue
            if l.find("COBOL") != -1:
                language.append("COBOL")
                continue
        tool_path = os.path.join(pwd, 'tool')
        tool_cmd = os.path.join(tool_path, 'VisualCodeGrepper.exe')
        xmlFile = os.path.join(tool_path, "tca-vcg-result.xml")
        for lset in set(language):
            to_scan = scan_len(lset)
            if to_scan:
                print(len(to_scan))
            else:
                print("file is empty , ", lset)
                continue
            if os.path.exists(xmlFile):
                print("清理xml缓存")
                os.remove(xmlFile)
            scan_cmd = [tool_cmd, '-c', '-t', source_dir, '-l', lset, '-x', xmlFile]
            print("scan_cmd : ", scan_cmd)
            process = subprocess.Popen(scan_cmd, cwd=tool_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
            stdout_thread = threading.Thread(target=stream_reader, args=(process,))
            stdout_thread.start()
            try:
                outtime = os.environ.get("VCG_TIMEOUT", "600")
                process.wait(timeout=int(outtime))
            except subprocess.TimeoutExpired:
                print("timeout")
                process.kill()
            # 等待线程结束
            stdout_thread.join()
            process.wait()
            if os.path.exists(xmlFile):
                issues.extend(processing(xmlFile, lset))
            # Yield CPU.
            time.sleep(0.0001)
        with open("result.json", "w") as fw:
            json.dump(issues, fw, indent=2)


if __name__ == '__main__':
    args = sys.argv
    if "test" in args:
        params = {"rules" : ["CPP-test"]}
        source_dir = args[-1]
        tool = Invocation(params)
        print("--- run tool ---")
        tool.run()
        print("--- end tool ---")
    else:
        print("--- start tool ---")
        params = get_task_params()
        tool = Invocation(params)
        print("--- run tool ---")
        tool.run()
        print("--- end tool ---")
