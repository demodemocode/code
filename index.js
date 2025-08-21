ALTER PROCEDURE dbo.CreditUnderwriting
    @Id INT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @xmlQuery XML,
            @merchantCount INT,
            @totalLength INT,
            @i INT = 1,
            @merchantNode XML,
            @updatedNode XML;

    -- Get XML from table
    SELECT @xmlQuery = XMLData
    FROM MatchPros
    WHERE Id = @Id;

    -- Count how many <terminatedMerchant> exist
    SET @merchantCount = @xmlQuery.value('count(/terminationInquiry/possibleMerchantMatches/terminatedMerchant)', 'INT');

    -- Loop over each terminatedMerchant
    WHILE @i <= @merchantCount
    BEGIN
        -- Extract the i-th terminatedMerchant
        SET @merchantNode = @xmlQuery.query('/terminationInquiry/possibleMerchantMatches/terminatedMerchant[position()=sql:variable("@i")]');

        -- Get just merchantMatch part
        DECLARE @merchantMatch XML = @merchantNode.query('/terminatedMerchant/merchantMatch');

        -- Transform merchantMatch
        EXEC dbo.TransformMerchantMatchXML @InputXML = @merchantMatch;

        -- Capture transformed output
        -- Assume TransformMerchantMatchXML RETURNS XML
        -- so change it to "OUTPUT parameter" if needed
        DECLARE @newMatch XML;
        EXEC dbo.TransformMerchantMatchXML @InputXML=@merchantMatch OUTPUT;

        -- Replace merchantMatch inside merchantNode
        SET @updatedNode = @merchantNode.modify('
            replace value of (/terminatedMerchant/merchantMatch)[1]
            with sql:variable("@newMatch")
        ');

        -- Update back into main XML
        SET @xmlQuery.modify('
            replace value of (/terminationInquiry/possibleMerchantMatches/terminatedMerchant[position()=sql:variable("@i")])[1]
            with sql:variable("@updatedNode")
        ');

        SET @i = @i + 1;
    END;

    -- Save back to table
    UPDATE MatchPros
    SET XMLData = @xmlQuery
    WHERE Id = @Id;
END;
