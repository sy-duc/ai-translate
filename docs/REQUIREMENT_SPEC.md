# AI Translate - Requirement Specification

> **Version:** 0.2 (Draft)
> **Last updated:** 2026-03-12
> **Status:** Thao luan

---

## 1. Tong quan san pham

**AI Translate** la cong cu dich tai lieu thong minh danh cho ca nhan, giao dien compact kieu UniKey. Cong cu ho tro dich nhieu dinh dang tai lieu pho bien voi kha nang **giu nguyen format goc**, dich theo **ngu canh/domain**, va cho phep nguoi dung tuy chon **translation engine** (AI hoac dich may truyen thong hoac offline).

### Dac diem chinh
- Giao dien nho gon kieu UniKey, khoi dong bang double-click nhu ung dung thuong
- Giu nguyen format tai lieu goc (chi dich text)
- Ho tro nhieu engine dich (OpenAI, Claude, Google Translate, DeepL, Gemini, Offline)
- Dich theo domain (muc dich tai lieu) va van phong
- Bang thuat ngu (glossary) 2 chieu, import/export CSV
- Dich ca ten file output va ten sheet
- Batch processing (chon nhieu file cung luc)

---

## 2. Tech Stack de xuat

| Thanh phan | Cong nghe | Ly do |
|---|---|---|
| **Backend / Core** | Python 3.11+ | He sinh thai xu ly tai lieu manh (openpyxl, python-docx, python-pptx...). De tich hop cac Translation API |
| **UI Framework** | PyQt6 / PySide6 | Nho gon, giao dien tuy bien cao, cross-platform (Windows, macOS, Linux) |
| **Packaging** | PyInstaller hoac Nuitka | Dong goi thanh 1 file `.exe` (Windows) hoac `.app` (macOS). Khong can cai Python. Khong ton chi phi van hanh |
| **Database (local)** | SQLite | Luu glossary, cau hinh. Khong can server |
| **Offline Translation** | Helsinki-NLP/MarianMT hoac Facebook NLLB-200 (qua HuggingFace) | Model dich pre-trained, chay local khong can train. Bundle size ~500MB-1GB |

### De xuat platform
- **Uu tien Windows** (chiem da so nguoi dung ca nhan Viet Nam)
- Kien truc cross-platform san (PyQt6), co the build cho macOS/Linux sau

---

## 3. Dinh dang tai lieu ho tro

| Format | Thu vien xu ly | Pham vi dich (v1) | Giu nguyen |
|---|---|---|---|
| **Excel** (.xlsx, .xls) | openpyxl / xlrd | Text trong cell, text trong shapes, ten sheet | Layout, merge cells, styles, formulas, conditional formatting, data validation, charts, images |
| **Word** (.docx) | python-docx | Text trong paragraphs, tables, headers/footers, text boxes | Font, style, layout, images, page setup |
| **PowerPoint** (.pptx) | python-pptx | Text trong slides, notes, shapes (text frames) | Layout, animations, images, master slides |
| **TXT** (.txt) | Built-in Python | Toan bo text | Encoding |
| **CSV** (.csv) | pandas / csv module | Text trong cac cell | Cau truc cot, delimiter |

### Ngoai pham vi v1
- PDF (tam thoi bo, xem xet o phien ban sau)
- OCR text trong anh nhung
- Dich text tren bieu do (chart labels)

---

## 4. Kien truc he thong

```
+--------------------------------------------------+
|              UI Layer (PyQt6)                     |
|  +--------------------------------------------+  |
|  | Main Window (UniKey-style compact window)   |  |
|  | - Dieu khien panel                          |  |
|  | - Mo rong panel (an/hien)                   |  |
|  +--------------------------------------------+  |
|  | Dialogs: Settings, Glossary, Info, Guide    |  |
|  +--------------------------------------------+  |
+--------------------------------------------------+
                        |
+--------------------------------------------------+
|              Translation Orchestrator             |
|  +-------------+  +----------+  +--------------+  |
|  | File Parser |  | Text     |  | File         |  |
|  | & Extractor |  | Translator|  | Reconstructor|  |
|  +-------------+  +----------+  +--------------+  |
+--------------------------------------------------+
                        |
+--------------------------------------------------+
|             Translation Engine Layer              |
|  (Common Interface / Adapter Pattern)             |
|  +--------+ +-------+ +--------+ +-------------+ |
|  | OpenAI | | Claude| | Google | | Offline      | |
|  | API    | | API   | | Trans. | | (MarianMT)   | |
|  +--------+ +-------+ +--------+ +-------------+ |
+--------------------------------------------------+
                        |
+--------------------------------------------------+
|               Local Data Layer (SQLite)           |
|  +-----------+  +----------------+                |
|  | Glossary  |  | User Settings  |                |
|  +-----------+  +----------------+                |
+--------------------------------------------------+
```

### 4.1. Translation Flow

```
Input File(s)
    |
    v
[Dich ten file] -- Dich ten file goc sang ngon ngu dich (dung lam ten file output)
    |
    v
[File Parser] -- Trich xuat text segments + metadata vi tri
    |            (bao gom ten sheet voi Excel)
    v
[Pre-process] -- Lookup glossary, xac dinh domain, smart chunking
    |            (toi uu token: loai bo text trung lap, gop batch thong minh)
    v
[Translation Engine] -- Gui text + context + domain prompt + style
    |                    (chi gui nhung gi can dich, khong gui thua)
    v
[Post-process] -- Ap dung glossary (replace), kiem tra consistency
    |
    v
[File Reconstructor] -- Ghep text dich vao dung vi tri trong file goc
    |
    v
Output File (giu nguyen format, ten file + ten sheet da dich)
```

---

## 5. Translation Engine - Thiet ke Common Interface

Moi engine implement cung mot interface de de dang thay the/them moi:

```python
class TranslationEngine(ABC):
    """Common interface cho tat ca translation engines."""

    @abstractmethod
    def translate(
        self,
        texts: list[str],
        source_lang: str,        # "auto" | "en" | "ja" | "vi" | ...
        target_lang: str,        # "vi" | "en" | "ja"
        domains: list[str],      # ["general"] | ["it_software", "finance"] | ...
        style: str,              # "default" | "formal" | ...
        glossary: dict[str, str], # {"API": "API", "deploy": "trien khai"}
        context: str | None,     # Ngu canh bo sung
    ) -> list[str]:
        """Dich mot batch text segments."""
        ...

    @abstractmethod
    def get_supported_languages(self) -> list[str]: ...

    @abstractmethod
    def validate_api_key(self, api_key: str) -> bool: ...

    @abstractmethod
    def get_name(self) -> str: ...

    @abstractmethod
    def estimate_tokens(self, texts: list[str]) -> int:
        """Uoc luong so token se su dung (de kiem soat chi phi)."""
        ...
```

### 5.1. Engines du kien

| Engine | Loai | Yeu cau | Ghi chu |
|---|---|---|---|
| **Offline (MarianMT/NLLB)** | Local | Tai model 1 lan | **Mac dinh.** Khong can internet, mien phi. Chat luong kha |
| **OpenAI (GPT)** | Cloud / AI | API Key | Dich ngu canh tot, ho tro domain prompt |
| **Anthropic (Claude)** | Cloud / AI | API Key | Manh ve reasoning, dich van ban dai chinh xac |
| **Google Translate** | Cloud / Traditional | API Key | Nhanh, ho tro nhieu ngon ngu |
| **DeepL** | Cloud / AI-hybrid | API Key | Chat luong cao cho EN-JA, EN-EU |
| **Gemini** | Cloud / AI | API Key | Free tier rong rai |

Nguoi dung chi can: **chon engine -> nhap API key (neu la cloud) -> dich**.

---

## 6. Giao dien chi tiet (UniKey-style)

### 6.1. Cua so chinh (Main Window) - Trang thai thu gon

Giao dien compact, co dinh kich thuoc (khong resize), giong UniKey.

```
+----------------------------------------------------------+
| [Icon] AI Translate                              [_][X]  |
+----------------------------------------------------------+
|  Dieu khien                                              |
| +--------------------------+  +------------------------+ |
| | Giao dien:  [Tieng Viet v] |  |  [ Chon file...     ] | |
| |                          |  |                        | |
| | File can dich:           |  |  [ Dich              ] | |
| |  report.xlsx             |  |                        | |
| |  contract.docx           |  |  [ Mo rong >>        ] | |
| |  data.csv                |  |                        | |
| |                          |  +------------------------+ |
| | Ngon ngu dich: [Tieng Viet v] |                        |
| +--------------------------+                             |
+----------------------------------------------------------+
|  [ Huong dan ]  [ Thong tin ]  [ Bang thuat ngu ]        |
+----------------------------------------------------------+
```

**Chi tiet thanh phan:**

| Thanh phan | Loai | Mo ta |
|---|---|---|
| **Giao dien** | Dropdown | Ngon ngu hien thi UI: Tieng Viet, English, Japanese |
| **File can dich** | Label + List | Hien thi ten file (chi ten, khong duong dan). Rong khi chua chon file |
| **Ngon ngu dich** | Dropdown | Tieng Viet, English, Japanese |
| **Chon file** | Button | Mo file dialog, cho chon nhieu file cung luc (multi-select). Khong ho tro keo tha |
| **Dich** | Button | Bat dau dich tat ca file trong danh sach. Hien progress dialog khi dang dich |
| **Mo rong >>** | Button | Toggle hien/an vung mo rong (xem 6.2) |
| **Huong dan** | Button | Mo dialog huong dan su dung |
| **Thong tin** | Button | Mo dialog thong tin phien ban, tac gia |
| **Bang thuat ngu** | Button | Mo dialog quan ly glossary (xem 6.5) |

### 6.2. Vung Mo rong (khi nhan "Mo rong >>")

Khi nhan "Mo rong >>", cua so duoc mo rong xuong duoi, day cac button "Huong dan", "Thong tin", "Bang thuat ngu" xuong phia duoi. Button doi thanh "<< Thu gon".

```
+----------------------------------------------------------+
| [Icon] AI Translate                              [_][X]  |
+----------------------------------------------------------+
|  Dieu khien                                              |
| +--------------------------+  +------------------------+ |
| | Giao dien:  [Tieng Viet v] |  |  [ Chon file...     ] | |
| |                          |  |                        | |
| | File can dich:           |  |  [ Dich              ] | |
| |  report.xlsx             |  |                        | |
| |  contract.docx           |  |  [ << Thu gon        ] | |
| |  data.csv                |  |                        | |
| |                          |  +------------------------+ |
| | Ngon ngu dich: [Tieng Viet v] |                        |
| +--------------------------+                             |
+----------------------------------------------------------+
|  Tuy chon nang cao                                       |
| +------------------------------------------------------+ |
| | Muc dich tai lieu:                                   | |
| |  [x] Khac   [ ] CNTT/Phan mem   [ ] Phap luat       | |
| |  [ ] Y te   [ ] Tai chinh/Ke toan                    | |
| |  [ ] Ky thuat/San xuat  [ ] Marketing                | |
| |  [ ] Hoc thuat/Nghien cuu                            | |
| +------------------------------------------------------+ |
| | Van phong:                                           | |
| |  (o) Mac dinh  ( ) Trang trong  ( ) Ngan gon        | |
| |  ( ) Sang tao  ( ) Ky thuat/Chinh xac               | |
| +------------------------------------------------------+ |
| | Che do dich:                                         | |
| |  (o) Mac dinh (Offline)  ( ) OpenAI  ( ) Claude     | |
| |  ( ) Google Translate    ( ) DeepL   ( ) Gemini     | |
| +------------------------------------------------------+ |
+----------------------------------------------------------+
|  [ Huong dan ]  [ Thong tin ]  [ Bang thuat ngu ]        |
+----------------------------------------------------------+
```

**Chi tiet vung mo rong:**

| Thanh phan | Loai | Mo ta |
|---|---|---|
| **Muc dich tai lieu** | Checkbox group (chon nhieu) | Mac dinh checked "Khac". Chon 1 hoac nhieu muc dich. Anh huong den domain prompt gui cho AI engine |
| **Van phong** | Radio group (chon 1) | Mac dinh "Mac dinh". Chi ap dung khi dung AI engine |
| **Che do dich** | Radio group (chon 1) | Mac dinh "Mac dinh (Offline)". Khi chon engine cloud, can co API key da cau hinh trong Settings |

### 6.3. Button Settings (Cau hinh)

Them button Settings (bieu tuong banh rang) o goc tren phai cua so, canh nut minimize/close.

```
| [Icon] AI Translate                        [S] [_][X]  |
```

**Settings Dialog** gom:
- **API Keys:** Nhap API key cho tung engine (OpenAI, Claude, Google, DeepL, Gemini). Moi engine co 1 text field + nut "Kiem tra" de validate key
- **Thu muc output:** Chon thu muc luu file dich. Mac dinh: cung thu muc voi file goc
- **Offline model:** Trang thai model (da tai / chua tai), nut tai model

### 6.4. Dich tai lieu (Document Translation)

| Tinh nang | Mo ta |
|---|---|
| **Batch processing** | Chon nhieu file cung luc qua file dialog |
| **Giu format goc** | File output co cung format va layout voi file input |
| **Dich ten file** | Ten file output duoc dich sang ngon ngu dich (vi du: `report.xlsx` -> `bao_cao.xlsx`) |
| **Dich ten sheet** | Ten cac sheet trong Excel cung duoc dich |
| **Auto-detect language** | Tu nhan dien ngon ngu nguon (dua vao engine hoac langdetect) |
| **Smart chunking** | Chia text thong minh de khong vuot token limit cua API, dong thoi giu ngu canh |
| **Token optimization** | Loai bo text trung lap, gop cac doan ngan, chi gui text can dich (khong gui formula, so thuan...) |
| **Progress tracking** | Hien thi progress dialog khi dang dich |
| **Dialog ket qua** | Khi hoan thanh: hien dialog thong bao danh sach file thanh cong va file loi (neu co) |
| **Error handling** | Neu 1 file loi, tiep tuc dich cac file con lai |

#### 6.4.1. Token Optimization (Kiem soat chi phi)

Day la van de quan trong khi dung Cloud AI engine. Cac chien luoc:

| Chien luoc | Mo ta |
|---|---|
| **Loc text khong can dich** | Bo qua cell chi chua so, formula, date, URL, email. Chi dich cell co text tu nhien |
| **Gop batch** | Gop nhieu doan text ngan thanh 1 request (tiet kiem overhead token cua system prompt) |
| **Loai trung lap** | Neu nhieu cell co cung noi dung, chi dich 1 lan roi ap dung cho tat ca |
| **Glossary pre-replace** | Thay the thuat ngu truoc khi gui API, giam token prompt glossary |
| **Cache ket qua** | Luu cache ket qua dich theo hash(text + engine + domain + style). Lan sau gap lai thi dung cache |
| **Gioi han glossary trong prompt** | Chi gui nhung thuat ngu xuat hien trong batch hien tai, khong gui toan bo glossary |

### 6.5. Bang thuat ngu (Glossary)

Khi nhan nut "Bang thuat ngu", mo dialog:

```
+----------------------------------------------------------+
| Bang thuat ngu                                    [X]    |
+----------------------------------------------------------+
| Ngon ngu nguon: [English    v]  Thuat ngu nguon: [_____] |
| Ngon ngu dich:  [Tieng Viet v]  Thuat ngu dich:  [_____] |
|                                                          |
|            [ Them / Cap nhat ]                           |
+----------------------------------------------------------+
| Tim kiem: [______________]                               |
| +------+----------+----------+----------+--------------+ |
| |  #   | Nguon    | Ngon ngu | Dich     | Ngon ngu     | |
| +------+----------+----------+----------+--------------+ |
| |  1   | deploy   | EN       | trien khai| VI          | |
| |  2   | bug      | EN       | loi       | VI          | |
| |  3   | server   | EN       | may chu   | VI          | |
| |  ...                                                 | |
| +------------------------------------------------------+ |
+----------------------------------------------------------+
| [ Import CSV ]  [ Export CSV ]              [ Dong ]     |
+----------------------------------------------------------+
```

**Chi tiet:**

| Tinh nang | Mo ta |
|---|---|
| **Them thu cong** | Chon ngon ngu nguon (dropdown), nhap thuat ngu nguon, chon ngon ngu dich (dropdown), nhap thuat ngu dich. Nhan "Them / Cap nhat" |
| **Ghi de** | Neu cap (thuat ngu nguon + ngon ngu nguon + ngon ngu dich) da ton tai -> ghi de thuat ngu dich |
| **2 chieu** | Khi them EN "deploy" -> VI "trien khai", tu dong tao luon VI "trien khai" -> EN "deploy". Khi dich EN->VI hoac VI->EN deu mapping duoc |
| **Import CSV** | File CSV 4 cot: `source_term, source_lang, target_term, target_lang`. Ghi de neu trung |
| **Export CSV** | Xuat toan bo glossary ra CSV de chia se |
| **Tim kiem** | Loc bang thuat ngu theo keyword |
| **Xoa** | Chon dong trong bang, nhan Delete hoac right-click -> Xoa |
| **Sua** | Double-click vao dong trong bang de sua truc tiep |

#### Cau truc du lieu Glossary (SQLite)

```sql
CREATE TABLE glossary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_term TEXT NOT NULL,
    source_lang TEXT NOT NULL,  -- 'en', 'vi', 'ja'
    target_term TEXT NOT NULL,
    target_lang TEXT NOT NULL,  -- 'en', 'vi', 'ja'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_term, source_lang, target_lang)
);
```

Khi them 1 entry (A, lang1) -> (B, lang2), tu dong them entry nguoc (B, lang2) -> (A, lang1).

### 6.6. Dich theo Muc dich tai lieu (Domain-Aware Translation)

Cac domain (checkbox, chon nhieu):

| Domain | Label hien thi | Mo ta |
|---|---|---|
| **other** | Khac (mac dinh) | Van ban thong thuong, khong chuyen nganh |
| **it_software** | CNTT/Phan mem | Cong nghe thong tin, lap trinh, phan mem |
| **legal** | Phap luat | Phap luat, hop dong, quy dinh |
| **medical** | Y te | Y te, duoc pham, y hoc |
| **finance** | Tai chinh/Ke toan | Tai chinh, ke toan, ngan hang |
| **engineering** | Ky thuat/San xuat | Ky thuat, co khi, san xuat |
| **marketing** | Marketing | Quang cao, truyen thong, ban hang |
| **academic** | Hoc thuat/Nghien cuu | Hoc thuat, luan van, nghien cuu |

Cach hoat dong:
- Moi domain co **system prompt** rieng gui kem khi goi AI engine
- Chon nhieu domain: gop cac prompt instruction tuong ung
- Voi engine Offline/Google Translate: domain khong ap dung (chi dich thuan tuy)

### 6.7. Van phong dich (Translation Style)

Radio group (chon 1):

| Style | Label hien thi | Mo ta |
|---|---|---|
| **default** | Mac dinh | Trung tinh, tu nhien |
| **formal** | Trang trong / Bao cao | Lich su, formal, cau day du |
| **concise** | Ngan gon / Suc tich | Co dong, bo tu thua |
| **creative** | Sang tao / Bay bong | Linh hoat, tu nhien, giau hinh anh |
| **technical** | Ky thuat / Chinh xac | Sat nghia, khong dien giai |

Cach hoat dong:
- Moi style la mot doan instruction bo sung vao prompt gui cho AI engine
- Voi engine Offline/Google Translate: style khong ap dung

---

## 7. Ten file output

Ten file output se duoc **dich sang ngon ngu dich**.

| Input | Target lang | Output |
|---|---|---|
| `report.xlsx` | VI | `bao_cao.xlsx` |
| `contract.docx` | VI | `hop_dong.docx` |
| `report.xlsx` | JA | `repoto.xlsx` (hoac giu nguyen neu khong dich duoc) |
| `bao_cao.xlsx` | EN | `report.xlsx` |

Quy tac:
- Dich ten file (khong bao gom extension) qua cung engine dang dung
- Neu ten file da o ngon ngu dich -> giu nguyen
- Neu dich that bai -> fallback: `{ten_goc}_{target_lang}.{ext}` (vi du: `report_vi.xlsx`)
- Neu file output trung ten -> them hau to `_1`, `_2`...
- Ten sheet trong Excel cung duoc dich tuong tu

---

## 8. Cau truc thu muc du an (de xuat)

```
ai-translate/
|-- src/
|   |-- main.py                  # Entry point
|   |-- app.py                   # QApplication setup
|   |-- ui/
|   |   |-- main_window.py       # Cua so chinh (UniKey-style)
|   |   |-- expand_panel.py      # Vung mo rong (domain, style, engine)
|   |   |-- settings_dialog.py   # Dialog cau hinh API keys
|   |   |-- glossary_dialog.py   # Dialog quan ly glossary
|   |   |-- progress_dialog.py   # Dialog progress khi dich
|   |   |-- result_dialog.py     # Dialog ket qua (thanh cong/loi)
|   |   |-- info_dialog.py       # Dialog thong tin
|   |   |-- guide_dialog.py      # Dialog huong dan
|   |   +-- widgets/             # Custom widgets
|   |-- core/
|   |   |-- orchestrator.py      # Dieu phoi toan bo flow dich
|   |   |-- chunker.py           # Smart text chunking + token optimization
|   |   |-- language_detect.py   # Auto-detect ngon ngu
|   |   +-- cache.py             # Translation cache (tiet kiem token)
|   |-- parsers/
|   |   |-- base.py              # Abstract parser interface
|   |   |-- excel_parser.py      # Excel (.xlsx/.xls)
|   |   |-- word_parser.py       # Word (.docx)
|   |   |-- pptx_parser.py       # PowerPoint (.pptx)
|   |   |-- txt_parser.py        # Plain text
|   |   +-- csv_parser.py        # CSV
|   |-- engines/
|   |   |-- base.py              # TranslationEngine ABC
|   |   |-- openai_engine.py     # OpenAI GPT
|   |   |-- claude_engine.py     # Anthropic Claude
|   |   |-- google_engine.py     # Google Translate
|   |   |-- deepl_engine.py      # DeepL
|   |   |-- gemini_engine.py     # Google Gemini
|   |   +-- offline_engine.py    # MarianMT / NLLB (local)
|   |-- data/
|   |   |-- db.py                # SQLite connection & migrations
|   |   |-- glossary_repo.py     # Glossary CRUD
|   |   +-- settings_repo.py     # User settings CRUD
|   +-- prompts/
|       |-- domains/             # Domain-specific system prompts
|       |   |-- other.txt
|       |   |-- it_software.txt
|       |   |-- legal.txt
|       |   |-- medical.txt
|       |   |-- finance.txt
|       |   |-- engineering.txt
|       |   |-- marketing.txt
|       |   +-- academic.txt
|       +-- styles/              # Style instructions
|           |-- default.txt
|           |-- formal.txt
|           |-- concise.txt
|           |-- creative.txt
|           +-- technical.txt
|-- resources/
|   |-- icons/                   # App icons
|   +-- i18n/                    # UI i18n (vi.json, en.json, ja.json)
|-- tests/
|-- docs/
|   +-- REQUIREMENT_SPEC.md      # File nay
|-- pyproject.toml
+-- README.md
```

---

## 9. Luong su dung chinh (User Flow)

### 9.1. Lan dau su dung
1. Cai dat (chay installer hoac extract portable)
2. Double-click mo app
3. (Tuy chon) Nhan Settings -> nhap API key cho engine muon dung
4. Mac dinh dung Offline engine, san sang dich ngay

### 9.2. Dich tai lieu (flow co ban)
1. Double-click mo app
2. Nhan "Chon file" -> chon 1 hoac nhieu file
3. Danh sach file hien thi trong "File can dich"
4. Chon "Ngon ngu dich"
5. Nhan "Dich"
6. Hien progress dialog
7. Hoan tat -> hien dialog ket qua:
   - Danh sach file dich thanh cong (ten file output, duong dan)
   - Danh sach file loi (ten file, ly do loi)
   - Nut "Mo thu muc output"

### 9.3. Dich tai lieu (flow nang cao)
1. Mo app, chon file, chon ngon ngu dich
2. Nhan "Mo rong >>"
3. Chon muc dich tai lieu (vi du: tick "CNTT/Phan mem" + "Tai chinh/Ke toan")
4. Chon van phong (vi du: "Trang trong / Bao cao")
5. Chon che do dich (vi du: "OpenAI")
6. Nhan "Dich"

### 9.4. Quan ly Glossary
1. Nhan "Bang thuat ngu"
2. Them thu cong: chon ngon ngu nguon/dich, nhap thuat ngu, nhan "Them / Cap nhat"
3. Import: nhan "Import CSV", chon file
4. Export: nhan "Export CSV"
5. Glossary tu dong ap dung khi dich

---

## 10. Ve Offline Translation

**Khong can train model.** Co cac model dich pre-trained san:

| Model | Kich thuoc | Chat luong | Ngon ngu |
|---|---|---|---|
| **Helsinki-NLP/MarianMT** | ~300MB moi cap ngon ngu | Kha (tuong duong Google Translate 2020) | Tung cap rieng: en-vi, en-ja, ja-vi... |
| **Facebook NLLB-200** (distilled) | ~600MB - 1.3GB | Tot hon MarianMT | 200 ngon ngu trong 1 model |

Cach hoat dong:
- Lan dau chon offline engine -> app tai model ve local (~5-10 phut)
- Sau do chay hoan toan offline, khong can internet
- Dung CPU (cham hon) hoac GPU neu co (nhanh hon)

**Trade-off so voi Cloud AI:**
- Uu: Mien phi, khong can internet, bao mat du lieu
- Nhuoc: Chat luong thap hon AI cloud (nhat la dich ngu canh), **khong ho tro domain prompt va style**

---

## 11. Cac van de can thao luan them

| # | Van de | Ghi chu |
|---|---|---|
| 1 | **Estimated cost** | Co muon hien thi uoc tinh chi phi API truoc khi dich? (huu ich de tranh bat ngo) |
| 2 | **Cache/Resume** | Neu dich file lon bi gian doan (mat mang, crash), co can resume tu cho do? |
| 3 | **Translation memory** | Ngoai glossary, co can luu lai cac cau da dich de reuse (giong CAT tool)? Giup tiet kiem API cost |
| 4 | **Auto-update** | Can co che auto-update cho app khong? |
| 5 | **Giay phep phan phoi** | Du kien phan phoi mien phi hay co ban tra phi? Anh huong den license cac thu vien su dung |
| 6 | **Xoa file khoi danh sach** | Co nut xoa tung file hoac xoa tat ca khoi danh sach "File can dich"? |
| 7 | **Thu muc output** | Mac dinh cung thu muc voi file goc? Hay cho chon rieng trong Settings? |
| 8 | **Gioi han file** | Co gioi han so file chon cung luc hoac kich thuoc file khong? |
| 9 | **Ho tro .xls (Excel cu)** | xlrd doc duoc .xls nhung khong ghi lai duoc .xls. Co can ho tro hay chi .xlsx? |

---

## 12. Phan pha phat trien (de xuat)

### Phase 1 - MVP
- Main window UniKey-style (co ban, chua co Mo rong)
- Ho tro Excel (.xlsx) - cell text + shapes text + ten sheet
- Dich ten file output
- 1 engine: Offline (MarianMT/NLLB)
- Glossary co ban (them/sua/xoa thu cong, import/export CSV, 2 chieu)
- 3 ngon ngu dich: VI, EN, JA
- Dialog ket qua dich
- Settings: thu muc output

### Phase 2 - Engine & Mo rong
- Them engines cloud: OpenAI, Claude, Google Translate, DeepL, Gemini
- Settings: cau hinh API keys
- Vung "Mo rong" (domain checkboxes, style radio, engine radio)
- Token optimization (loc, gop, cache)
- I18n giao dien (VI, EN, JA)

### Phase 3 - Multi-format
- Them Word (.docx), PowerPoint (.pptx), TXT, CSV
- Batch processing toi uu
- Dialog Huong dan, Thong tin

### Phase 4 - Polish
- Translation memory / cache nang cao
- Estimated cost display
- Resume interrupted translation
- Auto-update
- PDF support (xem xet)

---

## Phu luc A: Vi du prompt cho AI Engine

```
System prompt (domains = [IT/Software, Finance], style = Formal, target = VI):
---
Ban la chuyen gia dich thuat linh vuc Cong nghe thong tin va Tai chinh.
Hay dich cac doan text sau sang Tieng Viet.

Quy tac:
- Van phong: trang trong, phu hop bao cao ky thuat va tai chinh
- Giu nguyen cac thuat ngu ky thuat pho bien khong can dich: API, SDK, HTTP, URL, JSON...
- Su dung dung thuat ngu chuyen nganh IT va Tai chinh tieng Viet
- Bat buoc tuan thu bang thuat ngu duoi day:

Glossary (chi nhung thuat ngu xuat hien trong batch nay):
- "deploy" -> "trien khai"
- "repository" -> "kho luu tru"
- "revenue" -> "doanh thu"

Tra ve ket qua dich theo dung thu tu, moi doan cach nhau bang dau "---".
---
```

## Phu luc B: Format file CSV Glossary (Import/Export)

```csv
source_term,source_lang,target_term,target_lang
deploy,en,trien khai,vi
bug,en,loi,vi
server,en,may chu,vi
revenue,en,doanh thu,vi
```

Khi import:
- Dong dau tien la header (bo qua)
- Moi dong tao 1 entry + 1 entry nguoc (2 chieu)
- Neu trung (source_term + source_lang + target_lang) -> ghi de
