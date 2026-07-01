def readFile(self,file_path:str):
    #将路径转换为绝对路径，并解析其中的 ...
    path = Path(file_path).resolve()
    if not path.exists() or not path.is_file():
        raise ValueError(f"文件不存在{file_path}")
    logger.info("开始索引文件")
    try:
        #读取文件内容
        #with open(file_path,"r",encoding="utf-8") as f:
        content = path.read_text(encoding="utf-8")
        logger.info(f"读取文件{file_path}，内容长度：{len(content)}字符")

        #删除该文件的旧数据（如果存在）
        normalized_path = path.as_posix()#解析为标准路径 统一用 / 分隔

    except Exception as e:
        logger.error(e)

###################################
from pathlib import Path
KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = KNOWLEDGE_DIR / "config_5/config.py"
