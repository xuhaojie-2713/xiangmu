import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path

# 页面配置
st.set_page_config(page_title="Air Quality Dashboard", layout="wide")

# ==== 数据加载 & 预处理 ====
@st.cache_data(ttl=3600)
def load_data():
    # 自动定位项目根目录
    app_dir = Path(__file__).resolve().parent
    project_root = app_dir.parent
    data_path = project_root / "data" / "processed" / "china_50_cities.csv"

    if not data_path.exists():
        st.error(f"数据文件未找到：{data_path}")
        return pd.DataFrame()

    df = pd.read_csv(data_path, parse_dates=['Datetime'])
    df = df.set_index('Datetime').sort_index()
    return df

# 主程序
if __name__ == "__main__":
    df = load_data()
    if df.empty:
        st.stop()

    # 侧边栏：污染物选择
    pollutant = st.sidebar.selectbox(
        "选择污染物",
        ['CO(GT)', 'NO2(GT)', 'C6H6(GT)', 'NMHC(GT)']
    )
    label_map = {'CO(GT)': 'CO', 'NO2(GT)': 'NO2', 'C6H6(GT)': 'C6H6', 'NMHC(GT)': 'NMHC'}
    display_name = label_map[pollutant]

    # 时间范围选择
    min_date = df.index.min().date()
    max_date = df.index.max().date()
    start_date, end_date = st.sidebar.slider(
        "选择日期范围",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date)
    )
    df = df.loc[start_date:end_date]

    # 计算滑动平均
    df['rolling_avg'] = df[pollutant].rolling(window=7*24, min_periods=1).mean()

    # 月趋势：使用 'ME'，并重命名
    monthly = (
        df[pollutant]
        .resample('ME')
        .mean()
        .reset_index()
        .rename(columns={'Datetime': 'Month', pollutant: 'Value'})
    )

    # 小时趋势：构建统一 DataFrame
    hourly_series = df[pollutant].groupby(df.index.hour).mean()
    hourly = pd.DataFrame({
        'Hour': hourly_series.index,
        'Value': hourly_series.values
    })

    # AQI 分级
    def classify_aqi(val):
        if pd.isna(val):
            return 'Unknown'
        if val <= 1:
            return 'Good'
        if val <= 2:
            return 'Moderate'
        if val <= 10:
            return 'Unhealthy'
        return 'Hazardous'

    df['AQI_Level'] = df[pollutant].apply(classify_aqi)

    # 视图切换
    view = st.sidebar.radio(
        "选择视图",
        ['综合仪表盘', 'Monthly Animation', '导出 HTML']
    )

    # ==== 视图一：综合仪表盘 ====
    if view == '综合仪表盘':
        fig = make_subplots(
            rows=3, cols=2,
            horizontal_spacing=0.1, vertical_spacing=0.12
        )

        # 月趋势
        fig.add_trace(
            go.Scatter(x=monthly['Month'], y=monthly['Value'], name='Monthly Avg'),
            row=1, col=1
        )
        fig.update_xaxes(title_text='Month', row=1, col=1)
        fig.update_yaxes(title_text=display_name, row=1, col=1)

        # 小时趋势
        fig.add_trace(
            go.Bar(x=hourly['Hour'], y=hourly['Value'], name='Hourly Avg'),
            row=1, col=2
        )
        fig.update_xaxes(title_text='Hour', row=1, col=2)
        fig.update_yaxes(title_text=display_name, row=1, col=2)

        # 箱线图
        fig.add_trace(
            go.Box(y=df[pollutant].dropna(), name='Boxplot'),
            row=2, col=1
        )
        fig.update_xaxes(title_text='', row=2, col=1)
        fig.update_yaxes(title_text=display_name, row=2, col=1)

        # 相关热力图
        polls = ['CO(GT)', 'NO2(GT)', 'C6H6(GT)', 'NMHC(GT)']
        corr = df[polls].corr()
        fig.add_trace(
            go.Heatmap(
                z=corr.values,
                x=[label_map[c] for c in polls],
                y=[label_map[c] for c in polls],
                colorscale='Viridis', zmin=-1, zmax=1
            ),
            row=2, col=2
        )
        fig.update_xaxes(title_text='Pollutant', row=2, col=2)
        fig.update_yaxes(title_text='Pollutant', row=2, col=2)

        # 7 天滑动平均
        fig.add_trace(
            go.Scatter(x=df.index, y=df['rolling_avg'], name='7-day MA'),
            row=3, col=1
        )
        fig.update_xaxes(title_text='Datetime', row=3, col=1)
        fig.update_yaxes(title_text=f'{display_name} MA', row=3, col=1)

        # 按站点箱线图
        if 'Station' in df.columns:
            for station in df['Station'].unique():
                fig.add_trace(
                    go.Box(y=df[df['Station'] == station][pollutant], name=str(station)),
                    row=3, col=2
                )
        fig.update_xaxes(title_text='Station', row=3, col=2)
        fig.update_yaxes(title_text=display_name, row=3, col=2)

        fig.update_layout(
            height=900, width=1200,
            title_text=f"{display_name} Analysis Summary",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})

    # ==== 视图二：Monthly Animation ====:
        monthly['MonthStr'] = monthly['Month'].dt.strftime('%Y-%m')
        fig_anim = px.line(
            monthly, x='Month', y='Value',
            animation_frame='MonthStr',
            title=f"{display_name} Monthly Animation",
            labels={'Value': display_name, 'Month': 'Month'}
        )
        fig_anim.update_layout(transition={'duration': 500})
        st.plotly_chart(fig_anim, use_container_width=True)

    # 视图三：导出 HTML
    else:
        export_fig = make_subplots(rows=1, cols=1)
        export_fig.add_trace(
            go.Scatter(x=monthly['Month'], y=monthly['Value'], name='Monthly')
        )
        export_fig.update_layout(title=f"{display_name} Monthly", height=500)

        # 处理文件名中的特殊字符
        safe_pollutant = pollutant.replace("(", "").replace(")", "")
        html_path = f"interactive_{safe_pollutant}.html"
        export_fig.write_html(html_path, include_plotlyjs='cdn')

        st.success(f"✅ 已生成交互式 HTML：{html_path}")
        st.markdown(f"[点击此处下载 HTML 文件]({html_path})")
