import sys
import os
import win32com.client
sys.stdout.reconfigure(encoding='utf-8')

desktop = r'C:\Users\张潇予\Desktop'
ppt_dir = os.path.join(desktop, '病理解剖学课件')
output_dir = os.path.join(desktop, 'ppt_texts')
os.makedirs(output_dir, exist_ok=True)

ppt_files = [
    '1细胞适应.ppt',
    '2损伤.ppt',
    '3坏死.ppt',
    '4修复.ppt',
    '5循环障碍.ppt',
    '6炎症.ppt',
    '7肿瘤.ppt',
    '8肿瘤.ppt',
]

ppt = win32com.client.Dispatch('PowerPoint.Application')

try:
    for fname in ppt_files:
        path = os.path.join(ppt_dir, fname)
        out_path = os.path.join(output_dir, fname.replace('.ppt', '.txt'))
        print(f'Extracting: {fname}...', end=' ', flush=True)

        try:
            prs = ppt.Presentations.Open(path, ReadOnly=True, WithWindow=False)
            lines = []
            for slide_num, slide in enumerate(prs.Slides, 1):
                lines.append(f'\n=== Slide {slide_num} ===')
                for shape in slide.Shapes:
                    if shape.HasTextFrame:
                        text = shape.TextFrame.TextRange.Text.strip()
                        if text:
                            lines.append(text)
                    if shape.HasTable:
                        table = shape.Table
                        for row in range(1, table.Rows.Count + 1):
                            row_text = []
                            for col in range(1, table.Columns.Count + 1):
                                cell_text = table.Cell(row, col).Shape.TextFrame.TextRange.Text.strip()
                                row_text.append(cell_text)
                            lines.append(' | '.join(row_text))
            prs.Close()

            with open(out_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            print(f'{len(lines)} lines -> {out_path}')
        except Exception as e:
            print(f'ERROR: {e}')
finally:
    ppt.Quit()

print('\nDone!')
