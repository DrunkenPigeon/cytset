import os
import sys
import webview

def main():
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    html_path = os.path.join(base_dir, 'assets', 'index.html')
    url = 'file:///' + os.path.abspath(html_path).replace('\\', '/')

    window = webview.create_window(
        'CYTSET — Информационная безопасность',
        url=url,
        width=500,
        height=900,
        resizable=True,
        min_size=(400, 600)
    )
    webview.start(private_mode=False)

if __name__ == '__main__':
    main()
