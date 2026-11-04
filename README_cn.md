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

同時安裝兩種設定：

```bash
agent-setup install --claude --copilot
```

安裝 Codex 設定：

```bash
agent-setup install --codex
```

這會建立：

```text
/path/to/project/AGENTS.md
```

同時安裝所有支援的設定：

```bash
agent-setup install --claude --copilot --codex
```

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

覆寫已存在的設定檔：

```bash
agent-setup install --claude --force
```

將 Claude 設定安裝到目前使用者的 Claude 設定目錄：

```bash
agent-setup install --claude --global
```

預設情況下，已存在的設定檔不會被覆寫。只有明確要取代現有檔案時才使用 `--force`。

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

## 更新 AGENT.md 後重新打包

儲存庫根目錄的 `AGENT.md` 是唯一的主要指令來源。修改後請在儲存庫根目錄執行：

```bash
uv run pytest -q
uv build
ls -l dist
```

建置流程會自動把 `AGENT.md` 同步到 Claude、GitHub Copilot 與 Codex 的模板，並產生 wheel 與 source distribution：

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