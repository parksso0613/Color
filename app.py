import streamlit as st
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter

# 페이지 기본 설정
st.set_page_config(page_title="이미지 컬러 팔레트 추출기", layout="wide")

st.title("🎨 이미지 컬러 팔레트 추출기")
st.write("이미지를 업로드하고 추출하고 싶은 색상의 개수를 선택하세요.")

# 1. 파일 업로드
uploaded_file = st.file_uploader("이미지 파일을 업로드하세요 (JPG, PNG, JPEG)", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # 이미지 불러오기 및 디스플레이
    image = Image.open(uploaded_file).convert("RGB")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("업로드한 이미지")
        st.image(image, use_container_width=True)

    # 이미지 데이터 변환 (2D 배열로 변환)
    img_array = np.array(image)
    pixels = img_array.reshape(-1, 3)
    
    # 중복 제거된 고유 색상 개수 파악 (최대 선택 가능한 색상 수 제한용)
    unique_colors_count = len(np.unique(pixels, axis=0))

    with col2:
        st.subheader("팔레트 설정")
        # 색상 개수 선택 (1부터 고유 색상 전체 개수까지 설정 가능, 기본값 최대 20개 권장)
        max_colors_limit = min(unique_colors_count, 50)  # 연산 속도를 위해 UI slider 상한은 50 추천
        
        n_colors = st.slider(
            "추출할 색상 개수 선택",
            min_value=1,
            max_value=max_colors_limit,
            value=min(5, max_colors_limit),
            help="1등은 가장 많이 쓰인 대표 색상이며, 마지막 순위는 상대적으로 적게 쓰인 색상입니다."
        )

        # K-Means를 통한 주요 색상 추출 및 빈도 계산
        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        labels = kmeans.fit_predict(pixels)
        counts = Counter(labels)
        
        # 빈도수가 높은 순서대로 정렬 (가장 많이 쓰인 색상 -> 가장 적게 쓰인 색상)
        sorted_indices = [item[0] for item in counts.most_common()]
        palette = kmeans.cluster_centers_[sorted_indices].astype(int)
        
        st.write("### 추출된 컬러 팔레트")
        st.write("*(1번: 가장 많이 쓰인 색상 ➡️ 마지막: 상대적으로 적게 쓰인 색상)*")

        # 팔레트 시각화 및 HEX 코드 표시
        for idx, color in enumerate(palette, start=1):
            hex_code = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
            percent = (counts[sorted_indices[idx-1]] / len(pixels)) * 100
            
            # 색상 칩과 HEX 코드 표시
            c1, c2, c3 = st.columns([1, 3, 2])
            with c1:
                st.markdown(
                    f'<div style="background-color: {hex_code}; width: 100%; height: 35px; border-radius: 5px; border: 1px solid #ddd;"></div>',
                    unsafe_allow_html=True
                )
            with c2:
                st.write(f"**{idx}위**: `{hex_code.upper()}`")
            with c3:
                st.write(f"비율: `{percent:.1f}%`")
