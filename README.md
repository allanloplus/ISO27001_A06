# ISO 27001:2022 A.8.9 組態管理｜動畫教學簡報

控制屬性「運作流程 › 保全組態（Secure configuration）」教學動畫。
Q 版 **Allan Lo 講師**（台灣男聲 `zh-TW-YunJheNeural`）主講，**助教阿拉蕾**（`zh-TW-HsiaoYuNeural` 調高音調）串場。

## 成品

| 檔案 | 說明 |
|---|---|
| `output/ISO27001_A8.9_組態管理.mp4` | 1280×720 影片（含旁白、字幕），約 9 分 13 秒 |
| `index.html` → `slides/index.html` | 互動播放版（根目錄 index.html 會自動跳轉）：章節跳轉、字幕開關、全螢幕、鍵盤（空白鍵播放／←→ 快轉 5 秒） |
| `docs/講稿.md` | 完整逐字講稿與時間碼 |

## 課程大綱（13 段）

1. 開場｜8.9 組態管理（2022 新增控制）
2. 條文與控制屬性（建立、文件化、實作、監視、審查）
3. 運作流程地圖：5.37 → 8.9 →（8.4／8.18／8.19／8.24），對象：硬體・網路・軟體・服務
4. **Part 1 ISMS 作業重點**：組態管理生命週期、基準來源（原廠／CIS／GCB）、例外管理
5. 安全組態基準必備項目（ISO/IEC 27002 指引 7 項）
6. 組態紀錄（CMDB）・變更（8.32）・偏移監控
7. 管理案例一：防火牆臨時 Any-Any 規則變永久
8. 管理案例二：雲端儲存誤設公開讀取（服務組態、CSPM）
9. **Part 2 稽核查核重點**：文件／紀錄／現場三層查核法
10. 稽核員常用問句（問版本、問變更、問例外）
11. **Part 3 常見的缺失** TOP 6
12. 不符合事項寫法示範（事實＋要求＋證據）
13. 總結口訣：建・記・施・監・審

## 修改與重新產生

```bash
pip install edge-tts                      # 需要 ffmpeg
python3 build/tts.py                      # 依 build/script.py 產生語音、slides/narration.mp3、slides/timeline.js、docs/講稿.md
npm i playwright                          # 或使用既有的 Chromium
node build/render.mjs                     # 逐格渲染 → output/*.mp4
```

- 修改台詞：編輯 `build/script.py`，重跑 `tts.py`（時間軸會自動對齊）。
- 修改畫面：編輯 `slides/index.html` 中對應的 `<section data-scene="...">`；元素的 `data-in="n"` 表示第 n 句台詞開始時進場，`data-d` 為延遲秒數，`data-hl` 為該句講解時高亮。
- 渲染影片時若要與網頁相同字型，請在系統安裝 Huninn、Noto Sans TC、LXGW WenKai TC、JetBrains Mono（Google Fonts）。

> 案例皆經改編，不代表特定組織。阿拉蕾助教為原創 Q 版造型的致敬角色，對外公開發行前請自行評估角色名稱與造型的著作權／商標風險。
