from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="qt-UILoader",
    version="1.0.2",
    author="xindong888",
    author_email="xindong888@163.com",
    description="只要一个ui文件，自动加载对应的逻辑类.自动绑定ui里组件到逻辑类里。自动给ui组件绑定事件。",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xindong888999/qt-UILoader.git",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        # 在这里列出您的依赖项，例如：
        # "PyQt5>=5.15",
    ],
    project_urls={
        "Bug Tracker": "https://github.com/xindong888999/qt-UILoader/issues",
    },
)