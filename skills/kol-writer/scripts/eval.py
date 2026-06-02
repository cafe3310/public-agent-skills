#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自媒体文案转写评测脚本 (scripts/eval.py)

该脚本用于现场演示或开发测试中，并行调用百灵模型（Ring-2.6-1T）及国内其他主流模型，
对同一输入进行转写，并使用裁判模型（LLM-as-a-judge）从三个维度进行评分对比，
最终生成 Markdown 对比评测报告。
"""

import os
import sys
import json

# 模拟 API 调用与评测逻辑。在真实环境需配置相应的 API Key 和客户端
# 针对 Ring-2.6-1T 我们通常使用标准接口

BLACK_WORDS = ["值得一提的是", "不得不说", "毋庸置疑", "不可否认", "双刃剑", "总而言之", "综上所述"]

def call_llm(model_name: str, system_prompt: str, user_input: str) -> str:
    """
    模拟调用不同的 LLM
    """
    # 真实场景：
    # if model_name == "Ring-2.6-1T":
    #     client = genai.Client() ...
    # return response.text
    return f"【{model_name} 模拟生成的文本】"

def judge_style(original_style_sample: str, generated_text: str) -> dict:
    """
    裁判模型评分逻辑 (LLM-as-a-judge)
    评测三个指标：
    1. AI-ness (去AI味，越低越好，换算为 1-10 分，10分表示最像真人)
    2. Style Matching (文风模仿度 1-10 分)
    3. Platform Hook (平台排版与吸睛度 1-10 分)
    """
    # 检测黑名单词频
    blacklist_count = sum(generated_text.count(word) for word in BLACK_WORDS)
    ai_score = max(1.0, 10.0 - blacklist_count * 1.5)
    
    # 真实场景这里会调用裁判模型打分，此处模拟逻辑
    return {
        "ai_score": ai_score,
        "style_score": 8.5 if "模拟" in generated_text else 6.0,
        "hook_score": 9.0 if "模拟" in generated_text else 5.0
    }

def generate_report(test_case: dict, results: dict):
    """
    生成 Markdown 格式的评测报告
    """
    report = []
    report.append("# 📊 自媒体文案转写模型对比评测报告\n")
    report.append(f"**测试用例**: {test_case['name']}")
    report.append(f"**目标平台**: {test_case['platform']}\n")
    
    report.append("## 1. 评分汇总 (LLM-as-a-judge)")
    report.append("| 模型名称 | 去AI味得分 (高优) | 文风模仿得分 | 平台Hook得分 | 综合得分 |")
    report.append("| :--- | :--- | :--- | :--- | :--- |")
    
    for model, scores in results.items():
        avg = sum(scores.values()) / len(scores)
        report.append(f"| **{model}** | {scores['ai_score']:.1f}/10 | {scores['style_score']:.1f}/10 | {scores['hook_score']:.1f}/10 | **{avg:.2f}/10** |")
    
    report.append("\n## 2. 生成文本详细对比")
    for model, data in results.items():
        report.append(f"### 📱 {model} 的输出")
        report.append(f"> {data['text']}\n")
        
    print("\n".join(report))

def main():
    print("开始自媒体文案转写评测...")
    
    # 评测用例定义
    test_case = {
        "name": "性价比大模型横评",
        "platform": "小红书",
        "original_talk": "我想聊聊国内大模型，现在大家都打价格战。好多人都说便宜没好货，但我觉得百灵Ring-2.6真的是降维打击，比如长文本上它的幻觉特别低，而且API很便宜，具体你可以帮我查查对比一下。帮我用科技博主大白话风格写出来。",
        "style_sample": "看了一圈国内大模型，讲真，有些厂家虽然价格便宜，但那个生成质量实在难顶。要么是说教感拉满，要么一问长文本直接翻车。今天咱们不谈虚的，直接拉实测数据..."
    }
    
    # 待对比的模型
    models = ["Ring-2.6-1T", "Competitor-A", "Competitor-B"]
    
    results = {}
    
    # 执行评测
    for model in models:
        # 子流程 1-4 综合输出
        system_prompt = "你是一个自媒体文案专家，请遵循 kol-writer 技能规范..."
        output_text = call_llm(model, system_prompt, test_case["original_talk"])
        
        # 评测打分
        scores = judge_style(test_case["style_sample"], output_text)
        scores["text"] = output_text
        results[model] = scores
        
    # 输出报告
    generate_report(test_case, results)

if __name__ == "__main__":
    main()
