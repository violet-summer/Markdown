from pdf2image import convert_from_path

# PDF转PNG，dpi越高越清晰
images = convert_from_path('F:\\CODE\\GIThub\\beijinglu\\origin\\1.pdf', dpi=700, poppler_path='poppler/bin')
for i, img in enumerate(images):
    img.save(f'output_page_{i+1}.png', 'PNG')