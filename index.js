CREATE PROCEDURE dbo.TransformMerchantMatchXML
    @InputXML XML
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @OutputXML XML;

    -- Extract fields from input XML
    DECLARE @Name NVARCHAR(100) = @InputXML.value('(/merchantMatch/name/text())[1]', 'NVARCHAR(100)');
    DECLARE @DoingBusinessAsName NVARCHAR(100) = @InputXML.value('(/merchantMatch/doingBusinessAsName/text())[1]', 'NVARCHAR(100)');
    DECLARE @PhoneNumber NVARCHAR(100) = @InputXML.value('(/merchantMatch/phoneNumber/text())[1]', 'NVARCHAR(100)');
    DECLARE @Address NVARCHAR(100) = @InputXML.value('(/merchantMatch/address/text())[1]', 'NVARCHAR(100)');
    DECLARE @AltPhoneNumber NVARCHAR(100) = @InputXML.value('(/merchantMatch/altPhoneNumber/text())[1]', 'NVARCHAR(100)');
    DECLARE @CountrySubdivisionTaxId NVARCHAR(100) = @InputXML.value('(/merchantMatch/countrySubdivisionTaxId/text())[1]', 'NVARCHAR(100)');
    DECLARE @NationalTaxId NVARCHAR(100) = @InputXML.value('(/merchantMatch/nationalTaxId/text())[1]', 'NVARCHAR(100)');

    -- For Principal Matches
    DECLARE @PName NVARCHAR(100) = @InputXML.value('(/merchantMatch/principalMatches/name/text())[1]', 'NVARCHAR(100)');
    DECLARE @PAddress NVARCHAR(100) = @InputXML.value('(/merchantMatch/principalMatches/address/text())[1]', 'NVARCHAR(100)');
    DECLARE @PPhoneNumber NVARCHAR(100) = @InputXML.value('(/merchantMatch/principalMatches/phoneNumber/text())[1]', 'NVARCHAR(100)');
    DECLARE @PAltPhoneNumber NVARCHAR(100) = @InputXML.value('(/merchantMatch/principalMatches/altPhoneNumber/text())[1]', 'NVARCHAR(100)');
    DECLARE @PNationalId NVARCHAR(100) = @InputXML.value('(/merchantMatch/principalMatches/nationalId/text())[1]', 'NVARCHAR(100)');
    DECLARE @PDriversLicense NVARCHAR(100) = @InputXML.value('(/merchantMatch/principalMatches/driversLicense/text())[1]', 'NVARCHAR(100)');
    DECLARE @PEmail NVARCHAR(100) = @InputXML.value('(/merchantMatch/principalMatches/email/text())[1]', 'NVARCHAR(100)');
    DECLARE @PDateOfBirth NVARCHAR(100) = @InputXML.value('(/merchantMatch/principalMatches/dateOfBirth/text())[1]', 'NVARCHAR(100)');

    -- Build Output XML with required tags
    SET @OutputXML = 
    N'<merchantMatch>
        <zcloseMatch>
            <mercantMatchData></mercantMatchData>
        </zcloseMatch>
        <zexactMatch>
            <mercantMatchData>' + 
                CASE WHEN @Name = 'M01' THEN 'Name, ' ELSE '' END +
                CASE WHEN @DoingBusinessAsName = 'M01' THEN 'DoingBusinessAsName, ' ELSE '' END +
            '</mercantMatchData>
        </zexactMatch>
        <znoMatch>
            <mercantMatchData>' + 
                CASE WHEN @Address = 'M00' THEN 'Address, ' ELSE '' END +
                CASE WHEN @PhoneNumber = 'M00' THEN 'PhoneNumber, ' ELSE '' END +
                CASE WHEN @AltPhoneNumber = 'M00' THEN 'AltPhoneNumber, ' ELSE '' END +
                CASE WHEN @CountrySubdivisionTaxId = 'M02' THEN 'CountrySubdivisionTaxId, ' ELSE '' END +
                CASE WHEN @NationalTaxId = 'M00' THEN 'NationalTaxId, ' ELSE '' END +
            '</mercantMatchData>
        </znoMatch>
        <principalMatches>
            <zcloseMatch>
                <mercantMatchData></mercantMatchData>
            </zcloseMatch>
            <zexactMatch>
                <mercantMatchData>' + 
                    CASE WHEN @PName = 'M01' THEN 'Name, ' ELSE '' END +
                '</mercantMatchData>
            </zexactMatch>
            <znoMatch>
                <mercantMatchData>' + 
                    CASE WHEN @PAddress = 'M00' THEN 'Address, ' ELSE '' END +
                    CASE WHEN @PPhoneNumber = 'M00' THEN 'PhoneNumber, ' ELSE '' END +
                    CASE WHEN @PAltPhoneNumber = 'M00' THEN 'AltPhoneNumber, ' ELSE '' END +
                    CASE WHEN @PNationalId = 'M00' THEN 'NationalId, ' ELSE '' END +
                    CASE WHEN @PDriversLicense = 'M00' THEN 'DriversLicense, ' ELSE '' END +
                '</mercantMatchData>
            </znoMatch>
        </principalMatches>
    </merchantMatch>';

    SELECT @OutputXML;
END
