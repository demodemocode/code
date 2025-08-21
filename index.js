ALTER PROCEDURE dbo.CreditUnderwriting
    @Id INT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @xmlQuery XML,
            @merchantCount INT,
            @i INT = 1,
            @merchantMatch XML,
            @newMatch XML;

    -- Get XML from table
    SELECT @xmlQuery = XMLData
    FROM MatchPros
    WHERE Id = @Id;

    -- Count how many <terminatedMerchant> exist
    SET @merchantCount = @xmlQuery.value('count(/terminationInquiry/possibleMerchantMatches/terminatedMerchant)', 'INT');

    -- Loop through merchants
    WHILE @i <= @merchantCount
    BEGIN
        -- Extract the i-th merchantMatch
        SET @merchantMatch = @xmlQuery.query('/terminationInquiry/possibleMerchantMatches/terminatedMerchant[position()=sql:variable("@i")]/merchantMatch');

        -- Transform merchantMatch using your earlier procedure
        -- NOTE: Make TransformMerchantMatchXML return via OUTPUT param
        EXEC dbo.TransformMerchantMatchXML @InputXML=@merchantMatch, @OutputXML=@newMatch OUTPUT;

        -- Remove old <merchantMatch>
        SET @xmlQuery.modify('
            delete /terminationInquiry/possibleMerchantMatches/terminatedMerchant[position()=sql:variable("@i")]/merchantMatch
        ');

        -- Insert new <merchantMatch>
        SET @xmlQuery.modify('
            insert sql:variable("@newMatch")
            as last into (/terminationInquiry/possibleMerchantMatches/terminatedMerchant[position()=sql:variable("@i")])[1]
        ');

        SET @i += 1;
    END;

    -- Save updated XML back to table
    UPDATE MatchPros
    SET XMLData = @xmlQuery
    WHERE Id = @Id;
END;
