## 自有 Skill 的 Git 管理

共享 `skills/` 目录默认整体忽略，自有 Skill 按目录逐条白名单入库。新增自有 Skill 时，同步更新 `.gitignore`，添加 `!/skills/<name>/` 并确认该目录源码可由 Git 跟踪；不放开整个 Skills 目录。
