
import streamlit as st
from googletrans import Translator, LANGUAGES
import time
import cv2
import numpy as np
from PIL import Image
import pytesseract
import re

# Initialize the translator
translator = Translator()

# Language mappings
SUPPORTED_LANGUAGES = {
    'English': 'en',
    'Chinese (Simplified)': 'zh-cn',
    'Spanish': 'es'
}

def suggest_improvements(text, language):
    """Suggest improvements for native-like language quality and structure"""
    suggestions = []
    
    # Basic text analysis
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    words = text.split()
    text_lower = text.lower()
    
    # Language-specific native writing suggestions
    if language == 'en':
        # Check for common non-native patterns
        if 'very much' in text_lower:
            suggestions.append("🎯 Replace 'very much' with stronger adjectives (e.g., 'extremely', 'tremendously')")
        
        if 'more better' in text_lower or 'more good' in text_lower:
            suggestions.append("✨ Use 'better' instead of 'more better', 'good' instead of 'more good'")
        
        # Check for overuse of "very"
        very_count = text_lower.count(' very ')
        if very_count > 2:
            suggestions.append("💎 Replace 'very + adjective' with stronger words (very big → enormous, very small → tiny)")
        
        # Check for passive voice overuse
        passive_indicators = ['was', 'were', 'been', 'being']
        passive_count = sum(text_lower.count(f' {word} ') for word in passive_indicators)
        if passive_count > len(sentences) * 0.3:
            suggestions.append("🎬 Use active voice more often (e.g., 'I wrote the report' vs 'The report was written by me')")
        
        # Check for repetitive sentence starters
        sentence_starters = [s.split()[0].lower() for s in sentences if s.split()]
        if len(sentence_starters) > 1:
            starter_freq = {}
            for starter in sentence_starters:
                starter_freq[starter] = starter_freq.get(starter, 0) + 1
            repeated_starters = [word for word, freq in starter_freq.items() if freq > 2]
            if repeated_starters:
                suggestions.append(f"🌊 Vary sentence beginnings. Overused starters: {', '.join(repeated_starters)}")
        
        # Check for informal contractions in formal text
        contractions = ["don't", "won't", "can't", "shouldn't", "wouldn't", "couldn't"]
        found_contractions = [c for c in contractions if c in text_lower]
        if found_contractions and len(text) > 200:  # Longer texts might be formal
            suggestions.append("👔 Consider expanding contractions for formal writing (don't → do not)")
        
        # Check for filler words
        fillers = ['like', 'you know', 'basically', 'actually', 'literally']
        filler_count = sum(text_lower.count(f' {filler} ') for filler in fillers)
        if filler_count > 3:
            suggestions.append("🎯 Reduce filler words ('like', 'basically', 'actually') for clearer communication")
    
    elif language == 'es':
        # Spanish-specific suggestions
        if 'muy muy' in text_lower:
            suggestions.append("✨ En lugar de 'muy muy', usa palabras más expresivas (extraordinario, increíble)")
        
        # Check for anglicisms
        anglicisms = ['email', 'ok', 'shopping', 'weekend']
        found_anglicisms = [a for a in anglicisms if a in text_lower]
        if found_anglicisms:
            suggestions.append(f"🇪🇸 Considera usar equivalentes en español: email→correo, ok→bien, shopping→compras")
        
        # Check for proper accent usage reminders
        if len([c for c in text if c.isalpha()]) > 50:  # Only for longer texts
            suggestions.append("📍 Recuerda usar acentos correctamente (más, está, sí, etc.)")
    
    elif language == 'zh-cn':
        # Chinese-specific suggestions
        # Check for proper punctuation (Chinese uses different punctuation)
        if ',' in text and '，' not in text:
            suggestions.append("📝 在中文中使用中文标点符号（，。！？）而不是英文标点")
        
        # Check for measure words reminder
        numbers_in_text = bool(re.search(r'\d+', text))
        if numbers_in_text:
            suggestions.append("🔢 记住使用量词（个、本、只、条等）在数字和名词之间")
    
    # Universal writing quality checks
    # Check for sentence length variety
    if sentences:
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_length = sum(sentence_lengths) / len(sentence_lengths)
        
        if avg_length < 5:
            suggestions.append("📏 Try using some longer, more detailed sentences for better flow")
        elif avg_length > 20:
            suggestions.append("📏 Consider breaking up some long sentences for easier reading")
        
        # Check for sentence length variety
        length_variety = max(sentence_lengths) - min(sentence_lengths) if len(sentence_lengths) > 1 else 0
        if length_variety < 5 and len(sentences) > 3:
            suggestions.append("🎵 Vary sentence lengths for more engaging rhythm")
    
    # Check for repetitive words (enhanced)
    word_freq = {}
    for word in words:
        clean_word = re.sub(r'[^\w]', '', word.lower())
        if len(clean_word) > 4:  # Focus on longer words
            word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
    
    repeated_words = [(word, freq) for word, freq in word_freq.items() if freq > 2]
    if repeated_words:
        word_list = [f"{word}({freq}x)" for word, freq in repeated_words[:3]]
        suggestions.append(f"🔄 Vary vocabulary to sound more natural: {', '.join(word_list)}")
    
    # Check for transition words
    transition_words = ['however', 'therefore', 'furthermore', 'moreover', 'additionally', 'consequently']
    if language == 'en':
        transition_count = sum(text_lower.count(f' {word} ') for word in transition_words)
        if transition_count == 0 and len(sentences) > 3:
            suggestions.append("🔗 Add transition words (however, therefore, furthermore) to connect ideas smoothly")
    
    # Check for specific improvement patterns
    if text_lower.count('and') > len(sentences):
        suggestions.append("🔗 Replace some 'and' connections with semicolons or periods for better flow")
    
    # Encourage more descriptive language
    basic_adjectives = ['good', 'bad', 'big', 'small', 'nice', 'great']
    basic_count = sum(text_lower.count(f' {adj} ') for adj in basic_adjectives)
    if basic_count > 2:
        suggestions.append("🎨 Use more specific adjectives (good→excellent, big→enormous, nice→delightful)")
    
    return suggestions

def extract_text_from_image(image):
    """Extract text from uploaded image using OCR"""
    try:
        # Convert PIL image to numpy array
        img_array = np.array(image)
        
        # Use pytesseract to extract text
        extracted_text = pytesseract.image_to_string(img_array)
        
        return extracted_text.strip() if extracted_text.strip() else "No text detected in image"
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def translate_text(text, source_lang, target_lang):
    """Translate text from source language to target language"""
    try:
        if source_lang == target_lang:
            return text
        
        result = translator.translate(text, src=source_lang, dest=target_lang)
        return result.text
    except Exception as e:
        return f"Translation error: {str(e)}"

def main():
    st.set_page_config(
        page_title="Advanced Multilingual Translator",
        page_icon="🌍",
        layout="wide"
    )
    
    st.title("🌍 Advanced Multilingual Translator")
    st.markdown("Translate between English, Chinese, and Spanish with quality suggestions and photo translation")
    
    # Add tabs for different input methods
    tab1, tab2 = st.tabs(["📝 Text Translation", "📷 Photo Translation"])
    
    with tab1:
        # Create two columns for input and output
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Input")
            source_language = st.selectbox(
                "From:",
                options=list(SUPPORTED_LANGUAGES.keys()),
                index=0,
                key="text_source"
            )
            
            input_text = st.text_area(
                "Enter text to translate:",
                height=200,
                placeholder="Type your text here...",
                key="text_input"
            )
            
            # Show text quality suggestions
            if input_text:
                source_code = SUPPORTED_LANGUAGES[source_language]
                suggestions = suggest_improvements(input_text, source_code)
                
                if suggestions:
                    st.subheader("💡 Quality Suggestions")
                    for suggestion in suggestions:
                        st.info(suggestion)
        
        with col2:
            st.subheader("Translation")
            target_language = st.selectbox(
                "To:",
                options=list(SUPPORTED_LANGUAGES.keys()),
                index=1,
                key="text_target"
            )
            
            # Translation output area
            if input_text:
                with st.spinner("Translating..."):
                    source_code = SUPPORTED_LANGUAGES[source_language]
                    target_code = SUPPORTED_LANGUAGES[target_language]
                    
                    translated_text = translate_text(input_text, source_code, target_code)
                    
                    st.text_area(
                        "Translation:",
                        value=translated_text,
                        height=200,
                        disabled=True
                    )
                    
                    # Show word count and character count
                    col_stats1, col_stats2 = st.columns(2)
                    with col_stats1:
                        st.metric("Words", len(input_text.split()))
                    with col_stats2:
                        st.metric("Characters", len(input_text))
            else:
                st.text_area(
                    "Translation:",
                    value="",
                    height=200,
                    disabled=True,
                    placeholder="Translation will appear here..."
                )
        
        # Add swap languages button
        col_center = st.columns([1, 1, 1])[1]
        with col_center:
            if st.button("🔄 Swap Languages", use_container_width=True, key="text_swap"):
                # Store current values in session state for swapping
                if 'swap_flag' not in st.session_state:
                    st.session_state.swap_flag = True
                st.rerun()
    
    with tab2:
        st.subheader("📷 Photo Translation")
        st.markdown("Upload an image with text to extract and translate")
        
        # Create columns for photo translation
        photo_col1, photo_col2 = st.columns(2)
        
        with photo_col1:
            st.subheader("Upload Image")
            
            # Image upload
            uploaded_file = st.file_uploader(
                "Choose an image file",
                type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
                help="Upload an image containing text to extract and translate"
            )
            
            if uploaded_file is not None:
                # Display the uploaded image
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_container_width=True)
                
                # Language selection for photo
                photo_source_lang = st.selectbox(
                    "Source language in image:",
                    options=list(SUPPORTED_LANGUAGES.keys()),
                    index=0,
                    key="photo_source"
                )
                
                photo_target_lang = st.selectbox(
                    "Translate to:",
                    options=list(SUPPORTED_LANGUAGES.keys()),
                    index=1,
                    key="photo_target"
                )
                
                if st.button("🔍 Extract & Translate Text", use_container_width=True):
                    with st.spinner("Extracting text from image..."):
                        # Extract text from image
                        extracted_text = extract_text_from_image(image)
                        
                        if extracted_text and "No text detected" not in extracted_text and "Error" not in extracted_text:
                            st.session_state.extracted_text = extracted_text
                            st.session_state.photo_source_code = SUPPORTED_LANGUAGES[photo_source_lang]
                            st.session_state.photo_target_code = SUPPORTED_LANGUAGES[photo_target_lang]
        
        with photo_col2:
            st.subheader("Extracted Text & Translation")
            
            if hasattr(st.session_state, 'extracted_text'):
                # Show extracted text
                st.text_area(
                    "Extracted Text:",
                    value=st.session_state.extracted_text,
                    height=150,
                    disabled=True
                )
                
                # Show translation
                with st.spinner("Translating extracted text..."):
                    translated_photo_text = translate_text(
                        st.session_state.extracted_text,
                        st.session_state.photo_source_code,
                        st.session_state.photo_target_code
                    )
                    
                    st.text_area(
                        "Translation:",
                        value=translated_photo_text,
                        height=150,
                        disabled=True
                    )
                
                # Show quality suggestions for extracted text
                suggestions = suggest_improvements(st.session_state.extracted_text, st.session_state.photo_source_code)
                if suggestions:
                    st.subheader("💡 Text Quality Suggestions")
                    for suggestion in suggestions:
                        st.info(suggestion)
            else:
                st.info("Upload an image and click 'Extract & Translate Text' to see results here")
    
    # Language information
    st.markdown("---")
    st.markdown("### Supported Languages")
    cols = st.columns(3)
    
    with cols[0]:
        st.info("🇺🇸 **English**\nInternational language")
    
    with cols[1]:
        st.info("🇨🇳 **Chinese (Simplified)**\n中文简体")
    
    with cols[2]:
        st.info("🇪🇸 **Spanish**\nEspañol")
    
    # Usage instructions
    with st.expander("📖 How to use"):
        st.markdown("""
        ### Text Translation
        1. **Select source language** from the "From" dropdown
        2. **Enter your text** in the input area
        3. **Select target language** from the "To" dropdown
        4. **View translation** and quality suggestions
        5. **Use swap button** to quickly reverse language direction
        
        ### Photo Translation
        1. **Upload an image** containing text
        2. **Select source and target languages**
        3. **Click 'Extract & Translate Text'** to process
        4. **View extracted text and translation**
        
        ### Quality Features
        - **Text suggestions** for better writing structure
        - **Word and character counts** for text analysis
        - **OCR text extraction** from images
        - **Multi-language support** for all features
        
        **Supported translations:**
        - English ↔ Chinese ↔ Spanish
        - Any combination between the three languages
        """)

if __name__ == "__main__":
    main()
