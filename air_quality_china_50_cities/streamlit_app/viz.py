from turtle import st
from typing import Union, List

import pandas as pd
import numpy as np
from pyecharts.charts import (
    Line, Bar, HeatMap, Calendar, Surface3D, Timeline
)
from pyecharts import options as opts
import folium
from folium.plugins import TimestampedGeoJson
import plotly.graph_objects as go

# 配色方案
PALETTE = ["#5470C6", "#91CC75", "#EE6666", "#73C0DE", "#FAC858", "#3BA272"]

# 默认污染物和气象指标
DEFAULT_POLLUTANTS = [
    'CO(GT)', 'PT08.S1(CO)', 'NMHC(GT)', 'C6H6(GT)',
    'PT08.S2(NMHC)', 'NOx(GT)', 'PT08.S3(NOx)',
    'NO2(GT)', 'PT08.S4(NO2)', 'PT08.S5(O3)'
]
DEFAULT_METEO = ['T', 'RH', 'AH', 'W']

# --- 数据预处理辅助函数 ---
def ensure_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """
    确保 DataFrame 中有标准的 Datetime 和 Date 列
    """
    df = df.copy()  # ✅ 避免 SettingWithCopyWarning
    if 'Datetime' in df.columns:
        df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
        if 'Date' not in df.columns:
            df['Date'] = df['Datetime'].dt.date
    else:
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
            df['Datetime'] = pd.to_datetime(df['Date'])
        else:
            raise ValueError("数据缺少 'Datetime' 或 'Date' 列，无法处理时间。")
    return df

def filter_data(df: pd.DataFrame, cities: list, start_date, end_date) -> pd.DataFrame:
    """
    按城市和日期范围筛选数据
    """
    df = ensure_datetime(df)
    filtered = df[
        df['Station'].isin(cities) &
        df['Date'].between(pd.to_datetime(start_date).date(), pd.to_datetime(end_date).date())
    ]
    return filtered


# --- 图表生成函数 ---
def make_dynamic_line(df: pd.DataFrame, pollutant: str) -> Timeline:
    """
    生成污染物日均动态排名折线图 (Timeline)
    """
    df = ensure_datetime(df)
    dates = sorted(df['Date'].dropna().unique())
    tl = Timeline(init_opts=opts.InitOpts(width="800px", height="400px"))
    tl.add_schema(play_interval=1000, is_timeline_show=True, pos_bottom="0")

    for d in dates:
        sub = df[df['Date'] == d]
        avg = sub.groupby('Station')[pollutant].mean().reset_index()
        avg = avg.dropna(subset=[pollutant])
        if avg.empty:
            continue
        line = (
            Line()
            .add_xaxis(avg['Station'].tolist())
            .add_yaxis(pollutant, avg[pollutant].round(2).tolist(), label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
                title_opts=opts.TitleOpts(title=f"{d} {pollutant} 动态排名"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                datazoom_opts=[opts.DataZoomOpts()],
                visualmap_opts=opts.VisualMapOpts(is_show=False)
            )
            .set_colors(PALETTE)
        )
        tl.add(line, time_point=str(d))
    return tl


def make_line_trend(df: pd.DataFrame, pollutant: str) -> Line:
    """
    生成污染物日均趋势折线图
    """
    df = ensure_datetime(df)
    df[pollutant] = pd.to_numeric(df[pollutant], errors='coerce')
    daily = df.groupby('Date')[pollutant].mean().reset_index()
    daily = daily.dropna(subset=[pollutant])
    if daily.empty:
        daily = pd.DataFrame({'Date': [], pollutant: []})
    line = (
        Line()
        .add_xaxis(daily['Date'].astype(str).tolist())
        .add_yaxis(pollutant, daily[pollutant].fillna(0).tolist(), is_smooth=True)
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{pollutant} 日均趋势"),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            xaxis_opts=opts.AxisOpts(type_="category", name="日期"),
            yaxis_opts=opts.AxisOpts(type_="value", name=pollutant),
            datazoom_opts=[opts.DataZoomOpts()]
        )
        .set_colors(PALETTE)
    )
    return line

def make_multi_pollutant_trend(df: pd.DataFrame, pollutants: list) -> Line:
    """
    多污染物日均趋势折线图
    """
    df['Date'] = pd.to_datetime(df.get('Datetime', df['Date'])).dt.date
    line = Line()
    dates = sorted(df['Date'].unique())
    line.add_xaxis([str(d) for d in dates])
    for pollutant in pollutants:
        if pollutant in df.columns:
            daily_mean = df.groupby('Date')[pollutant].mean().reindex(dates, fill_value=np.nan).fillna(0)
            line.add_yaxis(
                pollutant,
                daily_mean.round(2).tolist(),
                is_smooth=True,
                label_opts=opts.LabelOpts(is_show=False)
            )
    line.set_global_opts(
        title_opts=opts.TitleOpts(title="多污染物日均趋势"),
        tooltip_opts=opts.TooltipOpts(trigger="axis"),
        xaxis_opts=opts.AxisOpts(type_="category", name="日期"),
        yaxis_opts=opts.AxisOpts(type_="value", name="污染物浓度"),
        legend_opts=opts.LegendOpts(pos_top="5%"),
        datazoom_opts=[opts.DataZoomOpts()]
    ).set_colors(PALETTE)
    return line


def make_aqi_rank_chart(df: pd.DataFrame, pollutant: str) -> Bar:
    """
    生成污染物平均值排名柱状图
    """
    df = df.copy()
    df[pollutant] = pd.to_numeric(df[pollutant], errors='coerce')
    avg = df.groupby('Station')[pollutant].mean().sort_values(ascending=False).reset_index()
    bar = (
        Bar()
        .add_xaxis(avg['Station'].tolist())
        .add_yaxis("平均值", avg[pollutant].round(2).tolist())
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{pollutant} 平均排名"),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            datazoom_opts=[opts.DataZoomOpts()]
        )
        .set_colors(PALETTE)
    )
    return bar


from collections import Counter

def make_aqi_level_chart(df: pd.DataFrame, pollutants: List[str]) -> Bar:
    def classify(v):
        if pd.isna(v): return "缺失"
        elif v <= 50: return "优"
        elif v <= 100: return "良"
        elif v <= 150: return "轻度污染"
        elif v <= 200: return "中度污染"
        elif v <= 300: return "重度污染"
        else: return "严重污染"

    station_levels = {}

    for pollutant in pollutants:
        if pollutant not in df.columns:
            continue
        df.loc[:, pollutant] = pd.to_numeric(df[pollutant], errors='coerce')
        df = df.copy()
        df.loc[:, 'AQI级别'] = df[pollutant].apply(classify)

        counts = df.groupby(['Station', 'AQI级别']).size()
        for (station, level), count in counts.items():
            if station not in station_levels:
                station_levels[station] = Counter()
            station_levels[station][level] += count

    # 所有等级标签（固定顺序）
    level_order = ["优", "良", "轻度污染", "中度污染", "重度污染", "严重污染", "缺失"]

    stations = list(station_levels.keys())
    bar = Bar()
    bar.add_xaxis(stations)

    for level in level_order:
        y_data = [station_levels[station][level] for station in stations]
        bar.add_yaxis(level, y_data, stack="stack")

    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="各站点 AQI 等级分布（多污染物合并）"),
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
        yaxis_opts=opts.AxisOpts(name="累计天数"),
        legend_opts=opts.LegendOpts(pos_top="5%")
    )
    return bar


def ensure_datetime(df):
    """确保 DataFrame 中的 'Datetime' 列为 datetime 类型"""
    if 'Datetime' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['Datetime']):
        df['Datetime'] = pd.to_datetime(df['Datetime'])
    return df


def make_city_bubble_map(df, pollutants, mapbox_token=None):
    """
    创建城市空气质量气泡图（Plotly Mapbox）

    参数:
    df: 包含空气质量数据的 DataFrame，必须包含 'Station', 'Latitude', 'Longitude', 'Datetime' 和污染物列
    pollutants: 污染物列表（如 ['PM2.5', 'PM10']）
    mapbox_token: Mapbox API token（可选）
    """
    df = ensure_datetime(df)
    df2 = df.dropna(subset=['Latitude', 'Longitude'] + pollutants)
    grouped = df2.groupby('Station')[pollutants + ['Latitude', 'Longitude']].mean().reset_index()

    fig = go.Figure()
    buttons = []

    for i, p in enumerate(pollutants):
        raw = grouped[p].fillna(0)
        sizes = (raw - raw.min()) / (raw.max() - raw.min() + 1e-6) * 50 + 10

        trace = go.Scattermapbox(
            lat=grouped['Latitude'],
            lon=grouped['Longitude'],
            mode='markers',
            name=p,
            marker=dict(
                size=sizes,
                color=raw,
                colorscale='RdYlGn_r',
                showscale=True,
                colorbar=dict(title=p),
                cmin=raw.min(),
                cmax=raw.max()
            ),
            text=grouped['Station'],
            hovertemplate=f"<b>%{{text}}</b><br>{p}: %{{marker.color:.2f}}<br>Lat: %{{lat:.3f}}<br>Lon: %{{lon:.3f}}<extra></extra>",
            visible=(i == 0)
        )
        fig.add_trace(trace)

        buttons.append(dict(label=p,
                            method='update',
                            args=[{"visible": [j == i for j in range(len(pollutants))]},
                                  {"title": f"城市空气质量气泡图 - {p}"}]))

    fig.update_layout(
        mapbox_style="mapbox://styles/mapbox/streets-v11" if mapbox_token else "open-street-map",
        mapbox_accesstoken=mapbox_token,
        mapbox_zoom=4,
        mapbox_center={"lat": grouped['Latitude'].mean(), "lon": grouped['Longitude'].mean()},
        updatemenus=[dict(active=0, buttons=buttons, x=0.05, y=1.1)],
        title="城市空气质量气泡图",
        template="plotly_white",
        height=600
    )
    return fig

def make_heatmap_corr(df: pd.DataFrame) -> HeatMap:
    """
    生成污染物及气象指标相关性热力图
    """
    metrics = [c for c in DEFAULT_POLLUTANTS + DEFAULT_METEO if c in df.columns]
    vals = df[metrics].apply(pd.to_numeric, errors='coerce')
    corr = vals.corr().round(2)
    data = [[i, j, corr.iloc[j, i]] for i in range(len(metrics)) for j in range(len(metrics))]

    heat = (
        HeatMap()
        .add_xaxis(metrics)
        .add_yaxis("相关性", metrics, data, label_opts=opts.LabelOpts(is_show=True))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="相关性热力图"),
            visualmap_opts=opts.VisualMapOpts(min_=-1, max_=1)
        )
        .set_colors(PALETTE)
    )
    return heat


def make_stacked_bar(df: pd.DataFrame, pollutant: str) -> Bar:
    """
    生成污染物月均值堆叠柱状图
    """
    df[pollutant] = pd.to_numeric(df[pollutant], errors='coerce')
    df = ensure_datetime(df)
    monthly = df.set_index('Datetime').resample('ME')[pollutant].mean().fillna(0).reset_index()
    bar = (
        Bar()
        .add_xaxis(monthly['Datetime'].dt.strftime('%Y-%m').tolist())
        .add_yaxis(pollutant, monthly[pollutant].tolist(), stack="stack")
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{pollutant} 月均值堆叠图"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow"),
            datazoom_opts=[opts.DataZoomOpts()]
        )
        .set_colors(PALETTE)
    )
    return bar


def make_calendar_plot(df: pd.DataFrame, pollutant: str) -> Calendar:
    """
    生成污染物日历图，优化标签、配色和范围显示
    """
    df = ensure_datetime(df)
    df[pollutant] = pd.to_numeric(df[pollutant], errors='coerce')
    cal_data = df.groupby('Date')[pollutant].mean().reset_index()
    data_list = [[d.strftime('%Y-%m-%d'), float(v)] for d, v in zip(cal_data['Date'], cal_data[pollutant])]
    start = cal_data['Date'].min().strftime('%Y-%m-%d')
    end = cal_data['Date'].max().strftime('%Y-%m-%d')
    cal = (
        Calendar(init_opts=opts.InitOpts(width="800px", height="300px"))
        .add("日均值", data_list, calendar_opts=opts.CalendarOpts(
            range_=[start, end], cell_size=[20, 'auto'], orient='horizontal'
        ))
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{pollutant} 日历图"),
            visualmap_opts=opts.VisualMapOpts(min_=min(v for _, v in data_list), max_=max(v for _, v in data_list), range_color=PALETTE)
        )
    )
    return cal


def make_3d_surface(df: pd.DataFrame, pollutant: str) -> Surface3D:
    """
    生成污染物按月和小时分布的3D表面图
    """
    df = ensure_datetime(df)
    df[pollutant] = pd.to_numeric(df[pollutant], errors='coerce')
    df['Month'] = df['Datetime'].dt.month
    df['Hour'] = df['Datetime'].dt.hour
    arr = df[['Month', 'Hour', pollutant]].dropna().values.tolist()

    surf = (
        Surface3D()
        .add("3D 表面", arr,
             xaxis3d_opts=opts.Axis3DOpts(name="Month"),
             yaxis3d_opts=opts.Axis3DOpts(name="Hour"),
             zaxis3d_opts=opts.Axis3DOpts(name=pollutant))
        .set_global_opts(title_opts=opts.TitleOpts(title="月-时 分布 3D 表面图"))
        .set_colors(PALETTE)
    )
    return surf


# --- 辅助数据计算函数 ---
def get_rank_timeseries(df: pd.DataFrame, pollutant: str) -> pd.DataFrame:
    """
    获取指定污染物按日期和城市的透视表，用于动态排名分析
    """
    df = ensure_datetime(df)
    df[pollutant] = pd.to_numeric(df[pollutant], errors='coerce')
    pivot = df.pivot_table(index='Date', columns='Station', values=pollutant).fillna(0)
    return pivot

def iqr_anomaly_detection(df: pd.DataFrame, pollutants: list, multiplier=1.5) -> pd.DataFrame:
    anomalies = []
    for pollutant in pollutants:
        if pollutant not in df.columns:
            st.warning(f"警告: 数据中不包含污染物列 {pollutant}")
            continue
        series = df[pollutant].dropna()
        if series.ndim != 1:
            st.error(f"错误: {pollutant} 列不是一维数据，维度为 {series.ndim}")
            continue
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        mask = (series < lower_bound) | (series > upper_bound)
        outliers = df.loc[mask, ['Date', pollutant]].copy()
        outliers['Pollutant'] = pollutant
        outliers.rename(columns={pollutant: 'Value'}, inplace=True)
        anomalies.append(outliers)
    if anomalies:
        return pd.concat(anomalies).reset_index(drop=True)
    else:
        return pd.DataFrame(columns=['Date', 'Value', 'Pollutant'])


def get_daily_mean(df: pd.DataFrame, pollutants: Union[str, List[str]]) -> pd.DataFrame:
    """
    获取指定污染物的日均值数据。
    支持单个污染物（返回2列DataFrame）或多个污染物（返回多列）。
    """
    df = ensure_datetime(df)
    if isinstance(pollutants, str):
        pollutants = [pollutants]

    for pollutant in pollutants:
        df[pollutant] = pd.to_numeric(df[pollutant], errors='coerce')

    daily = df.groupby('Date')[pollutants].mean().reset_index()
    return daily

def calculate_composite_aqi(df: pd.DataFrame, pollutants: list) -> pd.Series:
    """
    根据多污染物计算综合 AQI（简化示例，实际需要符合国家标准）
    这里示例用最大值代表综合AQI
    """
    df = df.copy()
    for p in pollutants:
        df[p] = pd.to_numeric(df[p], errors='coerce').fillna(0)
    composite = df[pollutants].max(axis=1)
    return composite

