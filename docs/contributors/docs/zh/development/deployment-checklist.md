# 部署待办

## 配置 Traefik

在预发布或生产主机上启动 Traefik 前，根据仓库中的示例创建本地环境文件：

```bash
cp env/.env.proxy.example env/.env.proxy
```

打开 `env/.env.proxy`，将 `TRAEFIK_ACME_EMAIL` 替换为真实且有人维护的运维邮箱。该文件已被 Git 忽略，因此每台代理主机都需要单独配置。

确认公开 DNS 记录已经指向代理主机，并且 TCP 端口 80 和 443 可以从公网访问。Let's Encrypt 的 HTTP-01 验证需要使用端口 80。

启动预发布或生产环境前，先校验并启动代理：

```bash
make proxy-check
make proxy-up
```

Traefik 签发的证书保存在 `aliencommons-proxy_letsencrypt` Docker volume 中。主机的持久化数据备份方案需要包含该 volume。
