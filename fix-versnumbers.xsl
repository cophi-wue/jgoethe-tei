<xsl:stylesheet
  version="3.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns="http://www.tei-c.org/ns/1.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0"
>
  <xsl:mode on-no-match="shallow-copy" />

  <!--
      Incorrectly placed line numbers look like this: <l>50 Hier sitz ich forme Menschen</l>
      they need to be moved into the @n attribute of the l or p element. We match:
      - l and p elements without an existing n attribute that have a number ending in 0 or 5 in their
  first text node
      - which is not years 17.. or 18..
      - which is not followed by something other than a space
      - which is not part of an enumeration, i.e. a number ending in 4 or 9 is in one of the preceding
  siblings of the l or p element
      - … and which is not in p[@xml:id='JG33758'] (special case)
  -->
  <xsl:template
    match="(l|p)
        [not(@n)]
        [matches(text()[1], '^\d*[05]')]
        [not(matches(text()[1], '^(1[78]\d\d(\D|$)|\d+[^0-9 ])'))]
        [not(some $preceding in preceding-sibling::*/text()[1] satisfies matches($preceding, '^\d*[49]'))]
        [not(@xml:id = 'JG33758')]
     ">
    <xsl:variable name="textnode" select="text()[1]" />
    <xsl:copy>
      <xsl:apply-templates select="@*" />
      <xsl:analyze-string
        regex="^\d+"
        select="text()[1]">
        <xsl:matching-substring>
          <xsl:attribute name="n" select="." />
        </xsl:matching-substring>
        <xsl:non-matching-substring>
          <!-- copy any elements before the first text node => milestones -->
          <xsl:apply-templates
            select="$textnode/preceding-sibling::node()/." />
          <xsl:copy-of
            select="." />
        </xsl:non-matching-substring>
      </xsl:analyze-string>
      <xsl:apply-templates
        select="text()[1]/following-sibling::node()" />
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
