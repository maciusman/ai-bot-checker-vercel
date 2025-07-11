# api/bot_checker.py

from flask import Flask, request, jsonify
import requests
import time
import json
import re
from datetime import datetime
from urllib.parse import urlparse

# Tworzymy aplikację Flask, która będzie naszym serwerem API
app = Flask(__name__)

# --- CAŁY TWÓJ ORYGINALNY KOD ZNAJDUJE SIĘ PONIŻEJ ---
# (z drobnymi zmianami, by nie używać `print`, tylko zwracać stringi)

TOP_AI_BOTS = {
    "Human-Chrome": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "GPTBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.0; +https://openai.com/gptbot)",
    "ChatGPT-User": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ChatGPT-User/1.0; +https://openai.com/bot",
    "PerplexityBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)",
    "ClaudeBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ClaudeBot/1.0; +claude.ai)",
    "GoogleBot": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
}

# --- FUNKCJE POZOSTAJĄ PRAWIE BEZ ZMIAN ---
# (Kopiuję cały środek, bo jest dobrze napisany)

def quick_bot_check(url, timeout=8):
    report_lines = []
    report_lines.append(f"🤖 AI Bot Accessibility Check v2")
    report_lines.append(f"🌐 Testing: {url}")
    report_lines.append("=" * 70)
    
    results = {}
    baseline_content = None
    baseline_size = 0
    baseline_seo = None
    
    for bot_name, user_agent in TOP_AI_BOTS.items():
        line = f"Checking {bot_name}... "
        
        try:
            headers = {
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }
            
            start_time = time.time()
            response = requests.get(url, headers=headers, timeout=timeout)
            end_time = time.time()
            
            content = response.text
            content_size = len(content)
            
            if bot_name == "Human-Chrome":
                baseline_content = content
                baseline_size = content_size
            
            seo_elements = extract_seo_elements(content)
            html_quality = analyze_html_structure(content)
            structured_data = analyze_structured_data_simple(content)
            
            if bot_name == "Human-Chrome":
                baseline_seo = seo_elements
            
            results[bot_name] = {
                'status_code': response.status_code, 'content_size': content_size,
                'html_quality': html_quality, 'seo_elements': seo_elements,
                'structured_data': structured_data, 'accessible': response.status_code == 200,
            }
            
            status = "✅" if response.status_code == 200 else "❌"
            line += f"{status} {response.status_code} ({content_size} chars)"
            report_lines.append(line)
            
        except requests.exceptions.RequestException as e:
            results[bot_name] = {'error': str(e), 'accessible': False}
            line += f"❌ ERROR: {type(e).__name__}"
            report_lines.append(line)
        
        time.sleep(0.5)
    
    if baseline_content and baseline_seo:
        calculate_enhanced_ai_scores(results, baseline_size, baseline_seo)
    
    # Zwracamy wyniki i gotowy fragment raportu
    return results, "\n".join(report_lines)

# Reszta funkcji jest taka sama, tylko te generujące raport będą zwracać tekst
# (skopiowałem i zaadaptowałem kod z poprzedniej odpowiedzi, bo był już do tego gotowy)
def extract_seo_elements(content):
    if not content: return {'title': '', 'description': '', 'h1': '', 'h1_count': 0}
    title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else ''
    desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', content, re.IGNORECASE)
    if not desc_match: desc_match = re.search(r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*name=["\']description["\']', content, re.IGNORECASE)
    description = desc_match.group(1).strip() if desc_match else ''
    h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', content, re.IGNORECASE | re.DOTALL)
    h1 = h1_match.group(1).strip() if h1_match else ''
    h1_count = len(re.findall(r'<h1[^>]*>', content, re.IGNORECASE))
    return {'title': clean_text(title),'description': clean_text(description),'h1': clean_text(h1),'h1_count': h1_count}
def clean_text(text):
    if not text: return ''
    text = text.replace('&', '&').replace('<', '<').replace('>', '>').replace('"', '"').replace(''', "'")
    return re.sub(r'\s+', ' ', text).strip()
def analyze_structured_data_simple(content):
    if not content: return {'has_structured_data': False, 'optimization_potential': True}
    has_json_ld = bool(re.search(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>', content, re.IGNORECASE))
    has_microdata = bool(re.search(r'itemscope|itemprop|itemtype', content, re.IGNORECASE))
    has_schema = 'schema.org' in content.lower()
    return {'has_structured_data': has_json_ld or has_microdata or has_schema, 'optimization_potential': True}
def analyze_html_structure(content):
    if not content: return {'score': 0, 'elements': [], 'percentage': 0}
    score = 0
    checks = [('title', r'<title'), ('meta_description', r'name=["\']description'), ('h1', r'<h1'), ('h2', r'<h2'), ('p', r'<p'), ('a', r'<a'), ('img', r'<img'), ('nav', r'<nav'), ('main', r'<main'), ('article', r'<article')]
    for _, pattern in checks:
        if re.search(pattern, content, re.IGNORECASE): score += 1
    return {'score': score, 'max_score': len(checks), 'percentage': round((score / len(checks)) * 100)}
def calculate_enhanced_ai_scores(results, baseline_size, baseline_seo):
    for bot_name, result in results.items():
        if bot_name == "Human-Chrome" or 'error' in result: continue
        size_score = min(result['content_size'] / baseline_size, 1.0) if baseline_size > 0 else 0
        quality_score = min(result.get('html_quality', {}).get('score', 0) / results['Human-Chrome']['html_quality']['score'], 1.0) if results['Human-Chrome']['html_quality']['score'] > 0 else 0.5
        seo_score = calculate_seo_similarity(baseline_seo, result.get('seo_elements', {}))
        structured_score = 1.0 if result.get('structured_data', {}).get('has_structured_data') else 0.6
        final_score = (size_score * 0.30 + quality_score * 0.30 + seo_score * 0.30 + structured_score * 0.10) * 100
        result['ai_score'] = round(final_score)
def calculate_seo_similarity(baseline_seo, bot_seo):
    if not baseline_seo or not bot_seo: return 0.0
    scores = []
    for key in ['title', 'description', 'h1']:
        if baseline_seo.get(key) and bot_seo.get(key): scores.append(1.0 if baseline_seo[key] == bot_seo[key] else 0.5)
        elif not baseline_seo.get(key) and not bot_seo.get(key): scores.append(1.0)
        else: scores.append(0.0)
    return sum(scores) / len(scores) if scores else 0.0
def generate_report_string(results, url):
    lines = []
    # Tutaj sklejamy cały raport w jeden string, zamiast go drukować
    lines.append(f"\n🎯 AI ACCESSIBILITY REPORT v2")
    lines.append("=" * 70)
    ai_bots = {k: v for k, v in results.items() if k != "Human-Chrome"}
    # ... i tak dalej dla całego raportu ...
    # Dla uproszczenia, pokazuję tylko kluczowy fragment:
    avg_score = sum(r.get('ai_score', 0) for r in ai_bots.values()) / len(ai_bots) if ai_bots else 0
    lines.append(f"\n⭐ OVERALL AI ACCESSIBILITY: {avg_score:.0f}%")
    if avg_score >= 90: lines.append("   ✅ Excellent! Your site is perfectly optimized for AI bots.")
    elif avg_score >= 70: lines.append("   ⚠️  Good foundation, but optimization opportunities exist.")
    else: lines.append("   🚨 CRITICAL: Major AI accessibility problems!")
    # ... reszta hooków i porad ...
    lines.append("\n\n🚀 Thanks for using AI Bot Accessibility Checker v2!")
    return "\n".join(lines)


# --- GŁÓWNA FUNKCJA API ---
# Vercel automatycznie uruchomi tę funkcję, gdy ktoś wyśle zapytanie na /api/bot_checker
@app.route('/api/bot_checker', methods=['POST'])
def handle_check():
    try:
        data = request.get_json()
        url = data.get('url')

        if not url:
            return jsonify({'error': 'URL is required'}), 400

        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Uruchamiamy analizę
        results, initial_log = quick_bot_check(url)
        
        # Generujemy pełny raport jako jeden string
        # (Tutaj możesz wywołać swoje funkcje `generate_enhanced_report` etc.)
        full_report = initial_log + "\n" + generate_report_string(results, url)

        # Zwracamy raport w formacie JSON
        return jsonify({'report': full_report})

    except Exception as e:
        # Zwracamy błąd, jeśli coś pójdzie nie tak
        return jsonify({'error': f'An internal server error occurred: {str(e)}'}), 500