import streamlit as st
import pdf2image
from PIL import Image
import pytesseract
from pytesseract import Output, TesseractError
from functions import convert_pdf_to_txt_pages, convert_pdf_to_txt_file, save_pages, displayPDF, images_to_txt

st.set_page_config(page_title="PDF to Text")


html_temp = """
            <div style="background-color:{};padding:1px">
            
            </div>
            """

# st.markdown("""
#     ## :outbox_tray: Text data extractor: PDF to Text
    
# """)
# st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"),unsafe_allow_html=True)
st.markdown("""
    ## Text data extractor: PDF to Text
    
""")
languages = {
    'English': 'eng',
    'French': 'fra',
    'Arabic': 'ara',
    'Spanish': 'spa',
}

with st.sidebar:
    st.title(":outbox_tray: PDF to Text")
    textOutput = st.selectbox(
        "How do you want your output text?",
        ('One text file (.txt)', 'Text file per page (ZIP)'))
    ocr_box = st.checkbox('Enable OCR (scanned document)')
    
    st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"),unsafe_allow_html=True)
    st.markdown("""
    # How does it work?
    Simply load your PDF and convert it to single-page or multi-page text.
    """)
    st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"),unsafe_allow_html=True)
    st.markdown("""
    Made by [Aman Jain](https://github.com/Amanjain00) 
    """)
    st.markdown(
        """
        <a href="https://www.linkedin.com/in/aman-jain2003" target="_blank">
        <img src="data:image/png;base64,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" alt="LinkedIn" height="30" width="150 ">
        </a>
        """,
        unsafe_allow_html=True,
    )
    

pdf_file = st.file_uploader("Load your PDF", type=['pdf', 'png', 'jpg'])
hide="""
<style>
footer{
	visibility: hidden;
    	position: relative;
}
.viewerBadge_container__1QSob{
  	visibility: hidden;
}
#MainMenu{
	visibility: hidden;
}
<style>
"""
st.markdown(hide, unsafe_allow_html=True)
if pdf_file:
    path = pdf_file.read()
    file_extension = pdf_file.name.split(".")[-1]
    
    if file_extension == "pdf":
        # display document
        with st.expander("Display document"):
            displayPDF(path)
        if ocr_box:
            option = st.selectbox('Select the document language', list(languages.keys()))
        # pdf to text
        if textOutput == 'One text file (.txt)':
            if ocr_box:
                texts, nbPages = images_to_txt(path, languages[option])
                totalPages = "Pages: "+str(nbPages)+" in total"
                text_data_f = "\n\n".join(texts)
            else:
                text_data_f, nbPages = convert_pdf_to_txt_file(pdf_file)
                totalPages = "Pages: "+str(nbPages)+" in total"

            st.info(totalPages)
            st.download_button("Download txt file", text_data_f)
        else:
            if ocr_box:
                text_data, nbPages = images_to_txt(path, languages[option])
                totalPages = "Pages: "+str(nbPages)+" in total"
            else:
                text_data, nbPages = convert_pdf_to_txt_pages(pdf_file)
                totalPages = "Pages: "+str(nbPages)+" in total"
            st.info(totalPages)
            zipPath = save_pages(text_data)
            # download text data   
            with open(zipPath, "rb") as fp:
                btn = st.download_button(
                    label="Download ZIP (txt)",
                    data=fp,
                    file_name="pdf_to_txt.zip",
                    mime="application/zip"
                )
    else:
        option = st.selectbox("What's the language of the text in the image?", list(languages.keys()))
        pil_image = Image.open(pdf_file)
        text = pytesseract.image_to_string(pil_image, lang=languages[option])
        col1, col2 = st.columns(2)
        with col1:
            with st.expander("Display Image"):
                st.image(pdf_file)
        with col2:
            with st.expander("Display Text"):
                st.info(text)
        st.download_button("Download txt file", text)

    st.markdown('''
    <a target="_blank" style="color: black" href="#">
        <button class="btn">
            Spread the word!
        </button>
    </a>
    <style>
    .btn{
        display: inline-flex;
        -moz-box-align: center;
        align-items: center;
        -moz-box-pack: center;
        justify-content: center;
        font-weight: 400;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        margin: 0px;
        line-height: 1.6;
        color: rgb(49, 51, 63);
        background-color: #fff;
        width: auto;
        user-select: none;
        border: 1px solid rgba(49, 51, 63, 0.2);
        }
    .btn:hover{
        color: #00acee;
        background-color: #fff;
        border: 1px solid #00acee;
    }
    </style>
    ''',
    unsafe_allow_html=True
    )
    
