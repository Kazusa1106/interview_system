#!/usr/bin/env python3
# coding: utf-8
"""
数据可视化模块 - 大学生五育并举访谈智能体
提供统计图表生成功能
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logger

# 检查plotly是否可用
PLOTLY_AVAILABLE = False
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    logger.warning("未安装plotly，可视化功能受限。请运行: pip install plotly")


class DataVisualizer:
    """数据可视化器"""

    def __init__(self):
        self.color_scheme = {
            '学校': '#3498db',
            '家庭': '#e74c3c',
            '社区': '#2ecc71',
            '德育': '#9b59b6',
            '智育': '#3498db',
            '体育': '#e67e22',
            '美育': '#e91e63',
            '劳育': '#16a085'
        }

    def create_pie_chart(self, data: Dict[str, int], title: str) -> Optional[go.Figure]:
        """
        创建饼图

        Args:
            data: 数据字典 {标签: 数值}
            title: 图表标题

        Returns:
            Plotly图表对象
        """
        if not PLOTLY_AVAILABLE or not data:
            return None

        labels = list(data.keys())
        values = list(data.values())
        colors = [self.color_scheme.get(label, '#95a5a6') for label in labels]

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors),
            hole=0.3,
            textinfo='label+percent',
            textposition='auto'
        )])

        fig.update_layout(
            title=dict(text=title, font=dict(size=20, family='Microsoft YaHei')),
            font=dict(family='Microsoft YaHei', size=14),
            showlegend=True,
            height=400
        )

        return fig

    def create_bar_chart(self, data: Dict[str, int], title: str,
                        x_label: str = "", y_label: str = "数量") -> Optional[go.Figure]:
        """
        创建柱状图

        Args:
            data: 数据字典
            title: 图表标题
            x_label: X轴标签
            y_label: Y轴标签

        Returns:
            Plotly图表对象
        """
        if not PLOTLY_AVAILABLE or not data:
            return None

        labels = list(data.keys())
        values = list(data.values())
        colors = [self.color_scheme.get(label, '#95a5a6') for label in labels]

        fig = go.Figure(data=[go.Bar(
            x=labels,
            y=values,
            marker=dict(color=colors),
            text=values,
            textposition='auto'
        )])

        fig.update_layout(
            title=dict(text=title, font=dict(size=20, family='Microsoft YaHei')),
            xaxis_title=x_label,
            yaxis_title=y_label,
            font=dict(family='Microsoft YaHei', size=14),
            height=400,
            showlegend=False
        )

        return fig

    def create_line_chart(self, data: List[Dict], title: str,
                         x_key: str = 'date', y_keys: List[str] = None) -> Optional[go.Figure]:
        """
        创建折线图

        Args:
            data: 数据列表
            title: 图表标题
            x_key: X轴数据的键名
            y_keys: Y轴数据的键名列表

        Returns:
            Plotly图表对象
        """
        if not PLOTLY_AVAILABLE or not data or not y_keys:
            return None

        fig = go.Figure()

        for y_key in y_keys:
            x_values = [item.get(x_key) for item in data]
            y_values = [item.get(y_key, 0) for item in data]

            fig.add_trace(go.Scatter(
                x=x_values,
                y=y_values,
                mode='lines+markers',
                name=y_key,
                line=dict(width=2),
                marker=dict(size=8)
            ))

        fig.update_layout(
            title=dict(text=title, font=dict(size=20, family='Microsoft YaHei')),
            xaxis_title=x_key.capitalize(),
            yaxis_title='数量',
            font=dict(family='Microsoft YaHei', size=14),
            height=400,
            hovermode='x unified'
        )

        return fig

    def create_statistics_dashboard(self, statistics: Dict) -> Optional[go.Figure]:
        """
        创建统计仪表盘（多图组合）

        Args:
            statistics: 统计数据字典

        Returns:
            Plotly图表对象
        """
        if not PLOTLY_AVAILABLE:
            return None

        # 创建子图布局
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('场景分布', '五育分布', '追问类型分布', '完成情况'),
            specs=[
                [{"type": "pie"}, {"type": "pie"}],
                [{"type": "bar"}, {"type": "indicator"}]
            ]
        )

        # 场景分布饼图
        scene_data = statistics.get('scene_distribution', {})
        if scene_data:
            labels = list(scene_data.keys())
            values = list(scene_data.values())
            colors = [self.color_scheme.get(label, '#95a5a6') for label in labels]

            fig.add_trace(go.Pie(
                labels=labels,
                values=values,
                marker=dict(colors=colors),
                hole=0.3,
                name='场景'
            ), row=1, col=1)

        # 五育分布饼图
        edu_data = statistics.get('edu_distribution', {})
        if edu_data:
            labels = list(edu_data.keys())
            values = list(edu_data.values())
            colors = [self.color_scheme.get(label, '#95a5a6') for label in labels]

            fig.add_trace(go.Pie(
                labels=labels,
                values=values,
                marker=dict(colors=colors),
                hole=0.3,
                name='五育'
            ), row=1, col=2)

        # 追问类型柱状图
        followup_data = statistics.get('followup_distribution', {})
        if followup_data:
            labels = list(followup_data.keys())
            values = list(followup_data.values())

            fig.add_trace(go.Bar(
                x=labels,
                y=values,
                marker=dict(color=['#3498db', '#e74c3c']),
                text=values,
                textposition='auto',
                name='追问'
            ), row=2, col=1)

        # 完成率指示器
        completion_rate = statistics.get('completion_rate', 0)
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=completion_rate,
            title={'text': "访谈完成率 (%)"},
            delta={'reference': 80},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#2ecc71"},
                'steps': [
                    {'range': [0, 50], 'color': "#ecf0f1"},
                    {'range': [50, 80], 'color': "#bdc3c7"},
                    {'range': [80, 100], 'color': "#95a5a6"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ), row=2, col=2)

        fig.update_layout(
            title=dict(
                text="访谈数据统计仪表盘",
                font=dict(size=24, family='Microsoft YaHei')
            ),
            font=dict(family='Microsoft YaHei', size=12),
            height=800,
            showlegend=False
        )

        return fig

    def create_trend_chart(self, daily_stats: List[Dict]) -> Optional[go.Figure]:
        """
        创建趋势图

        Args:
            daily_stats: 每日统计数据列表

        Returns:
            Plotly图表对象
        """
        if not PLOTLY_AVAILABLE or not daily_stats:
            return None

        dates = [item['date'] for item in daily_stats]
        total_counts = [item['session_count'] for item in daily_stats]
        finished_counts = [item['finished_count'] for item in daily_stats]

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=dates,
            y=total_counts,
            mode='lines+markers',
            name='总访谈数',
            line=dict(color='#3498db', width=2),
            marker=dict(size=8)
        ))

        fig.add_trace(go.Scatter(
            x=dates,
            y=finished_counts,
            mode='lines+markers',
            name='完成访谈数',
            line=dict(color='#2ecc71', width=2),
            marker=dict(size=8)
        ))

        fig.update_layout(
            title=dict(
                text="访谈量趋势图",
                font=dict(size=20, family='Microsoft YaHei')
            ),
            xaxis_title="日期",
            yaxis_title="访谈数量",
            font=dict(family='Microsoft YaHei', size=14),
            height=400,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        return fig

    def generate_html_report(self, statistics: Dict, daily_stats: List[Dict],
                           output_path: str = None) -> Optional[str]:
        """
        生成HTML统计报告

        Args:
            statistics: 统计数据
            daily_stats: 每日统计数据
            output_path: 输出文件路径

        Returns:
            HTML字符串或保存的文件路径
        """
        if not PLOTLY_AVAILABLE:
            return None

        html_parts = []

        # 头部
        html_parts.append("""
        <html>
        <head>
            <meta charset="utf-8">
            <title>访谈系统统计报告</title>
            <style>
                body { font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                .header { text-align: center; padding: 20px; background: #3498db; color: white; border-radius: 10px; margin-bottom: 20px; }
                .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
                .summary-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; }
                .summary-card h3 { margin: 0 0 10px 0; color: #7f8c8d; font-size: 14px; }
                .summary-card .value { font-size: 32px; font-weight: bold; color: #2c3e50; }
                .chart-container { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎓 大学生五育并举访谈系统</h1>
                <h2>数据统计报告</h2>
                <p>生成时间: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
            </div>
        """)

        # 摘要卡片
        html_parts.append("""
            <div class="summary">
                <div class="summary-card">
                    <h3>总访谈数</h3>
                    <div class="value">""" + str(statistics.get('total_sessions', 0)) + """</div>
                </div>
                <div class="summary-card">
                    <h3>完成访谈数</h3>
                    <div class="value">""" + str(statistics.get('finished_sessions', 0)) + """</div>
                </div>
                <div class="summary-card">
                    <h3>完成率</h3>
                    <div class="value">""" + str(statistics.get('completion_rate', 0)) + """%</div>
                </div>
                <div class="summary-card">
                    <h3>平均深度分</h3>
                    <div class="value">""" + str(statistics.get('avg_depth_score', 0)) + """</div>
                </div>
            </div>
        """)

        # 添加图表
        if statistics:
            dashboard = self.create_statistics_dashboard(statistics)
            if dashboard:
                html_parts.append('<div class="chart-container">')
                html_parts.append(dashboard.to_html(include_plotlyjs='cdn', full_html=False))
                html_parts.append('</div>')

        if daily_stats:
            trend_chart = self.create_trend_chart(daily_stats)
            if trend_chart:
                html_parts.append('<div class="chart-container">')
                html_parts.append(trend_chart.to_html(include_plotlyjs='cdn', full_html=False))
                html_parts.append('</div>')

        html_parts.append("""
        </body>
        </html>
        """)

        html_content = '\n'.join(html_parts)

        # 保存到文件
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logger.info(f"HTML报告已保存: {output_path}")
                return output_path
            except Exception as e:
                logger.error(f"保存HTML报告失败: {e}")

        return html_content


def check_plotly_available() -> bool:
    """检查plotly是否可用"""
    return PLOTLY_AVAILABLE
