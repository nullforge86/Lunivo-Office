"""Zentraler OOXML-Funktionskatalog (WordprocessingML) — unabhängig vom Testbestand definiert.

Grundlage: ECMA-376 / ISO/IEC 29500 (Transitional und Strict) und die dokumentierten Microsoft-Erweiterungen (``w14``, ``w15``, ``w16*``, ``wp14``, ``wps`` …).
Jede Funktion besteht aus Kennung, Bereich, Name, einer **Erkennungsregel** über die Beobachtungen der Analyse (``ooxml_analyse``) und einer Empfehlung, wie
ein fehlendes Testdokument aussehen soll. Der Katalog kennt kein einziges Testdokument; fehlende Funktionen werden dadurch erst sichtbar.

Regeln (Tupel):
    ("el", "w:tbl")                      Element kommt irgendwo vor
    ("attr", "w:jc", "w:val", "center")  Attribut (optional mit Wert) an einem Element
    ("rel", "footnotes")                 Beziehungstyp (letztes Segment der Typ-URI) im Paket
    ("teil", "word/header*.xml")         Paketteil vorhanden (fnmatch)
    ("ns", "w14")                        Namensraum wird benutzt
    ("in", "w:tbl", "w:tc")              Element ``w:tbl`` liegt unter ``w:tc`` (Verschachtelung; nur bei beobachteten Vorfahren)
    ("min", "w:p", 1000)                 Element kommt mindestens n-mal vor
    ("all", "id1", "id2" …)              Kombination: alle genannten Funktionen kommen im selben Dokument vor
    ("any", regel, regel …)              mindestens eine Regel trifft zu
    ("vererbt", "w:b")                   Eigenschaft wird in einer *benutzten* Formatvorlage (inkl. Vererbungskette) gesetzt
    ("strict",), ("transitional",)       OOXML-Variante
"""
from __future__ import annotations

# ---- Namensräume -----------------------------------------------------------------------------------------------------
NAMENSRAEUME = {
    "http://schemas.openxmlformats.org/wordprocessingml/2006/main": "w",
    "http://purl.oclc.org/ooxml/wordprocessingml/main": "w",                         # Strict
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships": "r",
    "http://purl.oclc.org/ooxml/officeDocument/relationships": "r",
    "http://schemas.openxmlformats.org/drawingml/2006/main": "a",
    "http://purl.oclc.org/ooxml/drawingml/main": "a",
    "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing": "wp",
    "http://purl.oclc.org/ooxml/drawingml/wordprocessingDrawing": "wp",
    "http://schemas.openxmlformats.org/drawingml/2006/picture": "pic",
    "http://purl.oclc.org/ooxml/drawingml/picture": "pic",
    "http://schemas.openxmlformats.org/drawingml/2006/chart": "c",
    "http://purl.oclc.org/ooxml/drawingml/chart": "c",
    "http://schemas.openxmlformats.org/drawingml/2006/diagram": "dgm",
    "http://purl.oclc.org/ooxml/drawingml/diagram": "dgm",
    "http://schemas.openxmlformats.org/drawingml/2006/lockedCanvas": "lc",
    "http://schemas.openxmlformats.org/officeDocument/2006/math": "m",
    "http://purl.oclc.org/ooxml/officeDocument/math": "m",
    "http://schemas.openxmlformats.org/markup-compatibility/2006": "mc",
    "urn:schemas-microsoft-com:vml": "v",
    "urn:schemas-microsoft-com:office:office": "o",
    "urn:schemas-microsoft-com:office:word": "w10",
    "urn:schemas-microsoft-com:office:excel": "x",
    "http://schemas.microsoft.com/office/word/2010/wordml": "w14",
    "http://schemas.microsoft.com/office/word/2012/wordml": "w15",
    "http://schemas.microsoft.com/office/word/2018/wordml": "w16",
    "http://schemas.microsoft.com/office/word/2018/wordml/cex": "w16cex",
    "http://schemas.microsoft.com/office/word/2016/wordml/cid": "w16cid",
    "http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash": "w16sdtdh",
    "http://schemas.microsoft.com/office/word/2020/oel/original": "w16oel",
    "http://schemas.microsoft.com/office/word/2023/wordml/word16du": "w16du",
    "http://schemas.microsoft.com/office/word/2015/wordml/symex": "w16se",
    "http://schemas.microsoft.com/office/word/2006/wordml": "wne",
    "http://schemas.microsoft.com/office/word/2010/wordprocessingShape": "wps",
    "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup": "wpg",
    "http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas": "wpc",
    "http://schemas.microsoft.com/office/word/2010/wordprocessingInk": "wpi",
    "http://schemas.microsoft.com/office/word/2008/wordml": "w12",
    "http://schemas.microsoft.com/office/drawing/2010/wordprocessingDrawing": "wp14",
    "http://schemas.microsoft.com/office/drawing/2008/diagram": "dsp",
    "http://schemas.microsoft.com/office/drawing/2010/main": "a14",
    "http://schemas.microsoft.com/office/drawing/2014/chartex": "cx",
    "http://schemas.microsoft.com/office/drawing/2016/ink": "aink",
    "http://schemas.microsoft.com/office/drawing/2017/model3d": "am3d",
    "http://schemas.openxmlformats.org/package/2006/relationships": "rel",
    "http://schemas.openxmlformats.org/package/2006/content-types": "ct",
    "http://schemas.openxmlformats.org/package/2006/metadata/core-properties": "cp",
    "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties": "ep",
    "http://schemas.openxmlformats.org/officeDocument/2006/custom-properties": "cust",
    "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes": "vt",
    "http://schemas.openxmlformats.org/officeDocument/2006/customXml": "cxml",
    "http://schemas.openxmlformats.org/officeDocument/2006/bibliography": "b",
    "http://purl.org/dc/elements/1.1/": "dc",
    "http://purl.org/dc/terms/": "dcterms",
    "http://www.w3.org/XML/1998/namespace": "xml",
    "http://www.w3.org/2001/XMLSchema-instance": "xsi",
    "http://schemas.microsoft.com/office/2006/metadata/properties": "mp",
    "http://schemas.microsoft.com/office/2006/metadata/contentType": "mct",
    "http://schemas.microsoft.com/office/infopath/2007/PartnerControls": "pc",
    "http://schemas.microsoft.com/office/drawing/2012/chart": "c15",
    "http://schemas.microsoft.com/office/drawing/2007/8/2/chart": "c14",
    "http://schemas.openxmlformats.org/schemaLibrary/2006/main": "sl",
    "http://schemas.openxmlformats.org/xmlPackage/2006/digital-signature": "ds",
}

# Beziehungstypen, die Word kennt (letztes Segment der Typ-URI)
BEKANNTE_BEZIEHUNGEN = {
    "officeDocument", "styles", "stylesWithEffects", "numbering", "settings", "webSettings", "fontTable", "theme", "footnotes", "endnotes", "comments",
    "commentsExtended", "commentsIds", "commentsExtensible", "people", "header", "footer", "image", "hyperlink", "oleObject", "package", "chart", "diagramData",
    "diagramLayout", "diagramQuickStyle", "diagramColors", "diagramDrawing", "customXml", "customXmlProps", "glossaryDocument", "vmlDrawing", "footnotes",
    "subDocument", "attachedTemplate", "font", "audio", "video", "themeOverride", "inkml", "aFChunk", "mailMergeSource", "mailMergeHeaderSource", "control",
    "thumbnail", "core-properties", "extended-properties", "custom-properties", "digital-signature-origin", "signature", "chartEx", "chartUserShapes",
    "model3d", "slicer", "diagramDrawing", "externalLinkPath", "bibliography", "docPartGallery", "vbaProject", "vbaData", "keyMapCustomizations",
    "recipientData", "ink", "customProperty", "hdphoto", "microsoft.com/office/2007/relationships/hdphoto", "schemaLibrary", "printerSettings", "origin",
    "relationships", "webSettings", "documentTasks", "intelligence", "wordMLExtendedAttributes", "wordMLXml", "attachedSchema", "xmlMaps", "mathSettings",
}

# Paketteile, die Word kennt (fnmatch)
BEKANNTE_TEILE = (
    "[Content_Types].xml", "_rels/*", "docProps/*", "word/document.xml", "word/_rels/*", "word/styles.xml", "word/stylesWithEffects.xml", "word/numbering.xml",
    "word/settings.xml", "word/webSettings.xml", "word/fontTable.xml", "word/theme/*", "word/footnotes.xml", "word/endnotes.xml", "word/comments*.xml",
    "word/people.xml", "word/header*.xml", "word/footer*.xml", "word/media/*", "word/embeddings/*", "word/charts/*", "word/diagrams/*", "word/drawings/*",
    "word/glossary/*", "word/fonts/*", "word/activeX/*", "word/ink/*", "word/model3d/*", "word/vbaProject.bin", "word/vbaData.xml", "word/document2.xml",
    "word/customizations.xml", "word/attachedToolbars.xml", "word/subdocs/*", "word/afchunk*", "word/tags/*", "word/revisions/*", "word/printerSettings/*",
    "word/webextensions/*", "word/intelligence*.xml", "word/documenttasks/*", "customXml/*", "_xmlsignatures/*", "word/diagrams/_rels/*", "word/*/_rels/*",
    "word/commentsExtensible.xml", "word/commentsIds.xml", "word/commentsExtended.xml", "word/mailMergeData*", "word/queryTable*", "docMetadata/*",
)

# Bekannte Elemente des Namensraums ``w`` (WordprocessingML, Transitional/Strict) — Elemente außerhalb dieser Liste werden als „unbekannt“ erfasst.
BEKANNT_W = frozenset("""
document body p r t tab br cr noBreakHyphen softHyphen sym pgNum ptab lastRenderedPageBreak delText instrText delInstrText fldChar fldSimple hyperlink
bookmarkStart bookmarkEnd commentRangeStart commentRangeEnd commentReference annotationRef footnoteReference endnoteReference footnoteRef endnoteRef
separator continuationSeparator continuationNotice footnote endnote footnotes endnotes pPr rPr rPrChange pPrChange sectPrChange tblPrChange tblGridChange trPrChange
tcPrChange tblPrExChange numberingChange cellIns cellDel cellMerge moveFrom moveTo moveFromRangeStart moveFromRangeEnd moveToRangeStart moveToRangeEnd ins del
customXmlInsRangeStart customXmlInsRangeEnd customXmlDelRangeStart customXmlDelRangeEnd customXmlMoveFromRangeStart customXmlMoveFromRangeEnd
customXmlMoveToRangeStart customXmlMoveToRangeEnd pStyle keepNext keepLines pageBreakBefore framePr widowControl numPr numId ilvl suppressLineNumbers pBdr shd tabs
suppressAutoHyphens kinsoku wordWrap overflowPunct topLinePunct autoSpaceDE autoSpaceDN bidi adjustRightInd snapToGrid spacing ind contextualSpacing
mirrorIndents suppressOverlap jc textDirection textAlignment textboxTightWrap outlineLvl divId cnfStyle sectPr pgSz pgMar paperSrc pgBorders lnNumType pgNumType cols
col formProt vAlign noEndnote titlePg rtlGutter docGrid headerReference footerReference type endnotePr footnotePr top left bottom right start end between bar insideH
insideV tl2br tr2bl rStyle rFonts b bCs i iCs caps smallCaps strike dstrike outline shadow emboss imprint noProof vanish webHidden color w kern position sz szCs
highlight u effect bdr vertAlign rtl cs em lang eastAsianLayout specVanish oMath tbl tblPr tblStyle tblpPr tblOverlap bidiVisual tblStyleRowBandSize
tblStyleColBandSize tblW tblCellSpacing tblInd tblBorders tblLayout tblCellMar tblLook tblCaption tblDescription tblGrid gridCol tr tc tblPrEx trPr tcPr cantSplit
trHeight tblHeader gridBefore gridAfter wBefore wAfter hidden tcW gridSpan hMerge vMerge tcBorders noWrap tcMar tcFitText hideMark headers sdt sdtPr sdtContent
sdtEndPr alias tag id lock placeholder docPart docPartObj docPartList docPartGallery docPartCategory docPartUnique showingPlcHdr dataBinding temporary label
tabIndex equation comboBox date dateFormat storeMappedDataAs calendar dropDownList listItem picture richText text citation group bibliography customXml customXmlPr
attr smartTag smartTagPr dir bdo contentPart subDoc proofErr permStart permEnd object drawing pict control txbxContent styles docDefaults rPrDefault pPrDefault
latentStyles lsdException style name aliases basedOn next link autoRedefine uiPriority semiHidden unhideWhenUsed qFormat locked personal personalCompose
personalReply rsid tblStylePr numbering abstractNum multiLevelType tmpl nsid styleLink numStyleLink lvl numFmt lvlRestart isLgl suff lvlText lvlPicBulletId legacy
lvlJc numPicBullet num abstractNumId lvlOverride startOverride settings writeProtection view zoom removePersonalInformation removeDateAndTime
doNotDisplayPageBoundaries displayBackgroundShape printPostScriptOverText printFractionalCharacterWidth printFormsData embedTrueTypeFonts embedSystemFonts
saveSubsetFonts saveFormsData mirrorMargins alignBordersAndEdges bordersDoNotSurroundHeader bordersDoNotSurroundFooter gutterAtTop hideSpellingErrors
hideGrammaticalErrors activeWritingStyle proofState formsDesign attachedTemplate linkStyles stylePaneFormatFilter stylePaneSortMethod documentType mailMerge
revisionView trackRevisions doNotTrackMoves doNotTrackFormatting documentProtection autoFormatOverride styleLockTheme styleLockQFSet defaultTabStop
autoHyphenation consecutiveHyphenLimit hyphenationZone doNotHyphenateCaps showEnvelope summaryLength clickAndTypeStyle defaultTableStyle evenAndOddHeaders
bookFoldRevPrinting bookFoldPrinting bookFoldPrintingSheets drawingGridHorizontalSpacing drawingGridVerticalSpacing displayHorizontalDrawingGridEvery
displayVerticalDrawingGridEvery doNotUseMarginsForDrawingGridOrigin drawingGridHorizontalOrigin drawingGridVerticalOrigin doNotShadeFormData noPunctuationKerning
characterSpacingControl printTwoOnOne strictFirstAndLastChars noLineBreaksAfter noLineBreaksBefore savePreviewPicture doNotValidateAgainstSchema saveInvalidXml
ignoreMixedContent alwaysShowPlaceholderText doNotDemarcateInvalidXml saveXmlDataOnly useXSLTWhenSaving saveThroughXslt showXMLTags alwaysMergeEmptyNamespace
updateFields hdrShapeDefaults compat docVars rsids mathPr attachedSchema themeFontLang clrSchemeMapping doNotIncludeSubdocsInStats doNotAutoCompressPictures
forceUpgrade captions readModeInkLockDown smartTagType schemaLibrary shapeDefaults doNotEmbedSmartTags decimalSymbol listSeparator compatSetting
useSingleBorderforContiguousCells wpJustification noTabHangInd noLeading spaceForUL noColumnBalance balanceSingleByteDoubleByteWidth noExtraLineSpacing
doNotLeaveBackslashAlone ulTrailSpace doNotExpandShiftReturn spacingInWholePoints lineWrapLikeWord6 printBodyTextBeforeHeader printColBlack wpSpaceWidth
showBreaksInFrames subFontBySize suppressBottomSpacing suppressTopSpacing suppressSpacingAtTopOfPage suppressTopSpacingWP suppressSpBfAfterPgBrk
swapBordersFacingPages convMailMergeEsc truncateFontHeightsLikeWP6 mwSmallCaps usePrinterMetrics doNotSuppressParagraphBorders wrapTrailSpaces
footnoteLayoutLikeWW8 shapeLayoutLikeWW8 alignTablesRowByRow forgetLastTabAlignment adjustLineHeightInTable autoSpaceLikeWord95 noSpaceRaiseLower
doNotUseHTMLParagraphAutoSpacing layoutRawTableWidth layoutTableRowsApart useWord97LineBreakRules doNotBreakWrappedTables doNotSnapToGridInCell
selectFldWithFirstOrLastChar applyBreakingRules doNotWrapTextWithPunct doNotUseEastAsianBreakRules useWord2002TableStyleRules growAutofit useFELayout
useNormalStyleForList doNotUseIndentAsNumberingTabStop useAltKinsokuLineBreakRules allowSpaceOfSameStyleInTable doNotSuppressIndentation
doNotAutofitConstrainedTables autofitToFirstFixedWidthCell underlineTabInNumList displayHangulFixedWidth splitPgBreakAndParaMark doNotVertAlignCellWithSp
doNotBreakConstrainedForcedTable ignoreVerticalAlignmentInTextboxes useAnsiKerningPairs cachedColBalance fontTable font altName panose1 charset family notTrueType
pitch sig embedRegular embedBold embedItalic embedBoldItalic webSettings optimizeForBrowser relyOnVML allowPNG doNotRelyOnCSS doNotSaveAsSingleFile
doNotOrganizeInFolder doNotUseLongFileNames pixelsPerInch targetScreenSz saveSmartTagsAsXml comments comment hdr ftr glossaryDocument docParts docPartPr behaviors
behavior types category gallery description guid ruby rt rubyPr rubyAlign hps hpsRaise hpsBaseText rubyBase dirty fitText div divs marLeft marRight marTop marBottom
divBdr blockQuote bodyDiv divsChild lvlText numStyleLink tblpPrChange sdtPrChange shapeLayout footnoteProps endnoteProps previousEntry exact hAnsi ascii eastAsia
cstheme asciiTheme hAnsiTheme eastAsiaTheme textInput maxLength default format lastValue fullDate storeItemID xpath prefixMappings checkbox checked
mathPr moveFromRangeStart sdtContent oMathPara noProof movie recipients recipient odso table src colDelim type fHdr fieldMapData mappedName column lid dynamicAddress
active linkToQuery dataType connectStr query dataSource headerSource mainDocumentType destination viewMergedData  mailAsAttachment doNotSuppressBlankLines
""".split())

# Vorfahren, für die Verschachtelungen aufgezeichnet werden
VORFAHREN = ("w:tbl", "w:tc", "w:tr", "w:txbxContent", "w:sdt", "w:sdtContent", "w:ins", "w:del", "w:moveFrom", "w:moveTo", "w:footnote", "w:endnote", "w:comment",
             "w:hdr", "w:ftr", "w:hyperlink", "w:fldSimple", "w:smartTag", "mc:AlternateContent", "mc:Fallback", "mc:Choice", "w:pict", "w:object", "w:drawing",
             "wp:anchor", "wp:inline", "wps:txbx", "wpg:wgp", "wpg:grpSp", "w:oMath", "m:oMath", "m:oMathPara", "w:pPr", "w:rPr", "w:sectPr", "w:ruby", "pic:spPr",
             "w:lvl", "w:tblPr", "w:tcPr", "w:p")

# Eigenschaften, die auch über Formatvorlagen (Vererbung) wirken
VERERBBAR = ("w:b", "w:i", "w:u", "w:strike", "w:caps", "w:smallCaps", "w:color", "w:sz", "w:rFonts", "w:highlight", "w:vertAlign", "w:spacing", "w:ind", "w:jc",
             "w:keepNext", "w:pageBreakBefore", "w:pBdr", "w:shd", "w:numPr", "w:tabs", "w:tblBorders", "w:tcBorders", "w:tblCellMar", "w:vanish", "w:w",
             "w:kern", "w:position", "w:effect", "w:emboss", "w:imprint", "w:outline", "w:shadow", "w:dstrike", "w:rtl", "w:bidi", "w:lang", "w:widowControl",
             "w:contextualSpacing", "w:outlineLvl", "w:textDirection", "w:keepLines", "w:suppressAutoHyphens", "w:tblW", "w:tblLayout", "w:tblInd", "w:vAlign")

# ---- Funktionskatalog -------------------------------------------------------------------------------------------------
# (Kennung, Bereich, Name, Regel, Empfehlung für ein fehlendes Testdokument)
_E = lambda t: ("el", t)                                       # noqa: E731
_A = lambda t, a, v=None: ("attr", t, a, v)                    # noqa: E731
_I = lambda k, v: ("in", k, v)                                 # noqa: E731
_ANY = lambda *r: ("any", *r)                                  # noqa: E731

ZEICHEN = "Zeichenformatierung"
ABSATZ = "Absatzformatierung"
SEITE = "Seitenlayout"
TABELLE = "Tabellen"
GRAFIK = "Grafiken und Zeichnungsobjekte"
WEITER = "Weitere Dokumentfunktionen"
STRUKTUR = "Struktur und Paket"
FORMAT = "OOXML-Variante und Kompatibilität"
NUMMER = "Nummerierung und Listen"
STILE = "Formatvorlagen und Themes"
KOMBI = "Funktionskombinationen"

KATALOG: tuple[tuple, ...] = (
    # --- Zeichenformatierung
    ("z.schriftart", ZEICHEN, "Schriftart direkt gesetzt (rFonts)", _A("w:rFonts", "w:ascii"), "Absätze in mindestens fünf Schriftarten (Serif, Sans, Mono, Schreibschrift)."),
    ("z.schriftart_ost", ZEICHEN, "Schriftart für Ostasien/Komplex (eastAsia, cs)", _ANY(_A("w:rFonts", "w:eastAsia"), _A("w:rFonts", "w:cs")), "Text mit gesetzten eastAsia- und cs-Schriften."),
    ("z.schriftart_thema", ZEICHEN, "Themenschriftart (asciiTheme)", _A("w:rFonts", "w:asciiTheme"), "Text, der ausschließlich Themenschriften (Haupt-/Nebenschrift) benutzt."),
    ("z.groesse", ZEICHEN, "Schriftgröße (sz)", _E("w:sz"), "Text in Größen von 6 pt bis 72 pt, auch halbe Punkte (10,5 pt)."),
    ("z.groesse_cs", ZEICHEN, "Schriftgröße komplexe Schrift (szCs)", _E("w:szCs"), "Arabischer/hebräischer Text mit abweichender szCs."),
    ("z.fett", ZEICHEN, "Fett (b)", _E("w:b"), "Fetter Text direkt formatiert."),
    ("z.kursiv", ZEICHEN, "Kursiv (i)", _E("w:i"), "Kursiver Text direkt formatiert."),
    ("z.fett_cs", ZEICHEN, "Fett/Kursiv komplexe Schrift (bCs, iCs)", _ANY(_E("w:bCs"), _E("w:iCs")), "Fett/kursiv in RTL-Text."),
    ("z.unterstrichen", ZEICHEN, "Unterstreichung (u)", _E("w:u"), "Unterstreichungen: einfach, doppelt, gepunktet, gestrichelt, wellig, dick, Wörter."),
    ("z.unterstrichen_arten", ZEICHEN, "Mehrere Unterstreichungsarten", ("vielfalt", "w:u", "w:val", 3), "Mindestens drei verschiedene Unterstreichungsarten (double, dotted, wave, thick …)."),
    ("z.unterstrichen_farbe", ZEICHEN, "Unterstreichungsfarbe", _A("w:u", "w:color"), "Unterstreichung mit eigener Farbe."),
    ("z.durchgestrichen", ZEICHEN, "Durchstreichung (strike, dstrike)", _ANY(_E("w:strike"), _E("w:dstrike")), "Einfach und doppelt durchgestrichener Text."),
    ("z.hochgestellt", ZEICHEN, "Hochgestellt (vertAlign=superscript)", _A("w:vertAlign", "w:val", "superscript"), "Hochgestellter Text (x², Fußnotenzahlen)."),
    ("z.tiefgestellt", ZEICHEN, "Tiefgestellt (vertAlign=subscript)", _A("w:vertAlign", "w:val", "subscript"), "Tiefgestellter Text (H₂O)."),
    ("z.position", ZEICHEN, "Zeichenposition angehoben/abgesenkt (position)", _E("w:position"), "Text mit positiver und negativer Position in Halbpunkten."),
    ("z.abstand", ZEICHEN, "Zeichenabstand (spacing)", _A("w:spacing", "w:val"), "Text mit erweitertem und gedrängtem Zeichenabstand."),
    ("z.skalierung", ZEICHEN, "Zeichenskalierung (w)", _E("w:w"), "Text mit 50 %, 80 % und 200 % Skalierung."),
    ("z.kerning", ZEICHEN, "Unterschneidung (kern)", _E("w:kern"), "Text mit eingeschalteter Unterschneidung ab bestimmter Größe."),
    ("z.versalien", ZEICHEN, "Großbuchstaben / Kapitälchen (caps, smallCaps)", _ANY(_E("w:caps"), _E("w:smallCaps")), "Text in Versalien und in Kapitälchen."),
    ("z.effekte", ZEICHEN, "Zeicheneffekte (Relief, Gravur, Kontur, Schatten)", _ANY(_E("w:emboss"), _E("w:imprint"), _E("w:outline"), _E("w:shadow")), "Text mit emboss, imprint, outline, shadow."),
    ("z.verborgen", ZEICHEN, "Verborgener Text (vanish)", _E("w:vanish"), "Text mit Attribut „Ausgeblendet“."),
    ("z.texteffekt_w14", ZEICHEN, "Moderne Texteffekte (w14: glow, shadow, reflection, textOutline, textFill)", _ANY(_E("w14:glow"), _E("w14:shadow"), _E("w14:reflection"), _E("w14:textOutline"), _E("w14:textFill"), _E("w14:props3d")), "Text mit Leuchten, Schatten, Spiegelung, Kontur und Farbverlauf."),
    ("z.ligaturen", ZEICHEN, "Ligaturen / Zahlenformen (w14:ligatures, numForm, numSpacing, stylisticSets)", _ANY(_E("w14:ligatures"), _E("w14:numForm"), _E("w14:numSpacing"), _E("w14:stylisticSets"), _E("w14:cntxtAlts")), "OpenType-Funktionen: Ligaturen, Ziffernform, Stilsets."),
    ("z.farbe", ZEICHEN, "Schriftfarbe (color)", _A("w:color", "w:val"), "Text in mehreren Farben (RGB)."),
    ("z.farbe_thema", ZEICHEN, "Themenfarbe mit Tönung (themeColor, themeTint, themeShade)", _A("w:color", "w:themeColor"), "Text mit Themenfarben und Aufhellung/Abdunklung."),
    ("z.hervorhebung", ZEICHEN, "Texthervorhebung (highlight)", _E("w:highlight"), "Text in allen 16 Hervorhebungsfarben."),
    ("z.zeichenschattierung", ZEICHEN, "Zeichenschattierung (rPr/shd)", _I("w:shd", "w:rPr"), "Text mit Zeichenschattierung (auch Muster)."),
    ("z.zeichenrahmen", ZEICHEN, "Zeichenrahmen (rPr/bdr)", _E("w:bdr"), "Text mit Rahmen um die Zeichen."),
    ("z.sprache", ZEICHEN, "Sprachzuweisung (lang)", _E("w:lang"), "Abschnitte in Deutsch, Englisch, Französisch, Arabisch, Japanisch."),
    ("z.sprache_ost", ZEICHEN, "Sprache Ostasien/Komplex (lang eastAsia, bidi)", _ANY(_A("w:lang", "w:eastAsia"), _A("w:lang", "w:bidi")), "Text mit gesetzten eastAsia- und bidi-Sprachen."),
    ("z.nicht_pruefen", ZEICHEN, "Rechtschreibprüfung aus (noProof)", _E("w:noProof"), "Text mit „Rechtschreibung nicht prüfen“."),
    ("z.zeichenformatvorlage", ZEICHEN, "Zeichenformatvorlage verwendet (rStyle)", _E("w:rStyle"), "Text mit mehreren Zeichenformatvorlagen."),
    ("z.symbol", ZEICHEN, "Symbolzeichen (sym)", _E("w:sym"), "Symbole aus Wingdings/Symbol als w:sym."),
    ("z.sonderzeichen", ZEICHEN, "Sonderzeichen (Tab, Zeilenumbruch, weicher Bindestrich, geschützter Bindestrich)", _ANY(_E("w:noBreakHyphen"), _E("w:softHyphen"), _E("w:cr")), "Text mit geschütztem und weichem Bindestrich."),
    ("z.ruby", ZEICHEN, "Phonetische Hilfszeichen (ruby)", _E("w:ruby"), "Japanischer Text mit Furigana."),
    ("z.zeichen_ausrichtung", ZEICHEN, "Ostasiatische Zeichenlayouts (eastAsianLayout, fitText)", _ANY(_E("w:eastAsianLayout"), _E("w:fitText")), "Text mit Horizontal-in-Vertikal, Zeichen anpassen."),
    ("z.emphasis", ZEICHEN, "Betonungszeichen (em)", _E("w:em"), "Text mit Betonungspunkten."),
    # --- Absatzformatierung
    ("a.ausrichtung", ABSATZ, "Absatzausrichtung (jc: links, zentriert, rechts, Blocksatz)", _A("w:jc", "w:val"), "Je ein Absatz links, mittig, rechts, Blocksatz, verteilt."),
    ("a.ausrichtung_arten", ABSATZ, "Mehrere Ausrichtungsarten", ("vielfalt", "w:jc", "w:val", 3), "Mindestens drei verschiedene jc-Werte."),
    ("a.einzug_links_rechts", ABSATZ, "Einzug links/rechts (ind)", _ANY(_A("w:ind", "w:left"), _A("w:ind", "w:start"), _A("w:ind", "w:right"), _A("w:ind", "w:end")), "Absätze mit linkem und rechtem Einzug."),
    ("a.einzug_erstzeile", ABSATZ, "Erstzeileneinzug / hängender Einzug", _ANY(_A("w:ind", "w:firstLine"), _A("w:ind", "w:hanging")), "Absätze mit Erstzeileneinzug und hängendem Einzug."),
    ("a.einzug_zeichen", ABSATZ, "Einzug in Zeichen (leftChars, firstLineChars)", _ANY(_A("w:ind", "w:leftChars"), _A("w:ind", "w:firstLineChars"), _A("w:ind", "w:hangingChars")), "Einzug in Zeicheneinheiten (ostasiatisch)."),
    ("a.tabulatoren", ABSATZ, "Tabstopps (tabs)", _E("w:tabs"), "Absätze mit Tabs links, zentriert, rechts, dezimal, Leiter ( . - _ )."),
    ("a.tab_arten", ABSATZ, "Mehrere Tabulatorarten", ("vielfalt", "w:tab", "w:val", 3), "Mindestens drei Tabulatorarten (left, center, right, decimal, bar)."),
    ("a.tab_fuellzeichen", ABSATZ, "Tab-Füllzeichen (leader)", _A("w:tab", "w:leader"), "Tabs mit Punkt-, Strich-, Unterstrich-Füllung."),
    ("a.zeilenabstand", ABSATZ, "Zeilenabstand (spacing line)", _A("w:spacing", "w:line"), "Absätze mit einfachem, 1,5-fachem, doppeltem, genauem und mindestens-Zeilenabstand."),
    ("a.zeilenabstand_regel", ABSATZ, "Zeilenabstandsregel (lineRule exact/atLeast)", _ANY(_A("w:spacing", "w:lineRule", "exact"), _A("w:spacing", "w:lineRule", "atLeast")), "Absätze mit genauem und mindestens-Abstand."),
    ("a.abstand_vor_nach", ABSATZ, "Abstand vor/nach (before, after)", _ANY(_A("w:spacing", "w:before"), _A("w:spacing", "w:after")), "Absätze mit Abstand vor und nach."),
    ("a.abstand_auto", ABSATZ, "Automatischer Abstand (beforeAutospacing)", _ANY(_A("w:spacing", "w:beforeAutospacing"), _A("w:spacing", "w:afterAutospacing")), "HTML-artiger automatischer Absatzabstand."),
    ("a.abstand_zeilen", ABSATZ, "Abstand in Zeilen (beforeLines, afterLines)", _ANY(_A("w:spacing", "w:beforeLines"), _A("w:spacing", "w:afterLines")), "Absatzabstand in Zeilen."),
    ("a.kein_abstand_gleich", ABSATZ, "Kein Abstand zwischen gleichen Formaten (contextualSpacing)", _E("w:contextualSpacing"), "Listenabsätze mit contextualSpacing."),
    ("a.rahmen", ABSATZ, "Absatzrahmen (pBdr)", _E("w:pBdr"), "Absätze mit Rahmen oben/unten/links/rechts und Linienarten."),
    ("a.rahmen_zwischen", ABSATZ, "Rahmen zwischen Absätzen (between, bar)", _ANY(_E("w:between"), _E("w:bar")), "Aufeinanderfolgende Absätze mit between-Rahmen."),
    ("a.schattierung", ABSATZ, "Absatzschattierung (shd)", _I("w:shd", "w:pPr"), "Absätze mit Füllfarbe und Muster."),
    ("a.zusammenhalten", ABSATZ, "Absatzkontrolle: zusammenhalten / mit nächstem (keepLines, keepNext)", _ANY(_E("w:keepLines"), _E("w:keepNext")), "Absatz, der nicht getrennt wird, und Überschrift mit nächstem Absatz."),
    ("a.seitenumbruch_vor", ABSATZ, "Seitenumbruch davor (pageBreakBefore)", _E("w:pageBreakBefore"), "Absatz mit „Seitenumbruch davor“."),
    ("a.witwen", ABSATZ, "Schusterjungen/Hurenkinder (widowControl)", _E("w:widowControl"), "Absätze mit ein- und ausgeschalteter Kontrolle."),
    ("a.zeilennummern_aus", ABSATZ, "Zeilennummern unterdrücken (suppressLineNumbers)", _E("w:suppressLineNumbers"), "Absatz in nummeriertem Bereich ohne Zeilennummer."),
    ("a.silbentrennung_aus", ABSATZ, "Keine Silbentrennung (suppressAutoHyphens)", _E("w:suppressAutoHyphens"), "Absatz ohne automatische Silbentrennung."),
    ("a.gliederungsebene", ABSATZ, "Gliederungsebene (outlineLvl)", _E("w:outlineLvl"), "Absätze auf Gliederungsebenen 1 bis 9."),
    ("a.rahmenabsatz", ABSATZ, "Positionsrahmen (framePr)", _E("w:framePr"), "Absatz in einem Positionsrahmen mit Umfluss."),
    ("a.textrichtung", ABSATZ, "Textrichtung (textDirection)", _E("w:textDirection"), "Absätze/Zellen mit vertikaler Textrichtung (tbRl, btLr)."),
    ("a.textausrichtung", ABSATZ, "Vertikale Textausrichtung in der Zeile (textAlignment)", _E("w:textAlignment"), "Absatz mit top/center/baseline/bottom."),
    ("a.spiegeleinzug", ABSATZ, "Spiegeleinzüge (mirrorIndents)", _E("w:mirrorIndents"), "Absatz mit gespiegelten Einzügen."),
    ("a.absatzformatvorlage", ABSATZ, "Absatzformatvorlage verwendet (pStyle)", _E("w:pStyle"), "Absätze in mehreren Formatvorlagen (Überschriften, Zitat, Listenabsatz)."),
    ("a.leerer_absatz", ABSATZ, "Leere Absätze und Absatzmarken-Format", _I("w:rPr", "w:pPr"), "Leere Absätze mit eigener Absatzmarken-Formatierung."),
    ("a.ostasiatisch", ABSATZ, "Ostasiatische Absatzregeln (kinsoku, wordWrap, overflowPunct, autoSpaceDE)", _ANY(_E("w:kinsoku"), _E("w:wordWrap"), _E("w:overflowPunct"), _E("w:topLinePunct"), _E("w:autoSpaceDE"), _E("w:autoSpaceDN")), "Japanischer/chinesischer Absatz mit Umbruchregeln."),
    ("a.raster", ABSATZ, "Am Raster ausrichten (snapToGrid)", _E("w:snapToGrid"), "Absatz mit Rasterausrichtung (docGrid)."),
    ("a.vererbt_format", ABSATZ, "Absatz-/Zeicheneigenschaften nur über Formatvorlagen (Vererbung)", ("vererbt_irgendwas",), "Dokument, das Formatierung ausschließlich über Vorlagen mit basedOn-Ketten setzt."),
    # --- Formatvorlagen / Themes / Nummerierung
    ("s.styles", STILE, "Formatvorlagen vorhanden (styles.xml)", _E("w:style"), "Dokument mit benutzerdefinierten Formatvorlagen."),
    ("s.basedon", STILE, "Vorlagenvererbung (basedOn)", _E("w:basedOn"), "Vorlagenkette mit mindestens drei Stufen."),
    ("s.basedon_tief", STILE, "Vererbungskette mit mindestens drei Stufen", ("kette", 3), "Vorlage A ← B ← C ← D, jede ändert eine Eigenschaft."),
    ("s.next_link", STILE, "Folgevorlage und verknüpfte Vorlage (next, link)", _ANY(_E("w:next"), _E("w:link")), "Vorlage mit Folgevorlage und Zeichen-/Absatz-Verknüpfung."),
    ("s.tabellenvorlage", STILE, "Tabellenformatvorlage mit bedingter Formatierung (tblStylePr)", _E("w:tblStylePr"), "Tabelle mit Formatvorlage, erste Zeile/Spalte, Bänderung."),
    ("s.tabellenvorlage_look", STILE, "Tabellenformat-Optionen (tblLook)", _E("w:tblLook"), "Tabelle mit ein-/ausgeschalteten Kopfzeilen-/Bänderungsoptionen."),
    ("s.numerierungsvorlage", STILE, "Listenformatvorlage (numStyleLink, styleLink)", _ANY(_E("w:numStyleLink"), _E("w:styleLink")), "Liste, die über eine Listenformatvorlage verknüpft ist."),
    ("s.doc_defaults", STILE, "Dokumentstandards (docDefaults)", _E("w:docDefaults"), "Dokument mit abweichenden Standardschrift- und Absatzwerten."),
    ("s.latent", STILE, "Latente Formatvorlagen (latentStyles)", _E("w:latentStyles"), "Dokument mit angepassten latenten Vorlagen."),
    ("s.lokalisiert", STILE, "Lokalisierte Standardvorlagennamen (Überschrift 1, Titre 1 …)", ("stilname_fremd",), "Dokument, dessen Vorlagen lokalisiert benannt sind."),
    ("s.theme", STILE, "Dokumentdesign (theme1.xml)", ("teil", "word/theme/theme*.xml"), "Dokument mit angepasstem Design (Farben und Schriften)."),
    ("s.theme_farben", STILE, "Themenfarben und Farbzuordnung (clrSchemeMapping)", _E("w:clrSchemeMapping"), "Dokument mit vertauschter Farbzuordnung (dark/light)."),
    ("s.theme_schriften", STILE, "Themenschriften (themeFontLang)", _E("w:themeFontLang"), "Dokument mit Themenschriften für Ostasien/Komplex."),
    ("s.schriftentabelle", STILE, "Schriftentabelle (fontTable)", ("teil", "word/fontTable.xml"), "Dokument mit mehreren Schriften inkl. Ersatz (altName, panose1)."),
    ("s.schriften_ersatz", STILE, "Schriftersatzangaben (altName, panose1, family, pitch)", _ANY(_E("w:altName"), _E("w:panose1"), _E("w:family")), "Dokument mit nicht installierten Schriften und Ersatzangaben."),
    ("s.schriften_eingebettet", STILE, "Eingebettete Schriften (embedRegular, odttf)", _ANY(_E("w:embedRegular"), _E("w:embedBold"), ("teil", "word/fonts/*")), "Dokument mit eingebetteten Schriften."),
    ("n.nummerierung", NUMMER, "Nummerierung vorhanden (numbering.xml)", _E("w:abstractNum"), "Dokument mit Aufzählung und Nummerierung."),
    ("n.mehrstufig", NUMMER, "Mehrstufige Nummerierung (multiLevelType=multilevel)", _A("w:multiLevelType", "w:val", "multilevel"), "Gliederung 1 / 1.1 / 1.1.1 über neun Ebenen."),
    ("n.stufen", NUMMER, "Mehrere Listenebenen benutzt (ilvl > 0)", ("hoeher", "w:ilvl", "w:val", 1), "Liste, die auf mindestens drei Ebenen benutzt wird."),
    ("n.formate", NUMMER, "Nummerierungsformate (numFmt)", _A("w:numFmt", "w:val"), "Listen mit decimal, upperRoman, lowerLetter, bullet, ordinal, Zahlwörter."),
    ("n.formate_vielfalt", NUMMER, "Mindestens fünf Nummerierungsformate", ("vielfalt", "w:numFmt", "w:val", 5), "Fünf oder mehr verschiedene numFmt-Werte."),
    ("n.formate_ost", NUMMER, "Ostasiatische/komplexe Nummerierung (ideographTraditional, hebrew1, arabicAlpha, thaiNumbers)", _ANY(_A("w:numFmt", "w:val", "ideographTraditional"), _A("w:numFmt", "w:val", "hebrew1"), _A("w:numFmt", "w:val", "arabicAlpha"), _A("w:numFmt", "w:val", "thaiNumbers"), _A("w:numFmt", "w:val", "chineseCounting"), _A("w:numFmt", "w:val", "japaneseCounting"), _A("w:numFmt", "w:val", "hindiNumbers")), "Listen mit Zahlsystemen anderer Schriften."),
    ("n.aufzaehlung_bild", NUMMER, "Bildaufzählungszeichen (numPicBullet)", _E("w:numPicBullet"), "Aufzählung mit Bildsymbol."),
    ("n.aufzaehlung_symbol", NUMMER, "Aufzählung mit Symbolschrift (Symbol, Wingdings)", _ANY(_A("w:rFonts", "w:ascii", "Symbol"), _A("w:rFonts", "w:ascii", "Wingdings")), "Aufzählung mit Symbol-/Wingdings-Zeichen."),
    ("n.neustart", NUMMER, "Neustart/Fortsetzung (startOverride, lvlRestart, start)", _ANY(_E("w:startOverride"), _E("w:lvlRestart"), _A("w:start", "w:val")), "Nummerierungen mit Neustart und abweichendem Startwert."),
    ("n.rechtlich", NUMMER, "Rechtliche Nummerierung (isLgl)", _E("w:isLgl"), "Gliederung 1.1.1 in arabischen Ziffern auch bei römischer Oberebene."),
    ("n.trennzeichen", NUMMER, "Nummerntrennzeichen (suff: tab, space, nothing)", _A("w:suff", "w:val"), "Nummern mit Leerzeichen und ohne Trennzeichen."),
    ("n.lvltext", NUMMER, "Nummerntext mit Platzhaltern (lvlText %1.%2)", _A("w:lvlText", "w:val"), "Nummerntext mit mehreren Platzhaltern und Text (\"Artikel %1\")."),
    ("n.ausrichtung", NUMMER, "Nummernausrichtung (lvlJc)", _A("w:lvlJc", "w:val"), "Nummern rechtsbündig und zentriert."),
    ("n.nummer_zeichenformat", NUMMER, "Zeichenformat der Nummer (lvl/rPr)", _I("w:rPr", "w:lvl"), "Nummer fett/farbig, Text normal."),
    ("n.nummer_absatzformat", NUMMER, "Einzug über Nummerierungsebene (lvl/pPr)", _I("w:pPr", "w:lvl"), "Nummerierung, deren Einzug nur in der Ebene definiert ist."),
    ("n.mehrere_listen", NUMMER, "Mehrere Listeninstanzen (num > 2)", ("min", "w:num", 3), "Dokument mit mindestens drei unabhängigen Listen."),
    ("n.verknuepfung_vorlage", NUMMER, "Nummerierung an Absatzformatvorlage gebunden (lvl/pStyle)", _I("w:pStyle", "w:lvl"), "Überschriftsnummerierung über die Überschriftenvorlagen."),
    ("n.hybrid", NUMMER, "Hybride/einstufige Liste (hybridMultilevel, singleLevel)", _ANY(_A("w:multiLevelType", "w:val", "hybridMultilevel"), _A("w:multiLevelType", "w:val", "singleLevel")), "Von Word erzeugte Standardliste."),
    # --- Seitenlayout
    ("p.seitengroesse", SEITE, "Papierformat (pgSz)", _A("w:pgSz", "w:w"), "Dokument im Format A4 und Letter."),
    ("p.seitengroesse_vielfalt", SEITE, "Mehrere Papierformate im Dokument", ("vielfalt", "w:pgSz", "w:w", 2), "Abschnitte in A4, A3 und Letter."),
    ("p.querformat", SEITE, "Querformat (orient=landscape)", _A("w:pgSz", "w:orient", "landscape"), "Abschnitt im Querformat."),
    ("p.raender", SEITE, "Seitenränder (pgMar)", _A("w:pgMar", "w:top"), "Abschnitte mit sehr kleinen und sehr großen Rändern."),
    ("p.bundsteg", SEITE, "Bundsteg (gutter, gutterAtTop, mirrorMargins)", _ANY(_A("w:pgMar", "w:gutter"), _E("w:gutterAtTop"), _E("w:mirrorMargins")), "Dokument mit Bundsteg und gespiegelten Rändern."),
    ("p.kopf_fuss_abstand", SEITE, "Abstand Kopf-/Fußzeile (pgMar header/footer)", _A("w:pgMar", "w:header"), "Kopf-/Fußzeilenabstand abweichend vom Standard."),
    ("p.abschnitte", SEITE, "Mehrere Abschnitte (sectPr > 1)", ("min", "w:sectPr", 2), "Dokument mit mindestens vier Abschnitten."),
    ("p.abschnitt_typ", SEITE, "Abschnittswechsel-Typ (type)", _A("w:type", "w:val"), "Abschnittswechsel: nächste Seite, fortlaufend, gerade, ungerade Seite."),
    ("p.abschnitt_typ_vielfalt", SEITE, "Mehrere Abschnittswechselarten", ("vielfalt", "w:type", "w:val", 3), "Mindestens drei der Arten nextPage/continuous/evenPage/oddPage/nextColumn."),
    ("p.spalten", SEITE, "Mehrspaltiger Text (cols)", _A("w:cols", "w:num"), "Abschnitt mit zwei, drei Spalten."),
    ("p.spalten_ungleich", SEITE, "Spalten mit ungleicher Breite (col)", _E("w:col"), "Spalten mit individuellen Breiten und Abständen."),
    ("p.spaltenlinie", SEITE, "Trennlinie zwischen Spalten (sep)", _A("w:cols", "w:sep"), "Zweispaltiger Text mit Trennlinie."),
    ("p.spaltenumbruch", SEITE, "Spaltenumbruch (br type=column)", _A("w:br", "w:type", "column"), "Manueller Spaltenumbruch."),
    ("p.seitenumbruch", SEITE, "Manueller Seitenumbruch (br type=page)", _A("w:br", "w:type", "page"), "Dokument mit hartem Seitenumbruch."),
    ("p.textumbruch", SEITE, "Textumbruch-Zeilenumbruch (br clear)", _A("w:br", "w:clear"), "Umbruch, der unter einer Grafik fortsetzt."),
    ("p.kopfzeile", SEITE, "Kopfzeile (header)", ("teil", "word/header*.xml"), "Dokument mit Kopfzeile."),
    ("p.fusszeile", SEITE, "Fußzeile (footer)", ("teil", "word/footer*.xml"), "Dokument mit Fußzeile."),
    ("p.kopffuss_erste", SEITE, "Erste Seite anders (titlePg, headerReference first)", _ANY(_E("w:titlePg"), _A("w:headerReference", "w:type", "first")), "Dokument mit eigener Kopfzeile auf der ersten Seite."),
    ("p.kopffuss_gerade", SEITE, "Gerade/ungerade Seiten unterschiedlich (evenAndOddHeaders)", _E("w:evenAndOddHeaders"), "Dokument mit unterschiedlichen Kopfzeilen für gerade und ungerade Seiten."),
    ("p.kopffuss_verknuepft", SEITE, "Kopf-/Fußzeile pro Abschnitt unterschiedlich", ("min", "w:headerReference", 3), "Abschnitte mit jeweils eigener Kopfzeile."),
    ("p.seitenzahl", SEITE, "Seitenzahlfeld (PAGE)", ("feld", "PAGE"), "Fußzeile mit „Seite X von Y“."),
    ("p.seitenzahl_format", SEITE, "Seitennummerierung (pgNumType)", _E("w:pgNumType"), "Seitenzählung mit römischen Ziffern und Neustart bei 1."),
    ("p.seitenrahmen", SEITE, "Seitenrand/Seitenrahmen (pgBorders)", _E("w:pgBorders"), "Seite mit Rahmen (Linie und Motiv)."),
    ("p.seitenhintergrund", SEITE, "Seitenhintergrund (background)", ("el", "w:background"), "Dokument mit Hintergrundfarbe und displayBackgroundShape."),
    ("p.wasserzeichen", SEITE, "Wasserzeichen (VML in Kopfzeile)", ("wasserzeichen",), "Dokument mit Text-/Bildwasserzeichen."),
    ("p.zeilennummern", SEITE, "Zeilennummerierung (lnNumType)", _E("w:lnNumType"), "Abschnitt mit Zeilennummern, Neustart je Seite."),
    ("p.vertikal_ausrichtung", SEITE, "Vertikale Seitenausrichtung (sectPr/vAlign)", _I("w:vAlign", "w:sectPr"), "Titelseite vertikal zentriert."),
    ("p.dokumentraster", SEITE, "Dokumentraster (docGrid)", _E("w:docGrid"), "Dokument mit Zeichen-/Zeilenraster."),
    ("p.rtl_abschnitt", SEITE, "Abschnitt von rechts nach links (bidi in sectPr)", _I("w:bidi", "w:sectPr"), "Abschnitt mit RTL-Seitenaufbau."),
    ("p.fussnoten_abschnitt", SEITE, "Fußnotenoptionen pro Abschnitt (footnotePr)", _E("w:footnotePr"), "Fußnoten mit Neustart je Seite/Abschnitt und eigenem Zahlenformat."),
    ("p.seitenanzahl", SEITE, "Mehrseitiges Dokument (≥ 20 Absätze, ≥ 1 Umbruch)", ("min", "w:p", 100), "Dokument über mindestens zehn Seiten."),
    # --- Tabellen
    ("t.tabelle", TABELLE, "Tabelle (tbl)", _E("w:tbl"), "Einfache Tabelle."),
    ("t.verbunden_horizontal", TABELLE, "Horizontal verbundene Zellen (gridSpan)", _E("w:gridSpan"), "Tabelle mit horizontal verbundenen Zellen."),
    ("t.verbunden_vertikal", TABELLE, "Vertikal verbundene Zellen (vMerge)", _E("w:vMerge"), "Tabelle mit vertikal verbundenen Zellen."),
    ("t.verbunden_alt", TABELLE, "Alte Zellverbindung (hMerge)", _E("w:hMerge"), "Tabelle, die hMerge benutzt."),
    ("t.verschachtelt", TABELLE, "Verschachtelte Tabellen (tbl in tc)", _I("w:tbl", "w:tc"), "Tabelle in Tabellenzelle, zwei Ebenen."),
    ("t.breite_auto", TABELLE, "Automatische Tabellenbreite (tblW type=auto/pct)", _ANY(_A("w:tblW", "w:type", "auto"), _A("w:tblW", "w:type", "pct")), "Tabelle mit automatischer und prozentualer Breite."),
    ("t.breite_fest", TABELLE, "Feste Tabellenbreite (tblW dxa, tblLayout fixed)", _ANY(_A("w:tblW", "w:type", "dxa"), _A("w:tblLayout", "w:type", "fixed")), "Tabelle mit fester Breite und fixem Layout."),
    ("t.layout_autofit", TABELLE, "Automatisch anpassen (tblLayout autofit)", _A("w:tblLayout", "w:type", "autofit"), "Tabelle, die sich dem Inhalt anpasst."),
    ("t.spaltenbreite", TABELLE, "Spaltenraster (tblGrid)", _E("w:gridCol"), "Tabelle mit unterschiedlich breiten Spalten."),
    ("t.zellbreite", TABELLE, "Zellbreite (tcW)", _E("w:tcW"), "Zellen mit Breite in dxa, pct und auto."),
    ("t.zellrand_innen", TABELLE, "Zellinnenabstände (tblCellMar, tcMar)", _ANY(_E("w:tblCellMar"), _E("w:tcMar")), "Tabellen mit großem Zellinnenabstand, pro Zelle abweichend."),
    ("t.zellabstand", TABELLE, "Zellabstand (tblCellSpacing)", _E("w:tblCellSpacing"), "Tabelle mit Abstand zwischen Zellen."),
    ("t.rahmen_tabelle", TABELLE, "Tabellenrahmen (tblBorders)", _E("w:tblBorders"), "Tabelle mit Außen- und Innenrahmen."),
    ("t.rahmen_zelle", TABELLE, "Zellrahmen (tcBorders)", _E("w:tcBorders"), "Zellen mit individuellen Rahmen."),
    ("t.rahmen_diagonal", TABELLE, "Diagonale Zellrahmen (tl2br, tr2bl)", _ANY(_E("w:tl2br"), _E("w:tr2bl")), "Zelle mit diagonaler Linie."),
    ("t.rahmen_arten", TABELLE, "Linienarten in Rahmen (single, double, dashed, dotted, thick …)", ("vielfalt", "w:top", "w:val", 3), "Rahmen mit mindestens drei Linienarten."),
    ("t.schattierung_zelle", TABELLE, "Zellschattierung (tcPr/shd)", _I("w:shd", "w:tcPr"), "Zellen mit Füll- und Musterschattierung."),
    ("t.schattierung_tabelle", TABELLE, "Tabellenschattierung (tblPr/shd)", _I("w:shd", "w:tblPr"), "Tabelle mit Tabellenfüllung."),
    ("t.kopfzeile_wiederholt", TABELLE, "Wiederholte Überschriftenzeile (tblHeader)", _E("w:tblHeader"), "Tabelle über mehrere Seiten mit Kopfzeile."),
    ("t.zeile_nicht_trennen", TABELLE, "Zeile nicht umbrechen (cantSplit)", _E("w:cantSplit"), "Hohe Zeile, die nicht über Seiten getrennt wird."),
    ("t.zeilenhoehe", TABELLE, "Zeilenhöhe (trHeight exact/atLeast)", _E("w:trHeight"), "Zeilen mit genauer und Mindesthöhe."),
    ("t.position_fliessend", TABELLE, "Tabellenpositionierung (tblpPr)", _E("w:tblpPr"), "Fließende Tabelle mit Textumfluss."),
    ("t.ausrichtung", TABELLE, "Tabellenausrichtung und Einzug (jc, tblInd)", _ANY(_I("w:jc", "w:tblPr"), _E("w:tblInd")), "Tabelle zentriert, rechts, mit Einzug."),
    ("t.vertikal_ausrichtung", TABELLE, "Vertikale Zellausrichtung (tcPr/vAlign)", _I("w:vAlign", "w:tcPr"), "Zellen oben/mittig/unten."),
    ("t.zelle_textrichtung", TABELLE, "Textrichtung in Zelle (tcPr/textDirection)", _I("w:textDirection", "w:tcPr"), "Zellen mit vertikalem Text."),
    ("t.zelle_nowrap", TABELLE, "Zelle ohne Umbruch / Anpassen (noWrap, tcFitText)", _ANY(_E("w:noWrap"), _E("w:tcFitText")), "Zellen mit noWrap und tcFitText."),
    ("t.bidi", TABELLE, "Tabelle von rechts nach links (bidiVisual)", _E("w:bidiVisual"), "RTL-Tabelle."),
    ("t.gridbefore", TABELLE, "Ausgelassene Gitterspalten (gridBefore, gridAfter)", _ANY(_E("w:gridBefore"), _E("w:gridAfter")), "Tabelle mit eingerückten Zeilen durch gridBefore."),
    ("t.seitenuebergreifend", TABELLE, "Seitenübergreifende Tabelle (≥ 40 Zeilen in einer Tabelle)", ("tabellenzeilen", 40), "Eine Tabelle mit mindestens 80 Zeilen."),
    ("t.bedingte_formatierung", TABELLE, "Bedingtes Format (cnfStyle)", _E("w:cnfStyle"), "Tabelle mit cnfStyle an Zeilen/Zellen."),
    ("t.titel_beschreibung", TABELLE, "Alternativtext der Tabelle (tblCaption, tblDescription)", _ANY(_E("w:tblCaption"), _E("w:tblDescription")), "Tabelle mit Titel und Beschreibung."),
    ("t.tabellenaenderung", TABELLE, "Verfolgte Tabellenänderung (tblPrChange, cellIns, trPrChange)", _ANY(_E("w:tblPrChange"), _E("w:cellIns"), _E("w:cellDel"), _E("w:trPrChange"), _E("w:tcPrChange"), _E("w:cellMerge")), "Tabelle mit verfolgten Struktur-/Formatänderungen."),
    ("t.tabelle_in_ausnahme", TABELLE, "Zeilenausnahmen (tblPrEx)", _E("w:tblPrEx"), "Zeilen mit abweichenden Tabelleneigenschaften."),
    # --- Grafiken
    ("g.inline", GRAFIK, "Inline-Grafik (wp:inline)", _E("wp:inline"), "Bild im Text (als Zeichen)."),
    ("g.anker", GRAFIK, "Verankerte Grafik (wp:anchor)", _E("wp:anchor"), "Frei positioniertes Bild."),
    ("g.umfluss_arten", GRAFIK, "Textumfluss (wrapSquare, wrapTight, wrapThrough, wrapTopAndBottom, wrapNone)", ("vielfalt_el", ("wp:wrapSquare", "wp:wrapTight", "wp:wrapThrough", "wp:wrapTopAndBottom", "wp:wrapNone"), 3), "Bilder mit mindestens drei Umflussarten."),
    ("g.umfluss_polygon", GRAFIK, "Konturumfluss (wrapPolygon)", _E("wp:wrapPolygon"), "Bild mit Kontur-Umfluss."),
    ("g.umfluss_abstand", GRAFIK, "Umflussabstand (distT, distB, distL, distR)", _ANY(_A("wp:anchor", "distL"), _A("wp:anchor", "distT")), "Bild mit Abstand zum Text."),
    ("g.position_relativ", GRAFIK, "Position relativ zu Seite/Rand/Absatz (positionH/V relativeFrom)", _A("wp:positionH", "relativeFrom"), "Bilder, positioniert relativ zu Seite, Rand, Absatz, Zeichen."),
    ("g.position_ausrichtung", GRAFIK, "Ausrichtung statt Versatz (wp:align)", _E("wp:align"), "Bild links/zentriert/rechts zur Seite ausgerichtet."),
    ("g.position_prozent", GRAFIK, "Prozentuale Position (wp14:pctPosHOffset)", _ANY(_E("wp14:pctPosHOffset"), _E("wp14:pctPosVOffset")), "Bild mit prozentualer Position."),
    ("g.hinter_text", GRAFIK, "Bild hinter dem Text (behindDoc)", _A("wp:anchor", "behindDoc", "1"), "Bild hinter dem Text."),
    ("g.z_ordnung", GRAFIK, "Z-Reihenfolge (relativeHeight)", _A("wp:anchor", "relativeHeight"), "Überlappende Bilder mit abweichender Z-Ordnung."),
    ("g.zuschnitt", GRAFIK, "Bildzuschnitt (a:srcRect)", _E("a:srcRect"), "Bild mit Zuschnitt auf allen vier Seiten."),
    ("g.skalierung", GRAFIK, "Skalierung/Ausdehnung (wp:extent, a:ext)", _E("wp:extent"), "Bilder verzerrt und proportional skaliert."),
    ("g.drehung", GRAFIK, "Drehung/Spiegelung (a:xfrm rot, flipH, flipV)", _ANY(_A("a:xfrm", "rot"), _A("a:xfrm", "flipH"), _A("a:xfrm", "flipV")), "Bild gedreht und gespiegelt."),
    ("g.bildformat_png_jpg", GRAFIK, "Rasterbilder (PNG, JPEG)", ("teil", "word/media/*.png"), "Dokument mit PNG und JPEG."),
    ("g.bildformat_vektor", GRAFIK, "Vektorbilder (EMF, WMF, SVG)", _ANY(("teil", "word/media/*.emf"), ("teil", "word/media/*.wmf"), ("teil", "word/media/*.svg")), "Dokument mit EMF, WMF und SVG."),
    ("g.bildformat_weitere", GRAFIK, "Weitere Bildformate (GIF, TIFF, BMP, WebP, HEIC)", _ANY(("teil", "word/media/*.gif"), ("teil", "word/media/*.tif*"), ("teil", "word/media/*.bmp"), ("teil", "word/media/*.webp"), ("teil", "word/media/*.hdp")), "Dokument mit GIF, TIFF, BMP, WebP."),
    ("g.bild_effekte", GRAFIK, "Bildeffekte (Transparenz, Helligkeit, Duoton, Künstlerisch)", _ANY(_E("a:alphaModFix"), _E("a:lum"), _E("a:duotone"), _E("a:biLevel"), _E("a:grayscl"), _E("a:clrChange"), _E("a14:imgProps"), _E("a14:artisticBlur")), "Bild mit Transparenz, Graustufen, Helligkeit/Kontrast."),
    ("g.bild_rahmen", GRAFIK, "Bildrahmen und Bildeffekte (a:ln, a:effectLst)", ("in", "a:ln", "pic:spPr"), "Bild mit Rahmen, Schatten, Leuchten, weichen Kanten."),
    ("g.bild_alt", GRAFIK, "Alternativtext (wp:docPr descr)", _A("wp:docPr", "descr"), "Bild mit Alternativtext und Titel."),
    ("g.bild_verknuepft", GRAFIK, "Verknüpftes Bild (r:link)", _A("a:blip", "r:link"), "Bild, das extern verlinkt ist."),
    ("g.bild_in_zelle", GRAFIK, "Bild in Tabellenzelle", ("kombi_in", "w:drawing", "w:tc"), "Tabellenzelle mit Bild."),
    ("g.form", GRAFIK, "Form (wps:wsp, a:prstGeom)", _ANY(_E("wps:wsp"), _E("a:prstGeom")), "Formen: Rechteck, Pfeil, Sprechblase, Stern."),
    ("g.form_freiform", GRAFIK, "Freiform (a:custGeom)", _E("a:custGeom"), "Freihand-/Freiformkontur."),
    ("g.form_fuellung", GRAFIK, "Füllungen (solidFill, gradFill, pattFill, blipFill)", ("vielfalt_el", ("a:solidFill", "a:gradFill", "a:pattFill", "a:blipFill", "a:noFill"), 3), "Formen mit Voll-, Verlauf-, Muster- und Bildfüllung."),
    ("g.form_linie", GRAFIK, "Linienformate (a:ln: Strich, Enden, Pfeile)", _ANY(_E("a:prstDash"), _E("a:headEnd"), _E("a:tailEnd"), _E("a:custDash")), "Linien mit Strichart und Pfeilspitzen."),
    ("g.form_effekte", GRAFIK, "Form-Effekte (Schatten, Leuchten, Spiegelung, 3D)", _ANY(_E("a:outerShdw"), _E("a:innerShdw"), _E("a:glow"), _E("a:reflection"), _E("a:softEdge"), _E("a:scene3d"), _E("a:sp3d")), "Form mit Schatten, Leuchten, Spiegelung, 3D-Drehung."),
    ("g.textfeld", GRAFIK, "Textfeld (wps:txbx / txbxContent)", _E("w:txbxContent"), "Textfeld mit mehreren Absätzen und Tabelle darin."),
    ("g.textfeld_verkettet", GRAFIK, "Verkettete Textfelder (wps:txbx id/seq)", _ANY(_E("wps:linkedTxbx"), _E("v:textbox")), "Zwei verkettete Textfelder."),
    ("g.textfeld_eigenschaften", GRAFIK, "Textfeld-Eigenschaften (wps:bodyPr: Innenabstand, Anker, Autofit)", _ANY(_A("wps:bodyPr", "lIns"), _E("a:spAutoFit"), _E("a:normAutofit")), "Textfeld mit Innenabstand und Autoanpassung."),
    ("g.gruppe", GRAFIK, "Gruppierte Zeichnungsobjekte (wpg:wgp, a:grpSp)", _ANY(_E("wpg:wgp"), _E("a:grpSp")), "Gruppe aus Form, Text und Bild; verschachtelte Gruppen."),
    ("g.gruppe_verschachtelt", GRAFIK, "Verschachtelte Gruppen", _I("wpg:grpSp", "wpg:wgp"), "Gruppe in Gruppe."),
    ("g.zeichenbereich", GRAFIK, "Zeichenbereich (wpc:wpc)", _E("wpc:wpc"), "Zeichenbereich mit mehreren Formen."),
    ("g.smartart", GRAFIK, "SmartArt (dgm)", _ANY(_E("dgm:relIds"), ("teil", "word/diagrams/data*.xml")), "SmartArt-Liste, Prozess und Hierarchie."),
    ("g.smartart_zeichnung", GRAFIK, "SmartArt-Ersatzzeichnung (dsp:drawing)", ("teil", "word/diagrams/drawing*.xml"), "SmartArt mit gespeicherter Zeichnung."),
    ("g.diagramm", GRAFIK, "Diagramm (c:chart)", _ANY(_E("c:chart"), ("teil", "word/charts/chart*.xml")), "Säulen-, Linien-, Kreisdiagramm."),
    ("g.diagramm_arten", GRAFIK, "Mehrere Diagrammarten", ("vielfalt_el", ("c:barChart", "c:lineChart", "c:pieChart", "c:areaChart", "c:scatterChart", "c:radarChart", "c:bubbleChart", "c:doughnutChart", "c:stockChart", "c:surfaceChart", "c:bar3DChart", "c:pie3DChart"), 3), "Mindestens drei Diagrammarten."),
    ("g.diagramm_ex", GRAFIK, "Neue Diagrammarten (cx: Waterfall, Sunburst, Histogramm)", _E("cx:chart"), "Wasserfall-/Sunburst-Diagramm."),
    ("g.diagramm_daten", GRAFIK, "Diagramm mit eingebetteter Arbeitsmappe", ("teil", "word/embeddings/*.xlsx"), "Diagramm mit Datenblatt."),
    ("g.vml", GRAFIK, "VML-Grafik (v:shape, v:rect, v:group, v:imagedata)", _ANY(_E("v:shape"), _E("v:rect"), _E("v:oval"), _E("v:line"), _E("v:group"), _E("v:roundrect"), _E("v:imagedata"), _E("v:shapetype")), "Dokument mit VML-Formen, z. B. aus Word 2003."),
    ("g.vml_textfeld", GRAFIK, "VML-Textfeld (v:textbox)", _E("v:textbox"), "VML-Textfeld."),
    ("g.vml_office", GRAFIK, "Office-VML-Zusätze (o:lock, o:OLEObject, o:gfxdata)", _ANY(_E("o:lock"), _E("o:OLEObject"), _E("o:gfxdata"), _E("o:diagram")), "VML mit Office-Zusätzen."),
    ("g.alternativ_inhalt", GRAFIK, "Alternative Inhalte (mc:AlternateContent, Choice, Fallback)", _E("mc:AlternateContent"), "Form mit DrawingML-Choice und VML-Fallback."),
    ("g.alternativ_requires", GRAFIK, "mc:Choice Requires=wps/wpg/w14", _A("mc:Choice", "Requires"), "Alternativer Inhalt mit Requires=wps."),
    ("g.ignorable", GRAFIK, "mc:Ignorable (Erweiterungen verschiedener Word-Versionen)", _A("w:document", "mc:Ignorable"), "Dokument mit mc:Ignorable=w14 w15 wp14."),
    ("g.ink", GRAFIK, "Freihandtinte (inkml, aink)", _ANY(_E("aink:contentPart"), ("teil", "word/ink/*"), _E("w:contentPart")), "Dokument mit Freihandzeichnung."),
    ("g.modell3d", GRAFIK, "3D-Modell (am3d)", _E("am3d:model3d"), "Dokument mit 3D-Modell."),
    ("g.hyperlink_bild", GRAFIK, "Hyperlink auf Grafik (a:hlinkClick)", _E("a:hlinkClick"), "Bild mit Hyperlink."),
    ("g.crop_form", GRAFIK, "Bild in Form (pic:spPr prstGeom)", _I("a:prstGeom", "pic:spPr"), "Bild, zugeschnitten auf Ellipse/abgerundetes Rechteck."),
    # --- Weitere Funktionen
    ("w.inhaltsverzeichnis", WEITER, "Inhaltsverzeichnis (TOC)", ("feld", "TOC"), "Dokument mit Inhaltsverzeichnis, Ebenen 1–3 und Hyperlinks."),
    ("w.inhaltsverzeichnis_sdt", WEITER, "Verzeichnis als Inhaltssteuerelement (docPartGallery Table of Contents)", _A("w:docPartGallery", "w:val", "Table of Contents"), "Von Word eingefügtes Inhaltsverzeichnis."),
    ("w.verzeichnis_weitere", WEITER, "Weitere Verzeichnisse (TOA, Index, Abbildungen)", _ANY(("feld", "INDEX"), ("feld", "TOA"), ("feld", "TC"), ("feld", "XE")), "Stichwortverzeichnis und Abbildungsverzeichnis."),
    ("w.querverweis", WEITER, "Querverweise (REF, PAGEREF, NOTEREF)", _ANY(("feld", "REF"), ("feld", "PAGEREF"), ("feld", "NOTEREF")), "Querverweise auf Überschriften, Lesezeichen, Abbildungen."),
    ("w.felder_komplex", WEITER, "Komplexe Felder (fldChar begin/separate/end)", _E("w:fldChar"), "Mehrere komplexe Felder, auch verschachtelt."),
    ("w.felder_einfach", WEITER, "Einfache Felder (fldSimple)", _E("w:fldSimple"), "Datum, Seitenzahl als fldSimple."),
    ("w.felder_arten", WEITER, "Verschiedene Feldarten (DATE, TIME, SEQ, IF, =, MERGEFIELD, STYLEREF, SAVEDATE, DOCPROPERTY)", ("feldvielfalt", 4), "Mindestens vier verschiedene Feldfunktionen."),
    ("w.felder_seq", WEITER, "Beschriftungen (SEQ)", ("feld", "SEQ"), "Abbildungen und Tabellen mit Beschriftung."),
    ("w.felder_formel", WEITER, "Formelfelder (= SUM)", ("feld", "="), "Tabelle mit =SUM(ABOVE)."),
    ("w.felder_seriendruck", WEITER, "Seriendruckfelder (MERGEFIELD, mailMerge)", _ANY(("feld", "MERGEFIELD"), _E("w:mailMerge")), "Seriendruckdokument."),
    ("w.felder_verschachtelt", WEITER, "Verschachtelte Felder", ("feld_verschachtelt",), "IF-Feld, das ein MERGEFIELD enthält."),
    ("w.felder_dirty", WEITER, "Felder, die beim Öffnen aktualisiert werden (dirty, updateFields)", _ANY(_A("w:fldChar", "w:dirty"), _E("w:updateFields")), "Dokument mit updateFields."),
    ("w.lesezeichen", WEITER, "Lesezeichen (bookmarkStart)", _E("w:bookmarkStart"), "Lesezeichen mit Bereich und Verweis."),
    ("w.hyperlink_extern", WEITER, "Externe Hyperlinks (r:id, TargetMode=External)", ("rel_extern", "hyperlink"), "Hyperlinks auf Webadressen und Mailadressen."),
    ("w.hyperlink_intern", WEITER, "Interne Hyperlinks (w:anchor)", _A("w:hyperlink", "w:anchor"), "Link auf Lesezeichen."),
    ("w.fussnote", WEITER, "Fußnoten (footnoteReference)", _E("w:footnoteReference"), "Dokument mit zehn Fußnoten, auch mit Tabelle und Formatierung darin."),
    ("w.endnote", WEITER, "Endnoten (endnoteReference)", _E("w:endnoteReference"), "Dokument mit Endnoten."),
    ("w.fussnote_format", WEITER, "Eigenes Fußnotenzeichen (customMark) und Zahlenformat", _ANY(_A("w:footnoteReference", "w:customMarkFollows"), _A("w:footnotePr", "w:numFmt")), "Fußnoten mit Sternchen oder römischen Ziffern."),
    ("w.fussnote_trennlinie", WEITER, "Fußnotentrennlinien (separator, continuationSeparator)", _E("w:continuationSeparator"), "Fußnoten, die auf die Folgeseite laufen."),
    ("w.kommentar", WEITER, "Kommentare (comments.xml)", _E("w:comment"), "Dokument mit Kommentaren verschiedener Autoren."),
    ("w.kommentar_antwort", WEITER, "Kommentarantworten (commentsExtended paraIdParent)", _ANY(_E("w15:commentEx"), _A("w15:commentEx", "w15:paraIdParent")), "Kommentar mit Antworten und erledigt-Status."),
    ("w.kommentar_formatiert", WEITER, "Kommentar mit Formatierung/Bild", _I("w:r", "w:comment"), "Kommentar mit mehreren Absätzen und Formatierung."),
    ("w.kommentar_bereich", WEITER, "Kommentarbereich (commentRangeStart)", _E("w:commentRangeStart"), "Kommentar auf einem Textbereich über mehrere Absätze."),
    ("w.aenderungen_einfuegen", WEITER, "Verfolgte Einfügung (ins)", ("el", "w:ins"), "Dokument mit eingefügtem Text von zwei Autoren."),
    ("w.aenderungen_loeschen", WEITER, "Verfolgte Löschung (del, delText)", _E("w:delText"), "Dokument mit gelöschtem Text."),
    ("w.aenderungen_verschieben", WEITER, "Verfolgte Verschiebung (moveFrom, moveTo)", _ANY(_E("w:moveFrom"), _E("w:moveTo")), "Absatz, der verschoben wurde."),
    ("w.aenderungen_format", WEITER, "Verfolgte Formatänderung (rPrChange, pPrChange, sectPrChange)", _ANY(_E("w:rPrChange"), _E("w:pPrChange"), _E("w:sectPrChange")), "Fett gesetzt, Einzug geändert mit Verfolgung."),
    ("w.aenderungen_nummerierung", WEITER, "Verfolgte Änderung an Nummerierung (numberingChange)", _E("w:numberingChange"), "Verfolgte Listenänderung."),
    ("w.aenderungen_absatzmarke", WEITER, "Verfolgte Absatzmarke (rPr/ins, rPr/del)", ("in", "w:ins", "w:rPr"), "Eingefügter und gelöschter Absatzumbruch."),
    ("w.aenderungen_autoren", WEITER, "Mehrere Autoren und Zeitstempel (w:author, w:date)", ("vielfalt", "w:ins", "w:author", 2), "Änderungen von mindestens zwei Autoren."),
    ("w.aenderungen_einstellung", WEITER, "Änderungsverfolgung eingeschaltet (trackRevisions)", _E("w:trackRevisions"), "Dokument mit aktiver Verfolgung."),
    ("w.rsid", WEITER, "Überarbeitungskennungen (rsid)", _ANY(_E("w:rsids"), _A("w:p", "w:rsidR")), "Von Word gespeichertes Dokument mit rsids."),
    ("w.formel", WEITER, "Mathematische Formeln (m:oMath)", _E("m:oMath"), "Brüche, Wurzeln, Summen, Matrizen."),
    ("w.formel_block", WEITER, "Formelblock (m:oMathPara)", _E("m:oMathPara"), "Abgesetzte Formel mit Ausrichtung."),
    ("w.formel_arten", WEITER, "Formelstrukturen (m:f, m:rad, m:nary, m:d, m:m, m:sSup, m:sSub, m:func, m:acc)", ("vielfalt_el", ("m:f", "m:rad", "m:nary", "m:d", "m:m", "m:sSup", "m:sSub", "m:sSubSup", "m:func", "m:acc", "m:bar", "m:eqArr", "m:limLow", "m:limUpp", "m:groupChr", "m:box", "m:borderBox", "m:phant"), 5), "Formeln mit mindestens fünf verschiedenen Strukturen."),
    ("w.formel_einstellungen", WEITER, "Formeleinstellungen (m:mathPr)", _E("m:mathPr"), "Dokument mit Math-Schriftart und Ausrichtung."),
    ("w.formel_in_text", WEITER, "Formel im Fließtext und in Tabelle", ("kombi_in", "m:oMath", "w:tc"), "Formel in Tabellenzelle."),
    ("w.inhaltssteuerelement", WEITER, "Inhaltssteuerelemente (sdt)", _E("w:sdt"), "Rich-Text-, Klartext-Steuerelement."),
    ("w.sdt_arten", WEITER, "Steuerelementtypen (Kombinationsfeld, Dropdown, Datum, Kontrollkästchen, Bild)", ("vielfalt_el", ("w:comboBox", "w:dropDownList", "w:date", "w:checkbox", "w14:checkbox", "w:picture", "w:text", "w:richText", "w:docPartObj", "w:citation", "w:bibliography", "w:group", "w:equation"), 4), "Mindestens vier Typen von Inhaltssteuerelementen."),
    ("w.sdt_bindung", WEITER, "Datenbindung (dataBinding)", _E("w:dataBinding"), "Steuerelement mit XML-Bindung."),
    ("w.sdt_platzhalter", WEITER, "Platzhaltertext (showingPlcHdr)", _E("w:showingPlcHdr"), "Leeres Steuerelement mit Platzhalter."),
    ("w.sdt_sperre", WEITER, "Steuerelement gesperrt (lock)", _E("w:lock"), "Steuerelement, nicht löschbar."),
    ("w.sdt_block_zeile", WEITER, "Block-, Zeilen- und Zellsteuerelement", ("sdt_ebenen",), "Steuerelemente auf Absatz-, Zeilen- und Zellebene."),
    ("w.formularfelder", WEITER, "Ältere Formularfelder (legacy: ffData, textInput, checkBox)", _ANY(_E("w:ffData"), _E("w:textInput"), _E("w:checkBox")), "Formular mit Textfeld, Kontrollkästchen, Liste."),
    ("w.activex", WEITER, "ActiveX-Steuerelemente", _ANY(_E("w:control"), ("teil", "word/activeX/*")), "Dokument mit ActiveX-Steuerelement."),
    ("w.makros", WEITER, "VBA-Makros (vbaProject)", ("teil", "word/vbaProject.bin"), "Dokument mit Makros (.docm)."),
    ("w.eingebettet_ole", WEITER, "Eingebettete Objekte (w:object, OLE)", _ANY(_E("w:object"), _E("o:OLEObject")), "Eingebettete Excel-Tabelle als OLE-Objekt."),
    ("w.eingebettet_paket", WEITER, "Eingebettete Pakete (word/embeddings)", ("teil", "word/embeddings/*"), "Dokument mit eingebetteter Arbeitsmappe und PDF."),
    ("w.eingebettet_dokument", WEITER, "Eingebettete Dokumente (altChunk, subDoc)", _ANY(_E("w:altChunk"), _E("w:subDoc")), "Dokument mit eingebettetem HTML/DOCX (altChunk)."),
    ("w.benutzerdefiniert_xml", WEITER, "Benutzerdefinierte XML-Daten (customXml)", _ANY(("teil", "customXml/item*.xml"), _E("w:customXml")), "Dokument mit Custom-XML-Part."),
    ("w.benutzerdefiniert_bibliographie", WEITER, "Literaturverzeichnis (b:Sources)", _E("b:Sources"), "Dokument mit Quellen und Zitaten."),
    ("w.dokumenteigenschaften", WEITER, "Dokumenteigenschaften (core.xml)", ("teil", "docProps/core.xml"), "Dokument mit Titel, Autor, Schlagwörtern."),
    ("w.dokumenteigenschaften_ext", WEITER, "Erweiterte Eigenschaften (app.xml)", ("teil", "docProps/app.xml"), "Dokument mit Statistik (Seiten, Wörter)."),
    ("w.dokumenteigenschaften_benutzer", WEITER, "Benutzerdefinierte Eigenschaften (custom.xml)", ("teil", "docProps/custom.xml"), "Dokument mit benutzerdefinierten Eigenschaften und DOCPROPERTY."),
    ("w.vorschaubild", WEITER, "Vorschaubild (thumbnail)", ("teil", "docProps/thumbnail.*"), "Dokument mit Vorschaubild."),
    ("w.dokumentschutz", WEITER, "Dokumentschutz (documentProtection)", _E("w:documentProtection"), "Dokument mit Bearbeitungseinschränkung (Formular, Kommentare, Änderungen)."),
    ("w.schreibschutz", WEITER, "Schreibschutzempfehlung (writeProtection)", _E("w:writeProtection"), "Dokument mit Schreibschutzempfehlung."),
    ("w.berechtigungen", WEITER, "Bearbeitungsbereiche (permStart, permEnd)", _E("w:permStart"), "Geschütztes Dokument mit freigegebenem Bereich."),
    ("w.signatur", WEITER, "Digitale Signatur (_xmlsignatures)", ("teil", "_xmlsignatures/*"), "Signiertes Dokument."),
    ("w.verschluesselt", WEITER, "Verschlüsseltes Paket (EncryptedPackage, kein ZIP)", ("verschluesselt",), "Kennwortgeschütztes Dokument."),
    ("w.rtl_absatz", WEITER, "Rechts-nach-links-Absatz (bidi)", _I("w:bidi", "w:pPr"), "Arabischer/hebräischer Absatz, Absatzrichtung RTL."),
    ("w.rtl_text", WEITER, "RTL-Zeichen (rtl, cs)", _E("w:rtl"), "Hebräischer Text mit rtl-Lauf."),
    ("w.rtl_gemischt", WEITER, "Gemischte Schreibrichtungen im Absatz", ("kombi", "w.rtl_text", "z.sprache"), "Absatz aus deutschem und arabischem Text mit Zahlen."),
    ("w.rtl_tabelle_liste", WEITER, "RTL in Tabelle und Liste", ("kombi", "w.rtl_absatz", "n.nummerierung", "t.bidi"), "RTL-Tabelle mit nummerierter RTL-Liste."),
    ("w.asiatisch", WEITER, "Asiatische Schriftsysteme (eastAsia)", ("kombi", "z.schriftart_ost", "z.sprache_ost"), "Japanisch, Chinesisch, Koreanisch mit eastAsia-Schrift."),
    ("w.asiatisch_vertikal", WEITER, "Vertikaler asiatischer Text", ("kombi", "a.textrichtung", "w.asiatisch"), "Japanischer Text mit tbRl."),
    ("w.sprachen_gemischt", WEITER, "Gemischte Sprachen (≥ 3 lang-Werte)", ("vielfalt", "w:lang", "w:val", 3), "Text in mindestens drei Sprachen."),
    ("w.komplexe_schrift", WEITER, "Komplexe Schriften (Thai, Devanagari, Arabisch mit cs)", ("kombi", "z.groesse_cs", "w.rtl_text"), "Text in Thai/Hindi mit cs-Schrift."),
    ("w.smarttag", WEITER, "Smarttags (smartTag)", _E("w:smartTag"), "Dokument mit Smarttag."),
    ("w.glossar", WEITER, "Glossar / Bausteine (glossaryDocument)", ("teil", "word/glossary/*"), "Dokument mit Bausteinen."),
    ("w.webeinstellungen", WEITER, "Webeinstellungen (webSettings)", ("teil", "word/webSettings.xml"), "Dokument mit webSettings."),
    ("w.begleitdokument", WEITER, "Angefügte Vorlage (attachedTemplate)", _E("w:attachedTemplate"), "Dokument mit verknüpfter Vorlage."),
    ("w.hdr_ftr_feld", WEITER, "Felder in Kopf-/Fußzeile", ("kombi_in", "w:fldChar", "w:hdr"), "Kopfzeile mit Datum und Dokumenttitel."),
    ("w.leer", WEITER, "Leeres Dokument (kein Text)", ("leer",), "Leeres Dokument mit nur einem Absatz."),
    ("w.sehr_gross", WEITER, "Sehr großes Dokument (≥ 5 MB oder ≥ 1000 Absätze)", ("gross",), "Dokument mit mehr als 1000 Absätzen und vielen Bildern."),
    ("w.zeichensatz", WEITER, "Unicode jenseits der BMP / Emoji", ("unicode_hoch",), "Text mit Emoji und CJK-Erweiterung B."),
    ("w.bild_text_umbruch_mix", WEITER, "Dokument mit Fließtext, Bild und Tabelle gemischt", ("kombi", "g.inline", "t.tabelle", "a.absatzformatvorlage"), "Realistisches Fachdokument."),
    # --- Variante und Kompatibilität
    ("o.transitional", FORMAT, "Transitional-OOXML", ("transitional",), "Dokument im Transitional-Format (Standard von Word)."),
    ("o.strict", FORMAT, "Strict-OOXML", ("strict",), "Dokument, als „Strict Open XML“ gespeichert."),
    ("o.kompat_modus_word2003", FORMAT, "Kompatibilitätsmodus Word 2003 (compatibilityMode ≤ 11)", ("kompat_modus", 0, 11), "Dokument im Kompatibilitätsmodus Word 2003."),
    ("o.kompat_modus_word2007", FORMAT, "Kompatibilitätsmodus Word 2007 (12)", ("kompat_modus", 12, 12), "Dokument im Kompatibilitätsmodus Word 2007."),
    ("o.kompat_modus_word2010", FORMAT, "Kompatibilitätsmodus Word 2010 (14)", ("kompat_modus", 14, 14), "Dokument im Kompatibilitätsmodus Word 2010."),
    ("o.kompat_modus_word2013", FORMAT, "Word 2013 und neuer (15)", ("kompat_modus", 15, 99), "Dokument im aktuellen Word-Modus."),
    ("o.kompat_einstellungen", FORMAT, "Kompatibilitätseinstellungen (compat)", _E("w:compat"), "Dokument mit vielen compat-Optionen."),
    ("o.kompat_einstellung_namen", FORMAT, "compatSetting-Einträge", _E("w:compatSetting"), "Dokument mit compatSetting-Einträgen (overrideTableStyleFontSizeAndJustification …)."),
    ("o.kompat_alt", FORMAT, "Alte Kompatibilitätsoptionen (z. B. useWord97LineBreakRules, noTabHangInd)", _ANY(_E("w:useWord97LineBreakRules"), _E("w:noTabHangInd"), _E("w:lineWrapLikeWord6"), _E("w:doNotExpandShiftReturn"), _E("w:usePrinterMetrics"), _E("w:suppressSpBfAfterPgBrk"), _E("w:wpJustification"), _E("w:splitPgBreakAndParaMark"), _E("w:doNotUseHTMLParagraphAutoSpacing")), "Dokument aus Word 97–2003 mit alten Optionen."),
    ("o.erweiterung_w14", FORMAT, "Word-2010-Erweiterungen (w14)", ("ns", "w14"), "Dokument mit w14-Attributen (paraId, checkbox)."),
    ("o.erweiterung_w15", FORMAT, "Word-2013-Erweiterungen (w15)", ("ns", "w15"), "Dokument mit w15 (Kommentarantworten, collapsed, person)."),
    ("o.erweiterung_w16", FORMAT, "Word-2016+-Erweiterungen (w16*)", _ANY(("ns", "w16"), ("ns", "w16cid"), ("ns", "w16cex"), ("ns", "w16se"), ("ns", "w16du"), ("ns", "w16sdtdh")), "Dokument aus aktuellem Word 365 (commentsIds, w16cex)."),
    ("o.erweiterung_wp14", FORMAT, "Zeichnungserweiterungen (wp14, a14)", _ANY(("ns", "wp14"), ("ns", "a14")), "Dokument mit wp14-Größenangaben."),
    ("o.erweiterung_wne", FORMAT, "Word-2006-Erweiterungen (wne, w12)", _ANY(("ns", "wne"), ("ns", "w12")), "Dokument mit wne-Erweiterung (Makros, Tastenbelegungen)."),
    ("o.personen", FORMAT, "Autorenliste (people.xml)", ("teil", "word/people.xml"), "Dokument mit Personenliste."),
    ("o.xml_space", FORMAT, "Leerraum erhalten (xml:space=preserve)", _A("w:t", "xml:space", "preserve"), "Text mit führenden/abschließenden Leerzeichen."),
    ("o.unbekannte_namensraeume", FORMAT, "Unbekannte Namensräume", ("unbekannt_ns",), "Dokument mit herstellerfremden Namensräumen."),
    ("o.externe_verweise", FORMAT, "Externe Beziehungen (TargetMode=External)", ("rel_extern_irgendwas",), "Dokument mit externen Verweisen (Bilder, Vorlage, Datenquelle)."),
    ("o.beziehungen_komplett", FORMAT, "Mehrere Beziehungsdateien (word/_rels)", ("teil", "word/_rels/*"), "Dokument mit Beziehungen zu Kopfzeile, Bild und Hyperlink."),
    ("o.content_types_override", FORMAT, "Content-Type-Überschreibungen (Override)", ("ct_override",), "Dokument mit individuellen Content-Types."),
    ("o.docm_dotx", FORMAT, "Vorlage/Makro-Variante (.dotx, .docm, .dotm)", ("ct", "template"), "Dokumentvorlage (.dotx) mit Platzhaltern."),
    ("o.fehlerhaft", FORMAT, "Beschädigte/ungültige Pakete (negativ)", ("beschaedigt",), "Gezielt beschädigtes Dokument (abgeschnittenes ZIP, fehlerhaftes XML)."),
    # --- Kombinationen (Funktionen, die nur zusammen auffallen)
    ("k.tabelle_bild", KOMBI, "Tabelle mit Bild und Textumfluss", ("kombi", "t.tabelle", "g.anker"), "Verankertes Bild neben/in einer Tabelle."),
    ("k.tabelle_liste", KOMBI, "Nummerierte Liste in Tabellenzelle", ("kombi_in", "w:numPr", "w:tc"), "Zelle mit mehrstufiger Liste."),
    ("k.tabelle_fussnote", KOMBI, "Fußnote in Tabelle", ("kombi_in", "w:footnoteReference", "w:tc"), "Zelle mit Fußnote."),
    ("k.tabelle_aenderung", KOMBI, "Verfolgte Änderung in Tabelle", ("kombi_in", "w:ins", "w:tc"), "Zelle mit verfolgter Einfügung."),
    ("k.tabelle_sdt", KOMBI, "Inhaltssteuerelement in Tabelle", ("kombi_in", "w:sdt", "w:tc"), "Zelle mit Inhaltssteuerelement."),
    ("k.tabelle_textfeld", KOMBI, "Textfeld mit Tabelle", ("kombi_in", "w:tbl", "w:txbxContent"), "Textfeld, das eine Tabelle enthält."),
    ("k.textfeld_bild", KOMBI, "Textfeld mit Bild", ("kombi_in", "w:drawing", "w:txbxContent"), "Textfeld mit Inline-Bild."),
    ("k.kopfzeile_tabelle", KOMBI, "Tabelle in Kopf-/Fußzeile", ("kombi_in", "w:tbl", "w:hdr"), "Kopfzeile mit Tabelle (Logo + Adresse)."),
    ("k.kopfzeile_bild", KOMBI, "Bild in Kopf-/Fußzeile", ("kombi_in", "w:drawing", "w:hdr"), "Kopfzeile mit Logo."),
    ("k.hyperlink_feld", KOMBI, "Feld innerhalb eines Hyperlinks", ("kombi_in", "w:fldChar", "w:hyperlink"), "Hyperlink mit Feld."),
    ("k.liste_aenderung", KOMBI, "Verfolgte Änderung in nummerierter Liste", ("kombi", "w.aenderungen_einfuegen", "n.nummerierung"), "Liste mit Einfügungen und Löschungen."),
    ("k.rtl_tabelle", KOMBI, "RTL-Text in Tabelle", ("kombi_in", "w:bidi", "w:tc"), "Tabellenzelle mit arabischem Text."),
    ("k.formel_liste", KOMBI, "Formel im selben Absatz wie Listennummer", ("absatz_mit", "w:numPr", "m:oMath"), "Listenpunkt mit Formel."),
    ("k.sdt_textfeld", KOMBI, "Steuerelement im Textfeld", ("kombi_in", "w:sdt", "w:txbxContent"), "Textfeld mit Steuerelement."),
    ("k.ebenen_tabelle_3", KOMBI, "Dreifach verschachtelte Tabelle", ("tiefe", "w:tbl", 3), "Tabellen drei Ebenen tief."),
    ("k.spalten_tabelle", KOMBI, "Tabelle in mehrspaltigem Abschnitt", ("kombi", "p.spalten", "t.tabelle"), "Zweispaltiger Abschnitt mit Tabelle."),
    ("k.abschnitt_kopfzeile_orient", KOMBI, "Querformat mit eigener Kopfzeile", ("kombi", "p.querformat", "p.kopfzeile"), "Querformat-Abschnitt mit eigener Kopfzeile."),
    ("k.fussnote_spalten", KOMBI, "Fußnoten in mehrspaltigem Text", ("kombi", "w.fussnote", "p.spalten"), "Zweispaltiger Text mit Fußnoten."),
)
