import streamlit as st
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import io
import base64
import fitz  # PyMuPDF
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import zipfile
from datetime import datetime

class PDFColorizer:
    def __init__(self):
        self.color_schemes = {
            "ビジネス": ["#1f4e79", "#4472c4", "#70ad47", "#ffc000", "#c5504b"],
            "エレガント": ["#2d3436", "#636e72", "#74b9ff", "#fd79a8", "#fdcb6e"],
            "モダン": ["#2c3e50", "#3498db", "#e74c3c", "#f39c12", "#9b59b6"],
            "ナチュラル": ["#27ae60", "#2ecc71", "#f1c40f", "#e67e22", "#95a5a6"]
        }
        
    def pdf_to_images(self, pdf_bytes):
        """PDFを画像に変換"""
        try:
            # PyMuPDFを使用してPDFを処理
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            images = []
            
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                # 高解像度で画像を取得
                mat = fitz.Matrix(3.0, 3.0)  # 3倍の解像度
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("ppm")
                img = Image.open(io.BytesIO(img_data))
                images.append(img)
            
            pdf_document.close()
            return images
        except Exception as e:
            st.error(f"PDF変換エラー: {e}")
            return []
    
    def enhance_contrast(self, image):
        """コントラストと明度を向上"""
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)
        
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.1)
        
        return image
    
    def detect_graph_areas(self, image):
        """矩形や枠線のある領域（グラフ・表・図）を検出"""
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # 矩形検出
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        graph_mask = np.zeros_like(gray, dtype=bool)
        
        # 矩形領域を検出
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:  # ある程度大きな領域
                # 矩形に近似
                approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
                if len(approx) >= 4:  # 四角形っぽい
                    cv2.fillPoly(graph_mask.astype(np.uint8), [contour], 1)
        
        # 直線検出も併用
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=20, maxLineGap=10)
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(graph_mask.astype(np.uint8), (x1, y1), (x2, y2), 1, 20)
        
        # 膨張処理
        kernel = np.ones((15, 15), np.uint8)
        graph_mask = cv2.dilate(graph_mask.astype(np.uint8), kernel, iterations=2).astype(bool)
        
        return graph_mask

    def detect_arrows(self, image):
        """矢印を検出"""
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # 三角形や矢印の形状を検出
        edges = cv2.Canny(gray, 100, 200)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        arrow_mask = np.zeros_like(gray, dtype=bool)
        for contour in contours:
            area = cv2.contourArea(contour)
            if 100 < area < 2000:  # 適度なサイズの図形
                approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
                if len(approx) >= 3:  # 三角形っぽい形
                    cv2.fillPoly(arrow_mask.astype(np.uint8), [contour], 1)
        
        return arrow_mask

    def detect_gold_elements(self, image):
        """ゴールド（黄色っぽい）要素を検出"""
        img_array = np.array(image)
        if len(img_array.shape) == 3:
            # カラー画像の場合、黄色っぽい領域を検出
            hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
            lower_yellow = np.array([15, 50, 50])
            upper_yellow = np.array([35, 255, 255])
            gold_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        else:
            # グレースケールの場合、明るい中間調を対象
            gray_array = np.array(image.convert('L'))
            gold_mask = (gray_array > 120) & (gray_array < 200)
            
        return gold_mask.astype(bool)

    def apply_color_mapping(self, image, color_scheme):
        """シンプルなグレー値ベースの配色変換"""
        img_array = np.array(image)
        
        if len(img_array.shape) == 3:
            gray_array = np.array(image.convert('L'))
        else:
            gray_array = img_array
            
        colored_img = np.zeros((gray_array.shape[0], gray_array.shape[1], 3), dtype=np.uint8)
        
        # 白い部分はそのまま保持
        white_mask = gray_array > 240
        colored_img[white_mask] = [255, 255, 255]
        
        # 黒い部分（テキスト）はそのまま保持
        black_mask = gray_array < 30
        colored_img[black_mask, 0] = gray_array[black_mask]
        colored_img[black_mask, 1] = gray_array[black_mask]
        colored_img[black_mask, 2] = gray_array[black_mask]
        
        # グレー値による配色
        # 薄いグレー（190-240）→ 薄い水色
        light_gray_mask = (gray_array >= 190) & (gray_array <= 240)
        colored_img[light_gray_mask, 0] = 230  # 薄い水色
        colored_img[light_gray_mask, 1] = 245
        colored_img[light_gray_mask, 2] = 255
        
        # 中間グレー（140-189）→ 中間水色
        mid_light_gray_mask = (gray_array >= 140) & (gray_array < 190)
        intensity = gray_array[mid_light_gray_mask] / 190.0
        colored_img[mid_light_gray_mask, 0] = (173 * intensity).astype(np.uint8)  # 水色
        colored_img[mid_light_gray_mask, 1] = (216 * intensity).astype(np.uint8)
        colored_img[mid_light_gray_mask, 2] = (230 * intensity).astype(np.uint8)
        
        # 中暗グレー（90-139）→ 暗い水色
        mid_dark_gray_mask = (gray_array >= 90) & (gray_array < 140)
        intensity = gray_array[mid_dark_gray_mask] / 150.0
        colored_img[mid_dark_gray_mask, 0] = (100 * intensity).astype(np.uint8)  # 暗い水色
        colored_img[mid_dark_gray_mask, 1] = (149 * intensity).astype(np.uint8)
        colored_img[mid_dark_gray_mask, 2] = (180 * intensity).astype(np.uint8)
        
        # 暗いグレー（30-89）→ 紺色またはグレー
        dark_gray_mask = (gray_array >= 30) & (gray_array < 90)
        # 暗い部分は基本的に紺色にする
        intensity = gray_array[dark_gray_mask] / 120.0
        colored_img[dark_gray_mask, 0] = (25 * intensity).astype(np.uint8)   # 紺色
        colored_img[dark_gray_mask, 1] = (25 * intensity).astype(np.uint8)
        colored_img[dark_gray_mask, 2] = (112 * intensity).astype(np.uint8)
            
        return Image.fromarray(colored_img)
    
    def detect_and_enhance_graphs(self, image):
        """グラフエリアを検出して装飾を追加"""
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # より控えめな直線検出
        edges = cv2.Canny(gray, 100, 200)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=150, minLineLength=100, maxLineGap=5)
        
        if lines is not None:
            # 長い直線のみを強調（グラフの軸と思われるもの）
            for line in lines:
                x1, y1, x2, y2 = line[0]
                length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                if length > 200:  # 長い線のみ
                    cv2.line(img_cv, (x1, y1), (x2, y2), (50, 100, 150), 2)
        
        return Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
    
    def add_luxury_effects(self, image):
        """高級感のある効果を追加"""
        # シャープネス向上
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.3)
        
        # 彩度向上
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.4)
        
        return image

def main():
    st.set_page_config(
        page_title="PDF カラフル変換ツール",
        page_icon="🎨",
        layout="wide"
    )
    
    st.title("🎨 PDF カラフル変換ツール")
    st.markdown("モノクロのパンフレットを色鮮やかで高級感のある仕上がりに変換します")
    
    colorizer = PDFColorizer()
    
    # サイドバー設定
    st.sidebar.header("設定")
    color_scheme = st.sidebar.selectbox(
        "カラースキーム",
        list(colorizer.color_schemes.keys())
    )
    
    enhance_graphs = st.sidebar.checkbox("グラフ装飾", value=True)
    add_luxury = st.sidebar.checkbox("高級感効果", value=True)
    
    # ファイルアップロード
    uploaded_file = st.file_uploader(
        "PDFファイルをアップロード",
        type=['pdf'],
        help="変換したいPDFファイルを選択してください"
    )
    
    if uploaded_file is not None:
        st.success("PDFが正常にアップロードされました！")
        
        # PDF処理
        with st.spinner("PDFを処理中..."):
            pdf_bytes = uploaded_file.read()
            images = colorizer.pdf_to_images(pdf_bytes)
        
        if images:
            st.success(f"{len(images)}ページの画像に変換されました")
            
            # 各ページを処理
            processed_images = []
            
            for i, img in enumerate(images):
                st.subheader(f"ページ {i+1}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**変換前**")
                    st.image(img, use_column_width=True)
                
                with col2:
                    st.write("**変換後**")
                    
                    # 画像処理
                    processed_img = colorizer.enhance_contrast(img)
                    processed_img = colorizer.apply_color_mapping(
                        processed_img, 
                        colorizer.color_schemes[color_scheme]
                    )
                    
                    if enhance_graphs:
                        processed_img = colorizer.detect_and_enhance_graphs(processed_img)
                    
                    if add_luxury:
                        processed_img = colorizer.add_luxury_effects(processed_img)
                    
                    st.image(processed_img, use_column_width=True)
                    processed_images.append(processed_img)
                
                st.markdown("---")
            
            # ダウンロードボタン
            if processed_images:
                st.subheader("ダウンロード")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**個別ダウンロード**")
                    for i, img in enumerate(processed_images):
                        img_buffer = io.BytesIO()
                        img.save(img_buffer, format='PNG', quality=95)
                        img_buffer.seek(0)
                        
                        st.download_button(
                            label=f"ページ {i+1}",
                            data=img_buffer.getvalue(),
                            file_name=f"colorized_page_{i+1}.png",
                            mime="image/png",
                            key=f"download_{i}"
                        )
                
                with col2:
                    st.write("**一括ダウンロード**")
                    
                    # ZIPファイル作成
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        for i, img in enumerate(processed_images):
                            img_buffer = io.BytesIO()
                            img.save(img_buffer, format='PNG', quality=95)
                            zip_file.writestr(f"colorized_page_{i+1}.png", img_buffer.getvalue())
                    
                    zip_buffer.seek(0)
                    
                    # 現在の日時でファイル名を生成
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    zip_filename = f"colorized_pdf_{timestamp}.zip"
                    
                    st.download_button(
                        label=f"全ページをZIPでダウンロード ({len(processed_images)}ページ)",
                        data=zip_buffer.getvalue(),
                        file_name=zip_filename,
                        mime="application/zip",
                        key="download_all"
                    )

if __name__ == "__main__":
    main()