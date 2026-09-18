import streamlit as st
import requests
from datetime import date, timedelta

st.set_page_config(
    page_title="영화 가설 검증",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 가설 검증")
st.write("원하는 날짜의 일별 박스오피스 TOP 10을 확인해 보세요.")

# -----------------------------
# KOBIS API 설정
# -----------------------------
try:
    KOBIS_KEY = st.secrets["KOBIS_KEY"]
except Exception:
    st.error("KOBIS_KEY가 Streamlit Secrets에 설정되어 있지 않습니다.")
    st.stop()

API_URL = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"

# -----------------------------
# 날짜 입력
# -----------------------------
today = date.today()

col1, col2 = st.columns(2)

with col1:
    month = st.number_input(
        "월",
        min_value=1,
        max_value=12,
        value=today.month,
        step=1
    )

with col2:
    day = st.number_input(
        "일",
        min_value=1,
        max_value=31,
        value=today.day,
        step=1
    )

# 날짜가 실제로 존재하는지 확인
try:
    selected_date = date(today.year, int(month), int(day))
except ValueError:
    st.error("존재하지 않는 날짜입니다. 다시 입력해 주세요.")
    st.stop()

# 미래 날짜 방지
if selected_date >= today:
    st.warning("오늘 이후의 날짜는 조회할 수 없습니다.")
    st.stop()

target_date = selected_date.strftime("%Y%m%d")

st.info(
    f"📅 조회 날짜: {selected_date.strftime('%Y년 %m월 %d일')}"
)

# -----------------------------
# KOBIS API 호출
# -----------------------------
@st.cache_data(ttl=3600)
def get_boxoffice(target_date):
    params = {
        "key": KOBIS_KEY,
        "targetDt": target_date
    }

    response = requests.get(
        API_URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    return data["boxOfficeResult"]["dailyBoxOfficeList"]


if st.button("🎬 박스오피스 조회", use_container_width=True):

    try:
        movies = get_boxoffice(target_date)

        if not movies:
            st.warning("그날은 아직 집계 전입니다.")
            st.stop()

        # -----------------------------
        # 관객수를 숫자로 변환
        # -----------------------------
        rows = []

        for movie in movies[:10]:
            audience = int(movie["audiCnt"].replace(",", ""))

            rows.append({
                "순위": int(movie["rank"]),
                "영화명": movie["movieNm"],
                "관객수": audience,
                "개봉일": movie["openDt"],
                "누적관객": int(movie["audiAcc"].replace(",", "")),
                "스크린수": int(movie["scrnCnt"].replace(",", ""))
            })

        # -----------------------------
        # 표 출력
        # -----------------------------
        st.subheader(
            f"📊 {selected_date.strftime('%Y년 %m월 %d일')} 박스오피스 TOP 10"
        )

        st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True,
            column_config={
                "순위": st.column_config.NumberColumn(
                    "순위",
                    format="%d위"
                ),
                "관객수": st.column_config.NumberColumn(
                    "관객수",
                    format="%d명"
                ),
                "누적관객": st.column_config.NumberColumn(
                    "누적관객",
                    format="%d명"
                ),
                "스크린수": st.column_config.NumberColumn(
                    "스크린수",
                    format="%d개"
                )
            }
        )

    except requests.exceptions.RequestException:
        st.error("KOBIS API를 불러오는 중 오류가 발생했습니다.")

    except Exception as e:
        st.error(f"데이터를 처리하는 중 오류가 발생했습니다.")
