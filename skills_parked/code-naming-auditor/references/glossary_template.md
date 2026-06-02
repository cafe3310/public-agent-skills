# 项目术语表 - 模板

本模板旨在帮助您定义项目中的命名规范。

---

## 1. 名词 (Nouns)

### 核心业务名词

- User -- 代表系统中的一个注册用户
- Order -- 代表一次客户交易
...

### 通用技术名词

- Content -- 由多行文本组成的文本块
- Line -- 文件中的单行文本
...

---

## 2. 动词 (Verbs)

- get -- 通过唯一标识符精确获取单个资源，如 getUserById, getSettings
- list -- 枚举一类资源，通常返回一个列表，如 listUsers, listAllEntityTypes
- find -- 根据结构化、确定性条件查找资源，如 findUsersByRole, findRelations
- search -- 根据模糊、非结构化模式搜索资源，如 searchUsersByBio, searchEntityContentByRegex
...
