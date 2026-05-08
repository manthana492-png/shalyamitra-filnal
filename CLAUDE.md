# ShalyaMitra Project - Claude Instructions

## Project Overview
- **Repository**: https://github.com/manthana492-png/shalyamitra-filnal.git
- **Owner**: manthana492-png
- **Local User**: Shiva Kumar (shivakumarcjh@gmail.com)
- **Branch**: main

## Graphify Integration (Always-On)

This project uses **graphify** for knowledge graph extraction and architecture understanding.

### Core Graph Files
- `graphify-out/GRAPH_REPORT.md` - Human-readable audit report with god nodes, communities, surprising connections
- `graphify-out/graph.json` - Machine-readable graph data (GraphRAG-ready)
- `graphify-out/graph.html` - Interactive visualization (open in browser)
- `graphify-out/cache/` - Semantic extraction cache for incremental updates

### When Working With This Codebase

**BEFORE answering architecture questions:**
1. Read `graphify-out/GRAPH_REPORT.md` for:
   - **God Nodes** (most connected abstractions)
   - **Community structure** (clusters of related concepts)
   - **Surprising Connections** (cross-cutting relationships)
   - **Suggested Questions** (graph-optimized queries)

2. If `graphify-out/wiki/index.md` exists, navigate it instead of reading raw files

**AFTER modifying code files:**
```powershell
# Rebuild graph incrementally (fast, no LLM needed for code-only changes)
python -c "from graphify.watch import _rebuild_code; from pathlib import Path; _rebuild_code(Path('.'))"
```

### Manual Graph Commands
```powershell
# Full rebuild (semantic extraction - uses Claude tokens)
python -m graphify . --update

# Query the graph
python -m graphify query "How does authentication work?"

# Find path between concepts
python -m graphify path "AuthUser" "BaseAgent"

# Explain a specific node
python -m graphify explain "DevilsAdvocateAgent"
```

### Git Hooks (Auto-Rebuild)
- **post-commit**: Auto-rebuilds graph after each commit (code-only, fast)
- **post-checkout**: Rebuilds graph when switching branches

To check status: `python -m graphify hook status`

### Graph Stats
- **Nodes**: 1259 entities/concepts
- **Edges**: 2326 relationships
- **Communities**: 159 clusters
- **Extraction**: 63% EXTRACTED, 37% INFERRED, 0% AMBIGUOUS

### Key Abstractions (God Nodes)
1. `AgentEvent` (89 edges) - Core event system
2. `EventType` (87 edges) - Event type definitions
3. `AuthUser` (75 edges) - Authentication layer
4. `BaseAgent` (61 edges) - Base agent implementation
5. `DevilsAdvocateAgent` (37 edges) - Surgical challenge agent

### Architecture Patterns
- **TriVision**: Three-camera operative perception
- **Dual-Path Audio**: Critical alerts vs conversational audio
- **Eleven-Agent Orchestration**: Event bus + memory cortex
- **PHI Redaction**: India-specific DPDP compliance
