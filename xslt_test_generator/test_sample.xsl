<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <!-- Global variable -->
    <xsl:variable name="defaultTitle" select="'Sample Document'"/>
    
    <!-- Root template -->
    <xsl:template match="/">
        <html>
            <head>
                <title><xsl:value-of select="$defaultTitle"/></title>
            </head>
            <body>
                <xsl:apply-templates select="//item"/>
            </body>
        </html>
    </xsl:template>
    
    <!-- Item template with conditional logic -->
    <xsl:template match="item">
        <div class="item">
            <h3><xsl:value-of select="@name"/></h3>
            <xsl:if test="@priority = 'high'">
                <span class="priority-high">HIGH PRIORITY</span>
            </xsl:if>
            <xsl:choose>
                <xsl:when test="@type = 'urgent'">
                    <xsl:call-template name="urgentItemTemplate"/>
                </xsl:when>
                <xsl:when test="@type = 'normal'">
                    <p><xsl:value-of select="description"/></p>
                </xsl:when>
                <xsl:otherwise>
                    <p>Unknown item type</p>
                </xsl:otherwise>
            </xsl:choose>
        </div>
    </xsl:template>
    
    <!-- Named template for urgent items -->
    <xsl:template name="urgentItemTemplate">
        <div class="urgent">
            <p><strong>URGENT:</strong> <xsl:value-of select="description"/></p>
            <xsl:if test="deadline">
                <p class="deadline">Deadline: <xsl:value-of select="deadline"/></p>
            </xsl:if>
        </div>
    </xsl:template>
    
</xsl:stylesheet>