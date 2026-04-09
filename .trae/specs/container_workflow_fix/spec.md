# Container Workflow 修复 - 产品需求文档

## Overview
- **Summary**: 分析并修复 `.github/workflows/container.yml` 与当前项目配置不一致的问题。该工作流文件试图构建多个 Docker 服务镜像，但项目中缺少相应的部署文件和配置。
- **Purpose**: 解决工作流配置与项目实际架构不匹配的问题，确保 CI/CD 流程符合项目当前的状态和目标。
- **Target Users**: 项目维护者和开发者

## Goals
- 识别 container.yml 与项目配置的所有不一致之处
- 分析差异产生的原因
- 提供符合项目当前标准的修改方案
- 确保修改后的工作流与项目整体配置保持一致

## Non-Goals (Out of Scope)
- 不新增部署基础设施（如 deploy 目录、Containerfile 等）
- 不将项目改造成多服务部署架构
- 不新增 Docker 镜像构建相关功能

## Background & Context
项目 `taolib` 是一个纯 Python 库（Python >= 3.14），提供各种工具模块，通过 PyPI 发布。项目当前架构：
- 无 deploy 目录或 Containerfile 文件
- 现有 CI/CD 工作流包括：ci.yml（测试、lint、安全审计）、python-publish.yml（发布到 PyPI）、pages.yml（文档）
- container.yml 是遗留配置，试图构建 config-center、data-sync、log-platform、qrcode 等服务的 Docker 镜像

## Functional Requirements
- **FR-1**: 分析并记录 container.yml 与项目配置的所有不一致点
- **FR-2**: 删除或修改 container.yml 使其符合项目当前状态
- **FR-3**: 确保修改后的工作流文件语法正确

## Non-Functional Requirements
- **NFR-1**: 修改应最小化，只解决不一致问题
- **NFR-2**: 保持现有其他工作流文件不变
- **NFR-3**: 提供清晰的修改说明

## Constraints
- **Technical**: 项目是纯 Python 库，不需要容器化部署
- **Business**: 保持项目的轻量级特性
- **Dependencies**: 无外部依赖变更

## Assumptions
- container.yml 是历史遗留文件，与当前项目目标不符
- 项目不需要 Docker 容器构建流程
- 删除该工作流文件不会影响项目的正常 CI/CD 流程

## Acceptance Criteria

### AC-1: 不一致点分析完成
- **Given**: 已查看项目结构和所有相关配置文件
- **When**: 完成不一致点分析
- **Then**: 应有完整的不一致点清单和原因分析
- **Verification**: `human-judgment`

### AC-2: 工作流文件修复完成
- **Given**: 已完成不一致点分析
- **When**: 实施修改方案
- **Then**: container.yml 应被删除或修改为符合项目当前状态
- **Verification**: `programmatic`

### AC-3: 工作流文件语法正确
- **Given**: 已修改工作流文件
- **When**: 检查 YAML 语法
- **Then**: 文件应通过 YAML 语法验证
- **Verification**: `programmatic`

## Open Questions
- 无
