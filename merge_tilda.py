#!/usr/bin/env python3
"""
Скрипт для объединения сайта Tilda в один HTML файл.
Встраивает все CSS, JS и изображения в base64.
"""

import os
import re
import base64
import mimetypes
from pathlib import Path
from urllib.parse import unquote

def get_mime_type(file_path):
    """Определяет MIME тип файла"""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or 'application/octet-stream'

def read_file_as_base64(file_path):
    """Читает файл и возвращает его в base64"""
    try:
        with open(file_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        print(f"Ошибка при чтении {file_path}: {e}")
        return None

def read_file_as_text(file_path, encoding='utf-8'):
    """Читает текстовый файл"""
    try:
        with open(file_path, encoding=encoding, errors='ignore') as f:
            return f.read()
    except Exception as e:
        print(f"Ошибка при чтении {file_path}: {e}")
        return None

def merge_tilda_site(source_html, base_dir, output_file):
    """
    Объединяет сайт Tilda в один HTML файл
    
    Args:
        source_html: путь к исходному HTML файлу
        base_dir: базовая директория с ресурсами
        output_file: путь к выходному файлу
    """
    print(f"Читаем исходный HTML: {source_html}")
    html_content = read_file_as_text(source_html)
    
    if not html_content:
        print("Не удалось прочитать исходный HTML файл")
        return False
    
    # Встраиваем CSS файлы
    print("\nВстраиваем CSS файлы...")
    css_pattern = r'<link[^>]*href=["\']([^"\']+\.css)["\'][^>]*>'
    
    def replace_css(match):
        css_path = match.group(1)
        # Убираем параметры URL
        css_path = css_path.split('?')[0]
        # Декодируем URL
        css_path = unquote(css_path)
        
        # Ищем файл
        full_path = None
        if css_path.startswith('http://') or css_path.startswith('https://'):
            print(f"  Пропускаем внешний CSS: {css_path}")
            return match.group(0)
        elif css_path.startswith('a_data/'):
            # Путь относительно папки с файлами
            css_path = css_path.replace('a_data/', '')
            full_path = os.path.join(base_dir, css_path)
        else:
            full_path = os.path.join(base_dir, css_path)
        
        if full_path and os.path.exists(full_path):
            print(f"  Встраиваем: {os.path.basename(full_path)}")
            css_content = read_file_as_text(full_path)
            if css_content:
                # Обрабатываем url() в CSS
                css_content = process_css_urls(css_content, base_dir, os.path.dirname(full_path))
                return f'<style type="text/css">\n{css_content}\n</style>'
        else:
            print(f"  Не найден: {css_path}")
        
        return match.group(0)
    
    html_content = re.sub(css_pattern, replace_css, html_content, flags=re.IGNORECASE)
    
    # Встраиваем JavaScript файлы
    print("\nВстраиваем JavaScript файлы...")
    js_pattern = r'<script[^>]*src=["\']([^"\']+\.js)["\'][^>]*>[\s\S]*?</script>'
    
    def replace_js(match):
        js_path = match.group(1)
        # Убираем параметры URL
        js_path = js_path.split('?')[0]
        # Декодируем URL
        js_path = unquote(js_path)
        
        # Ищем файл
        full_path = None
        if js_path.startswith('http://') or js_path.startswith('https://'):
            print(f"  Пропускаем внешний JS: {js_path}")
            return match.group(0)
        elif js_path.startswith('a_data/'):
            js_path = js_path.replace('a_data/', '')
            full_path = os.path.join(base_dir, js_path)
        else:
            full_path = os.path.join(base_dir, js_path)
        
        if full_path and os.path.exists(full_path):
            print(f"  Встраиваем: {os.path.basename(full_path)}")
            js_content = read_file_as_text(full_path)
            if js_content:
                attrs = re.search(r'<script([^>]*)src=', match.group(0))
                extra_attrs = attrs.group(1) if attrs else ''
                return f'<script{extra_attrs}>\n{js_content}\n</script>'
        else:
            print(f"  Не найден: {js_path}")
        
        return match.group(0)
    
    html_content = re.sub(js_pattern, replace_js, html_content, flags=re.IGNORECASE)
    
    # Встраиваем изображения
    print("\nВстраиваем изображения...")
    img_pattern = r'<img([^>]*)src=["\']([^"\']+)["\']([^>]*)>'
    
    def replace_img(match):
        before = match.group(1)
        img_path = match.group(2)
        after = match.group(3)
        
        # Убираем параметры URL
        img_path_clean = img_path.split('?')[0]
        img_path_clean = unquote(img_path_clean)
        
        if img_path_clean.startswith('data:'):
            return match.group(0)
        
        if img_path_clean.startswith('http://') or img_path_clean.startswith('https://'):
            print(f"  Пропускаем внешнее изображение: {img_path_clean}")
            return match.group(0)
        
        full_path = os.path.join(base_dir, img_path_clean)
        
        if os.path.exists(full_path):
            print(f"  Встраиваем: {os.path.basename(full_path)}")
            mime_type = get_mime_type(full_path)
            img_base64 = read_file_as_base64(full_path)
            if img_base64:
                return f'<img{before}src="data:{mime_type};base64,{img_base64}"{after}>'
        else:
            print(f"  Не найдено: {img_path_clean}")
        
        return match.group(0)
    
    html_content = re.sub(img_pattern, replace_img, html_content, flags=re.IGNORECASE)
    
    # Встраиваем background images в style атрибутах
    print("\nВстраиваем background изображения из style атрибутов...")
    style_bg_pattern = r'style=["\']([^"\']*url\([^)]+\)[^"\']*)["\']'
    
    def replace_style_bg(match):
        style_content = match.group(1)
        return f'style="{process_css_urls(style_content, base_dir, base_dir)}"'
    
    html_content = re.sub(style_bg_pattern, replace_style_bg, html_content, flags=re.IGNORECASE)
    
    # Удаляем внешние скрипты и ссылки на Tilda
    print("\nУдаляем ссылки на внешние ресурсы Tilda...")
    html_content = re.sub(r'<script[^>]*src=["\']https?://[^"\']*tilda[^"\']*["\'][^>]*>[\s\S]*?</script>', 
                          '', html_content, flags=re.IGNORECASE)
    
    # Сохраняем результат
    print(f"\nСохраняем результат в: {output_file}")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✓ Файл успешно создан!")
        print(f"✓ Размер: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB")
        return True
    except Exception as e:
        print(f"Ошибка при сохранении файла: {e}")
        return False

def process_css_urls(css_content, base_dir, css_dir):
    """Обрабатывает url() в CSS и встраивает изображения"""
    url_pattern = r'url\(["\']?([^"\')\s]+)["\']?\)'
    
    def replace_url(match):
        url = match.group(1)
        
        # Пропускаем data URI
        if url.startswith('data:'):
            return match.group(0)
        
        # Пропускаем абсолютные URL
        if url.startswith('http://') or url.startswith('https://'):
            return match.group(0)
        
        # Пропускаем пустые URL
        if not url or url == '#':
            return match.group(0)
        
        # Определяем полный путь к файлу
        if url.startswith('/'):
            full_path = os.path.join(base_dir, url.lstrip('/'))
        else:
            full_path = os.path.join(css_dir, url)
        
        full_path = os.path.normpath(full_path)
        
        # Если файл существует, встраиваем его
        if os.path.exists(full_path):
            mime_type = get_mime_type(full_path)
            file_base64 = read_file_as_base64(full_path)
            if file_base64:
                return f'url(data:{mime_type};base64,{file_base64})'
        
        return match.group(0)
    
    return re.sub(url_pattern, replace_url, css_content)

def main():
    # Настройка путей
    script_dir = Path(__file__).parent
    source_html = script_dir / "Tilda_ 7-я Конференция «Силаэдр»_files" / "a.htm"
    base_dir = script_dir / "Tilda_ 7-я Конференция «Силаэдр»_files"
    output_file = script_dir / "index.html"
    
    print("=" * 60)
    print("Объединение сайта Tilda в один HTML файл")
    print("=" * 60)
    
    if not os.path.exists(source_html):
        print(f"Ошибка: исходный файл не найден: {source_html}")
        return 1
    
    if not os.path.exists(base_dir):
        print(f"Ошибка: директория с ресурсами не найдена: {base_dir}")
        return 1
    
    success = merge_tilda_site(str(source_html), str(base_dir), str(output_file))
    
    if success:
        print("\n" + "=" * 60)
        print("✓ Готово! Сайт успешно объединен в один файл.")
        print(f"✓ Выходной файл: {output_file}")
        print("=" * 60)
        return 0
    else:
        print("\n✗ Произошла ошибка при объединении сайта")
        return 1

if __name__ == "__main__":
    exit(main())
