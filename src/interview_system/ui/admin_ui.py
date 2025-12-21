#!/usr/bin/env python3
# coding: utf-8
"""
管理后台模块 - 大学生五育并举访谈智能体
提供数据查看、统计分析和管理功能
"""

import os
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
import json

import interview_system.common.logger as logger
from interview_system.common.config import WEB_CONFIG, EXPORT_DIR, ensure_dirs
from interview_system.services.session_manager import get_session_manager
from interview_system.reports.visualization import DataVisualizer, check_plotly_available

# 检查Gradio是否可用
GRADIO_AVAILABLE = False
try:
    import gradio as gr
    GRADIO_AVAILABLE = True
except ImportError:
    logger.warning("未安装gradio，无法启动管理后台")


class AdminDashboard:
    """管理后台仪表盘"""

    def __init__(self):
        self.session_mgr = get_session_manager()
        self.visualizer = DataVisualizer()

    def get_overview_stats(self) -> dict:
        """获取概览统计"""
        stats = self.session_mgr.get_statistics()
        return {
            "total": stats.get('total_sessions', 0),
            "finished": stats.get('finished_sessions', 0),
            "completion_rate": stats.get('completion_rate', 0),
            "avg_depth": stats.get('avg_depth_score', 0)
        }

    def format_sessions_table(self, sessions: List) -> List[List]:
        """格式化会话列表为表格数据"""
        table_data = []
        for session in sessions:
            table_data.append([
                session.session_id,
                session.user_name,
                session.start_time,
                session.end_time or "进行中",
                "✅ 已完成" if session.is_finished else "⏳ 进行中",
                len(session.conversation_log) if hasattr(session, 'conversation_log') else 0
            ])
        return table_data

    def get_session_detail(self, session_id: str) -> Tuple[str, str, str]:
        """获取会话详情"""
        if not session_id:
            return "请选择一个会话", "", ""

        session = self.session_mgr.get_session(session_id)
        if not session:
            return "会话不存在", "", ""

        # 基本信息
        info = f"""
## 📋 会话信息

- **会话ID**: {session.session_id}
- **用户名**: {session.user_name}
- **开始时间**: {session.start_time}
- **结束时间**: {session.end_time or '进行中'}
- **状态**: {'✅ 已完成' if session.is_finished else '⏳ 进行中'}
- **当前问题**: 第 {session.current_question_idx + 1} 题
- **对话记录数**: {len(session.conversation_log)}
"""

        # 对话记录
        conversation_md = "## 💬 对话记录\n\n"
        if session.conversation_log:
            for i, log in enumerate(session.conversation_log, 1):
                topic = log.get('topic', '未知')
                q_type = log.get('question_type', '未知')
                question = log.get('question', '无问题')
                answer = log.get('answer', '无回答')
                depth = log.get('depth_score', 0)
                is_ai = log.get('is_ai_generated', False)

                ai_badge = "🤖" if is_ai else "📝"
                conversation_md += f"""
### {i}. {topic} - {q_type} {ai_badge}

**问题**: {question}

**回答**: {answer}

**深度分**: {depth}

---
"""
        else:
            conversation_md += "*暂无对话记录*\n"

        # 统计信息
        scene_stats = {}
        edu_stats = {}
        for log in session.conversation_log:
            topic = log.get('topic', '')
            if '-' in topic:
                scene, edu = topic.split('-')
                scene_stats[scene] = scene_stats.get(scene, 0) + 1
                edu_stats[edu] = edu_stats.get(edu, 0) + 1

        stats_md = "## 📊 话题统计\n\n"
        if scene_stats:
            stats_md += "**场景分布**:\n"
            for scene, count in scene_stats.items():
                stats_md += f"- {scene}: {count} 次\n"

        if edu_stats:
            stats_md += "\n**五育分布**:\n"
            for edu, count in edu_stats.items():
                stats_md += f"- {edu}: {count} 次\n"

        return info, conversation_md, stats_md

    def export_session_data(self, session_id: str) -> str:
        """导出会话数据"""
        if not session_id:
            return "❌ 请选择一个会话"

        file_path = self.session_mgr.export_session(session_id)
        if file_path:
            return f"✅ 导出成功！\n\n文件路径: {file_path}"
        else:
            return "❌ 导出失败"

    def generate_statistics_report(self, days: int = 7) -> Tuple[Optional[object], str]:
        """生成统计报告"""
        if not check_plotly_available():
            return None, "⚠️ 未安装plotly，无法生成可视化图表\n\n请运行: pip install plotly"

        # 获取统计数据
        end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        stats = self.session_mgr.get_statistics(start_date, end_date)

        if not stats or stats.get('total_sessions', 0) == 0:
            return None, f"📊 最近{days}天暂无访谈数据"

        # 生成仪表盘
        dashboard = self.visualizer.create_statistics_dashboard(stats)

        # 生成文字报告
        report = f"""
# 📊 统计报告 (最近{days}天)

## 总体概况
- 总访谈数: {stats.get('total_sessions', 0)}
- 完成访谈数: {stats.get('finished_sessions', 0)}
- 完成率: {stats.get('completion_rate', 0)}%
- 平均深度分: {stats.get('avg_depth_score', 0)}

## 场景分布
"""
        for scene, count in stats.get('scene_distribution', {}).items():
            report += f"- {scene}: {count} 次\n"

        report += "\n## 五育分布\n"
        for edu, count in stats.get('edu_distribution', {}).items():
            report += f"- {edu}: {count} 次\n"

        report += "\n## 追问统计\n"
        for followup_type, count in stats.get('followup_distribution', {}).items():
            report += f"- {followup_type}: {count} 次\n"

        return dashboard, report

    def export_html_report(self, days: int = 7) -> str:
        """导出HTML报告"""
        if not check_plotly_available():
            return "❌ 未安装plotly，无法生成HTML报告"

        ensure_dirs()
        end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

        stats = self.session_mgr.get_statistics(start_date, end_date)
        daily_stats = self.session_mgr.get_daily_statistics(days)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(EXPORT_DIR, f"statistics_report_{timestamp}.html")

        result = self.visualizer.generate_html_report(stats, daily_stats, output_path)

        if result:
            return f"✅ HTML报告已导出！\n\n文件路径: {result}"
        else:
            return "❌ 导出失败"


def create_admin_interface():
    """创建管理后台界面"""
    if not GRADIO_AVAILABLE:
        logger.error("Gradio未安装，无法创建管理后台")
        return None

    dashboard = AdminDashboard()

    with gr.Blocks(
        title="访谈系统管理后台",
        theme=gr.themes.Soft()
    ) as demo:
        gr.Markdown("# 🎓 大学生五育并举访谈系统 - 管理后台")
        gr.Markdown("查看访谈记录、统计分析和数据导出")

        with gr.Tabs():
            # ===== Tab 1: 概览 =====
            with gr.Tab("📊 概览"):
                gr.Markdown("## 系统概览")

                with gr.Row():
                    total_box = gr.Number(label="总访谈数", interactive=False)
                    finished_box = gr.Number(label="完成访谈数", interactive=False)
                    rate_box = gr.Number(label="完成率 (%)", interactive=False)
                    depth_box = gr.Number(label="平均深度分", interactive=False)

                refresh_overview_btn = gr.Button("🔄 刷新概览", variant="primary")

                gr.Markdown("## 最近7天趋势")
                stats_days = gr.Slider(
                    minimum=1, maximum=30, value=7, step=1,
                    label="统计天数"
                )
                plot_output = gr.Plot(label="统计图表")
                report_output = gr.Markdown()

                with gr.Row():
                    gen_stats_btn = gr.Button("📈 生成统计图表", variant="primary")
                    export_html_btn = gr.Button("💾 导出HTML报告")

                export_result = gr.Textbox(label="导出结果", lines=3)

            # ===== Tab 2: 会话列表 =====
            with gr.Tab("📋 会话列表"):
                gr.Markdown("## 所有访谈会话")

                refresh_list_btn = gr.Button("🔄 刷新列表", variant="primary")

                sessions_table = gr.Dataframe(
                    headers=["会话ID", "用户名", "开始时间", "结束时间", "状态", "记录数"],
                    label="会话列表",
                    interactive=False,
                    wrap=True
                )

                gr.Markdown("## 会话详情")
                session_id_input = gr.Textbox(
                    label="会话ID",
                    placeholder="从上方表格复制会话ID粘贴到这里",
                    lines=1
                )

                view_detail_btn = gr.Button("👁️ 查看详情", variant="primary")
                export_session_btn = gr.Button("💾 导出此会话")

                with gr.Row():
                    with gr.Column():
                        session_info = gr.Markdown(label="基本信息")
                    with gr.Column():
                        session_stats = gr.Markdown(label="统计信息")

                conversation_detail = gr.Markdown(label="对话记录")
                export_session_result = gr.Textbox(label="导出结果", lines=2)

            # ===== Tab 3: 数据管理 =====
            with gr.Tab("🗄️ 数据管理"):
                gr.Markdown("## 数据库信息")

                db_info = gr.Markdown("""
### 数据库位置
- 文件名: `interview_data.db`
- 位置: 项目根目录

### 数据表
- `sessions`: 会话表
- `conversation_logs`: 对话日志表

### 备份建议
定期备份 `interview_data.db` 文件以防数据丢失。
""")

                gr.Markdown("## 批量导出")
                batch_export_btn = gr.Button("📦 导出所有会话 (JSON)", variant="secondary")
                batch_export_result = gr.Textbox(label="批量导出结果", lines=5)

        # ===== 事件绑定 =====
        def refresh_overview():
            stats = dashboard.get_overview_stats()
            return (
                stats['total'],
                stats['finished'],
                stats['completion_rate'],
                stats['avg_depth']
            )

        def refresh_sessions_list():
            sessions = dashboard.session_mgr.get_all_sessions()
            return dashboard.format_sessions_table(sessions)

        def batch_export_all():
            sessions = dashboard.session_mgr.get_all_sessions()
            results = []
            success_count = 0

            for session in sessions:
                file_path = dashboard.session_mgr.export_session(session.session_id)
                if file_path:
                    success_count += 1
                    results.append(f"✅ {session.session_id}: {file_path}")
                else:
                    results.append(f"❌ {session.session_id}: 导出失败")

            summary = f"批量导出完成！\n成功: {success_count}/{len(sessions)}\n\n"
            return summary + "\n".join(results)

        # 绑定事件
        refresh_overview_btn.click(
            refresh_overview,
            outputs=[total_box, finished_box, rate_box, depth_box]
        )

        gen_stats_btn.click(
            dashboard.generate_statistics_report,
            inputs=[stats_days],
            outputs=[plot_output, report_output]
        )

        export_html_btn.click(
            dashboard.export_html_report,
            inputs=[stats_days],
            outputs=[export_result]
        )

        refresh_list_btn.click(
            refresh_sessions_list,
            outputs=[sessions_table]
        )

        view_detail_btn.click(
            dashboard.get_session_detail,
            inputs=[session_id_input],
            outputs=[session_info, conversation_detail, session_stats]
        )

        export_session_btn.click(
            dashboard.export_session_data,
            inputs=[session_id_input],
            outputs=[export_session_result]
        )

        batch_export_btn.click(
            batch_export_all,
            outputs=[batch_export_result]
        )

        # 页面加载时刷新概览
        demo.load(
            refresh_overview,
            outputs=[total_box, finished_box, rate_box, depth_box]
        )

        demo.load(
            refresh_sessions_list,
            outputs=[sessions_table]
        )

    return demo


def check_gradio_available() -> bool:
    """检查Gradio是否可用"""
    return GRADIO_AVAILABLE


def start_admin_server(port: int = None):
    """
    启动管理后台服务器

    Args:
        port: 端口号（默认7861）
    """
    if not GRADIO_AVAILABLE:
        logger.error("无法启动管理后台：缺少 gradio 库")
        print("❌ 无法启动管理后台：缺少 gradio 库")
        print("请先运行: pip install gradio plotly")
        return

    demo = create_admin_interface()
    if not demo:
        return

    admin_port = port or (WEB_CONFIG.port + 1)

    print("\n" + "=" * 50)
    print("🔧 管理后台即将启动！")
    print(f"📍 访问地址：http://localhost:{admin_port}")
    print("=" * 50 + "\n")

    try:
        demo.launch(
            server_name="0.0.0.0",
            server_port=admin_port,
            share=False,  # 管理后台不生成公网链接
            prevent_thread_lock=False
        )
    except Exception as e:
        logger.error(f"启动管理后台失败: {e}")
        print(f"❌ 启动失败: {e}")


if __name__ == "__main__":
    start_admin_server()
