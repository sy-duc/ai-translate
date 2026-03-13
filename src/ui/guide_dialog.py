"""
User guide dialog with basic usage instructions.
Content changes based on the current UI language.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton
from PyQt6.QtCore import Qt

from src.i18n import I18nManager

# Guide content per language (HTML format for QTextBrowser)
_GUIDE_CONTENT = {
    "vi": """
<h2>Hướng dẫn sử dụng AI Translate</h2>

<h3>1. Dịch tài liệu cơ bản</h3>
<ol>
  <li>Nhấn <b>Chọn file</b> để chọn 1 hoặc nhiều file cần dịch</li>
  <li>Chọn <b>Ngôn ngữ đích</b> (Tiếng Việt, English, Japanese)</li>
  <li>Nhấn <b>Dịch</b></li>
  <li>Đợi hoàn tất, xem kết quả trong dialog thông báo</li>
</ol>

<h3>2. Tùy chọn nâng cao</h3>
<ol>
  <li>Nhấn <b>Mở rộng >></b> để hiển thị thêm tùy chọn</li>
  <li><b>Mục đích tài liệu:</b> chọn 1 hoặc nhiều lĩnh vực (CNTT, Pháp luật, Y tế...)</li>
  <li><b>Văn phong:</b> chọn kiểu dịch (Mặc định, Trang trọng, Ngắn gọn...)</li>
  <li><b>Chế độ dịch:</b> chọn engine (Offline, OpenAI, Claude...)</li>
</ol>

<h3>3. Cấu hình API Key</h3>
<ol>
  <li>Nhấn biểu tượng <b>cài đặt</b> (bánh răng) ở góc trên phải</li>
  <li>Nhập API key cho engine bạn muốn sử dụng</li>
  <li>Nhấn <b>Kiểm tra</b> để xác nhận key hợp lệ</li>
  <li>Nhấn <b>Lưu</b></li>
</ol>

<h3>4. Bảng thuật ngữ</h3>
<ol>
  <li>Nhấn <b>Bảng thuật ngữ</b> ở thanh dưới cùng</li>
  <li>Thêm thuật ngữ: chọn ngôn ngữ nguồn/đích, nhập thuật ngữ, nhấn <b>Thêm / Cập nhật</b></li>
  <li>Thuật ngữ được áp dụng 2 chiều tự động</li>
  <li>Hỗ trợ <b>Import/Export CSV</b> để chia sẻ</li>
</ol>

<h3>5. Định dạng hỗ trợ</h3>
<ul>
  <li>Excel (.xlsx, .xls)</li>
  <li>Word (.docx)</li>
  <li>PowerPoint (.pptx)</li>
  <li>Text (.txt)</li>
  <li>CSV (.csv)</li>
</ul>
""",
    "en": """
<h2>AI Translate User Guide</h2>

<h3>1. Basic Translation</h3>
<ol>
  <li>Click <b>Choose files</b> to select one or more files</li>
  <li>Select <b>Target language</b></li>
  <li>Click <b>Translate</b></li>
  <li>Wait for completion and review results</li>
</ol>

<h3>2. Advanced Options</h3>
<ol>
  <li>Click <b>Expand >></b> to show more options</li>
  <li><b>Document purpose:</b> select one or more domains</li>
  <li><b>Translation style:</b> choose style (Default, Formal, Concise...)</li>
  <li><b>Translation engine:</b> choose engine (Offline, OpenAI, Claude...)</li>
</ol>

<h3>3. API Key Configuration</h3>
<ol>
  <li>Click the <b>gear icon</b> in the top-right corner</li>
  <li>Enter API key for your chosen engine</li>
  <li>Click <b>Test</b> to verify</li>
  <li>Click <b>Save</b></li>
</ol>

<h3>4. Glossary</h3>
<ol>
  <li>Click <b>Glossary</b> at the bottom</li>
  <li>Add terms with source/target language and text</li>
  <li>Terms are automatically bidirectional</li>
  <li>Supports <b>CSV Import/Export</b></li>
</ol>

<h3>5. Supported Formats</h3>
<ul>
  <li>Excel (.xlsx, .xls)</li>
  <li>Word (.docx)</li>
  <li>PowerPoint (.pptx)</li>
  <li>Text (.txt)</li>
  <li>CSV (.csv)</li>
</ul>
""",
    "ja": """
<h2>AI Translate ユーザーガイド</h2>

<h3>1. 基本的な翻訳</h3>
<ol>
  <li><b>ファイル選択</b>をクリックしてファイルを選択</li>
  <li><b>対象言語</b>を選択</li>
  <li><b>翻訳</b>をクリック</li>
  <li>完了を待って結果を確認</li>
</ol>

<h3>2. 詳細オプション</h3>
<ol>
  <li><b>展開 >></b>をクリックして追加オプションを表示</li>
  <li><b>文書の目的:</b> 1つまたは複数の分野を選択</li>
  <li><b>翻訳スタイル:</b> スタイルを選択</li>
  <li><b>翻訳エンジン:</b> エンジンを選択</li>
</ol>

<h3>3. APIキーの設定</h3>
<ol>
  <li>右上の<b>歯車アイコン</b>をクリック</li>
  <li>選択したエンジンのAPIキーを入力</li>
  <li><b>テスト</b>をクリックして確認</li>
  <li><b>保存</b>をクリック</li>
</ol>

<h3>4. 用語集</h3>
<ol>
  <li>下部の<b>用語集</b>をクリック</li>
  <li>原文/対象の言語と用語を入力して追加</li>
  <li>用語は自動的に双方向で登録されます</li>
  <li><b>CSVインポート/エクスポート</b>対応</li>
</ol>

<h3>5. 対応フォーマット</h3>
<ul>
  <li>Excel (.xlsx, .xls)</li>
  <li>Word (.docx)</li>
  <li>PowerPoint (.pptx)</li>
  <li>Text (.txt)</li>
  <li>CSV (.csv)</li>
</ul>
""",
}


class GuideDialog(QDialog):
    """Dialog showing user guide content based on current language."""

    def __init__(self, i18n: I18nManager, parent=None):
        super().__init__(parent)
        self._i18n = i18n
        self._init_ui()

    def _init_ui(self):
        t = self._i18n.t
        self.setWindowTitle(t("guide_title"))
        self.setMinimumSize(500, 450)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)

        # HTML content viewer
        browser = QTextBrowser()
        browser.setOpenExternalLinks(False)
        lang = self._i18n.current_language
        browser.setHtml(_GUIDE_CONTENT.get(lang, _GUIDE_CONTENT["vi"]))
        layout.addWidget(browser, stretch=1)

        # Close button
        close_btn = QPushButton(t("glossary_close"))
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)
