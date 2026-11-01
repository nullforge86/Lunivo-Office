#!/usr/bin/env python3
"""Vergleicht Lunivo-Symbole mit offenen Icon-Projekten (nur Analyse, nichts wird übernommen):  .venv/bin/python werkzeug/icon-vergleich-extern.py [Ziel.png]

Lädt je Funktion das Symbol aus Tabler (MIT), Phosphor (MIT), Bootstrap Icons (MIT), Fluent UI System Icons (MIT), Material Symbols (Apache-2.0)
und KDE Breeze (LGPL-3.0) von GitHub in einen Temp-Ordner und rendert sie mit Qt neben das Lunivo-Symbol. Die Fremdsymbole werden nicht im Projekt gespeichert. Kein HTML."""
import os, urllib.request, urllib.parse, concurrent.futures as cf, json
import tempfile
S=os.path.join(tempfile.gettempdir(),'lunivo-icon-vergleich')+'/'
# Funktion: (lunivo, tabler, phosphor, bootstrap, fluent(Ordner,datei), material, breeze)
F={
"Speichern":("speichern","device-floppy","floppy-disk","floppy",("Save","save"),"save","document-save"),
"Öffnen":("oeffnen","folder-open","folder-open","folder2-open",("Folder Open","folder_open"),"folder_open","document-open"),
"Neu":("neu","file-plus","file-plus","file-earmark-plus",("Document Add","document_add"),"note_add","document-new"),
"Drucken":("drucken","printer","printer","printer",("Print","print"),"print","document-print"),
"Ausschneiden":("schere","scissors","scissors","scissors",("Cut","cut"),"content_cut","edit-cut"),
"Kopieren":("kopie","copy","copy","files",("Copy","copy"),"content_copy","edit-copy"),
"Einfügen":("kleben","clipboard","clipboard","clipboard",("Clipboard Paste","clipboard_paste"),"content_paste","edit-paste"),
"Rückgängig":("zurueck","arrow-back-up","arrow-counter-clockwise","arrow-counterclockwise",("Arrow Undo","arrow_undo"),"undo","edit-undo"),
"Wiederholen":("vor","arrow-forward-up","arrow-clockwise","arrow-clockwise",("Arrow Redo","arrow_redo"),"redo","edit-redo"),
"Suchen":("lupe","search","magnifying-glass","search",("Search","search"),"search","edit-find"),
"Ersetzen":("ersetzen","replace","swap","arrow-left-right",("Arrow Swap","arrow_swap"),"find_replace","edit-find-replace"),
"Links":("links","align-left","text-align-left","text-left",("Text Align Left","text_align_left"),"format_align_left","format-justify-left"),
"Zentriert":("mitte","align-center","text-align-center","text-center",("Text Align Center","text_align_center"),"format_align_center","format-justify-center"),
"Rechts":("rechts","align-right","text-align-right","text-right",("Text Align Right","text_align_right"),"format_align_right","format-justify-right"),
"Blocksatz":("block","align-justified","text-align-justify","justify",("Text Align Justify","text_align_justify"),"format_align_justify","format-justify-fill"),
"Aufzählung":("punkte","list","list-bullets","list-ul",("Text Bullet List","text_bullet_list"),"format_list_bulleted","format-list-unordered"),
"Nummerierung":("zahlen","list-numbers","list-numbers","list-ol",("Text Number List Ltr","text_number_list_ltr"),"format_list_numbered","format-list-ordered"),
"Tabelle":("tabelle","table","table","table",("Table","table"),"table","insert-table"),
"Zeile einfügen":("tabellezeile","row-insert-bottom","rows-plus-bottom","plus-square",("Table Insert Row","table_insert_row"),"add_row_below","edit-table-insert-row-below"),
"Spalte einfügen":("spalteWahl","column-insert-right","columns-plus-right","plus-square",("Table Insert Column","table_insert_column"),"add_column_right","edit-table-insert-column-right"),
"Kommentar":("kommentarneu","message-plus","chat-text","chat-left-text",("Comment Add","comment_add"),"add_comment","list-add"),
"Einstellungen":("einstellungen","settings","gear","gear",("Settings","settings"),"settings","configure"),
"Link":("verknuepft","link","link","link-45deg",("Link","link"),"link","insert-link"),
"Bild":("bild","photo","image","image",("Image","image"),"image","insert-image"),
"Rechtschreibung":("rechtschreibpruefung","spell-check","text-aa","spellcheck",("Text Proofing Tools","text_proofing_tools"),"spellcheck","tools-check-spelling"),
"Spalten (Seite)":("spalten","columns","columns","layout-three-columns",("Text Column Two","text_column_two"),"view_column","view-split-left-right"),
"Export/Teilen":("pdf","share","export","box-arrow-up",("Share","share"),"ios_share","document-export"),
"Markieren":("marker","highlight","highlighter","highlighter",("Highlight","highlight"),"format_ink_highlighter","format-text-color"),
"Löschen":("radierer","trash","trash","trash",("Delete","delete"),"delete","edit-delete"),
"Zoom":("kleinerLupe","zoom-in","magnifying-glass-plus","zoom-in",("Zoom In","zoom_in"),"zoom_in","zoom-in"),
}
def url(lib,v):
    if lib=="tabler":return f"https://raw.githubusercontent.com/tabler/tabler-icons/main/icons/outline/{v}.svg"
    if lib=="phosphor":return f"https://raw.githubusercontent.com/phosphor-icons/core/main/assets/regular/{v}.svg"
    if lib=="bootstrap":return f"https://raw.githubusercontent.com/twbs/icons/main/icons/{v}.svg"
    if lib=="fluent":
        o,d=v;return "https://raw.githubusercontent.com/microsoft/fluentui-system-icons/main/assets/"+urllib.parse.quote(o)+f"/SVG/ic_fluent_{d}_24_regular.svg"
    if lib=="material":return f"https://raw.githubusercontent.com/google/material-design-icons/master/symbols/web/{v}/materialsymbolsoutlined/{v}_24px.svg"
    if lib=="breeze":return f"https://raw.githubusercontent.com/KDE/breeze-icons/master/icons/actions/22/{v}.svg"
libs=["tabler","phosphor","bootstrap","fluent","material","breeze"]
jobs=[]
for f,t in F.items():
    for lib,v in zip(libs,t[1:]): jobs.append((f,lib,v))
def get(j):
    f,lib,v=j;p=S+lib+"/"+f.replace(" ","_").replace("/","_")+".svg"
    os.makedirs(S+lib,exist_ok=True)
    try:
        d=urllib.request.urlopen(urllib.request.Request(url(lib,v),headers={"User-Agent":"x"}),timeout=25).read();open(p,"wb").write(d);return (f,lib,v,True)
    except Exception as e: return (f,lib,v,False)
with cf.ThreadPoolExecutor(12) as ex: res=list(ex.map(get,jobs))
fehl=[(f,l,v) for f,l,v,ok in res if not ok]
print(len(jobs)-len(fehl),"von",len(jobs),"geladen; fehlend:",fehl)
json.dump({f:t[0] for f,t in F.items()},open(S+'map.json','w'))

import sys
sys.path.insert(0,'src');os.environ['QT_QPA_PLATFORM']='offscreen'
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import *
from PySide6.QtCore import Qt, QByteArray, QRectF
from PySide6.QtSvg import QSvgRenderer
app=QApplication([])
from lunivo_writer.ui.widgets import icons
mp=json.load(open(S+'map.json'));al=icons.pfade_original()
libs=["tabler","phosphor","bootstrap","fluent","material","breeze"]
fk=list(mp);half=(len(fk)+1)//2
W,H,NB=130,50,120
def rows(img,p,namen,x0):
    for i,f in enumerate(namen):
        y=34+i*H
        p.setPen(QColor("#1f2328"));p.drawText(x0+4,y,NB,H,Qt.AlignVCenter|Qt.TextWordWrap,f)
        im=icons.pfad_bild(al[mp[f]],36,"#1f2328");p.drawImage(x0+NB,y+7,im)
        for k,l in enumerate(libs):
            fp=S+l+"/"+f.replace(" ","_").replace("/","_")+".svg"
            if not os.path.exists(fp): continue
            d=open(fp,'rb').read().replace(b'currentColor',b'#1f2328')
            r=QSvgRenderer(QByteArray(d))
            if not r.isValid(): continue
            ti=QImage(36,36,QImage.Format_ARGB32);ti.fill(Qt.transparent);q=QPainter(ti);q.setRenderHint(QPainter.Antialiasing);r.render(q,QRectF(0,0,36,36));q.end()
            p.drawImage(x0+NB+44+k*44,y+7,ti)
        p.setPen(QColor(200,200,200));p.drawLine(x0,y+H-1,x0+NB+44+7*44,y+H-1)
w=NB+44+7*44+10
img=QImage(2*w,34+half*H,QImage.Format_ARGB32);img.fill(Qt.white);p=QPainter(img);p.setFont(QFont("DejaVu Sans",8))
for x0 in (0,w):
    p.setPen(QColor("#1f2328"))
    p.drawText(x0+NB,4,44,30,Qt.AlignCenter,"Lunivo")
    for k,l in enumerate(["Tabler","Phosphor","Bootstrap","Fluent","Material","Breeze"]):p.drawText(x0+NB+44+k*44-4,4,52,30,Qt.AlignCenter,l)
rows(img,p,fk[:half],0);rows(img,p,fk[half:],w);p.end();img.save(sys.argv[1] if len(sys.argv)>1 else os.path.join(S,'vergleich.png'));print(img.width(),img.height())
