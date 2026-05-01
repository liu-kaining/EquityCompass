"""
通用码生成器
支持生成不同长度、不同类型的随机码（邀请码、充值码等）
"""
import secrets
import string


class CodeGenerator:
    """通用码生成器"""
    
    # 字符集：大小写字母 + 数字（62个字符）
    CHARACTERS = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    
    def __init__(self, length=18):
        """
        初始化码生成器
        
        Args:
            length: 码的长度，默认18（邀请码）
        """
        if length < 1:
            raise ValueError("码长度必须大于0")
        self.length = length
    
    def generate(self):
        """
        生成一个随机码
        
        Returns:
            str: 生成的随机码
        """
        # 使用secrets模块生成密码学安全的随机数
        # 从62个字符中随机选择length个字符
        code = ''.join(secrets.choice(self.CHARACTERS) for _ in range(self.length))
        return code
    
    def generate_batch(self, count):
        """
        批量生成码
        
        Args:
            count: 生成数量
            
        Returns:
            list: 生成的码列表
        """
        if count < 1:
            raise ValueError("生成数量必须大于0")
        
        codes = []
        for _ in range(count):
            codes.append(self.generate())
        
        return codes
    
    @staticmethod
    def normalize_code(code):
        """
        标准化码（去除分隔符和空格，保持原始大小写）
        
        Args:
            code: 原始码
            
        Returns:
            str: 标准化后的码
        """
        if not code:
            return None
        # 去除所有分隔符和空格，但保持大小写（因为码区分大小写）
        normalized = code.replace('-', '').replace(' ', '').replace('_', '').strip()
        return normalized
    
    @staticmethod
    def format_display(code, group_size=6):
        """
        格式化显示码（添加分隔符）
        
        Args:
            code: 原始码
            group_size: 每组字符数，默认6（18字符分为3组：6-6-6）
            
        Returns:
            str: 格式化后的码，如：ABCDEF-GHIJKL-MNOPQR
        """
        if not code:
            return ''
        
        # 先标准化
        normalized = CodeGenerator.normalize_code(code)
        
        # 按group_size分组
        groups = []
        for i in range(0, len(normalized), group_size):
            groups.append(normalized[i:i+group_size])
        
        return '-'.join(groups)


# 预设的生成器实例
INVITATION_CODE_GENERATOR = CodeGenerator(length=18)  # 邀请码：18字符


def generate_invitation_code():
    """生成一个邀请码"""
    return INVITATION_CODE_GENERATOR.generate()


def generate_invitation_codes(count):
    """批量生成邀请码"""
    return INVITATION_CODE_GENERATOR.generate_batch(count)

