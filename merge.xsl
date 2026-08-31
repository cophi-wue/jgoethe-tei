<?xml version="1.0" encoding="UTF-8"?>
<!--
  Merges the 24 per-file jgoetheN.xml documents (after tools/fix-xref.xsl has
  turned their xref[@doc,@from] into ref[@data-target]) into one big
  jgoethe.xml, at the same P4-ish XML stage - i.e. before running
  tei-p4-from.xsl.

  - All 24 files share (almost) the same teiHeader, verified by inspection;
    the merged document keeps just one (jgoethe1's, the fullest version -
    only jgoethe0 differs, missing one sentence in projectDesc).
  - <text><body> is flattened: the <div1> children of all 24 files are
    concatenated in file order (jgoethe0's, then jgoethe1's, ...) directly
    under one <body>, with no wrapper marking which file a div1 came from.
  - Merging collapses 24 independent id spaces into one. Of ~118,600 ids in
    the corpus, exactly 8 collide across (never within) a file pair - see
    $renames below. The second-occurring file's copy of each is suffixed
    with "1", both on the defining @id and on any @data-target that pointed
    at it via doc="JGOETHEn" (checked: no bare, doc-less @data-target in the
    corpus ever targets one of these 8 ids, so no same-file case to handle).
  - Every other @data-target of the form "jgoetheN.xml#frag" loses its
    filename prefix, since the target is now in the same document.

  Run with a fixed/jgoetheN.xml file as -s: (any one; its content is
  ignored, only its base URI is used to locate its 23 siblings), e.g.:
    saxon -s:fixed/jgoethe0.xml -xsl:tools/merge.xsl -o:jgoethe.xml
-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:xs="http://www.w3.org/2001/XMLSchema"
                exclude-result-prefixes="xs"
                version="3.0">

  <xsl:output method="xml" encoding="UTF-8" indent="no"/>

  <!-- source file number -> shared teiHeader is taken from this one -->
  <xsl:param name="header-source" as="xs:integer" select="1"/>

  <!-- (file number, lower-cased id) pairs to rename, and their replacement -->
  <xsl:variable name="renames" as="element(rename)*">
    <rename file="7" id="aaa" to="aaa1"/>
    <rename file="7" id="aba" to="aba1"/>
    <rename file="7" id="aca" to="aca1"/>
    <rename file="7" id="ada" to="ada1"/>
    <rename file="7" id="aea" to="aea1"/>
    <rename file="19" id="iris" to="iris1"/>
    <rename file="19" id="laugiermarcantoine" to="laugiermarcantoine1"/>
    <rename file="19" id="patusundarria" to="patusundarria1"/>
  </xsl:variable>

  <xsl:function name="local:renamed" as="xs:string?" xmlns:local="urn:jgoethe-tei:merge">
    <xsl:param name="filenum" as="xs:integer"/>
    <xsl:param name="id" as="xs:string"/>
    <xsl:sequence select="($renames[xs:integer(@file) = $filenum and lower-case(@id) = lower-case($id)]/@to)[1]/string()"/>
  </xsl:function>

  <xsl:template match="/" name="main">
    <xsl:variable name="base" select="base-uri(/)"/>
    <TEI.2>
      <xsl:copy-of select="document(resolve-uri('jgoethe' || $header-source || '.xml', $base))/TEI.2/teiHeader"/>
      <text>
        <body>
          <xsl:for-each select="0 to 23">
            <xsl:variable name="filenum" select="."/>
            <xsl:variable name="src" select="document(resolve-uri('jgoethe' || $filenum || '.xml', $base))"/>
            <xsl:apply-templates select="$src/TEI.2/text/body/*">
              <xsl:with-param name="filenum" select="$filenum" tunnel="yes"/>
            </xsl:apply-templates>
          </xsl:for-each>
        </body>
      </text>
    </TEI.2>
  </xsl:template>

  <xsl:template match="@id">
    <xsl:param name="filenum" as="xs:integer" tunnel="yes"/>
    <xsl:variable name="to" select="local:renamed($filenum, .)" xmlns:local="urn:jgoethe-tei:merge"/>
    <xsl:attribute name="id" select="if (exists($to)) then $to else ."/>
  </xsl:template>

  <xsl:template match="@data-target">
    <xsl:param name="filenum" as="xs:integer" tunnel="yes"/>
    <xsl:analyze-string select="." regex="^(?:jgoethe([0-9]+)\.xml)?#(.+)$">
      <xsl:matching-substring>
        <xsl:variable name="target-file" as="xs:integer"
                      select="if (regex-group(1) != '') then xs:integer(regex-group(1)) else $filenum"/>
        <xsl:variable name="frag" select="regex-group(2)"/>
        <xsl:variable name="to" select="local:renamed($target-file, $frag)" xmlns:local="urn:jgoethe-tei:merge"/>
        <xsl:attribute name="data-target" select="'#' || (if (exists($to)) then $to else $frag)"/>
      </xsl:matching-substring>
      <xsl:non-matching-substring>
        <!-- doesn't match the expected shape (shouldn't happen); pass through unchanged -->
        <xsl:attribute name="data-target" select="."/>
      </xsl:non-matching-substring>
    </xsl:analyze-string>
  </xsl:template>

  <!-- identity transform, threading the tunnel parameter through -->
  <xsl:template match="@*|node()">
    <xsl:param name="filenum" as="xs:integer?" tunnel="yes"/>
    <xsl:copy>
      <xsl:apply-templates select="@*|node()">
        <xsl:with-param name="filenum" select="$filenum" tunnel="yes"/>
      </xsl:apply-templates>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
