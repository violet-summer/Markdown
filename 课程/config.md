## kimi配置

eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ1c2VyLWNlbnRlciIsImV4cCI6MTczOTI0MDYzOSwiaWF0IjoxNzMxNDY0NjM5LCJqdGkiOiJjc3EwcmZ2YzFlY3RkMzY5c2IyZyIsInR5cCI6InJlZnJlc2giLCJhcHBfaWQiOiJraW1pIiwic3ViIjoiY3NxMHJmdmMxZWN0ZDM2OXNiMWciLCJzcGFjZV9pZCI6ImNzcTByZnZjMWVjdGQzNjlzYjEwIiwiYWJzdHJhY3RfdXNlcl9pZCI6ImNzcTByZnZjMWVjdGQzNjlzYjBnIiwic3NpZCI6IjE3MzEwODQzMDA5NTEyNDQxMDAiLCJkZXZpY2VfaWQiOiI3NDM2NTgzODY1NTQxNzE0MTgyIn0.g1My93eGILowlXcub3ebVrZPEYTAmCV-xRTXdSmBWQPCAU8v2y3svotKsEX0ARTvBrSV4sVzm0_qNLogcEMAgw

### pdftoken

sk-XLCaXZ19uJx4FzVGUmvRRHxRm7AX4iw38qgKj3qTlquteSvg

199 sk-ufSAzqPRlDRnixiHZHroJg9weWgxcVdLNtWcsZNgzeNh8nEC

## pd

1,500,000 bytes correspond to approximately 750,000 Chinese characters. This is because each Chinese character typically takes up 2 bytes in UTF-8 encoding.

每分钟200

# 配置如下，依次执行即可

## ubuntu配置jupyter的部分步骤

```

conda create -n train39 python=3.9

conda activate train39

pip install jupyter
pip install ipykernel


apt-get install vim

jupyter notebook --generate-config

vim ~/.jupyter/jupyter_notebook_config.py


直接顶部添加以下内容，允许远程访问
c.NotebookApp.ip = '*'
c.NotebookApp.open_browser = False
c.NotebookApp.port = 8888

jupyter notebook --allow-root

出现以下信息
```

![image-20241107231950722](./assets/image-20241107231950722.png)

然后自己把相应框选链接全部内容配置到server，配置完再次点击会出现下图。

![image-20241107232434855](./assets/image-20241107232434855.png)

## jupyter切换内核-原本解释器是3.9

https://juejin.cn/post/7065481886121852935

## conda导出环境

```
conda env export --no-build >env_windows.yaml

conda env export --no-build >env_linux.yaml
```



## Conda环境配置 创建一个新环境 python=3.9即可

```
pip cache purge  出现什么类找不到的问题，可能是网络问题导致文件确实，清空缓存，卸载重装即可
pip install langchain==0.3.3
pip install langchain_community==0.3.2
pip install langchain_core==0.3.15
pip install faiss-gpu==1.7.2
pip install rank_bm25==0.2.2
pip install cryptography==3.1
pip install  pydantic==2.7.4
pip install jina==3.27.19
pip install pypdf
pip install sentence-transformers
pip install modelscope
pip install pandas
pip install IPython
pip install torch
pip install jieba
pip install protobuf
pip install tiktoken
pip install faiss-gpu（windows使用conda安装pip会找不到）


推荐使用这个，git直接克隆下载可能会因为网络问题、带宽限制导致某些文件下载不成功，导致报错
modelscope download --model Xorbits/bge-reranker-large
modelscope download --model AI-ModelScope/bge-large-zh-v1.5

如果依旧有某些bin文件没有下载成功，使用如下命令
modelscope download --model AI-ModelScope/bge-large-zh-v1.5 <文件名> --local_dir <位置>

示例如下（这三个文件很大（>1g），单独下载比较靠谱）
modelscope download --model AI-ModelScope/bge-large-zh-v1.5 model.safetensors --local_dir ./bge-large-zh-v1.5
modelscope download --model AI-ModelScope/bge-large-zh-v1.5 pytorch_model.bin --local_dir ./bge-large-zh-v1.5
modelscope download --model Xorbits/bge-reranker-large model.safetensors --local_dir ./bge-reranker-large
modelscope download --model Xorbits/bge-reranker-large sentencepiece.bpe.model --local_dir ./bge-reranker-large

建议安装-作用大概和计算加速有
pip install nvidia-cublas-cu12==12.4.5.8
pip install nvidia-cuda-cupti-cu12==12.4.127
pip install nvidia-cuda-nvrtc-cu12==12.4.127
pip install nvidia-cuda-runtime-cu12==12.4.127
pip install nvidia-cudnn-cu12==9.1.0.70
pip install nvidia-cufft-cu12==11.2.1.3
pip install nvidia-curand-cu12==10.3.5.147
pip install nvidia-cusolver-cu12==11.4.5.127






```

## 依赖冲突解决

自动更新，它会检查缺失的依赖以及一些冲突的包问题

```
conda update --all
conda env update -f environment.yaml
```



```
conda install urllib3=2.2.3 libhwloc=2.11.2 tbb=2022.0.0 libblas=3.9.0=8_mkl libcblas=3.9.0=8_mkl liblapack=3.9.0=8_mkl mkl=2020.4
```

