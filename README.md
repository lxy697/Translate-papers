# Translate-papers

一个基于MinerU、DeepSeek的全自动论文翻译器，以及中英文对照阅读解决方案

### 使用方法

1. 下载本项目代码，安装python及对应软件包
  
2. 注册DeepSeek，创建并充值APIkey，并将APIkey粘贴到main.py中的对应位置
  
3. 下载MinerU客户端，将其下载路径设置为本项目中的paper文件夹
  
4. 将论文PDF文件拖拽到MinerU中，等待一会。
  
5. 双击本项目中的run.bat文件（win系统），等待软件运行结束后即可在`/paper/<文献名>/` 路径中找到Markdown格式的中文与英文论文。
  
  若翻译过程中出现网络不稳定、DeepSeek服务不稳定、用户手动中断程序等异常情况，待程序结束后再次双击run.bat即可，已经成功翻译过的段落不会被重新翻译。
  

### 依赖的项目

- [MinerU]([opendatalab/MinerU: A high-quality tool for convert PDF to Markdown and JSON.一站式开源高质量数据提取工具，将PDF转换成Markdown和JSON格式。](https://github.com/opendatalab/MinerU)) 一个通过OCR将PDF转为Markdown的工具
  
- （可选）[obsidian-releases](https://github.com/obsidianmd/obsidian-releases) 一个笔记软件，用于阅读输出的文献。
  

### 其他

- 本项目输出的 `output_text_cn.md` 与 `output_text_en.md` 两个文件中的中英内容是逐行对应的，因此强烈建议使用Obsidian的 `Markdown Sync Scroll` 插件进行中英文对照阅读，可以同步滚动中英文文档。
  
- 文献翻译依赖于OCR识别与大语言模型，可能会出现不稳定的情况。
