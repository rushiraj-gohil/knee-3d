"""Extract the full-resolution film image from each page of the MRI PDF -> raw_p1.png, raw_p2.png, raw_p3.png"""
import sys, fitz
d = fitz.open(sys.argv[1] if len(sys.argv) > 1 else 'mri.pdf')
for i, p in enumerate(d):
    for img in p.get_images():
        fitz.Pixmap(d, img[0]).save(f'raw_p{i+1}.png')
        print('saved', f'raw_p{i+1}.png')
