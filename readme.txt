Der junge Goethe in seiner Zeit. 
Zur TEI-konformen Fassung des Textes

Inhalt
1. Warum TEI?
2. Inhalt des Unterverzeichnisses \tei
3. Darstellung der Texte
4. Folio- und TEI-Version
5. Zusammenführen der Einzeldateien in eine größere Datei
6. Tags und Attribute

1. Warum TEI?
Die Verwendungszeit elektronischer Editionen wird von mehreren 
Faktoren verkürzt: der kurzen Lebensdauer der Programme, die zu 
ihrer Darstellung verwendet werden, der etwas längeren der 
Betriebssysteme, unter denen die Darstellungsprogramme laufen, 
der logischen Einrichtung des Datenträgers, auf dem sich die 
Edition befindet, und dessen physischer Dauer. Elektronische 
Editionen teilen diese Probleme mit allen digitalisierten Texten.
Um wenigstens die Abhängigkeit von einem bestimmten Programm und
einem bestimmten Betriebssystem zu vermeiden, wurde bereits 
1986 ein Standard zur Definition von Textauszeichnungssystemen
verabschiedet: SGML (Standard Generalized Markup Language).(1)
SGML ist selbst kein Textauszeichnungssystem (wie z.B. RTF, 
HTML oder das interne Format von Winword-Dateien), sondern 
ist eine Metasprache, mit der man Textauszeichnungssysteme 
definieren kann. Der Vorteil besteht darin, daß man mit SGML-
konformen Programmen alle so ausgezeichneten Texte lesen kann. 
Der Anwender ist also für die Darstellung und Analyse seiner 
Texte nicht auf ein bestimmtes Programm angewiesen, sondern kann
frei unter allen Programmen wählen, die SGML-Daten verarbeiten
können. Beispiele für solche aufgrund von SGML definierten 
Textauszeichnungssysteme sind HTML (die Seitenbeschreibungssprache
des Internets) und TEI, die philologische Textbeschreibungssprache
der Text Encoding Initiative. 
TEI stellt dem Textwissenschaftler mehrere hundert Auszeichner (tags) 
zur Verfügung, um nahezu jeden gewünschten Aspekt eines Textes
mit Zusatzinformationen zu versehen. Die exzellenten Handbücher,
herausgegeben von den Lou Burnard und Michael Sperberg-
McQueen, und auch die 'Grammatik'-Dateien (DTDs) selbst sind 
im Internet verfügbar. (2)
Daten, die entsprechend den TEI-Richtlinien ausgezeichnet worden sind, 
können mit jedem Programm, das SGML-Daten verarbeiten kann, 
dargestellt, umgewandelt oder durchsucht werden. Vor allem können
verschiedene Editionen, wenn sie TEI zur Auszeichnung verwendet
haben, vom Anwender zur Recherche zu einem Korpus
zusammengeschlossen werden. Wissenschaftler können also, wenn sie sich
an diesen Richtlinien orientieren, die für ihre Belange geschaffen wurden 
und auch neueren Anforderungen angepaßt werden können, ihre Daten 
langfristig und unabhängig von einzelnen Firmen archivieren und dem
Anwender zur Nutzung zugänglich machen. 
Verwendet wurde für die Auszeichnung der vorliegenden Edition 'teilite', 
eine Teilmenge des gesamten Auszeichnungssystems TEI, die auf 
einige von dessen komplexeren Merkmale verzichtet und deshalb auch 
eine einfache Konvertierung der Daten zu neueren Metasprachen 
für Auszeichnungssysteme wie XML, einer Teilmenge von SGML, 
ermöglicht.
SGML-Programme mit der Leistungsfähigkeit von Folio Views sind 
z.Zt. noch relativ teuer, daher wurde für die vorliegende 
Edition der Weg gewählt, den Text doppelt auf die CD zu legen: 
Einmal für die sofortige Nutzung mit einer komfortablen 
Oberfläche und einmal ohne Software in einem Format, das seine 
langfristige Verwendbarkeit wahrscheinlicher macht. 
Das Nachstehende soll einige Hinweise zur Einrichtung der TEI-
Dateien geben, um deren weitere Verwendung zu erleichtern. 


2. Inhalt des Unterverzeichnisses \tei
Die TEI-Version dieser Ausgabe der Werke des jungen Goethe 
liegt im Verzeichnis "\tei" auf der CD. In den Verzeichnissen 
unterhalb von \tei liegen die notwendigen Grafiken. Das 
Verzeichnis \tei ist selbständig, d.h. es werden keine weiteren 
Grafik- oder Textdateien benötigt, außer denen, die in \tei 
liegen, um den Text mit einem SGML-konformen Programm 
verarbeiten zu können. 

jgoethe0.sgm - jgoethe23.sgm      die Textdateien
jgoethe0.ent - jgoethe23.ent      die zugehörigen Entities
teilite.dtd                       die verwendete TEI-DTD
usermod.ent                       Modifikation der TEI-DTD (3)
iso-*.ent                         Dateien mit Informationen zu  
                                  Sonderzeichen 
catalog                           Zuordnung von public identifiern zu 
                                  Systemdateiein
readme.txt, readme.htm            die Datei, die sie gerade lesen
jgoethe.ssh                       Ein Stylesheet für die Darstellung 
                                  der Dateien in Softquads Panorama Pro
jgoethe.nav                       Navigationsinformationen für Softquads 
                                  Panorama Pro
nav.ssh                           Stylesheet für das Navigationsfenster von 
                                  Softquads Panorama Pro

3. Darstellung der Texte
TEI ist ein Auszeichnungssystem, um die Struktur von Texten zu 
beschreiben. Es legt die Art der Darstellung auf dem Bildschirm 
oder dem Papier nicht fest. Die meisten SGML-Programme 
verwenden proprietäre Stylesheet-Formate, um das Ausgabeformat 
des Textes zu bestimmen. Als Beispiel für ein solches 
stylesheet liegen die Dateien jgoethe.ssh und jgoethe.nav bei, 
die die Bildschirmpräsentation im Programm Softquad Panorama 
Pro steuern. Es handelt  sich um einfache Textdateien, die 
einen Eindruck vermitteln sollen, wie die 
Auszeichnungsinformationen zur Gestaltung der Darstellung 
verwendet werden können. Ein Überblick über die wichtigsten 
verwendeten Attribute und ihre Werte findet sich am Ende dieser 
Datei. 


4. Folio- und TEI-Version
Bis auf einige geringfügige Korrekturen sind die beiden 
elektronischen Texte textidentisch. Die Record-IDs der 
Folio-Edition wurde als Wert des Attributs 'id' in den 
Elementen DIV1-7, LG oder P notiert. Der Zahl ist stets ein 
'jg' vorangestellt (Bsp.: id="jg2345"). Die Record-Ids der 
Folio Edition sind jedoch nicht identisch mit den angezeigten
Record-Nummern, sondern werden nur sichtbar, wenn man einen
Textabschnitt exportiert und in den Export Optionen den 
Schalter "Eintrags-IDs schreiben" aktiviert hat. Die Folio
IDs sind Hexadezimal-Zahlen, die TEI-Ids Dezimalzahlen.
Die Gruppensuche von Folio basiert auf einer Auszeichnung der 
Records mit einer Gruppeninformation. Diese Auszeichnung wurde 
in das Element MILESTONE übernommen. Die entsprechenden 
MILESTONE-Elemente haben als Attributwert für 'ed' 
"foliogruppe". Der Wert des Attributs 'unit' enthält die 
Gruppeninformation. Bs: <MILESTONE ed="foliogruppe" 
unit="JGoethe 1765-68">
Es wurden nicht alle programmtechnischen Besonderheiten der 
Folio-Edition in der TEI-Auszeichnung berücksichtigt. Folio 
Views ermöglicht sogenannte Query-Links, also Hyperlinks, die 
keine feste Zieladresse haben, sondern einen spezifizierten 
Suchlauf starten. Diese Query-Links könnten zwar in die Syntax 
von XREF-Verweisen übersetzt werden, da dort auch ein pattern 
als Ziel angegeben werden kann; der Mangel an Software, die 
diese Verweistechnik unterstützt, ließ aber den 
Konvertierungsaufwand in diesem Punkt ungerechtfertigt 
erscheinen. 


5. Zusammenführen der Einzeldateien in eine einzige Datei
Der Text ist für eine einfachere Verwendung mit kleineren 
Leseprogrammen in 24 Einzeldateien zerlegt worden. Will man die 
Gesamtdatei wiederherstellen, muß man den TEI-Header in allen 
Dateien außer der ersten entfernen; ebenso die Schlußtags am 
Ende aller Dateien außer der letzten. (</BODY></TEXT></TEI.2>). 
Außerdem müssen die Dateiangaben in den Zielangaben der 
Hyperlinks angepaßt werden. Da sie alle das Format "JGOETHE" 
gefolgt von einer Zahl haben, ist dies leicht zu 
bewerkstelligen 
Außerdem müssen die Entityangaben, die zur Zeit getrennt nach 
Dateien vorliegen (in den Dateien mit der Endung .ent) in eine 
Datei zusammengeführt und der Verweis auf diese Entitydatei am 
Kopf der neuen Text-Datei angepaßt werden. 


6. Tags und Attribute
Umlaute, frz. Akzente, griechische Buchstaben usw. sind durch 
die entsprechenden Entities ersetzt (siehe zum Schlüssel die 
beiliegenden Dateien iso*.ent). 
Folgende Tags wurden in der Textauszeichnung (also nicht im 
Header) verwendet: 

Die Schreibweise der Attribut-Namen wechselt zwischen Klein- 
und Großschreibung. 
Angaben in [] sind im folgenden als Platzhalter zu verstehen. 

<ANCHOR id="[Zielangabe für XREF]">
<AUTHOR>
<BODY>
<CELL>
<DATE>
<DIV1 type="Überschrift1">
<DIV2 type="Überschrift2">
<DIV3 type="Überschrift2">
<DIV3 type="Überschrift3" >
<DIV3 type="Überschrift3">
<DIV4 type="Überschrift4">
<DIV5 type="Überschrift5">
<DIV6 type="Überschrift6">
<DIV7 type="Überschrift7">
<EMPH>
<FIGURE entity="[Entityname]" rend="extern">
<HEAD>
<HI>
<L>
<L n="[Zeilenzahl]">
<L rend="Absatzhaengend">
<L rend="Bibelvers" >
<L rend="ErlaeuterungenKlein">
<L>
<LB>
<LG>
<LG rend="Versrede" type="Verse">
<LG type="Bibelverse">
<LG type="Strophe" >
<MILESTONE ed="foliogruppe" unit="JGoethe 1749-65">
<MILESTONE ed="foliogruppe" unit="JGoethe 1765-68">
<MILESTONE ed="foliogruppe" unit="JGoethe 1768-70">
<MILESTONE ed="foliogruppe" unit="JGoethe 1770-71">
<MILESTONE ed="foliogruppe" unit="JGoethe 1771- Mai 72">
<MILESTONE ed="foliogruppe" unit="JGoethe 1772 Juni-Sept.">
<MILESTONE ed="foliogruppe" unit="JGoethe 1772, Okt., - 73">
<MILESTONE ed="foliogruppe" unit="JGoethe 1774/1 Jan-Juni">
<MILESTONE ed="foliogruppe" unit="JGoethe 1774/2 Juli-Aug">
<MILESTONE ed="foliogruppe" unit="JGoethe 1774/3 Aug-Dez">
<MILESTONE ed="foliogruppe" unit="JGoethe 1775/1 Jan-Mai">
<MILESTONE ed="foliogruppe" unit="JGoethe 1775/2 Mai-Juli">
<MILESTONE ed="foliogruppe" unit="JGoethe 1775/3 ab Juli">
<NAME>
<NAME type="Dramenfigur">
<NAME type="Namenglossar">
<NAME type="Sprecher im Gedicht">
<NOTE>
<NOTE type="Bild">
<NOTE type="bild">
<P>
<P  rend="Dramenprosa">
<P rend="Absatzhaengend">
<P rend="BinnenTrennZeichen">
<P rend="Dramenprosa">
<P rend="Erlaeuterungen">
<P rend="ErlaeuterungenKlein">
<P rend="ErlaeuterungenKleinLyrik">
<P rend="ErlaeuterungenMitErsteinzug">
<P rend="ErlaeuterungenOhneLeereinzug">
<P rend="ErlaeuterungenZitat">
<P rend="Liste">
<P rend="Nachwort">
<P rend="ProsaMitErsteinzug">
<P rend="ProsaOhneLeereinzug">
<P rend="Prosatext">
<PB ed="Buchausgabe" n="[Band Seitenzahl]">
<PB ed="Goetz" n=[gz Seitenzahl]>
<PB ed="Werther" n=[wt Seitenzahl]>
<ROW>
<SEG>
<SEG Type="Sprecher">
<SEG type="Fremde Hand">
<SEG type="Grafikverweis">
<SEG type="altgriechisch">
<SP>
<SP rend="Dramenprosa">
<SP rend="Absatzhaengend">
<SP rend="Dramenprosa">
<SP rend="ProsaMitErsteinzug">
<SPEAKER>
<STAGE>
<TABLE>
<TEXT>
<TITLE type="Goethewerk">
<TITLE>
<XREF DOC="JGOETHE[0-23]" FROM="id ([id des Anchor-Elements im 
Ziel])">

Abschließend sei noch einmal auf die Webseite für diese Edition 
verwiesen:
http://www.jgoethe.uni-muenchen.de

-------------------------------------------------------------
(1) Ausführliche Informationen zu SGML einschließlich eines 
Verweises auf eine Liste mit SGML-Programmen findet man unter 
http://www.sgmlopen.org/. Ein sehr gute Einführung bietet: 
Wolfgang Rieger: SGML für die Praxis. Ansatz und Einsatz von 
ISO 8879. Springer: Heidelberg 1995. 

(2) Alle Handbücher, DTDs und eine Beschreibung der TEI sind im 
Internet unter der Adresse http://www.uic.edu:80/orgs/tei/ 
einzusehen. Zur Einführung siehe Fotis Jannidis: Wider das Altern 
elektronischer Texte: philologische Textauszeichnung mit TEI. 
In: editio 11 (1997), S. 152-177.

(3) Die Datei teilite.dtd wurde bis auf einen Punkt unverändert 
übernommen: Die Notation für das Grafikformat GIF wurde auskommentiert
und eine neue Notations-Anweisung in der Datei usermod.ent definiert.
