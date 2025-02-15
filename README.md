# 拆书程序介绍文档

## 程序功能

本程序是一个用于将小说进行章节分割，并使用LLM模型生成章节纲要的工具。它基于`tkinter`库开发，提供图形用户界面，方便用户操作。

## 使用方法

1.  **安装依赖**

    首先，需要安装程序所需的依赖库。在命令行中执行以下命令：

    ```bash
    pip install tkinter langchain_openai pydantic
    ```

2.  **运行程序**

    下载程序代码后，直接运行`test.py`文件：

    ```bash
    python test.py
    ```

3.  **界面操作**

    程序启动后，会显示主窗口。用户需要在界面上填写以下参数：

    *   **Temperature**: LLM模型的temperature参数，用于控制生成文本的随机性。
    *   **Model**: LLM模型的名称。
    *   **Max Tokens**: LLM模型生成文本的最大token数。
    *   **OpenAI API Key**: OpenAI API Key，用于访问LLM模型。
    *   **OpenAI API Base**: OpenAI API Base，用于指定API的地址。

    填写完参数后，点击“选择小说文件夹”按钮，选择包含小说文件的文件夹。然后，点击“拆书”按钮，程序将自动分割章节并生成章节纲要。

4.  **自定义提示词**

    用户可以在“自定义提示词”文本框中输入自定义的提示词。程序会将这些提示词作为LLM模型的输入，以影响生成章节纲要的结果。提示词支持JSON格式和普通文本格式。如果输入的是普通文本，程序会自动将其转换为JSON格式。

## 参数说明

*   **Temperature**: LLM模型的temperature参数，类型为浮点数，默认值为0.8。
*   **Model**: LLM模型的名称，类型为字符串，默认值为"AIDC-AI/Marco-o1"。
*   **Max Tokens**: LLM模型生成文本的最大token数，类型为整数，默认值为700。
*   **OpenAI API Key**: OpenAI API Key，类型为字符串，用于访问LLM模型。
*   **OpenAI API Base**: OpenAI API Base，类型为字符串，用于指定API的地址，默认值为"https://api.siliconflow.cn/v1"。

## 注意事项

*   程序依赖于`langchain_openai`库，需要确保该库已正确安装。
*   程序使用OpenAI API，需要提供有效的API Key。
*   程序会将章节分割后的文件保存到`dataChai/data`目录下，章节纲要保存到`dataChai/<小说文件名>`目录下。
*   程序支持多线程处理，可以同时处理多个文件。
*   程序会对文件大小进行限制，超出限制的文件将不会被处理。
