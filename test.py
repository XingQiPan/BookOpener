import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import time
from datetime import datetime
import shutil
import os
import re
import threading
import queue
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
import json

def detect_encoding(file_path):
    """
        判断文件编码
    """
    return 'utf-8'


def create_or_append_file(file_path, content, mode='a'):
    """
    创建文件或在文件已存在时追加内容。

    :param file_path: 文件路径
    :param content: 要写入的内容
    :param mode: 打开文件的模式，默认为 'a'（追加模式）
    """
    file_path = os.path.abspath(file_path)

    # 确保文件所在的目录存在，如果不存在则创建
    # 这个就是注释
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # 使用'with'语句确保文件最终会被关闭
    with open(file_path, mode, encoding='utf-8') as file:
        file.write(content)
        # 如果需要在追加内容后立即保存到文件，可以调用flush()方法
        file.flush()


def create_folder(folder_path):
    """
    创建文件夹，如果文件夹已存在，则不执行任何操作。

    :param folder_path: 文件夹路径
    """
    # 使用exist_ok=True，如果文件夹已存在，不会抛出异常
    folder_path = os.path.abspath(folder_path)
    os.makedirs(folder_path, exist_ok=True)


def get_filename_and_extension(file_path):
    """
    从给定的文件路径中提取文件名和后缀。

    :param file_path: 文件的完整路径
    :return: 文件名和后缀的元组
    """
    # 获取文件的基本名称（不包含目录）
    base_name = os.path.basename(file_path)
    # 分离文件名和后缀
    file_name, file_extension = os.path.splitext(base_name)

    # os.path.splitext会保留点（.），所以如果需要可以去掉
    file_extension = file_extension.lstrip('.')
    return file_name, file_extension


def delete_directory_and_contents(dir_path):
    try:
        # 使用rmtree删除目录及其所有内容
        shutil.rmtree(dir_path)
        print(f"目录及其所有内容已被删除: {dir_path}")
    except FileNotFoundError:
        # 如果目录不存在，不执行任何操作
        print(f"目录不存在，无需删除: {dir_path}")
    except Exception as e:
        # 处理其他可能的异常
        print(f"删除目录时发生错误: {e}")


def load_file(file_path, isArray=False, encoding='utf-8'):
    """
    加载文件
    """
    file_path = os.path.abspath(file_path)
    # 检查文件是否存在
    if not os.path.exists(file_path):
        return []

    encoding = detect_encoding(file_path)
    with open(file_path, 'r', encoding=encoding) as f:
        if isArray:
            return f.readlines()
        else:
            return ''.join(f.readlines())

def get_files(dir_path):
    # 检查目录是否存在
    if not os.path.exists(dir_path):
        print(f"目录不存在: {dir_path}")
        return []
    # 获取目录下的所有文件和文件夹
    dir_path = os.path.abspath(dir_path)
    entries = os.listdir(dir_path)
    # 按照文件名排序
    entries.sort()
    # 过滤出文件，并构建完整的文件路径
    file_paths = [os.path.join(dir_path, entry) for entry in entries if os.path.isfile(
        os.path.join(dir_path, entry))]
    return file_paths


def spile_file(file_path, dir_name):
    """
    分割章节到文件
    """
    file_path = os.path.abspath(file_path)
    encoding = detect_encoding(file_path)

    path = '.'
    if dir_name:
        path = f'./{dir_name}'

    with open(file_path, 'r', encoding=encoding) as f:
        zj_w = ''
        nr_w = []
        file_name, file_extension = get_filename_and_extension(file_path)
        if file_name:
            delete_directory_and_contents(f'{path}/{file_name}')
            create_folder(f'{path}/{file_name}')

        i = 0
        #拆章节逻辑
        for line in f:
            line = line.strip()
            if (line != ''):
                zj = re.search(
                    r'^(.*?)第(\d+|[一二三四五六七八九十百千]+)[章节段][：:]?\s+[\u4e00-\u9fa5]+.*$', line)
                if (zj is None):
                    zj = re.search(
                        r'^[0-9一二三四五六七八九十百千零]+[、，,  ：:].*$', line)

                if (zj is not None and len(line) < 60):
                    if zj_w:
                        zj_h = zj_w
                        pattern = r'(第[\d一二三四五六七八九十百千万]+[章节段](?:\s+[\\u4e00-\\u9fa5]+)*)'
                        match = re.search(pattern, zj_h)
                        if match:
                            title = match.group(1)
                            zj_h = zj_h[zj_w.index(title) + len(title):]
                            zj_h = zj_h.strip()

                        i = i+1
                        zj_str = f''.join(nr_w)
                        if not zj_str:
                            continue

                        #zj_str = f'此片段的小说名称是：{file_name}，章节名称是：{zj_h}，第{i:04d}章\n\n'+zj_str
                        nr_w = []
                        create_or_append_file(
                            f'{path}/{file_name}/第{i:04d}章{zj_h}.txt', zj_str)

                    zj_w = re.sub(r'[^\w\s]+', '', line)
                else:
                    nr_w.append(str(line))
                    nr_w.append('\n')

#这个部分就是请求api。这里有不同的模型，具体可以在官网查到
#那个key是我自己的，别用我的不够用了
def get_llm_open_ai(temperature='0.8', model='AIDC-AI/Marco-o1', max_tokens=700, timeout=60*5, openai_api_key="", openai_api_base="https://api.siliconflow.cn/v1"):
    """
        获取llm ChatOpenAI
    """
    

    llama_model = ChatOpenAI(
        temperature=float(temperature),
        model=model,
        max_tokens=int(max_tokens),
        timeout=timeout,
        openai_api_key=openai_api_key_entry.get(),
        openai_api_base=openai_api_base_entry.get()
    )
    return llama_model


from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
)


def get_prompt(messages=[]):
    """
    """

    array = []
    for m in messages:
        if 'system' in m and m['system']:
            array.append(
                SystemMessagePromptTemplate.from_template(m['system']))
        if 'human' in m and m['human']:
            array.append(
                HumanMessagePromptTemplate.from_template(m['human']))
        if 'ai' in m and m['ai']:
            array.append(
                AIMessagePromptTemplate.from_template(m['ai']))

    prompt = ChatPromptTemplate(
        messages=array,
    )
    return prompt


from langchain.chains import LLMChain

def llm_chain(llm, prompt, memory=None, verbose=False):
    
    chain = LLMChain(llm=llm, prompt=prompt, memory=memory, verbose=verbose)
    return chain


# llm = get_llm_open_ai(max_tokens=1000*6)


def chai_load(file_path, messages=[], two=[], max_tokens=1000*6):
    if not os.path.exists(file_path):
        print('文件不存在')
        return ''

    # 分割章节
    spile_file(file_path, 'dataChai/data')
    file_name, file_extension = get_filename_and_extension(file_path)

    llm = get_llm_open_ai(temperature=temperature_entry.get(), model=model_entry.get(), max_tokens=max_tokens_entry.get())
    cs_shu_fx = './dataChai/'+file_name
    cs_shu = './dataChai/data/'+file_name
    cs_files = get_files(cs_shu)

    i = 0
    j = 0
    s = 0
    prompt = get_prompt(messages=[*messages, {'human': '{input}'}])
    chain = llm_chain(llm=llm, prompt=prompt, memory=None, verbose=False)
    for file_path in cs_files:
        try:
            s = s+1
            cs_yj = load_file(cs_shu_fx+'/已分析.txt', isArray=True)

            # 转换为相对路径
            current_working_directory = os.getcwd()
            relative_path = os.path.relpath(
                file_path, current_working_directory)
            if any(x.strip() == relative_path for x in cs_yj):
                continue

            res_text = ''
            cs_nr = load_file(file_path)
            res = chain.invoke({'input': cs_nr})
            res_text = res['text']

            # 再度对话 容易跑偏
            for t in two:
                res = chain.invoke({'input': t})
                res_text = res['text']
                print(res_text)

            if (int(s / 250) > 0):
                j = int(s / 250)

            #cs_file = cs_shu_fx+'/时间线.txt'
            cs_file = cs_shu_fx +'/章纲'
            # if j > 0:
            #     cs_file = f'{cs_shu_fx}/章纲{j}.txt'

            # 手动记录标题
            cs_name, cs_extension = get_filename_and_extension(file_path)
            # create_or_append_file(
            #     cs_file, f'\n\n--开始分析：{cs_name}--\n' + res_text+'\n--结束--\n\n')
            chapter_folder = os.path.dirname(cs_file) 

             # 创建并写入当前章节的分析结果到单独的 txt 文件
            chapter_file = os.path.join(chapter_folder, f'{cs_name}章纲.txt')
            # create_or_append_file(
            #     chapter_file, f'\n\nUser: ' + res_text + '\n\n' + "Assistant: " + cs_nr  + "\n\n")
            create_or_append_file(
                chapter_file, f''+res_text+'')

            relative_path = os.path.relpath(
                file_path, current_working_directory)
            create_or_append_file(cs_shu_fx+'/已分析.txt',
                                  '\n'+relative_path)
            print(f'完成({datetime.now().strftime("%H:%M:%S")})————{file_path}')
            
            # 更新进度信息
            progress_text.insert(tk.END, f'完成({datetime.now().strftime("%H:%M:%S")})————{file_path}\n')
            progress_text.see(tk.END)  # 自动滚动到最新内容

            i = i+1
            if (i > 20):
                i = 0

            time.sleep(0.4)
        except Exception as e:
            print(f"发生错误,在生成章纲中: {e}")
            messagebox.showerror("错误", f"发生错误,在生成章纲中: {e}")

#这里支持丢文件，在这个路径，可以打包提示词给他
#但我不用
# “#”是注释，不会在程序运行
cs_jc = load_file('./basics/基础.txt')
cs_sj = load_file('./basics/时间拆分.txt')
cs_bz = load_file('./basics/写作步骤.txt')
cs_qj = load_file('./basics/情节创作.txt')

#这玩意也没啥用
two = [

]




# 创建一个队列来存储待处理的文件路径
file_queue = queue.Queue()

# 定义一个工作函数，用于处理每个文件
def process_file():
    while True:
        file_path = file_queue.get()
        if file_path is None:
            break
        # 在这里执行原代码中的 chai_load 函数处理文件
        chai_load(file_path, custom_messages, two)
        file_queue.task_done()

#这里是多次请求，就是可以多次发送，智普限制最多5个请求，如果你们有新api可以改
# 创建并启动多个线程
threads = []
for _ in range(5):
    thread = threading.Thread(target=process_file)
    thread.start()
    threads.append(thread)


def select_folder():
    folder_path = filedialog.askdirectory(title="选择小说文件夹")
    if folder_path:
        files = get_files(folder_path)
        for file_path in files:
            file_size = os.path.getsize(file_path)
            if file_size > 1024 * 1024 * 30:
                messagebox.showerror("错误", f"文件 {file_path} 超出限制的文本大小")
                continue
            file_queue.put(file_path)

def run_chai_shu():
    temperature = temperature_entry.get()
    model = model_entry.get()
    max_tokens = max_tokens_entry.get()
    openai_api_key = openai_api_key_entry.get()
    openai_api_base = openai_api_base_entry.get()

    # 在这里添加你的拆书逻辑
    try:
        if messagebox.askokcancel("确认", "确定开始拆书吗？"):
            # 清空进度信息
            progress_text.delete("1.0", tk.END)
            
            # 获取自定义提示词
            try:
                global custom_messages
                custom_messages = json.loads(messages_text.get("1.0", tk.END))
            except json.JSONDecodeError:
                # 如果不是 JSON 格式，则自动转换为 JSON 格式
                prompt_text = messages_text.get("1.0", tk.END).strip()
                custom_messages = [{"system": prompt_text}]
            
            select_folder()
    except Exception as e:
        messagebox.showerror("错误", f"加载 LLM 模型时出错：{e}")

def on_closing():
    """
    窗体关闭事件处理函数
    """
    if messagebox.askokcancel("退出", "确定要退出吗？"):
        # 停止所有线程
        for thread in threads:
            file_queue.put(None)
        for thread in threads:
            thread.join()
        root.destroy()

# 创建主窗口
root = tk.Tk()
root.title("拆书程序")

style = ttk.Style()
style.theme_use('vista')  # 或者选择其他主题，如 'alt'

# 创建标签和输入框
temperature_label = ttk.Label(root, text="Temperature:", font=('Arial', 10))
temperature_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
temperature_entry = ttk.Entry(root, font=('Arial', 10))
temperature_entry.insert(0, "0.8")  # 默认值
temperature_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.E)

model_label = ttk.Label(root, text="Model:", font=('Arial', 10))
model_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
model_entry = ttk.Entry(root, font=('Arial', 10))
model_entry.insert(0, "AIDC-AI/Marco-o1")  # 默认值
model_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.E)

max_tokens_label = ttk.Label(root, text="Max Tokens:", font=('Arial', 10))
max_tokens_label.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
max_tokens_entry = ttk.Entry(root, font=('Arial', 10))
max_tokens_entry.insert(0, "700")  # 默认值
max_tokens_entry.grid(row=2, column=1, padx=10, pady=5, sticky=tk.E)

openai_api_key_label = ttk.Label(root, text="OpenAI API Key:", font=('Arial', 10))
openai_api_key_label.grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
openai_api_key_entry = ttk.Entry(root, font=('Arial', 10))
openai_api_key_entry.grid(row=3, column=1, padx=10, pady=5, sticky=tk.E)

openai_api_base_label = ttk.Label(root, text="OpenAI API Base:", font=('Arial', 10))
openai_api_base_label.grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
openai_api_base_entry = ttk.Entry(root, font=('Arial', 10))
openai_api_base_entry.insert(0, "https://api.siliconflow.cn/v1")  # 默认值
openai_api_base_entry.grid(row=4, column=1, padx=10, pady=5, sticky=tk.E)

# 创建选择文件夹按钮
style.configure('TButton', font=('Arial', 10))
select_folder_button = ttk.Button(root, text="选择小说文件夹", command=select_folder, style='TButton')
select_folder_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

# 创建拆书按钮
chai_shu_button = ttk.Button(root, text="拆书", command=run_chai_shu, style='TButton')
chai_shu_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

# 创建进度信息文本框
style.configure('TLabel', font=('Arial', 10))
progress_label = ttk.Label(root, text="拆书进度:", style='TLabel')
progress_label.grid(row=7, column=0, padx=10, pady=5, sticky=tk.W)
progress_text = tk.Text(root, height=10, width=50)
progress_text.grid(row=8, column=0, columnspan=2, padx=10, pady=5)

# 创建提示词输入框
messages_label = ttk.Label(root, text="自定义提示词:", style='TLabel')
messages_label.grid(row=9, column=0, padx=10, pady=5, sticky=tk.W)
messages_text = tk.Text(root, height=10, width=50)
messages_text.grid(row=10, column=0, columnspan=2, padx=10, pady=5)

# 注册窗体关闭事件处理函数
root.protocol("WM_DELETE_WINDOW", on_closing)

# 运行主循环
root.mainloop()

# 确保所有线程都已完成
for thread in threads:
    file_queue.put(None)
for thread in threads:
    thread.join()
