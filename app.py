import streamlit as st
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter
import pandas as pd

st.set_page_config(page_title="이미지 컬러 팔레트 추출기", layout="wide")

st.title("🎨 이미지 컬러 팔레트 추출기")
st.write("이미지를 업로드하고 추출하고 싶은 색상의 개수를 선택하세요.")

uploaded_file = st.file_uploader("이미지 파일을 업로드하세요 (JPG, PNG, JPEG)", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("업로드한 이미지")
        st.image(image, use_container_width=True)

    # [연산 최적화] 해상도 축소
    img_small = image.copy()
    img_small.thumbnail((300, 300))
    
    img_array = np.array(img_small)
    pixels = img_array.reshape(-1, 3)
    
    unique_colors_count = len(np.unique(pixels, axis=0))

    with col2:
        st.subheader("팔레트 설정")
        max_colors_limit = min(unique_colors_count, 30)
        
        n_colors = st.slider(
            "추출할 색상 개수 선택",
            min_value=1,
            max_value=max_colors_limit,
            value=min(5, max_colors_limit),
            help="1등은 가장 많이 쓰인 대표 색상이며, 마지막 순위는 상대적으로 적게 쓰인 색상입니다."
        )

        # K-Means 연산
        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=5)
        labels = kmeans.fit_predict(pixels)
        counts = Counter(labels)
        
        sorted_indices = [item[0] for item in counts.most_common()]
        palette = kmeans.cluster_centers_[sorted_indices].astype(int)
        
        st.write("### 추출된 컬러 팔레트")
        st.write("*(1번: 가장 많이 쓰인 색상 ➡️ 마지막: 상대적으로 적게 쓰인 색상)*")

        # 저장용 데이터 수집
        color_data = []
        hex_list = []

        for idx, color in enumerate(palette, start=1):
            r, g, b = color[0], color[1], color[2]
            hex_code = f"#{r:02x}{g:02x}{b:02x}".upper()
            percent = (counts[sorted_indices[idx-1]] / len(pixels)) * 100
            
            hex_list.append(hex_code)
            color_data.append({
                "순위": idx,
                "HEX": hex_code,
                "RGB": f"({r}, {g}, {b})",
                "비율(%)": round(percent, 2)
            })
            
            c1, c2, c3 = st.columns([1, 3, 2])
            with c1:
                st.markdown(
                    f'<div style="background-color: {hex_code}; width: 100%; height: 35px; border-radius: 5px; border: 1px solid #ddd;"></div>',
                    unsafe_allow_html=True
                )
            with c2:
                st.write(f"**{idx}위**: `{hex_code}` | RGB`({r}, {g}, {b})`")
            with c3:
                st.write(f"비율: `{percent:.1f}%`")

        st.divider()
        st.subheader("💾 팔레트 내보내기 & 저장")

        # 1. 전체 HEX 코드 한 번에 복사하기
        all_hex_text = ", ".join(hex_list)
        st.text_input("전체 HEX 코드 (한 번에 복사가능)", value=all_hex_text)

        # 2. 파일 다운로드 버튼 (CSV / TXT)
        df_palette = pd.DataFrame(color_data)
        csv_data = df_palette.to_csv(index=False).encode('utf-8-sig')
        
        txt_content = "=== 추출된 컬러 팔레트 ===\n"
        for item in color_data:
            txt_content += f"{item['순위']}위: HEX {item['HEX']} | RGB {item['RGB']} | 비율 {item['비율(%)']}%\n"

        d_col1, d_col2 = st.columns(2)
        with d_col1:
            st.download_button(
                label="📄 TXT 파일로 다운로드",
                data=txt_content,
                file_name="color_palette.txt",
                mime="text/plain",
                use_container_width=True
            )
        with d_col2:
            st.download_button(
                label="📊 CSV (엑셀) 파일로 다운로드",
                data=csv_data,
                file_name="color_palette.csv",
                mime="text/csv",
                use_container_width=True
            )
