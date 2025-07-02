import os
import re
import quopri
import uuid
from datetime import datetime, date, timedelta
from icalendar import Calendar, Event, vDate
import pytz

def parse_vcs_properties(vcs_event_block_bytes):
    """VEVENTブロックのバイト列を解析し、プロパティ辞書を返す。"""
    content_bytes = vcs_event_block_bytes.replace(b'=\r\n', b'').replace(b'=\n', b'')
    content_bytes = re.sub(b'\r?\n[ \t]', b'', content_bytes)
    
    properties = {}
    
    for line_bytes in content_bytes.split(b'\n'):
        if b':' not in line_bytes: continue
        key_part_bytes, value_part_bytes = line_bytes.split(b':', 1)
        try:
            key_part_str = key_part_bytes.decode('utf-8')
        except UnicodeDecodeError:
            key_part_str = key_part_bytes.decode('ascii', errors='ignore')

        charset_match = re.search(r'CHARSET=([^;:]+)', key_part_str, re.IGNORECASE)
        encoding = (charset_match.group(1) if charset_match else 'utf-8').lower()
        
        if 'ENCODING=QUOTED-PRINTABLE' in key_part_str.upper():
            try:
                decoded_bytes = quopri.decodestring(value_part_bytes)
                value = decoded_bytes.decode('cp932' if 'shift_jis' in encoding else encoding, errors='replace')
            except Exception: value = value_part_bytes.decode('utf-8', errors='ignore')
        else:
            value = value_part_bytes.decode('utf-8', errors='ignore')
        
        main_key = key_part_str.split(';')[0].upper().strip()
        if main_key: properties[main_key] = value.strip()
    return properties

def convert_vcs_to_ics(input_path, output_path):
    print(f"'{input_path}' を読み込んでいます...")
    try:
        with open(input_path, 'rb') as f:
            vcs_content_bytes = f.read()
    except Exception as e:
        print(f"ファイル読み込み失敗: {e}")
        return

    # --- ここからがデバッグの本丸 ---
    print("\n--- プログラムによるイベントブロックの検出結果 ---")
    event_blocks_bytes = re.findall(b'BEGIN:VEVENT(.*?)\r?\nEND:VEVENT', vcs_content_bytes, re.DOTALL)
    print(f"検出されたVEVENTブロックの総数: {len(event_blocks_bytes)}件")

    found_events = {}
    for i, block in enumerate(event_blocks_bytes):
        # SUMMARY部分だけを抜き出してデコードしてみる
        summary_text = "（SUMMARYプロパティが見つかりません）"
        summary_match = re.search(b'SUMMARY(?:;[^:]*)?:(.*)', block.replace(b'\r\n', b'\n'))
        if summary_match:
            try:
                val_bytes = summary_match.group(1)
                # 複数行QPを簡易的に結合
                val_bytes = val_bytes.replace(b'=\n', b'').replace(b'\n ', b'')
                decoded = quopri.decodestring(val_bytes)
                # UTF-8かCP932(Shift_JIS)でデコード試行
                try: summary_text = decoded.decode('utf-8')
                except: summary_text = decoded.decode('cp932')
            except Exception:
                summary_text = "（SUMMARYのデコードに失敗）"
        
        # どのイベントが何回見つかったかを記録
        summary_text = summary_text.strip()
        found_events[summary_text] = found_events.get(summary_text, 0) + 1

    print("\n【検出されたイベント名と回数】")
    for name, count in found_events.items():
        print(f"- '{name}': {count}回")
        
    print("\n--- 検出結果ここまで。変換処理を開始します。 ---\n")
    # --- デバッグここまで ---

    if not event_blocks_bytes:
        print("変換可能なVEVENTが見つかりませんでした。")
        return

    cal = Calendar()
    cal.add('prodid', '-//My VCS to ICS Converter//')
    cal.add('version', '2.0')
    jst = pytz.timezone('Asia/Tokyo')

    for block_bytes in event_blocks_bytes:
        event_data = parse_vcs_properties(block_bytes)
        if 'DTSTART' not in event_data: continue
        event = Event()
        if event_data.get('X-DCM-SID'):
            safe_sid = re.sub(r'[^a-zA-Z0-9-]', '', event_data['X-DCM-SID'])
            uid = f"{safe_sid}@vcs-converter.local"
            event.add('uid', uid)
        else:
            seed = (event_data.get('DTSTART','') + event_data.get('SUMMARY','')).encode('utf-8')
            event.add('uid', uuid.uuid5(uuid.NAMESPACE_DNS, str(seed)))
            
        last_modified_str = event_data.get('LAST-MODIFIED', '').replace('Z', '')
        if last_modified_str:
             try:
                dt_stamp_utc = datetime.strptime(last_modified_str, '%Y%m%dT%H%M%S')
                event.add('dtstamp', pytz.utc.localize(dt_stamp_utc))
             except ValueError:
                event.add('dtstamp', datetime.now(pytz.utc))
        else:
            event.add('dtstamp', datetime.now(pytz.utc))
            
        for key in ['SUMMARY', 'LOCATION', 'DESCRIPTION']:
            if event_data.get(key): event.add(key.lower(), event_data[key])
        
        is_allday = event_data.get('X-DCM-ALLDAY') == '1'
        
        def parse_dt(dt_str, is_allday_flag):
            if not dt_str: return None
            dt_str_clean = dt_str.upper().replace('Z', '')
            try:
                if is_allday_flag: return vDate(datetime.strptime(dt_str_clean[:8], '%Y%m%d').date())
                else: return jst.localize(datetime.strptime(dt_str_clean, '%Y%m%dT%H%M%S'))
            except (ValueError, IndexError): return None
            
        dtstart = parse_dt(event_data.get('DTSTART'), is_allday)
        if not dtstart: continue
        event.add('dtstart', dtstart)

        dtend = parse_dt(event_data.get('DTEND'), is_allday)
        if dtend:
            if isinstance(dtstart, vDate) and dtstart.dt >= dtend.dt:
                 dtend = vDate(dtstart.dt + timedelta(days=1))
            event.add('dtend', dtend)
        else:
            if is_allday: event.add('dtend', vDate(dtstart.dt + timedelta(days=1)))
            else: event.add('dtend', dtstart + timedelta(hours=1))

        cal.add_component(event)

    print(f"\n'{output_path}' に変換結果を保存しています...")
    with open(output_path, 'wb') as f:
        f.write(cal.to_ical())
    print("変換が完了しました。")


if __name__ == '__main__':
    # (main関数部分は変更なし)
    import argparse
    parser = argparse.ArgumentParser(description='docomo VCS (.vcs) to iCalendar (.ics) converter.', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('input_file', help='Input .vcs file path.')
    parser.add_argument('-o', '--output', help='Output .ics file path.\nIf not specified, it will be created in the same directory\nwith the same name but a .ics extension.')
    args = parser.parse_args()
    input_path = args.input_file
    if not os.path.exists(input_path):
        print(f"エラー: 入力ファイルが見つかりません: {input_path}")
    else:
        if args.output:
            output_path = args.output
        else:
            base, _ = os.path.splitext(input_path)
            output_path = base + '.ics'
        convert_vcs_to_ics(input_path, output_path)