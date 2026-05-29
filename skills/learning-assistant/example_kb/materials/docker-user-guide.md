# Docker 官方用户指南

本文是 Docker 官方镜像与容器管理的用户指南。

- 来源/出处：[Docker Documentation](https://docs.docker.com/get-started/)

## 1. 基础说明
Docker 提供了通过容器打包和运行应用的能力。它提供了一套工具，使开发人员可以使用容器进行高效地部署、共享和运行软件。

## 2. 核心架构
- **Docker 守护进程 (Docker Daemon)**：监听 Docker API 请求并管理 Docker 对象。
- **Docker 客户端 (Docker Client)**：与 Docker 守护进程进行交互的主要方式。
- **Docker 仓库 (Docker Registry)**：存储 Docker 镜像的公开/私有仓库，例如 Docker Hub。
