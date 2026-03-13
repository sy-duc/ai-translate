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
<h2>Huong dan su dung AI Translate</h2>

<h3>1. Dich tai lieu co ban</h3>
<ol>
  <li>Nhan <b>Chon file</b> de chon 1 hoac nhieu file can dich</li>
  <li>Chon <b>Ngon ngu dich</b> (Tieng Viet, English, Japanese)</li>
  <li>Nhan <b>Dich</b></li>
  <li>Doi hoan tat, xem ket qua trong dialog thong bao</li>
</ol>

<h3>2. Tuy chon nang cao</h3>
<ol>
  <li>Nhan <b>Mo rong >></b> de hien thi them tuy chon</li>
  <li><b>Muc dich tai lieu:</b> chon 1 hoac nhieu linh vuc (CNTT, Phap luat, Y te...)</li>
  <li><b>Van phong:</b> chon kieu dich (Mac dinh, Trang trong, Ngan gon...)</li>
  <li><b>Che do dich:</b> chon engine (Offline, OpenAI, Claude...)</li>
</ol>

<h3>3. Cau hinh API Key</h3>
<ol>
  <li>Nhan bieu tuong <b>cai dat</b> (banh rang) o goc tren phai</li>
  <li>Nhap API key cho engine ban muon su dung</li>
  <li>Nhan <b>Kiem tra</b> de xac nhan key hop le</li>
  <li>Nhan <b>Luu</b></li>
</ol>

<h3>4. Bang thuat ngu</h3>
<ol>
  <li>Nhan <b>Bang thuat ngu</b> o thanh duoi cung</li>
  <li>Them thuat ngu: chon ngon ngu nguon/dich, nhap thuat ngu, nhan <b>Them / Cap nhat</b></li>
  <li>Thuat ngu duoc ap dung 2 chieu tu dong</li>
  <li>Ho tro <b>Import/Export CSV</b> de chia se</li>
</ol>

<h3>5. Dinh dang ho tro</h3>
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
