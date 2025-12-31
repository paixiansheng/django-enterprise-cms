import os

# 定义项目根目录名称（可根据你的实际需求修改，默认与之前规划一致）
PROJECT_ROOT = "django-enterprise-cms"

# 定义完整的目录和文件结构
# 格式：(路径, 是否为目录, 若为文件则指定内容，空字符串表示空白文件)
PROJECT_STRUCTURE = [
    # 项目根目录下的文件（先创建已规划的文档）
    (f"{PROJECT_ROOT}/project_function_list.md", False, ""),
    (f"{PROJECT_ROOT}/project_tech_stack.md", False, ""),
    (f"{PROJECT_ROOT}/requirements.txt", False, ""),
    (f"{PROJECT_ROOT}/.gitignore", False, ""),
    (f"{PROJECT_ROOT}/README.md", False, ""),
    # 虚拟环境目录（仅创建目录，后续由venv自动填充）
    (f"{PROJECT_ROOT}/django_env", True, ""),
    # Django项目核心配置目录（先创建骨架，后续用django-admin初始化）
    (f"{PROJECT_ROOT}/django_cms", True, ""),
    (f"{PROJECT_ROOT}/django_cms/settings", True, ""),
    (f"{PROJECT_ROOT}/django_cms/settings/__init__.py", False, ""),
    (f"{PROJECT_ROOT}/django_cms/settings/dev.py", False, ""),
    (f"{PROJECT_ROOT}/django_cms/settings/prod.py", False, ""),
    (f"{PROJECT_ROOT}/django_cms/urls.py", False, ""),
    (f"{PROJECT_ROOT}/django_cms/asgi.py", False, ""),
    (f"{PROJECT_ROOT}/django_cms/wsgi.py", False, ""),
    (f"{PROJECT_ROOT}/django_cms/__init__.py", False, ""),
    # 业务应用目录
    (f"{PROJECT_ROOT}/apps", True, ""),
    (f"{PROJECT_ROOT}/apps/__init__.py", False, ""),
    # 全局模板目录
    (f"{PROJECT_ROOT}/templates", True, ""),
    (f"{PROJECT_ROOT}/templates/base.html", False, ""),
    (f"{PROJECT_ROOT}/templates/404.html", False, ""),
    (f"{PROJECT_ROOT}/templates/500.html", False, ""),
    # 全局静态资源目录
    (f"{PROJECT_ROOT}/static", True, ""),
    (f"{PROJECT_ROOT}/static/css", True, ""),
    (f"{PROJECT_ROOT}/static/js", True, ""),
    (f"{PROJECT_ROOT}/static/plugins", True, ""),
    # 用户上传文件目录
    (f"{PROJECT_ROOT}/media", True, "")
]

def create_project_structure():
    """
    自动创建项目目录和空白文件
    """
    # 遍历所有需要创建的路径
    for path, is_dir, content in PROJECT_STRUCTURE:
        try:
            # 如果是目录，创建目录（递归创建父目录，已存在则不报错）
            if is_dir:
                os.makedirs(path, exist_ok=True)
                print(f"✅ 成功创建目录：{path}")
            # 如果是文件，先创建父目录，再创建文件（已存在则不覆盖）
            else:
                # 获取文件父目录
                parent_dir = os.path.dirname(path)
                os.makedirs(parent_dir, exist_ok=True)
                # 仅当文件不存在时创建，避免覆盖已有内容
                if not os.path.exists(path):
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"✅ 成功创建文件：{path}")
                else:
                    print(f"ℹ️ 文件已存在，跳过创建：{path}")
        except Exception as e:
            print(f"❌ 创建失败 {path}：{str(e)}")

if __name__ == "__main__":
    print("开始自动创建Django项目目录结构...\n")
    create_project_structure()
    print("\n🎉 项目目录结构创建完成！")
    print(f"📌 项目根目录：{os.path.abspath(PROJECT_ROOT)}")