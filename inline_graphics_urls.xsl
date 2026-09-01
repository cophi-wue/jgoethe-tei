<?xml-model href="https://www.w3.org/TR/xslt-30/schema-for-xslt30.rnc"?>
<xsl:stylesheet version="3.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns="http://www.tei-c.org/ns/1.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0">

  <xsl:mode on-no-match="shallow-copy" />

  <xsl:variable name="urlmap"
    select="document('../graphics.xml')" />

  <xsl:template match="*[@url]">
    <xsl:variable name="path" select="id(substring(@url, 8), $urlmap)/@url" />
    <xsl:choose>
      <xsl:when test="$path">
        <xsl:copy>
          <xsl:attribute name="url" select="$path" />
          <xsl:copy-of select="@* except @url" />
          <xsl:apply-templates
            select="node()" />
        </xsl:copy>
      </xsl:when>
      <xsl:otherwise>
        <xsl:message expand-text="yes">Could not resolve {.}</xsl:message>
        <xsl:next-match />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
