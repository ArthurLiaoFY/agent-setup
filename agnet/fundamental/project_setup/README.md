01. Environment Detection

辨識目前執行環境
- OS detection (Windows / macOS / Linux)
- Python installation & version
- uv availability & version
- git availability & version
- Existing virtual environment


02. Project Detection

辨識目前專案狀態
- pyproject.toml
- uv.lock
- requirements.txt
- .python-version
- Existing project structure


03. Environment Initialization

建立開發環境
- Install uv if necessary
- Initialize project if new
- Create .venv
- Select Python interpreter


04. Dependency Setup

處理專案依賴
- Install dependencies
- Synchronize lock file
- Handle development dependencies
- Preserve existing dependencies


05. Project Validation

確認環境是否正確
- Verify Python interpreter
- Verify installed packages
- Verify imports
- Verify project entry point

## Python Project Setup Workflow

```mermaid
flowchart TD
    A["01. Environment Detection<br/>OS / Python / uv / Git / Virtual Environment"]
    B["02. Project Detection<br/>pyproject.toml / uv.lock / requirements.txt<br/>.python-version / Project Structure"]
    C{"03. Is Environment Initialization Required?"}
    D["03. Environment Initialization<br/>Install uv if necessary<br/>Initialize project if new<br/>Select Python interpreter<br/>Create .venv"]
    E["Skip Environment Initialization<br/>Reuse Existing Project Configuration<br/>and Virtual Environment"]
    F["04. Dependency Setup<br/>Install / Synchronize Dependencies<br/>Update Lockfile if Necessary<br/>Handle Development Dependencies<br/>Preserve Existing Dependencies"]
    G["05. Project Validation<br/>Verify Python Interpreter<br/>Verify Installed Packages<br/>Verify Imports<br/>Verify Project Entry Point"]
    H["Project Environment Ready"]

    A --> B
    B --> C
    C -->|Yes| D
    C -->|No| E
    D --> F
    E --> F
    F --> G
    G --> H

    classDef detection fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef initialization fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef dependency fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef validation fill:#d1fae5,stroke:#059669,color:#064e3b

    class A,B detection
    class D,E initialization
    class F dependency
    class G,H validation
```