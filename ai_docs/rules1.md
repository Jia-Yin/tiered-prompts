# AI Prompt Engineering Rules - 從模組化重構經驗萃取

本文檔記錄從 AI Prompt Engineering System 開發過程中萃取的規則，特別是資料庫模組化重構的經驗。這些規則遵循三層架構：Primitive → Semantic → Task。

---

## Primitive Rules (基礎構建塊)

### P1: 檔案結構驗證
**Type**: constraint
**Content**: 在進行任何檔案操作前，必須先使用 `list_dir` 驗證當前目錄結構，確保對專案架構有正確理解。

### P2: 讀取前確認
**Type**: constraint
**Content**: 編輯檔案前必須使用 `read_file` 讀取完整內容，確保了解現有程式碼結構和依賴關係。

### P3: 模組化路徑原則
**Type**: pattern
**Content**: 使用相對導入 (`from .database import`) 而非絕對導入，保持模組間的清晰界限。

### P4: 批次操作優先
**Type**: instruction
**Content**: 對同一檔案的多個修改應該在單次工具調用中完成，避免頻繁的檔案讀寫操作。

### P5: 錯誤處理檢查
**Type**: constraint
**Content**: 每次檔案編輯後，必須檢查 `get_errors` 確保沒有語法錯誤或導入問題。

### P6: 測試驗證循環
**Type**: pattern
**Content**: 重構後立即運行相關測試，確保功能正常運作：`run_in_terminal` → 測試命令 → 驗證結果。

### P7: 依賴搜尋完整性
**Type**: constraint
**Content**: 使用 `grep_search` 系統性搜尋所有導入語句和檔案引用，確保沒有遺漏任何需要更新的依賴關係。

### P8: 步驟間驗證
**Type**: pattern
**Content**: 每完成一個重構步驟就立即驗證：移動檔案 → 檢查語法 → 運行測試 → 確認功能，避免累積錯誤。

---

## Semantic Rules (語義模板規則)

### S1: 模組化重構流程
**Type**: workflow
**Dependencies**: P1, P2, P3, P5, P7, P8
**Content**:
1. 分析現有結構 (P1, P2)
2. 搜尋所有相關依賴 (P7)
3. 創建新模組目錄結構
4. 移動相關檔案到新模組
5. 更新所有導入語句 (P3)
6. 創建 `__init__.py` 檔案暴露必要 API
7. 步驟間驗證 (P8) - 檢查語法和運行基本測試
8. 運行完整測試確保功能完整 (P6)

### S2: 導入路徑重構策略
**Type**: refactoring
**Dependencies**: P2, P3, P5, P7
**Content**:
- 使用 `grep_search` 識別所有受影響的導入語句 (P7)
- 使用相對導入維持模組封裝
- 在 `__init__.py` 中暴露公共 API
- 批次更新所有引用檔案的導入路徑 (P4)
- 驗證導入鏈的完整性 (P5)

### S3: 清理和優化規範
**Type**: maintenance
**Dependencies**: P1, P6
**Content**:
- 移除不再需要的檔案和目錄
- 清理 `__pycache__` 和臨時檔案
- 更新相關文檔反映新結構
- 確保 `.gitignore` 涵蓋所有臨時檔案

### S4: 文檔同步更新流程
**Type**: documentation
**Dependencies**: P1, P2
**Content**:
- 識別所有需要更新的文檔檔案
- 更新檔案路徑引用
- 更新架構圖和範例程式碼
- 添加重構成就到項目里程碑
- 確保文檔與實際結構一致

---

## Task Rules (特定任務實現)

### T1: Python 專案資料庫模組重構
**Domain**: Python Development
**Technology**: SQLite, Python Modules
**Dependencies**: S1, S2, S3
**Context**: 將單體架構重構為模組化架構
**Content**:
```
目標: 將資料庫相關功能重構到獨立模組
步驟:
1. 創建 src/database/ 目錄結構
2. 移動檔案: connection.py, crud.py, migrations.py, validation.py, seed_data.py, schema.sql
3. 創建 src/database/__init__.py 暴露核心 API
4. 更新 src/__init__.py 中的導入語句
5. 更新 main.py 中的導入路徑
6. 移除舊的 src/engine/ 和 src/utils/ 模組
7. 清理所有 __pycache__ 目錄
8. 運行 CLI 測試: init, status, data create
9. 運行完整測試套件驗證功能
10. 更新文檔反映新架構
```

### T2: CLI 系統模組化適配
**Domain**: Command Line Interface
**Technology**: Python argparse, Click
**Dependencies**: S1, S2
**Context**: 確保 CLI 在模組重構後正常運作
**Content**:
```
目標: 適配 CLI 系統到新模組結構
關鍵點:
- 更新所有 from src.* 導入為模組化路徑
- 確保 main.py 能正確訪問重構後的功能
- 測試所有 CLI 命令的正常運作
- 維持向後兼容的 API 接口
驗證: python main.py init, status, validate, data create
```

### T3: 測試系統重構適配
**Domain**: Testing
**Technology**: Python unittest, pytest
**Dependencies**: S1, S2, P6
**Context**: 確保測試在模組重構後繼續有效
**Content**:
```
目標: 適配測試系統到新模組結構
步驟:
1. 更新測試檔案中的導入語句
2. 確保測試能訪問重構後的模組
3. 移除對已刪除模組的測試引用
4. 驗證所有測試通過
5. 確保測試覆蓋率維持在原有水平
執行: python -m pytest tests/ -v
```

### T4: 項目文檔架構更新
**Domain**: Documentation
**Technology**: Markdown
**Dependencies**: S4
**Context**: 更新項目文檔反映模組化重構
**Content**:
```
目標: 同步更新所有項目文檔
文檔類型:
- plan.md: 更新檔案路徑、架構圖、成就列表
- phase1.md: 更新模組描述、API 範例、檔案結構
- README.md: 更新安裝和使用說明
更新要點:
- 所有檔案路徑引用 (src/database/*)
- 架構圖和模組關係
- 導入語句範例
- 新增模組化重構為重要成就
```

---

## Meta Rules (應用指南)

### 使用這些規則的最佳實踐

1. **按層次應用**: 先確保 Primitive Rules，再應用 Semantic Rules，最後執行 Task Rules
2. **驗證循環**: 每個階段都要進行驗證，確保沒有破壞現有功能
3. **文檔同步**: 代碼變更和文檔更新應該同時進行
4. **測試驅動**: 始終以測試通過作為重構成功的標準

### 適用場景

這些規則特別適用於：
- Python 專案模組化重構
- 資料庫層抽象和封裝
- CLI 工具重構和適配
- 大型專案檔案結構重組
- 開發流程文檔維護

### 避免的陷阱

- 在不了解現有結構的情況下直接修改檔案
- 忘記更新所有相關的導入語句
- 重構後不進行充分的測試驗證
- 代碼重構完成但忘記同步更新文檔
- 清理工作不徹底留下過時檔案
- **不使用系統性搜尋工具找出所有依賴** ← 主要繞遠路原因
- **沒有在每個步驟後立即驗證** ← 累積錯誤導致難以定位問題
- **頻繁小範圍編輯而非批次操作** ← 效率低且容易出錯

## 繞遠路分析與預防

### 模組化重構中的常見繞遠路

基於實際經驗，以下是導致繞遠路的主要原因及預防措施：

#### 問題1: 導入依賴分析不完整
**症狀**: 移動檔案後發現還有很多地方需要更新導入路徑
**原因**: 沒有使用 `grep_search` 系統性搜尋所有導入語句
**預防**: 應用 P7 - 使用 `grep_search "from src\." --isRegexp=true` 找出所有相關導入

#### 問題2: 累積錯誤難以定位
**症狀**: 修改多個檔案後測試失敗，但不知道哪個步驟出錯
**原因**: 沒有在每個步驟後立即驗證
**預防**: 應用 P8 - 每完成一個操作就檢查語法和運行基本測試

#### 問題3: 工具使用效率低
**症狀**: 需要多次編輯同一檔案，頻繁讀寫
**原因**: 沒有預先分析所有需要修改的地方
**預防**: 應用 P4 + P7 - 先搜尋所有相關位置，然後批次修改

### 規則覆蓋度分析

現有規則已能有效預防這些繞遠路：
- ✅ **P7**: 強制使用搜尋工具找出所有依賴
- ✅ **P8**: 強制步驟間驗證
- ✅ **P4**: 強制批次操作
- ✅ **S1**: 將這些原則整合到標準流程中
- ✅ **S2**: 明確要求使用搜尋工具識別依賴

---

*本規則集基於 2025年7月3日 AI Prompt Engineering System 資料庫模組化重構的實際經驗萃取而成。*
