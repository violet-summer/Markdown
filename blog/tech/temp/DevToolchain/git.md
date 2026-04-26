---
title: Git 实用入门与协作流程
published: 2026-04-13
updated: 2026-04-13

description: "从本地版本管理到团队协作，整理一套高频 Git 命令和可落地工作流。"
pinned: false
tags: [DevToolchain, Git, 工程效率]
category: 开发工具链
image: ""
draft: false
---

# git使用简要教程

Git 是开发中最常用的版本控制工具。它最核心的价值不是“记住命令”，而是帮助你在多人协作中**安全地记录变化、追踪问题、回滚风险**。

本文按照“从单人开发到团队协作”的顺序整理常用操作，适合作为日常速查手册。

## 1. 三个工作区的理解

很多 Git 困惑都来自对工作区模型不清晰。你可以先记住这三个区域：

- **工作区（Working Tree）**：你正在修改的文件。
- **暂存区（Index / Staging）**：准备提交的内容快照。
- **本地仓库（Repository）**：通过 commit 保存的历史记录。

对应的高频命令：

```bash
git status          # 看当前状态
git add <file>      # 把修改放进暂存区
git commit -m "msg" # 把暂存区内容提交到本地仓库
```

## 2. 新项目最小流程

```bash
git init
git add .
git commit -m "chore: init project"
git branch -M main
git remote add origin <repo-url>
git push -u origin main
```

如果是克隆现有项目：

```bash
git clone <repo-url>
cd <repo>
git checkout -b feature/xxx
```

## 3. 日常开发循环

推荐把每天的开发切成“小步提交”：

1. 拉取最新主干代码
2. 在功能分支开发
3. 每完成一个小目标就 commit
4. 推送并发起 PR

示例：

```bash
git checkout main
git pull --rebase
git checkout -b feature/login
# ... coding
git add .
git commit -m "feat: add login form validation"
git push -u origin feature/login
```

## 4. 冲突处理的基本套路

多人协作不可避免会冲突，核心是“先同步，再解决，再验证”。

```bash
git pull --rebase origin main
# 发生冲突后，手动编辑冲突文件
git add <resolved-file>
git rebase --continue
```

建议：

- 解决冲突后先本地运行测试再继续推送。
- 单个提交只做一件事，冲突会明显减少。
- 命名清晰的分支和 commit message 能大幅降低沟通成本。

## 5. 常见回退与恢复

### 撤销工作区修改（未暂存）

```bash
git restore <file>
```

### 撤销暂存区（保留工作区改动）

```bash
git restore --staged <file>
```

### 回退到指定提交（生成反向提交，适合已推送场景）

```bash
git revert <commit-id>
```

> 对共享分支，优先使用 `revert`，少用改写历史的操作。

## 6. 提交信息建议

建议使用约定式提交（Conventional Commits）：

- `feat:` 新功能
- `fix:` 修复问题
- `refactor:` 重构
- `docs:` 文档更新
- `test:` 测试相关
- `chore:` 杂项维护

示例：

```text
feat(auth): add refresh token rotation
fix(api): handle empty query result
docs(git): add rebase conflict section
```

## 7. 一份可长期复用的 Git 习惯

- 主分支保持可发布状态。
- 功能开发都走分支，不在主分支直接改。
- 小步提交，提交信息能说明“为什么改”。
- 推送前先同步主干，减少冲突。
- 出问题先看 `git status` 和 `git log --oneline --graph`。

如果你把这些习惯稳定下来，Git 就会从“记命令”变成“可控协作系统”。

## 8. 初学小问题：`.gitignore` 不生效

很多人都会遇到这个问题：事后更新了 `.gitignore`，但某个目录仍然被 Git 追踪。

根本原因是：`.gitignore` 只对“未被追踪”的文件生效。  
如果文件已经被提交过（或已在索引中），Git 会继续追踪它。

### 正确处理步骤

先保证 `.gitignore` 规则正确，例如忽略 `config/`：

```gitignore
config/
```

然后把已追踪文件从索引中移除（保留本地文件）：

```bash
git rm -r --cached config/
git add .
git status
git commit -m "chore: stop tracking config directory"
```

如果你改了很多规则，想全量重算一次：

```bash
git rm -r --cached .
git add .
git status
git commit -m "chore: refresh tracked files with new gitignore"
```

### 注意事项

- `--cached` 只取消追踪，不会删除你本地工作区文件。
- 该提交推送后，远程仓库会表现为这些文件被删除（从版本控制中移除）。
- 执行全量重算前，最好先保证工作区干净，避免误操作。

## 9. Git 常用命令速查

```bash
# 状态与历史
git status
git log --oneline --graph --decorate -20
git diff

# 分支与切换
git branch
git checkout -b feature/xxx
git switch main

# 提交与同步
git add .
git commit -m "feat: ..."
git pull --rebase
git push -u origin <branch>

# 回退与恢复
git restore <file>
git restore --staged <file>
git revert <commit-id>
```
