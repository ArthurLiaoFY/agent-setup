# agent-setup

`agent-setup` 是用來安裝共用 AI coding agent 指令的命令列工具。它會將封裝好的指令範本安裝到指定專案，不需要在目標專案中加入 Python 程式碼。

## 安裝命令列工具

請選擇下列其中一種方式。這一步只會安裝 `agent-setup` 命令，不會直接修改你的專案。

### Windows

從 GitHub 安裝：

```powershell
py -m pip install "git+https://github.com/ArthurLiaoFY/agent-setup.git"
```

從本機原始碼安裝：

```powershell
cd C:\path\to\agent-setup
py -m pip install .
```

使用 uv 安裝：

```powershell
cd C:\path\to\agent-setup
uv tool install .
```

不永久安裝，直接執行目前專案：

```powershell
cd C:\path\to\agent-setup
uvx --from . agent-setup install --claude
```

若安裝後找不到 `agent-setup` 命令，請重新開啟終端機並確認 Python Scripts 目錄或 uv tools 目錄已加入 `PATH`。

### Linux / macOS

從 GitHub 安裝：

```bash
python3 -m pip install "git+https://github.com/ArthurLiaoFY/agent-setup.git"
```

從本機原始碼安裝：

```bash
cd /path/to/agent-setup
python3 -m pip install .
```

使用 uv 安裝：

```bash
cd /path/to/agent-setup
uv tool install .
```

不永久安裝，直接執行目前專案：

```bash
cd /path/to/agent-setup
uvx --from . agent-setup install --claude
```

## 安裝指令到專案

安裝完命令列工具後，先進入目標專案。

**Windows（PowerShell）：**

```powershell
cd C:\path\to\project
agent-setup install --claude
```

**Linux / macOS：**

```bash
cd /path/to/project
agent-setup install --claude
```

這會建立：

```text
/path/to/project/CLAUDE.md
```

安裝 GitHub Copilot 設定：

```bash
agent-setup install --copilot
```

這會建立：

```text
/path/to/project/.github/copilot-instructions.md
```

另外指定目標專案安裝：

```bash
agent-setup install --claude /path/to/project
```

安裝 Codex 設定：

```bash
agent-setup install --codex
```

這會建立：

```text
/path/to/project/AGENTS.md
```

每次安裝只能選擇一種 Agent profile。若要安裝多種設定，請分別執行對應指令。

## 其他選項

不切換目錄，直接指定目標專案。

**Windows（PowerShell）：**

```powershell
agent-setup install --claude C:\path\to\project
```

**Linux / macOS：**

```bash
agent-setup install --claude /path/to/project
```

將 Claude 設定安裝到目前使用者的 Claude 設定目錄：

```bash
agent-setup install --claude --global
```

重複安裝時，Adapter、`agent_rules/CORE.md` 與 `agent_rules/fundamental/` 會更新；現有的
`agent_rules/additional/` 檔案會保留，不會被覆寫。`--force` 已移除，因為檔案歸屬規則會
自動套用。

## 確認安裝結果

```bash
agent-setup --help
agent-setup install --help
```

## 關於 pip 的參數

設定類型參數是由 `agent-setup` 處理，不是由 `pip` 處理。因此以下寫法無效：

```bash
pip install agent-setup --claude
```

正確方式需要分成兩個步驟：

```bash
pip install "git+https://github.com/ArthurLiaoFY/agent-setup.git"
agent-setup install --claude
```

## 更新 Agent 資源後重新打包

共用行為位於 `src/agent_setup/resources/core/CORE.md`，各工具入口位於 `src/agent_setup/resources/adapters/`。修改後請在儲存庫根目錄執行：

```bash
uv run pytest -q
uv build
ls -l dist
```

建置流程會產生包含所有 Agent 資源的 wheel 與 source distribution：

```text
dist/agent_setup-<版本>.whl
dist/agent_setup-<版本>.tar.gz
```

若要更新已安裝於本機的 uv tool：

```bash
uv tool install --force .
```

如果修改了 `pyproject.toml` 中的專案版本，仍然使用相同指令重新建置：

```bash
uv build
```


# 版本更新流程
## 1. 修改版本號（例如 0.1.0 -> 0.1.1）
## 編輯 pyproject.toml

## 2. 執行測試
uv run pytest

## 3. Build
uv build

## 4. 確認 build artifacts
ls dist/

## 5. Commit & Push
git add pyproject.toml src/agent_setup/resources/core/CORE.md
git commit -m "Update core agent rules"
git push origin main

## 6. 建立版本標籤（建議）
git tag v0.1.1
git push origin v0.1.1