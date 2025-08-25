VCS to ICS Converter
この Python スクリプトは，NTT ドコモの VCS (Virtual Calendar Specification) 形式のファイルを，標準的な iCalendar (ICS) 形式に変換するためのツールです．
これにより，ドコモの携帯電話で作成されたスケジュールデータを，Google カレンダーや Apple カレンダーなどのカレンダーアプリケーションで利用できるようになります．

主な機能
VCS ファイルからイベント情報を解析します．

Quoted-Printable エンコーディングおよび Shift_JIS (CP932) を含む様々な文字エンコーディングを処理します．

抽出されたイベントデータに基づいて，iCalendar 形式のファイル (.ics) を生成します．

全日イベントの正しい処理と，開始時刻と終了時刻の整合性を確保します．

X-DCM-SID が存在する場合はそれを使用して UID を生成し，存在しない場合はイベントデータから一意の UID を生成します．

必要なもの
このスクリプトを実行するには，以下の Python ライブラリが必要です．

・icalendar
・pytz

pip install icalendar pytz

使用方法
python your_script_name.py <入力 VCS ファイルパス> [-o <出力 ICS ファイルパス>]

<入力 VCS ファイルパス>: 変換したい VCS ファイルのパスを指定します．

-o <出力 ICS ファイルパス>, --output <出力 ICS ファイルパス>: (オプション) 生成される ICS ファイルのパスを指定します．このオプションを省略した場合，入力ファイルと同じディレクトリに，同じファイル名で拡張子を .ics に変更したファイルが作成されます．

例

my_schedule.vcs というファイルを変換し，my_schedule.ics として保存する場合:

python3 your_script_name.py my_schedule.vcs

input.vcs を変換し，output_calendar.ics という名前で保存する場合:

python3 your_script_name.py input.vcs -o output_calendar.ics
