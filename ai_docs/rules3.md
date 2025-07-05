# AI Prompt Engineering Rules - 從 Phase 3 MCP 服務器開發經驗萃取

本文檔記錄從 AI Prompt Engineering System Phase 3 開發過程中萃取的規則，特別是 MCP 服務器架構設計、生產級系統實現和虛擬環境管理的經驗。這些規則遵循三層架構：Primitive → Semantic → Task。

---

## Primitive Rules (基礎構建塊)

### P17: 虛擬環境強制使用
**Type**: constraint
**Content**: 所有 Python 腳本執行、測試運行和包安裝都必須在激活的虛擬環境中進行。執行前必須確認 `python --version` 和 `which python` 指向虛擬環境路徑。

### P18: 依賴版本固定
**Type**: constraint
**Content**: 所有外部依賴必須在 requirements.txt 中固定具體版本號，避免隱式依賴和版本衝突。

### P19: 配置外部化
**Type**: pattern
**Content**: 所有配置參數必須外部化到配置文件或環境變量，支援多環境部署和運行時配置調整。

### P20: 監控埋點標準
**Type**: pattern
**Content**: 所有關鍵操作必須埋點監控，記錄請求計數、響應時間、錯誤率等指標，支援生產環境問題診斷。

### P21: 優雅降級機制
**Type**: constraint
**Content**: 系統必須支援關鍵依賴不可用時的優雅降級，提供基本功能而不是完全失敗。

### P22: 健康檢查完整性
**Type**: constraint
**Content**: 服務必須提供全面的健康檢查，涵蓋所有關鍵組件和依賴項，支援自動化監控和運維。

### P23: 日誌結構化
**Type**: pattern
**Content**: 所有日誌必須使用結構化格式，包含時間戳、級別、組件、操作、參數等信息，便於分析和問題排查。

### P24: API 協議標準化
**Type**: constraint
**Content**: 對外 API 必須遵循標準協議（如 MCP），確保與不同客戶端的相容性和互操作性。

---

## Semantic Rules (語義模板規則)

### S9: MCP 服務器架構模式
**Type**: architecture
**Dependencies**: P17, P18, P19, P20, P21, P22, P23, P24
**Content**:
1. 使用官方 MCP SDK 確保協議相容性 (P24)
2. 實現工具 (Tools)、資源 (Resources)、提示 (Prompts) 三類功能
3. 設計統一的應用上下文和依賴注入 (P21)
4. 集成結構化日誌和監控系統 (P20, P23)
5. 支援多環境配置和部署 (P19)
6. 提供完整的健康檢查功能 (P22)
7. 在虛擬環境中開發和測試 (P17)

### S10: 生產級系統實現策略
**Type**: production_readiness
**Dependencies**: P19, P20, P21, P22, P23
**Content**:
- 實現請求/響應的完整日誌記錄 (P23)
- 建立性能監控和指標收集 (P20)
- 設計多層配置管理系統 (P19)
- 實現服務健康檢查和自監控 (P22)
- 提供優雅啟動和關閉機制 (P21)
- 支援容器化和自動化部署

### S11: 虛擬環境管理規範
**Type**: environment_management
**Dependencies**: P17, P18
**Content**:
- 項目根目錄統一創建 .venv 虛擬環境
- 所有開發和測試活動都在虛擬環境中進行
- 使用 requirements.txt 管理依賴版本 (P18)
- 提供環境設置和驗證腳本
- 文檔中明確虛擬環境激活步驟

### S12: API 工具設計模式
**Type**: api_design
**Dependencies**: P20, P21, P24
**Content**:
- 設計直觀的工具名稱和參數結構
- 統一的響應格式和錯誤處理
- 支援參數驗證和自動補全
- 提供詳細的工具文檔和示例
- 實現工具級別的監控和統計 (P20)

---

## Task Rules (特定任務實現)

### T6: MCP 服務器完整實現
**Domain**: MCP Server Development
**Technology**: Python, FastMCP, MCP SDK
**Dependencies**: S9, S10, S11, S12
**Context**: 實現基於 MCP 協議的 AI 服務器
**Content**:
```
目標: 建立生產就緒的 MCP 服務器系統
核心組件:
1. FastMCP 服務器框架集成
2. 5個核心工具: generate_prompt, analyze_rules, validate_rules, search_rules, optimize_rules
3. 3個資源類型: rules hierarchy, performance stats, rule relationships
4. 監控和日誌系統
5. 配置管理和健康檢查
實現要點:
- 使用官方 MCP Python SDK v1.10.1+
- 在 .venv 虛擬環境中開發和測試
- 實現統一的應用上下文和依賴注入
- 集成性能監控和結構化日誌
- 支援 Mock 模式用於開發階段
測試方法:
- 虛擬環境激活: source .venv/bin/activate
- 服務器啟動: python mcp_server/fastmcp_server.py
- 功能測試: python test_mcp_server.py
- 健康檢查: python health_check.py
```

### T7: 生產環境監控系統
**Domain**: Production Monitoring
**Technology**: Python, Logging, Metrics
**Dependencies**: S10, S12
**Context**: 實現完整的生產監控和運維系統
**Content**:
```
目標: 建立完整的生產監控和運維體系
核心功能:
1. 請求/響應日誌記錄
2. 性能指標收集和統計
3. 錯誤追蹤和分析
4. 健康狀態監控
5. 配置管理和熱更新
實現要點:
- 使用裝飾器自動化監控集成
- 結構化日誌格式便於分析
- 支援多環境配置管理
- 提供健康檢查 API 端點
- 實現優雅的服務啟動和關閉
部署配置:
- 環境變量配置管理
- 容器化部署支援
- 自動化部署腳本
- 監控指標採集
```

### T8: 虛擬環境標準化管理
**Domain**: Python Environment Management
**Technology**: Python venv, pip, requirements.txt
**Dependencies**: S11
**Context**: 建立標準化的 Python 虛擬環境管理流程
**Content**:
```
目標: 確保所有開發和生產環境的一致性
標準流程:
1. 項目根目錄創建虛擬環境: python -m venv .venv
2. 激活虛擬環境: source .venv/bin/activate
3. 安裝依賴: pip install -r requirements.txt
4. 驗證環境: python --version && which python
5. 運行測試: python -m pytest
關鍵規則:
- 絕對不在系統 Python 中運行項目代碼
- 所有腳本執行前必須確認虛擬環境激活
- 依賴版本固定在 requirements.txt
- 提供環境設置和驗證腳本
- 文檔中明確環境設置步驟
常見問題解決:
- 虛擬環境路徑問題: 使用絕對路徑或確認工作目錄
- 依賴版本衝突: 重新創建虛擬環境
- 測試環境不一致: 使用 requirements.txt 統一依賴
```

---

## 實施指南

### 規則應用優先級

#### 高優先級 (必須遵守)
- **P17**: 虛擬環境強制使用 - 所有 Python 操作的基礎
- **P22**: 健康檢查完整性 - 生產環境穩定性保障
- **P24**: API 協議標準化 - 系統互操作性基礎

#### 中優先級 (強烈建議)
- **P19**: 配置外部化 - 支援多環境部署
- **P20**: 監控埋點標準 - 生產問題診斷
- **P21**: 優雅降級機制 - 系統可用性保障

#### 低優先級 (建議採用)
- **P18**: 依賴版本固定 - 環境一致性
- **P23**: 日誌結構化 - 問題排查效率

### 規則驗證清單

在實施任何 MCP 服務器或生產系統開發時，請確認：

- [ ] 虛擬環境已激活且 Python 路徑正確
- [ ] 所有依賴已在 requirements.txt 中固定版本
- [ ] 配置文件支援多環境和環境變量覆蓋
- [ ] 關鍵操作已埋點監控
- [ ] 實現了優雅降級機制
- [ ] 健康檢查涵蓋所有關鍵組件
- [ ] 日誌使用結構化格式
- [ ] API 遵循標準協議 (MCP)

### 故障排除指南

#### 虛擬環境問題
1. 確認虛擬環境路徑: `which python`
2. 檢查 Python 版本: `python --version`
3. 驗證包安裝: `pip list`
4. 重新激活: `source .venv/bin/activate`

#### 依賴衝突問題
1. 清理虛擬環境: `rm -rf .venv`
2. 重新創建: `python -m venv .venv`
3. 激活並安裝: `source .venv/bin/activate && pip install -r requirements.txt`

#### 監控和配置問題
1. 檢查配置文件格式和內容
2. 驗證環境變量設置
3. 查看結構化日誌輸出
4. 運行健康檢查腳本

---

## 參考資源

### 相關文檔
- [Phase 3 實現文檔](phase3.md) - 完整的 MCP 服務器實現過程
- [項目計劃](plan.md) - 三級規則系統架構設計
- [Phase 1 規則](rules1.md) - 基礎開發規則和模塊化重構
- [Phase 2 規則](rules2.md) - 複雜系統架構和規則引擎實現

### 技術標準
- [MCP 協議規範](https://github.com/anthropics/mcp) - Model Context Protocol 官方文檔
- [FastMCP 框架](https://github.com/jlowin/fastmcp) - Python MCP 服務器框架
- [Python 虛擬環境指南](https://docs.python.org/3/tutorial/venv.html) - 官方虛擬環境文檔

### 最佳實踐
- 始終在虛擬環境中進行開發和測試
- 使用版本控制管理 requirements.txt
- 實現完整的監控和日誌系統
- 提供詳細的健康檢查和故障排除文檔
- 遵循 MCP 協議標準確保互操作性

**注意**: 本規則集特別強調虛擬環境管理，這是 Phase 3 開發過程中反覆遇到的問題。請務必遵循 P17 規則，確保所有 Python 操作都在正確的虛擬環境中進行。
