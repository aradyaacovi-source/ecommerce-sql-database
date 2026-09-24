-- Function, trigger and stored procedure (Task 2)
-- Source: the team's original Part 3 SQL file, split into separate files for this repository.
-- Hebrew comments are original; "-- EN:" lines are English translations added for readers.
-- [portfolio edits] The objects below are also created by 01_create_database_and_load_data.sql.
-- So this file can run after it without errors, CREATE was changed to CREATE OR ALTER and GO batch
-- separators were added before each CREATE statement. The logic is unchanged from the submitted version.
-- Note: the trigger test UPDATEs order 1, so it changes the data.

USE zales;
GO

-- ============================================================
-- מטלה 2 — כלים מתקדמים
-- EN: Task 2 - Advanced tools (function, trigger, stored procedure)
-- ============================================================

-- 2.1: פונקציה טבלאית — סיכום מכירות לפי מדינה
-- EN: 2.1: Table-valued function - sales summary by state
GO
CREATE OR ALTER FUNCTION dbo.GetStateSalesSummary (@State VARCHAR(50))
RETURNS TABLE
AS
RETURN (
    SELECT
        C.Email,
        C.Name_First,
        C.Name_Last,
        C.Phone,
        Total_Spent  = SUM(I.Quantity * CP.Price_Addition),
        Order_Count  = COUNT(DISTINCT O.Order_ID),
        Last_Order   = MAX(O.Date)
    FROM CUSTOMERS C
    JOIN ORDERS_TABLE O  ON C.Email = O.Email
    JOIN INCLUDES I      ON O.Order_ID = I.Order_ID
    JOIN BUILDS_FROM BF  ON I.Jewelry_Variant = BF.Jewelry_Variant
    JOIN COMPONENTS CP   ON BF.Component = CP.Component
    WHERE O.Address_State = @State
    GROUP BY C.Email, C.Name_First, C.Name_Last, C.Phone
);
GO

-- הרצת הפונקציה:
-- EN: Run the function:
SELECT * FROM dbo.GetStateSalesSummary('Louisiana');

-- ============================================================

-- 2.2: טריגר — עדכון אוטומטי של Total_Order_Value
-- EN: 2.2: Trigger - keep Total_Order_Value updated automatically
GO
CREATE OR ALTER TRIGGER trg_UpdateOrderValue
ON INCLUDES
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    IF @@ROWCOUNT = 0 RETURN;

    UPDATE O
    SET Total_Order_Value = ISNULL((
        SELECT SUM(I.Quantity * C.Price_Addition)
        FROM INCLUDES AS I
        JOIN BUILDS_FROM AS BF ON I.Jewelry_Variant = BF.Jewelry_Variant
        JOIN COMPONENTS AS C ON BF.Component = C.Component
        WHERE I.Order_ID = O.Order_ID
    ), 0)
    FROM ORDERS_TABLE AS O
    WHERE O.Order_ID IN (
        SELECT Order_ID FROM INSERTED
        UNION
        SELECT Order_ID FROM DELETED
    );
END;
GO

-- בדיקת הטריגר (לפני ואחרי):
-- EN: Trigger test (before / after):
SELECT TOP 1 O.Order_ID, O.Total_Order_Value
FROM ORDERS_TABLE AS O
INNER JOIN INCLUDES AS I ON O.Order_ID = I.Order_ID;

UPDATE INCLUDES SET Quantity = 5 WHERE Order_ID = 1;

SELECT Order_ID, Total_Order_Value
FROM ORDERS_TABLE
WHERE Order_ID = 1;

-- ============================================================

-- 2.3: Stored Procedure — קביעת סוג אריזה לפי שווי הזמנה
-- EN: 2.3: Stored procedure - set packaging type by order value
GO
CREATE OR ALTER PROCEDURE sp_SetOrderPackaging (@OrderID INT)
AS
BEGIN
    UPDATE ORDERS_TABLE
    SET Packaging_Type = (
        SELECT CASE
            WHEN Total_Order_Revenue >= 2000 THEN 'Premium Velvet Box'
            ELSE 'Standard Box'
        END
        FROM V_ORDER_ANALYSIS
        WHERE Order_ID = @OrderID
    )
    WHERE Order_ID = @OrderID;

    SELECT Order_ID, Packaging_Type
    FROM ORDERS_TABLE
    WHERE Order_ID = @OrderID;
END;
GO

-- הרצת הפרוצדורה:
-- EN: Run the procedure:
SELECT Order_ID, Packaging_Type FROM ORDERS_TABLE WHERE Order_ID = 918;
EXECUTE sp_SetOrderPackaging @OrderID = 918;
