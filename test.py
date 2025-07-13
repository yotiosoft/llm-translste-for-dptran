import subprocess
import re
import time

# 言語ごとの記号とコード対応表
LANG_MAP = {
    '英語': 'EN',
    '中国語': 'ZH',
    'フランス語': 'FR',
    '韓国語': 'KO',
    'ドイツ語': 'DE',
    'スペイン語': 'ES',
    'ロシア語': 'RU',
    'イタリア語': 'IT',
    'タイ語': 'TH',
    'ベトナム語': 'VI',
    'ヒンディー語': 'HI',
    'アラビア語': 'AR',
    'ベンガル語': 'BN',
    'ビルマ語': 'MY',
    'インドネシア語': 'ID',
    'スワヒリ語': 'SW',
}

input_file = "llm-translate-test.txt"
output_file = "results/output.txt"

current_lang_code = None

with open(input_file, 'r', encoding='utf-8') as infile, \
    open(output_file, 'a', encoding='utf-8') as outfile:

    for line in infile:
        line = line.strip()

        # 空行はスキップ
        if not line:
            continue

        # 言語切替行の検出
        lang_match = re.search(r'([🇦-🇿]+)\s+(.+?)（', line)
        if lang_match:
            readable_lang = lang_match.group(2)
            current_lang_code = LANG_MAP.get(readable_lang)
            continue

        # 翻訳対象文（→ が含まれていない）
        if not line.startswith('→') and not line.startswith('　→') and current_lang_code:
            try:
                start = time.perf_counter()
                result = subprocess.run(
                    ["dptran", line, "-f", current_lang_code, "-t", "JA"],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    check=True
                )
                end = time.perf_counter()
                translated = (result.stdout or "").strip()
                rtt = round(end - start, 3)
            except subprocess.CalledProcessError as e:
                translated = f"[Command Error] {e.stderr.strip() if e.stderr else e}"
                rtt = -1
            except UnicodeDecodeError as e:
                translated = f"[Decode Error] {str(e)}"
                rtt = -1
            except Exception as e:
                translated = f"[Unexpected Error] {str(e)}"
                rtt = -1

            # 出力形式：原文 + 翻訳 + RTT
            outfile.write(f"原文: {line}\n翻訳: {translated}\nRTT: {rtt} 秒\n\n")
