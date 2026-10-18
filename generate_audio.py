#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_audio.py — يولّد ملفات صوت (mp3) لكل فقرة عربية في book.js بأصوات Edge العصبية،
ويكتب audio.js الذي يقرؤه التطبيق.

التشغيل (حاسوب أو Termux على الهاتف):
    pip install edge-tts
    python generate_audio.py --book pwa            # المجلد الذي فيه book.js
    python generate_audio.py --book pwa --list     # عرض الأصوات العربية المتاحة
    python generate_audio.py --book pwa --dry      # تقدير الحجم والمدة بلا توليد

الخيارات: --voice ar-SA-HamedNeural  --rate +0%  --pitch +0Hz  --sections intro1,p1a  --jobs 3
السكربت يكمل من حيث توقف: يتجاوز الملفات الموجودة. بعد الانتهاء ارفع مجلد audio/ وملف audio.js مع التطبيق.

تنبيه: خدمة Edge العصبية غير رسمية من Microsoft وقد تتغير أو تتوقف، وشروط استعمالها خارج متصفح Edge غير واضحة.
للنشر العام فكّر في Azure AI Speech الرسمية بالأصوات نفسها.
"""
import argparse, asyncio, json, os, re, sys

def load_book(path):
    s = open(os.path.join(path, 'book.js'), encoding='utf-8').read()
    m = re.search(r'const BOOK=(\{.*\});\s*$', s, re.S)
    if not m: sys.exit('تعذّر قراءة book.js')
    return json.loads(m.group(1))

def speech_text(t):
    t = t.replace('ﷺ', 'صلى الله عليه وسلم').replace('ﷻ', 'جل جلاله').replace('ـ', '')
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def name(sec, i): return f"{sec}-{i+1:03d}.mp3"

async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--book', default='.'); ap.add_argument('--out', default='audio')
    ap.add_argument('--voice', default='ar-SA-HamedNeural'); ap.add_argument('--rate', default='+0%'); ap.add_argument('--pitch', default='+0Hz')
    ap.add_argument('--sections', default=''); ap.add_argument('--jobs', type=int, default=3)
    ap.add_argument('--list', action='store_true'); ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()
    book = load_book(a.book); chs = book['ch']
    if a.sections: want = set(a.sections.split(',')); chs = [c for c in chs if c['id'] in want]
    total = sum(len(p) for c in chs for p in c['ar'])
    if a.dry:
        n = sum(len(c['ar']) for c in chs)
        print(f"{len(chs)} قسماً، {n} فقرة، {total:,} حرفاً ≈ {total/14/3600:.1f} ساعة صوت، ≈ {total/14*6/1024:.0f} MB (تقدير)"); return
    import edge_tts
    voices = await edge_tts.list_voices()
    ar = [v for v in voices if v['Locale'].startswith('ar-')]
    if a.list:
        for v in ar: print(v['ShortName'], v['Gender'], v['Locale']); return
    if a.voice not in [v['ShortName'] for v in voices]:
        print('الصوت غير موجود. الأصوات العربية المتاحة:')
        for v in ar: print(' ', v['ShortName'], v['Gender'])
        sys.exit(1)
    outdir = os.path.join(a.book, a.out); os.makedirs(outdir, exist_ok=True)
    sem = asyncio.Semaphore(a.jobs); done = 0; fails = []
    jobs = [(c['id'], i, p) for c in chs for i, p in enumerate(c['ar'])]
    async def one(sec, i, text):
        nonlocal done
        f = os.path.join(outdir, name(sec, i))
        if os.path.exists(f) and os.path.getsize(f) > 1000: done += 1; return
        async with sem:
            for k in range(5):
                try:
                    await edge_tts.Communicate(speech_text(text), a.voice, rate=a.rate, pitch=a.pitch).save(f + '.part')
                    os.replace(f + '.part', f); break
                except Exception as e:
                    await asyncio.sleep(2 ** k)
            else: fails.append(f)
        done += 1
        if done % 20 == 0: print(f'{done}/{len(jobs)}', flush=True)
    await asyncio.gather(*[one(*j) for j in jobs])
    counts = {}
    for c in book['ch']:
        n = len(c['ar'])
        if n and all(os.path.exists(os.path.join(outdir, name(c['id'], i))) for i in range(n)): counts[c['id']] = n
    open(os.path.join(a.book, 'audio.js'), 'w', encoding='utf-8').write('AUDIO=' + json.dumps({'voice': a.voice, 'dir': a.out + '/', 'ar': counts}, ensure_ascii=False) + ';\n')
    print(f'اكتمل: {len(counts)}/{len(book["ch"])} قسماً جاهزاً، وفشل {len(fails)} ملف')
    if fails: print('أعد التشغيل لإكمال الناقص:', *fails[:5], sep='\n  ')

asyncio.run(main())
