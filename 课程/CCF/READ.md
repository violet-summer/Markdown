https://www.datafountain.cn/competitions/1045

1. PDF文本提取（Bert模型）
2. 向量数据库
3. 文本向量化-已经有了模型bge-large-zh-v1.5
4. 知识库构建

通过使用RAG检索增强生成技术将私域数据作为大模型的外接知识库，可以很好地解决大模型知识幻觉的问题，这也是当前大模型应用落地的主要方式之一。而知识库的搭建与信息检索环节直接影响到最终模型的效果，是这一技术实践中的关键环节。如何设计文档解析、知识库生成、文本召回的策略，以更准确地向大模型提供用户问题对应的答案信息，具有重要的研究价值和实际意义。

**• 赛题任务**

本赛题要求选手使用运营商相关的文档构建知识库，根据用户问题检索知识库并返回答案所在的文本块。

本赛题要求选手使用运营商相关的文档构建知识库，根据用户问题检索知识库并返回答案所在的文本块。选手需要完成的任务可能包括但不限于：
（1）文档解析：将运营商相关的PDF文档解析为文本数据。
（2）知识库生成：完成文本分块和向量化处理，并存储入向量数据库，也可以尝试构建知识图谱。本赛题限定选手应使用bge-large-zh-v1.5模型进行文本向量化。
（3）文本召回：基于向量检索、关键字检索等方法设计召回策略，返回问题答案所在的文本块。

**赛题任务区分A、B榜**：
（1）A榜期间提供120篇文档和100个评测问题，所有问题的答案都可以在文档原文中找到。选手可根据A榜评测结果设计并持续改进方案及代码，排行榜将记录选手历次提交中的最高成绩。
（2）B榜期间提供70份新文档和80个新评测问题，选手需使用A榜期间设计的方案及代码，向知识库补充新文档内容后进行召回。B榜问题中约70%与新文档有关，另外30%出自A榜期间已提供的文档，所有问题的答案都可以在文档原文中找到。选手在B榜期间只可以提交三次评测,并且仅以最后一次提交的结果为准。

本赛题使用的运营商相关文档包括三类：
（1）新闻稿件150篇，部分文档经过改写或扩写，因此内容可能与现实情况不符，可能不具有现实意义，仅允许在本次比赛中使用。
（2）公开报告25篇，包括年度及半年度报告摘要、季度报告、股东大会会议资料等。
（3）通信行业权威研究报告及白皮书15篇（来源：中国信息通信研究院）。
评测问题的答案由人工标注并进行复核，具体见评测标准。

## 提交要求

选手需按submit_example.csv的格式提交UTF-8编码的评测文件。每行包括四列内容，第1列ques_id为问题编号，第2列question为问题原文，第3列answer为选手返回的问题答案所在文本块，第4列embedding为将第3列文本块使用bge-large-zh-v1.5向量模型映射得到的向量表示。选手提交的答案文件格式应与submit_example.csv严格一致。
向量模型下载地址：
https://www.modelscope.cn/models/AI-ModelScope/bge-large-zh-v1.5
B榜TOP5队伍将进入复现审核阶段，需将方案文档、源代码等压缩打包后提交，要求源代码能复现B榜榜单结果。复现审核通过后的队伍将进入决赛线下答辩评审。

## 评测标准

• **问题评分**
对于任意问题，采用如下公式评分：

**score 𝑖=[\*i\*=[ weight 𝑖𝑘𝑤×\*i\**k\**w\*× score 𝑖𝑘𝑤+(1−\*i\**k\**w\*+(1− weight 𝑖𝑘𝑤)×\*i\**k\**w\*)× score 𝑖𝑒𝑠]×𝑝𝑖\*i\**e\**s\*]×\*p\**i\***

**scoreikw**: 关键词评分。出题方为每题标注了若干答案关键词，选手提交文件的answer列中准确包含所有关键词得1分，包含部分关键词则按比例得分。
**scoreies** ：向量相似度评分。出题方为每题标注了答案所在文本块，根据选手提交文件中embedding列与标注文本块向量表示的余弦相似度打分，完全一致得1分。
**weightikw** ：关键词评分占总评分的权重。通常为0.1至0.9之间的权重，表格查数问题的关键词得分权重为1。
**pi**：长度惩罚项。根据选手 answer 的长度 𝑙𝑒𝑛𝑖𝑠𝑢𝑏*l**e**n**i**s**u**b*​ 与标注文本块长度 𝑙𝑒𝑛𝑖𝑠𝑡𝑑*l**e**n**i**s**t**d*​ 确定, 𝑙𝑒𝑛𝑖sub ≤1.5𝑙𝑒𝑛𝑖std *l**e**n**i*sub ​≤1.5*l**e**n**i*std ​ 时该项为 1;1.51;1.5 len 𝑖std <𝑙𝑒𝑛𝑖sub ≤2.5𝑙𝑒𝑛𝑖std *i*std ​<*l**e**n**i*sub ​≤2.5*l**e**n**i*std ​ 时该项为 0.9;0.9; 𝑙𝑒𝑛𝑖sub >2.5𝑙𝑒𝑛𝑖std *l**e**n**i*sub ​>2.5*l**e**n**i*std ​ 时该项为 0.75 。

• **榜单总分**
AB榜分数计算公式为：

**totalscore =∑𝑖𝑓𝑖×=∑\*i\*\*f\**i\*× score 𝑖\*i\***

**fi**：难度系数。通常为1，少部分问题的难度系数为2，它们具有以下特征之一：（1）问题答案存在于文档表格中；（2）问题答案涉及文档多个段落或者多个文档，需要选手将多个文本块合并后返回。

## 公平竞技

1.参赛团队需共同维护竞赛环境的公平公正，禁止在指定考核技术能力的范围外，利用规则漏洞或技术漏洞等不良途径提高成绩与排名，禁止在比赛中抄袭他人作品、交换答案、使用多个小号，一经发现将取消比赛成绩并严肃处理。
2.DataFountain基于自动化反作弊系统、结合人工审核，赛中动态反违规、反作弊，若收到团队封禁通知，可在指定页面申诉。



该代码是一个处理PDF文档、提取和过滤文本、将文本分块、向量化文本，并根据查询执行检索和重新排序的Python脚本。以下是代码各个部分的作用及其涉及的知识领域的解析：

### 1. 导入库
代码导入了用于文档处理、文本分割、嵌入、检索和其他实用程序的各种库。
```python
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter, TokenTextSplitter
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.retrievers.bm25 import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_community.vectorstores import Chroma, FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import pandas as pd
import numpy as np
import torch
import os
import gc
import re
from IPython.display import display
```
**知识领域**：Python、自然语言处理（NLP）、文档处理、机器学习

### 2. 设置常量
定义目录、模型和文件的常量。
```python
DOCS_DIR = './A/A_document'
EMB_MODEL = './bge-large-zh-v1.5'
RERANK_MODEL = "./bge-reranker-large"
PERSIST_DIR = './vectordb'
QUERY_DIR = './A/A_question.csv'
SUB_DIR = './submit_example.csv'
```
**知识领域**：文件处理、配置管理

### 3. 加载和显示数据
从CSV文件加载查询和提交数据，并显示前几行。
```python
query = pd.read_csv(QUERY_DIR)
sub = pd.read_csv("./submit_example.csv")
display(query.head(3))
display(sub.head(3))
```
**知识领域**：数据处理、Pandas

### 4. PDF文档解析和切分
加载并将PDF文档分割成页面。
```python
loader = PyPDFDirectoryLoader(DOCS_DIR)
pages = loader.load_and_split()
pdf_list = os.listdir(DOCS_DIR)
```
**知识领域**：文档处理、PDF处理

### 5. 文本过滤
定义一个函数，通过删除不需要的模式和字符来过滤文本。
```python
def filter_text(text):
    text = text.replace('\n','').replace(' ','')
    head_pattern = '本文档为2024CCFBDCI比赛用语料的一部分。[^\s]+仅允许在本次比赛中使用。'
    pattern1 = r"发布时间：[^\s]+发布人：新闻宣传中心"
    pattern2 = r"发布时间：[^\s]+发布人：新闻发布人"
    pattern3 =  r'发布时间：\d{4}年\d{1,2}月\d{1,2}日'
    news_pattern = head_pattern+'|'+pattern1+'|'+pattern2+'|'+pattern3
    text = re.sub(news_pattern,'',text)
    report_pattern1 = '第一节重要提示[^\s]+本次利润分配方案尚需提交本公司股东大会审议。'
    report_pattern12 = '一重要提示[^\s]+股东大会审议。'
    report_pattern13 = '一、重要提示[^\s]+季度报告未经审计。'
    report_pattern2 = '本公司董事会及全体董事保证本公告内容不存在任何虚假记载、[^\s]+季度财务报表是否经审计□是√否'
    report_pattern3 = '中国联合网络通信股份有限公司（简称“公司”）董事会审计委员会根据相关法律法规、[^\s]+汇报如下：'
    report_pattern = report_pattern1+'|'+report_pattern12+'|'+report_pattern13+'|'+report_pattern2+'|'+report_pattern3
    text = re.sub( report_pattern,'',text)
    return text
```
**知识领域**：文本处理、正则表达式

### 6. 应用文本过滤
应用文本过滤函数到加载的PDF文本并将结果保存到文件。
```python
for pdf_id in pdf_text.keys():
    pdf_text[pdf_id] = filter_text(pdf_text[pdf_id])
with open('AZ.txt','w',encoding = 'utf-8') as file:
    pdf_all = ''.join(list(pdf_text.values())).encode('utf-8', 'replace').decode('utf-8')
    file.write( pdf_all)
```
**知识领域**：文件处理、文本处理

### 7. 加载和分割文本
加载过滤后的文本并将其分割成块。
```python
from langchain_community.document_loaders import TextLoader
loader = TextLoader("AZ.txt",encoding="utf-8")
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=245,
        chunk_overlap=128,
        separators = ["。", "！", "？"],
        keep_separator='end',
    )
docs = text_splitter.split_documents(documents)
```
**知识领域**：文本分割、NLP

### 8. 向量化文本
使用预训练模型嵌入文本块并保存嵌入。
```python
embeddings = HuggingFaceEmbeddings(model_name=EMB_MODEL, show_progress=True)
vectordb = FAISS.from_documents(
    documents=docs,
    embedding=embeddings,
)
vectordb.save_local(PERSIST_DIR)
```
**知识领域**：嵌入、向量数据库、机器学习

### 9. 设置检索器
设置密集和BM25检索器并将它们组合成一个集成检索器。
```python
import jieba
dense_retriever = vectordb.as_retriever(search_kwargs={"k": 5})
bm25_retriever = BM25Retriever.from_documents(
    docs,
    k=5,
    bm25_params={"k1": 1.5, "b": 0.75},
    preprocess_func=jieba.lcut
)
ensemble_retriever = EnsembleRetriever(retrievers=[bm25_retriever, dense_retriever], weights=[0.4, 0.6])
```
**知识领域**：信息检索、NLP

### 10. 文本召回和重排
定义一个函数，根据查询检索和重新排序文本。
```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

def rerank(questions, retriever, top_n=1, cut_len=384):
    rerank_model = HuggingFaceCrossEncoder(model_name=RERANK_MODEL)
    compressor = CrossEncoderReranker(model=rerank_model, top_n=top_n)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, base_retriever=retriever
    )
    rerank_answers = []
    for question in tqdm(questions):
        relevant_docs = compression_retriever.invoke(question)
        answer=''
        for rd in relevant_docs:
            answer += rd.page_content
        rerank_answers.append(answer[:245])
    return rerank_answers

questions = list(query['question'].values)
rerank_answers = rerank(questions, ensemble_retriever)
print(rerank_answers[0])
```
**知识领域**：信息检索、NLP、机器学习

### 11. 嵌入答案
使用预训练模型嵌入重新排序的答案。
```python
def emb(answers, emb_batch_size = 4):
    model = SentenceTransformer(EMB_MODEL, trust_remote_code=True)
    all_sentence_embeddings = []
    for i in tqdm(range(0, len(answers), emb_batch_size), desc="embedding sentences"):
        batch_sentences = answers[i:i+emb_batch_size]
        sentence_embeddings = model.encode(batch_sentences, normalize_embeddings=True)
        all_sentence_embeddings.append(sentence_embeddings)
    all_sentence_embeddings = np.concatenate(all_sentence_embeddings, axis=0)
    print('emb_model max_seq_length: ', model.max_seq_length)
    print('emb_model embeddings_shape: ', all_sentence_embeddings.shape[-1])
    del model
    gc.collect()
    torch.cuda.empty_cache()
    return all_sentence_embeddings

all_sentence_embeddings = emb(rerank_answers)
```
**知识领域**：嵌入、机器学习

### 12. 保存结果
将重新排序的答案及其嵌入保存到CSV文件。
```python
sub['answer'] = rerank_answers
sub['embedding']= [','.join([str(a) for a in all_sentence_embeddings[i]]) for i in range(len(all_sentence_embeddings))]
sub.to_csv('submit.csv', index=None)
sub.head()
```
**知识领域**：数据处理、Pandas、文件处理