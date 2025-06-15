<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="xml" encoding="UTF-8" indent="yes"/>
	<xsl:template match="/">
		<OrderCreateRQ Version="17.2">
			<xsl:if test="Request/Context/correlationID">
				<xsl:attribute name="CorrelationID">
					<xsl:value-of select="Request/Context/correlationID"/>
				</xsl:attribute>
				<xsl:attribute name="TransactionIdentifier">
					<xsl:value-of select="Request/Context/correlationID"/>
				</xsl:attribute>
			</xsl:if>
			<PointOfSale>
				<Location>
					<CountryCode>FR</CountryCode>
					<CityCode>NCE</CityCode>
				</Location>
			</PointOfSale>
			<Document>
				<xsl:attribute name="id">document</xsl:attribute>
			</Document>
			<xsl:if test="Request/TravelAgency">
				<Party>
					<Sender>
						<TravelAgencySender>
							<xsl:if test="Request/TravelAgency/Name">
								<Name><xsl:value-of select="Request/TravelAgency/Name"/></Name>
							</xsl:if>
							<xsl:if test="Request/TravelAgency/Contact">
								<Contacts>
									<xsl:for-each select="Request/TravelAgency/Contact">
										<Contact>
											<xsl:for-each select="Address">
												<AddressContact>
													<xsl:for-each select="line">
														<Street><xsl:value-of select="."/></Street>
													</xsl:for-each>
													<xsl:if test="CityName">
														<CityName><xsl:value-of select="CityName"/></CityName>
													</xsl:if>
													<xsl:if test="CountryCode">
														<CountryCode><xsl:value-of select="CountryCode"/></CountryCode>
													</xsl:if>
													<xsl:if test="Zip">
														<PostalCode><xsl:value-of select="Zip"/></PostalCode>
													</xsl:if>
												</AddressContact>
											</xsl:for-each>
											<xsl:for-each select="Email">
												<EmailContact>
													<xsl:if test="EmailAddress">
														<Address><xsl:value-of select="EmailAddress"/></Address>
													</xsl:if>
												</EmailContact>
											</xsl:for-each>
											<xsl:for-each select="Phone">
												<PhoneContact>
													<xsl:if test="PhoneNumber">
														<Number><xsl:value-of select="translate(PhoneNumber, concat(' `~!@#$%^&amp;*()-_=+[]{}|\:;&quot;',&quot;',./&lt;&gt;?abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ&quot;), '')"/></Number>
													</xsl:if>
												</PhoneContact>
											</xsl:for-each>
										</Contact>
									</xsl:for-each>
								</Contacts>
							</xsl:if>
							<PseudoCity>AH9D</PseudoCity>
							<xsl:if test="Request/TravelAgency/IATA_Number">
								<IATA_Number><xsl:value-of select="Request/TravelAgency/IATA_Number"/></IATA_Number>
								<AgencyID><xsl:value-of select="Request/TravelAgency/IATA_Number"/></AgencyID>
							</xsl:if>
							<AgentUser>
								<AgentUserID>xmluser001</AgentUserID>
							</AgentUser>
						</TravelAgencySender>
					</Sender>
				</Party>
			</xsl:if>
			<xsl:if test="Request/set">
				<Query>
					<Order>
						<xsl:for-each select="Request/set">
							<Offer>
								<xsl:if test="property[key='OwnerCode']">
									<xsl:attribute name="Owner">
										<xsl:value-of select="property[key='OwnerCode']/value"/>
									</xsl:attribute>
								</xsl:if>
								<xsl:attribute name="OfferID">
									<xsl:value-of select="ID"/>
								</xsl:attribute>
								<xsl:attribute name="ResponseID">
									<xsl:value-of select="TID"/>
								</xsl:attribute>
								<xsl:for-each select="product">
									<OfferItem>
										<xsl:attribute name="OfferItemID">
											<xsl:value-of select="ID"/>
										</xsl:attribute>
										<xsl:if test="RefIDs">
											<PassengerRefs><xsl:value-of select="RefIDs"/></PassengerRefs>
										</xsl:if>
										<xsl:if test="EST">
											<SeatSelection>
												<xsl:if test="EST/Data/seatNbr">
													<Row><xsl:value-of select="number(substring(EST/Data/seatNbr, 1, (string-length(string(EST/Data/seatNbr)) - 1)))"/></Row>
													<Column><xsl:value-of select="substring(EST/Data/seatNbr, string-length(string(EST/Data/seatNbr)), 1)"/></Column>
												</xsl:if>
											</SeatSelection>
										</xsl:if>
									</OfferItem>
								</xsl:for-each>
							</Offer>
						</xsl:for-each>
					</Order>
					<DataLists>
						<PassengerList>
							<xsl:for-each select="Request/actor">
								<Passenger>
									<xsl:attribute name="PassengerID">
										<xsl:value-of select="ID"/>
									</xsl:attribute>
									<PTC><xsl:value-of select="PTC"/></PTC>
									<Individual>
										<xsl:if test="DateOfBirth">
											<Birthdate><xsl:value-of select="DateOfBirth"/></Birthdate>
										</xsl:if>
										<xsl:if test="Name/Type">
											<Gender>
												<xsl:choose>
													<xsl:when test="Name/Type='Other'">
														<xsl:value-of select="'Unspecified'"/>
													</xsl:when>
													<xsl:otherwise>
														<xsl:value-of select="Name/Type"/>
													</xsl:otherwise>
												</xsl:choose>
											</Gender>
										</xsl:if>
										<xsl:if test="Name/FirstName">
											<GivenName><xsl:value-of select="Name/FirstName"/></GivenName>
										</xsl:if>
										<xsl:if test="Name/LastName">
											<Surname><xsl:value-of select="Name/LastName"/></Surname>
										</xsl:if>
									</Individual>
									<xsl:for-each select="loyalty">
										<LoyaltyProgramAccount>
											<xsl:if test="companyCode">
												<Airline>
													<AirlineDesignator><xsl:value-of select="companyCode"/></AirlineDesignator>
												</Airline>
											</xsl:if>
											<xsl:if test="identifier">
												<AccountNumber><xsl:value-of select="identifier"/></AccountNumber>
											</xsl:if>
										</LoyaltyProgramAccount>
									</xsl:for-each>
								</Passenger>
							</xsl:for-each>
						</PassengerList>
					</DataLists>
				</Query>
			</xsl:if>
		</OrderCreateRQ>
	</xsl:template>
</xsl:stylesheet>