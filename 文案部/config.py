import os
from dotenv import load_dotenv

# 加载 .env 环境变量
load_dotenv()

class Config:
    """全局配置体系 (Config & Cache)"""
    
    # ------------------
    # LLM API 基础配置
    # ------------------
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-208329981b3940e89602e2afe567d227")
    DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
    
    # ------------------
    # 业务规则配置
    # ------------------
    # 平台设定：包括字数要求与基础排版指导
    PLATFORM_SPECS = {
        "小红书": {
            "word_count": "150-300字",
            "style": "干货导购/避坑指南风格。像一个懂车且精打细算的朋友给你提供选车建议，语气克制且真诚。",
            "structure": "首句直击受众选车痛点/纠结，中间用1-2个具体配置（配合竞品常识）进行降维对比，结尾给出务实选车建议。",
            "limits": (150, 300)
        },
        "抖音": {
            "word_count": "200-350字",
            "style": "短视频口播脚本的衍生文案。极具冲突感、快节奏，抛出问题后立马给解药，不拖泥带水。",
            "structure": "开头必须是二选一的疑问或高能转折（如“看xx还是看xx？”），中间用精简的数据打出优势，结尾强调性价比/实际体验。",
            "limits": (200, 350)
        },
        "今日头条": {
            "word_count": "600-800字",
            "style": "深度车评/行业快讯风格。使用媒体人的客观中立体，带有理性的市场分析与产品解读。",
            "structure": "醒目资讯标题，开头引入市场现状或普遍出行痛点，正文分段拆解核心技术（动力/空间/安全），结尾拔高质量口碑或销量背书。",
            "limits": (600, 800)
        },
        "朋友圈": {
            "word_count": "50-150字",
            "style": "朋友圈车主的真实生活切片，不经意的凡尔赛或实用派心得分享。",
            "structure": "一句话点出生活痛点，紧接一句话引出爱车解决方式及一个直观数据，不喊口号。",
            "limits": (50, 150)
        }
    }
    
    # 支持的备选车型
    SUPPORTED_CAR_MODELS = ["CR-V", "HRV", "思域", "英仕派"]
    
    # 支持的社交平台
    SUPPORTED_PLATFORMS = ["抖音", "今日头条", "小红书"]
    
    # ------------------
    # 单例缓存 (IO 缓存体系)
    # ------------------
    _material_cache = {}

    @classmethod
    def load_material(cls, file_path: str) -> str:
        """
        加载参考材料，带内存字典缓存
        [架构防御点 2]: 拦截底层并发重复 IO 读取
        """
        if file_path in cls._material_cache:
            return cls._material_cache[file_path]
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                cls._material_cache[file_path] = content
                return content
        except FileNotFoundError:
            return f"材料文件未找到：{file_path}"

# 实例化全局配置实例，供各个 Agent 直接调取
config = Config()
