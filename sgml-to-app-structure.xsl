<?xml version="1.0" encoding="UTF-8"?>
<!--
  Transforms jgoethe-from-sgml.xml into a document that is structurally
  equivalent to jgoethe-from-app.xml (modulo @TEIform, which both sides
  should have stripped before comparing - see the note at the end).

  Differences bridged, found by diffing jgoethe-from-app.rnc against
  jgoethe-from-sgml.rnc (both trang-generated from the respective XML
  files) and then confirming each one against the actual data:

  - @id (no namespace) -> @xml:id, with the value upper-cased. Applies to
    every element that carries it (div1-div7, l, lg, p, sp, anchor).
  - xref[@doc,@from] -> ref[@target,@targOrder]. @target is the
    parenthesised part of @from (e.g. from="id (LyrikAnfang)" -> target
    text "LyrikAnfang"), upper-cased, with any "/" removed (a few @from
    values contain a stray "/", e.g. "Werther//" -> target "WERTHER").
    @doc is dropped (all anchors live in one merged document) and
    @targOrder is always "U" in the app version, so it's added as a
    constant.
  - A handful (5, checked by hand) of xref elements are artifacts of the
    SGML->XML conversion: an omitted end-tag became a second, bare
    <xref> instead of </xref>, e.g.
      <xref doc="..." from="...">Björnsthåls<xref> Tagebuch ...</xref></xref>
    where the inner bare <xref> has neither @doc nor @from. The app
    version shows the intended reading: the ref closes right before the
    bare marker, and the marker's own text continues as plain sibling
    content afterwards. Handled by the two xref templates below.
  - teiHeader/@status="new", sourceDesc|projectDesc|editorialDecl/@default="NO":
    present as constants in the app header, absent from the sgml one.
    (The header occurs exactly once in the merged document, so these are
    simply hard-coded rather than derived.)
  - div1-div7 and lg gain constant @org="uniform" @sample="complete"
    @part="N". l and seg gain constant @part="N". note gains constant
    @place="unspecified". None of these vary across the corpus (checked:
    every occurrence in jgoethe-from-app.xml has exactly that one value).

  Known residual differences NOT handled here (checked, but not safely
  fixable from this file alone - see ISSUES.md):
  - A handful of ids ("aaa", "iris", "laugiermarcantoine", "patusundarria",
    ...) occur twice each in jgoethe-from-sgml.xml, already disambiguated
    there by suffixing the second occurrence with "1". The app export
    resolved the same collisions differently, but *not* by a uniform
    string rule: e.g. of several <ref> elements that all read
    target="LAUGIERMARCANTOINE" in our document, only the defining
    <anchor> (plus one specific <ref>) is renamed to "LAUGIERMARCANTOINE0"
    in the app version - the rest legitimately stay "LAUGIERMARCANTOINE".
    Telling those apart requires knowing which physical occurrence each
    ref "meant", information that's gone once the 24 source files are
    merged into one id space; a blanket rename would fix a couple of
    elements while breaking several others (verified - tried it, made
    things worse). Affects on the order of 10 elements total.
  - A single id, "afa", is renamed to "AFA1" in the app export with no
    corresponding "AFA0"/second occurrence anywhere - an isolated,
    unexplained rename, not a collision. Matches ISSUES.md's note on
    "lyrikanfang" vs. "LYRIKANFANG" being a similar naming-authority
    mismatch between the two conversions.
  - "jg1", "jg2" and "jg3" (the very first three @id values in the
    document) are left lower-case in the app export instead of being
    upper-cased like every other id; likewise one anchor, "DestinationA",
    keeps its original mixed case. Both look like one-off artifacts of
    however the app export was produced, not a rule.
  - One <head> is missing an <anchor> that the app version has (1 of
    ~37,100 anchors) - an isolated content difference, not structural.
  - Prose text itself sometimes differs in ways unrelated to markup: the
    app export spells some German umlauts as ASCII digraphs in a few notes
    (e.g. "fuer" for "für"), uses a different apostrophe/quote character
    in places, and has one instance of a mis-decoded character (a
    replacement-character glyph) where jgoethe-from-sgml.xml has a proper
    "´". These are content/encoding differences, not structural ones, and
    are out of scope for this stylesheet.

  @TEIform is intentionally left untouched (present on both sides,
  inconsistently) per instructions to ignore it; strip it from both
  documents before diffing (e.g. with a small stylesheet, or by ignoring
  it in whatever comparison tool is used).

  Usage:
    xsltproc sgml-to-app-structure.xsl jgoethe-from-sgml.xml > out.xml
    saxon -s:jgoethe-from-sgml.xml -xsl:sgml-to-app-structure.xsl -o:out.xml
-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:output method="xml" encoding="UTF-8" indent="no"/>

  <xsl:variable name="lower" select="'abcdefghijklmnopqrstuvwxyz'"/>
  <xsl:variable name="upper" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'"/>

  <!-- identity transform -->
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- id -> xml:id, upper-cased -->
  <xsl:template match="@id">
    <xsl:attribute name="xml:id">
      <xsl:value-of select="translate(., $lower, $upper)"/>
    </xsl:attribute>
  </xsl:template>

  <!-- real xref: doc/from -> ref/target+targOrder -->
  <xsl:template match="xref[@from or @doc]">
    <!-- the malformed conversion artifact, if this xref has one as its last child -->
    <xsl:variable name="bad" select="xref[not(@from) and not(@doc)][last()]"/>
    <ref targOrder="U">
      <xsl:if test="@from">
        <xsl:variable name="raw" select="substring-before(substring-after(@from, '('), ')')"/>
        <xsl:attribute name="target">
          <xsl:value-of select="translate(translate($raw, '/', ''), $lower, $upper)"/>
        </xsl:attribute>
      </xsl:if>
      <xsl:apply-templates select="node()[not($bad) or not(generate-id(.) = generate-id($bad))]"/>
    </ref>
    <xsl:if test="$bad">
      <xsl:apply-templates select="$bad/node()"/>
    </xsl:if>
  </xsl:template>

  <!-- bare xref met on its own (defensive fallback; the 5 known instances are
       consumed by the template above as part of their enclosing xref) -->
  <xsl:template match="xref[not(@from) and not(@doc)]">
    <xsl:apply-templates select="node()"/>
  </xsl:template>

  <!-- constant attributes required by the app schema but absent from sgml -->

  <xsl:template match="div1|div2|div3|div4|div5|div6|div7|lg">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:attribute name="org">uniform</xsl:attribute>
      <xsl:attribute name="sample">complete</xsl:attribute>
      <xsl:attribute name="part">N</xsl:attribute>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="l|seg">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:attribute name="part">N</xsl:attribute>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="note">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:attribute name="place">unspecified</xsl:attribute>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="teiHeader">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:attribute name="status">new</xsl:attribute>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="sourceDesc|projectDesc|editorialDecl">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:attribute name="default">NO</xsl:attribute>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
