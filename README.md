VCS to ICS Converter
このPythonスクリプトは、NTTドコモのVCS（Virtual Calendar Specification）形式のファイルを、標準的なiCalendar（ICS）形式に変換するためのツールです。これにより、ドコモの携帯電話で作成されたスケジュールデータを、GoogleカレンダーやAppleカレンダーなどの現代の多くのカレンダーアプリケーションで利用できるようになります。

主な機能
VCSファイルからイベント情報を解析します。

Quoted-PrintableエンコーディングおよびShift_JIS（CP932）を含む様々な文字エンコーディングを処理します。

抽出されたイベントデータに基づいて、iCalendar形式のファイル（.ics）を生成します。

全日イベントの正しい処理と、開始時刻と終了時刻の整合性を確保します。

X-DCM-SIDが存在する場合はそれを使用してUIDを生成し、存在しない場合はイベントデータから一意のUIDを生成します。

必要なもの
このスクリプトを実行するには、以下のPythonライブラリが必要です。

・icalendar
・pytz

これらのライブラリは、pipを使ってインストールできます。

pip install icalendar pytz

使用方法
スクリプトはコマンドラインから実行します。

python your_script_name.py <入力VCSファイルパス> [-o <出力ICSファイルパス>]

<入力VCSファイルパス>: 変換したいVCSファイルのパスを指定します。

-o <出力ICSファイルパス>, --output <出力ICSファイルパス>: (オプション) 生成されるICSファイルのパスを指定します。このオプションを省略した場合、入力ファイルと同じディレクトリに、同じファイル名で拡張子を .ics に変更したファイルが作成されます。

例

my_schedule.vcs というファイルを変換し、my_schedule.ics として保存する場合:

python3 your_script_name.py my_schedule.vcs

input.vcs を変換し、output_calendar.ics という名前で保存する場合:

python3 your_script_name.py input.vcs -o output_calendar.ics
