## 自有 Skill 的 Git 管理

`skills/` 默认整体忽略，只逐条白名单放行自有 Skill。新增自有 Skill 时，必须同步在 `.gitignore` 添加 `!/skills/<name>/`，让自有源码由 Git 管理。
