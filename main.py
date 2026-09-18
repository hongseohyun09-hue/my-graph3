# ── 그래프 2. 장르 안의 영화 (트리맵) ──
st.header("2. 장르 안의 영화 (트리맵)")

fig2 = px.treemap(
    df,
    path=["장르", "movieNm"],
    values="total_audi",
    custom_data=["movieNm", "total_audi"]
)

fig2.update_traces(
    hovertemplate="<b>영화명: %{customdata[0]}</b><br>총 관객: %{customdata[1]:,}명<extra></extra>"
)

st.plotly_chart(fig2, width="stretch")
st.caption("이 그래프로 알 수 있는 것: 장르별로 어떤 영화의 총 관객이 많은지 한눈에 비교할 수 있다.")
