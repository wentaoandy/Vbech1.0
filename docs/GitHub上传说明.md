# GitHub 上传说明

这个目录是干净版仓库，可以直接初始化 Git 并推送到 GitHub。

推荐命令：

```powershell
cd B:\vbench_github_clean
git init
git branch -M main
git remote add origin https://github.com/wentaoandy/Vbech1.0.git
git add .
git commit -m "Add clean ConsisID VBench report package"
git push -u origin main
```

如果目标仓库已有失败历史，建议使用这个干净目录重新推送，而不是在旧的 `B:\vbench_struct` 里删除文件后继续提交。原因是旧 Git 历史中已经包含大对象，删除工作区文件不会自动删除历史对象。
