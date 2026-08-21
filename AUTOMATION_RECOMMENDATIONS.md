## Claude Code Automation Recommendations

I've analyzed your codebase and identified the top automations for each category. Here are my top 1-2 recommendations per type:

### Codebase Profile
- **Type**: Python/C embedded ML project
- **Framework**: Scikit-learn based ML pipeline
- **Key Libraries**: numpy, scipy, scikit-learn, matplotlib (inferred)

---

### 🔌 MCP Servers

#### context7
**Why**: Live documentation lookup for Python ML libraries (numpy, scikit-learn, matplotlib) and embedded development references will significantly reduce context switching during development.
**Install**: `claude mcp add context7`

---

### 🎯 Skills

#### ml-pipeline-boilerplate
**Why**: Your project follows a standard ML workflow (data collection → feature extraction → model training → evaluation). A skill to generate boilerplate for new ML pipelines would save repetitive setup time.
**Create**: `.claude\skills\ml-pipeline-boilerplate\SKILL.md`
**Invocation**: Both
```yaml
---
name: ml-pipeline-boilerplate
description: Generate boilerplate code for standard ML pipeline stages
disable-model-invocation: false
---
```
**Also available in**: Could be part of a future ml-utils plugin

---

### ⚡ Hooks

#### auto-format-python
**Why**: Python files in host_scripts/ and analysis/ directories would benefit from consistent formatting on save to maintain code quality across the ML codebase.
**Where**: `.claude\settings.json`
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python -m black $FILE_PATH",
            "timeout": 5000
          }
        ]
      }
    ]
  }
}
```

---

### 🤖 Subagents

#### firmware-ml-reviewer
**Why**: Your firmware contains signal processing (FFT.py) and ML inference code (embedded_main.py, model.py) that would benefit from parallel review for correctness and efficiency.
**Where**: `.claude\agents\firmware-ml-reviewer.md`
```yaml
---
name: firmware-ml-reviewer
description: Specialized reviewer for embedded ML and signal processing code
trigger: firmware/* files
---
```

---

**Want more?** Ask for additional recommendations for any specific category (e.g., "show me more MCP server options" or "what other hooks would help?").

**Want help implementing any of these?** Just ask and I can help you set up any of the recommendations above.