import os
import re
import chardet

def get_file_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read(4096)
        result = chardet.detect(raw_data)
        return result['encoding'] or 'utf-8'
    
def update_includes(directory):
    #步骤1：收集所有原始文件名（不包括路径）。
    original_files = set()   # 用集合避免重复
    for foldername, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(".h") or filename.endswith(".hpp"):
                if filename.startswith("S_"):
                    new_filename = filename[2:]  # 去掉"S_"前缀
                else:
                    new_filename = filename
                original_files.add(new_filename)
                new_filename2 = new_filename.replace(".", ".generated.")
                original_files.add(new_filename2)
    #步骤2：重命名所有文件（包括子目录中的文件）。
    # 我们需要再次遍历，因为第一次遍历只收集了文件名，没有记录完整路径
    for foldername, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(('.c', '.cpp', '.h', '.hpp')):
                # 构造原始文件的完整路径
                old_path = os.path.join(foldername, filename)
                # 新文件名
                if not filename.startswith("S_"):
                    new_filename = "S_" + filename
                    new_path = os.path.join(foldername, new_filename)
                    # 重命名
                    os.rename(old_path, new_path)
    #步骤3：修改文件内容。
    # 再次遍历所有文件（此时文件名已经加上S_）
    for foldername, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            # 注意：现在文件名都是加了S_的
            file_path = os.path.join(foldername, filename)
            if (file_path.endswith(".h") or file_path.endswith(".cpp")) and filename.startswith("S_"):
                # 只处理以"S_"开头的.cpp文件
                # 读取文件内容
                updated = False
                try:
                    encoding = get_file_encoding(file_path)
                    with open(file_path, 'r', encoding=encoding, errors='replace') as f:                
                        lines = f.readlines()

                    # 修改内容
                    new_lines = []
                    for line in lines:
                        # 只处理#include开头的行
                        if line.strip().startswith("#include"):
                            # 使用正则表达式精确匹配头文件名部分
                            new_line = re.sub(
                                r'(\s*#include\s+[<"])([^">]+)([">])',
                                lambda m: replace_header(m, original_files),
                                line
                            )
                            if new_line != line:
                                updated = True
                            new_lines.append(new_line)
                        else:
                            new_lines.append(line)
                except Exception as e:
                    print(f"跳过无法解码的文件: {file_path} | 错误: {str(e)}")
                    continue
                
                if updated:
                    try:
                        # 以写入模式打开文件，使用检测到的编码
                        with open(file_path, 'w', encoding=encoding, errors='replace') as f:
                            f.writelines(new_lines)
                        print(f"更新: {filename} 中的#include引用")
                    except Exception as e:
                        print(f"写入文件 {filename} 时出错: {e}")

def replace_header(match, original_files):
    """
    精确替换头文件名部分（只修改文件名，保留其他内容）
    """
    prefix = match.group(1)  # #include前的空格和引号/尖括号
    header_path = match.group(2)  # 头文件路径（可能包含目录）
    suffix = match.group(3)  # 结尾的引号/尖括号
    
    # 提取纯文件名（不含路径）
    filename = os.path.basename(header_path)
    
    # 如果文件名在原始列表中，只修改文件名部分
    if filename in original_files:
        new_filename = "S_" + filename
        # 保留路径信息（如果有）
        dir_part = os.path.dirname(header_path)
        if dir_part:
            new_header = os.path.join(dir_part, new_filename).replace('\\', '/')
        else:
            new_header = new_filename
        return prefix + new_header + suffix
    
    return match.group(0)  # 无匹配则返回原始内容


root_dir = "G:\\work\\UEPyGame\\Plugins\\PythonPluginNew\\Source"  # 替换为你的目录
update_includes(root_dir)