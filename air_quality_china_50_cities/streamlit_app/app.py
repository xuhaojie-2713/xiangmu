import time
import os

import streamlit as st
import pandas as pd

from streamlit_echarts import st_pyecharts
from streamlit_folium import st_folium
import folium
from folium.plugins import TimestampedGeoJson
import plotly.io as pio
import plotly.graph_objects as go

from viz import (
    filter_data,
    make_dynamic_line,
    make_line_trend,
    make_multi_pollutant_trend,
    make_aqi_rank_chart,
    make_aqi_level_chart,
    make_city_bubble_map,
    #make_city_bubble_scatter,
    #make_map_timeline,
    make_heatmap_corr,
    make_stacked_bar,
    make_calendar_plot,
    make_3d_surface,
    iqr_anomaly_detection,
    get_daily_mean,
)

# 页面配置
st.set_page_config(
    page_title="空气质量可视化平台",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>
    .stApp {background-color:#F5F5F5;}
    .main .block-container {padding:1rem 2rem;}
</style>
""", unsafe_allow_html=True)

# 引入 Mapbox GL CSS
st.markdown(
    """
    <link href="https://api.mapbox.com/mapbox-gl-js/v2.3.1/mapbox-gl.css" rel="stylesheet"/>
    """,
    unsafe_allow_html=True,
)

# 城市气泡图展示函数
def display_bubble_map(df: pd.DataFrame, pollutants: list):
    st.subheader("🔵 城市空气质量气泡图")
    if df.empty:
        st.warning("⚠️ 无数据，请调整筛选条件。")
        return
    metrics = [p for p in pollutants if p in df.columns]
    if not metrics:
        st.error(f"未找到污染物列，请检查：{df.columns.tolist()}")
        return
    mode = st.radio("选择气泡图模式", ("Mapbox 地图", "普通散点图"))
    token = st.text_input("Mapbox Access Token（可选）", type="password") if mode == "Mapbox 地图" else None
    df2 = df.dropna(subset=["Latitude", "Longitude"] + metrics)
    if df2.empty:
        st.warning("⚠️ 无有效经纬度或污染物数据。")
        return
    if mode == "Mapbox 地图":
        fig = make_city_bubble_map(df2, metrics, token)
    else:
        fig = make_city_bubble_scatter(df2, metrics)
    if fig and fig.data:
        st.plotly_chart(fig, use_container_width=True)
        html = fig.to_html(full_html=False).encode('utf-8')
        st.download_button("下载 HTML", html, "bubble_map.html", "text/html")
        try:
            png = pio.to_image(fig, format="png", width=800, height=600, scale=2, engine="orca")
            st.download_button("下载 PNG", png, "bubble_map.png", "image/png")
        except Exception as e:
            st.warning(f"Orca 渲染失败：{e}")
    else:
        st.warning("⚠️ 数据不足，无法生成气泡图。")

# 数据加载
@st.cache_data(show_spinner=True)
def load_data():
    path = os.path.join(os.path.dirname(__file__), "data/processed/china_50_cities.csv")
    df = pd.read_csv(path, parse_dates=["Datetime"] )
    df["Date"] = df["Datetime"].dt.date
    df["Hour"] = pd.to_numeric(df.get("Hour",0), errors="coerce").fillna(0).astype(int)
    df["Station"] = df["Station"].astype(str)
    return df

df = load_data()

# 侧边栏筛选
st.sidebar.header("筛选条件")
cities = df["Station"].unique().tolist()
selected_cities = st.sidebar.multiselect("城市", cities, default=cities)
pollutants_all = ["CO(GT)","NMHC(GT)","C6H6(GT)","NOx(GT)","NO2(GT)"]
selected_pollutants = st.sidebar.multiselect("污染物", pollutants_all, default=[pollutants_all[0]])
date_min, date_max = df["Date"].min(), df["Date"].max()
date_range = st.sidebar.date_input("日期范围", [date_min,date_max], min_value=date_min, max_value=date_max)
# 时空地图粒度
agg = st.sidebar.radio("时空地图粒度", ["Daily","Hourly"])
aggregate = 'D' if agg=='Daily' else 'H'
# 动态时间
unique_dates = pd.to_datetime(sorted(df["Date"].unique()))
idx_min,idx_max=0,len(unique_dates)-1
st.session_state.setdefault('play',False)
st.session_state.setdefault('idx',idx_min)
date_idx=st.sidebar.slider("时间点",idx_min,idx_max,st.session_state.idx)
selected_date=unique_dates[date_idx].date()
if st.sidebar.button("▶️ 播放" if not st.session_state.play else "⏸️ 暂停"):
    st.session_state.play=not st.session_state.play
if st.session_state.play:
    st.session_state.idx = (st.session_state.idx + 1) % (idx_max + 1)
    time.sleep(0.5)
    # 自动刷新
    try:
        st.experimental_rerun()
    except AttributeError:
        pass
else:
    st.session_state.idx = date_idx
    st.session_state.idx=date_idx

# 数据过滤
filtered=filter_data(df, selected_cities, date_range[0], date_range[1])
filtered_date=filtered[filtered['Date']==selected_date]

# 主页面
st.title(f"🌍 空气质量可视化 - {selected_date}")
st.info(f"当前日期：{selected_date}")
st.markdown("---")
if not selected_cities: st.warning("请至少选择一个城市")
elif not selected_pollutants: st.warning("请至少选择一个污染物")
else:
    # 1. AQI 排名
    st.subheader("🏅 AQI 排名")
    for p in selected_pollutants:
        st.markdown(f"#### {p}")
        try:
            c=make_aqi_rank_chart(filtered_date,p)
            st_pyecharts(c)
            st.download_button(f"下载 {p}",c.render_embed().encode(),f"{p}_rank.html")
        except: st.error(f"{p} 排名失败")

    # 2. 单污染物趋势
    st.subheader("📈 单污染物趋势")
    sel=st.selectbox("污染物",pollutants_all)
    d=get_daily_mean(filtered,sel)
    l=make_line_trend(d,sel)
    a=iqr_anomaly_detection(d,[sel])
    st.write(f"异常点：{len(a)}")
    st.dataframe(a)
    st_pyecharts(l)
    st.download_button("下载趋势",l.render_embed().encode(),f"trend_{sel}.html")

    # 3. 多污染物对比
    st.subheader("📈 多污染物趋势对比")
    dm=get_daily_mean(filtered,selected_pollutants)
    ml=make_multi_pollutant_trend(dm,selected_pollutants)
    an=iqr_anomaly_detection(dm,selected_pollutants)
    st.write(f"异常点：{len(an)}")
    st.dataframe(an)
    st_pyecharts(ml)
    st.download_button("下载多趋势",ml.render_embed().encode(),"trend_multi.html")

    # 4. 堆叠 & 等级
    st.subheader("📊 月均堆叠")
    try:
        sb=make_stacked_bar(filtered,selected_pollutants[0])
        st_pyecharts(sb)
        st.download_button("下载堆叠",sb.render_embed().encode(),"stacked_bar.html")
    except: st.info("堆叠失败")
    st.subheader("🌈 AQI 等级")
    lv=make_aqi_level_chart(filtered_date,selected_pollutants)
    st_pyecharts(lv)
    st.download_button("下载等级",lv.render_embed().encode(),"aqi_level.html")

    #5. 气泡图
    st.subheader("🏙️ 城市空气质量气泡图")


    def make_city_bubble_map(df, pollutants):
        import plotly.graph_objects as go

        df2 = df.dropna(subset=['Latitude', 'Longitude'] + pollutants)
        grouped = df2.groupby('Station')[pollutants + ['Latitude', 'Longitude']].mean().reset_index()

        fig = go.Figure()
        buttons = []

        for i, p in enumerate(pollutants):
            raw = grouped[p].fillna(0)
            sizes = (raw - raw.min()) / (raw.max() - raw.min() + 1e-6) * 50 + 10

            fig.add_trace(go.Scattermapbox(
                lat=grouped['Latitude'],
                lon=grouped['Longitude'],
                mode='markers',
                name=p,
                marker=dict(
                    size=sizes,
                    color=raw,
                    colorscale='RdYlGn_r',
                    showscale=True,
                    colorbar=dict(title=p)
                ),
                text=grouped['Station'],
                hovertemplate=f"<b>%{{text}}</b><br>{p}: %{{marker.color:.2f}}<br>Lat: %{{lat:.3f}}<br>Lon: %{{lon:.3f}}<extra></extra>",
                visible=(i == 0)
            ))

            buttons.append(dict(label=p,
                                method='update',
                                args=[{"visible": [j == i for j in range(len(pollutants))]},
                                      {"title": f"城市空气质量气泡图 - {p}"}]))

        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox_zoom=6,
            mapbox_center={"lat": grouped['Latitude'].mean(), "lon": grouped['Longitude'].mean()},
            updatemenus=[dict(active=0, buttons=buttons)],
            title="城市空气质量气泡图",
            template="plotly_white",
            height=600
        )
        return fig
    bubble_fig = make_city_bubble_map(df, selected_pollutants)
    st.plotly_chart(bubble_fig, use_container_width=True)


    auto_play = st.session_state.play
    def make_map_timeline(df, pollutant, aggregate='D', auto_play=False):
        import folium
        from folium.plugins import TimestampedGeoJson

        df['Datetime'] = df['Datetime'].dt.to_period(aggregate).dt.to_timestamp()

        features = []
        for _, row in df.iterrows():
            if pd.isna(row[pollutant]) or pd.isna(row['Latitude']) or pd.isna(row['Longitude']):
                continue
            features.append({
                'type': 'Feature',
                'geometry': {'type': 'Point', 'coordinates': [row['Longitude'], row['Latitude']]},
                'properties': {
                    'time': row['Datetime'].strftime('%Y-%m-%dT%H:%M:%S'),
                    'popup': f"{row['Station']} {pollutant}: {row[pollutant]:.2f}",
                    'icon': 'circle',
                    'iconstyle': {
                        'fillColor': '#3186cc',
                        'fillOpacity': 0.7,
                        'radius': 6
                    }
                }
            })

        m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=6)
        TimestampedGeoJson(
            {'type': 'FeatureCollection', 'features': features},
            period=f'P1{aggregate}',
            add_last_point=True,
            auto_play=auto_play,
            loop=False,
            max_speed=1,
            loop_button=True,
            time_slider_drag_update=True
        ).add_to(m)
        return m

    # 调用函数时传入 auto_play 参数
    tl_map = make_map_timeline(
        df=df,
        pollutant=selected_pollutants[0],
        aggregate=aggregate,
        auto_play=auto_play  # 确保这里传入了 auto_play 参数
    )

    # 使用 streamlit-folium 显示地图
    st_data = st_folium(tl_map, width=800, height=600)

    # 提供下载地图的选项
    html_map = tl_map.get_root().render()
    st.download_button(
        label="📥 下载时空地图（HTML）",
        data=html_map,
        file_name="map_timeline.html",
        mime="text/html"
    )
    # 6. 时空动态地图
    st.subheader("🗺️ 时空动态地图")


    # ✅ 修改后（正确）：
    tl_map = make_map_timeline(
        df=df,
        pollutant=selected_pollutants[0],
        auto_play=auto_play
    )

    # 7. 相关性 热力 日历 3D 相关性 热力 日历 3D
    st.subheader("🔥 相关性热力图")
    hm=make_heatmap_corr(filtered_date[selected_pollutants])
    st_pyecharts(hm)
    st.download_button("下载热力",hm.render_embed().encode(),"heatmap.html")
    st.subheader("📅 日历图")
    cl=make_calendar_plot(filtered,selected_pollutants[0])
    if cl.options.get('series') and cl.options['series'][0].get('data'):
        st_pyecharts(cl,height='400px',width='100%')
        st.download_button("下载日历",cl.render_embed().encode(),"calendar.html")
    else: st.info("无日历数据")
    st.subheader("📊 3D 表面")
    sf=make_3d_surface(filtered,selected_pollutants[0])
    st_pyecharts(sf,height='400px')
    st.download_button("下载3D",sf.render_embed().encode(),"surface3d.html")

    # 8. 导出
    st.markdown("---")
    st.download_button("下载CSV",filtered_date.to_csv(index=False).encode(),"data.csv")

st.markdown("---")
st.markdown("**说明：支持粒度选择及完整可视化**")
