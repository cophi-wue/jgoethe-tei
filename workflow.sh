#!/bin/sh

# This workflow converts the original SGML TEI version from the CD to a P5 based version,
# with the intermediate P4 based version used by the old edition.
TOOLS=$(pwd)

mkdir conversion
git worktree add --locked conversion/0-CD CD
cd conversion
cp -rp 0-CD 1-references

# Move files to modern locations, fix references, write graphics.xml
"$TOOLS"/fix-references.py 1-references

cp -rp 1-references 2-XML
cd 2-P3-XML

# prepare iso*.ent files to create unicode codepoints
"$TOOLS"/ent2unicode.py

# actually translate and cleanup the files
for sgml in *.sgm; do
  "$TOOLS"/sgml2xml.sh "${sgml}" | xsltproc "$TOOLS"/tei2tei.xsl >"${sgml%%.sgm}.xml"
done
rm ./*.sgm ./*.ent
cd ..

# now prepare the structure from the old webapp
cp -rp 2-P3-XML 3-oldapp-XML
cd 3-oldapp-XML
saxon -xsl:"$TOOLS/merge.xsl" -s:jgoethe0.xml -o:jgoethe-raw.xml
rm jgoethe[0-9].xml jgoethe1[0-9].xml jgoethe2[0-3].xml
xsltproc "$TOOLS/sgml-to-app-structure.xsl" jgoethe-raw.xml >jgoethe.xml
rm jgoethe-raw.xml
cd ..

# finally a P5 version
cp -rp 3-oldapp-XML 4-P5
cd 4-P5
p4totei jgoethe.xml jgoethe-p5.xml
cd ..
