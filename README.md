# 我的个人主页

这是我的个人网站源码仓库，使用 [Hugo](https://gohugo.io/) 构建，并采用 [PaperMod](https://github.com/adityatelange/hugo-PaperMod) 主题。

网站内容主要用于记录个人博客、项目与思考。

## 在线访问

GitHub Pages：

https://12041720.github.io/my-website/

## 技术栈

- Hugo
- PaperMod
- Markdown
- GitHub Actions
- GitHub Pages

## 本地运行

仓库使用 Git Submodule 管理 PaperMod 主题，首次克隆时建议同时拉取子模块：

```bash
git clone --recurse-submodules https://github.com/12041720/my-website.git
cd my-website
```

如果已经克隆了仓库但没有拉取主题，可以执行：

```bash
git submodule update --init --recursive
```

启动 Hugo 本地开发服务器：

```bash
hugo server -D
```

然后访问：

```text
http://localhost:1313/
```

## 构建

生成生产环境静态文件：

```bash
hugo --gc --minify
```

生成后的站点文件位于 `public/` 目录。

## 项目结构

```text
.
├── .github/workflows/   # GitHub Actions 部署配置
├── archetypes/          # Hugo 内容模板
├── assets/              # 站点资源
├── content/             # 页面、博客和项目内容
├── layouts/             # 自定义页面布局
├── scripts/             # 辅助脚本
├── themes/PaperMod/     # PaperMod 主题子模块
├── hugo.toml            # Hugo 主配置
└── README.md
```

## 部署

仓库已经配置 GitHub Actions。向 `main` 分支推送代码后，工作流会自动使用 Hugo 构建站点，并部署到 GitHub Pages。
