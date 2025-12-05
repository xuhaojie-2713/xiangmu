#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
analysis.py

功能：
1. 读取 processed/air_quality_clean.csv
2. 描述性统计 → 输出 reports/descriptive_stats.csv
3. 相关性分析 → 输出 reports/correlation.csv
4. 聚类分析 (KMeans, n=3) → 输出 reports/clusters.csv & reports/cluster_centers.csv
"""

import os
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

INPUT_PATH      = os.path.join("../data", "processed", "china_50_cities.csv")
OUT_STATS       = os.path.join("reports", "descriptive_stats.csv")
OUT_CORR        = os.path.join("reports", "correlation.csv")
OUT_CLUSTERS    = os.path.join("reports", "clusters.csv")
OUT_CENTERS     = os.path.join("reports", "cluster_centers.csv")

def main():
    os.makedirs("reports", exist_ok=True)

    df = pd.read_csv(INPUT_PATH, parse_dates=['Datetime'])

    pollutants = ['CO(GT)','NMHC(GT)','C6H6(GT)','NOx(GT)','NO2(GT)']

    # 1. 描述性统计
    desc = df.groupby('Station')[pollutants].agg(['mean','median','std']).round(2)
    desc.to_csv(OUT_STATS)
    print(f"[analysis] 已输出描述性统计：{OUT_STATS}")

    # 2. 相关性分析
    corr = df[pollutants].corr().round(2)
    corr.to_csv(OUT_CORR)
    print(f"[analysis] 已输出相关性矩阵：{OUT_CORR}")

    # 3. 聚类分析
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[pollutants].fillna(0))
    kmeans = KMeans(n_clusters=3, random_state=42)
    df['Cluster'] = kmeans.fit_predict(X_scaled)

    df.to_csv(OUT_CLUSTERS, index=False)
    centers = pd.DataFrame(
        scaler.inverse_transform(kmeans.cluster_centers_),
        columns=pollutants
    ).round(2)
    centers['Cluster'] = centers.index
    centers.to_csv(OUT_CENTERS, index=False)
    print(f"[analysis] 已输出聚类结果：{OUT_CLUSTERS}")
    print(f"[analysis] 已输出聚类中心：{OUT_CENTERS}")

if __name__ == "__main__":
    main()
