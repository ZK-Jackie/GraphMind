import os
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QProgressBar,
                             QGridLayout, QHBoxLayout, QFileDialog, QInputDialog, QMessageBox)
from dotenv import load_dotenv, find_dotenv

from graphmind.adapter.engine.hierarchy.engine import HierarchyEngine
from graphmind.adapter.reader.markdown import MarkdownReader
from graphmind.core.base import GraphmindModel, get_default_llm, get_default_embeddings, get_default_database


class MainWindow(QWidget):
    input_text: QLineEdit = None
    browse_button: QPushButton = None
    start_button: QPushButton = None
    config_button: QPushButton = None
    progress_label_left: QLabel = None
    progress_bar: QProgressBar = None
    progress_label_right: QLabel = None
    bottom_label: QLabel = None

    def __init__(self):
        super().__init__()
        self.initUI()
        self.initState()
        self.start_button.clicked.connect(self.start_button_clicked)
        self.config_button.clicked.connect(self.config_button_clicked)
        self.browse_button.clicked.connect(self.browse_button_clicked)

    def browse_button_clicked(self):
        # 获取文件夹
        file_path = self.input_text.text()
        file_path = QFileDialog.getExistingDirectory(self, "选择文件夹", file_path)
        if file_path or file_path != "":
            self.input_text.setText(file_path)
            self.start_button.setEnabled(True)
            self.bottom_label.setVisible(True)
            self.bottom_label.setText("等待开始...")
            QMessageBox.about(self, "选择文件夹", "选择文件夹成功！")

    def start_button_clicked(self):
        # 顶部按钮全部禁用
        self.start_button.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.config_button.setEnabled(False)
        # 底部标签显示
        self.bottom_label.setVisible(True)
        self.bottom_label.setText("构建中...")
        # 1 读取文件路径
        file_path = self.filePathPreviewEdit.text()
        # 2 执行构建
        try:
            models = GraphmindModel(llm=get_default_llm(),
                                    llm_batch_size=os.getenv("LLM_CONCUR_NUM", 20),
                                    task_buffer_size=os.getenv("TASK_BUFFER_SIZE", 32),
                                    embeddings=get_default_embeddings(),
                                    database=get_default_database(debug=True))
            reader = MarkdownReader(file=file_path, skip_mark="<abd>", file_title="离散数学")
            engine = HierarchyEngine(models=models, reader=reader, work_name="离散数学")
            engine.execute()
        except Exception as e:
            self.bottom_label.setText(f"构建失败：{e[0:100]}...")

    def config_button_clicked(self):
        # 读取 .env 文件内容
        env_file = '.env'
        template_file = ".env.template"

        try:
            env_file_path = find_dotenv(env_file)
            with open(env_file_path, 'r', encoding="utf-8") as file:
                env_content = file.read()
        except FileNotFoundError:
            env_file_path = find_dotenv(template_file)
            with open(env_file_path, 'r', encoding="utf-8") as file:
                env_content = file.read()

        # 显示弹窗并获取用户输入
        value, ok = QInputDialog.getMultiLineText(self, "参数配置", "请在开发人员的指导下修改参数：", env_content)
        if ok:
            # 更新 .env 文件内容
            with open(env_file, 'w', encoding="utf-8") as file:
                file.write(value)
            QMessageBox.about(self, "参数配置", "参数配置成功！")
            load_dotenv(env_file)

    def initUI(self):
        # 创建网格布局
        layout = QGridLayout()

        # 添加软件版本标签
        version_label = QLabel("基于大语言模型的知识图谱构造软件 V1.0", self)
        # 设置字体
        version_label.setStyleSheet("font-size: 36px;")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label, 0, 0, 1, 3)

        # 创建文本输入框和浏览按钮
        self.input_text = QLineEdit(self)
        self.browse_button = QPushButton("浏览", self)
        layout.addWidget(self.input_text, 1, 0, 1, 2)
        layout.addWidget(self.browse_button, 1, 2)
        # 参数：组件对象，当前组件行号（从 0 开始），当前组件列号（从 0 开始），组件占用的行数，组件占用的列数。

        # 创建水平布局，填入开始构建和配置参数按钮
        hbox_layout = QHBoxLayout()
        self.start_button = QPushButton("开始构建", self)
        self.config_button = QPushButton("配置参数", self)
        hbox_layout.addWidget(self.start_button)
        hbox_layout.addWidget(self.config_button)
        # 创建一个容器小部件来包含水平布局，并让它占用第二行整行
        container_widget = QWidget()
        container_widget.setLayout(hbox_layout)
        layout.addWidget(container_widget, 2, 0, 1, 3)

        # 创建进度条和标签
        self.progress_label_left = QLabel("TextLabel", self)
        self.progress_label_left.setAlignment(Qt.AlignRight)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(24)  # 设置进度条初始值
        self.progress_label_right = QLabel("TextLabel", self)
        self.progress_label_left.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.progress_label_left, 3, 0)
        layout.addWidget(self.progress_bar, 3, 1)
        layout.addWidget(self.progress_label_right, 3, 2)

        # 底部文本标签
        self.bottom_label = QLabel("TextLabel", self)
        self.bottom_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.bottom_label, 4, 0, 1, 3)

        # 设置窗口布局
        self.setLayout(layout)

        # 设置样式表，放大所有内容
        self.setStyleSheet("""
                    QWidget {
                        font-size: 24px;  /* 放大字体 */
                    }
                    QLineEdit, QPushButton, QLabel, QProgressBar {
                        min-height: 50px;  /* 放大组件高度 */
                        min-width: 200px;  /* 放大组件宽度 */
                    }
                """)

        # 设置窗口属性
        self.setWindowTitle('基于大语言模型的知识图谱构造软件 V1.0')
        self.setFixedSize(800, 600)  # 设置固定窗口大小
        self.show()

    def initState(self):
        # 设置输入框为只读
        self.input_text.setReadOnly(True)
        # 设置按钮初始时不可用
        self.start_button.setEnabled(False)
        # 设置下方内容隐藏
        self.progress_label_left.setVisible(False)
        self.progress_bar.setVisible(False)
        self.progress_label_right.setVisible(False)
        # 设置底部消息栏隐藏
        self.bottom_label.setVisible(False)
